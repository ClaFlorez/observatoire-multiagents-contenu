"""Contrôler trois exports Studio sans modifier les sources."""

import argparse
import csv
import hashlib
import json
import re
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path


class ImportInvalide(ValueError):
    """Un export ne respecte pas le contrat attendu."""


SCHEMAS = {
    'Chart data.csv': ('Date', 'Geography', 'Engaged views'),
    'Totals.csv': ('Date', 'Engaged views'),
    'Table data.csv': (
        'Geography', 'Engaged views', 'Subscribers',
        'Average percentage viewed (%)', 'Playlist watch time (hours)',
        'Card clicks', 'Views', 'Watch time (hours)', 'Average view duration',
    ),
}
COUNTS = {'Engaged views', 'Subscribers', 'Card clicks', 'Views'}
DECIMALS = {
    'Average percentage viewed (%)', 'Playlist watch time (hours)',
    'Watch time (hours)',
}


def nombre(value, column):
    if not value:
        return None
    try:
        parsed = Decimal(value)
    except InvalidOperation as exc:
        raise ImportInvalide(f'{column} : nombre invalide') from exc
    if not parsed.is_finite():
        raise ImportInvalide(f'{column} : nombre non fini')
    if column in COUNTS and parsed != parsed.to_integral_value():
        raise ImportInvalide(f'{column} : entier attendu')
    if parsed < 0 and column != 'Subscribers':
        raise ImportInvalide(f'{column} : valeur négative')
    return int(parsed) if column in COUNTS else parsed


def lire_fichier(path):
    expected = SCHEMAS[path.name]
    rows, keys, warnings = [], set(), []
    with path.open(encoding='utf-8-sig', newline='') as handle:
        reader = csv.DictReader(handle)
        headers = reader.fieldnames or []
        if len(headers) != len(set(headers)):
            raise ImportInvalide(f'{path.name} : colonnes dupliquées')
        missing = set(expected) - set(headers)
        if missing:
            if 'Content' in headers and 'Video title' in headers:
                raise ImportInvalide('Export par vidéo détecté : choisir Contenu par vidéo dans Type de rapport.')
            raise ImportInvalide(f'{path.name} : colonnes absentes : {sorted(missing)}')
        for line, raw in enumerate(reader, 2):
            try:
                if None in raw or any(raw[col] is None for col in expected):
                    raise ImportInvalide('nombre de cellules incorrect')
                row = {}
                for column in expected:
                    value = raw[column].strip()
                    if column == 'Date':
                        row[column] = date.fromisoformat(value).isoformat()
                    elif column == 'Geography':
                        if value != 'Total' and not re.fullmatch(r'[A-Z]{2}', value):
                            raise ImportInvalide('code pays invalide')
                        if value == 'Total' and path.name != 'Table data.csv':
                            raise ImportInvalide('Total interdit dans les détails quotidiens')
                        row[column] = value
                    elif column == 'Average view duration':
                        if not value:
                            row[column] = None
                        else:
                            if not re.fullmatch(r'\d+:[0-5]\d:[0-5]\d', value):
                                raise ImportInvalide('durée attendue au format H:MM:SS')
                            hours, minutes, seconds = map(int, value.split(':'))
                            row[column] = hours * 3600 + minutes * 60 + seconds
                    else:
                        row[column] = nombre(value, column)
                if row['Engaged views'] is None:
                    raise ImportInvalide('vues engagées manquantes')
                key = tuple(row[col] for col in ('Date', 'Geography') if col in row)
                if key in keys:
                    raise ImportInvalide('doublon de granularité')
                keys.add(key)
                percentage = row.get('Average percentage viewed (%)')
                if percentage is not None and percentage > 100:
                    warnings.append(f'{path.name}, ligne {line} : pourcentage supérieur à 100 %, conservé pour vérification.')
                rows.append(row)
            except (ValueError, InvalidOperation) as exc:
                raise ImportInvalide(f'{path.name}, ligne {line} : {exc}') from exc
    if not rows:
        raise ImportInvalide(f'{path.name} : aucune donnée')
    return rows, warnings


def analyser(source, origine):
    """Retourner données typées et contrôle de cohérence, sans inférer les écarts."""
    source = Path(source)
    datasets, warnings, provenance = {}, [], {}
    for filename in SCHEMAS:
        path = source / filename
        try:
            data, alerts = lire_fichier(path)
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
        except OSError as exc:
            raise ImportInvalide(f'{filename} : lecture impossible') from exc
        datasets[filename] = data
        warnings.extend(alerts)
        provenance[filename] = {'lignes': len(data), 'sha256': digest}
    chart = datasets['Chart data.csv']
    table = datasets['Table data.csv']
    daily = datasets['Totals.csv']
    totals = [row for row in table if row['Geography'] == 'Total']
    if len(totals) != 1:
        raise ImportInvalide('Table data.csv : exactement une ligne Total attendue')
    details = [row for row in table if row['Geography'] != 'Total']
    chart_sum = sum(row['Engaged views'] for row in chart)
    table_sum = sum(row['Engaged views'] for row in details)
    daily_sum = sum(row['Engaged views'] for row in daily)
    total = totals[0]['Engaged views']
    if chart_sum != table_sum:
        warnings.append('Somme des détails quotidiens différente des détails par pays.')
    if daily_sum != total:
        warnings.append('Somme des totaux quotidiens différente de la ligne Total.')
    if total != table_sum:
        warnings.append('Écart entre Total et pays détaillés : cause non établie.')
    daily_map = {row['Date']: row['Engaged views'] for row in daily}
    if {row['Date'] for row in chart} != set(daily_map):
        warnings.append('Couverture des dates différente entre détails et totaux.')
    chart_groups = {}
    for row in chart:
        key = row['Geography']
        chart_groups[key] = chart_groups.get(key, 0) + row['Engaged views']
    table_groups = {row['Geography']: row['Engaged views'] for row in details}
    if chart_groups != table_groups:
        warnings.append('Détails par pays non concordants entre les deux exports.')
    for day, day_total in daily_map.items():
        observed = sum(row['Engaged views'] for row in chart if row['Date'] == day)
        if observed > day_total:
            warnings.append(f'{day} : les détails dépassent le total quotidien.')
    summary = {
        'origine': origine,
        'periode': {'debut': min(daily_map), 'fin': max(daily_map)},
        'fichiers': provenance,
        'vues_engagees': {
            'details_quotidiens': chart_sum, 'details_par_pays': table_sum,
            'total_quotidien': daily_sum, 'ligne_total': total,
            'ecart_total_details': total - table_sum,
        },
        'avertissements': warnings,
        'limites': [
            'Aucun identifiant vidéo : comparaison de contenus indisponible.',
            'Cet import ne constitue pas une exécution du système multiagents.',
            'Les zéros et valeurs absentes gardent leur sens source sans interprétation automatique.',
        ],
    }
    return {'resume': summary, 'donnees': datasets}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True, help='Dossier contenant les trois CSV')
    parser.add_argument('--origine', choices=('reelle', 'fictive'), required=True)
    args = parser.parse_args()
    try:
        result = analyser(args.source, args.origine)
    except ImportInvalide as exc:
        parser.exit(2, f'Import refusé : {exc}\n')
    print(json.dumps(result['resume'], ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
