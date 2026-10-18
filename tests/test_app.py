import importlib.util
import tempfile
import unittest
from datetime import date
from pathlib import Path


@unittest.skipUnless(importlib.util.find_spec('streamlit'), 'Installer les dépendances de l’interface')
class InterfaceTests(unittest.TestCase):
    def test_load_filter_and_invalid_source(self):
        from streamlit.testing.v1 import AppTest

        root = Path(__file__).resolve().parents[1]
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        source = (root / 'app.py').read_text(encoding='utf-8')
        source = source.replace('ROOT = Path(__file__).resolve().parent', f'ROOT = Path({str(root)!r})')
        source = source.replace("DATABASE = ROOT / 'data' / 'private' / 'observatoire.sqlite'", f'DATABASE = Path({str(Path(temporary.name) / "test.sqlite")!r})')
        app = AppTest.from_string(source, default_timeout=15).run()
        self.assertEqual(len(app.exception), 0)
        app.button(key='charger_csv').click().run()
        self.assertEqual(len(app.exception), 0)
        navigation = '\n'.join(item.value for item in app.sidebar.markdown)
        self.assertIn('href="#tableau-de-bord"', navigation)
        self.assertIn('href="#agents-audience"', navigation)
        self.assertEqual(app.metric[0].label, 'Exécutions IA locales enregistrées')
        self.assertEqual(app.metric[3].value, '45')
        self.assertEqual(app.metric[4].value, '35')
        self.assertEqual(len(app.get('plotly_chart')), 2)
        app.multiselect[0].set_value(['CA']).run()
        self.assertEqual(app.metric[3].value, '45')
        self.assertEqual(app.metric[4].value, '30')
        app.date_input[0].set_value((date(2026, 1, 1), date(2026, 1, 1))).run()
        self.assertEqual(app.metric[3].value, '20')
        self.assertEqual(app.metric[4].value, '10')
        app.multiselect[0].set_value([]).run()
        self.assertEqual(len(app.get('plotly_chart')), 0)
        self.assertEqual(len(app.exception), 0)
        app.text_input[0].set_value('dossier_absent').run()
        app.button(key='charger_csv').click().run()
        self.assertTrue(app.error)
        self.assertEqual(len(app.metric), 3)  # Résumé de la base, indépendant de l’import invalide.
        self.assertEqual(len(app.exception), 0)
