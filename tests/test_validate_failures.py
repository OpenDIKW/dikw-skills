from pathlib import Path
import shutil
import tempfile
import unittest

from dikw_skills import sync
from dikw_skills.validate import validate_repo


ROOT = Path(__file__).resolve().parents[1]


class ValidationFailureTests(unittest.TestCase):
    def _copy_repo(self) -> Path:
        tmp = Path(tempfile.mkdtemp())
        for name in ["skills", "plugins", ".agents", "registry"]:
            src = ROOT / name
            if src.exists():
                shutil.copytree(src, tmp / name)
        return tmp

    def test_missing_skill_file_is_rejected(self) -> None:
        tmp = self._copy_repo()
        try:
            (tmp / "skills" / "dikw-client-observe" / "SKILL.md").unlink()
            result = validate_repo(tmp)
            self.assertTrue(any("missing SKILL.md" in error for error in result.errors))
        finally:
            shutil.rmtree(tmp)

    def test_bad_frontmatter_is_rejected(self) -> None:
        tmp = self._copy_repo()
        try:
            skill = tmp / "skills" / "dikw-client-observe" / "SKILL.md"
            skill.write_text("---\nname: wrong\n---\nbody\n", encoding="utf-8")
            result = validate_repo(tmp)
            self.assertTrue(any("description" in error for error in result.errors))
        finally:
            shutil.rmtree(tmp)

    def test_stale_plugin_copy_is_rejected(self) -> None:
        tmp = self._copy_repo()
        try:
            plugin_skill = (
                tmp
                / "plugins"
                / "dikw-skills"
                / "skills"
                / "dikw-client-utils"
                / "SKILL.md"
            )
            plugin_skill.write_text(plugin_skill.read_text(encoding="utf-8") + "\nSTALE\n")
            result = sync.check_sync(tmp)
            self.assertTrue(any("stale plugin copy" in error for error in result.errors))
        finally:
            shutil.rmtree(tmp)


if __name__ == "__main__":
    unittest.main()
