# Validation et protocole expérimental

## Grille de remise

Toutes les lignes sont **à réaliser** au démarrage. Une exigence ne passe à « validée » qu’avec une preuve reproductible.

État intermédiaire : le laboratoire déterministe permet de tester le graphe, la timeline, le Sankey et la relecture sans API. Ses traces portent `mode=simulation` et `eligible_campagne_reelle=false` et sont stockées séparément. Les filtres de démonstration sont testables mais ne prouvent pas le fonctionnement des agents IA. Le budget courant est de 0 USD et aucune clé n’est utilisée.

Une section distincte exécute maintenant les quatre agents CrewAI sur Qwen3 4B local, avec appels réels à deux outils et sauvegarde dans `executions_reelles`. Deux pilotes ont réussi les contrôles minimaux d’intégration, l’un sur exemple fictif et l’autre sur exports réels. Les pilotes, dont les échecs de mise au point, restent exclus du décompte de campagne tant que leur conformité méthodologique n’a pas été revue. La grille complète n’est pas déclarée validée.

La version 2 ajoute un troisième outil pour le vérificateur : recalcul indépendant, contrôles explicites, verdict et réserves. Les chiffres et le verdict de la synthèse sont comparés aux sources et son texte doit citer le pays et son volume. Les tests couvrent notamment un mauvais dénominateur, des données quotidiennes incohérentes, des dates manquantes et une conclusion générique. Ces contrôles numériques ne remplacent pas les quatre critères de qualité décrits plus bas.

| Exigence | Critère d’acceptation et preuve |
|---|---|
| Quatre agents distincts | Rôles configurés et tâches réellement exécutées ; traces d’interactions entre agents |
| Au moins deux outils | Appels réels à la lecture des données et aux calculs Python, avec résultats et erreurs tracés |
| Vingt exécutions et cinq scénarios | Manifest des exécutions réelles, identifiants, scénarios et configurations ; essais fictifs exclus |
| Six visualisations | Graphe, timeline, Sankey, comparaison, carte thermique et indicateurs lisibles |
| Trois filtres | Agent, scénario et état testés séparément et ensemble ; vues actualisées et sélection vide traitée |
| Présentation des graphiques | Titre, unité appropriée, axes et légende lorsque nécessaires, interprétation courte |
| Conclusions mesurables | Chaque conclusion cite un indicateur, un effectif et une comparaison ou visualisation |
| Secrets et données sensibles absents | Contrôle des fichiers suivis et de l’historique avant partage ; aucune clé, aucun jeton ou export privé |
| README utilisable | Installation et démarrage réussis dans un environnement Windows propre |
| Maîtrise du projet | L’étudiante explique les agents, outils, calculs, graphiques et limites ; peut modifier un élément pendant la démonstration |

Les données YouTube ne sont pas des traces d’exécution. Vingt lignes de CSV, vingt publications ou vingt agents invoqués ne constituent pas vingt exécutions du système.

## Cinq scénarios

Le [protocole détaillé des cinq scénarios](scenarios.md) précise les consignes, preuves attendues, données manquantes et critères humains. Il s’agit d’une préparation de campagne ; l’interface ne propose pas encore les cinq missions.

| ID | Mission | Condition nécessaire |
|---|---|---|
| S1 | Classer les contenus selon les vues et la durée de visionnage | Export par vidéo et période commune |
| S2 | Comparer deux formats | Format fiable ; sinon deux groupes de vidéos choisis explicitement |
| S3 | Comparer deux périodes de même longueur | Couverture et métriques compatibles ; exporter de nouvelles données si nécessaire |
| S4 | Examiner un contenu sous-performant par rapport à un groupe comparable | Définition explicite du groupe et du critère de sous-performance |
| S5 | Proposer une priorité éditoriale avec preuves et réserves | Synthèse des données disponibles, sans promesse de résultat commercial |

Les scénarios et paramètres seront figés après inspection de l’export par vidéo, avant la campagne. Les fichiers géographiques actuels fourniront le contexte d’audience.

## Campagne réelle

Plan minimal : **cinq scénarios × deux configurations × deux répétitions = vingt exécutions réelles**. Les deux configurations locales T0 et T04 utilisent le même Qwen3 4B, avec températures 0 et 0,4. Aucun fournisseur externe ; 0 USD d’API externe. Le registre et les grilles humaines sont disponibles ; leur existence ne prouve pas vingt essais réalisés et notés. Voir [le protocole actuel](campagne.md). Ce plan ne compare pas deux modèles différents.

Conserver le même jeu de données, la même question et les mêmes consignes pour les comparaisons appariées. Enregistrer versions, paramètres, ordre des essais, date et modèle effectivement retourné. Alterner l’ordre des configurations pour limiter un effet d’ordre. Ne pas supprimer un échec pour améliorer les moyennes.

Une exécution est un lancement identifié du workflow complet. Les tentatives et corrections restent des étapes de cette exécution. Les échecs sont conservés ; si des essais ne démarrent pas ou ne fournissent aucune trace exploitable, compléter la campagne et déclarer le nombre total de lancements.

## Évaluation de la qualité

Quatre critères, chacun noté de 0 à 2 : exactitude numérique, traçabilité des preuves, respect de la demande, prise en compte des limites. Le score total va de 0 à 8. Pour chaque critère : 0 = absent ou incorrect ; 1 = partiel ; 2 = satisfait avec preuve vérifiable.

Validation réussie : score d’au moins 6/8, exactitude et preuves à 2/2, aucune erreur critique ni divulgation. Le score automatique du vérificateur sera contrôlé manuellement sur les vingt résultats et les désaccords documentés. Cette grille évalue une réponse ; elle ne mesure pas un gain commercial réel.

## Tests nécessaires

- Import : colonnes absentes, doublons au bon niveau d’agrégation, cellules vides, dates invalides et conversion des durées.
- Calculs : petit jeu à résultats connus, division par zéro, séparation Total/détails, différence entre vues et vues engagées.
- Traces : identifiants liés, ordre des messages, tentatives distinctes et absence de double comptage des appels.
- Workflow : succès, données insuffisantes, erreur d’outil, panne de modèle, correction unique et arrêt au budget.
- Interface : cohérence des indicateurs avec SQLite, filtres combinés, comparaison et relecture sans nouvel appel IA.
- Confidentialité : aucune donnée sensible dans les prompts, résultats partagés ou événements envoyés à AgentOps.

Les tests avec réponses simulées valident le logiciel ; seuls les essais avec appels réels étayent l’analyse des performances IA.

## Analyse et limites

Étudier les jetons, durées, erreurs, reprises, coût et qualité ; repérer les goulots et communications peu utiles. Produire au moins trois recommandations reliées aux mesures.

L’effet du nombre d’agents sur la durée ne peut pas être établi en gardant toujours quatre agents. Si cette question est retenue dans l’analyse, ajouter une expérience contrôlée avec quatre puis cinq agents, en conservant tâches et modèles comparables ; ces essais s’ajoutent à la campagne minimale. Sinon, déclarer cette question non mesurée.

Vingt observations et deux répétitions par configuration permettent une exploration descriptive, sans garantir une généralisation statistique. Aucun lien causal entre coût et qualité ne sera affirmé sur la seule base d’une corrélation.

## Rapport et présentation

Le rapport présentera problème, public cible, agents, architecture, données, choix visuels, résultats, limites, au moins trois recommandations et conclusion. L’annexe API restera distincte du périmètre réalisé.

Préparer une démonstration individuelle de dix à douze minutes : problème, architecture, exécution, tableau de bord, interprétation et limites. Une relecture locale de traces réelles permettra de présenter les résultats en cas de panne réseau ; elle sera annoncée comme relecture.

La répartition indicative de l’évaluation est : système 15, données 10, visualisations 25, interactivité 15, interprétation 20, technique 5, rapport 5, présentation 5, soit 100 points.
