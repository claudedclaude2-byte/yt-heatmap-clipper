#!/bin/bash
# Quick restore script — run this if something goes wrong
# Usage: bash scripts/restore.sh [backup-folder-name]
# Example: bash scripts/restore.sh 2026-05-16_pre-implementation

set -e

BACKUP_DIR="backups/${1:-}"

if [ -z "$1" ]; then
    echo "Available backups:"
    ls backups/
    echo ""
    echo "Usage: bash scripts/restore.sh <backup-folder-name>"
    exit 1
fi

if [ ! -d "$BACKUP_DIR" ]; then
    echo "ERROR: Backup '$BACKUP_DIR' not found."
    echo "Available backups:"
    ls backups/
    exit 1
fi

echo "Restoring from: $BACKUP_DIR"
echo "Files in backup:"
ls "$BACKUP_DIR"
echo ""

read -p "Are you sure you want to restore? This overwrites current files. (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo "Aborted."
    exit 0
fi

# Create a safety backup of current state before restoring
SAFETY="backups/$(date +%Y-%m-%d_%H-%M)_pre-restore"
mkdir -p "$SAFETY"
cp -r pine rules prompts scripts CLAUDE.md "$SAFETY/" 2>/dev/null || true
echo "Safety backup of current state saved to: $SAFETY"

# Restore
cp -r "$BACKUP_DIR"/. .
echo ""
echo "Restore complete from $BACKUP_DIR"
echo "Run: git diff   to see what changed"
