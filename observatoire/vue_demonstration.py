"""Visualisation explicite des simulations, sans client API."""

import sqlite3

import plotly.graph_objects as go
import streamlit as st

from observatoire.demonstration import ROLES, SCENARIOS, simuler
from observatoire.stockage import enregistrer_demonstration, lire_demonstrations


def afficher_demonstration(resultat, database):
    st.subheader('Laboratoire local des quatre rôles — simulation')
    st.warning('Budget API : 0 USD. Aucun modèle IA, aucune lecture de clé et aucun appel externe. Les rôles suivent des règles Python prédéfinies. Ces démonstrations sont exclues des vingt exécutions réelles du cours.')
    scenario = st.selectbox('Mission de démonstration', SCENARIOS, key='demo_mission')
    st.caption('La mission utilise la période complète de l’import. Les filtres des graphiques d’audience ne modifient pas cette mission.')
    if st.button('Simuler les quatre rôles sans API', key='simuler_roles'):
        trace = simuler(resultat, scenario)
        try:
            enregistrer_demonstration(trace, database)
        except (sqlite3.Error, OSError):
            st.error('Sauvegarde impossible ; simulation conservée uniquement dans cette session.')
            st.session_state['demo_temporaire'] = trace
        else:
            st.session_state.pop('demo_temporaire', None)
            st.session_state['demo_derniere'] = trace['id']
    try:
        traces = lire_demonstrations(database)
    except sqlite3.Error:
        st.error('Impossible de lire les simulations locales.')
        return
    if st.session_state.get('demo_temporaire'):
        traces.insert(0, st.session_state['demo_temporaire'])
    if not traces:
        st.caption('Lancer une démonstration pour voir les messages, le graphe et les étapes.')
        return
    missions = st.multiselect('Filtre des simulations par scénario', SCENARIOS, default=list(SCENARIOS), key='demo_scenarios')
    states = st.multiselect('Filtre des simulations par état', ['terminee', 'non_validee'], default=['terminee', 'non_validee'], key='demo_etats')
    traces = [t for t in traces if t['scenario'] in missions and t['etat'] in states]
    if not traces:
        st.info('Aucune simulation ne correspond aux filtres.')
        return
    st.caption(f'{len(traces)} simulation(s) dans la sélection · 0 exécution IA réelle dans cette sélection de simulations · 0 jeton de modèle · 0 USD de frais API. Les ressources matérielles locales ne sont pas chiffrées.')
    labels = {t['id']: f"{t['debut_utc'][:19]} UTC · {t['scenario']} · {t['id'][:8]}" for t in traces}
    selected_id = st.selectbox('Simulation à relire', list(labels), format_func=labels.get, key='demo_selection')
    trace = next(t for t in traces if t['id'] == selected_id)
    st.caption(f"Données de cette simulation : {trace['origine_donnees']} · {trace['periode']['debut']} au {trace['periode']['fin']}. Elles peuvent différer de l’import actuellement chargé.")
    st.write(trace['resultat'])
    roles = st.multiselect('Filtre des étapes par rôle', ROLES, default=list(ROLES), key='demo_roles')
    # Clé par simulation pour remettre le curseur sur un domaine valide.
    index = st.slider('Relecture : étape observée', 1, len(trace['etapes']), 1, key=f"relecture_{trace['id']}")
    steps = [s for s in trace['etapes'][:index] if s['agent'] in roles]
    current = trace['etapes'][index - 1]
    st.write(f"Étape sélectionnée : **{current['agent']}** — {current['tache']}. L’exécution est terminée ; le surlignage représente une relecture.")
    if not roles:
        st.info('Sélectionner au moins un rôle pour afficher les étapes.')
        return
    messages = [m for m in trace['messages'] if m['apres_etape'] < index and m['emetteur'] in roles and m['destinataire'] in roles]
    positions = {role: i for i, role in enumerate(ROLES)}
    graph = go.Figure()
    for message in messages:
        x0, x1 = positions[message['emetteur']], positions[message['destinataire']]
        # Le retour vers le coordonnateur est dessiné en dessous des liens directs.
        y = -0.6 if x1 < x0 else 0
        graph.add_trace(go.Scatter(x=[x0, x0, x1, x1], y=[0, y, y, 0], mode='lines', showlegend=False,
                                  text=[message['resume']] * 4, hoverinfo='text'))
        graph.add_annotation(x=x1, y=0, ax=x0, ay=y, axref='x', ayref='y', arrowhead=2, text='', showarrow=True)
    graph.add_trace(go.Scatter(x=[positions[r] for r in roles], y=[0] * len(roles), mode='markers+text',
                              text=roles, textposition='top center', marker={'size': 24, 'color': ['#ef9b20' if r == current['agent'] else '#2583c5' for r in roles]}, showlegend=False))
    graph.update_layout(title='Communications prédéfinies entre les rôles', xaxis={'visible': False, 'range': [-0.5, 3.5]}, yaxis={'visible': False, 'range': [-1, 1]}, height=320)
    st.plotly_chart(graph, width='stretch', key='demo_graphe')
    st.caption('Interprétation : les flèches représentent les messages déjà transmis à cette étape de relecture ; orange désigne le rôle sélectionné. Ce graphe ne montre pas un agent IA en activité.')
    if steps:
        timeline = go.Figure(go.Bar(x=[s['duree_ms'] for s in steps], base=[s['debut_ms'] for s in steps], y=[f"{s['ordre']} · {s['agent']}" for s in steps], orientation='h'))
        timeline.update_layout(title='Chronologie des fonctions Python locales', xaxis_title='Millisecondes depuis le lancement', yaxis_title='Étape et rôle')
        st.plotly_chart(timeline, width='stretch', key='demo_timeline')
        st.caption('Interprétation : durées réellement mesurées des fonctions locales, sans attente réseau ni génération IA. Elles ne prédisent pas la latence de futurs modèles.')
    if messages:
        # Distinguer les deux interventions du coordonnateur pour un flux sans cycle.
        labels_etapes = [f"{s['ordre']} · {s['agent']}" for s in trace['etapes']]
        sankey = go.Figure(go.Sankey(node={'label': labels_etapes}, link={'source': [m['ordre'] - 1 for m in messages], 'target': [m['ordre'] for m in messages], 'value': [1] * len(messages)}))
        sankey.update_layout(title='Circulation des messages de démonstration — unité : message')
        st.plotly_chart(sankey, width='stretch', key='demo_sankey')
        st.caption(f'Interprétation : {len(messages)} message(s) prédéfini(s) visibles avec les filtres et l’étape actuels. Leur volume ne mesure pas une qualité de coopération IA.')
    with st.expander('Événements et résultats de la relecture'):
        st.json({'mode': trace['mode'], 'etapes': steps, 'messages': messages})
