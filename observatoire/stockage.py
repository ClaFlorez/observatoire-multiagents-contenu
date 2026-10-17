"""Sauvegarde locale des imports, distincte des futures traces multiagents."""

import hashlib
import json
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path


def _encode(value):
    if isinstance(value, Decimal):
        return str(value)
    raise TypeError(f'Type non sérialisable : {type(value).__name__}')


def enregistrer_import(resultat, destination):
    """Insérer une seule fois le même contenu pour une origine donnée."""
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    resume = resultat['resume']
    signature = {
        'origine': resume['origine'],
        'fichiers': {name: item['sha256'] for name, item in resume['fichiers'].items()},
    }
    identifiant = hashlib.sha256(json.dumps(signature, sort_keys=True).encode()).hexdigest()
    payload = json.dumps(resultat, ensure_ascii=False, default=_encode)
    with closing(sqlite3.connect(destination)) as connection, connection:
        connection.execute('''CREATE TABLE IF NOT EXISTS imports (
            id TEXT PRIMARY KEY,
            cree_utc TEXT NOT NULL,
            origine TEXT NOT NULL,
            contenu_json TEXT NOT NULL
        )''')
        cursor = connection.execute(
            'INSERT OR IGNORE INTO imports VALUES (?, ?, ?, ?)',
            (identifiant, datetime.now(timezone.utc).isoformat(), resume['origine'], payload),
        )
        inserted = cursor.rowcount == 1
    return identifiant, inserted


def lister_imports(destination):
    if not Path(destination).exists():
        return []
    with closing(sqlite3.connect(destination)) as connection:
        return connection.execute(
            'SELECT id, cree_utc, origine FROM imports ORDER BY cree_utc DESC, id'
        ).fetchall()


def charger_import(destination, identifiant):
    with closing(sqlite3.connect(destination)) as connection:
        row = connection.execute(
            'SELECT contenu_json FROM imports WHERE id = ?', (identifiant,)
        ).fetchone()
    if row is None:
        raise KeyError('Import introuvable')
    # Les décimaux stockés en texte conservent la précision source.
    result = json.loads(row[0])
    from observatoire.import_youtube import DECIMALS
    for rows in result['donnees'].values():
        for item in rows:
            for column in DECIMALS & item.keys():
                if item[column] is not None:
                    item[column] = Decimal(item[column])
    return result


def enregistrer_demonstration(trace, destination):
    """Conserver uniquement des démonstrations, dans une table distincte."""
    if trace.get('mode') != 'simulation' or trace.get('eligible_campagne_reelle') is not False:
        raise ValueError('Cette table accepte uniquement des simulations identifiées.')
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(destination)) as connection, connection:
        connection.execute('''CREATE TABLE IF NOT EXISTS demonstrations (
            id TEXT PRIMARY KEY, contenu_json TEXT NOT NULL
        )''')
        connection.execute('INSERT OR IGNORE INTO demonstrations VALUES (?, ?)',
                           (trace['id'], json.dumps(trace, ensure_ascii=False, default=_encode)))


def lire_demonstrations(destination):
    if not Path(destination).exists():
        return []
    with closing(sqlite3.connect(destination)) as connection:
        if not connection.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='demonstrations'").fetchone():
            return []
        return [json.loads(row[0]) for row in connection.execute('SELECT contenu_json FROM demonstrations ORDER BY rowid DESC')]


def enregistrer_execution_reelle(trace, destination):
    if trace.get('mode') != 'ia_locale' or trace.get('orchestrateur') != 'CrewAI':
        raise ValueError('Une trace CrewAI locale réelle est requise')
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(destination, timeout=20)) as connection, connection:
        connection.execute('''CREATE TABLE IF NOT EXISTS executions_reelles (
            id TEXT PRIMARY KEY, contenu_json TEXT NOT NULL
        )''')
        connection.execute('''INSERT INTO executions_reelles VALUES (?, ?)
            ON CONFLICT(id) DO UPDATE SET contenu_json=excluded.contenu_json''',
                           (trace['id'], json.dumps(trace, ensure_ascii=False, default=_encode)))


def lire_executions_reelles(destination):
    if not Path(destination).exists():
        return []
    with closing(sqlite3.connect(destination, timeout=20)) as connection:
        if not connection.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='executions_reelles'").fetchone():
            return []
        return [json.loads(row[0]) for row in connection.execute('SELECT contenu_json FROM executions_reelles ORDER BY rowid DESC')]


def enregistrer_import_videos(resultat, destination):
    if resultat.get('type') != 'videos':
        raise ValueError('Import par vidéo attendu')
    signature = {'type': 'videos', 'origine': resultat['origine'],
                 'periode': resultat['periode'], 'sha256': resultat['fichier']['sha256']}
    identifier = hashlib.sha256(json.dumps(signature, sort_keys=True).encode()).hexdigest()
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(destination)) as connection, connection:
        connection.execute('CREATE TABLE IF NOT EXISTS imports_videos (id TEXT PRIMARY KEY, contenu_json TEXT NOT NULL)')
        connection.execute('INSERT OR IGNORE INTO imports_videos VALUES (?, ?)',
                           (identifier, json.dumps(resultat, ensure_ascii=False, default=_encode)))
    return identifier


def charger_import_videos(destination, identifiant):
    with closing(sqlite3.connect(destination)) as connection:
        row = connection.execute('SELECT contenu_json FROM imports_videos WHERE id=?', (identifiant,)).fetchone()
    if row is None:
        raise KeyError('Import vidéo introuvable')
    data = json.loads(row[0])
    for video in [data['total'], *data['videos']]:
        for key in ('heures', 'ctr_pct'):
            if video[key] is not None:
                video[key] = Decimal(video[key])
    for item in data['rapprochements']:
        for key in ('total_source', 'somme_connue', 'ecart_total_details'):
            if item[key] is not None:
                item[key] = Decimal(str(item[key]))
    return data
