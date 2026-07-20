<div align="center">

# 🗒️ StickyTasks

**A little sticky-note board you can share with people on the same Wi-Fi.**

Jot things down, drag them around, box related notes together, and watch everyone's changes show up live.
No accounts, no cloud — it just runs on your machine and saves to a plain `tasks.json` you can back up or peek at any time.

![Python](https://img.shields.io/badge/Python-3-3776AB?logo=python&logoColor=white)
![No dependencies](https://img.shields.io/badge/dependencies-none-brightgreen)
![Runs on](https://img.shields.io/badge/runs-in%20your%20browser-f7b955)
![Offline](https://img.shields.io/badge/cloud-not%20required-8b5cf6)

<img width="2498" alt="StickyTasks board" src="https://github.com/user-attachments/assets/1e962d90-d07d-4cd9-a02b-e80accc923ac" />

</div>

---

## 🚀 Start it

1. Install [Python](https://www.python.org/downloads/) — tick **Add python.exe to PATH** during setup.
2. Double-click **`Start StickyTasks.bat`**.
3. Your browser opens the board. Keep the little black window open while you use it.

> [!TIP]
> **Want others to join?** The black window prints a share link like `http://192.168.1.42:8777/`.
> Send it to anyone on the same network and you're editing the same board together, live.

> [!IMPORTANT]
> First run, Windows may ask about the firewall — allow it, and set the network to **Private**, or nobody else can connect. It's password-free, so stick to networks you trust.

> [!NOTE]
> No Python? You can still open `task-manager.html` on its own. Works the same — it just saves inside your browser instead of the shared file (use **Export** to keep a copy).

---

## ✨ What you can do

| | |
|---|---|
| 📝 **Notes** | Type in the bar and hit Enter — the note lands in the middle of your view. Pick its color with the dot on the left, drag it anywhere, right-click to recolor or rename, and drop it on the green bar to finish it. Notes grow to fit their content. |
| ✅ **Subtasks** | Every note holds a little checklist. Hit **+ subtask**, tick things off, double-click a subtask to rename it. The note resizes as the list changes. |
| ▭ **Groups** | Grab the frame tool by the input and draw a box around related notes, Figma-style. Drag the header to move the whole cluster (notes stay independent). Resize from any edge or corner, rename, recolor, or delete the frame without touching what's inside. |
| 📂 **Pages** | Keep separate boards in the sidebar, each with its own color. **+** to add, click to switch, double-click to rename, right-click to recolor. |
| 🔗 **Links** | Drag the dot on a note's edge onto another to connect them — the line finds the shortest path between the two. |
| 🌙 **The rest** | Dark mode, recenter, and export/import live in the **⋯** menu. Pan by dragging empty space (or middle-mouse); press **Home** to jump back. |

---

## 💾 Where your stuff lives

Everything sits in **`tasks.json`** next to the app — pages, notes, colors, groups, subtasks, the lot.
Copy that file to back up or move your board. If the host closes the black window, the shared board goes offline until it's started again.
