"""Garde-fous du processus CrewAI local ; ne pas installer dans Streamlit."""

import os
import socket
import sys
from pathlib import Path


def verifier_evenement(event, args):
    if event == 'socket.connect':
        address = args[1]
        caller = sys._getframe(1)
        # asyncio Windows crée un canal interne avec socket.socketpair().
        internal_pipe = (caller.f_code.co_name == '_fallback_socketpair'
                         and caller.f_code.co_filename == socket.__file__)
        if not isinstance(address, tuple) or address[0] != '127.0.0.1' or (address[1] != 11434 and not internal_pipe):
            raise PermissionError('Connexion externe interdite dans le processus local')
    elif event == 'socket.getaddrinfo':
        if args[0] not in ('127.0.0.1', b'127.0.0.1'):
            raise PermissionError('Résolution externe interdite dans le processus local')
    elif event == 'open' and isinstance(args[0], (str, bytes, os.PathLike)):
        name = os.fsdecode(args[0])
        if Path(name).name.lower() in ('.env', '.env.local', 'secrets.toml'):
            raise PermissionError('Lecture de secrets interdite dans le processus local')


def environnement_local(root):
    env = {key: value for key, value in os.environ.items()
           if not key.endswith('_API_KEY') and key not in ('OPENAI_TOKEN', 'ANTHROPIC_AUTH_TOKEN')}
    env.update({
        'PYTHON_DOTENV_DISABLED': '1', 'OTEL_SDK_DISABLED': 'true',
        'CREWAI_DISABLE_TELEMETRY': 'true', 'CREWAI_TRACING_ENABLED': 'false',
        'ANONYMIZED_TELEMETRY': 'False', 'HF_HUB_OFFLINE': '1',
        'CREWAI_STORAGE_DIR': str(Path(root) / '.local' / 'crewai'),
        # Redirection limitée au worker : CrewAI y crée son magasin technique.
        'LOCALAPPDATA': str(Path(root) / '.local' / 'crewai' / 'appdata'),
        'OLLAMA_NO_CLOUD': '1', 'PYTHONUTF8': '1',
    })
    return env


def installer_garde_fous(root):
    env = environnement_local(root)
    os.environ.clear()
    os.environ.update(env)
    # Certains réglages Pydantic lisent directement .env, même lorsque
    # python-dotenv est désactivé. Un répertoire vide évite cette recherche.
    workspace = Path(root) / '.local' / 'crewai' / 'travail'
    workspace.mkdir(parents=True, exist_ok=True)
    os.chdir(workspace)
    sys.addaudithook(verifier_evenement)
