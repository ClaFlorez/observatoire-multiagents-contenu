"""Lancement borné du worker CrewAI, sans modifier le processus Streamlit."""

from datetime import datetime, timezone
from pathlib import Path
import sqlite3
import subprocess
import sys
from threading import Lock
from uuid import uuid4

from observatoire.securite_locale import environnement_local
from observatoire.stockage import enregistrer_execution_reelle, enregistrer_import, lire_executions_reelles
from observatoire.stockage import enregistrer_import_videos


RUN_LOCK = Lock()


def lancer_agents(resultat, destination, configuration_id='T0', repetition=1, campagne_id=None, run_id=None):
    from observatoire.configurations import configuration
    configuration(configuration_id, repetition)
    if not RUN_LOCK.acquire(blocking=False):
        raise RuntimeError('Une exécution locale est déjà en cours dans cette application.')
    try:
        destination = Path(destination).resolve()
        if destination.exists():
            with sqlite3.connect(destination, timeout=20) as connection:
                has_campaign = connection.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='essais_campagne'").fetchone()
                if has_campaign and connection.execute("SELECT 1 FROM essais_campagne WHERE etat='en_cours' AND id != ?", (run_id or '',)).fetchone():
                    raise RuntimeError('Un essai de campagne est en cours ; aucun pilote concurrent autorisé.')
        domain = resultat.get('type') if resultat.get('type') in ('videos', 'periodes', 'S1', 'S2', 'S4') else 'geographie'
        if domain in ('S1', 'S2', 'S4'):
            from observatoire.agents_groupes import enregistrer_mission
            import_id = enregistrer_mission(resultat, destination)
        elif domain == 'periodes':
            from observatoire.agents_periodes import charger_paire
            import_id = ':'.join(resultat['imports'])
            charger_paire(destination, import_id)
        elif domain == 'videos':
            import_id = enregistrer_import_videos(resultat, destination)
        else:
            import_id, _ = enregistrer_import(resultat, destination)
        run_id = run_id or str(uuid4())
        if any(t['id'] == run_id for t in lire_executions_reelles(destination)):
            raise ValueError('Identifiant déjà exécuté : aucun lancement en double.')
        root = Path(__file__).resolve().parents[1]
        command = [sys.executable, '-m', 'observatoire.execution_locale',
                   '--import-id', import_id, '--database', str(destination), '--id', run_id,
                   '--type-rapport', domain, '--configuration', configuration_id, '--repetition', str(repetition)]
        if campagne_id:
            command += ['--campagne-id', campagne_id]
        timed_out = False
        try:
            subprocess.run(command, cwd=root, env=environnement_local(root),
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=600, check=False)
        except subprocess.TimeoutExpired:
            timed_out = True
        trace = next((t for t in lire_executions_reelles(destination) if t['id'] == run_id), None)
        if trace is None:
            raise RuntimeError('Le processus CrewAI n’a pas produit de trace. Vérifier les dépendances locales.')
        if timed_out or trace['etat'] == 'en_cours':
            trace.update(etat='echouee', fin_utc=datetime.now(timezone.utc).isoformat())
            trace['duree_s'] = (datetime.fromisoformat(trace['fin_utc']) - datetime.fromisoformat(trace['debut_utc'])).total_seconds()
            trace['erreurs'].append({'type': 'TimeoutProcessus' if timed_out else 'ProcessusInterrompu'})
            for step in trace['etapes']:
                if step['etat'] == 'en_cours':
                    step['etat'] = 'echouee'
            enregistrer_execution_reelle(trace, destination)
        # Export facultatif et isolé, après arrêt du worker : aucun accès réseau
        # ajouté au worker et aucune réécriture des traces historiques.
        from observatoire.connexion_agentops import transmettre
        try:
            transmettre(trace)
        except Exception:
            pass  # L'observabilité ne doit pas invalider le calcul local.
        return trace
    finally:
        RUN_LOCK.release()
