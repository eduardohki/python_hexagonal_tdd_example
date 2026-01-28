#!/usr/bin/env python3
"""Clean script to remove temporary and ignored files from the project.

This script removes build artifacts, caches, and other temporary files
while preserving important local configuration files like .env, .envrc,
and similar developer-specific settings.

Usage:
    uv run clean          # Normal clean
    uv run clean --dry-run  # Preview what would be deleted
    uv run clean --all    # Also remove .venv (use with caution)
"""

import argparse
import shutil
from pathlib import Path

# Directories to always remove
DIRS_TO_CLEAN = [
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".hypothesis",
    ".tox",
    ".nox",
    "build",
    "dist",
    "wheels",
    "htmlcov",
    "*.egg-info",
]

# Files to always remove
FILES_TO_CLEAN = [
    "*.pyc",
    "*.pyo",
    "*.pyd",
    ".coverage",
    "coverage.xml",
    "*.cover",
    "*.py,cover",
]

# Patterns to preserve (local config files)
PRESERVE_PATTERNS = [
    ".env",
    ".env.*",
    ".envrc",
    ".python-version",
    ".tool-versions",
    ".editorconfig",
    ".vscode",
    ".idea",
    "*.local",
    "*.local.*",
]


def find_project_root() -> Path:
    """Find the project root directory (where pyproject.toml is located)."""
    current = Path(__file__).resolve().parent
    while current != current.parent:
        if (current / "pyproject.toml").exists():
            return current
        current = current.parent
    # Fallback to script's parent's parent
    return Path(__file__).resolve().parent.parent


def should_preserve(path: Path) -> bool:
    """Check if a path should be preserved."""
    name = path.name
    for pattern in PRESERVE_PATTERNS:
        if pattern.startswith("*."):
            # Suffix match
            if name.endswith(pattern[1:]):
                return True
        elif "*" in pattern:
            # Simple wildcard match
            prefix, suffix = pattern.split("*", 1)
            if name.startswith(prefix) and name.endswith(suffix):
                return True
        elif name == pattern:
            return True
    return False


def find_dirs_to_clean(root: Path, include_venv: bool = False) -> list[Path]:
    """Find all directories that should be cleaned."""
    dirs_found: list[Path] = []

    for pattern in DIRS_TO_CLEAN:
        if "*" in pattern:
            # Glob pattern (e.g., *.egg-info)
            dirs_found.extend(root.rglob(pattern))
        else:
            # Exact name match
            dirs_found.extend(root.rglob(pattern))

    # Optionally include .venv
    if include_venv:
        venv_path = root / ".venv"
        if venv_path.exists():
            dirs_found.append(venv_path)

    # Filter out preserved paths and paths inside .venv (unless removing it)
    result = []
    for d in dirs_found:
        if should_preserve(d):
            continue
        # Skip anything inside .venv unless we're cleaning .venv itself
        if not include_venv and ".venv" in d.parts:
            continue
        if d.is_dir():
            result.append(d)

    return sorted(set(result))


def find_files_to_clean(root: Path) -> list[Path]:
    """Find all files that should be cleaned."""
    files_found: list[Path] = []

    for pattern in FILES_TO_CLEAN:
        files_found.extend(root.rglob(pattern))

    # Filter out preserved files and files inside .venv
    result = []
    for f in files_found:
        if should_preserve(f):
            continue
        # Skip anything inside .venv
        if ".venv" in f.parts:
            continue
        if f.is_file():
            result.append(f)

    return sorted(set(result))


def format_size(size_bytes: int) -> str:
    """Format bytes as human-readable size."""
    size: float = float(size_bytes)
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def get_dir_size(path: Path) -> int:
    """Get total size of a directory."""
    total = 0
    try:
        for entry in path.rglob("*"):
            if entry.is_file():
                total += entry.stat().st_size
    except (PermissionError, OSError):
        pass
    return total


def is_inside_any_dir(file_path: Path, dirs: list[Path]) -> bool:
    """Check if a file is inside any of the given directories."""
    for d in dirs:
        try:
            file_path.relative_to(d)
            return True
        except ValueError:
            continue
    return False


def clean(dry_run: bool = False, include_venv: bool = False) -> None:
    """Remove temporary and ignored files."""
    root = find_project_root()
    print(f"🧹 Cleaning project: {root}")
    print()

    if include_venv:
        print("⚠️  --all flag set: .venv will also be removed!")
        print()

    dirs = find_dirs_to_clean(root, include_venv=include_venv)
    all_files = find_files_to_clean(root)

    # Filter out files that are inside directories we're already deleting
    files = [f for f in all_files if not is_inside_any_dir(f, dirs)]

    if not dirs and not files:
        print("✨ Already clean! Nothing to remove.")
        return

    total_size = 0

    # Process directories
    if dirs:
        print("📁 Directories to remove:")
        for d in dirs:
            rel_path = d.relative_to(root)
            size = get_dir_size(d)
            total_size += size
            print(f"   {rel_path}/ ({format_size(size)})")

            if not dry_run:
                try:
                    shutil.rmtree(d)
                except (PermissionError, OSError) as e:
                    print(f"   ⚠️  Failed to remove {rel_path}: {e}")
        print()

    # Process files (only orphan files not inside deleted directories)
    if files:
        print("📄 Files to remove:")
        for f in files:
            rel_path = f.relative_to(root)
            try:
                size = f.stat().st_size
                total_size += size
            except (PermissionError, OSError):
                size = 0
            print(f"   {rel_path} ({format_size(size)})")

            if not dry_run:
                try:
                    f.unlink()
                except (PermissionError, OSError) as e:
                    print(f"   ⚠️  Failed to remove {rel_path}: {e}")
        print()

    # Summary
    if dry_run:
        print(f"🔍 Dry run complete. Would free {format_size(total_size)}")
        print("   Run without --dry-run to actually delete these files.")
    else:
        print(f"✅ Cleaned! Freed {format_size(total_size)}")


def main() -> None:
    """Entry point for the clean script."""
    parser = argparse.ArgumentParser(
        description="Remove temporary and ignored files from the project.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    uv run clean              # Remove all temporary files
    uv run clean --dry-run    # Preview what would be deleted
    uv run clean --all        # Also remove .venv directory

Preserved files (never deleted):
    .env, .env.*, .envrc, .python-version, .tool-versions,
    .editorconfig, .vscode/, .idea/, *.local, *.local.*
        """,
    )
    parser.add_argument(
        "--dry-run",
        "-n",
        action="store_true",
        help="Show what would be deleted without actually deleting",
    )
    parser.add_argument(
        "--all",
        "-a",
        action="store_true",
        help="Also remove .venv directory (use with caution!)",
    )

    args = parser.parse_args()
    clean(dry_run=args.dry_run, include_venv=args.all)


if __name__ == "__main__":
    main()
