"""Accès manuel au premier essai d’inférence locale depuis Streamlit."""

from urllib.error import URLError
from concurrent.futures import ThreadPoolExecutor, TimeoutError as AttenteResultat
from time import monotonic

import streamlit as st

from observatoire.essai_local import essai_local


def afficher_essai_local():
    with st.expander('Premier essai IA réel sur ce poste — sans API payante'):
        st.write('Cet essai appelle Qwen3 4B sur le serveur local Ollama, en mode CPU. Il utilise uniquement deux nombres fictifs et ne lit pas votre clé OpenAI.')
        st.caption('Il vérifie une inférence et une réponse JSON ; il ne lance pas les quatre agents CrewAI et ne compte pas dans la campagne multiagents. Le premier chargement peut prendre du temps.')
        if st.button('Tester le modèle local avec des données fictives', key='tester_modele_local'):
            st.session_state.pop('rapport_essai_local', None)
            suivi = st.empty()
            debut = monotonic()
            try:
                with st.spinner('Génération sur le processeur local…'):
                    with ThreadPoolExecutor(max_workers=1) as executor:
                        future = executor.submit(essai_local)
                        while True:
                            suivi.info(
                                'Qwen3 4B · Comparaison de données fictives : CA = 30 vues, FR = 5. '
                                'La demande est transmise à Ollama ; attente de la réponse JSON du modèle local '
                                '(chargement éventuel et génération sur CPU). '
                                f'Temps écoulé : {monotonic() - debut:.0f} s. '
                                'Jetons disponibles à la réception de la réponse. Aucun agent CrewAI lancé.'
                            )
                            try:
                                report = future.result(timeout=1)
                                break
                            except AttenteResultat:
                                if future.done():
                                    raise
            except (URLError, TimeoutError, ValueError):
                st.error('Essai non validé. Vérifier que le serveur Ollama est démarré et que qwen3:4b est téléchargé. Aucune API externe de remplacement ne sera utilisée.')
            else:
                suivi.success('Réponse JSON reçue et contrôlée : comparaison du pays retourné avec le pays attendu CA. '
                              f"Jetons d’entrée : {report.get('jetons_entree')} · Jetons de sortie : {report.get('jetons_sortie')}.")
                st.session_state['rapport_essai_local'] = report
            finally:
                if 'rapport_essai_local' not in st.session_state:
                    suivi.empty()
        report = st.session_state.get('rapport_essai_local')
        if report:
            if report['controle_pays']:
                st.success('Réponse structurée reçue ; le pays attendu CA a été identifié.')
            else:
                st.warning('Réponse reçue mais le contrôle du pays attendu a échoué.')
            st.json(report)
