"""Sync canonical skills into the plugin wrapper."""

from __future__ import annotations

from dataclasses import dataclass
from filecmp import cmp
from pathlib import Path
import shutil

from .catalog import EXPECTED_SKILLS, PLUGIN_DIR


@dataclass(frozen=True)
class SyncResult:
    errors: list[str]

    @property
    def ok(self) -> bool:
        return not self.errors


def _copy_tree(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def sync_plugin(root: str | Path) -> None:
    root = Path(root)
    plugin_root = root / PLUGIN_DIR
    plugin_root.mkdir(parents=True, exist_ok=True)
    _copy_tree(root / "skills", plugin_root / "skills")


def _same_tree(src: Path, dst: Path) -> list[str]:
    errors: list[str] = []
    if not dst.exists():
        return [f"missing plugin copy: {dst}"]
    src_files = sorted(path.relative_to(src) for path in src.rglob("*") if path.is_file())
    dst_files = sorted(path.relative_to(dst) for path in dst.rglob("*") if path.is_file())
    if src_files != dst_files:
        errors.append(f"stale plugin copy: file list differs for {dst}")
        return errors
    for rel in src_files:
        if not cmp(src / rel, dst / rel, shallow=False):
            errors.append(f"stale plugin copy: {dst / rel}")
    return errors


def check_sync(root: str | Path) -> SyncResult:
    root = Path(root)
    errors: list[str] = []
    plugin_root = root / PLUGIN_DIR
    for skill_name in EXPECTED_SKILLS:
        src = root / "skills" / skill_name
        dst = plugin_root / "skills" / skill_name
        if not src.exists():
            errors.append(f"missing canonical skill: {src}")
            continue
        errors.extend(_same_tree(src, dst))
    return SyncResult(errors)
