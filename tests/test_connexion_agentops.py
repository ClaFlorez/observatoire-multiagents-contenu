import tempfile
from importlib.util import find_spec
from pathlib import Path
import unittest
from unittest.mock import patch
from unittest.mock import Mock

from observatoire.connexion_agentops import resume_public, transmettre


class AgentOpsTests(unittest.TestCase):
    @unittest.skipUnless(find_spec('agentops'), 'SDK AgentOps facultatif non installe')
    def test_transport_failure_is_not_confused_with_successful_flush(self):
        import agentops
        from agentops.sdk import core, processors
        from agentops.sdk.exporters import AuthenticatedOTLPExporter
        from opentelemetry.sdk.trace.export import SpanExportResult
        from observatoire.connexion_agentops import exporter
        with tempfile.TemporaryDirectory() as folder:
            key = Path(folder) / 'test.key'
            key.write_text('fictive')
            transport = Mock()
            transport.export.return_value = SpanExportResult.FAILURE
            provider = Mock()
            provider.force_flush.return_value = True
            # Un flush réussi ne doit pas masquer le refus du transport.
            def finish(*args):
                AuthenticatedOTLPExporter.export(object(), [])
            with patch('observatoire.connexion_agentops.CLE', key), \
                 patch.object(agentops, 'init'), \
                 patch.object(agentops, 'get_client', return_value=Mock(get_current_jwt=lambda: 'fictif')), \
                 patch.object(agentops, 'start_trace', return_value=object()), \
                 patch.object(agentops, 'update_trace_metadata'), \
                 patch.object(agentops, 'end_trace', side_effect=finish), \
                 patch.object(core.tracer, 'provider', provider), \
                 patch.object(core, 'get_global_resource_attributes'), \
                 patch.object(core, 'get_system_resource_attributes'), \
                 patch.object(processors, 'upload_logfile'), \
                 patch.object(AuthenticatedOTLPExporter, 'export'), \
                 patch('opentelemetry.exporter.otlp.proto.http.trace_exporter.OTLPSpanExporter', return_value=transport):
                with self.assertRaisesRegex(RuntimeError, 'export non accepte'):
                    exporter({'etat': 'terminee', 'etapes': []})
            transport.shutdown.assert_called_once()

    def test_no_private_content_is_exported(self):
        trace = {'id': 'prive', 'etat': 'terminee', 'duree_s': 2.5,
                 'resultat': 'secret', 'provenance': 'chemin prive',
                 'configuration_id': 'T0', 'jetons_entree': 20,
                 'etapes': [{'agent': 'nom prive', 'sortie': 'secret',
                             'etat': 'terminee', 'duree_s': 1}]}
        payload = resume_public(trace)
        self.assertEqual(payload['duree_s'], 2.5)
        self.assertEqual(payload['etapes'], [{'ordre': 1, 'etat': 'terminee', 'duree_s': 1}])
        self.assertNotIn('secret', str(payload))
        self.assertNotIn('prive', str(payload))
        self.assertEqual(resume_public(payload), payload)

    def test_disabled_does_not_start_subprocess(self):
        with tempfile.TemporaryDirectory() as folder:
            with patch('observatoire.connexion_agentops.CLE', Path(folder) / 'absente.key'):
                with patch('observatoire.connexion_agentops.subprocess.run') as run:
                    self.assertEqual(transmettre({})['etat'], 'non_configure')
                    run.assert_not_called()

    def test_failed_export_preserves_local_result_and_hides_errors(self):
        with tempfile.TemporaryDirectory() as folder:
            key = Path(folder) / 'test.key'
            key.write_text('valeur_fictive')
            original = {'etat': 'terminee', 'resultat': 'prive'}
            with patch('observatoire.connexion_agentops.CLE', key), patch('observatoire.connexion_agentops.DOSSIER', Path(folder)):
                with patch('observatoire.connexion_agentops.subprocess.run', side_effect=OSError('secret')):
                    receipt = transmettre(original)
            self.assertEqual(receipt['etat'], 'echec_connexion')
            self.assertNotIn('secret', str(receipt))
            self.assertEqual(original, {'etat': 'terminee', 'resultat': 'prive'})


if __name__ == '__main__':
    unittest.main()
