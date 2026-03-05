#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_DIR"

export PATH="$HOME/.local/bin:$HOME/.deno/bin:$PATH"

# Add Homebrew to PATH (macOS)
if [[ "$(uname)" == "Darwin" ]]; then
    if [[ -f /opt/homebrew/bin/brew ]]; then
        eval "$(/opt/homebrew/bin/brew shellenv)"
    elif [[ -f /usr/local/bin/brew ]]; then
        eval "$(/usr/local/bin/brew shellenv)"
    fi
fi

echo ""
echo "  ╔══════════════════════════════════════╗"
echo "  ║       Video Library Update           ║"
echo "  ╚══════════════════════════════════════╝"
echo ""

# 1. Update uv itself
echo "  → Updating uv..."
if command -v uv &> /dev/null; then
    uv self update 2>/dev/null || curl -LsSf https://astral.sh/uv/install.sh | sh
    echo "  ✓ uv up to date"
else
    echo "  ✗ uv not found — run install.sh first"
    exit 1
fi

# 2. Update Python dependencies (yt-dlp, etc.)
echo "  → Updating Python dependencies..."
uv lock --upgrade --quiet
uv sync --quiet
echo "  ✓ Python dependencies updated"

# 3. Update ffmpeg
echo "  → Checking ffmpeg..."
if command -v ffmpeg &> /dev/null; then
    if [[ "$(uname)" == "Darwin" ]] && command -v brew &> /dev/null; then
        brew upgrade ffmpeg 2>/dev/null || echo "  · ffmpeg already latest"
    elif [[ "$(uname)" == "Linux" ]]; then
        if command -v apt-get &> /dev/null; then
            sudo apt-get update -qq && sudo apt-get install -y -qq --only-upgrade ffmpeg 2>/dev/null || true
        elif command -v dnf &> /dev/null; then
            sudo dnf upgrade -y ffmpeg 2>/dev/null || true
        elif command -v pacman &> /dev/null; then
            sudo pacman -S --noconfirm ffmpeg 2>/dev/null || true
        fi
    fi
    echo "  ✓ ffmpeg: $(ffmpeg -version 2>&1 | head -1)"
else
    echo "  ⚠ ffmpeg not found — run install.sh to set it up"
fi

# 4. Update deno
echo "  → Checking deno..."
if command -v deno &> /dev/null; then
    deno upgrade 2>/dev/null || true
    echo "  ✓ deno: $(deno --version 2>&1 | head -1)"
else
    echo "  ⚠ deno not found — run install.sh to set it up"
fi

# 5. Restart the service to pick up changes
echo "  → Restarting service..."
if [[ "$(uname)" == "Darwin" ]]; then
    PLIST="$HOME/Library/LaunchAgents/com.breathwork.app.plist"
    if [[ -f "$PLIST" ]]; then
        launchctl unload "$PLIST" 2>/dev/null || true
        launchctl load "$PLIST"
        echo "  ✓ Service restarted (launchd)"
    else
        echo "  · No launchd service found (start with install.sh)"
    fi
elif [[ "$(uname)" == "Linux" ]]; then
    if systemctl --user is-enabled breathwork.service &>/dev/null; then
        systemctl --user restart breathwork.service
        echo "  ✓ Service restarted (systemd)"
    else
        echo "  · No systemd service found (start with install.sh)"
    fi
fi

echo ""
echo "  ╔══════════════════════════════════════╗"
echo "  ║         Update Complete!             ║"
echo "  ╚══════════════════════════════════════╝"
echo ""
