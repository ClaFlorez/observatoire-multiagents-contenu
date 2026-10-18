"""Sélecteur de CSV local, sans copie ni chargement automatique."""
from pathlib import Path
import streamlit as st


def contenu_csv(base, dossier):
    base, dossier = Path(base).resolve(), Path(dossier).resolve()
    if not dossier.is_relative_to(base):
        raise ValueError('Choisir un dossier situé dans la source sélectionnée.')
    folders, files = [], []
    for item in dossier.iterdir():
        if item.name.startswith('.') or not item.resolve().is_relative_to(base):
            continue
        if item.is_dir():
            folders.append(item)
        elif item.is_file() and item.suffix.lower() == '.csv':
            files.append(item)
    return sorted(folders, key=lambda p: p.name.casefold()), sorted(files, key=lambda p: p.name.casefold())


@st.dialog('Choisir un fichier CSV', width='large', dismissible=False)
def _fenetre_csv(root, cible):
    root = Path(root).resolve()
    source = st.selectbox('Emplacement des fichiers', ['data', 'youtube_csv'],
                          format_func=lambda s: 'data — exemples et données locales' if s == 'data' else 'youtube_csv — exports YouTube (88 vidéos dans setp-oct)',
                          key='source_csv_' + cible)
    base = root / source
    dossier_key = '_dossier_csv_' + cible
    dossier = Path(st.session_state.get(dossier_key, str(base)))
    st.caption('Choisir une source, ouvrir un sous-dossier, puis sélectionner le CSV. Le choix ne lance aucun import ni appel IA.')
    if st.button('Annuler', key='annuler_csv_' + cible):
        st.session_state['_fenetre_csv_' + cible] = False
        st.rerun()
    try:
        folders, files = contenu_csv(base, dossier)
    except (OSError, ValueError):
        dossier = base
        st.session_state[dossier_key] = str(base)
        try:
            folders, files = contenu_csv(base, dossier)
        except OSError:
            st.error('Le dossier sélectionné est inaccessible.')
            return
    st.write('**Dossier ouvert :** ' + str(dossier))
    if dossier != base and st.button('Remonter au dossier parent', key='parent_' + cible):
        st.session_state[dossier_key] = str(dossier.parent)
        st.rerun()
    if folders:
        chosen = st.selectbox('Sous-dossier', folders, format_func=lambda p: p.name,
                              key='dossier_liste_' + cible + str(dossier))
        if st.button('Ouvrir le dossier', key='ouvrir_dossier_' + cible):
            st.session_state[dossier_key] = str(chosen)
            st.rerun()
    if not files:
        st.info('Aucun CSV dans ce dossier. Ouvrir un sous-dossier ou remonter.')
        return
    selected = st.selectbox('Fichier CSV', files, format_func=lambda p: p.name,
                            key='csv_liste_' + cible + str(dossier))
    st.caption(f'Taille : {selected.stat().st_size:,} octets')
    if st.button('Utiliser ce CSV', key='choisir_csv_' + cible, type='primary'):
        # Appliquer avant la création du champ texte lors du prochain rendu complet.
        st.session_state['_selection_csv_' + cible] = str(selected)
        st.session_state['_fenetre_csv_' + cible] = False
        st.rerun()


def afficher_choix_csv(root, cible, label='Choisir un CSV — data ou YouTube'):
    pending = '_selection_csv_' + cible
    if pending in st.session_state:
        st.session_state[cible] = st.session_state.pop(pending)
    if st.button(label, key='parcourir_' + cible):
        st.session_state['_dossier_csv_' + cible] = str(Path(root) / 'data')
        st.session_state['_fenetre_csv_' + cible] = True
    if st.session_state.get('_fenetre_csv_' + cible, False):
        _fenetre_csv(root, cible)
