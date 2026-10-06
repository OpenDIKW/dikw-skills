from pathlib import Path
import unittest

from dikw_skills.catalog import EXPECTED_SKILLS, iter_owned_commands
from dikw_skills.validate import validate_repo


ROOT = Path(__file__).resolve().parents[1]


class CatalogTests(unittest.TestCase):
    def test_all_client_commands_have_one_owner(self) -> None:
        expected = {
            "info",
            "status",
            "health",
            "check",
            "retrieve",
            "pages list",
            "pages get",
            "pages links",
            "pages provenance",
            "graph get",
            "assets get",
            "import",
            "ingest",
            "synth",
            "eval",
            "lint",
            "lint propose",
            "lint proposals",
            "lint apply",
            "delete",
            "wisdom write",
            "tasks list",
            "tasks status",
            "tasks events",
            "tasks wait",
            "tasks cancel",
            "serve-and-run",
        }
        ownership = list(iter_owned_commands())
        commands = [command for _, command in ownership]

        self.assertEqual(set(commands), expected)
        self.assertEqual(len(commands), len(set(commands)))

    def test_planned_skill_names_are_present(self) -> None:
        self.assertEqual(
            set(EXPECTED_SKILLS),
            {
                "dikw-client-observe",
                "dikw-client-retrieve",
                "dikw-client-import",
                "dikw-client-curate",
                "dikw-client-utils",
            },
        )

    def test_skill_files_contain_their_owned_commands(self) -> None:
        for skill_name, commands in EXPECTED_SKILLS.items():
            text = (ROOT / "skills" / skill_name / "SKILL.md").read_text(encoding="utf-8")
            for command in commands:
                self.assertIn(f"dikw client {command}", text)

    def test_skills_do_not_cite_removed_commands_or_paths(self) -> None:
        # dikw-core 0.4.0 renamed the K-layer tree wiki/ -> knowledge/; the W layer
        # became hand-written (`wisdom write`), so `distill` and `review *` are gone.
        removed = ["dikw client distill", "dikw client review", " wiki/", "`wiki/"]
        for skill_name in EXPECTED_SKILLS:
            text = (ROOT / "skills" / skill_name / "SKILL.md").read_text(encoding="utf-8")
            for marker in removed:
                self.assertNotIn(marker, text, f"{skill_name} cites {marker!r}")

    def test_versions_are_consistent(self) -> None:
        import re

        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        version = re.search(r'^version = "([^"]+)"', pyproject, re.M).group(1)
        for rel in [
            ".claude-plugin/marketplace.json",
            "plugins/dikw-skills/.claude-plugin/plugin.json",
            "plugins/dikw-skills/.codex-plugin/plugin.json",
            "registry/hermes.json",
            "registry/openclaw.json",
        ]:
            text = (ROOT / rel).read_text(encoding="utf-8")
            self.assertIn(f'"version": "{version}"', text, rel)
        uv_lock = (ROOT / "uv.lock").read_text(encoding="utf-8")
        self.assertIn(f'name = "dikw-skills"\nversion = "{version}"', uv_lock)
        from dikw_skills import build

        self.assertEqual(build.PACKAGE_VERSION, version)

    def test_repo_validation_passes(self) -> None:
        result = validate_repo(ROOT)
        self.assertEqual(result.errors, [])

    def test_openai_metadata_uses_interface_schema(self) -> None:
        for skill_name in EXPECTED_SKILLS:
            path = ROOT / "skills" / skill_name / "agents" / "openai.yaml"
            lines = path.read_text(encoding="utf-8").splitlines()

            self.assertEqual(lines[0], "interface:")
            self.assertTrue(any(line.startswith('  display_name: "') for line in lines))
            short = next(line for line in lines if line.startswith('  short_description: "'))
            # Codex's agents/openai.yaml schema allows 25-64 characters.
            text = short.split('"', 1)[1].rsplit('"', 1)[0]
            self.assertTrue(25 <= len(text) <= 64, f"{skill_name}: {len(text)} chars")
            default_prompt = next(
                line for line in lines if line.startswith('  default_prompt: "')
            )
            self.assertIn(f"${skill_name}", default_prompt)


if __name__ == "__main__":
    unittest.main()
