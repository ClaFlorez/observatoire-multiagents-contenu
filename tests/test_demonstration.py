import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from observatoire.demonstration import ROLES, SCENARIOS, simuler
from observatoire.import_youtube import analyser
from observatoire.stockage import enregistrer_demonstration, lire_demonstrations


ROOT = Path(__file__).resolve().parents[1]


class DemonstrationTests(unittest.TestCase):
    def test_zero_network_and_verifiable_result(self):
        data = analyser(ROOT / 'data' / 'examples', 'fictive')
        with patch('socket.create_connection', side_effect=AssertionError('Réseau interdit')), patch.dict('os.environ', {'OPENAI_API_KEY': 'secret_de_test_ne_pas_lire'}):
            trace = simuler(data, SCENARIOS[0])
        self.assertFalse(trace['eligible_campagne_reelle'])
        self.assertEqual(trace['mode'], 'simulation')
        self.assertEqual(trace['appels_modele'], 0)
        self.assertEqual(trace['cout_api_usd'], 0)
        self.assertEqual({s['agent'] for s in trace['etapes']}, set(ROLES))
        self.assertEqual(len(trace['messages']), 4)
        self.assertEqual(trace['etapes'][2]['sortie']['total'], 45)
        self.assertEqual(trace['etapes'][2]['sortie']['part_du_total_pct'], 30 / 45 * 100)
        self.assertIn('CA', trace['resultat'])
        self.assertNotIn('secret_de_test', str(trace))
        self.assertTrue(all(s['duree_ms'] >= 0 for s in trace['etapes']))

    def test_bad_totals_are_not_validated(self):
        data = analyser(ROOT / 'data' / 'examples', 'fictive')
        data['donnees']['Totals.csv'][0]['Engaged views'] += 1
        trace = simuler(data, SCENARIOS[1])
        self.assertEqual(trace['etat'], 'non_validee')
        self.assertIn('Examiner les exports', trace['resultat'])

    def test_storage_is_separate_and_deduplicated(self):
        trace = simuler(analyser(ROOT / 'data' / 'examples', 'fictive'), SCENARIOS[1])
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / 'local.sqlite'
            self.assertEqual(lire_demonstrations(database), [])
            enregistrer_demonstration(trace, database)
            enregistrer_demonstration(trace, database)
            self.assertEqual(lire_demonstrations(database), [trace])
            with self.assertRaises(ValueError):
                enregistrer_demonstration({'mode': 'reel'}, database)


class DemoInterfaceTests(unittest.TestCase):
    def test_simulation_and_replay(self):
        from streamlit.testing.v1 import AppTest

        with tempfile.TemporaryDirectory() as directory:
            source = (ROOT / 'app.py').read_text(encoding='utf-8')
            source = source.replace('ROOT = Path(__file__).resolve().parent', f'ROOT = Path({str(ROOT)!r})')
            source = source.replace("DATABASE = ROOT / 'data' / 'private' / 'observatoire.sqlite'", f'DATABASE = Path({str(Path(directory) / "test.sqlite")!r})')
            app = AppTest.from_string(source, default_timeout=15).run()
            app.button(key='charger_csv').click().run()
            app.button(key='simuler_roles').click().run()
            self.assertEqual(len(app.exception), 0)
            self.assertEqual(len(app.get('plotly_chart')), 4)  # audience + graphe et timeline
            trace = lire_demonstrations(Path(directory) / 'test.sqlite')[0]
            app.slider(key=f"relecture_{trace['id']}").set_value(5).run()
            self.assertEqual(len(app.exception), 0)
            self.assertEqual(len(app.get('plotly_chart')), 5)  # ajout du Sankey
            self.assertTrue(any('0 exécution IA réelle' in text.value for text in app.caption))
            app.multiselect(key='demo_roles').set_value([]).run()
            self.assertEqual(len(app.exception), 0)
            self.assertEqual(len(app.get('plotly_chart')), 2)
            app.multiselect(key='demo_scenarios').set_value([]).run()
            self.assertEqual(len(app.exception), 0)
