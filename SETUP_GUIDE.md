# Setting Up Breathwork Library on Your Mac

This guide walks you through every single step. Nothing is assumed.
If something goes wrong, the fix is included.

---

## What This Does

You'll have a beautiful app on your Mac that:

- Lets you save YouTube breathwork videos for offline watching
- Plays them right in your browser, no internet needed
- Lets you write personal notes alongside each session
- Starts automatically every time you turn on your Mac
- Works from your phone over WiFi (before you head out)

---

## Step 1: Open Terminal

Terminal is a built-in app on every Mac. It looks like a black screen where you type commands. Don't be scared of it -- you only need it once.

1. Press **Command + Space** (this opens Spotlight search)
2. Type **Terminal**
3. Press **Enter**

A window will open with a blinking cursor. This is where you'll paste commands.

---

## Step 2: Copy the project to your Mac

Someone has given you a folder called `youtube`. You need to put it in the right place.

**Option A: If the folder was sent to you (AirDrop, USB, zip file, etc.)**

1. Unzip it if needed (double-click the .zip file)
2. Move the `youtube` folder to your **home folder**
   - Open Finder
   - Press **Command + Shift + H** (this opens your home folder)
   - Drag the `youtube` folder here

**Option B: If it's on GitHub**

Paste this into Terminal and press Enter:

```
git clone https://github.com/REPO_URL_HERE ~/youtube
```

(Replace `REPO_URL_HERE` with the actual link you were given.)

---

## Step 3: Run the installer

Paste this into Terminal and press Enter:

```
bash ~/youtube/scripts/install.sh
```

**What's happening:** The installer will:
1. Install a tool called `uv` (a Python package manager)
2. Download the things the app needs to run
3. Set up the database
4. Set it to start automatically on boot
5. Start the app right now

When it's done, you'll see something like:

```
  ╔══════════════════════════════════════╗
  ║          Setup Complete!             ║
  ╚══════════════════════════════════════╝

  Open in browser:  http://localhost:8765
  Phone access:     http://192.168.1.42:8765
```

---

## Step 4: Open the app

1. Open **Safari** (or Chrome, or any browser)
2. Go to: **http://localhost:8765**
3. You should see the Breathwork library -- a dark, calm screen

**Bookmark it!** Press **Command + D** to save it as a bookmark.

---

## Step 5: Save your first video

1. Go to YouTube in another tab
2. Find a breathwork video you love
3. Copy the URL from the address bar (click the bar, Command + A, Command + C)
4. Go back to your Breathwork tab
5. Click the **"Save"** button (top right, warm/golden button)
6. Paste the URL (Command + V)
7. Click **"Save Video"**
8. Wait for it to download -- you'll see a progress bar

Once it's done, the video appears in your library. Click it to play.

---

## Step 6: Access from your phone (over WiFi)

This only works when your phone is on the **same WiFi network** as your Mac.

1. Look at the bottom of the Breathwork page on your Mac
2. You'll see something like: `phone: http://192.168.1.42:8765`
3. On your iPhone, open Safari
4. Type that exact address into the URL bar
5. The same library appears on your phone

**Tip:** Bookmark it on your phone too. Before heading out, you can use this to
stream videos to your phone, or AirDrop them (see below).

---

## AirDropping a video to your phone

AirDrop lets you send the actual video file to your iPhone so you can watch it
with zero WiFi or internet.

1. Open a video in the Breathwork app
2. Click **"Reveal in Finder"** (under the video)
3. A Finder window opens with the video file highlighted
4. **Right-click** the file
5. Click **Share** > **AirDrop**
6. Select your iPhone from the list
7. Accept on your phone -- the video saves to your Files or Photos app

---

## That's It!

The app runs automatically every time you start your Mac. You never need to
open Terminal again.

---

## Troubleshooting

### "The page won't load"

The app might not be running. Open Terminal and paste:

```
launchctl load ~/Library/LaunchAgents/com.breathwork.app.plist
```

Then try http://localhost:8765 again. Wait about 5 seconds for it to start.

### "I want to stop the app"

Open Terminal, paste:

```
launchctl unload ~/Library/LaunchAgents/com.breathwork.app.plist
```

### "I want to re-start the app"

Open Terminal, paste:

```
launchctl unload ~/Library/LaunchAgents/com.breathwork.app.plist
launchctl load ~/Library/LaunchAgents/com.breathwork.app.plist
```

### "I want to run the install again"

```
bash ~/youtube/scripts/install.sh
```

This is safe to run multiple times. It won't delete your videos or notes.

### "It says 'uv: command not found'"

Run this first, then try again:

```
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then close Terminal and open a new one.

### "Download failed"

- Make sure you're connected to the internet
- Make sure you pasted a full YouTube URL (starts with https://...)
- Some videos are restricted and can't be downloaded

### "Where are my video files?"

Open Finder, press Command + Shift + G, and type:

```
~/youtube/data/videos
```

All your downloaded videos are there as regular .mp4 files. You can open them
in any video player, copy them, AirDrop them -- they're just normal files.

### "I need to move the app to a different Mac"

Copy the entire `~/youtube` folder to the other Mac (AirDrop, USB drive,
whatever). Then on the new Mac, open Terminal and run:

```
bash ~/youtube/scripts/install.sh
```

This will set everything up. All your videos and notes come with the folder.
