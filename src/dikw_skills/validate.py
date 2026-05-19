"""Repository validation for DIKW skills packaging."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

from .catalog import EXPECTED_SKILLS, PLUGIN_DIR, PLUGIN_NAME, iter_owned_commands
from .sync import check_sync


@dataclass(frozen=True)
class ValidationResult:
    errors: list[str]

    @property
    def ok(self) -> bool:
        return not self.errors


def _parse_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}
    try:
        _, frontmatter, _ = text.split("---\n", 2)
    except ValueError:
        return {}
    data: dict[str, str] = {}
    for line in frontmatter.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"')
    return data


def validate_repo(root: str | Path) -> ValidationResult:
    root = Path(root)
    errors: list[str] = []

    for skill_name, commands in EXPECTED_SKILLS.items():
        skill_path = root / "skills" / skill_name / "SKILL.md"
        if not skill_path.exists():
            errors.append(f"{skill_name}: missing SKILL.md")
            continue

        frontmatter = _parse_frontmatter(skill_path)
        if frontmatter.get("name") != skill_name:
            errors.append(f"{skill_name}: frontmatter name must be {skill_name!r}")
        if not frontmatter.get("description"):
            errors.append(f"{skill_name}: frontmatter description is required")

        text = skill_path.read_text(encoding="utf-8")
        for command in commands:
            marker = f"dikw client {command}"
            if marker not in text:
                errors.append(f"{skill_name}: missing command marker {marker!r}")

    seen: dict[str, str] = {}
    for skill_name, command in iter_owned_commands():
        if command in seen:
            errors.append(
                f"duplicate command ownership for {command!r}: {seen[command]}, {skill_name}"
            )
        seen[command] = skill_name

    plugin_json = root / PLUGIN_DIR / ".codex-plugin" / "plugin.json"
    if not plugin_json.exists():
        errors.append("plugin manifest missing")
    else:
        try:
            plugin = json.loads(plugin_json.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"plugin manifest invalid JSON: {exc}")
        else:
            if plugin.get("name") != PLUGIN_NAME:
                errors.append(f"plugin manifest name must be {PLUGIN_NAME!r}")
            if plugin.get("skills") != "./skills/":
                errors.append("plugin manifest skills path must be './skills/'")

    marketplace = root / ".agents" / "plugins" / "marketplace.json"
    if not marketplace.exists():
        errors.append("marketplace.json missing")
    else:
        try:
            data = json.loads(marketplace.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"marketplace.json invalid JSON: {exc}")
        else:
            entries = data.get("plugins", [])
            matching = [entry for entry in entries if entry.get("name") == PLUGIN_NAME]
            if not matching:
                errors.append("marketplace entry for dikw-skills missing")
            elif matching[0].get("source", {}).get("path") != "./plugins/dikw-skills":
                errors.append("marketplace path must be './plugins/dikw-skills'")

    errors.extend(check_sync(root).errors)
    return ValidationResult(errors)
