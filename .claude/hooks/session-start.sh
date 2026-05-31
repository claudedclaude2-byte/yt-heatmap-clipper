#!/bin/bash
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

SKILLS_DIR="${HOME}/.claude/skills"
REPO_CACHE="${HOME}/.claude/anthropics-skills-cache"
REPO_URL="https://github.com/anthropics/skills"

mkdir -p "$SKILLS_DIR"

# Clone or update the anthropics/skills repo
if [ -d "${REPO_CACHE}/.git" ]; then
  GIT_TERMINAL_PROMPT=0 git -C "$REPO_CACHE" pull --ff-only --quiet 2>/dev/null || true
else
  GIT_TERMINAL_PROMPT=0 git clone --quiet --depth=1 "$REPO_URL" "$REPO_CACHE"
fi

# Copy each skill directory to ~/.claude/skills/ if not already present
if [ -d "${REPO_CACHE}/skills" ]; then
  for skill_dir in "${REPO_CACHE}/skills"/*/; do
    if [ -f "${skill_dir}SKILL.md" ]; then
      skill_name=$(basename "$skill_dir")
      target="${SKILLS_DIR}/${skill_name}"
      if [ ! -d "$target" ]; then
        cp -r "$skill_dir" "$target"
        echo "Installed skill: ${skill_name}"
      fi
    fi
  done
fi
