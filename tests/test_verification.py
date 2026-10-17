from copy import deepcopy
from pathlib import Path
import unittest

from observatoire.import_youtube import analyser
from observatoire.outils_audience import calculer_audience
from observatoire.verification import verifier_audience, verifier_synthese


class VerificationTests(unittest.TestCase):
    def setUp(self):
        self.data = analyser(Path(__file__).resolve().parents[1] / 'data' / 'examples', 'fictive')
        self.analysis = calculer_audience(self.data)

    def test_known_gap_and_high_percentage_are_reserves_not_invented_errors(self):
        report = verifier_audience(self.data, self.analysis)
        self.assertEqual(report['verdict'], 'accepte_avec_reserves')
        self.assertTrue(all(c['etat'] != 'echoue' for c in report['controles']))
        self.assertEqual(report['mesures_sources']['total'], 45)
        self.assertEqual(report['mesures_sources']['ecart_non_explique'], 10)
        self.assertTrue(any('100 %' in text for text in report['avertissements']))

    def test_wrong_denominator_or_invented_volume_is_refused(self):
        for key, value in [('part_du_total_pct', 85.71), ('volume_pays_en_tete', 300), ('unite', 'vues')]:
            with self.subTest(key=key):
                candidate = {**self.analysis, key: value}
                report = verifier_audience(self.data, candidate)
                self.assertEqual(report['verdict'], 'refuse')
                self.assertTrue(any(c['etat'] == 'echoue' for c in report['controles']))

    def test_mismatched_daily_total_is_refused(self):
        self.data['donnees']['Totals.csv'][0]['Engaged views'] += 1
        report = verifier_audience(self.data, self.analysis)
        self.assertEqual(report['verdict'], 'refuse')
        self.assertEqual(next(c['etat'] for c in report['controles'] if c['code'] == 'total_quotidien'), 'echoue')

    def test_country_identity_and_date_coverage_are_checked(self):
        mismatch = deepcopy(self.data)
        for row in mismatch['donnees']['Chart data.csv']:
            if row['Geography'] == 'FR':
                row['Geography'] = 'BE'
        report = verifier_audience(mismatch, self.analysis)
        self.assertEqual(next(c['etat'] for c in report['controles'] if c['code'] == 'details_pays'), 'echoue')
        self.data['donnees']['Chart data.csv'].pop()  # ligne FR à zéro, sans changer les sommes
        report = verifier_audience(self.data, self.analysis)
        self.assertEqual(next(c['etat'] for c in report['controles'] if c['code'] == 'couverture_dates'), 'echoue')

    def test_zero_denominator_has_explicit_non_applicable_control(self):
        for rows in self.data['donnees'].values():
            for row in rows:
                row['Engaged views'] = 0
        analysis = calculer_audience(self.data)
        report = verifier_audience(self.data, analysis)
        self.assertEqual(report['verdict'], 'accepte_avec_reserves')
        self.assertIsNone(report['mesures_sources']['part_du_total_pct'])
        self.assertEqual(next(c['etat'] for c in report['controles'] if c['code'] == 'pourcentage'), 'non_applicable')
        analysis['part_du_total_pct'] = 0
        self.assertEqual(verifier_audience(self.data, analysis)['verdict'], 'refuse')

    def test_malformed_analysis_is_never_accepted(self):
        for candidate in (None, [], 'Résumé sans preuve', {}):
            with self.subTest(candidate=candidate):
                self.assertEqual(verifier_audience(self.data, candidate)['verdict'], 'refuse')

    def test_final_numbers_and_verdict_must_match_structured_sources(self):
        report = verifier_audience(self.data, self.analysis)
        final = {**report['mesures_sources'], 'verdict_source': report['verdict'], 'resultat': 'CA possède 30 vues engagées sur 45. L’écart reste inexpliqué.'}
        self.assertTrue(all(verifier_synthese(final, report).values()))
        generic = {**final, 'resultat': 'Synthèse des mesures et du verdict.'}
        self.assertFalse(verifier_synthese(generic, report)['texte_etaye'])
        final['total'] = 450
        self.assertFalse(verifier_synthese(final, report)['total'])
        final['total'] = 45
        report['verdict'] = 'refuse'
        self.assertFalse(verifier_synthese(final, report)['verdict_respecte'])
        final['verdict_source'] = 'refuse'
        self.assertFalse(verifier_synthese(final, report)['sources_acceptees'])
