# Vérification de la remise

État vérifié le 16 octobre 2026. Cette liste n'est pas une note attribuée par
l'enseignant. La modalité individuelle et l'approbation du sujet restent à confirmer.

| Exigence | Preuve et limite |
|---|---|
| Quatre agents distincts | Cadrage, provenance, calcul, vérification et synthèse ; coordonnateur utilisé deux fois |
| Au moins deux outils | Lecture, calcul et recalcul indépendant |
| 20 exécutions et 5 scénarios | Campagne figée, 20 traces et 20 avis ; 19 validations automatiques et un refus lexical conservé |
| Six visualisations | Graphe et relecture, timeline, Sankey, durées comparées, heatmap des notes et indicateurs de campagne |
| Trois interactions | Sélection d'exécution, filtres scénario/état/configuration/agent et relecture |
| Vue d'ensemble | Nombre d'exécutions, validation, durée moyenne, jetons, frais API, erreurs de workflow, rôles les plus appelé et lent |
| Interprétation | Trois recommandations mesurées, S4 exploratoire, S5 encore générique, pas d'effet causal de température établi |
| Observabilité AgentOps | Pilote fictif séparé, 6 spans reçus ; résumé postérieur et aucune instrumentation LLM native revendiquée |
| Rapport | Version française de 132 pages avec preuves et limites |
| Présentation | 15 diapositives ; notes de 715 secondes, soit 11 min 55 s indicatives |
| Tests | 67 tests locaux réussis ; ce résultat ne remplace pas un essai sur ordinateur vierge |
| Confidentialité | Paquet à liste blanche ; clés, logs, bases réelles, .env et runtime exclus |

## Installation et essai avant présentation

1. Installer Python 3.12 et créer un environnement virtuel.
2. Installer requirements.txt ; requirements-agentops.txt ajoute l'option AgentOps.
3. Lancer les tests puis Streamlit selon le README.
4. Charger les exemples fictifs. Pour les vidéos, utiliser les CSV avant/après
   fournis sous data/examples/videos, déclarer l'origine fictive et les périodes
   20 août au 16 septembre puis 17 septembre au 14 octobre 2026.
5. Installer Ollama et Qwen3 4B séparément pour exécuter les agents réels.
   Une simple consultation des graphiques n'exige pas d'inférence.
6. Pour S2/S4, choisir explicitement les groupes et exporter/recharger leurs
   paramètres avant les missions. L'absence de comparabilité reste une réserve.

## Vérifications humaines restantes

Entraîner la démonstration de 10 à 12 minutes, vérifier l'installation sur un
autre poste, confirmer le sujet et le travail individuel avec l'enseignant.
La nouvelle ligne d'indicateurs a passé la suite de tests ; sa lisibilité sur
le poste de présentation reste à contrôler. La campagne initiale est en lecture
historique : les évolutions du code ne modifient pas ses traces.

Les données et bases réelles restent privées. Le paquet contient des exemples
fictifs pour tester l'application, mais pas une copie des 20 traces privées.
Ne pas annoncer qu'une installation vierge montrera automatiquement la campagne
historique ; les résultats et captures sont dans le rapport.
