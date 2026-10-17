"""Contrôles numériques indépendants des formulations produites par le modèle."""

from decimal import Decimal, InvalidOperation
import re


def verifier_audience(resultat, analyse):
    checks, warnings = [], list(resultat['resume']['avertissements'])
    rows = resultat['donnees']['Table data.csv']
    total = next(row['Engaged views'] for row in rows if row['Geography'] == 'Total')
    countries = {row['Geography']: row['Engaged views'] for row in rows if row['Geography'] != 'Total'}
    daily = {row['Date']: row['Engaged views'] for row in resultat['donnees']['Totals.csv']}
    by_country, by_date = {}, {}
    dates_by_country = {}
    for row in resultat['donnees']['Chart data.csv']:
        country, day, count = row['Geography'], row['Date'], row['Engaged views']
        by_country[country] = by_country.get(country, 0) + count
        by_date[day] = by_date.get(day, 0) + count
        dates_by_country.setdefault(country, set()).add(day)

    def check(code, title, valid, observed, expected, applicable=True):
        checks.append({'code': code, 'controle': title,
                       'etat': ('reussi' if valid else 'echoue') if applicable else 'non_applicable',
                       'observe': observed, 'attendu': expected})

    check('total_quotidien', 'Somme quotidienne égale à la ligne Total', sum(daily.values()) == total, sum(daily.values()), total)
    check('details_pays', 'Détails quotidiens et table concordants pour chaque pays', by_country == countries,
          'concordants' if by_country == countries else 'différents', 'mêmes pays et mêmes sommes')
    coverage = set(by_date) == set(daily) and all(days == set(daily) for days in dates_by_country.values())
    check('couverture_dates', 'Couverture quotidienne complète des pays détaillés', coverage,
          'complète' if coverage else 'différente ou incomplète', 'mêmes dates dans les séries')
    overflows = [day for day, count in by_date.items() if day not in daily or count > daily[day]]
    check('details_journaliers', 'Détails quotidiens inférieurs ou égaux au total quotidien', not overflows, overflows, [])
    detailed = sum(countries.values())
    check('borne_details', 'Somme des pays comprise entre zéro et le total', 0 <= detailed <= total, detailed, f'0 à {total}')

    leader = max(countries, key=countries.get) if countries else None
    peak = max(daily, key=daily.get)
    source = {
        'unite': 'vues engagées', 'periode': resultat['resume']['periode'],
        'total': total, 'somme_pays_detailles': detailed, 'ecart_non_explique': total - detailed,
        'somme_quotidienne': sum(daily.values()), 'pays_en_tete': leader,
        'volume_pays_en_tete': countries.get(leader), 'date_pic': peak, 'volume_pic': daily[peak],
    }
    if not isinstance(analyse, dict):
        analyse = {}
    for key, expected in source.items():
        observed = analyse.get(key)
        valid = key in analyse and observed == expected
        if isinstance(expected, int) and isinstance(observed, bool):
            valid = False
        check('analyse_' + key, 'Valeur calculée : ' + key, valid, observed, expected)

    expected_share = Decimal(countries[leader]) / Decimal(total) * 100 if leader is not None and total else None
    observed_share = analyse.get('part_du_total_pct')
    if expected_share is None:
        share_ok = observed_share is None and 'part_du_total_pct' in analyse
        check('pourcentage_indisponible', 'Aucun pourcentage inventé sans dénominateur', share_ok, observed_share, None)
        check('pourcentage', 'Part du pays dans le total', True, None, None, applicable=False)
        warnings.append('Pourcentage indisponible : dénominateur nul ou aucun pays détaillé.')
    else:
        try:
            observed_decimal = Decimal(str(observed_share))
            share_ok = observed_decimal.is_finite() and abs(observed_decimal - expected_share) <= Decimal('0.005')
        except InvalidOperation:
            share_ok = False
        check('pourcentage', 'Part calculée sur le total global, à 0,005 point près', share_ok,
              observed_share, float(expected_share.quantize(Decimal('0.01'))))
    source['part_du_total_pct'] = float(expected_share.quantize(Decimal('0.01'))) if expected_share is not None else None
    if total != detailed:
        warnings.append(f'Écart non expliqué entre total et pays détaillés : {total - detailed} vues engagées. Aucune cause attribuée.')
    if not countries:
        warnings.append('Aucun pays détaillé : classement indisponible.')
    elif countries[leader] == 0:
        warnings.append('Volumes détaillés tous nuls : le classement ne démontre aucune dominance.')
    ties = [country for country, count in countries.items() if count == countries.get(leader)]
    if len(ties) > 1:
        warnings.append('Plusieurs pays partagent le maximum : ' + ', '.join(ties))
    warnings.append('Sans identifiant vidéo, aucune recommandation par vidéo ou explication causale ne peut être validée.')
    warnings = list(dict.fromkeys(warnings))
    verdict = 'refuse' if any(c['etat'] == 'echoue' for c in checks) else 'accepte_avec_reserves'
    return {'version': 1, 'methode': 'recalcul_python_independant', 'verdict': verdict,
            'controles': checks, 'avertissements': warnings, 'mesures_sources': source,
            'limite': 'Contrôles de cohérence numérique, sans score de qualité éditoriale ou garantie commerciale.'}


def verifier_synthese(synthese, rapport):
    """Vérifier les champs structurés du coordonnateur, sans prétendre juger le texte libre."""
    if not isinstance(synthese, dict):
        return {'format_structure': False}
    source = rapport['mesures_sources']
    checks = {'verdict_respecte': synthese.get('verdict_source') == rapport['verdict'],
              'sources_acceptees': rapport['verdict'] != 'refuse',
              'texte_present': isinstance(synthese.get('resultat'), str) and bool(synthese['resultat'].strip())}
    text = synthese.get('resultat', '') if isinstance(synthese.get('resultat'), str) else ''
    compact = text.replace(' ', '').replace('\u202f', '').replace('\u00a0', '')
    country, volume = source['pays_en_tete'], source['volume_pays_en_tete']
    checks['texte_etaye'] = (
        bool(re.search(r'\b' + re.escape(country) + r'\b', text))
        and bool(re.search(r'(?<!\d)' + re.escape(str(volume)) + r'(?!\d)', compact))
    ) if country is not None and volume is not None else 'indisponible' in text.lower()
    for key in ('unite', 'pays_en_tete', 'volume_pays_en_tete', 'total', 'ecart_non_explique'):
        observed = synthese.get(key)
        checks[key] = key in synthese and observed == source[key]
        if isinstance(source[key], int) and isinstance(observed, bool):
            checks[key] = False
    return checks
