from copy import deepcopy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from test_agents_videos import exemple
from test_agents_groupes import protocole
from observatoire.configurations import configuration
from observatoire.campagne import (creer_plan, essais, executer_prochain, evaluations,
    enregistrer_evaluation, CRITERES)
from observatoire.stockage import enregistrer_execution_reelle


class CampaignTests(unittest.TestCase):
    def setUp(self):
        runtime = patch('observatoire.campagne.runtime_local', return_value={'modele': 'fictif', 'modele_digest': 'test', 'ollama_version': 'test'})
        runtime.start()
        self.addCleanup(runtime.stop)

    def setup_plan(self, database):
        current = exemple()
        current['origine'] = 'reelle'
        previous = deepcopy(current)
        previous['periode'].update(debut='2026-08-20', fin='2026-09-16')
        previous['fichier']['sha256'] = 'avant'
        return creer_plan(current, previous, protocole(current), database)

    def test_twenty_unique_slots_alternated_and_idempotent_freeze(self):
        with tempfile.TemporaryDirectory() as directory:
            db = Path(directory)/'test.sqlite'
            plan = self.setup_plan(db)
            self.assertEqual(self.setup_plan(db)['id'], plan['id'])
            entries = essais(db, plan['id'])
            self.assertEqual(len(entries), 20)
            self.assertEqual(len({e['id'] for e in entries}), 20)
            self.assertEqual(len({(e['scenario'], e['configuration'], e['repetition']) for e in entries}), 20)
            self.assertEqual(entries[0]['configuration'], 'T0')
            self.assertEqual(entries[2]['configuration'], 'T04')
            self.assertEqual(entries[10]['configuration'], 'T04')
            a, b = configuration('T0', 2), configuration('T04', 2)
            self.assertEqual(a['seed'], b['seed'])
            self.assertNotEqual(a['temperature'], b['temperature'])

    def test_claims_once_and_refuses_changed_code(self):
        with tempfile.TemporaryDirectory() as directory:
            db = Path(directory)/'test.sqlite'
            plan = self.setup_plan(db)
            with patch('observatoire.lancement_local.lancer_agents', return_value={'etat': 'terminee'}) as launch:
                first = executer_prochain(db, plan['id'])
                second = executer_prochain(db, plan['id'])
                self.assertNotEqual(first['essai']['id'], second['essai']['id'])
                self.assertEqual(launch.call_count, 2)
                self.assertEqual(launch.call_args.args[4], plan['id'])
            with patch('observatoire.campagne.empreinte_code', return_value='modifie'), self.assertRaises(ValueError):
                executer_prochain(db, plan['id'])

    def test_launch_failure_retained_and_not_retried(self):
        with tempfile.TemporaryDirectory() as directory:
            db = Path(directory)/'test.sqlite'
            plan = self.setup_plan(db)
            with patch('observatoire.lancement_local.lancer_agents', side_effect=RuntimeError('moteur indisponible')):
                result = executer_prochain(db, plan['id'])
            self.assertEqual(result['etat'], 'incident_lancement')
            self.assertEqual(essais(db, plan['id'])[0]['etat'], 'incident_lancement')
            self.assertEqual(evaluations(db), {})

    def test_human_scores_explicit_auditable_and_not_from_numeric_checks(self):
        with tempfile.TemporaryDirectory() as directory:
            db = Path(directory)/'test.sqlite'
            plan = self.setup_plan(db)
            identifier = essais(db, plan['id'])[0]['id']
            enregistrer_execution_reelle({'id': identifier, 'mode': 'ia_locale', 'orchestrateur': 'CrewAI',
                                          'campagne_id': plan['id'], 'etat': 'terminee'}, db)
            notes = dict.fromkeys(CRITERES, 2)
            with self.assertRaises(ValueError):
                enregistrer_evaluation(db, identifier, {**notes, 'limites': None}, 'Test', 'Preuves', False)
            self.assertEqual(evaluations(db), {})
            result = enregistrer_evaluation(db, identifier, notes, 'Test humain', 'Calculs et texte examinés', False)
            self.assertTrue(result['reussite_qualite'])
            result = enregistrer_evaluation(db, identifier, notes, 'Test humain', 'Correction : erreur critique', True)
            self.assertFalse(result['reussite_qualite'])
            self.assertEqual(evaluations(db)[identifier]['score'], 8)

    def test_dashboard_empty_filters_and_reading_do_not_launch_agents(self):
        from streamlit.testing.v1 import AppTest
        with tempfile.TemporaryDirectory() as directory:
            db = Path(directory)/'test.sqlite'
            self.setup_plan(db)
            data = exemple()
            data['origine'] = 'reelle'
            source = f'''
from pathlib import Path
from decimal import Decimal
from observatoire.vue_campagne import afficher_campagne
afficher_campagne(Path({directory!r}), {data!r}, Path({str(db)!r}))
'''
            with patch('observatoire.vue_campagne.executer_prochain') as launch:
                app = AppTest.from_string(source, default_timeout=15).run()
                self.assertFalse(app.exception)
                self.assertEqual(app.metric[0].value, '0')
                self.assertEqual(len(app.get('plotly_chart')), 1)
                app.multiselect(key='campagne_filtre_scenario').set_value([]).run()
                self.assertFalse(app.exception)
                self.assertEqual(len(app.get('plotly_chart')), 0)
                launch.assert_not_called()
