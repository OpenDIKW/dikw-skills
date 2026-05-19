"""Canonical skill and command ownership catalog."""

from __future__ import annotations

from collections.abc import Iterator

PLUGIN_NAME = "dikw-skills"
PLUGIN_DIR = "plugins/dikw-skills"

EXPECTED_SKILLS: dict[str, tuple[str, ...]] = {
    "dikw-client-observe": (
        "info",
        "status",
        "health",
        "check",
    ),
    "dikw-client-retrieve": (
        "retrieve",
        "pages list",
        "pages get",
        "pages links",
        "graph get",
        "assets get",
    ),
    "dikw-client-import": ("import",),
    "dikw-client-curate": (
        "ingest",
        "synth",
        "distill",
        "eval",
        "lint",
        "lint propose",
        "lint proposals",
        "lint apply",
        "review list",
        "review approve",
        "review reject",
    ),
    "dikw-client-utils": (
        "tasks list",
        "tasks status",
        "tasks events",
        "tasks wait",
        "tasks cancel",
        "serve-and-run",
    ),
}


def iter_owned_commands() -> Iterator[tuple[str, str]]:
    for skill_name, commands in EXPECTED_SKILLS.items():
        for command in commands:
            yield skill_name, command
