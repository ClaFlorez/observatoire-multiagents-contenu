"""Campagne : plan explicite, prochain essai et grille humaine sans note automatique."""
from datetime import date
import json
from pathlib import Path
import statistics
import streamlit as st
import plotly.graph_objects as go

from observatoire.campagne import (creer_plan, plans, essais, executer_prochain, evaluations,
    enregistrer_evaluation, CRITERES, synchroniser)
from observatoire.stockage import lire_executions_reelles
from observatoire.import_videos import importer_videos


def afficher_campagne(root, current, database):
    st.divider()
    st.header('Campagne évaluée — vingt essais à préparer et noter')
    st.caption('Cinq scénarios × deux températures du même Qwen3 4B × deux répétitions. T0 = 0 ; T04 = 0,4. Même graine au sein de chaque paire, mêmes données et limites. Ce protocole ne compare pas deux modèles différents. Pilotes exclus ; qualité évaluée par une personne.')
    with st.expander('Préparer et figer le plan des vingt essais'):
        candidates = sorted((Path(root) / 'youtube_csv').glob('parametres_s2_s4*.json'))
        path = st.text_input('JSON des groupes pour la campagne', str(candidates[0] if candidates else Path(root)/'youtube_csv'/'parametres_s2_s4.json'), key='campagne_json')
        previous_path = st.text_input('CSV de la période précédente pour S3', str(Path(root)/'youtube_csv'/'aout-sept'/'Table data.csv'), key='campagne_csv_avant')
        dates = st.date_input('Dates déclarées du rapport précédent pour la campagne',
                              value=(date(2026, 8, 20), date(2026, 9, 16)), key='campagne_dates')
        confirmed = st.checkbox('Je confirme les dates, groupes et limites exploratoires de S4 avant les essais.', key='campagne_confirmation')
        if st.button('Figer le plan — aucun appel IA', key='figer_campagne'):
            try:
                if not confirmed or len(dates) != 2:
                    raise ValueError('Confirmer les paramètres et les deux dates.')
                if Path(path).stat().st_size > 1000000:
                    raise ValueError('JSON trop volumineux.')
                protocol = json.loads(Path(path).read_text(encoding='utf-8-sig'))
                previous = importer_videos(previous_path, dates[0].isoformat(), dates[1].isoformat(), current['origine'])
                plan = creer_plan(current, previous, protocol, database)
                st.session_state['campagne_active'] = plan['id']
                st.success('Plan enregistré : vingt essais en attente, sans reprendre les pilotes.')
            except (ValueError, OSError, KeyError, TypeError) as exc:
                st.error(str(exc))
    available = plans(database)
    if not available:
        st.info('Aucun plan enregistré. Préparer le plan ci-dessus avant les vingt essais.')
        return
    identifiers = [p['id'] for p in available]
    active = st.session_state.get('campagne_active')
    chosen = st.selectbox('Campagne à consulter', identifiers,
                          index=identifiers.index(active) if active in identifiers else 0,
                          format_func=lambda i: next(p['cree_utc'][:19] + ' UTC · ' + i[:8] for p in available if p['id'] == i), key='campagne_selection')
    plan = next(p for p in available if p['id'] == chosen)
    for warning in plan['limites']:
        st.caption(warning)
    if st.button('Actualiser les fins d’essais depuis les traces', key='campagne_synchroniser'):
        st.info(f"{synchroniser(database, chosen)} état(s) synchronisé(s), aucun nouvel appel IA.")
    if st.button('Exécuter le prochain essai de campagne — 0 USD API', key='campagne_prochain'):
        try:
            with st.spinner('Essai local en cours : garder cette session ouverte…'):
                result = executer_prochain(database, chosen)
            if result is None:
                st.info('Tous les emplacements du plan ont été traités. Consulter les échecs et compléter les évaluations humaines.')
            elif result['etat'] == 'terminee':
                st.success('Essai terminé et conservé. La note humaine reste à remplir.')
            else:
                st.warning('Essai conservé avec état ' + result['etat'] + '. Aucun résultat de remplacement ni note inventés.')
        except (RuntimeError, ValueError, OSError) as exc:
            st.error(str(exc))
    entries = essais(database, chosen)
    traces = {t['id']: t for t in lire_executions_reelles(database) if t.get('campagne_id') == chosen}
    reviews = evaluations(database)
    cols = st.columns(3)
    cols[0].metric('Emplacements traités / 20', sum(e['etat'] not in ('en_attente', 'en_cours') for e in entries))
    cols[1].metric('Exécutions avec trace', len(traces))
    cols[2].metric('Évaluations humaines', sum(i in reviews for i in traces))
    st.caption('Un emplacement traité peut avoir échoué. Vingt emplacements ne prouvent pas vingt résultats exploitables ni vingt réussites.')
    if traces:
        st.subheader('Vue d’ensemble de la campagne sélectionnée')
        values = list(traces.values())
        durations = [t['duree_s'] for t in values if t.get('duree_s') is not None]
        tokens = [t.get(k) for t in values for k in ('jetons_entree', 'jetons_sortie')]
        costs = [t.get('cout_api_usd') for t in values]
        calls, role_times = {}, {}
        for trace in values:
            for call in trace.get('appels', []):
                role = call.get('agent', 'Inconnu')
                calls[role] = calls.get(role, 0) + 1
            by_role = {}
            for step in trace.get('etapes', []):
                if step.get('duree_s') is not None:
                    role = step['agent']
                    by_role[role] = by_role.get(role, 0) + step['duree_s']
            for role, seconds in by_role.items():
                role_times.setdefault(role, []).append(seconds)
        metrics = [
            ('Exécutions observées', len(values)),
            ('Validation automatique', f"{100 * sum(t['etat'] == 'terminee' for t in values) / len(values):.1f} %"),
            ('Durée moyenne', f'{statistics.mean(durations):.2f} s' if durations else 'Indisponible'),
            ('Jetons entrée et sortie', sum(tokens) if all(v is not None for v in tokens) else 'Indisponible'),
            ('Frais API externes', f'{sum(costs):.2f} USD' if all(v is not None for v in costs) else 'Indisponible'),
            ('Erreurs de workflow enregistrées', sum(len(t.get('erreurs', [])) for t in values)),
            ('Rôle le plus appelé', max(calls, key=calls.get) if calls else 'Indisponible'),
            ('Rôle le plus lent en moyenne', max(role_times, key=lambda r: statistics.mean(role_times[r])) if role_times else 'Indisponible'),
        ]
        for start in (0, 4):
            for column, (label, value) in zip(st.columns(4), metrics[start:start + 4]):
                column.metric(label, value)
        st.caption('Indicateurs sur toute la campagne sélectionnée, avant les filtres ci-dessous. Validation automatique distincte de la qualité humaine ; erreurs de workflow distinctes des refus lexicaux. Durée par rôle cumulée sur ses tâches ; électricité et matériel non chiffrés.')
    scenarios = st.multiselect('Filtrer la campagne par scénario', ['S1', 'S2', 'S3', 'S4', 'S5'], default=['S1', 'S2', 'S3', 'S4', 'S5'], key='campagne_filtre_scenario')
    states = sorted({e['etat'] for e in entries})
    states_selected = st.multiselect('Filtrer la campagne par état', states, default=states, key='campagne_filtre_etat')
    configs = st.multiselect('Filtrer la campagne par configuration', ['T0', 'T04'], default=['T0', 'T04'], key='campagne_filtre_configuration')
    agent = st.selectbox('Agent pour les durées affichées', ['Tous les agents', 'Coordonnateur', 'Chercheur', 'Analyste', 'Vérificateur'], key='campagne_filtre_agent')
    visible = [e for e in entries if e['scenario'] in scenarios and e['etat'] in states_selected and e['configuration'] in configs]
    def duration(trace):
        if agent == 'Tous les agents':
            return trace.get('duree_s')
        values = [s['duree_s'] for s in trace.get('etapes', []) if s['agent'] == agent and s.get('duree_s') is not None]
        return sum(values) if values else None
    st.dataframe([{'ordre': e['ordre'], 'scenario': e['scenario'], 'configuration': e['configuration'], 'repetition': e['repetition'],
                   'etat': e['etat'], 'execution_id': e['id'], 'duree_s': duration(traces.get(e['id'], {})),
                   'score_humain_sur_8': reviews.get(e['id'], {}).get('score'), 'diagnostic': e['diagnostic']} for e in visible], hide_index=True, width='stretch')
    plotted = [e for e in visible if duration(traces.get(e['id'], {})) is not None]
    if plotted:
        fig = go.Figure()
        for config in configs:
            group = [e for e in plotted if e['configuration'] == config]
            fig.add_bar(name=config, x=[f"{e['scenario']} R{e['repetition']}" for e in group], y=[duration(traces[e['id']]) for e in group])
        fig.update_layout(title='Durées réelles — ' + agent, xaxis_title='Scénario et répétition', yaxis_title='Secondes', barmode='group')
        st.plotly_chart(fig, width='stretch', key='campagne_durees')
        st.caption('Comparaison descriptive de tâches identiques par scénario. Les temps de chargement et le cache peuvent varier ; aucun effet causal établi sur deux répétitions.')
    if visible:
        z, labels = [], []
        for scenario in ('S1', 'S2', 'S3', 'S4', 'S5'):
            values = []
            for config in configs:
                scores = [reviews[e['id']]['score'] for e in visible if e['scenario'] == scenario and e['configuration'] == config and e['id'] in reviews]
                values.append(statistics.mean(scores) if scores else None)
            z.append(values)
            labels.append(scenario)
        fig = go.Figure(go.Heatmap(z=z, x=configs, y=labels, zmin=0, zmax=8, colorbar={'title': 'Score / 8'}, hoverongaps=False))
        fig.update_layout(title='Qualité humaine — moyenne des essais notés', xaxis_title='Configuration', yaxis_title='Scénario')
        st.plotly_chart(fig, width='stretch', key='campagne_heatmap')
        st.caption('Case vide = aucune évaluation humaine dans la sélection. Les contrôles automatiques ne créent aucune note.')
    completed = [e for e in entries if e['id'] in traces and traces[e['id']]['etat'] != 'en_cours']
    if completed:
        selected = st.selectbox('Exécution à examiner et noter', [e['id'] for e in completed],
                                format_func=lambda i: next(f"{e['ordre']} · {e['scenario']} · {e['configuration']} · R{e['repetition']} · {i[:8]}" for e in completed if e['id'] == i), key='campagne_a_noter')
        with st.expander('Preuves de l’exécution sélectionnée', expanded=True):
            st.json(traces[selected])
        with st.form('campagne_evaluation_' + selected):
            st.caption('0 = absent ou incorrect ; 1 = partiel ; 2 = satisfait avec preuve. Aucune note présélectionnée.')
            notes = {key: st.selectbox(key + ' / 2', [0, 1, 2], index=None, key=selected + '_' + key) for key in CRITERES}
            evaluator = st.text_input('Évaluateur', key=selected + '_evaluateur')
            justification = st.text_area('Justification des quatre notes et preuves consultées', key=selected + '_justification')
            critical = st.checkbox('Erreur critique détectée', key=selected + '_critique')
            if st.form_submit_button('Enregistrer l’évaluation humaine'):
                try:
                    review = enregistrer_evaluation(database, selected, notes, evaluator, justification, critical)
                    st.success(f"Évaluation conservée : {review['score']}/8. Les versions précédentes restent dans l’historique.")
                    st.rerun()
                except ValueError as exc:
                    st.error(str(exc))
    st.download_button('Télécharger le manifeste et les évaluations', json.dumps({'plan': plan, 'essais': entries, 'evaluations': {i: reviews[i] for i in traces if i in reviews}}, ensure_ascii=False, indent=2),
                       file_name='manifeste_campagne_' + chosen[:8] + '.json', mime='application/json', key='export_campagne')
