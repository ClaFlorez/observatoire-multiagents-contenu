import csv
from decimal import Decimal
from pathlib import Path
import tempfile
import unittest

from observatoire.import_videos import COLUMNS, importer_videos
from observatoire.import_youtube import ImportInvalide


class VideoImportTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.path = Path(self.folder.name) / 'Table data.csv'
        self.rows = [
            ['Total', '', '', '', '100', '1.0000', '1', '0:00:36', '500', '2'],
            ['video000001', 'Exemple fictif, vidéo A', 'Sep 18, 2026', '120', '100', '1.0001', '1', '0:00:36', '400', '2.5'],
            ['video000002', 'Exemple fictif B', '', '30', '', '', '', '', '100', ''],
        ]
        self.write()

    def write(self):
        with self.path.open('w', encoding='utf-8', newline='') as handle:
            writer = csv.writer(handle)
            writer.writerow(COLUMNS)
            writer.writerows(self.rows)

    def load(self):
        return importer_videos(self.path, '2026-09-17', '2026-10-14', 'fictive')

    def test_missing_values_and_rounding_are_preserved(self):
        data = self.load()
        self.assertEqual(len(data['videos']), 2)
        self.assertEqual(data['videos'][0]['publication'], '2026-09-18')
        self.assertIsNone(data['videos'][1]['publication'])
        self.assertIsNone(data['videos'][1]['vues'])
        self.assertIsNone(data['videos'][1]['ctr_pct'])
        self.assertEqual(data['total']['vues'], 100)
        self.assertEqual(data['rapprochements'][1]['ecart_total_details'], Decimal('-0.0001'))
        self.assertEqual(data['rapprochements'][0]['valeurs_absentes'], 1)
        self.assertEqual(data['periode']['source'], 'declaration_utilisateur')

    def test_period_is_not_inferred_from_publication(self):
        data = importer_videos(self.path, '2026-10-01', '2026-10-14', 'fictive')
        self.assertEqual(len(data['videos']), 2)
        self.assertEqual(data['videos'][0]['publication'], '2026-09-18')
        with self.assertRaises(ImportInvalide):
            importer_videos(self.path, '2026-10-14', '2026-09-17', 'fictive')

    def test_duplicate_video_refused(self):
        self.rows.append(self.rows[1])
        self.write()
        with self.assertRaisesRegex(ImportInvalide, 'dupliqué'):
            self.load()

    def test_playlist_schema_refused(self):
        self.path.write_text('Date,Playlist,Views from playlist\n2026-09-17,playlist,2\n', encoding='utf-8')
        with self.assertRaisesRegex(ImportInvalide, 'Colonnes'):
            self.load()

    def test_invalid_number_or_date_refused(self):
        for value in ('NaN', '-1', '1.5'):
            with self.subTest(value=value):
                self.rows[1][4] = value
                self.write()
                with self.assertRaises(ImportInvalide):
                    self.load()
        self.rows[1][4] = '100'
        self.rows[1][2] = 'Feb 30, 2026'
        self.write()
        with self.assertRaises(ImportInvalide):
            self.load()

    def test_interface_requires_period_confirmation_and_separates_agents(self):
        from streamlit.testing.v1 import AppTest

        root = Path(__file__).resolve().parents[1]
        source = (root / 'app.py').read_text(encoding='utf-8')
        source = source.replace('ROOT = Path(__file__).resolve().parent', f'ROOT = Path({str(root)!r})')
        source = source.replace("DATABASE = ROOT / 'data' / 'private' / 'observatoire.sqlite'", f'DATABASE = Path({str(Path(self.folder.name) / "test.sqlite")!r})')
        app = AppTest.from_string(source, default_timeout=15).run()
        app.selectbox(key='type_rapport').set_value('Contenu par vidéo').run()
        app.text_input(key='video_fichier').set_value(str(self.path)).run()
        app.selectbox(key='video_origine').set_value('fictive').run()
        app.button(key='charger_videos').click().run()
        self.assertTrue(app.error)
        app.checkbox(key='video_confirmation').check().run()
        app.button(key='charger_videos').click().run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(app.metric[0].value, '2')
        self.assertEqual(app.metric[1].value, '100')
        self.assertFalse(any(button.key == 'lancer_agents_locaux' for button in app.button))
        self.assertTrue(any(button.key == 'lancer_agents_locaux_videos' for button in app.button))
        app.text_input(key='video_recherche').set_value('introuvable').run()
        self.assertEqual(len(app.exception), 0)
        # Le classement filtré disparaît ; S1 conserve les deux classements de l’import complet.
        self.assertEqual(len(app.get('plotly_chart')), 2)
        self.assertTrue(any(button.key == 'lancer_agents_locaux_S1' for button in app.button))
