"""Deux configurations du même modèle local, paramètres explicitement tracés."""
CONFIGURATIONS = {
    'T0': {'modele': 'qwen3:4b', 'temperature': 0.0},
    'T04': {'modele': 'qwen3:4b', 'temperature': 0.4},
}


def runtime_local():
    import json
    from urllib.request import build_opener, ProxyHandler
    from observatoire.essai_local import SansRedirection
    opener = build_opener(ProxyHandler({}), SansRedirection())
    with opener.open('http://127.0.0.1:11434/api/tags', timeout=5) as response:
        models = json.load(response)['models']
    with opener.open('http://127.0.0.1:11434/api/version', timeout=5) as response:
        version = json.load(response)['version']
    selected = next((m for m in models if m.get('name') == 'qwen3:4b'), None)
    if selected is None or not selected.get('digest'):
        raise ValueError('Le modèle local Qwen3 4B doit être disponible avant le gel du plan.')
    return {'ollama_version': version, 'modele': selected['name'], 'modele_digest': selected['digest']}


def configuration(identifier, repetition=1):
    if identifier not in CONFIGURATIONS or repetition not in (1, 2):
        raise ValueError('Configuration ou répétition non autorisée.')
    return {**CONFIGURATIONS[identifier], 'id': identifier, 'seed': 4100 + repetition,
            'num_ctx': 4096, 'num_gpu': 0, 'think': False, 'num_predict': 512, 'max_appels': 12}
