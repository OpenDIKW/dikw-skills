"""Console entry points."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .build import build_dist
from .sync import check_sync, sync_plugin
from .validate import validate_repo


def _root(value: str | None) -> Path:
    return Path(value).resolve() if value else Path.cwd()


def validate_main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root")
    args = parser.parse_args(argv)
    result = validate_repo(_root(args.root))
    if result.errors:
        for error in result.errors:
            print(f"error: {error}", file=sys.stderr)
        return 1
    print("dikw-skills validation passed")
    return 0


def sync_plugin_main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    root = _root(args.root)
    if args.check:
        result = check_sync(root)
        if result.errors:
            for error in result.errors:
                print(f"error: {error}", file=sys.stderr)
            return 1
        print("plugin skill copies are in sync")
        return 0
    sync_plugin(root)
    print("plugin skill copies synced")
    return 0


def build_main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root")
    parser.add_argument("--dist")
    args = parser.parse_args(argv)
    artifacts = build_dist(_root(args.root), Path(args.dist) if args.dist else None)
    for artifact in artifacts:
        print(artifact)
    return 0


if __name__ == "__main__":
    raise SystemExit(validate_main())
