#!/usr/bin/env python3
"""
StickyTasks - shared local-network server.

Serves task-manager.html and keeps one shared board in tasks.json. Every change
a client makes is sent as a small "operation", applied to the shared board, saved
to tasks.json, and pushed live to everyone else via Server-Sent Events. So several
people on the same network can edit the same board and see updates in real time.

Run it with the "Start Tasks" launcher, or directly:  python server.py
"""

import json
import os
import queue
import socket
import sys
import threading
import uuid
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "tasks.json")
HTML = os.path.join(BASE, "task-manager.html")

# ---------------- shared board (canonical state) ----------------
# The board is split into independent "pages" (workspaces). Each page keeps its
# own tasks, completed items and connections. Older single-board files are
# migrated into one default page on load.
doc = {"pages": [], "seq": 1}
doc_lock = threading.Lock()

def gen_page_id():
    return "p" + uuid.uuid4().hex[:12]

def normalize_page(p):
    p = p or {}
    return {
        "id":          p.get("id") or gen_page_id(),
        "name":        p.get("name") or "Untitled",
        "color":       p.get("color"),
        "tasks":       list(p.get("tasks") or []),
        "completed":   list(p.get("completed") or []),
        "connections": list(p.get("connections") or []),
    }

def normalize(d):
    d = d or {}
    if d.get("pages"):
        pages = [normalize_page(p) for p in d["pages"] if isinstance(p, dict)]
    else:
        # migrate the old single-board file shape into one default page
        pages = [normalize_page({
            "id": "p_main", "name": "Main",
            "tasks": d.get("tasks"), "completed": d.get("completed"),
            "connections": d.get("connections"),
        })]
    if not pages:
        pages = [normalize_page({"id": "p_main", "name": "Main"})]
    return {"pages": pages, "seq": d.get("seq") or 1}

def load_doc():
    global doc
    try:
        with open(DATA, "r", encoding="utf-8") as f:
            d = json.load(f)
    except (FileNotFoundError, ValueError):
        d = {}
    doc = normalize(d)

# ---------------- persistence (debounced writes) ----------------
_pending = None
_save_timer = None
_save_lock = threading.Lock()

def schedule_save(js):
    global _pending, _save_timer
    with _save_lock:
        _pending = js
        if _save_timer is None:
            _save_timer = threading.Timer(0.4, _flush_save)
            _save_timer.daemon = True
            _save_timer.start()

def _flush_save():
    global _pending, _save_timer
    with _save_lock:
        js = _pending
        _pending = None
        _save_timer = None
    if js is not None:
        tmp = DATA + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(js)
        os.replace(tmp, DATA)

# ---------------- apply an operation to the shared board ----------------
def _find(lst, tid):
    for x in lst:
        if x.get("id") == tid:
            return x
    return None

def _page(pid):
    for p in doc["pages"]:
        if p.get("id") == pid:
            return p
    return None

def apply_op(op):
    t = op.get("type")

    # ----- page (workspace) operations -----
    if t == "addPage":
        p = op.get("page") or {}
        if isinstance(p, dict) and p.get("id") and not _page(p["id"]):
            doc["pages"].append(normalize_page(p))
        return
    if t == "renamePage":
        p = _page(op.get("id"))
        if p:
            p["name"] = op.get("name") or "Untitled"
        return
    if t == "pageColor":
        p = _page(op.get("id"))
        if p:
            p["color"] = op.get("color")
        return
    if t == "delPage":
        pid = op.get("id")
        doc["pages"] = [p for p in doc["pages"] if p.get("id") != pid]
        if not doc["pages"]:
            doc["pages"] = [normalize_page({"id": "p_main", "name": "Main"})]
        return
    if t == "replace":
        nd = normalize(op.get("doc"))
        doc["pages"] = nd["pages"]
        doc["seq"] = nd["seq"]
        return

    # ----- task operations (scoped to a single page) -----
    pg = _page(op.get("page"))
    if pg is None:
        return
    tasks, completed, conns = pg["tasks"], pg["completed"], pg["connections"]

    if t == "add":
        task = op.get("task") or {}
        if task.get("id") and not _find(tasks, task["id"]):
            tasks.append(task)
    elif t == "move":
        x = _find(tasks, op.get("id"))
        if x:
            x["x"] = op.get("x"); x["y"] = op.get("y")
    elif t == "text":
        x = _find(tasks, op.get("id"))
        if x:
            x["text"] = op.get("text", "")
    elif t == "accent":
        x = _find(tasks, op.get("id"))
        if x:
            x["accent"] = op.get("accent")
    elif t == "del":
        tid = op.get("id")
        pg["tasks"] = [x for x in tasks if x.get("id") != tid]
        pg["connections"] = [c for c in conns
                             if c.get("a") != tid and c.get("b") != tid]
    elif t == "complete":
        x = _find(tasks, op.get("id"))
        if x:
            pg["tasks"] = [n for n in tasks if n.get("id") != x["id"]]
            x["ts"] = op.get("ts")
            completed.insert(0, x)
    elif t == "undo":
        x = _find(completed, op.get("id"))
        if x:
            pg["completed"] = [n for n in completed if n.get("id") != x["id"]]
            x.pop("ts", None)
            if op.get("x") is not None: x["x"] = op.get("x")
            if op.get("y") is not None: x["y"] = op.get("y")
            tasks.append(x)
    elif t == "delDone":
        tid = op.get("id")
        pg["completed"] = [x for x in completed if x.get("id") != tid]
        pg["connections"] = [c for c in conns
                             if c.get("a") != tid and c.get("b") != tid]
    elif t == "connect":
        c = op.get("conn") or {}
        a, b = c.get("a"), c.get("b")
        dupe = any((k.get("a") == a and k.get("b") == b) or
                   (k.get("a") == b and k.get("b") == a) for k in conns)
        if a and b and a != b and not dupe:
            conns.append(c)
    elif t == "disconnect":
        cid = op.get("id")
        pg["connections"] = [c for c in conns if c.get("id") != cid]

# ---------------- live push (Server-Sent Events) ----------------
subscribers = {}
subs_lock = threading.Lock()

def sse(event, data):
    return "event: %s\ndata: %s\n\n" % (event, data)

def broadcast_op(op_json):
    with subs_lock:
        msg = sse("op", op_json)
        for q in subscribers.values():
            q.put(msg)

def broadcast_presence():
    with subs_lock:
        msg = sse("presence", json.dumps({"count": len(subscribers)}))
        for q in subscribers.values():
            q.put(msg)

# ---------------- HTTP handler ----------------
class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _send(self, code, body=b"", ctype="text/plain; charset=utf-8"):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        if body:
            self.wfile.write(body)

    def do_GET(self):
        path = urlparse(self.path).path
        if path in ("/", "/index.html", "/task-manager.html"):
            try:
                with open(HTML, "rb") as f:
                    self._send(200, f.read(), "text/html; charset=utf-8")
            except FileNotFoundError:
                self._send(404, "task-manager.html not found next to server.py")
        elif path == "/api/state":
            with doc_lock:
                self._send(200, json.dumps(doc), "application/json; charset=utf-8")
        elif path == "/api/events":
            self._serve_events()
        else:
            self._send(404, "Not found")

    def do_POST(self):
        path = urlparse(self.path).path
        if path == "/api/op":
            length = int(self.headers.get("Content-Length", 0) or 0)
            raw = self.rfile.read(length).decode("utf-8")
            try:
                op = json.loads(raw)
                with doc_lock:
                    apply_op(op)
                    snap = json.dumps(doc)
                schedule_save(snap)
                broadcast_op(json.dumps(op))
                self._send(200, '{"ok":true}', "application/json")
            except Exception as e:
                self._send(400, json.dumps({"ok": False, "error": str(e)}), "application/json")
        else:
            self._send(404, "Not found")

    def _serve_events(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.send_header("X-Accel-Buffering", "no")
        self.end_headers()
        q = queue.Queue()
        key = object()
        with subs_lock:
            subscribers[key] = q
        try:
            with doc_lock:
                snap = json.dumps(doc)
            self._raw(sse("snapshot", snap))
            broadcast_presence()               # tell everyone the new head-count
            while True:
                try:
                    msg = q.get(timeout=15)
                except queue.Empty:
                    msg = ": ping\n\n"           # keep the connection warm
                self._raw(msg)
        except (BrokenPipeError, ConnectionResetError, OSError):
            pass
        finally:
            with subs_lock:
                subscribers.pop(key, None)
            broadcast_presence()

    def _raw(self, s):
        self.wfile.write(s.encode("utf-8"))
        self.wfile.flush()

    def log_message(self, *args):
        pass


def lan_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except OSError:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


def main():
    port = 8777
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass

    load_doc()

    httpd = None
    chosen = port
    for p in range(port, port + 25):
        try:
            httpd = ThreadingHTTPServer(("0.0.0.0", p), Handler)   # 0.0.0.0 = reachable on the LAN
            chosen = p
            break
        except OSError:
            continue
    if httpd is None:
        print("Could not find a free port. Close other apps and try again.")
        sys.exit(1)

    ip = lan_ip()
    local_url = "http://127.0.0.1:%d/" % chosen
    share_url = "http://%s:%d/" % (ip, chosen)
    print("=" * 60)
    print("  StickyTasks is running (shared board).")
    print("  You:            " + local_url)
    print("  Others, share:  " + share_url)
    print("  Data file:      " + DATA)
    print("")
    print("  * Same Wi-Fi / network required.")
    print("  * If Windows shows a Firewall prompt, click 'Allow access'")
    print("    (tick Private networks) or others can't connect.")
    print("  * Anyone with the link can view and edit. Keep it on trusted networks.")
    print("  Close this window to stop the app for everyone.")
    print("=" * 60)

    threading.Timer(0.7, lambda: webbrowser.open(local_url)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
