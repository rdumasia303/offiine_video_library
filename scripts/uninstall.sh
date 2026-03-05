#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_DIR"

echo ""
echo "  ╔══════════════════════════════════════╗"
echo "  ║       Video Library Uninstall        ║"
echo "  ╚══════════════════════════════════════╝"
echo ""

# 1. Stop and remove auto-start service
if [[ "$(uname)" == "Darwin" ]]; then
    PLIST="$HOME/Library/LaunchAgents/com.breathwork.app.plist"
    if [[ -f "$PLIST" ]]; then
        echo "  → Stopping macOS service..."
        launchctl unload "$PLIST" 2>/dev/null || true
        rm -f "$PLIST"
        echo "  ✓ launchd service removed"
    else
        echo "  · No launchd service found (skipping)"
    fi

elif [[ "$(uname)" == "Linux" ]]; then
    SYSTEMD_FILE="$HOME/.config/systemd/user/breathwork.service"
    if [[ -f "$SYSTEMD_FILE" ]]; then
        echo "  → Stopping Linux service..."
        systemctl --user stop breathwork.service 2>/dev/null || true
        systemctl --user disable breathwork.service 2>/dev/null || true
        rm -f "$SYSTEMD_FILE"
        systemctl --user daemon-reload
        echo "  ✓ systemd service removed"
    else
        echo "  · No systemd service found (skipping)"
    fi
fi

# 2. Ask about data
echo ""
if [[ -d "$PROJECT_DIR/data" ]]; then
    TOTAL_SIZE=$(du -sh "$PROJECT_DIR/data" 2>/dev/null | awk '{print $1}')
    VIDEO_COUNT=$(find "$PROJECT_DIR/data/videos" -type f 2>/dev/null | wc -l | tr -d ' ')
    echo "  You have ${VIDEO_COUNT} videos (${TOTAL_SIZE} total) in data/"
    echo ""
    read -p "  Delete all downloaded videos and data? [y/N]: " DELETE_DATA
    if [[ "$DELETE_DATA" == [yY] ]]; then
        rm -rf "$PROJECT_DIR/data"
        echo "  ✓ Data directory deleted"
    else
        echo "  · Keeping data directory"
    fi
else
    echo "  · No data directory found"
fi

# 3. Ask about the project itself
echo ""
read -p "  Delete the entire project directory? [y/N]: " DELETE_PROJECT
if [[ "$DELETE_PROJECT" == [yY] ]]; then
    echo "  → Removing $PROJECT_DIR ..."
    cd /
    rm -rf "$PROJECT_DIR"
    echo "  ✓ Project deleted"
else
    echo "  · Keeping project directory"
    echo "    You can delete it manually: rm -rf $PROJECT_DIR"
fi

echo ""
echo "  ╔══════════════════════════════════════╗"
echo "  ║        Uninstall Complete            ║"
echo "  ╚══════════════════════════════════════╝"
echo ""
