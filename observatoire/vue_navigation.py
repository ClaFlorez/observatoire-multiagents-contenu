"""Navigation par ancres et résumé local, sans lancement ni modification de traces."""
import sqlite3
import streamlit as st
from observatoire.stockage import lire_executions_reelles


def appliquer_style():
    st.markdown('''<style>
    .stApp {background:#f2f6fc;}
    .stMainBlockContainer {max-width:1450px;padding-top:2rem;}
    .stMain h1,.stMain h2,.stMain h3 {color:#14334d;}
    [data-testid="stSidebar"] {background:#122b43;border-right:1px solid #294760;}
    [data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] label,[data-testid="stSidebar"] p {color:#edf5fc;}
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {color:#b8d0e3;}
    .observatoire-menu a {display:block;padding:.65rem .85rem;margin:.3rem 0;
      color:#e8f4ff;text-decoration:none;border-radius:8px;border-left:3px solid transparent;}
    .observatoire-menu a:hover,.observatoire-menu a:focus {background:#23465f;
      border-left-color:#41d0c3;color:white;}
    [data-testid="stMetric"] {background:#fff;border:1px solid #dce6ef;
      border-top:4px solid #118a91;border-radius:12px;padding:1rem 1.1rem;
      box-shadow:0 3px 12px #18304708;}
    [data-testid="stMetricValue"] {color:#0a7281;}
    [data-testid="stExpander"] {background:#fff;border-radius:10px;}
    [data-testid="stPlotlyChart"] {border:1px solid #dce6ef;border-radius:12px;padding:.4rem;background:white;}
    </style>''', unsafe_allow_html=True)


def afficher_navigation(videos=False):
    links = [('Tableau de bord', 'tableau-de-bord')]
    if videos:
        links += [('Qualité et provenance', 'qualite-videos'),
                  ('Classement des vidéos', 'classement-videos'),
                  ('S1 · Trois premières vidéos', 'scenario-s1'),
                  ('S2 / S4 · Groupes et cible', 'scenarios-s2-s4'),
                  ('S3 · Comparer les périodes', 'scenario-s3'),
                  ('Agents IA · Mission vidéos', 'agents-videos'),
                  ('Campagne et évaluations', 'campagne-evaluee')]
    else:
        links += [('Qualité et provenance', 'qualite-audience'),
                  ('Audience et graphiques', 'audience-graphiques'),
                  ('Simulation des rôles', 'simulation-roles'),
                  ('Essai du modèle local', 'essai-modele'),
                  ('Agents IA · Audience', 'agents-audience')]
    with st.sidebar:
        st.subheader('Navigation')
        st.markdown('<nav class="observatoire-menu" aria-label="Sections du rapport">' +
                    ''.join(f'<a href="#{anchor}" target="_self">{label}</a>'
                            for label, anchor in links) + '</nav>', unsafe_allow_html=True)
        st.caption('Accès direct aux sections du rapport chargé. Aucun appel IA.')
        st.divider()


def ancre(identifier):
    st.markdown(f'<div id="{identifier}" style="scroll-margin-top:5rem"></div>',
                unsafe_allow_html=True)


def afficher_dashboard(database, report=None):
    st.header('Tableau de bord', anchor='tableau-de-bord')
    st.caption('Vue d’ensemble locale · modèle configuré : Qwen3 4B via Ollama · orchestration : CrewAI.')
    if report is not None:
        cols = st.columns(3)
        cols[0].metric('Vidéos dans le fichier', len(report['videos']))
        cols[1].metric('Vues — ligne Total', report['total']['vues'] if report['total']['vues'] is not None else 'Indisponible')
        cols[2].metric('Visionnage — heures, ligne Total', str(report['total']['heures']) if report['total']['heures'] is not None else 'Indisponible')
    try:
        traces = lire_executions_reelles(database)
    except (sqlite3.Error, OSError, ValueError):
        st.warning('Résumé des exécutions indisponible : vérifier la base locale.')
        return
    cols = st.columns(3)
    campaign = sum(bool(t.get('campagne_id')) for t in traces)
    cols[0].metric('Exécutions IA locales enregistrées', len(traces))
    cols[1].metric('Traces liées à une campagne', campaign)
    cols[2].metric('Pilotes hors campagne', len(traces) - campaign)
    st.caption('Ces trois compteurs couvrent toute la base locale, indépendamment du CSV chargé. '
               'Ils ne mesurent ni le nombre de réussites ni les notes humaines. '
               'La campagne sélectionnée possède ses indicateurs détaillés plus bas.')
