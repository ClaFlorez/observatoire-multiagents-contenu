"""Plan figé, exécutions sans doublon et évaluations humaines séparées."""
from contextlib import closing
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import sqlite3
from uuid import uuid4

from observatoire.agents_groupes import enregistrer_mission, charger_mission, preparer
from observatoire.agents_periodes import charger_paire
from observatoire.comparaison_periodes import comparer_periodes
from observatoire.stockage import enregistrer_import_videos, charger_import_videos, lire_executions_reelles
from observatoire.vue_s1 import mission_s1
from observatoire.configurations import CONFIGURATIONS, runtime_local


def maintenant():
    return datetime.now(timezone.utc).isoformat()


def empreinte_code():
    digest = hashlib.sha256()
    for source in sorted(Path(__file__).parent.glob('*.py')):
        digest.update(source.name.encode())
        digest.update(source.read_bytes())
    return digest.hexdigest()


def connexion(database):
    connection = sqlite3.connect(database, timeout=20)
    connection.execute('CREATE TABLE IF NOT EXISTS campagnes (id TEXT PRIMARY KEY, contenu_json TEXT NOT NULL)')
    connection.execute('CREATE TABLE IF NOT EXISTS essais_campagne (id TEXT PRIMARY KEY, campagne_id TEXT NOT NULL, ordre INTEGER NOT NULL, scenario TEXT NOT NULL, configuration TEXT NOT NULL, repetition INTEGER NOT NULL, etat TEXT NOT NULL, diagnostic TEXT)')
    connection.execute('CREATE TABLE IF NOT EXISTS evaluations_humaines (id INTEGER PRIMARY KEY AUTOINCREMENT, execution_id TEXT NOT NULL, cree_utc TEXT NOT NULL, contenu_json TEXT NOT NULL)')
    connection.commit()
    return connection


def creer_plan(current, previous, protocol, database):
    comparer_periodes(previous, current)
    if current['origine'] != 'reelle':
        raise ValueError('La campagne exige des exports déclarés réels.')
    missions = {'S1': {'type': 'S1', 'id': enregistrer_mission(mission_s1(current), database)},
                'S3': {'type': 'periodes', 'imports': [enregistrer_import_videos(r, database) for r in (previous, current)]},
                'S5': {'type': 'videos', 'id': enregistrer_import_videos(current, database)}}
    for s in ('S2', 'S4'):
        missions[s] = {'type': s, 'id': enregistrer_mission(preparer(current, protocol, s), database)}
    identity = {'missions': missions, 'configurations': CONFIGURATIONS, 'code_sha256': empreinte_code(), 'runtime': runtime_local(),
                'protocole': '5 scenarios x 2 temperatures du meme modele x 2 repetitions',
                'limites': ['Synthèses fortement contraintes par les outils et schémas ; pas une comparaison générale des capacités des modèles.',
                            'S4 exploratoire : sujets différents et référence unique, comparabilité non démontrée.',
                            'Réchauffement/cache possibles ; ordre alterné, aucun effet causal de vitesse établi.',
                            'Chaque résultat exige une évaluation humaine ; les pilotes restent exclus.']}
    identifier = hashlib.sha256(json.dumps(identity, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    plan = {'id': identifier, 'cree_utc': maintenant(), **identity}
    with closing(connexion(database)) as connection, connection:
        if connection.execute('SELECT 1 FROM campagnes WHERE id=?', (identifier,)).fetchone():
            return charger_plan(database, identifier)
        connection.execute('INSERT INTO campagnes VALUES (?, ?)', (identifier, json.dumps(plan, ensure_ascii=False)))
        order = 0
        for repetition in (1, 2):
            for index, scenario in enumerate(('S1', 'S2', 'S3', 'S4', 'S5')):
                configs = ('T0', 'T04') if (index + repetition) % 2 else ('T04', 'T0')
                for config in configs:
                    order += 1
                    connection.execute('INSERT INTO essais_campagne VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                                       (str(uuid4()), identifier, order, scenario, config, repetition, 'en_attente', None))
    return plan


def charger_plan(database, identifier):
    with closing(connexion(database)) as connection:
        row = connection.execute('SELECT contenu_json FROM campagnes WHERE id=?', (identifier,)).fetchone()
    if not row:
        raise ValueError('Plan introuvable.')
    return json.loads(row[0])


def plans(database):
    if not Path(database).exists():
        return []
    with closing(connexion(database)) as connection:
        return [json.loads(r[0]) for r in connection.execute('SELECT contenu_json FROM campagnes ORDER BY rowid DESC')]


def essais(database, identifier):
    with closing(connexion(database)) as connection:
        connection.row_factory = sqlite3.Row
        return [dict(row) for row in connection.execute('SELECT * FROM essais_campagne WHERE campagne_id=? ORDER BY ordre', (identifier,))]


def mission_du_plan(plan, scenario, database):
    descriptor = plan['missions'][scenario]
    if descriptor['type'] == 'periodes':
        charger_paire(database, ':'.join(descriptor['imports']))
        return descriptor
    if descriptor['type'] == 'videos':
        return charger_import_videos(database, descriptor['id'])
    return {**charger_mission(database, descriptor['id']), 'type': descriptor['type']}


def executer_prochain(database, identifier):
    from observatoire.lancement_local import lancer_agents
    plan = charger_plan(database, identifier)
    if empreinte_code() != plan['code_sha256']:
        raise ValueError('Le code a changé après le gel du plan. Préparer une nouvelle campagne, sans mélanger les versions.')
    if runtime_local() != plan['runtime']:
        raise ValueError('Version Ollama ou empreinte du modèle modifiée depuis le gel du plan.')
    with closing(connexion(database)) as connection, connection:
        connection.execute('BEGIN IMMEDIATE')
        if connection.execute("SELECT 1 FROM essais_campagne WHERE etat='en_cours'").fetchone():
            raise RuntimeError('Un essai de campagne est déjà en cours ; consulter sa trace avant toute reprise.')
        connection.row_factory = sqlite3.Row
        row = connection.execute("SELECT * FROM essais_campagne WHERE campagne_id=? AND etat='en_attente' ORDER BY ordre LIMIT 1", (identifier,)).fetchone()
        if row is None:
            return None
        entry = dict(row)
        connection.execute("UPDATE essais_campagne SET etat='en_cours' WHERE id=?", (entry['id'],))
    try:
        trace = lancer_agents(mission_du_plan(plan, entry['scenario'], database), database,
                              entry['configuration'], entry['repetition'], identifier, entry['id'])
        state, diagnostic = trace['etat'], None
    except Exception as exc:
        state, diagnostic = 'incident_lancement', type(exc).__name__ + ': ' + str(exc)
        trace = None
    with closing(connexion(database)) as connection, connection:
        connection.execute('UPDATE essais_campagne SET etat=?, diagnostic=? WHERE id=?', (state, diagnostic, entry['id']))
    return {'essai': entry, 'trace': trace, 'etat': state, 'diagnostic': diagnostic}


CRITERES = ('exactitude', 'tracabilite', 'respect_mission', 'limites')


def enregistrer_evaluation(database, execution_id, notes, evaluateur, justification, erreur_critique):
    if set(notes) != set(CRITERES) or any(type(v) is not int or v not in (0, 1, 2) for v in notes.values()):
        raise ValueError('Quatre notes entières entre 0 et 2 sont requises.')
    if not evaluateur.strip() or not justification.strip() or type(erreur_critique) is not bool:
        raise ValueError('Évaluateur, justification et indication d’erreur critique requis.')
    trace = next((t for t in lire_executions_reelles(database) if t['id'] == execution_id), None)
    if not trace or not trace.get('campagne_id') or trace['etat'] == 'en_cours':
        raise ValueError('Une exécution de campagne terminée ou échouée est requise.')
    score = sum(notes.values())
    evaluation = {'notes': notes, 'score': score, 'evaluateur': evaluateur, 'justification': justification,
                  'erreur_critique': erreur_critique, 'execution_id': execution_id,
                  'reussite_qualite': score >= 6 and notes['exactitude'] == notes['tracabilite'] == 2 and not erreur_critique}
    with closing(connexion(database)) as connection, connection:
        connection.execute('INSERT INTO evaluations_humaines (execution_id, cree_utc, contenu_json) VALUES (?, ?, ?)',
                           (execution_id, maintenant(), json.dumps(evaluation, ensure_ascii=False)))
    return evaluation


def evaluations(database):
    with closing(connexion(database)) as connection:
        return {row[0]: json.loads(row[1]) for row in connection.execute('SELECT execution_id, contenu_json FROM evaluations_humaines ORDER BY id')}


def synchroniser(database, identifier):
    """Récupérer une fin de worker enregistrée sans relancer une tentative interrompue."""
    traces = {t['id']: t for t in lire_executions_reelles(database) if t.get('campagne_id') == identifier}
    updated = 0
    with closing(connexion(database)) as connection, connection:
        for entry in essais(database, identifier):
            trace = traces.get(entry['id'])
            if entry['etat'] == 'en_cours' and trace and trace['etat'] != 'en_cours':
                connection.execute('UPDATE essais_campagne SET etat=? WHERE id=?', (trace['etat'], entry['id']))
                updated += 1
    return updated


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Exécuter les essais en attente d’un plan figé, sans noter automatiquement la qualité.')
    parser.add_argument('--database', type=Path, required=True)
    parser.add_argument('--id', required=True)
    parser.add_argument('--limite', type=int, choices=range(1, 21), default=20)
    args = parser.parse_args()
    for _ in range(args.limite):
        result = executer_prochain(args.database.resolve(), args.id)
        if result is None:
            break
        entry = result['essai']
        print(json.dumps({'ordre': entry['ordre'], 'scenario': entry['scenario'], 'configuration': entry['configuration'],
                          'id': entry['id'], 'etat': result['etat'], 'diagnostic': result['diagnostic']}, ensure_ascii=False), flush=True)
        if result['etat'] == 'incident_lancement':
            raise SystemExit('Incident de lancement conservé : vérifier le moteur avant de poursuivre.')


if __name__ == '__main__':
    main()
