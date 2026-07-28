import unittest

from src.rag import build_prompt, format_context, retrieve_context, run_rag


class RagTest(unittest.TestCase):
    def test_prompt_contains_guardrails_and_context(self) -> None:
        context = retrieve_context(
            "What datasets are available for KRAS G12C research in NSCLC?",
            catalog_path="data/processed/seed_catalog.json",
            top_k=2,
        )
        prompt = build_prompt(context.question, format_context(context.question, context.retrieved))

        self.assertIn("Do not provide medical advice", prompt)
        self.assertIn("Do not claim", prompt)
        self.assertIn("Do not use outside biomedical knowledge", prompt)
        self.assertIn("Cite catalog entries", prompt)
        self.assertIn("gdc:TCGA", prompt)
        self.assertIn("limitations", prompt)

    def test_dry_run_returns_prompt_and_fallback_answer(self) -> None:
        output = run_rag(
            "What datasets are available for KRAS G12C research in NSCLC?",
            catalog_path="data/processed/seed_catalog.json",
            top_k=2,
            live=False,
        )

        self.assertIn("DRY RUN", output)
        self.assertIn("Prompt preview", output)
        self.assertIn("Deterministic fallback answer", output)
        self.assertIn("not clinical recommendations", output)


if __name__ == "__main__":
    unittest.main()
