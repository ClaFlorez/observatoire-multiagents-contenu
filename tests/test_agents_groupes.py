from copy import deepcopy
from decimal import Decimal
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from test_agents_videos import exemple
from observatoire.agents_groupes import (preparer, signature, enregistrer_mission, charger_mission,
    calculer_groupes, verifier_groupes, formulation, verifier_synthese_groupes)


def protocole(data):
    return {**{k: data[k] for k in ('fichier', 'periode', 'origine')},
            'S2': {'groupe_a': ['video000001'], 'groupe_b': ['video000002', 'video000003'], 'justification': 'Groupes explicites'},
            'S4': {'cible': 'video000002', 'references': ['video000001', 'video000003'], 'mesure': 'vues', 'justification': 'Exploration'}}


class GroupAgentsTests(unittest.TestCase):
    def test_saved_protocol_recomputed_and_bound_to_snapshot(self):
        data = exemple()
        protocol = protocole(data)
        protocol['S2']['calcul'] = {'vues': 99999}
        mission = preparer(data, protocol, 'S2')
        self.assertEqual(calculer_groupes(mission)['vues_A_somme_connue'], 100)
        other = deepcopy(protocol)
        other['periode']['debut'] = '2020-01-01'
        with self.assertRaises(ValueError):
            preparer(data, other, 'S2')

    def test_independent_verification_detects_tampering_in_both_scenarios(self):
        for scenario in ('S2', 'S4'):
            data = exemple()
            mission = preparer(data, protocole(data), scenario)
            analysis = calculer_groupes(mission)
            with patch('observatoire.agents_groupes.calculer_groupes', side_effect=AssertionError('not independent')):
                verified = verifier_groupes(mission, analysis)
            self.assertEqual(verified['verdict'], 'accepte_avec_reserves')
            key = 'vues_A_mediane_connue' if scenario == 'S2' else 'ecart_mediane'
            bad = {**analysis, key: Decimal(999)}
            self.assertEqual(verifier_groupes(mission, bad)['verdict'], 'refuse')
            final = {'resultat': formulation(verified), 'verdict_source': verified['verdict']}
            self.assertTrue(all(verifier_synthese_groupes(final, verified).values()))
            final['resultat'] = 'Ce sujet explique la baisse.'
            self.assertFalse(all(verifier_synthese_groupes(final, verified).values()))

    def test_mission_storage_separates_groups_and_preserves_decimal(self):
        data = exemple()
        protocol = protocole(data)
        with tempfile.TemporaryDirectory() as directory:
            db = Path(directory) / 'test.sqlite'
            mission = preparer(data, protocol, 'S2')
            mission['type'] = 'S2'
            identifier = enregistrer_mission(mission, db)
            restored = charger_mission(db, identifier)
            self.assertEqual(signature(restored), identifier)
            self.assertEqual(restored['videos'][0]['heures'], Decimal('1'))
            changed = deepcopy(mission)
            changed['parametres_scenario']['justification'] = 'Autre choix'
            self.assertNotEqual(enregistrer_mission(changed, db), identifier)

    def test_ui_load_has_separate_buttons_and_no_inference(self):
        from streamlit.testing.v1 import AppTest
        import json
        data = exemple()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'youtube_csv').mkdir()
            (root / 'youtube_csv' / 'parametres_s2_s4 .json').write_text(json.dumps(protocole(data)), encoding='utf-8')
            source = f'''
from pathlib import Path
from decimal import Decimal
from observatoire.vue_scenarios import afficher_preparation
report = {data!r}
afficher_preparation(report, Path({str(root)!r}), Path({str(root / 'test.sqlite')!r}))
'''
            with patch('observatoire.vue_agents_locaux.lancer_agents') as launch:
                app = AppTest.from_string(source, default_timeout=15).run()
                app.button(key='charger_missions_groupes').click().run()
                self.assertFalse(app.exception)
                self.assertIsNotNone(app.button(key='lancer_agents_locaux_S2'))
                self.assertIsNotNone(app.button(key='lancer_agents_locaux_S4'))
                launch.assert_not_called()
