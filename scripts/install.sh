#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_DIR"

# Ensure ~/.local/bin is in PATH (where uv installs)
export PATH="$HOME/.local/bin:$PATH"

echo ""
echo "  ╔══════════════════════════════════════╗"
echo "  ║        Video Library Setup           ║"
echo "  ╚══════════════════════════════════════╝"
echo ""

# 1. Check for uv, install if missing
if ! command -v uv &> /dev/null; then
    echo "  → Installing uv (Python package manager)..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi
echo "  ✓ uv found: $(which uv)"

# 2. Check for ffmpeg, install if missing
if ! command -v ffmpeg &> /dev/null; then
    echo "  → ffmpeg not found — installing..."
    if [[ "$(uname)" == "Darwin" ]]; then
        if command -v brew &> /dev/null; then
            brew install ffmpeg
        else
            echo "  → Homebrew not found — installing Homebrew first..."
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            # Add brew to PATH for Apple Silicon and Intel Macs
            if [[ -f /opt/homebrew/bin/brew ]]; then
                eval "$(/opt/homebrew/bin/brew shellenv)"
            elif [[ -f /usr/local/bin/brew ]]; then
                eval "$(/usr/local/bin/brew shellenv)"
            fi
            brew install ffmpeg
        fi
    elif [[ "$(uname)" == "Linux" ]]; then
        if command -v apt-get &> /dev/null; then
            sudo apt-get update -qq && sudo apt-get install -y -qq ffmpeg
        elif command -v dnf &> /dev/null; then
            sudo dnf install -y ffmpeg
        elif command -v pacman &> /dev/null; then
            sudo pacman -S --noconfirm ffmpeg
        else
            echo "  ✗ Could not install ffmpeg — please install it manually"
            exit 1
        fi
    fi
fi
if command -v ffmpeg &> /dev/null; then
    echo "  ✓ ffmpeg found: $(ffmpeg -version 2>&1 | head -1)"
else
    echo "  ✗ ffmpeg installation failed — please install it manually"
    echo "    macOS:  brew install ffmpeg"
    echo "    Linux:  sudo apt install ffmpeg"
    exit 1
fi

# 3. Check for deno (required by yt-dlp for YouTube extraction)
if ! command -v deno &> /dev/null; then
    echo "  → deno not found — installing (required by yt-dlp)..."
    if [[ "$(uname)" == "Darwin" ]]; then
        brew install deno
    elif [[ "$(uname)" == "Linux" ]]; then
        curl -fsSL https://deno.land/install.sh | sh
        export PATH="$HOME/.deno/bin:$PATH"
    fi
fi
if command -v deno &> /dev/null; then
    echo "  ✓ deno found: $(deno --version 2>&1 | head -1)"
else
    echo "  ✗ deno installation failed — please install it manually"
    echo "    See: https://docs.deno.com/runtime/getting_started/installation/"
    exit 1
fi

# 4. Create data directories
mkdir -p data/videos data/thumbnails data/logs
echo "  ✓ Data directories ready"

# 5. Install Python dependencies
echo "  → Installing dependencies..."
uv sync --quiet
echo "  ✓ Dependencies installed"

# 6. Choose a theme
echo ""
echo "  Choose a theme for your library:"
echo ""
echo "    1) Breathwork   — Dark, meditative, warm amber tones"
echo "    2) Cyberpunk    — Neon cyan, dark matrix aesthetic"
echo "    3) Classy       — Clean, elegant, understated gold"
echo ""
read -p "  Enter choice [1-3, default=1]: " THEME_CHOICE
case "${THEME_CHOICE}" in
    2) THEME_ID="cyberpunk" ;;
    3) THEME_ID="classy" ;;
    *) THEME_ID="breathwork" ;;
esac
echo "{\"theme\": \"${THEME_ID}\"}" > data/theme.json
echo "  ✓ Theme set to: ${THEME_ID}"

# 7. Initialize database
echo "  → Initializing database..."
uv run python -c "
from breathwork.database import init_db
import asyncio
asyncio.run(init_db())
"
echo "  ✓ Database initialized"

# 8. Install auto-start service
UV_PATH="$(which uv)"
HOME_DIR="$HOME"

if [[ "$(uname)" == "Darwin" ]]; then
    # ───── macOS: launchd ─────
    echo "  → Setting up auto-start (macOS launchd)..."
    PLIST_DST="$HOME/Library/LaunchAgents/com.breathwork.app.plist"

    sed -e "s|__UV_PATH__|${UV_PATH}|g" \
        -e "s|__PROJECT_DIR__|${PROJECT_DIR}|g" \
        -e "s|__HOME_DIR__|${HOME_DIR}|g" \
        "$PROJECT_DIR/scripts/com.breathwork.app.plist" > "$PLIST_DST"

    launchctl unload "$PLIST_DST" 2>/dev/null || true
    launchctl load "$PLIST_DST"
    echo "  ✓ Auto-start service installed (launchd)"

elif [[ "$(uname)" == "Linux" ]]; then
    # ───── Linux: systemd user service ─────
    echo "  → Setting up auto-start (Linux systemd)..."
    SYSTEMD_DIR="$HOME/.config/systemd/user"
    mkdir -p "$SYSTEMD_DIR"

    # Use python for templating to avoid sed escaping issues with paths
    uv run python -c "
import sys
with open('$PROJECT_DIR/scripts/breathwork.service') as f:
    c = f.read()
c = c.replace('__UV_PATH__', '${UV_PATH}')
c = c.replace('__PROJECT_DIR__', '${PROJECT_DIR}')
with open('${SYSTEMD_DIR}/breathwork.service', 'w') as f:
    f.write(c)
"

    systemctl --user daemon-reload
    systemctl --user enable breathwork.service
    systemctl --user restart breathwork.service
    echo "  ✓ Auto-start service installed (systemd)"

    # Enable lingering so the service runs even when logged out
    if command -v loginctl &> /dev/null; then
        loginctl enable-linger "$(whoami)" 2>/dev/null || true
    fi
fi

# 9. Wait a moment for service to start, then check
sleep 2
if curl -s --max-time 3 http://localhost:8765/api/system/info > /dev/null 2>&1; then
    echo "  ✓ Server is running!"
else
    echo "  ⚠ Server didn't respond yet. It may still be starting up."
    echo "    Check with: curl http://localhost:8765/api/system/info"
fi

# 10. Get local IP
LOCAL_IP="127.0.0.1"
if [[ "$(uname)" == "Darwin" ]]; then
    LOCAL_IP=$(ipconfig getifaddr en0 2>/dev/null || echo "127.0.0.1")
else
    LOCAL_IP=$(hostname -I 2>/dev/null | awk '{print $1}' || echo "127.0.0.1")
fi

HOSTNAME_LOCAL=""
if [[ "$(uname)" == "Darwin" ]]; then
    HOSTNAME_LOCAL=$(scutil --get LocalHostName 2>/dev/null || true)
    if [[ -n "$HOSTNAME_LOCAL" ]]; then
        HOSTNAME_LOCAL="${HOSTNAME_LOCAL}.local"
    fi
fi

echo ""
echo "  ╔══════════════════════════════════════╗"
echo "  ║          Setup Complete!             ║"
echo "  ╚══════════════════════════════════════╝"
echo ""
echo "  Open in browser:  http://localhost:8765"
echo "  Phone access:     http://${LOCAL_IP}:8765"
if [[ -n "$HOSTNAME_LOCAL" ]]; then
echo "  Or by name:       http://${HOSTNAME_LOCAL}:8765"
fi
echo ""
echo "  Videos stored in: $PROJECT_DIR/data/videos/"
echo ""
echo "  ┌─────────────────────────────────────────────┐"
echo "  │ The service starts automatically on reboot.  │"
echo "  │ To stop:  see commands below                 │"
echo "  └─────────────────────────────────────────────┘"
echo ""
if [[ "$(uname)" == "Darwin" ]]; then
echo "  Stop:     launchctl unload ~/Library/LaunchAgents/com.breathwork.app.plist"
echo "  Start:    launchctl load ~/Library/LaunchAgents/com.breathwork.app.plist"
echo "  Logs:     tail -f $PROJECT_DIR/data/logs/stderr.log"
else
echo "  Stop:     systemctl --user stop breathwork"
echo "  Start:    systemctl --user start breathwork"
echo "  Logs:     journalctl --user -u breathwork -f"
fi
echo ""
