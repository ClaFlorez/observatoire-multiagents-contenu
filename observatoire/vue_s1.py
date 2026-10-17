"""Classements S1 et lancement explicite des agents."""
import streamlit as st
import plotly.graph_objects as go
from observatoire.agents_s1 import calculer_s1
from observatoire.vue_agents_locaux import afficher_agents_locaux


def mission_s1(report):
    return {**report, 'type': 'S1', 'scenario_groupe': 'S1',
            'parametres_scenario': {'nombre': 3, 'mesures': ['vues', 'heures'],
                                    'population': 'import_complet', 'ex_aequo': 'ordre_source'}}


def afficher_s1(report, database):
    st.divider()
    st.subheader('S1 — trois premières vidéos par vues et par heures')
    st.caption('Calcul Python sans appel IA automatique. L’import complet est utilisé ; les filtres précédents ne changent pas cette mission.')
    result = calculer_s1(report)
    titles = {v['id']: v['titre'] for v in report['videos']}
    for metric, unit in (('vues', 'Vues'), ('heures', 'Heures de visionnage')):
        table = [{'rang': rank, 'id': result[f'{metric}_{rank}_id'],
                  'titre': titles[result[f'{metric}_{rank}_id']], 'valeur': str(result[f'{metric}_{rank}_valeur']), 'unite': unit}
                 for rank in range(1, 4) if result[f'{metric}_{rank}_id'] is not None]
        st.write('**Trois premières — ' + unit.lower() + '**')
        if table:
            st.dataframe(table, hide_index=True, width='stretch')
            figure = go.Figure(go.Bar(x=[float(row['valeur']) for row in reversed(table)],
                                      y=[row['id'] for row in reversed(table)], orientation='h'))
            figure.update_layout(xaxis_title=unit, yaxis_title='Identifiant vidéo', height=280)
            st.plotly_chart(figure, width='stretch', key='s1_classement_' + metric)
        else:
            st.info('Classement indisponible : aucune valeur connue.')
        st.caption(f"{result[metric + '_absentes']} valeur(s) absente(s) ; {result[metric + '_classees']} vidéo(s) classée(s). Ex æquo départagés par l’ordre source, sans supériorité entre valeurs égales. Aucune cause établie.")
    afficher_agents_locaux(mission_s1(report), database, 'S1')
