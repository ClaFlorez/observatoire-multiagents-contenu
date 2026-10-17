"""Préparation explicite des groupes de campagne, sans appel au modèle."""

import json
from pathlib import Path
import streamlit as st
from observatoire.scenarios_groupes import comparer_groupes, comparer_cible
from observatoire.agents_groupes import preparer
from observatoire.vue_agents_locaux import afficher_agents_locaux


def afficher_preparation(report, root=None, database=None):
    st.divider()
    st.subheader('Préparer les scénarios S2 et S4')
    st.caption('Calcul Python uniquement. Choisir les groupes avant la campagne ; aucun format vidéo ni lien causal ne sont déduits. Cette préparation ne lance pas les agents.')
    rows = {row['id']: row for row in report['videos']}
    ids = sorted(rows)
    label = lambda identifier: f"{identifier} — {rows[identifier]['titre'] or 'Titre indisponible'}"
    # L’empreinte évite de réutiliser les choix d’un autre export.
    prefix = 'scenario_' + report['fichier']['sha256']
    with st.expander('S2 — deux groupes explicites'):
        a = st.multiselect('Vidéos du groupe A', ids, format_func=label, key=prefix + '_a')
        b = st.multiselect('Vidéos du groupe B', ids, format_func=label, key=prefix + '_b')
        rationale = st.text_input('Justification du choix des groupes', key=prefix + '_justification')
        result_s2 = None
        if a and b:
            try:
                result_s2 = comparer_groupes(report, a, b)
                st.dataframe([{'mesure': metric, 'groupe': group, **{k: str(v) if v is not None else 'Indisponible' for k, v in stats.items()}}
                              for metric, groups in result_s2.items() for group, stats in groups.items()], hide_index=True)
                st.caption('Les sommes dépendent des effectifs ; les médianes portent uniquement sur les valeurs connues. La comparabilité des groupes exige une justification humaine.')
            except ValueError as exc:
                st.error(str(exc))
    with st.expander('S4 — cible et références explicites'):
        target = st.selectbox('Vidéo cible', ids, index=None, format_func=label, key=prefix + '_cible')
        reference = st.multiselect('Groupe de référence de la cible', ids, format_func=label, key=prefix + '_reference')
        metric = st.selectbox('Mesure de la cible', ['vues', 'heures'], key=prefix + '_mesure')
        reason = st.text_input('Pourquoi ce groupe est-il comparable à la cible ?', key=prefix + '_comparabilite')
        result_s4 = None
        if target and reference:
            try:
                result_s4 = comparer_cible(report, target, reference, metric)
                st.json(json.loads(json.dumps(result_s4, default=str)), expanded=True)
                st.caption('Un écart négatif signifie seulement une valeur sous la médiane connue du groupe choisi. Il ne prouve ni un échec général ni sa cause.')
            except ValueError as exc:
                st.error(str(exc))
    if result_s2 is not None and result_s4 is not None and rationale.strip() and reason.strip():
        protocol = {'statut': 'preparation_sans_execution_IA', 'fichier': report['fichier'],
                    'periode': report['periode'], 'origine': report['origine'],
                    'S2': {'groupe_a': sorted(a), 'groupe_b': sorted(b), 'justification': rationale, 'calcul': result_s2},
                    'S4': {'cible': target, 'references': sorted(reference), 'mesure': metric, 'justification': reason, 'calcul': result_s4}}
        st.download_button('Enregistrer les paramètres S2 et S4 (JSON)',
                           json.dumps(protocol, ensure_ascii=False, indent=2, default=str),
                           file_name='parametres_s2_s4.json', mime='application/json', key=prefix + '_export')
    if root is None or database is None:
        return
    st.subheader('Charger les paramètres enregistrés — S2 et S4')
    candidates = sorted((Path(root) / 'youtube_csv').glob('parametres_s2_s4*.json'))
    default = candidates[0] if candidates else Path(root) / 'youtube_csv' / 'parametres_s2_s4.json'
    path = st.text_input('Fichier JSON S2/S4', str(default), key='missions_groupes_fichier')
    if st.button('Charger et vérifier les paramètres S2/S4', key='charger_missions_groupes'):
        st.session_state.pop('missions_groupes_chargees', None)
        try:
            source = Path(path)
            if source.stat().st_size > 1000000:
                raise ValueError('JSON trop volumineux.')
            protocol = json.loads(source.read_text(encoding='utf-8-sig'))
            missions = {s: preparer(report, protocol, s) for s in ('S2', 'S4')}
            st.session_state['missions_groupes_chargees'] = missions
        except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
            st.error('Paramètres refusés : ' + str(exc))
    saved = st.session_state.get('missions_groupes_chargees')
    if saved and all(saved['S2'][key] == report[key] for key in ('fichier', 'periode', 'origine')):
        st.caption('Paramètres chargés et calculs recalculés. Les modifications des sélecteurs ci-dessus ne changent pas ces missions enregistrées ; exporter puis recharger pour les remplacer.')
        for scenario in ('S2', 'S4'):
            mission = {**saved[scenario], 'type': scenario}
            afficher_agents_locaux(mission, database, scenario)
