from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class SkillDocumentationTests(unittest.TestCase):
    def test_import_skill_documents_optional_converters(self) -> None:
        text = (ROOT / "skills" / "dikw-client-import" / "SKILL.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("dikw-converter-mineru", text)
        self.assertIn("dikw-converter-epub", text)
        self.assertIn("dikw client import", text)

    def test_curate_skill_owns_ingest_lint_review_and_eval(self) -> None:
        text = (ROOT / "skills" / "dikw-client-curate" / "SKILL.md").read_text(
            encoding="utf-8"
        )

        for command in [
            "dikw client ingest",
            "dikw client lint",
            "dikw client lint propose",
            "dikw client lint apply",
            "dikw client review list",
            "dikw client eval",
        ]:
            self.assertIn(command, text)

    def test_utils_skill_contains_full_task_lifecycle_sop(self) -> None:
        utils = (ROOT / "skills" / "dikw-client-utils" / "SKILL.md").read_text(
            encoding="utf-8"
        )

        for required in [
            "dikw client tasks list",
            "dikw client tasks status",
            "dikw client tasks events",
            "dikw client tasks wait",
            "dikw client tasks cancel",
            "dikw client serve-and-run",
            "task_id",
            "next_from_seq",
            "succeeded=0",
            "failed=1",
            "cancelled=130",
            "timeout=124",
        ]:
            self.assertIn(required, utils)

        for skill_name in [
            "dikw-client-observe",
            "dikw-client-retrieve",
            "dikw-client-import",
            "dikw-client-curate",
        ]:
            text = (ROOT / "skills" / skill_name / "SKILL.md").read_text(encoding="utf-8")
            self.assertNotIn("next_from_seq", text)


if __name__ == "__main__":
    unittest.main()
