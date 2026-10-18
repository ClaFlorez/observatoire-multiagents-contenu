"""Chargement explicite de la période précédente et comparaison locale."""

from datetime import date
import streamlit as st
import plotly.graph_objects as go

from observatoire.comparaison_periodes import comparer_periodes
from observatoire.import_videos import importer_videos
from observatoire.import_youtube import ImportInvalide
from observatoire.stockage import enregistrer_import_videos
from observatoire.vue_agents_locaux import afficher_agents_locaux
from observatoire.vue_fichiers import afficher_choix_csv


def afficher_comparaison(root, current, database):
    st.divider()
    st.subheader('Comparer deux périodes — scénario S3')
    st.caption('La comparaison Python ne lance aucun appel IA. Après chargement, un bouton distinct permet de lancer les quatre agents locaux sur ces deux instantanés.')
    with st.expander('Charger la période précédente'):
        afficher_choix_csv(root, 'comparaison_fichier', 'Choisir le CSV précédent dans data')
        st.session_state.setdefault('comparaison_fichier', str(root / 'youtube_csv' / 'aout-sept' / 'Table data.csv'))
        path = st.text_input('CSV vidéo de référence', key='comparaison_fichier')
        dates = st.date_input('Période de référence déclarée dans YouTube Studio',
                              value=(date(2026, 8, 20), date(2026, 9, 16)), key='comparaison_dates')
        confirmed = st.checkbox('Je confirme les dates de cet export de référence', key='comparaison_confirmation')
        if st.button('Comparer les deux périodes', key='comparer_periodes'):
            st.session_state.pop('comparaison_periodes', None)
            if not confirmed or len(dates) != 2:
                st.error('Confirmer les deux dates du rapport de référence.')
            else:
                try:
                    previous = importer_videos(path, dates[0].isoformat(), dates[1].isoformat(), current['origine'])
                    comparison = comparer_periodes(previous, current)
                    ids = [enregistrer_import_videos(report, database) for report in (previous, current)]
                    st.session_state['comparaison_periodes'] = {'resultat': comparison, 'imports': ids,
                        'courant': (current['fichier']['sha256'], current['periode'])}
                except (ImportInvalide, ValueError, OSError) as exc:
                    st.error(str(exc))
    saved = st.session_state.get('comparaison_periodes')
    if not saved or saved['courant'] != (current['fichier']['sha256'], current['periode']):
        return
    comparison = saved['resultat']
    st.write(f"**{comparison['jours_par_periode']} jours par période** · {comparison['nb_avant']} vidéos avant · {comparison['nb_apres']} après · **{comparison['nb_communs']} identifiants communs**.")
    st.caption(f"Avant : {comparison['periode_avant']['debut']} au {comparison['periode_avant']['fin']} ; après : {comparison['periode_apres']['debut']} au {comparison['periode_apres']['fin']}.")
    def display(value):
        return 'Indisponible' if value is None else str(round(value, 4))
    table = []
    for population, values in (('Canal — ligne Total', comparison['totaux_canal']), ('Vidéos communes — paires connues', comparison['cohorte_appariee'])):
        for metric, numbers in values.items():
            table.append({'Population': population, 'Mesure': metric,
                          **{k: display(numbers[k]) for k in ('avant', 'apres', 'ecart', 'variation_pct')},
                          'Paires connues': numbers.get('nb_paires_connues'),
                          'Paires incomplètes': numbers.get('nb_paires_incompletes')})
    st.dataframe(table, hide_index=True, width='stretch')
    metric = st.selectbox('Mesure de comparaison temporelle', ['vues', 'heures'], key='comparaison_mesure')
    chart = go.Figure()
    for label, values in (('Canal — Total', comparison['totaux_canal']), ('Cohorte appariée', comparison['cohorte_appariee'])):
        chart.add_bar(name=label, x=['Avant', 'Après'], y=[float(values[metric][k]) if values[metric][k] is not None else None for k in ('avant', 'apres')])
    chart.update_layout(title='Deux périodes : canal et vidéos communes', barmode='group', yaxis_title=metric.capitalize(), xaxis_title='Période')
    st.plotly_chart(chart, width='stretch', key='comparaison_graphique')
    st.caption('Interprétation : comparer avant/après au sein de la même population. Les heures et les vues sont affichées séparément ; les valeurs absentes ne sont pas remplacées par zéro.')
    for warning in comparison['limites']:
        st.warning(warning)
    with st.expander('Détails par identifiant commun et provenance'):
        st.dataframe([{'id': row['id'], 'titre': row['titre'], **{f'{m}_{k}': display(row[m][k]) for m in ('vues', 'heures') for k in ('avant', 'apres', 'ecart', 'variation_pct')}} for row in comparison['videos_communes']], hide_index=True, width='stretch')
        st.json({'imports': saved['imports'], 'fichiers': comparison['fichiers'],
                 'uniquement_avant': comparison['uniquement_avant'], 'uniquement_apres': comparison['uniquement_apres']})
    afficher_agents_locaux({'type': 'periodes', 'imports': saved['imports']}, database, 'periodes')
