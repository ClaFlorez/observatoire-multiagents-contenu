"""Comparaison descriptive de deux exports vidéo, sans appel IA."""

from datetime import date
from decimal import Decimal


def comparer_periodes(avant, apres):
    periods = []
    for report in (avant, apres):
        start, end = (date.fromisoformat(report['periode'][k]) for k in ('debut', 'fin'))
        if end < start:
            raise ValueError('Période inversée.')
        periods.append((start, end, (end - start).days + 1))
    if periods[0][2] != periods[1][2]:
        raise ValueError('Les périodes doivent avoir la même longueur.')
    if periods[0][1] >= periods[1][0]:
        raise ValueError('La période de référence doit précéder la période courante, sans chevauchement.')
    if avant['origine'] != apres['origine']:
        raise ValueError('Ne pas comparer une origine réelle et une origine fictive.')
    if avant['fichier']['sha256'] == apres['fichier']['sha256']:
        raise ValueError('Le même fichier ne prouve pas deux périodes distinctes.')
    old = {v['id']: v for v in avant['videos']}
    new = {v['id']: v for v in apres['videos']}
    common = sorted(old.keys() & new.keys())
    def delta(a, b):
        if a is None or b is None:
            return {'avant': a, 'apres': b, 'ecart': None, 'variation_pct': None}
        a, b = Decimal(str(a)), Decimal(str(b))
        return {'avant': a, 'apres': b, 'ecart': b - a,
                'variation_pct': (b - a) / a * 100 if a != 0 else None}
    totals, matched, rows = {}, {}, []
    for metric in ('vues', 'heures'):
        totals[metric] = delta(avant['total'][metric], apres['total'][metric])
        eligible = [i for i in common if old[i][metric] is not None and new[i][metric] is not None]
        matched[metric] = {'nb_paires_connues': len(eligible),
                           'nb_paires_incompletes': len(common) - len(eligible),
                           **delta(sum((Decimal(str(old[i][metric])) for i in eligible), Decimal(0)),
                                   sum((Decimal(str(new[i][metric])) for i in eligible), Decimal(0)))}
        # Aucune observation ne devient un volume connu nul par une somme vide.
        if not eligible:
            matched[metric].update(avant=None, apres=None, ecart=None, variation_pct=None)
    for i in common:
        rows.append({'id': i, 'titre': new[i]['titre'] or old[i]['titre'],
                     **{metric: delta(old[i][metric], new[i][metric]) for metric in ('vues', 'heures')}})
    return {'jours_par_periode': periods[0][2], 'periode_avant': avant['periode'],
            'periode_apres': apres['periode'], 'fichiers': [avant['fichier'], apres['fichier']],
            'nb_avant': len(old), 'nb_apres': len(new), 'nb_communs': len(common),
            'uniquement_avant': sorted(old.keys() - new.keys()),
            'uniquement_apres': sorted(new.keys() - old.keys()),
            'totaux_canal': totals, 'cohorte_appariee': matched, 'videos_communes': rows,
            'limites': ['Les identifiants présents dans un seul export ne sont pas assimilés à zéro dans l’autre.',
                        'Les totaux du canal et la cohorte appariée décrivent des populations différentes.',
                        'Les écarts sont descriptifs ; aucune cause ni effet éditorial ne sont établis.',
                        'Les périodes restent déclarées par l’utilisateur ; leur contenu ne peut être prouvé par cette table seule.']}
