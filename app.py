"""Première interface locale : imports et audience, sans appel IA."""

import sqlite3
from datetime import date
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

from observatoire.import_youtube import ImportInvalide, analyser
from observatoire.stockage import charger_import, enregistrer_import, lister_imports
from observatoire.vue_demonstration import afficher_demonstration
from observatoire.vue_essai_local import afficher_essai_local
from observatoire.vue_agents_locaux import afficher_agents_locaux
from observatoire.vue_videos import afficher_videos


ROOT = Path(__file__).resolve().parent
DATABASE = ROOT / 'data' / 'private' / 'observatoire.sqlite'
st.set_page_config(page_title='Observatoire de contenu', layout='wide')
st.title('Observatoire multiagents de contenu numérique')
st.caption('Prototype local — import et audience YouTube')
st.info('L’audience et la simulation fonctionnent sans modèle. Les essais IA et les quatre agents CrewAI locaux se lancent séparément en bas de page. Aucun service IA payant n’est appelé.')

with st.sidebar:
    export_type = st.selectbox('Type de rapport', ['Audience par pays', 'Contenu par vidéo'], key='type_rapport')
if export_type == 'Contenu par vidéo':
    afficher_videos(ROOT, DATABASE)
    st.stop()

with st.sidebar:
    st.header('Source des données')
    source = st.text_input('Dossier contenant les trois CSV', str(ROOT / 'data' / 'examples'))
    origin = st.selectbox('Provenance déclarée', ['fictive', 'reelle'])
    st.caption('Déclarer explicitement si les données sont réelles ou fictives. Les fichiers restent sur cet ordinateur.')
    if st.button('Charger et vérifier', type='primary', key='charger_csv'):
        try:
            result = analyser(source, origin)
        except ImportInvalide as exc:
            st.session_state.pop('resultat', None)
            st.error(str(exc))
        else:
            st.session_state['resultat'] = result
    st.divider()
    st.subheader('Imports sauvegardés')
    try:
        imports = lister_imports(DATABASE)
    except sqlite3.Error:
        imports = []
        st.error('Impossible de lire la base locale.')
    if imports:
        labels = {row[0]: f'{row[1][:19]} UTC · {row[2]} · {row[0][:8]}' for row in imports}
        chosen = st.selectbox('Import local', list(labels), format_func=labels.get)
        if st.button('Ouvrir cet import', key='ouvrir_import'):
            try:
                st.session_state['resultat'] = charger_import(DATABASE, chosen)
            except (sqlite3.Error, KeyError, ValueError):
                st.error('Impossible de restaurer cet import.')
    else:
        st.caption('Aucun import sauvegardé.')

if 'resultat' not in st.session_state:
    st.write('Commencer par charger les fichiers fictifs fournis ou le dossier local de vos exports YouTube Studio.')
    st.stop()

result = st.session_state['resultat']
summary = result['resume']
datasets = result['donnees']
st.subheader('Qualité et provenance')
st.write(f"Origine : **{summary['origine']}** · période totale : **{summary['periode']['debut']} au {summary['periode']['fin']}**")
if summary['origine'] == 'fictive':
    st.warning('Données entièrement fictives : démonstration du logiciel uniquement.')
for warning in summary['avertissements']:
    st.warning(warning)
if st.button('Sauvegarder cet import dans SQLite', key='sauvegarder_import'):
    try:
        identifier, inserted = enregistrer_import(result, DATABASE)
    except (sqlite3.Error, OSError):
        st.error('Impossible de sauvegarder dans la base locale.')
    else:
        st.success(('Import sauvegardé : ' if inserted else 'Import déjà présent : ') + identifier[:12])
        st.caption('La liste des imports sera actualisée à la prochaine interaction.')

with st.expander('Provenance des fichiers et limites'):
    st.json(summary['fichiers'])
    for limit in summary['limites']:
        st.write('• ' + limit)

st.subheader('Audience et évolution')
chart = datasets['Chart data.csv']
daily = datasets['Totals.csv']
table = datasets['Table data.csv']
countries = sorted({row['Geography'] for row in chart})
left, right = st.columns(2)
selected = left.multiselect('Pays détaillés', countries, default=countries)
start = date.fromisoformat(summary['periode']['debut'])
end = date.fromisoformat(summary['periode']['fin'])
period = right.date_input('Période des séries quotidiennes', value=(start, end), min_value=start, max_value=end)
if len(period) != 2:
    st.info('Sélectionner une date de début et une date de fin.')
    st.stop()
begin, finish = (item.isoformat() for item in period)
filtered = [row for row in chart if row['Geography'] in selected and begin <= row['Date'] <= finish]
daily_filtered = [row for row in daily if begin <= row['Date'] <= finish]
metrics = st.columns(3)
global_total = sum(row['Engaged views'] for row in daily_filtered)
selected_total = sum(row['Engaged views'] for row in filtered)
metrics[0].metric('Total quotidien, tous pays', f'{global_total:,}'.replace(',', ' '))
metrics[1].metric('Détails des pays sélectionnés', f'{selected_total:,}'.replace(',', ' '))
metrics[2].metric('Écart total − sélection', f'{global_total - selected_total:,}'.replace(',', ' '))
st.caption('Unité : vues engagées. Le total tous pays ne change pas avec le filtre pays. L’écart inclut les pays désélectionnés et la part non détaillée ; il ne mesure pas une erreur à lui seul.')
if not filtered:
    st.info('Aucune ligne ne correspond aux filtres. Les données complètes restent disponibles dans la provenance.')
else:
    figure = go.Figure()
    figure.add_trace(go.Scatter(x=[r['Date'] for r in daily_filtered], y=[r['Engaged views'] for r in daily_filtered], name='Total tous pays', mode='lines+markers'))
    for country in selected:
        rows = sorted((r for r in filtered if r['Geography'] == country), key=lambda r: r['Date'])
        figure.add_trace(go.Scatter(x=[r['Date'] for r in rows], y=[r['Engaged views'] for r in rows], name=country, mode='lines+markers'))
    figure.update_layout(title='Évolution quotidienne des vues engagées', xaxis_title='Date statistique', yaxis_title='Vues engagées', legend_title='Couverture')
    st.plotly_chart(figure, width='stretch')
    st.write(f'Interprétation : les pays sélectionnés représentent {selected_total:,} vues engagées sur la période choisie. Les variations ne permettent pas, seules, d’expliquer leurs causes.')
    amounts = {country: sum(r['Engaged views'] for r in filtered if r['Geography'] == country) for country in selected}
    ordered = sorted(amounts, key=amounts.get, reverse=True)
    bars = go.Figure(go.Bar(x=ordered, y=[amounts[c] for c in ordered]))
    bars.update_layout(title='Vues engagées par pays détaillé', xaxis_title='Code pays', yaxis_title='Vues engagées')
    st.plotly_chart(bars, width='stretch')
    st.write(f'Interprétation : {ordered[0]} possède le total le plus élevé dans la sélection ({amounts[ordered[0]]:,}). Ce classement porte sur le volume, sans mesurer la qualité des contenus.')

with st.expander('Statistiques agrégées par pays — période complète de l’export'):
    st.caption('Ces valeurs ne sont pas recalculées pour la période quotidienne filtrée. Les durées moyennes sont affichées en secondes. Les cellules absentes restent vides.')
    st.dataframe([
        {key: (str(value) if value is not None else None) for key, value in row.items()}
        for row in table if row['Geography'] in selected
    ], width='stretch')

st.divider()
afficher_demonstration(result, DATABASE)
st.caption('Les visualisations de simulation et d’audience ne remplacent pas la campagne réelle exigée. Les premiers agents locaux sont disponibles dans une section distincte ci-dessous.')
afficher_essai_local()
afficher_agents_locaux(result, DATABASE)
