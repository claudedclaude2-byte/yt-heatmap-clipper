#!/bin/bash
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

SKILLS_DIR="${HOME}/.claude/skills"
mkdir -p "$SKILLS_DIR"

install_skills_from_repo() {
  local repo_url="$1"
  local cache_dir="$2"
  local skills_subdir="$3"

  if [ -d "${cache_dir}/.git" ]; then
    GIT_TERMINAL_PROMPT=0 git -C "$cache_dir" pull --ff-only --quiet 2>/dev/null || true
  else
    GIT_TERMINAL_PROMPT=0 git clone --quiet --depth=1 "$repo_url" "$cache_dir"
  fi

  if [ -d "${cache_dir}/${skills_subdir}" ]; then
    for skill_dir in "${cache_dir}/${skills_subdir}"/*/; do
      if [ -f "${skill_dir}SKILL.md" ]; then
        skill_name=$(basename "$skill_dir")
        cp -rf "$skill_dir" "${SKILLS_DIR}/${skill_name}"
        echo "Installed skill: ${skill_name}"
      fi
    done
  fi
}

# Install all skills from anthropics/skills
install_skills_from_repo \
  "https://github.com/anthropics/skills" \
  "${HOME}/.claude/anthropics-skills-cache" \
  "skills"

# Install frontend-design plugin from anthropics/claude-plugins-official
install_skills_from_repo \
  "https://github.com/anthropics/claude-plugins-official" \
  "${HOME}/.claude/anthropics-plugins-cache" \
  "plugins/frontend-design/skills"
