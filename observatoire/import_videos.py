"""Import autonome de Table data.csv par vidéo ; aucune jointure avec les playlists."""

import csv
from datetime import date
from decimal import Decimal
import hashlib
from pathlib import Path
import re

from observatoire.import_youtube import ImportInvalide, nombre


COLUMNS = ('Content', 'Video title', 'Video publish time', 'Duration', 'Views',
           'Watch time (hours)', 'Subscribers', 'Average view duration',
           'Thumbnail impressions', 'Thumbnail click-through rate (%)')
MONTHS = {name: i + 1 for i, name in enumerate(('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'))}


def date_publication(value):
    if not value:
        return None
    try:
        return date.fromisoformat(value).isoformat()
    except ValueError:
        match = re.fullmatch(r'([A-Za-z]{3}) (\d{1,2}), (\d{4})', value)
        if not match or match[1] not in MONTHS:
            raise ImportInvalide('date de publication non reconnue') from None
        return date(int(match[3]), MONTHS[match[1]], int(match[2])).isoformat()


def entier(value, column):
    number = nombre(value, column)
    if number is not None and number != int(number):
        raise ImportInvalide(f'{column} : entier attendu')
    return int(number) if number is not None else None


def importer_videos(source, debut, fin, origine):
    source = Path(source)
    if source.suffix.lower() != '.csv':
        raise ImportInvalide('Un fichier CSV par vidéo est requis')
    try:
        debut, fin = date.fromisoformat(debut), date.fromisoformat(fin)
    except ValueError:
        raise ImportInvalide('Période invalide') from None
    if debut > fin:
        raise ImportInvalide('La date de début dépasse la date de fin')
    if origine not in ('fictive', 'reelle'):
        raise ImportInvalide('Origine inconnue')
    videos, totals, seen = [], [], set()
    try:
        with source.open(encoding='utf-8-sig', newline='') as handle:
            reader = csv.DictReader(handle)
            headers = reader.fieldnames or []
            if len(headers) != len(set(headers)) or set(COLUMNS) - set(headers):
                raise ImportInvalide('Colonnes du rapport par vidéo absentes ou dupliquées')
            for line, raw in enumerate(reader, 2):
                try:
                    if None in raw or any(raw[c] is None for c in COLUMNS):
                        raise ImportInvalide('Nombre de cellules incorrect')
                    row = {key: raw[key].strip() for key in COLUMNS}
                    identifier = row['Content']
                    if identifier in seen:
                        raise ImportInvalide('Identifiant dupliqué')
                    seen.add(identifier)
                    if identifier != 'Total' and not re.fullmatch(r'[A-Za-z0-9_-]{11}', identifier):
                        raise ImportInvalide('Identifiant vidéo invalide')
                    duration = row['Average view duration']
                    if duration and not re.fullmatch(r'\d+:[0-5]\d:[0-5]\d', duration):
                        raise ImportInvalide('Durée moyenne attendue au format H:MM:SS')
                    average = None
                    if duration:
                        h, m, s = map(int, duration.split(':'))
                        average = h * 3600 + m * 60 + s
                    parsed = {
                        'id': identifier, 'titre': row['Video title'] or None,
                        'publication': date_publication(row['Video publish time']),
                        'duree_video_s': entier(row['Duration'], 'Duration'),
                        'vues': entier(row['Views'], 'Views'),
                        'heures': nombre(row['Watch time (hours)'], 'Watch time (hours)'),
                        'abonnes': entier(row['Subscribers'], 'Subscribers'),
                        'duree_moyenne_s': average,
                        'impressions': entier(row['Thumbnail impressions'], 'Thumbnail impressions'),
                        'ctr_pct': nombre(row['Thumbnail click-through rate (%)'], 'Thumbnail click-through rate (%)'),
                    }
                    (totals if identifier == 'Total' else videos).append(parsed)
                except ValueError as exc:
                    raise ImportInvalide(f'Table vidéo, ligne {line} : {exc}') from None
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
    except OSError:
        raise ImportInvalide('Lecture du fichier par vidéo impossible') from None
    if len(totals) != 1 or not videos:
        raise ImportInvalide('Une ligne Total et au moins une vidéo sont requises')
    warnings, comparisons = [], []
    for key, label in (('vues', 'vues'), ('heures', 'heures de visionnage'), ('impressions', 'impressions')):
        known = [v[key] for v in videos if v[key] is not None]
        summed = sum(known, Decimal(0))
        total = totals[0][key]
        missing = len(videos) - len(known)
        delta = Decimal(str(total)) - summed if total is not None else None
        comparisons.append({'mesure': label, 'total_source': total, 'somme_connue': summed,
                            'valeurs_absentes': missing, 'ecart_total_details': delta})
        if missing:
            warnings.append(f'{missing} vidéo(s) sans valeur pour {label} : absence conservée, jamais assimilée à zéro.')
        if delta is not None and delta != 0:
            warnings.append(f'Écart entre total et détails connus pour {label} : {delta}. Cause non établie ; les arrondis peuvent intervenir pour les heures.')
    no_date = sum(v['publication'] is None for v in videos)
    if no_date:
        warnings.append(f'{no_date} vidéo(s) sans date de publication ; aucune date inventée.')
    if any(v['ctr_pct'] is not None and v['ctr_pct'] > 100 for v in videos):
        warnings.append('Un taux de clics dépasse 100 % : valeur conservée pour vérification.')
    warnings.extend([
        'La période statistique est déclarée par l’utilisateur : elle ne figure pas dans cette table.',
        'Vues (Views) et vues engagées (Engaged views) sont des mesures distinctes.',
        'Les dates de publication ne définissent pas la période des statistiques et ne prouvent pas le format Short.',
        'Les fichiers de playlists ne sont pas joints à cette table. Les moyennes et taux ne sont pas additionnés.',
    ])
    return {'type': 'videos', 'origine': origine,
            'periode': {'debut': debut.isoformat(), 'fin': fin.isoformat(), 'source': 'declaration_utilisateur'},
            'fichier': {'nom': source.name, 'sha256': digest},
            'videos': videos, 'total': totals[0], 'rapprochements': comparisons, 'avertissements': warnings}
