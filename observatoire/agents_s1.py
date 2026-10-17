"""S1 : trois premières vidéos par mesure, ordre source pour les ex æquo."""
from decimal import Decimal
from observatoire.analyse_videos import egal


def calculer_s1(data):
    rows = data['videos']
    result = {'nb_videos': len(rows)}
    for metric in ('vues', 'heures'):
        known = [r for r in rows if r[metric] is not None]
        result[metric + '_absentes'] = len(rows) - len(known)
        result[metric + '_classees'] = min(3, len(known))
        top = sorted(known, key=lambda r: Decimal(str(r[metric])), reverse=True)[:3]
        for n in range(3):
            row = top[n] if n < len(top) else None
            result[f'{metric}_{n+1}_id'] = row['id'] if row else None
            result[f'{metric}_{n+1}_valeur'] = row[metric] if row else None
    return result


def verifier_s1(data, analysis):
    # Rang calculé par comptage des valeurs précédentes, sans réutiliser le calculateur.
    rows = data['videos']
    source = {'nb_videos': len(rows)}
    for metric in ('vues', 'heures'):
        known = [(index, row['id'], Decimal(str(row[metric]))) for index, row in enumerate(rows) if row[metric] is not None]
        source[metric + '_absentes'] = len(rows) - len(known)
        source[metric + '_classees'] = min(3, len(known))
        ranks = {}
        for index, identifier, value in known:
            rank = 1 + sum(other > value or (other == value and position < index) for position, _, other in known)
            if rank <= 3:
                ranks[rank] = (identifier, value)
        for rank in range(1, 4):
            identifier, value = ranks.get(rank, (None, None))
            source[f'{metric}_{rank}_id'] = identifier
            source[f'{metric}_{rank}_valeur'] = value
    candidate = analysis if isinstance(analysis, dict) else {}
    checks = [{'code': k, 'controle': k, 'etat': 'reussi' if k in candidate and egal(candidate[k], v) else 'echoue',
               'observe': candidate.get(k), 'attendu': v} for k, v in source.items()]
    checks.append({'code': 'identifiants_uniques', 'controle': 'Identifiants uniques',
                   'etat': 'reussi' if len({r['id'] for r in rows}) == len(rows) else 'echoue',
                   'observe': len({r['id'] for r in rows}), 'attendu': len(rows)})
    return {'scenario': 'S1', 'methode': 'recalcul_python_independant',
            'verdict': 'refuse' if any(c['etat'] == 'echoue' for c in checks) else 'accepte_avec_reserves',
            'controles': checks, 'mesures_sources': source,
            'avertissements': data['avertissements'] + [
                'Classements séparés sur valeurs connues ; rang indisponible si moins de trois valeurs connues.',
                'Ex æquo départagés par l’ordre du CSV, sans supériorité entre valeurs égales.',
                'Absences distinctes de zéro ; vues et heures ne prouvent ni causalité ni format vidéo.'],
            'limite': 'Comparaison descriptive du même import complet, indépendante des filtres du classement.'}


def formulation_s1(report):
    if report['verdict'] == 'refuse':
        return 'Classements S1 refusés : contrôles échoués. Aucune conclusion validée.'
    s = report['mesures_sources']
    parts = []
    for metric in ('vues', 'heures'):
        entries = [f"{rank}. {s[f'{metric}_{rank}_id']} ({s[f'{metric}_{rank}_valeur']})"
                   for rank in range(1, 4) if s[f'{metric}_{rank}_id'] is not None]
        parts.append(f"Top {metric} : " + (' ; '.join(entries) or 'indisponible') + f" ; {s[metric + '_absentes']} valeur(s) absente(s).")
    return ' '.join(parts) + ' Ordre source pour les ex æquo ; aucune cause établie.'
