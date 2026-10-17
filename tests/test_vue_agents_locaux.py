from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from observatoire.stockage import enregistrer_execution_reelle
from observatoire.import_youtube import analyser
from observatoire.outils_audience import calculer_audience
from observatoire.verification import verifier_audience


class RealAgentsInterfaceTests(unittest.TestCase):
    def test_reading_stored_trace_does_not_launch_model(self):
        from streamlit.testing.v1 import AppTest

        root = Path(__file__).resolve().parents[1]
        roles = ['Coordonnateur', 'Chercheur', 'Analyste', 'Vérificateur', 'Coordonnateur']
        # Fixture d’interface uniquement ; aucune inférence prétendue dans cette base temporaire.
        trace = {
            'id': 'fixture-interface', 'mode': 'ia_locale', 'orchestrateur': 'CrewAI',
            'type': 'test_logiciel', 'modele': 'qwen3:4b', 'etat': 'terminee',
            'debut_utc': '2026-01-01T00:00:00+00:00', 'origine_donnees': 'fictive',
            'duree_s': 5, 'jetons_entree': 10, 'jetons_sortie': 5,
            'resultat': '{"resultat":"Constat de test."}', 'erreurs': [], 'appels': [], 'outils': [],
            'etapes': [{'ordre': i + 1, 'agent': role, 'tache': 'Tâche de test',
                        'etat': 'terminee', 'duree_s': 1, 'debut_s': i, 'sortie': 'Sortie fictive de test'}
                       for i, role in enumerate(roles)],
            'messages': [{'emetteur': roles[i], 'destinataire': roles[i + 1],
                          'etape_source': i + 1, 'etape_cible': i + 2, 'resume': 'Contexte fictif'} for i in range(4)],
        }
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / 'test.sqlite'
            enregistrer_execution_reelle(trace, database)
            source = (root / 'app.py').read_text(encoding='utf-8')
            source = source.replace('ROOT = Path(__file__).resolve().parent', f'ROOT = Path({str(root)!r})')
            source = source.replace("DATABASE = ROOT / 'data' / 'private' / 'observatoire.sqlite'", f'DATABASE = Path({str(database)!r})')
            with patch('observatoire.vue_agents_locaux.lancer_agents') as launch:
                app = AppTest.from_string(source, default_timeout=15).run()
                app.button(key='charger_csv').click().run()
                self.assertEqual(len(app.exception), 0)
                self.assertEqual(len(app.get('plotly_chart')), 5)
                app.slider(key='ia_relecture_fixture-interface').set_value(1).run()
                self.assertEqual(len(app.exception), 0)
                self.assertEqual(len(app.get('plotly_chart')), 4)
                data = analyser(root / 'data' / 'examples', 'fictive')
                trace['verification'] = verifier_audience(data, calculer_audience(data))
                trace['verification']['verdict'] = 'refuse'
                trace['validation_synthese'] = {'sources_acceptees': False}
                enregistrer_execution_reelle(trace, database)
                app.run()
                self.assertEqual(len(app.exception), 0)
                self.assertTrue(any('Synthèse non validée' in error.value for error in app.error))
                self.assertTrue(any('Brouillon généré non validé' in expander.label for expander in app.expander))
                launch.assert_not_called()
