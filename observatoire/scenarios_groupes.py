"""Calculs descriptifs S2/S4 sur des groupes choisis explicitement."""

from decimal import Decimal
from statistics import median


def selection(report, identifiers):
    ids = list(identifiers)
    if not ids or len(ids) != len(set(ids)):
        raise ValueError('Choisir un groupe non vide, sans identifiant répété.')
    rows = {row['id']: row for row in report['videos']}
    if any(identifier not in rows for identifier in ids):
        raise ValueError('Un identifiant est absent de cet instantané.')
    return [rows[identifier] for identifier in sorted(ids)]


def statistiques(rows, metric):
    known = [Decimal(str(row[metric])) for row in rows if row[metric] is not None]
    return {'effectif': len(rows), 'connus': len(known), 'absents': len(rows) - len(known),
            'somme_connue': sum(known, Decimal(0)) if known else None,
            'mediane_connue': median(known) if known else None}


def comparer_groupes(report, groupe_a, groupe_b):
    a, b = selection(report, groupe_a), selection(report, groupe_b)
    if set(groupe_a) & set(groupe_b):
        raise ValueError('Les deux groupes doivent être distincts, sans vidéo commune.')
    return {metric: {'A': statistiques(a, metric), 'B': statistiques(b, metric)}
            for metric in ('vues', 'heures')}


def comparer_cible(report, cible, reference, metric):
    if metric not in ('vues', 'heures'):
        raise ValueError('Choisir vues ou heures.')
    target = selection(report, [cible])[0]
    rows = selection(report, reference)
    if cible in reference:
        raise ValueError('La cible doit être exclue du groupe de référence.')
    stats = statistiques(rows, metric)
    if target[metric] is None or stats['mediane_connue'] is None:
        raise ValueError('La cible et au moins une référence doivent avoir une valeur connue.')
    value = Decimal(str(target[metric]))
    return {'cible': cible, 'mesure': metric, 'valeur_cible': value, **stats,
            'ecart_mediane': value - stats['mediane_connue'],
            'sous_mediane': value < stats['mediane_connue']}
