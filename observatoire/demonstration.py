"""Simulation déterministe des rôles, sans modèle, clé ni connexion réseau."""

from datetime import datetime, timezone
from time import perf_counter
from uuid import uuid4


ROLES = ('Coordonnateur', 'Chercheur', 'Analyste', 'Vérificateur')
SCENARIOS = ('Concentration géographique', 'Évolution quotidienne')


def simuler(resultat, scenario):
    if scenario not in SCENARIOS:
        raise ValueError('Scénario de démonstration inconnu')
    steps, messages = [], []
    summary = resultat['resume']
    started = datetime.now(timezone.utc).isoformat()
    clock = perf_counter()

    def step(role, task, operation, tool=None):
        begin = perf_counter()
        begin_utc = datetime.now(timezone.utc).isoformat()
        output = operation()
        end = perf_counter()
        steps.append({
            'ordre': len(steps) + 1, 'agent': role, 'tache': task,
            'etat': 'terminee', 'debut_utc': begin_utc,
            'fin_utc': datetime.now(timezone.utc).isoformat(),
            'debut_ms': (begin - clock) * 1000,
            'duree_ms': (end - begin) * 1000,
            'outil': tool, 'sortie': output,
            'modele': None, 'jetons': 0, 'cout_api_usd': 0,
        })
        return output

    def send(source, target, text):
        messages.append({'ordre': len(messages) + 1, 'emetteur': source,
                         'destinataire': target, 'resume': text,
                         'apres_etape': len(steps)})

    step('Coordonnateur', 'Définir une mission prédéfinie', lambda: {
        'scenario': scenario, 'perimetre': summary['periode'],
        'limite': 'Aucune recommandation par vidéo sans export par contenu.',
    })
    send('Coordonnateur', 'Chercheur', 'Sélectionner les tables et vérifier leur provenance.')
    step('Chercheur', 'Consulter les données déjà importées', lambda: {
        'origine_donnees': summary['origine'], 'fichiers': summary['fichiers'],
        'avertissements': summary['avertissements'],
    }, 'consultation_import_local')
    send('Chercheur', 'Analyste', 'Calculer les indicateurs sur la période complète de cet import.')

    def calculate():
        daily = resultat['donnees']['Totals.csv']
        table = resultat['donnees']['Table data.csv']
        details = [row for row in table if row['Geography'] != 'Total']
        total_row = next(row for row in table if row['Geography'] == 'Total')
        full = total_row['Engaged views']
        detailed = sum(row['Engaged views'] for row in details)
        base = {'total': full, 'details': detailed, 'ecart': full - detailed,
                'somme_quotidienne': sum(row['Engaged views'] for row in daily),
                'unite': 'vues engagées'}
        if scenario == SCENARIOS[0]:
            leader = max(details, key=lambda row: row['Engaged views']) if details else None
            base.update({'pays_en_tete': leader['Geography'] if leader else None,
                         'volume_pays_en_tete': leader['Engaged views'] if leader else None,
                         'part_du_total_pct': leader['Engaged views'] / full * 100 if leader and full else None})
        else:
            peak = max(daily, key=lambda row: row['Engaged views'])
            base.update({'date_pic': peak['Date'], 'volume_pic': peak['Engaged views'],
                         'moyenne_quotidienne': base['somme_quotidienne'] / len(daily)})
        return base

    metrics = step('Analyste', 'Calculer les indicateurs avec Python', calculate, 'calcul_python')
    send('Analyste', 'Vérificateur', 'Contrôler le total, les détails et les limites du constat.')
    validation = step('Vérificateur', 'Appliquer des contrôles déterministes', lambda: {
        'total_coherent': metrics['somme_quotidienne'] == metrics['total'],
        'details_inferieurs_au_total': 0 <= metrics['details'] <= metrics['total'],
        'reserve': 'Un écart ne prouve pas sa cause. Aucun lien causal ni gain commercial démontré.',
        'type_validation': 'règles Python, sans jugement de modèle IA',
    })
    valid = validation['total_coherent'] and validation['details_inferieurs_au_total']
    if not valid:
        steps[-1]['etat'] = 'non_validee'
    send('Vérificateur', 'Coordonnateur', 'Constat accepté avec réserves.' if valid else 'Contrôles non satisfaits : ne pas conclure.')

    def final():
        if not valid:
            return 'Contrôles non satisfaits. Examiner les exports avant toute recommandation.'
        if scenario == SCENARIOS[0]:
            if metrics['pays_en_tete'] is None:
                return 'Aucun pays détaillé : classement indisponible.'
            return (f"Parmi les pays détaillés, {metrics['pays_en_tete']} possède le volume le plus élevé "
                    f"({metrics['volume_pays_en_tete']} vues engagées). "
                    'Approfondir avec un export par vidéo avant de choisir un sujet ou un format.')
        return (f"Le pic observé est le {metrics['date_pic']} avec {metrics['volume_pic']} vues engagées. "
                'Consulter les publications et les sources de trafic de cette date avant de proposer une explication.')

    conclusion = step('Coordonnateur', 'Assembler une synthèse prédéfinie', final)
    return {
        'id': str(uuid4()), 'mode': 'simulation', 'version': 1,
        'scenario': scenario, 'origine_donnees': summary['origine'],
        'provenance': summary['fichiers'], 'periode': summary['periode'],
        'debut_utc': started, 'duree_ms': (perf_counter() - clock) * 1000,
        'etat': 'terminee' if valid else 'non_validee',
        'etapes': steps, 'messages': messages, 'resultat': conclusion,
        'jetons': 0, 'cout_api_usd': 0, 'appels_modele': 0,
        'eligible_campagne_reelle': False,
    }
