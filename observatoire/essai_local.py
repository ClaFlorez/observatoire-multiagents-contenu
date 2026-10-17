"""Premier appel réel à un modèle CPU local, sans clé et sans données privées."""

import json
from datetime import datetime, timezone
from urllib.error import URLError
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener


class SansRedirection(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError('Redirection interdite pour un essai local')


def essai_local():
    payload = {
        'model': 'qwen3:4b', 'stream': False, 'think': False, 'format': 'json',
        'prompt': (
            'Réponds uniquement par un objet JSON avec les clés pays et justification. '
            'Données entièrement fictives : CA = 30 vues engagées, FR = 5. '
            'Quel pays possède le volume le plus élevé ? '
            'La justification doit être une phrase courte en français, sans inventer de données.'
        ),
        'options': {'num_gpu': 0, 'num_ctx': 4096, 'num_predict': 128, 'temperature': 0},
        'keep_alive': '5m',
    }
    request = Request('http://127.0.0.1:11434/api/generate',
                      data=json.dumps(payload, ensure_ascii=False).encode('utf-8'),
                      headers={'Content-Type': 'application/json'}, method='POST')
    opener = build_opener(ProxyHandler({}), SansRedirection())
    with opener.open(request, timeout=180) as response:
        answer = json.load(response)
    text = answer.get('response', '')
    parsed = json.loads(text)
    if not answer.get('done') or not isinstance(parsed, dict):
        raise ValueError('Réponse locale incomplète ou non structurée')
    return {
        'type': 'essai_inference_locale', 'modele': answer.get('model'),
        'date_utc': datetime.now(timezone.utc).isoformat(),
        'donnees': 'fictives', 'resultat': parsed,
        'controle_pays': parsed.get('pays') == 'CA',
        'jetons_entree': answer.get('prompt_eval_count'),
        'jetons_sortie': answer.get('eval_count'),
        'duree_totale_s': answer.get('total_duration', 0) / 1e9,
        'chargement_s': answer.get('load_duration', 0) / 1e9,
        'generation_s': answer.get('eval_duration', 0) / 1e9,
        'cout_api_usd': 0, 'eligible_campagne_multiagents': False,
    }


def main():
    try:
        report = essai_local()
    except (URLError, TimeoutError, ValueError) as exc:
        raise SystemExit(f'Essai local non validé : {type(exc).__name__}. Vérifier le serveur et le modèle.') from None
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not report['controle_pays']:
        raise SystemExit(2)


if __name__ == '__main__':
    main()
