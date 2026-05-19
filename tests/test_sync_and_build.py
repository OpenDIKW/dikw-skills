from pathlib import Path
import json
import shutil
import tempfile
import unittest
import zipfile

from dikw_skills import build, sync


ROOT = Path(__file__).resolve().parents[1]


class SyncAndBuildTests(unittest.TestCase):
    def test_plugin_skill_copy_is_in_sync(self) -> None:
        result = sync.check_sync(ROOT)
        self.assertEqual(result.errors, [])

    def test_build_creates_expected_release_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = (Path(tmp) / "dist").resolve()
            artifacts = build.build_dist(ROOT, out_dir)

            expected_files = {
                out_dir / "skills" / "dikw-client-observe.zip",
                out_dir / "skills" / "dikw-client-retrieve.zip",
                out_dir / "skills" / "dikw-client-import.zip",
                out_dir / "skills" / "dikw-client-curate.zip",
                out_dir / "skills" / "dikw-client-utils.zip",
                out_dir / "plugins" / "dikw-skills-plugin.zip",
                out_dir / "site" / ".well-known" / "skills" / "index.json",
                out_dir / "site" / ".well-known" / "agent-skills" / "index.json",
                out_dir / "checksums.txt",
            }

            self.assertTrue(expected_files.issubset(set(artifacts)))
            with zipfile.ZipFile(out_dir / "plugins" / "dikw-skills-plugin.zip") as zf:
                names = set(zf.namelist())
            self.assertIn("dikw-skills/.codex-plugin/plugin.json", names)
            self.assertIn("dikw-skills/skills/dikw-client-retrieve/SKILL.md", names)

    def test_registry_archive_paths_resolve_to_built_skill_archives(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = (Path(tmp) / "dist").resolve()
            build.build_dist(ROOT, out_dir)
            index_path = out_dir / "site" / ".well-known" / "skills" / "index.json"
            payload = json.loads(index_path.read_text(encoding="utf-8"))

            for skill in payload["skills"]:
                archive = (index_path.parent / skill["archive"]).resolve()
                self.assertTrue(archive.exists(), skill["archive"])

    def test_build_rejects_dangerous_output_directories(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            for name in ["skills", "plugins", "references", ".agents", "registry"]:
                shutil.copytree(ROOT / name, repo / name)

            for dangerous in [repo, repo / "src", repo / "skills", repo.parent]:
                with self.subTest(dangerous=dangerous):
                    with self.assertRaises(ValueError):
                        build.build_dist(repo, dangerous)


if __name__ == "__main__":
    unittest.main()
