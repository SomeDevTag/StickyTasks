# StickyTasks

A little sticky-note board you can share with people on the same Wi-Fi.

Jot things down, drag them around, box related notes together, and watch everyone's changes show up live. No accounts, no cloud — it just runs on your machine and saves to a plain `tasks.json` you can back up or peek at any time.

<img width="1870" height="950" alt="StickyTasks board" src="https://github.com/user-attachments/assets/1e801fd4-e001-4bcf-8623-7ec72db1edc8" />

## Start it

1. Install [Python](https://www.python.org/downloads/) (tick *Add python.exe to PATH* during setup).
2. Double-click **Start StickyTasks.bat**.
3. Your browser opens the board. Keep the little black window open while you use it.

Want others to join? The black window prints a "share" link like `http://192.168.1.42:8777/`. Send it to anyone on the same network and you're editing the same board together, live.

> First run, Windows may ask about the firewall — allow it, and make sure the network is set to **Private**, or nobody else can connect. It's password-free, so stick to networks you trust.

No Python? You can still open `task-manager.html` on its own. It works the same, it just saves inside your browser instead of the shared file (use Export to keep a copy).

## What you can do

**Notes.** Type in the bar at the bottom and hit Enter — the note drops into the middle of your view. Pick its color with the dot on the left first if you like. Drag notes anywhere, right-click one to recolor or rename it, and drop it on the green bar to mark it done. Notes grow to fit whatever you put in them.

**Subtasks.** Every note can hold a little checklist. Hit **+ subtask**, tick things off, double-click a subtask to rename it. The note resizes itself as the list changes.

**Groups.** Grab the ▭ tool next to the input and draw a box around related notes — like a frame in Figma. Drag its header to move the whole cluster at once (the notes stay independent, they just come along). Resize it from any edge or corner, rename it, recolor it, or delete the frame without touching the notes inside.

**Pages.** Keep separate boards in the sidebar. Each page has its own color and its own notes. Click **+** to add one, click to switch, double-click to rename, right-click to change its color.

**Links.** Hover a note, drag the dot on its edge onto another note to connect them. The line finds the shortest path between the two.

**The rest.** Dark mode, recenter, and export/import all live in the **⋯** menu. Pan around by dragging empty space (or middle-mouse), and press Home to jump back to the start.

## Where your stuff lives

Everything sits in `tasks.json` next to the app — pages, notes, colors, groups, subtasks, the lot. Copy that file to back up or move your board. If the host closes the black window, the shared board goes offline until it's started again.
