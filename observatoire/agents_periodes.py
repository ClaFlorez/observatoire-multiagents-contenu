"""Outils et contrat de synthèse du scénario S3."""

from datetime import date
from decimal import Decimal

from observatoire.stockage import charger_import_videos
from observatoire.comparaison_periodes import comparer_periodes
from observatoire.analyse_videos import egal


def charger_paire(database, identifier):
    before_id, after_id = identifier.split(':')
    before, after = (charger_import_videos(database, i) for i in (before_id, after_id))
    comparer_periodes(before, after)  # Refuser les entrées incompatibles avant toute inférence.
    return {'avant': before, 'apres': after, 'origine': after['origine'],
            'fichier': [before['fichier'], after['fichier']],
            'periode': {'avant': before['periode'], 'apres': after['periode']},
            'avertissements': list(dict.fromkeys(before['avertissements'] + after['avertissements']))}


def calculer_periodes(pair):
    c = comparer_periodes(pair['avant'], pair['apres'])
    result = {k: c[k] for k in ('jours_par_periode', 'nb_avant', 'nb_apres', 'nb_communs')}
    for name, population in (('canal', 'totaux_canal'), ('cohorte', 'cohorte_appariee')):
        for metric in ('vues', 'heures'):
            for key, value in c[population][metric].items():
                result[f'{name}_{metric}_{key}'] = value.quantize(Decimal('.0001')) if key == 'variation_pct' and value is not None else value
    return result


def verifier_periodes(pair, analysis):
    # Recalcul indépendant, sans appel au calculateur ni au comparateur.
    a, b = pair['avant'], pair['apres']
    old, new = ({v['id']: v for v in report['videos']} for report in (a, b))
    common = old.keys() & new.keys()
    days = lambda r: (date.fromisoformat(r['periode']['fin']) - date.fromisoformat(r['periode']['debut'])).days + 1
    source = {'jours_par_periode': days(a), 'nb_avant': len(old), 'nb_apres': len(new), 'nb_communs': len(common)}
    checks = []
    def check(key, valid, observed, expected):
        checks.append({'code': key, 'controle': key, 'etat': 'reussi' if valid else 'echoue', 'observe': observed, 'attendu': expected})
    check('periodes_compatibles', days(a) == days(b) and days(a) > 0 and a['periode']['fin'] < b['periode']['debut'] and a['origine'] == b['origine'] and a['fichier']['sha256'] != b['fichier']['sha256'], pair['periode'], 'Même longueur, ordre sans chevauchement, même origine, fichiers distincts')
    for metric in ('vues', 'heures'):
        ids = [i for i in common if old[i][metric] is not None and new[i][metric] is not None]
        for population in ('canal', 'cohorte'):
            if population == 'canal':
                values = [r['total'][metric] for r in (a, b)]
            else:
                values = [sum((Decimal(str(rows[i][metric])) for i in ids), Decimal(0)) if ids else None for rows in (old, new)]
                source[f'cohorte_{metric}_nb_paires_connues'] = len(ids)
                source[f'cohorte_{metric}_nb_paires_incompletes'] = len(common) - len(ids)
            x, y = (Decimal(str(v)) if v is not None else None for v in values)
            difference = y - x if x is not None and y is not None else None
            pct = (difference / x * 100).quantize(Decimal('.0001')) if difference is not None and x != 0 else None
            for key, value in zip(('avant', 'apres', 'ecart', 'variation_pct'), (x, y, difference, pct)):
                source[f'{population}_{metric}_{key}'] = value
    candidate = analysis if isinstance(analysis, dict) else {}
    for key, value in source.items():
        check(key, key in candidate and egal(candidate[key], value), candidate.get(key), value)
    warnings = pair['avertissements'] + ['Deux populations distinctes : canal complet et cohorte de paires connues.',
        'Identifiants présents dans un seul export et valeurs absentes : jamais remplacés par zéro.',
        'Comparaison descriptive ; aucune cause ni effet éditorial établis. Les dates sont déclarées par l’utilisateur.']
    return {'version': 1, 'methode': 'recalcul_python_independant',
            'verdict': 'refuse' if any(c['etat'] == 'echoue' for c in checks) else 'accepte_avec_reserves',
            'controles': checks, 'avertissements': list(dict.fromkeys(warnings)), 'mesures_sources': source,
            'limite': 'Les populations et dénominateurs diffèrent ; aucune cause attribuée.'}


FINAL_FIELDS = ('nb_communs', 'cohorte_vues_nb_paires_connues', 'cohorte_heures_nb_paires_connues',
                'canal_vues_ecart', 'canal_heures_ecart', 'cohorte_vues_ecart', 'cohorte_heures_ecart')


def formulations(report):
    if report['verdict'] == 'refuse':
        return ['Comparaison refusée : les contrôles ont échoué. Aucune conclusion validée.']
    s = report['mesures_sources']
    return [f"Canal complet : écart de {s['canal_vues_ecart']} vues et {s['canal_heures_ecart']} heures. Cohorte appariée : écart de {s['cohorte_vues_ecart']} vues et {s['cohorte_heures_ecart']} heures. Populations distinctes ; aucune cause établie.",
            f"{s['nb_communs']} identifiants communs ; {s['cohorte_vues_nb_paires_connues']} paires connues pour les vues et {s['cohorte_heures_nb_paires_connues']} pour les heures. Absences conservées ; ne pas confondre cette cohorte avec les totaux du canal. Aucune cause établie."]


def schema_synthese_periodes(report):
    props = {'resultat': {'type': 'string', 'enum': formulations(report)},
             'verdict_source': {'type': 'string', 'enum': ['accepte_avec_reserves', 'refuse']}}
    props.update({key: {'type': ['number', 'null']} for key in FINAL_FIELDS})
    return {'type': 'object', 'properties': props, 'required': list(props), 'additionalProperties': False}


def verifier_synthese_periodes(final, report):
    if not isinstance(final, dict):
        return {'format_structure': False}
    source = report['mesures_sources']
    result = {'sources_acceptees': report['verdict'] != 'refuse',
              'verdict_respecte': final.get('verdict_source') == report['verdict'],
              'texte_encadre': final.get('resultat') in formulations(report)}
    for key in FINAL_FIELDS:
        value = source[key]
        result[key] = key in final and egal(final[key], Decimal(str(value)) if value is not None else None)
    return result
