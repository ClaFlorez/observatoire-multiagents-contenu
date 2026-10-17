from decimal import Decimal
import unittest
from test_agents_videos import exemple
from observatoire.scenarios_groupes import comparer_groupes, comparer_cible


class GroupScenariosTests(unittest.TestCase):
    def test_missing_is_not_zero_and_metrics_stay_separate(self):
        result = comparer_groupes(exemple(), ['video000001', 'video000003'], ['video000002'])
        self.assertEqual(result['vues']['A']['effectif'], 2)
        self.assertEqual(result['vues']['A']['connus'], 1)
        self.assertEqual(result['vues']['A']['mediane_connue'], 100)
        self.assertEqual(result['heures']['A']['somme_connue'], Decimal('1'))
        unknown = comparer_groupes(exemple(), ['video000003'], ['video000002'])
        self.assertIsNone(unknown['vues']['A']['somme_connue'])

    def test_invalid_populations_refused(self):
        for a, b in [([], ['video000002']), (['absent'], ['video000002']),
                     (['video000001'] * 2, ['video000002']),
                     (['video000001'], ['video000001'])]:
            with self.subTest(a=a, b=b), self.assertRaises(ValueError):
                comparer_groupes(exemple(), a, b)

    def test_target_is_excluded_and_comparison_uses_known_median(self):
        data = exemple()
        result = comparer_cible(data, 'video000002', ['video000001', 'video000003'], 'vues')
        self.assertEqual(result['ecart_mediane'], -80)
        self.assertTrue(result['sous_mediane'])
        self.assertEqual(result['absents'], 1)
        for target, refs in [('video000002', ['video000002']),
                             ('video000003', ['video000001']),
                             ('video000001', ['video000003'])]:
            with self.assertRaises(ValueError):
                comparer_cible(data, target, refs, 'vues')

    def test_preparation_interface_reacts_without_model_calls(self):
        from streamlit.testing.v1 import AppTest
        app = AppTest.from_string('''
from observatoire.vue_scenarios import afficher_preparation
from decimal import Decimal
report = {'origine': 'fictive', 'fichier': {'sha256': 'test'},
          'periode': {'debut': '2026-09-17', 'fin': '2026-10-14'},
          'videos': [{'id': 'a', 'titre': 'A', 'vues': 100, 'heures': Decimal('1')},
                     {'id': 'b', 'titre': 'B', 'vues': 20, 'heures': Decimal('2')}]}
afficher_preparation(report)
''', default_timeout=15).run()
        app.multiselect(key='scenario_test_a').set_value(['a'])
        app.multiselect(key='scenario_test_b').set_value(['b'])
        app.text_input(key='scenario_test_justification').set_value('Groupes manuels')
        app.selectbox(key='scenario_test_cible').set_value('b')
        app.multiselect(key='scenario_test_reference').set_value(['a'])
        app.text_input(key='scenario_test_comparabilite').set_value('Comparaison descriptive')
        app.run()
        self.assertFalse(app.exception)
        self.assertEqual(len(app.get('download_button')), 1)
