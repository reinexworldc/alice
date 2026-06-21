import unittest

from core.providers.config import ProvidersConfig


class ProvidersConfigTests(unittest.TestCase):
    def test_openai_models_prioritize_latest_family(self):
        models = ProvidersConfig.available_models("openai")

        self.assertEqual(models[0], "gpt-5.5")
        self.assertIn("gpt-5.4-mini", models)
        self.assertIn("gpt-4.1", models)
        self.assertIn("gpt-4o-mini", models)
        self.assertIn("o4-mini", models)

    def test_openai_model_menu_excludes_specialized_api_models(self):
        models = ProvidersConfig.available_models("openai")

        excluded_fragments = (
            "audio",
            "codex",
            "image",
            "realtime",
            "search",
            "transcribe",
            "tts",
        )
        for model in models:
            self.assertFalse(any(fragment in model for fragment in excluded_fragments))

        self.assertNotIn("gpt-5.5-pro", models)


if __name__ == "__main__":
    unittest.main()
