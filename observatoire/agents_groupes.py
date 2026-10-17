"""Instantanés et vérification indépendante des missions S2 et S4."""
from contextlib import closing
from decimal import Decimal
import hashlib
import json
import sqlite3

from observatoire.stockage import enregistrer_import_videos, charger_import_videos
from observatoire.scenarios_groupes import comparer_groupes, comparer_cible
from observatoire.analyse_videos import egal
from observatoire.agents_s1 import calculer_s1, verifier_s1, formulation_s1


def preparer(report, protocol, scenario):
    if scenario not in ('S2', 'S4'):
        raise ValueError('Scénario inconnu.')
    if any(protocol.get(k) != report[k] for k in ('fichier', 'periode', 'origine')):
        raise ValueError('Le JSON ne correspond pas au CSV, à son origine ou à sa période.')
    raw = protocol.get(scenario, {})
    keys = ('groupe_a', 'groupe_b', 'justification') if scenario == 'S2' else ('cible', 'references', 'mesure', 'justification')
    params = {k: raw[k] for k in keys}
    if not isinstance(params['justification'], str) or not params['justification'].strip():
        raise ValueError('Une justification explicite est requise.')
    if len(params['justification']) > 2000:
        raise ValueError('Justification trop longue (2000 caractères maximum).')
    for key in (('groupe_a', 'groupe_b') if scenario == 'S2' else ('references',)):
        if not isinstance(params[key], list) or not all(isinstance(i, str) for i in params[key]):
            raise ValueError('Une liste d’identifiants est requise.')
        params[key] = sorted(params[key])
    data = {**report, 'scenario_groupe': scenario, 'parametres_scenario': params}
    calculer_groupes(data)  # Recalcul : ignorer les valeurs calculées dans le JSON téléchargé.
    return data


def signature(data):
    identity = {k: data[k] for k in ('fichier', 'periode', 'origine', 'scenario_groupe', 'parametres_scenario')}
    return hashlib.sha256(json.dumps(identity, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def enregistrer_mission(data, database):
    calculer_groupes(data)
    import_id = enregistrer_import_videos({**data, 'type': 'videos'}, database)
    identifier = signature(data)
    payload = {'import_id': import_id, 'scenario': data['scenario_groupe'], 'parametres': data['parametres_scenario']}
    with closing(sqlite3.connect(database)) as connection, connection:
        connection.execute('CREATE TABLE IF NOT EXISTS missions_groupes (id TEXT PRIMARY KEY, contenu_json TEXT NOT NULL)')
        connection.execute('INSERT OR IGNORE INTO missions_groupes VALUES (?, ?)', (identifier, json.dumps(payload, ensure_ascii=False)))
    return identifier


def charger_mission(database, identifier):
    with closing(sqlite3.connect(database)) as connection:
        row = connection.execute('SELECT contenu_json FROM missions_groupes WHERE id=?', (identifier,)).fetchone()
    if row is None:
        raise ValueError('Mission introuvable.')
    payload = json.loads(row[0])
    report = charger_import_videos(database, payload['import_id'])
    report.update(scenario_groupe=payload['scenario'], parametres_scenario=payload['parametres'])
    if signature(report) != identifier:
        raise ValueError('Empreinte de mission incohérente.')
    calculer_groupes(report)
    return report


def calculer_groupes(data):
    if data['scenario_groupe'] == 'S1':
        return calculer_s1(data)
    p = data['parametres_scenario']
    if data['scenario_groupe'] == 'S2':
        result = comparer_groupes(data, p['groupe_a'], p['groupe_b'])
        return {f'{metric}_{group}_{key}': value for metric, groups in result.items()
                for group, stats in groups.items() for key, value in stats.items()}
    if data['scenario_groupe'] != 'S4':
        raise ValueError('Scénario inconnu.')
    return comparer_cible(data, p['cible'], p['references'], p['mesure'])


def verifier_groupes(data, analysis):
    if data['scenario_groupe'] == 'S1':
        return verifier_s1(data, analysis)
    # Ne pas appeler statistiques, comparer_groupes, comparer_cible ou calculer_groupes ici.
    rows = {row['id']: row for row in data['videos']}
    p = data['parametres_scenario']
    def independent(ids, metric):
        values = sorted(Decimal(str(rows[i][metric])) for i in ids if rows[i][metric] is not None)
        n = len(values)
        med = (values[(n - 1) // 2] + values[n // 2]) / 2 if n else None
        return {'effectif': len(ids), 'connus': n, 'absents': len(ids) - n,
                'somme_connue': sum(values, Decimal(0)) if n else None, 'mediane_connue': med}
    if data['scenario_groupe'] == 'S2':
        source = {f'{m}_{g}_{k}': v for m in ('vues', 'heures')
                  for g, ids in (('A', p['groupe_a']), ('B', p['groupe_b']))
                  for k, v in independent(ids, m).items()}
    else:
        stats = independent(p['references'], p['mesure'])
        value = Decimal(str(rows[p['cible']][p['mesure']]))
        source = {'cible': p['cible'], 'mesure': p['mesure'], 'valeur_cible': value, **stats,
                  'ecart_mediane': value - stats['mediane_connue'], 'sous_mediane': value < stats['mediane_connue']}
    candidate = analysis if isinstance(analysis, dict) else {}
    def matches(k, v):
        if k not in candidate:
            return False
        return type(candidate[k]) is bool and candidate[k] == v if isinstance(v, bool) else egal(candidate[k], v)
    checks = [{'code': k, 'controle': k, 'etat': 'reussi' if matches(k, v) else 'echoue',
               'observe': candidate.get(k), 'attendu': v} for k, v in source.items()]
    return {'verdict': 'refuse' if any(c['etat'] == 'echoue' for c in checks) else 'accepte_avec_reserves',
            'methode': 'recalcul_python_independant', 'scenario': data['scenario_groupe'], 'controles': checks,
            'mesures_sources': source, 'parametres_scenario': p,
            'avertissements': data['avertissements'] + ['Groupes choisis manuellement ; comparabilité à examiner par une personne.',
                'Médianes et sommes sur valeurs connues ; absences conservées. Aucune cause établie.',
                'Un groupe de référence d’une seule valeur connue reste une comparaison exploratoire.'],
            'limite': 'Calcul descriptif, sans validation automatique de la comparabilité ni de qualité éditoriale.'}


def formulation(report):
    if report.get('scenario') == 'S1':
        return formulation_s1(report)
    if report['verdict'] == 'refuse':
        return 'Comparaison refusée : contrôles échoués. Aucune conclusion validée.'
    s = report['mesures_sources']
    if report['scenario'] == 'S2':
        show = lambda value: 'indisponible' if value is None else str(value)
        return (f"Groupes A/B : médianes connues de {show(s['vues_A_mediane_connue'])}/{show(s['vues_B_mediane_connue'])} vues et "
                f"{show(s['heures_A_mediane_connue'])}/{show(s['heures_B_mediane_connue'])} heures. Groupes manuels, absences conservées ; aucune cause établie.")
    return (f"{s['cible']} : {s['valeur_cible']} {s['mesure']}, médiane de référence {s['mediane_connue']} "
            f"({s['connus']} valeur(s) connue(s), {s['absents']} absente(s)), écart {s['ecart_mediane']} {s['mesure']}. "
            'Comparaison exploratoire ; aucune cause ni échec général établis.')


def schema_synthese_groupes(report):
    return {'type': 'object', 'properties': {'resultat': {'type': 'string', 'enum': [formulation(report)]},
            'verdict_source': {'type': 'string', 'enum': [report['verdict']]}},
            'required': ['resultat', 'verdict_source'], 'additionalProperties': False}


def verifier_synthese_groupes(final, report):
    return {'sources_acceptees': report['verdict'] != 'refuse',
            'texte_encadre': isinstance(final, dict) and final.get('resultat') == formulation(report),
            'verdict_respecte': isinstance(final, dict) and final.get('verdict_source') == report['verdict']}
