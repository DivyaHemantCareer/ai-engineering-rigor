#!/usr/bin/env sh
set -eu

usage() {
  cat <<'EOF'
Install AI Engineering Rigor skills into another repository.

Usage:
  scripts/install.sh --target /path/to/repo [options]

Options:
  -t, --target DIR       Target repository. Defaults to current directory.
  -p, --platform NAME    codex, claude, or both. Defaults to both.
  -s, --skills LIST      Comma-separated skill names. Defaults to all.
                         Names may be short (review,security) or full
                         (ai-rigor-review,ai-rigor-security).
  -c, --with-config      Copy .ai-rigor/ into the target repo if absent.
  -f, --force            Overwrite existing installed skill folders.
  -l, --list             List available skills and exit.
  -h, --help             Show this help.

Examples:
  scripts/install.sh --target ~/work/my-repo
  scripts/install.sh --target ~/work/my-repo --platform codex
  scripts/install.sh --target ~/work/my-repo --skills review,security --with-config
  scripts/install.sh --target ~/work/my-repo --platform claude --force
EOF
}

fail() {
  printf 'error: %s\n' "$1" >&2
  exit 1
}

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
repo_root=$(CDPATH= cd -- "$script_dir/.." && pwd)

target_dir=$(pwd)
platform="both"
skills="all"
with_config="false"
force="false"

available_skills="review coverage commit deps dev qa infra release security"

list_skills() {
  printf '%s\n' "$available_skills" | tr ' ' '\n'
}

normalize_skill() {
  skill=$(printf '%s' "$1" | tr -d '[:space:]')

  case "$skill" in
    ai-rigor-review|review) printf '%s\n' "ai-rigor-review" ;;
    ai-rigor-coverage|coverage) printf '%s\n' "ai-rigor-coverage" ;;
    ai-rigor-commit|commit) printf '%s\n' "ai-rigor-commit" ;;
    ai-rigor-deps|deps|dependencies) printf '%s\n' "ai-rigor-deps" ;;
    ai-rigor-dev|dev|development) printf '%s\n' "ai-rigor-dev" ;;
    ai-rigor-qa|qa) printf '%s\n' "ai-rigor-qa" ;;
    ai-rigor-infra|infra|infrastructure) printf '%s\n' "ai-rigor-infra" ;;
    ai-rigor-release|release) printf '%s\n' "ai-rigor-release" ;;
    ai-rigor-security|security) printf '%s\n' "ai-rigor-security" ;;
    *) fail "unknown skill '$1'. Run with --list to see available skills." ;;
  esac
}

copy_dir() {
  src=$1
  dest=$2

  [ -d "$src" ] || fail "source directory not found: $src"
  src_abs=$(CDPATH= cd -- "$src" && pwd)

  if [ -e "$dest" ]; then
    if [ -d "$dest" ]; then
      dest_abs=$(CDPATH= cd -- "$dest" && pwd)
      if [ "$src_abs" = "$dest_abs" ]; then
        printf 'skip: source and destination are the same (%s)\n' "$dest"
        return 0
      fi
    fi

    if [ "$force" = "true" ]; then
      rm -rf "$dest"
    else
      printf 'skip: %s already exists (use --force to overwrite)\n' "$dest"
      return 0
    fi
  fi

  mkdir -p "$(dirname -- "$dest")"
  cp -R "$src" "$dest"
  printf 'installed: %s\n' "$dest"
}

install_platform_skill() {
  platform_name=$1
  skill_name=$2

  case "$platform_name" in
    codex)
      copy_dir "$repo_root/.agents/skills/$skill_name" "$target_dir/.agents/skills/$skill_name"
      ;;
    claude)
      copy_dir "$repo_root/.claude/skills/$skill_name" "$target_dir/.claude/skills/$skill_name"
      ;;
    *)
      fail "unsupported platform '$platform_name'"
      ;;
  esac
}

install_skill() {
  skill_name=$1

  case "$platform" in
    codex|claude)
      install_platform_skill "$platform" "$skill_name"
      ;;
    both)
      install_platform_skill codex "$skill_name"
      install_platform_skill claude "$skill_name"
      ;;
    *)
      fail "unsupported platform '$platform'. Use codex, claude, or both."
      ;;
  esac
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    -t|--target)
      [ "$#" -ge 2 ] || fail "$1 requires a value"
      target_dir=$2
      shift 2
      ;;
    -p|--platform)
      [ "$#" -ge 2 ] || fail "$1 requires a value"
      platform=$2
      shift 2
      ;;
    -s|--skills)
      [ "$#" -ge 2 ] || fail "$1 requires a value"
      skills=$2
      shift 2
      ;;
    -c|--with-config)
      with_config="true"
      shift
      ;;
    -f|--force)
      force="true"
      shift
      ;;
    -l|--list)
      list_skills
      exit 0
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      fail "unknown option '$1'. Run with --help for usage."
      ;;
  esac
done

case "$platform" in
  codex|claude|both) ;;
  *) fail "unsupported platform '$platform'. Use codex, claude, or both." ;;
esac

mkdir -p "$target_dir"
target_dir=$(CDPATH= cd -- "$target_dir" && pwd)

if [ "$skills" = "all" ]; then
  for short_name in $available_skills; do
    install_skill "$(normalize_skill "$short_name")"
  done
else
  old_ifs=$IFS
  IFS=,
  set -- $skills
  IFS=$old_ifs

  for requested_skill in "$@"; do
    install_skill "$(normalize_skill "$requested_skill")"
  done
fi

if [ "$with_config" = "true" ]; then
  copy_dir "$repo_root/.ai-rigor" "$target_dir/.ai-rigor"
fi

printf '\nDone. Open %s in Codex or Claude Code to use the installed skills.\n' "$target_dir"
