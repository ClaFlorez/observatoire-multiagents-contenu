"""Comparaison descriptive par vidéo et vérification indépendante des chiffres."""

from decimal import Decimal, InvalidOperation
import re


def calculer_videos(data):
    videos = data['videos']
    views = [v for v in videos if v['vues'] is not None]
    hours = [v for v in videos if v['heures'] is not None]
    first_views = max(views, key=lambda v: v['vues']) if views else None
    first_hours = max(hours, key=lambda v: v['heures']) if hours else None
    return {
        'nb_videos': len(videos), 'total_vues': data['total']['vues'],
        'somme_vues_connues': sum(v['vues'] for v in views), 'vues_absentes': len(videos) - len(views),
        'total_heures': data['total']['heures'],
        'somme_heures_connues': sum((v['heures'] for v in hours), Decimal(0)),
        'heures_absentes': len(videos) - len(hours),
        'video_vues_id': first_views['id'] if first_views else None,
        'video_vues_valeur': first_views['vues'] if first_views else None,
        'video_heures_id': first_hours['id'] if first_hours else None,
        'video_heures_valeur': first_hours['heures'] if first_hours else None,
        'top_vues': [{'id': v['id'], 'vues': v['vues'], 'heures': v['heures']} for v in sorted(views, key=lambda v: v['vues'], reverse=True)[:3]],
        'top_heures': [{'id': v['id'], 'vues': v['vues'], 'heures': v['heures']} for v in sorted(hours, key=lambda v: v['heures'], reverse=True)[:3]],
        'limite': 'Classements des valeurs connues uniquement ; aucun format, lien causal ou résultat futur déduit.',
    }


def egal(observed, expected):
    if expected is None:
        return observed is None
    if isinstance(expected, (int, Decimal)):
        if isinstance(observed, bool):
            return False
        try:
            value = Decimal(str(observed))
            return value.is_finite() and value == Decimal(str(expected))
        except (InvalidOperation, ValueError):
            return False
    return observed == expected


def verifier_videos(data, analysis):
    checks = []
    rows = data['videos']
    view_pairs = [(v['id'], v['vues']) for v in rows if v['vues'] is not None]
    hour_pairs = [(v['id'], Decimal(str(v['heures']))) for v in rows if v['heures'] is not None]
    # Chemin de recalcul distinct : aucune réutilisation de calculer_videos.
    leader_v = sorted(view_pairs, key=lambda pair: pair[1], reverse=True)
    leader_h = sorted(hour_pairs, key=lambda pair: pair[1], reverse=True)
    source = {
        'nb_videos': len(rows), 'total_vues': data['total']['vues'],
        'somme_vues_connues': sum(pair[1] for pair in view_pairs),
        'vues_absentes': sum(v['vues'] is None for v in rows),
        'total_heures': data['total']['heures'],
        'somme_heures_connues': sum((pair[1] for pair in hour_pairs), Decimal(0)),
        'heures_absentes': sum(v['heures'] is None for v in rows),
        'video_vues_id': leader_v[0][0] if leader_v else None,
        'video_vues_valeur': leader_v[0][1] if leader_v else None,
        'video_heures_id': leader_h[0][0] if leader_h else None,
        'video_heures_valeur': leader_h[0][1] if leader_h else None,
    }
    def check(code, label, valid, observed, expected):
        checks.append({'code': code, 'controle': label, 'etat': 'reussi' if valid else 'echoue',
                       'observe': observed, 'attendu': expected})
    check('identifiants', 'Identifiants vidéo uniques', len({v['id'] for v in rows}) == len(rows), len({v['id'] for v in rows}), len(rows))
    if not isinstance(analysis, dict):
        analysis = {}
    for key, expected in source.items():
        observed = analysis.get(key)
        check(key, 'Mesure par vidéo : ' + key, key in analysis and egal(observed, expected), observed, expected)
    for field, pairs in (('top_vues', leader_v), ('top_heures', leader_h)):
        expected = [pair[0] for pair in pairs[:3]]
        observed = analysis.get(field)
        ids = [v.get('id') for v in observed if isinstance(v, dict)] if isinstance(observed, list) else None
        check(field, 'Ordre du classement : ' + field, ids == expected, ids, expected)
        values_ok = isinstance(observed, list) and len(observed) == len(expected)
        indexed = {v['id']: v for v in rows}
        if values_ok:
            for v in observed:
                original = indexed.get(v.get('id')) if isinstance(v, dict) else None
                if original is None or not all(k in v and egal(v[k], original[k]) for k in ('vues', 'heures')):
                    values_ok = False
        check(field + '_valeurs', 'Valeurs et absences conservées : ' + field, values_ok, values_ok, True)
    total = source['total_vues']
    check('borne_vues', 'Somme des vues connues compatible avec le total',
          total is None or source['somme_vues_connues'] <= total,
          source['somme_vues_connues'], total)
    warnings = list(data['avertissements'])
    warnings.extend([
        'Les classements portent sur des valeurs connues, pas sur les cellules absentes.',
        'Une recommandation éditoriale est une hypothèse à tester, sans garantie de vues ou de croissance.',
        'Ni la durée seule ni le titre ne prouvent le format Short ; les dates de publication ne définissent pas la période statistique.',
    ])
    if not leader_v or not leader_h:
        warnings.append('Un des classements est indisponible ; ne pas inventer de vidéo en tête.')
    for pairs, label in ((leader_v, 'vues'), (leader_h, 'heures')):
        if len(pairs) > 1 and pairs[0][1] == pairs[1][1]:
            warnings.append(f'Ex æquo au maximum pour {label} ; le premier correspond à l’ordre source.')
    return {'version': 1, 'methode': 'recalcul_python_independant',
            'verdict': 'refuse' if any(c['etat'] == 'echoue' for c in checks) else 'accepte_avec_reserves',
            'controles': checks, 'avertissements': list(dict.fromkeys(warnings)), 'mesures_sources': source,
            'limite': 'Cohérence descriptive vérifiée ; aucune causalité ni qualité éditoriale complète démontrée.'}


def recommandations_encadrees(report):
    source = report['mesures_sources']
    leaders = list(dict.fromkeys(v for v in (source['video_vues_id'], source['video_heures_id']) if v))
    return [f'Tester {action} sur un futur contenu inspiré de {video} ; comparer les {measure} sur une période de même longueur, sans gain garanti.'
            for video in leaders for action in ('un nouvel angle', 'une variante de présentation') for measure in ('vues', 'heures')]


def schema_synthese_videos(report=None):
    properties = {
        'resultat': {'type': 'string', 'maxLength': 350},
        'recommandation': {'type': 'string', 'maxLength': 250},
        'statut_recommandation': {'type': 'string', 'enum': ['hypothese_a_tester']},
        'video_reference': {'type': ['string', 'null']},
        'indicateur_test': {'type': 'string', 'enum': ['vues', 'heures']},
        'verdict_source': {'type': 'string', 'enum': ['accepte_avec_reserves', 'refuse']},
        'nb_videos': {'type': 'integer'}, 'total_vues': {'type': ['integer', 'null']},
        'vues_absentes': {'type': 'integer'},
        'video_vues_id': {'type': ['string', 'null']}, 'video_vues_valeur': {'type': ['integer', 'null']},
        'video_heures_id': {'type': ['string', 'null']}, 'video_heures_valeur': {'type': ['number', 'null']},
    }
    if report and recommandations_encadrees(report):
        properties['recommandation']['enum'] = recommandations_encadrees(report)
    return {'type': 'object', 'properties': properties, 'required': list(properties), 'additionalProperties': False}


def verifier_synthese_videos(final, report):
    if not isinstance(final, dict):
        return {'format_structure': False}
    checks = {'sources_acceptees': report['verdict'] != 'refuse',
              'verdict_respecte': final.get('verdict_source') == report['verdict'],
              'recommandation_presente': isinstance(final.get('recommandation'), str) and bool(final['recommandation'].strip()),
              'hypothese_explicite': final.get('statut_recommandation') == 'hypothese_a_tester'}
    for key in ('nb_videos', 'total_vues', 'vues_absentes', 'video_vues_id', 'video_vues_valeur', 'video_heures_id', 'video_heures_valeur'):
        expected = report['mesures_sources'][key]
        if key == 'video_heures_valeur' and expected is not None:
            expected = Decimal(str(expected))
        checks[key] = key in final and egal(final[key], expected)
    text = final.get('resultat') if isinstance(final.get('resultat'), str) else ''
    source = report['mesures_sources']
    leader = source['video_vues_id']
    compact = text.replace(' ', '').replace('\u202f', '').replace('\u00a0', '')
    checks['texte_etaye'] = (bool(re.search(re.escape(leader), text)) and
                             bool(re.search(r'(?<!\d)' + str(source['video_vues_valeur']) + r'(?!\d)', compact))) if leader else 'indisponible' in text.lower()
    recommendation = final.get('recommandation', '')
    recommendation = recommendation if isinstance(recommendation, str) else ''
    reference = final.get('video_reference')
    allowed = {v for v in (leader, source['video_heures_id']) if v is not None}
    checks['reference_recommandation'] = reference in allowed and reference in recommendation if allowed else reference is None
    checks['indicateur_test'] = final.get('indicateur_test') in ('vues', 'heures')
    checks['action_cadree'] = recommendation in recommandations_encadrees(report)
    checks['indicateur_texte_coherent'] = ('comparer les ' + str(final.get('indicateur_test')) + ' sur') in recommendation
    hours = source['video_heures_valeur']
    checks['texte_heures_exactes'] = (source['video_heures_id'] in text and bool(re.search(
        r'(?<![\d.,])' + re.escape(str(hours)).replace(r'\.', '[.,]') + r'\s*heures\b', text))) if hours is not None else 'indisponible' in text.lower()
    checks['aucune_conversion_horaire'] = not bool(re.search(r'\d\s*h\s*\d', text, re.IGNORECASE))
    # Filet lexical limité : il ne remplace pas une évaluation humaine du sens.
    checks['absences_non_assimilees_zero'] = not bool(re.search(
        r'sans (?:vues|heures)|(?:manquantes|absentes).{0,25}(?:expliquent|causent)|(?<!sans )gain garanti|\d+ vues et \d+ heures absentes',
        text + ' ' + recommendation, flags=re.IGNORECASE))
    return checks


def contexte_synthese_videos(report):
    """Transmission compacte, sans modifier ni effacer le rapport complet sauvegardé."""
    return {'verdict': report['verdict'], 'mesures_sources': report['mesures_sources'],
            'avertissements': report['avertissements'], 'limite': report['limite'],
            'controles_reussis': sum(c['etat'] == 'reussi' for c in report['controles']),
            'controles_echoues': [c for c in report['controles'] if c['etat'] == 'echoue']}
