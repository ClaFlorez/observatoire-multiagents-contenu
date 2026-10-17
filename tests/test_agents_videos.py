from copy import deepcopy
from decimal import Decimal
from pathlib import Path
import tempfile
import unittest

from observatoire.analyse_videos import calculer_videos, verifier_videos, verifier_synthese_videos
from observatoire.stockage import charger_import_videos, enregistrer_import_videos


def exemple():
    def video(identifier, views, hours):
        return {'id': identifier, 'titre': 'Exemple fictif', 'publication': None,
                'duree_video_s': 120, 'vues': views, 'heures': hours,
                'abonnes': None, 'duree_moyenne_s': None, 'impressions': 10, 'ctr_pct': None}
    return {'type': 'videos', 'origine': 'fictive',
            'periode': {'debut': '2026-09-17', 'fin': '2026-10-14', 'source': 'declaration_utilisateur'},
            'fichier': {'nom': 'exemple.csv', 'sha256': 'empreinte-fictive'},
            'total': video('Total', 125, Decimal('3.0001')),
            'videos': [video('video000001', 100, Decimal('1')), video('video000002', 20, Decimal('2')),
                       video('video000003', None, None)],
            'rapprochements': [], 'avertissements': ['Une valeur absente est inconnue.']}


class VideoAgentsTests(unittest.TestCase):
    def test_rankings_are_distinct_and_missing_counts_explicit(self):
        data = exemple()
        analysis = calculer_videos(data)
        self.assertEqual(analysis['video_vues_id'], 'video000001')
        self.assertEqual(analysis['video_heures_id'], 'video000002')
        self.assertEqual(analysis['somme_vues_connues'], 120)
        self.assertEqual(analysis['total_vues'], 125)
        self.assertEqual(analysis['vues_absentes'], 1)
        self.assertEqual(verifier_videos(data, analysis)['verdict'], 'accepte_avec_reserves')

    def test_wrong_leader_order_or_missing_value_changed_to_zero_refused(self):
        data = exemple()
        analysis = calculer_videos(data)
        for field, value in [('video_vues_valeur', 1000), ('vues_absentes', 0), ('video_heures_id', 'video000001')]:
            with self.subTest(field=field):
                wrong = {**analysis, field: value}
                self.assertEqual(verifier_videos(data, wrong)['verdict'], 'refuse')
        wrong = deepcopy(analysis)
        wrong['top_vues'].reverse()
        self.assertEqual(verifier_videos(data, wrong)['verdict'], 'refuse')

    def test_unknown_leaders_remain_null(self):
        data = exemple()
        for video in data['videos']:
            video['vues'] = None
            video['heures'] = None
        analysis = calculer_videos(data)
        self.assertIsNone(analysis['video_vues_id'])
        self.assertIsNone(analysis['video_heures_valeur'])
        self.assertEqual(analysis['vues_absentes'], 3)
        self.assertEqual(verifier_videos(data, analysis)['verdict'], 'accepte_avec_reserves')

    def test_video_snapshot_roundtrip_and_period_identity(self):
        data = exemple()
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / 'local.sqlite'
            identifier = enregistrer_import_videos(data, database)
            self.assertEqual(charger_import_videos(database, identifier), data)
            self.assertEqual(enregistrer_import_videos(data, database), identifier)
            other_period = deepcopy(data)
            other_period['periode']['debut'] = '2026-10-01'
            self.assertNotEqual(enregistrer_import_videos(other_period, database), identifier)
            with self.assertRaises(KeyError):
                charger_import_videos(database, 'absent')

    def test_final_requires_correct_numbers_and_explicit_hypothesis(self):
        data = exemple()
        report = verifier_videos(data, calculer_videos(data))
        final = {**report['mesures_sources'], 'resultat': 'video000001 possède 100 vues. video000002 possède 2 heures.',
                 'verdict_source': 'accepte_avec_reserves', 'recommandation': 'Tester un nouvel angle sur un futur contenu inspiré de video000001 ; comparer les vues sur une période de même longueur, sans gain garanti.',
                 'video_reference': 'video000001', 'indicateur_test': 'vues',
                 'statut_recommandation': 'hypothese_a_tester'}
        self.assertTrue(all(verifier_synthese_videos(final, report).values()))
        stored_report = deepcopy(report)
        stored_report['mesures_sources']['video_heures_valeur'] = '2'
        self.assertTrue(all(verifier_synthese_videos(final, stored_report).values()))
        converted = {**final, 'resultat': 'video000001 possède 100 vues. video000002 : 2h30m.'}
        self.assertFalse(verifier_synthese_videos(converted, report)['texte_heures_exactes'])
        self.assertFalse(verifier_synthese_videos(converted, report)['aucune_conversion_horaire'])
        final['vues_absentes'] = 0
        self.assertFalse(verifier_synthese_videos(final, report)['vues_absentes'])
        final['statut_recommandation'] = 'gain_garanti'
        self.assertFalse(verifier_synthese_videos(final, report)['hypothese_explicite'])

    def test_unrelated_or_misleading_recommendation_is_refused(self):
        data = exemple()
        report = verifier_videos(data, calculer_videos(data))
        final = {**report['mesures_sources'], 'resultat': 'video000001 : 100 vues.',
                 'verdict_source': report['verdict'], 'statut_recommandation': 'hypothese_a_tester',
                 'video_reference': 'video000003', 'indicateur_test': 'vues',
                 'recommandation': 'Tester les vidéos sans vues.'}
        checks = verifier_synthese_videos(final, report)
        self.assertFalse(checks['reference_recommandation'])
        self.assertFalse(checks['absences_non_assimilees_zero'])

    def test_compact_context_preserves_reserves_and_failed_controls(self):
        from observatoire.analyse_videos import contexte_synthese_videos
        data = exemple()
        analysis = calculer_videos(data)
        analysis['total_vues'] = 999
        report = verifier_videos(data, analysis)
        compact = contexte_synthese_videos(report)
        self.assertEqual(compact['verdict'], 'refuse')
        self.assertEqual(compact['mesures_sources'], report['mesures_sources'])
        self.assertEqual(compact['avertissements'], report['avertissements'])
        self.assertTrue(compact['controles_echoues'])
