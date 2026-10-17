import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from observatoire.import_youtube import analyser
from observatoire.outils_audience import calculer_audience
from observatoire.securite_locale import environnement_local, verifier_evenement
from observatoire.stockage import enregistrer_execution_reelle, lire_demonstrations, lire_executions_reelles


class AgentsLocauxTests(unittest.TestCase):
    def test_security_rejects_external_connections_and_secret_files(self):
        verifier_evenement('socket.connect', (None, ('127.0.0.1', 11434)))
        for address in [('api.openai.com', 443), ('8.8.8.8', 443), ('127.0.0.1', 9999)]:
            with self.subTest(address=address), self.assertRaises(PermissionError):
                verifier_evenement('socket.connect', (None, address))
        with self.assertRaises(PermissionError):
            verifier_evenement('socket.getaddrinfo', ('api.openai.com', 443))
        for name in ('.env', '/secret/.env.local', 'secrets.toml'):
            with self.assertRaises(PermissionError):
                verifier_evenement('open', (name, 'r', 0))

    def test_worker_environment_removes_key_without_modifying_parent(self):
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'valeur_fictive', 'GROQ_API_KEY': 'autre_fictive'}):
            env = environnement_local(Path.cwd())
            self.assertNotIn('OPENAI_API_KEY', env)
            self.assertNotIn('GROQ_API_KEY', env)
            self.assertEqual(os.environ['OPENAI_API_KEY'], 'valeur_fictive')
            self.assertEqual(env['PYTHON_DOTENV_DISABLED'], '1')
            self.assertEqual(env['CREWAI_DISABLE_TELEMETRY'], 'true')

    def test_tool_uses_global_denominator_and_keeps_gap(self):
        data = analyser(Path(__file__).resolve().parents[1] / 'data' / 'examples', 'fictive')
        metrics = calculer_audience(data)
        self.assertEqual(metrics['total'], 45)
        self.assertEqual(metrics['ecart_non_explique'], 10)
        self.assertEqual(metrics['pays_en_tete'], 'CA')
        self.assertEqual(metrics['part_du_total_pct'], 66.67)
        for row in data['donnees']['Table data.csv']:
            row['Engaged views'] = 0
        self.assertIsNone(calculer_audience(data)['part_du_total_pct'])

    def test_real_trace_stays_separate_and_updates_same_run(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'trace.sqlite'
            self.assertEqual(lire_executions_reelles(path), [])
            trace = {'id': 'test', 'mode': 'ia_locale', 'orchestrateur': 'CrewAI', 'etat': 'en_cours'}
            enregistrer_execution_reelle(trace, path)
            trace['etat'] = 'echouee'
            enregistrer_execution_reelle(trace, path)
            self.assertEqual(lire_executions_reelles(path), [trace])
            self.assertEqual(lire_demonstrations(path), [])
            with self.assertRaises(ValueError):
                enregistrer_execution_reelle({'mode': 'simulation'}, path)
