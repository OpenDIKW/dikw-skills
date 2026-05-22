"""Build distributable skill, plugin, and registry artifacts."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

from .catalog import EXPECTED_SKILLS, PLUGIN_DIR, PLUGIN_NAME
from .sync import sync_plugin


@dataclass(frozen=True)
class RegistryEntry:
    name: str
    path: str
    description: str


def _zip_dir(src: Path, dest: Path, prefix: str | None = None) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(dest, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(src.rglob("*")):
            if not path.is_file():
                continue
            rel = path.relative_to(src)
            arcname = Path(prefix) / rel if prefix else rel
            zf.write(path, arcname.as_posix())


def _skill_description(skill_md: Path) -> str:
    text = skill_md.read_text(encoding="utf-8")
    if text.startswith("---\n"):
        _, frontmatter, _ = text.split("---\n", 2)
        for line in frontmatter.splitlines():
            if line.startswith("description:"):
                return line.split(":", 1)[1].strip().strip('"')
    return ""


def _write_registry(root: Path, out_dir: Path) -> list[Path]:
    entries = [
        {
            "name": name,
            "archive": f"../../../skills/{name}.zip",
            "path": f"skills/{name}",
            "description": _skill_description(root / "skills" / name / "SKILL.md"),
        }
        for name in EXPECTED_SKILLS
    ]
    payload = {
        "name": PLUGIN_NAME,
        "version": "0.1.0",
        "skills": entries,
    }
    paths = [
        out_dir / "site" / ".well-known" / "skills" / "index.json",
        out_dir / "site" / ".well-known" / "agent-skills" / "index.json",
    ]
    for path in paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return paths


def _write_checksums(files: list[Path], out_dir: Path) -> Path:
    checksums = out_dir / "checksums.txt"
    lines = []
    for path in sorted(files):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append(f"{digest}  {path.relative_to(out_dir).as_posix()}")
    checksums.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return checksums


def _safe_output_dir(root: Path, out_dir: Path) -> Path:
    root = root.resolve()
    out_dir = out_dir.resolve(strict=False)

    if out_dir == root or out_dir in root.parents:
        raise ValueError(f"refusing to build into repository root or parent: {out_dir}")

    protected = [
        root / "src",
        root / "skills",
        root / "plugins",
        root / "tests",
        root / ".agents",
        root / "registry",
    ]
    for path in protected:
        path = path.resolve(strict=False)
        if out_dir == path or path in out_dir.parents:
            raise ValueError(f"refusing to build inside source directory: {out_dir}")

    return out_dir


def build_dist(root: str | Path, out_dir: str | Path | None = None) -> list[Path]:
    root = Path(root).resolve()
    requested_out_dir = Path(out_dir) if out_dir is not None else root / "dist"
    out_dir = _safe_output_dir(root, requested_out_dir)
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)

    sync_plugin(root)

    artifacts: list[Path] = []
    for skill_name in EXPECTED_SKILLS:
        dest = out_dir / "skills" / f"{skill_name}.zip"
        _zip_dir(root / "skills" / skill_name, dest, prefix=skill_name)
        artifacts.append(dest)

    plugin_zip = out_dir / "plugins" / "dikw-skills-plugin.zip"
    _zip_dir(root / PLUGIN_DIR, plugin_zip, prefix=PLUGIN_NAME)
    artifacts.append(plugin_zip)
    artifacts.extend(_write_registry(root, out_dir))
    artifacts.append(_write_checksums(artifacts, out_dir))
    return artifacts
