from copy import deepcopy
from decimal import Decimal
import unittest

from observatoire.comparaison_periodes import comparer_periodes
from test_agents_videos import exemple


class PeriodComparisonTests(unittest.TestCase):
    def pair(self):
        current = exemple()
        previous = deepcopy(current)
        previous['periode'].update(debut='2026-08-20', fin='2026-09-16')
        previous['fichier']['sha256'] = 'autre-empreinte'
        return previous, current

    def test_paired_population_and_unknowns_are_separate_from_totals(self):
        previous, current = self.pair()
        previous['videos'].pop(1)
        previous['videos'][0]['vues'] = 50
        result = comparer_periodes(previous, current)
        self.assertEqual(result['jours_par_periode'], 28)
        self.assertEqual(result['nb_communs'], 2)
        self.assertEqual(result['uniquement_apres'], ['video000002'])
        views = result['cohorte_appariee']['vues']
        self.assertEqual(views['nb_paires_connues'], 1)
        self.assertEqual(views['nb_paires_incompletes'], 1)
        self.assertEqual(views['variation_pct'], Decimal(100))
        self.assertEqual(result['totaux_canal']['vues']['avant'], 125)

    def test_zero_base_and_no_known_pairs_are_unavailable(self):
        previous, current = self.pair()
        previous['total']['vues'] = 0
        for row in previous['videos']:
            row['heures'] = None
        result = comparer_periodes(previous, current)
        self.assertIsNone(result['totaux_canal']['vues']['variation_pct'])
        self.assertIsNone(result['cohorte_appariee']['heures']['apres'])
        self.assertIsNone(result['cohorte_appariee']['heures']['ecart'])

    def test_incompatible_periods_origins_or_identical_file_refused(self):
        previous, current = self.pair()
        for change in ('duration', 'overlap', 'origin', 'file'):
            candidate = deepcopy(previous)
            if change == 'duration':
                candidate['periode']['debut'] = '2026-08-19'
            elif change == 'overlap':
                candidate['periode'] = dict(current['periode'])
            elif change == 'origin':
                candidate['origine'] = 'reelle'
            else:
                candidate['fichier'] = dict(current['fichier'])
            with self.subTest(change=change), self.assertRaises(ValueError):
                comparer_periodes(candidate, current)
