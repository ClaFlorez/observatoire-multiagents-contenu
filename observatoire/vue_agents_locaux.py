"""Interface des premières exécutions CrewAI réelles, séparées du laboratoire."""

import sqlite3
import json

import plotly.graph_objects as go
import streamlit as st

from observatoire.lancement_local import lancer_agents
from observatoire.stockage import lire_executions_reelles
from observatoire.analyse_videos import verifier_synthese_videos
from observatoire.agents_periodes import verifier_synthese_periodes
from observatoire.agents_groupes import verifier_synthese_groupes, signature


def afficher_agents_locaux(resultat, database, type_rapport='geographie'):
    video_mode = type_rapport == 'videos'
    period_mode = type_rapport == 'periodes'
    group_mode = type_rapport in ('S1', 'S2', 'S4')
    suffix = '_' + type_rapport if video_mode or period_mode or group_mode else ''
    st.divider()
    st.subheader('Quatre agents CrewAI locaux — exécution IA réelle' + (' — ' + type_rapport if group_mode else ' — S3 périodes' if period_mode else ' — vidéos' if video_mode else ''))
    st.info('Cette mission utilise réellement Qwen3 4B sur votre CPU : coordonnateur, chercheur, analyste et vérificateur. Aucun fournisseur externe et aucune clé OpenAI. Il s’agit d’un pilote d’intégration ; la campagne évaluée reste à préparer.')
    if type_rapport == 'S1':
        st.caption('Mission S1 : deux classements des trois premières vidéos, par vues et par heures. Calcul et vérification indépendante des rangs, valeurs et absences. Ex æquo dans l’ordre du CSV. Synthèse factuelle préparée en Python ; aucun lien causal. Plafond : dix minutes et douze appels locaux.')
    elif group_mode:
        st.caption('Mission ' + type_rapport + ' : lire les paramètres figés, calculer les valeurs connues et les contrôler indépendamment. La synthèse reprend une formulation préparée en Python, sans validation automatique de la comparabilité. Plafond : dix minutes et douze appels locaux.')
        st.json(resultat['parametres_scenario'], expanded=False)
    elif period_mode:
        st.caption('Mission S3 : comparer les deux instantanés, recalculer indépendamment les totaux et paires connues, puis sélectionner une synthèse parmi des formulations factuelles préparées en Python. Aucun texte causal libre. Prévoir plusieurs minutes ; plafond de dix minutes et douze appels locaux.')
    elif video_mode:
        st.caption('Mission : comparer les vidéos par vues et heures, contrôler les valeurs connues et proposer une hypothèse éditoriale à tester. L’import complet est utilisé, indépendamment des filtres du classement. Prévoir plusieurs minutes ; plafond de dix minutes et douze appels locaux.')
    else:
        st.caption('Mission : identifier le pays en tête en vues engagées, contrôler les totaux et formuler les limites. L’import complet est utilisé, indépendamment des filtres d’audience. Prévoir plusieurs minutes ; plafond de dix minutes et douze appels locaux.')
    if st.button('Lancer les quatre agents IA locaux — 0 USD API', key='lancer_agents_locaux' + suffix):
        try:
            with st.spinner('Les agents travaillent sur le processeur local. Ne pas fermer cette session…'):
                trace = lancer_agents(resultat, database)
        except (RuntimeError, ValueError, OSError, sqlite3.Error) as exc:
            st.error(f'Lancement non terminé ({type(exc).__name__}). Vérifier le moteur local et les dépendances. Aucun repli vers une API payante.')
        else:
            st.session_state['derniere_execution_ia' + suffix] = trace['id']
            if trace['etat'] == 'terminee':
                st.success('Les cinq tâches ont été exécutées et les contrôles minimaux d’intégration ont réussi.')
            else:
                st.warning('Exécution conservée, mais non validée. Consulter les étapes et les diagnostics ci-dessous.')
    try:
        traces = lire_executions_reelles(database)
        traces = [t for t in traces if t.get('type_rapport', 'geographie') == type_rapport and not t.get('campagne_id')]
        if period_mode:
            traces = [t for t in traces if t.get('imports') == resultat['imports']]
        if group_mode:
            traces = [t for t in traces if t.get('import_id') == signature(resultat)]
    except sqlite3.Error:
        st.error('Impossible de lire les traces IA locales.')
        return
    if not traces:
        st.caption('Aucune exécution CrewAI enregistrée. Les simulations restent dans une autre table.')
        return
    ids = [t['id'] for t in traces]
    latest = st.session_state.get('derniere_execution_ia' + suffix)
    chosen = st.selectbox('Exécution IA locale à consulter', ids,
                          index=ids.index(latest) if latest in ids else 0,
                          format_func=lambda value: next(f"{t['debut_utc'][:19]} UTC · {t.get('configuration_id', 'pilote historique')} · {t['etat']} · {value[:8]}" for t in traces if t['id'] == value),
                          key='execution_ia_selection' + suffix)
    trace = next(t for t in traces if t['id'] == chosen)
    if trace.get('configuration_id'):
        st.caption(f"Configuration : {trace['configuration_id']} · température : {trace['parametres']['temperature']} · graine : {trace['parametres'].get('seed', 'non enregistrée')}")
    if trace.get('revalidation'):
        with st.expander('Revalidation tracée — état initial conservé'):
            st.json(trace['revalidation'])
    st.caption(f"Origine des données : {trace.get('origine_donnees', 'non chargées')} · modèle : {trace['modele']} · frais API externes : 0 USD. Les jetons ci-dessous sont réellement rapportés par Ollama ; les inconnus restent indisponibles.")
    columns = st.columns(3)
    columns[0].metric('Durée mesurée de cette exécution', f"{trace['duree_s']:.1f} s")
    columns[1].metric('Jetons d’entrée', trace['jetons_entree'] if trace.get('jetons_entree') is not None else 'Indisponible')
    columns[2].metric('Jetons de sortie', trace['jetons_sortie'] if trace.get('jetons_sortie') is not None else 'Indisponible')
    if trace.get('resultat'):
        final_data = {}
        try:
            final_data = json.loads(trace['resultat'])
            conclusion = final_data.get('resultat', trace['resultat'])
        except (ValueError, AttributeError):
            conclusion = trace['resultat']
        validator = verifier_synthese_groupes if group_mode else verifier_synthese_periodes if period_mode else verifier_synthese_videos
        current_checks = validator(final_data, trace['verification']) if (video_mode or period_mode or group_mode) and trace.get('verification') else None
        if current_checks is not None:
            with st.expander('Contrôles actuels du texte — trace originale conservée'):
                st.json(current_checks)
        if (current_checks is not None and not all(current_checks.values())) or trace.get('verification', {}).get('verdict') == 'refuse' or (
                trace.get('validation_synthese') and not all(trace['validation_synthese'].values())):
            st.error('Synthèse non validée : un contrôle a échoué. Ne pas utiliser la conclusion comme recommandation.')
            with st.expander('Brouillon généré non validé'):
                st.write(conclusion)
        else:
            st.write(conclusion)
            if video_mode and isinstance(final_data, dict) and final_data.get('recommandation'):
                st.warning('Hypothèse éditoriale à tester : ' + final_data['recommandation'])
                st.caption('Ce texte est généré par le modèle. Sa pertinence éditoriale nécessite une revue humaine ; aucun gain de vues n’est garanti.')
        st.caption(('Unités de cette mission : vues (Views) et heures de visionnage, sans assimilation aux vues engagées. ' if video_mode or period_mode or group_mode else 'Unité de cette mission : vues engagées, distinctes de la colonne Views. ') + 'Cette synthèse reste soumise à une revue humaine.')
    report = trace.get('verification')
    if report:
        st.subheader('Rapport du vérificateur')
        if report['verdict'] == 'refuse':
            st.error('Verdict : refusé — des contrôles numériques ont échoué.')
        else:
            st.success('Verdict : accepté avec réserves — cohérence numérique vérifiée.')
        labels = {'reussi': 'Réussi', 'echoue': 'Échoué', 'non_applicable': 'Non applicable'}
        def formatted(value):
            return json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else str(value) if value is not None else 'Indisponible'
        st.dataframe([{'Contrôle': c['controle'], 'État': labels[c['etat']],
                       'Observé': formatted(c['observe']), 'Attendu': formatted(c['attendu'])}
                      for c in report['controles']], width='stretch', hide_index=True)
        for warning in report['avertissements']:
            st.warning(warning)
        st.caption('Les contrôles et le verdict sont calculés par un outil Python appelé par le vérificateur. Le modèle ne peut pas transformer un échec numérique en validation. Les réserves ne prouvent pas la cause des écarts.')
        if trace.get('validation_synthese'):
            with st.expander('Respect du verdict et des chiffres par la synthèse'):
                st.json(trace['validation_synthese'])
    else:
        st.caption('Ancienne trace : pas de rapport détaillé du vérificateur. Lancer une nouvelle mission pour obtenir les contrôles explicites ; les anciennes traces sont conservées sans modification.')
    if trace.get('validation_integration'):
        with st.expander('Contrôles d’intégration — sans score de qualité complet'):
            st.json(trace['validation_integration'])
            st.write(trace['limite_validation'])
    if trace['erreurs']:
        st.error('Erreur de fonctionnement : la trace conserve les mesures partielles sans annoncer une réussite.')
        st.json(trace['erreurs'])
    steps = trace['etapes']
    if not steps:
        return
    index = st.slider('Relecture de l’exécution IA réelle', 1, len(steps), len(steps), key=f"ia_relecture_{chosen}")
    visible = steps[:index]
    messages = [m for m in trace['messages'] if m['etape_cible'] <= index]
    roles = list(dict.fromkeys(s['agent'] for s in steps))
    positions = {role: i for i, role in enumerate(roles)}
    graph = go.Figure()
    for message in messages:
        x0, x1 = positions[message['emetteur']], positions[message['destinataire']]
        y = -0.6 if x1 < x0 else 0
        graph.add_trace(go.Scatter(x=[x0, x0, x1, x1], y=[0, y, y, 0], mode='lines',
                                  text=[message['resume']] * 4, hoverinfo='text', showlegend=False))
        graph.add_annotation(x=x1, y=0, ax=x0, ay=y, axref='x', ayref='y', arrowhead=2, text='')
    graph.add_trace(go.Scatter(x=list(positions.values()), y=[0] * len(roles), mode='markers+text',
                              text=roles, textposition='top center', showlegend=False,
                              marker={'size': 24, 'color': ['#ef9b20' if role == steps[index - 1]['agent'] else '#2583c5' for role in roles]}))
    graph.update_layout(title='Contextes effectivement transmis entre agents CrewAI', height=300,
                        xaxis={'visible': False, 'range': [-0.5, len(roles) - 0.5]}, yaxis={'visible': False, 'range': [-1, 1]})
    st.plotly_chart(graph, width='stretch', key='ia_graphe' + suffix)
    st.caption('Interprétation : les liens représentent les résultats réellement transmis comme contexte à la tâche suivante. Le rôle orange correspond à l’étape de relecture, pas à un agent en activité actuelle.')
    st.dataframe([{'Étape': s['ordre'], 'Agent': s['agent'], 'Tâche': s['tache'], 'État': s['etat'],
                   'Durée (s)': s.get('duree_s')} for s in visible], width='stretch')
    measured = [s for s in visible if s.get('duree_s') is not None]
    if measured:
        figure = go.Figure(go.Bar(x=[s['duree_s'] for s in measured], base=[s.get('debut_s', 0) for s in measured],
                                 y=[f"{s['ordre']} · {s['agent']}" for s in measured], orientation='h'))
        figure.update_layout(title='Chronologie des tâches CrewAI locales', xaxis_title='Secondes depuis le lancement', yaxis_title='Tâche et agent')
        st.plotly_chart(figure, width='stretch', key='ia_timeline' + suffix)
        st.caption('Interprétation : chaque segment couvre le premier appel du modèle jusqu’au retour de la tâche, outils inclus. La durée totale inclut aussi l’initialisation du framework. Ces mesures ne sont pas les temps de la simulation.')
    if messages:
        sankey = go.Figure(go.Sankey(
            node={'label': [f"{s['ordre']} · {s['agent']}" for s in steps]},
            link={'source': [m['etape_source'] - 1 for m in messages],
                  'target': [m['etape_cible'] - 1 for m in messages], 'value': [1] * len(messages)}))
        sankey.update_layout(title='Transmission des résultats CrewAI — unité : contexte de tâche')
        st.plotly_chart(sankey, width='stretch', key='ia_sankey' + suffix)
        st.caption(f'Interprétation : {len(messages)} transmission(s) de résultat vers une tâche terminée à cette étape. Les liens ne mesurent ni les jetons ni la durée.')
    for step in visible:
        with st.expander(f"{step['ordre']} · {step['agent']} — résultat et appels"):
            st.write(step.get('sortie', 'Pas de résultat final pour cette étape.'))
            st.json({'appels': [c for c in trace['appels'] if c['etape'] == step['ordre']],
                     'outils': [t for t in trace['outils'] if t['etape'] == step['ordre']],
                     'messages': [m for m in trace['messages'] if m['etape_cible'] == step['ordre']]})
    st.caption('Les appels réels sont conservés dans executions_reelles ; les simulations restent dans demonstrations. Les pilotes et échecs ne sont pas automatiquement comptés comme vingt essais conformes du cours.')
