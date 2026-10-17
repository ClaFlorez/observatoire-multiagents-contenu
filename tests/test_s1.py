from copy import deepcopy
from decimal import Decimal
import unittest
from unittest.mock import patch
from test_agents_videos import exemple
from observatoire.agents_s1 import calculer_s1, verifier_s1, formulation_s1
from observatoire.agents_groupes import verifier_synthese_groupes


class S1Tests(unittest.TestCase):
    def test_distinct_rankings_unknowns_and_independent_verifier(self):
        data = exemple()
        result = calculer_s1(data)
        self.assertEqual(result['vues_1_id'], 'video000001')
        self.assertEqual(result['heures_1_id'], 'video000002')
        self.assertEqual(result['vues_absentes'], 1)
        self.assertIsNone(result['vues_3_valeur'])
        with patch('observatoire.agents_s1.calculer_s1', side_effect=AssertionError()):
            report = verifier_s1(data, result)
        self.assertEqual(report['verdict'], 'accepte_avec_reserves')
        final = {'resultat': formulation_s1(report), 'verdict_source': report['verdict']}
        self.assertTrue(all(verifier_synthese_groupes(final, report).values()))
        bad = {**result, 'vues_2_id': 'video000001'}
        self.assertEqual(verifier_s1(data, bad)['verdict'], 'refuse')
        final['resultat'] += ' Le thème explique ces résultats.'
        self.assertFalse(all(verifier_synthese_groupes(final, report).values()))

    def test_ties_keep_source_order_and_zero_is_known(self):
        data = exemple()
        for row in data['videos']:
            row.update(vues=0, heures=Decimal(0))
        data['videos'].reverse()
        result = calculer_s1(data)
        self.assertEqual(result['vues_1_id'], 'video000003')
        self.assertEqual(result['vues_3_id'], 'video000001')
        self.assertEqual(result['vues_absentes'], 0)
        self.assertEqual(verifier_s1(data, result)['verdict'], 'accepte_avec_reserves')

    def test_all_missing_stays_unavailable(self):
        data = deepcopy(exemple())
        for row in data['videos']:
            row.update(vues=None, heures=None)
        result = calculer_s1(data)
        self.assertEqual(result['heures_classees'], 0)
        self.assertIsNone(result['heures_1_valeur'])
        self.assertEqual(verifier_s1(data, result)['verdict'], 'accepte_avec_reserves')

    def test_interface_has_separate_rankings_without_launch(self):
        from streamlit.testing.v1 import AppTest
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as directory:
            source = f'''
from decimal import Decimal
from pathlib import Path
from observatoire.vue_s1 import afficher_s1
report = {exemple()!r}
afficher_s1(report, Path({str(Path(directory)/'test.sqlite')!r}))
'''
            with patch('observatoire.vue_agents_locaux.lancer_agents') as launch:
                app = AppTest.from_string(source, default_timeout=15).run()
                self.assertFalse(app.exception)
                self.assertEqual(len(app.dataframe), 2)
                self.assertIsNotNone(app.button(key='lancer_agents_locaux_S1'))
                launch.assert_not_called()
