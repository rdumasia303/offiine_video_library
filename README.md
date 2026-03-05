# Offline Video Library

A self-hosted video library that downloads YouTube videos for offline viewing. Runs as a background service on your Mac or Linux machine, accessible from any device on your local network — your laptop, your phone, a tablet on the couch.

Download a video at home over Wi-Fi. Watch it later with no internet. That's it.

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│   Your Computer (always running)                    │
│   ┌───────────────────────────────────┐             │
│   │  Offline Video Library            │             │
│   │  http://localhost:8765            │ ◄── You     │
│   │                                   │             │
│   │  • Downloads from YouTube         │             │
│   │  • Stores videos locally          │ ◄── Phone   │
│   │  • Streams to any device          │    (Wi-Fi)  │
│   │  • Works completely offline       │             │
│   └───────────────────────────────────┘             │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## Features

- **One-click YouTube downloads** — paste a URL, it handles the rest
- **Offline playback** — videos are stored locally, no internet needed to watch
- **Phone access** — open the same URL on your phone over Wi-Fi
- **Save to device** — download videos directly to your phone for truly offline use
- **Personal notes** — write notes on any video, auto-saved as you type
- **Favorites** — mark videos you want to come back to
- **Search** — find videos by title, channel, or your notes
- **Background service** — starts automatically on boot, always ready
- **Themeable** — three built-in visual themes, choose during setup

---

## Themes

Pick a theme during installation. Each one changes the entire look, feel, and language of the UI.

| Breathwork | Cyberpunk | Classy |
|:---:|:---:|:---:|
| Dark, meditative, warm amber | Neon cyan, hacker terminal | Refined, minimal, muted gold |
| *"Begin your practice"* | *"No data cached"* | *"Your collection is empty"* |

---

## Quick Start

### Requirements

- macOS or Linux
- Internet connection (for initial setup and downloading videos)
- That's it. Everything else is installed automatically.

### Install

```bash
git clone git@github.com:rdumasia303/offiine_video_library.git
cd offiine_video_library
bash scripts/install.sh
```

The installer will:
1. Install [uv](https://docs.astral.sh/uv/) (if not present) — a fast Python package manager
2. Install all dependencies
3. Ask you to **choose a theme**
4. Initialize the database
5. Set up a background service (launchd on Mac, systemd on Linux)
6. Start the server

When it's done:

```
  Open in browser:  http://localhost:8765
  Phone access:     http://192.168.x.x:8765
```

### Use It

1. Open `http://localhost:8765` in your browser
2. Click the **"From YouTube"** button
3. Paste a YouTube URL
4. Wait for the download to finish
5. Click the video to watch it

### Access from Your Phone

Your phone can access the library over Wi-Fi — the install script prints the URL. Just make sure your phone is on the same network as the computer running the service.

**To save a video to your phone:**
1. Open a video in the player
2. Tap **"Save to This Device"**
3. The video downloads to your browser's Downloads folder

> On iPhone (Safari/Chrome), downloaded files appear in the Files app under the browser's Downloads folder.

---

## Managing the Service

### macOS

```bash
# Stop the service
launchctl unload ~/Library/LaunchAgents/com.breathwork.app.plist

# Start the service
launchctl load ~/Library/LaunchAgents/com.breathwork.app.plist

# View logs
tail -f ~/offiine_video_library/data/logs/stderr.log
```

### Linux

```bash
# Stop the service
systemctl --user stop breathwork

# Start the service
systemctl --user start breathwork

# View logs
journalctl --user -u breathwork -f
```

---

## Changing Themes

Edit `data/theme.json` and restart the service:

```bash
# Switch to cyberpunk
echo '{"theme": "cyberpunk"}' > data/theme.json

# Then restart (macOS)
launchctl unload ~/Library/LaunchAgents/com.breathwork.app.plist
launchctl load ~/Library/LaunchAgents/com.breathwork.app.plist

# Or restart (Linux)
systemctl --user restart breathwork
```

Available themes: `breathwork`, `cyberpunk`, `classy`

---

## Uninstall

```bash
bash scripts/uninstall.sh
```

This will:
1. Stop and remove the background service
2. Ask if you want to delete your downloaded videos
3. Ask if you want to delete the project directory

---

## Project Structure

```
├── scripts/
│   ├── install.sh              One-command setup
│   └── uninstall.sh            Clean removal
├── src/breathwork/
│   ├── main.py                 FastAPI application
│   ├── config.py               Paths, port, theme config
│   ├── models.py               Database models
│   ├── routers/                API endpoints
│   ├── services/               YouTube download engine
│   ├── themes/                 Theme registry + metadata
│   ├── templates/              Jinja2 HTML template
│   └── static/
│       ├── css/                Structural CSS + per-theme styles
│       ├── js/                 App logic + per-theme config
│       └── vendor/             Alpine.js + Tailwind (vendored)
└── data/                       Videos, thumbnails, database (gitignored)
```

---

## Tech Stack

| | |
|---|---|
| **Backend** | FastAPI, SQLAlchemy, aiosqlite |
| **Downloader** | yt-dlp |
| **Frontend** | Alpine.js, Tailwind CSS (no build step) |
| **Database** | SQLite |
| **Package manager** | uv |
| **Service** | launchd (macOS) / systemd (Linux) |

---

## Adding a Theme

Create three files:

1. `src/breathwork/themes/mytheme.py` — metadata (fonts URL, favicon, title)
2. `src/breathwork/static/css/themes/mytheme.css` — CSS custom properties + animations
3. `src/breathwork/static/js/themes/mytheme.js` — Tailwind config + UI copy strings

Then add one import to `src/breathwork/themes/__init__.py` and one option to `scripts/install.sh`.

---
## Making an app


🚀 Guide: Create a Borderless Desktop App for your Local Tool
This guide will turn your local service (running on port 8675) into a standalone, distraction-free macOS App that sits in your Dock and launches without browser tabs or address bars.

🛠 Prerequisites
Google Chrome installed.

Your Mac’s Hostname. (Find this in System Settings > General > Sharing, or type hostname in Terminal. It usually looks like My-Macbook.local).

Step 1: Create the "App" Wrapper
We use macOS Automator to build a tiny script that tells Chrome to run in "App Mode."

Open Automator (Cmd + Space, type "Automator").

Select New Document then choose Application.

In the search box on the left, type "Shell" and double-click Run Shell Script.

Paste the following code into the box, replacing YOUR-HOSTNAME.local with your actual hostname:

Bash
open -n -a "Google Chrome" --args "--app=http://YOUR-HOSTNAME.local:8675"
Why use the hostname? Using http://localhost:8675 only works for the person sitting at the keyboard. Using http://macbook-pro.local:8675 ensures the shortcut is more robust and identifies the specific machine on your local network.

Step 2: Save and Deploy
Go to File > Save.

Name it (e.g., "My Local Dashboard").

Save it directly to your Applications folder (or Desktop).

Step 3: Add a Custom Icon (The "Pro" Touch)
By default, this will have a generic Automator icon. Let's make it look like a real app:

Find a PNG icon you like (or a screenshot of the tool).

Open the image in Preview.

Press Cmd + A (Select All) then Cmd + C (Copy).

Right-click your new App file and select Get Info.

Click the small icon at the very top-left of the Info window (it will glow blue).

Press Cmd + V (Paste).

Step 4: Pin to the Dock
Drag your new app from your Applications folder (or Desktop) onto the left side of your Dock.

Click it.

Result: Chrome launches a dedicated, borderless window that feels exactly like a native Mac application.

💡 Quick Troubleshooting
Window too big/small? You can force a specific size by adding "--window-size=1200,800" to the end of the script in Step 1.

Updating the URL: If your port changes, just right-click the App, select Open with > Automator, and edit the URL.

## License

MIT
