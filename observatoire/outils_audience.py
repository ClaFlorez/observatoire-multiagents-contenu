"""Calculs reproductibles communs aux outils CrewAI et aux contrôles."""


def calculer_audience(resultat):
    details = [r for r in resultat['donnees']['Table data.csv'] if r['Geography'] != 'Total']
    total = next(r['Engaged views'] for r in resultat['donnees']['Table data.csv'] if r['Geography'] == 'Total')
    somme = sum(r['Engaged views'] for r in details)
    daily = resultat['donnees']['Totals.csv']
    leader = max(details, key=lambda r: r['Engaged views']) if details else None
    return {
        'unite': 'vues engagées', 'periode': resultat['resume']['periode'],
        'total': total, 'somme_pays_detailles': somme, 'ecart_non_explique': total - somme,
        'somme_quotidienne': sum(r['Engaged views'] for r in daily),
        'pays_en_tete': leader['Geography'] if leader else None,
        'volume_pays_en_tete': leader['Engaged views'] if leader else None,
        'part_du_total_pct': round(leader['Engaged views'] / total * 100, 2) if leader and total else None,
        'date_pic': max(daily, key=lambda r: r['Engaged views'])['Date'],
        'volume_pic': max(r['Engaged views'] for r in daily),
        'limite': 'Aucune cause des écarts ni performance par vidéo ne peut être établie avec ces exports.',
    }
