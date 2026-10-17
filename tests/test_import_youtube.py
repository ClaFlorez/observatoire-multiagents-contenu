import shutil
import tempfile
import unittest
from pathlib import Path

from observatoire.import_youtube import ImportInvalide, analyser


EXAMPLE = Path(__file__).resolve().parents[1] / 'data' / 'examples'


class ImportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.source = Path(self.temp.name)
        for filename in ('Chart data.csv', 'Table data.csv', 'Totals.csv'):
            shutil.copyfile(EXAMPLE / filename, self.source / filename)

    def test_totals_are_separate_and_missing_is_not_zero(self):
        result = analyser(self.source, 'fictive')
        metrics = result['resume']['vues_engagees']
        self.assertEqual(metrics['details_par_pays'], 35)
        self.assertEqual(metrics['ligne_total'], 45)
        self.assertEqual(metrics['ecart_total_details'], 10)
        ca = result['donnees']['Table data.csv'][1]
        self.assertIsNone(ca['Playlist watch time (hours)'])
        self.assertEqual(ca['Card clicks'], 0)
        self.assertEqual(ca['Average view duration'], 90)
        self.assertEqual(result['donnees']['Table data.csv'][2]['Average percentage viewed (%)'], 125)
        self.assertTrue(any('100 %' in msg for msg in result['resume']['avertissements']))

    def test_duplicate_refused(self):
        with (self.source / 'Chart data.csv').open('a', encoding='utf-8') as handle:
            handle.write('\n2026-01-01,CA,10\n')
        with self.assertRaisesRegex(ImportInvalide, 'doublon'):
            analyser(self.source, 'fictive')

    def test_missing_column_refused(self):
        (self.source / 'Totals.csv').write_text('Date,Views\n2026-01-01,20\n', encoding='utf-8')
        with self.assertRaisesRegex(ImportInvalide, 'colonnes absentes'):
            analyser(self.source, 'fictive')

    def test_non_finite_and_fractional_counts_refused(self):
        path = self.source / 'Totals.csv'
        for invalid in ('NaN', 'Infinity', '1.5', '-1'):
            with self.subTest(invalid=invalid):
                path.write_text(f'Date,Engaged views\n2026-01-01,{invalid}\n', encoding='utf-8')
                with self.assertRaises(ImportInvalide):
                    analyser(self.source, 'fictive')

    def test_invalid_date_refused(self):
        (self.source / 'Totals.csv').write_text('Date,Engaged views\n2026-02-30,1\n', encoding='utf-8')
        with self.assertRaises(ImportInvalide):
            analyser(self.source, 'fictive')

    def test_country_mismatch_detected_even_if_sum_matches(self):
        path = self.source / 'Chart data.csv'
        path.write_text(path.read_text(encoding='utf-8').replace(',FR,', ',BE,'), encoding='utf-8')
        result = analyser(self.source, 'fictive')
        self.assertTrue(any('non concordants' in msg for msg in result['resume']['avertissements']))


if __name__ == '__main__':
    unittest.main()
