import unittest
from config import Settings

class SettingsTests(unittest.TestCase):
    def test_missing_credentials_report_names_only(self):
        with self.assertRaisesRegex(ValueError, 'LIVEKIT_URL'):
            Settings.from_env({})

    def test_routes_mini_through_livekit_without_openai_key(self):
        env = dict.fromkeys(['LIVEKIT_URL', 'LIVEKIT_API_KEY', 'LIVEKIT_API_SECRET', 'DEEPGRAM_API_KEY', 'CARTESIA_API_KEY'], 'test')
        env['LIVEKIT_URL'] = 'wss://example.livekit.cloud'
        settings = Settings.from_env(env)
        self.assertEqual(settings.llm_model, 'openai/gpt-4o-mini')

    def test_rejects_non_websocket_url(self):
        env = dict.fromkeys(['LIVEKIT_URL', 'LIVEKIT_API_KEY', 'LIVEKIT_API_SECRET', 'DEEPGRAM_API_KEY', 'CARTESIA_API_KEY'], 'test')
        with self.assertRaisesRegex(ValueError, 'wss://'):
            Settings.from_env(env)

if __name__ == '__main__':
    unittest.main()
