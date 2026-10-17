from copy import deepcopy
import json
from decimal import Decimal
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from test_agents_videos import exemple
from observatoire.stockage import enregistrer_import_videos
from observatoire.agents_periodes import (charger_paire, calculer_periodes, verifier_periodes,
    verifier_synthese_periodes, formulations, FINAL_FIELDS)


class PeriodAgentsTests(unittest.TestCase):
    def pair(self):
        after = exemple()
        before = deepcopy(after)
        before['periode'].update(debut='2026-08-20', fin='2026-09-16')
        before['fichier']['sha256'] = 'autre-fichier'
        before['videos'][0]['vues'] = 0
        before['videos'][0]['heures'] = None
        return before, after

    def test_snapshots_and_independent_checks(self):
        before, after = self.pair()
        with tempfile.TemporaryDirectory() as directory:
            db = Path(directory) / 'local.sqlite'
            ids = [enregistrer_import_videos(r, db) for r in (before, after)]
            pair = charger_paire(db, ':'.join(ids))
            analysis = calculer_periodes(pair)
            with patch('observatoire.agents_periodes.comparer_periodes', side_effect=AssertionError('Pas de calcul partagé')):
                report = verifier_periodes(pair, analysis)
            self.assertEqual(report['verdict'], 'accepte_avec_reserves')
            self.assertEqual(analysis['cohorte_heures_nb_paires_connues'], 1)
            wrong = {**analysis, 'cohorte_heures_nb_paires_connues': 3}
            self.assertEqual(verifier_periodes(pair, wrong)['verdict'], 'refuse')
            wrong = {**analysis, 'cohorte_vues_variation_pct': Decimal('999')}
            self.assertEqual(verifier_periodes(pair, wrong)['verdict'], 'refuse')
            self.assertEqual(verifier_periodes(pair, None)['verdict'], 'refuse')
            with self.assertRaises(ValueError):
                charger_paire(db, ':'.join(reversed(ids)))

    def test_synthesis_populations_values_and_storage_roundtrip(self):
        a, b = self.pair()
        pair = {'avant': a, 'apres': b, 'periode': {'avant': a['periode'], 'apres': b['periode']}, 'avertissements': []}
        report = verifier_periodes(pair, calculer_periodes(pair))
        final = {k: report['mesures_sources'][k] for k in FINAL_FIELDS}
        final.update(resultat=formulations(report)[0], verdict_source=report['verdict'])
        self.assertTrue(all(verifier_synthese_periodes(final, report).values()))
        stored = json.loads(json.dumps(report, default=str))
        self.assertTrue(all(verifier_synthese_periodes(final, stored).values()))
        final['canal_vues_ecart'] = Decimal(999)
        self.assertFalse(verifier_synthese_periodes(final, report)['canal_vues_ecart'])
        final['resultat'] = 'La publicité explique la baisse.'
        self.assertFalse(verifier_synthese_periodes(final, report)['texte_encadre'])

    def test_empty_pairs_and_zero_base_do_not_become_known_changes(self):
        a, b = self.pair()
        a['total']['vues'] = 0
        for row in a['videos']:
            row['vues'] = None
        pair = {'avant': a, 'apres': b, 'periode': {'avant': a['periode'], 'apres': b['periode']}, 'avertissements': []}
        analysis = calculer_periodes(pair)
        self.assertIsNone(analysis['canal_vues_variation_pct'])
        self.assertIsNone(analysis['cohorte_vues_ecart'])
        self.assertEqual(verifier_periodes(pair, analysis)['verdict'], 'accepte_avec_reserves')
