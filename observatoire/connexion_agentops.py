"""Export explicite de métadonnées ; aucun contenu utilisateur ni secret exporté.

Le SDK s'exécute dans un processus séparé du worker CrewAI protégé.
Les traces sont des résumés après exécution, pas une instrumentation LLM native.
"""
import argparse
from datetime import datetime, timezone
import getpass
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
DOSSIER = ROOT / '.local' / 'agentops'
CLE = DOSSIER / 'connexion.key'


def resume_public(trace):
    """Liste blanche stricte : jamais prompts, sorties, CSV, chemins ou erreurs."""
    result = {'mode': 'resume_apres_execution', 'modele': 'qwen3:4b'}
    for key in ('etat', 'configuration_id'):
        allowed = {'terminee', 'non_validee', 'echouee', 'en_cours', 'T0', 'T04'}
        if trace.get(key) in allowed:
            result[key] = trace[key]
    for key in ('duree_s', 'jetons_entree', 'jetons_sortie'):
        value = trace.get(key)
        if type(value) in (int, float) and value >= 0:
            result[key] = value
    result['etapes'] = []
    for i, step in enumerate(trace.get('etapes', [])[:5]):
        item = {'ordre': i + 1}
        if step.get('etat') in ('terminee', 'echouee', 'en_cours', 'en_attente'):
            item['etat'] = step['etat']
        if type(step.get('duree_s')) in (int, float) and step['duree_s'] >= 0:
            item['duree_s'] = step['duree_s']
        result['etapes'].append(item)
    return result


def transmettre(trace):
    """Échec indépendant : ne modifie ni le résultat ni la campagne SQLite."""
    if not CLE.exists():
        return {'etat': 'non_configure'}
    payload = resume_public(trace)
    env = {k: v for k, v in os.environ.items()
           if not k.endswith('_API_KEY') and not k.startswith(('AGENTOPS_', 'OTEL_'))}
    env['PYTHON_DOTENV_DISABLED'] = '1'
    try:
        child = subprocess.run([sys.executable, '-m', 'observatoire.connexion_agentops', '--exporter'],
                               input=json.dumps(payload), text=True, cwd=ROOT, env=env,
                               capture_output=True, timeout=45, check=False)
        status = 'envoye_a_verifier_dashboard' if child.returncode == 0 else 'echec_connexion'
    except (OSError, subprocess.TimeoutExpired):
        status = 'echec_connexion'
    receipt = {'etat': status, 'date_utc': datetime.now(timezone.utc).isoformat(),
               'limite': 'Résumé technique après exécution ; réception à vérifier dans AgentOps.'}
    DOSSIER.mkdir(parents=True, exist_ok=True)
    (DOSSIER / 'dernier_envoi.json').write_text(json.dumps(receipt), encoding='utf-8')
    return receipt


def exporter(payload):
    # Réduction supplémentaire avant toute initialisation réseau du SDK.
    payload = resume_public(payload)
    import agentops
    from opentelemetry import trace as otel
    from agentops.sdk.core import tracer
    from agentops.sdk import core, processors
    from agentops.semconv import ResourceAttributes
    from agentops.sdk.exporters import AuthenticatedOTLPExporter
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.trace.export import SpanExportResult
    # Le SDK 0.4.21 ajoute les bibliothèques au Resource même avec
    # env_data_opt_out=True. Retirer explicitement cette collecte et les logs.
    core.get_global_resource_attributes = lambda service_name, project_id=None: {
        ResourceAttributes.SERVICE_NAME: 'observatoire',
        **({ResourceAttributes.PROJECT_ID: project_id} if project_id else {}),
    }
    core.get_system_resource_attributes = lambda: {}
    processors.upload_logfile = lambda *args, **kwargs: None
    results = []
    def checked_export(self, spans):
        # AgentOps 0.4.21 utilise _headers/_session, retirés dans OTel 1.45.
        # Utiliser l'interface publique du transport avec le JWT courant.
        transport = OTLPSpanExporter(
            endpoint='https://otlp.agentops.ai/v1/traces',
            headers={'Authorization': 'Bearer ' + agentops.get_client().get_current_jwt()},
            timeout=10,
        )
        try:
            result = transport.export(spans)
        finally:
            transport.shutdown()
        results.append(result)
        return result

    AuthenticatedOTLPExporter.export = checked_export
    agentops.init(api_key=CLE.read_text(encoding='utf-8').strip(),
                  endpoint='https://api.agentops.ai',
                  exporter_endpoint='https://otlp.agentops.ai/v1/traces',
                  auto_start_session=False, instrument_llm_calls=False,
                  env_data_opt_out=True, log_level='CRITICAL', fail_safe=False,
                  log_session_replay_url=False)
    deadline = time.monotonic() + 12
    while not agentops.get_client().get_current_jwt():
        if time.monotonic() >= deadline:
            raise RuntimeError('Authentification AgentOps non confirmee')
        time.sleep(0.1)
    session = agentops.start_trace('Observatoire - resume technique',
                                   tags=['observatoire', 'metadonnees', 'apres-execution'])
    if session is None:
        raise RuntimeError('Initialisation AgentOps impossible')
    try:
        agentops.update_trace_metadata({k: v for k, v in payload.items() if k != 'etapes'})
        roles = ['Coordonnateur - cadrage', 'Chercheur', 'Analyste',
                 'Verificateur', 'Coordonnateur - synthese']
        for step in payload['etapes']:
            with otel.get_tracer('observatoire').start_as_current_span(roles[step['ordre'] - 1]) as span:
                for key, value in step.items():
                    span.set_attribute('observatoire.' + key, value)
                span.set_attribute('observatoire.mesure', 'duree_locale_en_attribut_pas_duree_du_span')
    finally:
        agentops.end_trace(session, 'Success' if payload.get('etat') == 'terminee' else 'Indeterminate')
        if not tracer.provider.force_flush(timeout_millis=10000):
            raise RuntimeError('Export AgentOps non termine')
        if not results or any(result != SpanExportResult.SUCCESS for result in results):
            raise RuntimeError('Serveur AgentOps : export non accepte')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--configurer', action='store_true')
    parser.add_argument('--tester', action='store_true')
    parser.add_argument('--exporter', action='store_true', help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.configurer:
        key = getpass.getpass('Cle API AgentOps (saisie masquee) : ').strip()
        if not key or any(c.isspace() for c in key):
            raise SystemExit('Cle vide ou invalide.')
        DOSSIER.mkdir(parents=True, exist_ok=True)
        CLE.write_text(key, encoding='utf-8')
        print('Cle enregistree localement dans un fichier ignore par Git. Aucun envoi effectue.')
    elif args.tester:
        print(json.dumps(transmettre({'etat': 'terminee', 'etapes': []}), ensure_ascii=False))
    elif args.exporter:
        try:
            exporter(json.load(sys.stdin))
        except Exception:
            # Ne jamais imprimer une exception SDK : elle peut contenir des secrets.
            raise SystemExit(1)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
