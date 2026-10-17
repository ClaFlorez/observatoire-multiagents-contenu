"""Accès manuel au premier essai d’inférence locale depuis Streamlit."""

from urllib.error import URLError

import streamlit as st

from observatoire.essai_local import essai_local


def afficher_essai_local():
    with st.expander('Premier essai IA réel sur ce poste — sans API payante'):
        st.write('Cet essai appelle Qwen3 4B sur le serveur local Ollama, en mode CPU. Il utilise uniquement deux nombres fictifs et ne lit pas votre clé OpenAI.')
        st.caption('Il vérifie une inférence et une réponse JSON ; il ne lance pas les quatre agents CrewAI et ne compte pas dans la campagne multiagents. Le premier chargement peut prendre du temps.')
        if st.button('Tester le modèle local avec des données fictives', key='tester_modele_local'):
            st.session_state.pop('rapport_essai_local', None)
            try:
                with st.spinner('Génération sur le processeur local…'):
                    report = essai_local()
            except (URLError, TimeoutError, ValueError):
                st.error('Essai non validé. Vérifier que le serveur Ollama est démarré et que qwen3:4b est téléchargé. Aucune API externe de remplacement ne sera utilisée.')
            else:
                st.session_state['rapport_essai_local'] = report
        report = st.session_state.get('rapport_essai_local')
        if report:
            if report['controle_pays']:
                st.success('Réponse structurée reçue ; le pays attendu CA a été identifié.')
            else:
                st.warning('Réponse reçue mais le contrôle du pays attendu a échoué.')
            st.json(report)
