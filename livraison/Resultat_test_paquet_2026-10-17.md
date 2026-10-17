# Vérification du paquet de remise

Date : 17 octobre 2026, heure de Toronto.
Archive : Observatoire_multiagents_remise_2026-10-16.zip
SHA256 : 429ba61bfb6aa22f6be6621b19b72d234f0e7c47b6ff67573de22388db76d165

## Résultats

- Intégrité ZIP et empreintes des 73 fichiers du manifeste : réussies.
- Extraction dans une nouvelle arborescence de test : réussie.
- Absence de .env, clés, logs, bases privées, modèles et environnements dans les chemins distribués : vérifiée sur la liste des fichiers autorisés.
- Installation avec Python 3.12.14 dans un environnement virtuel neuf, sans accès aux paquets de l’environnement habituel : réussie.
- Dépendances directes : Streamlit 1.66.0, Plotly 7.1.0, CrewAI 1.15.28, AgentOps 0.4.21.
- pip check : aucune dépendance incompatible détectée.
- Tests depuis le code extrait avec le nouvel environnement : 67 tests, tous réussis, 11,129 secondes.
- Exemple vidéo livré : 8 vidéos, 560 vues et 5,6 heures sur la ligne Total ; interface AppTest sans exception et 3 graphiques.
- Indicateurs de campagne : contrôle sur fixture fictive, 1 exécution, 120 jetons, durée moyenne 100 secondes ; sélection vide du filtre scénario sans exception.
- Packages Word et PowerPoint : intégrité ZIP et XML valides. Ce contrôle structurel ne constitue pas une nouvelle inspection visuelle.

## Portée

L’installation est propre au niveau des dépendances Python, mais utilise le même ordinateur et le runtime de base Python existant. Un autre ordinateur Windows reste à vérifier. Les modèles Ollama ne sont pas inclus et aucun nouvel appel au modèle ni envoi AgentOps n’a été effectué pendant cet essai du paquet. Les clés et bases réelles n’ont pas été copiées. Les essais historiques restent consultables dans le rapport, pas dans une base privée livrée automatiquement.

Les contrôles AppTest du CSV livré et de la nouvelle ligne d’indicateurs ont été faits avec l’environnement de développement avant la suite complète dans l’environnement neuf. Aucun résultat d’inférence ou score de qualité nouveau n’est revendiqué.
