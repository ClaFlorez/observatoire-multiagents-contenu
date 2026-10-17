import io
import json
import unittest
from unittest.mock import patch

from observatoire.essai_local import SansRedirection, essai_local


class LocalInferenceTests(unittest.TestCase):
    def test_cpu_loopback_and_real_token_counts(self):
        answer = {
            'model': 'qwen3:4b', 'done': True,
            'response': '{"pays":"CA","justification":"Le volume est supérieur."}',
            'prompt_eval_count': 80, 'eval_count': 20,
            'total_duration': 5_000_000_000, 'load_duration': 1_000_000_000,
            'eval_duration': 2_000_000_000,
        }
        with patch('observatoire.essai_local.build_opener') as builder:
            builder.return_value.open.return_value = io.BytesIO(json.dumps(answer).encode())
            report = essai_local()
            request = builder.return_value.open.call_args.args[0]
            self.assertEqual(request.full_url, 'http://127.0.0.1:11434/api/generate')
            self.assertNotIn('Authorization', request.headers)
            payload = json.loads(request.data)
            self.assertEqual(payload['options']['num_gpu'], 0)
            self.assertFalse(payload['think'])
        self.assertTrue(report['controle_pays'])
        self.assertEqual(report['jetons_entree'], 80)
        self.assertEqual(report['jetons_sortie'], 20)
        self.assertEqual(report['duree_totale_s'], 5)
        self.assertFalse(report['eligible_campagne_multiagents'])

    def test_partial_response_refused(self):
        with patch('observatoire.essai_local.build_opener') as builder:
            builder.return_value.open.return_value = io.BytesIO(b'{"done":false,"response":"{}"}')
            with self.assertRaises(ValueError):
                essai_local()

    def test_redirects_refused(self):
        with self.assertRaisesRegex(ValueError, 'Redirection interdite'):
            SansRedirection().redirect_request(None, None, 302, '', {}, 'https://example.org')
