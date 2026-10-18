"""Vue locale des statistiques par contenu, sans appel IA automatique."""

from datetime import date

import plotly.graph_objects as go
import streamlit as st

from observatoire.import_youtube import ImportInvalide
from observatoire.import_videos import importer_videos
from observatoire.vue_agents_locaux import afficher_agents_locaux
from observatoire.vue_comparaison import afficher_comparaison
from observatoire.vue_scenarios import afficher_preparation
from observatoire.vue_s1 import afficher_s1
from observatoire.vue_campagne import afficher_campagne
from observatoire.vue_navigation import afficher_dashboard, ancre
from observatoire.vue_fichiers import afficher_choix_csv


def afficher_videos(root, database=None):
    st.subheader('Statistiques par vidéo')
    st.info('Cette vue importe uniquement la table par vidéo. Les quatre agents locaux peuvent comparer ses vues et ses heures dans une mission dédiée en bas de page. Les rapports par pays et playlists restent séparés.')
    with st.sidebar:
        default_path = root / 'youtube_csv' / 'setp-oct' / 'Table data.csv'
        if not default_path.exists():
            default_path = root / 'youtube_csv' / 'Table data.csv'
        afficher_choix_csv(root, 'video_fichier')
        st.session_state.setdefault('video_fichier', str(default_path))
        path = st.text_input('Fichier CSV par vidéo', key='video_fichier')
        origin = st.selectbox('Origine du fichier vidéo', ['reelle', 'fictive'], key='video_origine')
        period = st.date_input('Période statistique confirmée dans YouTube Studio',
                               value=(date(2026, 9, 17), date(2026, 10, 14)), key='video_periode')
        confirmed = st.checkbox('Je confirme la période de cet export', key='video_confirmation')
        if st.button('Charger le rapport par vidéo', key='charger_videos', type='primary'):
            st.session_state.pop('import_videos', None)
            if not confirmed or len(period) != 2:
                st.error('Confirmer les deux dates de la période statistique.')
            else:
                try:
                    st.session_state['import_videos'] = importer_videos(path, period[0].isoformat(), period[1].isoformat(), origin)
                except ImportInvalide as exc:
                    st.error(str(exc))
    report = st.session_state.get('import_videos')
    if report is None:
        afficher_dashboard(database or root / 'data' / 'private' / 'observatoire.sqlite')
        st.write('Vérifier le chemin et le même intervalle que dans YouTube Studio, confirmer puis charger la table. Les fichiers Chart data et Totals ne sont pas nécessaires à cette vue.')
        return
    st.write(f"Origine : **{report['origine']}** · période déclarée : **{report['periode']['debut']} au {report['periode']['fin']}**")
    if report['origine'] == 'fictive':
        st.warning('Données fictives : développement uniquement.')
    destination = database or root / 'data' / 'private' / 'observatoire.sqlite'
    afficher_dashboard(destination, report)
    ancre('qualite-videos')
    with st.expander('Qualité et provenance', expanded=True):
        for warning in report['avertissements']:
            st.warning(warning)
        st.dataframe([{k: str(v) if v is not None else 'Indisponible' for k, v in item.items()}
                      for item in report['rapprochements']], width='stretch', hide_index=True)
        st.caption('Les indicateurs de la ligne Total ne sont pas recalculés par les filtres ci-dessous. Une somme connue peut être égale au total tout en contenant des cellules absentes.')
        st.json(report['fichier'])
    st.subheader('Classement des vidéos', anchor='classement-videos')
    query = st.text_input('Filtrer les vidéos par titre ou identifiant', key='video_recherche').strip().casefold()
    metrics = {'Vues': ('vues', 'vues'), 'Temps de visionnage': ('heures', 'heures'), 'Impressions de miniature': ('impressions', 'impressions')}
    selected_metric = st.selectbox('Indicateur de classement', list(metrics), key='video_mesure')
    limit = st.selectbox('Nombre maximal de vidéos affichées', [5, 10, 20], index=1, key='video_limite')
    filtered = [v for v in report['videos'] if query in (v['titre'] or '').casefold() or query in v['id'].casefold()]
    column, unit = metrics[selected_metric]
    known = sorted((v for v in filtered if v[column] is not None), key=lambda v: v[column], reverse=True)[:limit]
    if known:
        chart = go.Figure(go.Bar(x=[float(v[column]) for v in reversed(known)],
                                 y=[v['id'] for v in reversed(known)], orientation='h',
                                 customdata=[[v['titre'] or 'Titre indisponible'] for v in reversed(known)],
                                 hovertemplate='%{customdata[0]}<br>%{y} : %{x}<extra></extra>'))
        chart.update_layout(title=f'Classement des vidéos — {selected_metric.lower()}', xaxis_title=unit.capitalize(),
                            yaxis_title='Identifiant vidéo', height=max(360, len(known) * 30))
        st.plotly_chart(chart, width='stretch', key='classement_videos')
        st.caption(f"Interprétation : {known[0]['id']} présente la valeur connue la plus élevée dans la sélection ({known[0][column]} {unit}). Il s’agit d’une comparaison descriptive sur la période déclarée, sans explication causale.")
    else:
        st.info('Aucune valeur connue pour les vidéos et l’indicateur sélectionnés.')
    st.caption(f'{len(filtered)} vidéo(s) correspondent à la recherche. Les cellules absentes restent indisponibles. Les durées sont en secondes ; les heures et les taux de clics conservent leur unité.')
    st.dataframe([{key: (str(value) if value is not None else None) for key, value in video.items()} for video in filtered], width='stretch', hide_index=True)
    destination = database or root / 'data' / 'private' / 'observatoire.sqlite'
    ancre('scenario-s1')
    afficher_s1(report, destination)
    ancre('scenarios-s2-s4')
    afficher_preparation(report, root, destination)
    ancre('scenario-s3')
    afficher_comparaison(root, report, destination)
    ancre('agents-videos')
    afficher_agents_locaux(report, destination, 'videos')
    ancre('campagne-evaluee')
    afficher_campagne(root, report, destination)
