#!/usr/bin/env python3
"""
install.py — Install or update the DeepResearch skill for Roo / Zoo Code.

Run from anywhere; the script locates its own files via __file__.
"""

import shutil
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Error: PyYAML is required.  Install it with:  pip install pyyaml")
    sys.exit(1)


REPO_DIR = Path(__file__).parent.resolve()
ROO_DIR = Path.home() / ".roo"
SKILLS_SRC = REPO_DIR / "skills"
COMMANDS_SRC = REPO_DIR / "commands"
MODES_SRC = REPO_DIR / "modes" / "custom_modes.yaml"
ROO_SKILLS = ROO_DIR / "skills"
ROO_COMMANDS = ROO_DIR / "commands"

# VS Code globalStorage path for Zoo Code.
VSCODE_STORAGE = Path.home() / ".config" / "Code" / "User" / "globalStorage"
ZOO_CODE_MODES = VSCODE_STORAGE / "zoocodeorganization.zoo-code" / "settings" / "custom_modes.yaml"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def ask(prompt: str, default: str = "y") -> bool:
    hint = "[Y/n]" if default == "y" else "[y/N]"
    try:
        answer = input(f"{prompt} {hint}: ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        sys.exit(0)
    if not answer:
        return default == "y"
    return answer in ("y", "yes")



# ---------------------------------------------------------------------------
# Data collection
# ---------------------------------------------------------------------------

def collect_skills() -> list:
    """Top-level subdirectories under skills/ (each is one skill)."""
    if not SKILLS_SRC.is_dir():
        return []
    return sorted(p for p in SKILLS_SRC.iterdir() if p.is_dir())


def collect_commands() -> list:
    """*.md files under commands/."""
    if not COMMANDS_SRC.is_dir():
        return []
    return sorted(COMMANDS_SRC.glob("*.md"))


def collect_source_modes() -> list:
    with open(MODES_SRC) as f:
        data = yaml.safe_load(f)
    return data.get("customModes", [])


def load_modes_file(path: Path) -> dict:
    """Load a custom_modes.yaml, returning a skeleton if absent."""
    if not path.exists():
        return {"customModes": []}
    with open(path) as f:
        data = yaml.safe_load(f) or {}
    data.setdefault("customModes", [])
    return data


# ---------------------------------------------------------------------------
# Installation helpers
# ---------------------------------------------------------------------------

def remove_existing(dst: Path):
    if dst.is_symlink() or dst.is_file():
        dst.unlink()
    elif dst.is_dir():
        shutil.rmtree(dst)


def patch_paths(dst: Path, home: str) -> None:
    """Replace ~/.roo/ with the real home path in all copied text files."""
    files = [dst] if dst.is_file() else dst.rglob("*")
    for f in files:
        if not f.is_file():
            continue
        try:
            text = f.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        patched = text.replace("~/.roo/", f"{home}/.roo/")
        if patched != text:
            f.write_text(patched, encoding="utf-8")


def install_item(src: Path, dst: Path, label: str, home: str) -> str:
    """
    Copy src → dst.
    Returns 'installed', 'updated', or 'skipped'.
    Asks the user when dst already exists.
    """
    already_exists = dst.exists() or dst.is_symlink()
    if already_exists:
        if not ask(f"  {label} already exists. Update it?", default="n"):
            return "skipped"
        remove_existing(dst)

    if src.is_dir():
        shutil.copytree(src, dst)
    else:
        shutil.copy2(src, dst)
    patch_paths(dst, home)

    return "updated" if already_exists else "installed"


def merge_modes(modes: list, modes_path: Path, label: str, home: str) -> bool:
    """Merge source modes into a target custom_modes.yaml. Returns True if changed."""
    target = load_modes_file(modes_path)
    slug_to_index = {m["slug"]: i for i, m in enumerate(target["customModes"])}
    changed = False

    for mode in modes:
        slug = mode["slug"]
        display = f"{slug}  —  {mode.get('name', '')}"
        if slug in slug_to_index:
            if ask(f"  [{label}] Mode '{slug}' already exists. Update it?", default="n"):
                target["customModes"][slug_to_index[slug]] = mode
                print(f"  [updated  ] {display}")
                changed = True
            else:
                print(f"  [skipped  ] {display}")
        else:
            target["customModes"].append(mode)
            slug_to_index[slug] = len(target["customModes"]) - 1
            print(f"  [installed] {display}")
            changed = True

    if changed:
        modes_path.parent.mkdir(parents=True, exist_ok=True)
        with open(modes_path, "w") as f:
            yaml.dump(
                target,
                f,
                allow_unicode=True,
                sort_keys=False,
                default_flow_style=False,
                width=120,
            )
        patch_paths(modes_path, home)
        print(f"  Saved → {modes_path}")

    return changed


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

def print_summary(skills, commands, modes):
    print(f"\n{'─'*55}")
    print("What will be installed")
    print(f"{'─'*55}")

    print(f"\nSkills  (copied → {ROO_SKILLS}/):")
    for s in skills:
        print(f"  • {s.name}/")

    print(f"\nCommands  (copied → {ROO_COMMANDS}/):")
    for c in commands:
        print(f"  • {c.name}")

    print(f"\nModes  (merged into {ZOO_CODE_MODES}):")
    for m in modes:
        print(f"  • {m['slug']}  —  {m.get('name', '')}")

    print(f"{'─'*55}\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=== DeepResearch Skill Installer ===\n")

    skills = collect_skills()
    commands = collect_commands()
    modes = collect_source_modes()

    if not skills and not commands and not modes:
        print("Nothing found to install. Are you running from the right directory?")
        sys.exit(1)

    home = str(Path.home())

    # --- Dry-run summary + confirmation ---
    print_summary(skills, commands, modes)
    if not ask("Proceed with installation?", default="y"):
        print("Aborted.")
        sys.exit(0)

    print()

    # 1. Ensure target directories exist
    ROO_SKILLS.mkdir(parents=True, exist_ok=True)
    ROO_COMMANDS.mkdir(parents=True, exist_ok=True)
    print(f"Directories ready: {ROO_SKILLS}")
    print(f"                   {ROO_COMMANDS}\n")

    # 2. Skills
    print("--- Skills ---")
    for skill in skills:
        dst = ROO_SKILLS / skill.name
        result = install_item(skill, dst, f"Skill '{skill.name}/'", home)
        print(f"  [{result:<9}] {skill.name}/")

    # 3. Commands
    print("\n--- Commands ---")
    for cmd in commands:
        dst = ROO_COMMANDS / cmd.name
        result = install_item(cmd, dst, f"Command '{cmd.name}'", home)
        print(f"  [{result:<9}] {cmd.name}")

    # 4. Modes
    print("\n--- Modes ---")
    merge_modes(modes, ZOO_CODE_MODES, "Zoo Code", home)

    print("\n=== Installation complete ===")


if __name__ == "__main__":
    main()
