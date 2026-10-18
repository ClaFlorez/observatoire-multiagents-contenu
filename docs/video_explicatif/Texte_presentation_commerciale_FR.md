# Présentation commerciale de l’observatoire multiagents

Vidéo en français, sans narration et sans marque ni image personnelle.
Durée : 10 minutes 30 secondes ; 21 séquences de 30 secondes.
Les graphiques de démonstration utilisent les exemples fictifs du projet.

## 00:00 — Vos statistiques méritent une réponse claire

Un observatoire multiagents pour les créateurs de contenu

Vous publiez des vidéos. Vous accumulez des chiffres. Mais comment savoir quelles performances examiner et quelles questions poser ensuite ?

Je vous présente un prototype qui rassemble les données, organise leur analyse et permet de retrouver les preuves de ses constats.

Des statistiques à des décisions mieux préparées

## 00:30 — Publier ne suffit pas pour comprendre

Le problème auquel répond notre projet

Une vidéo obtient plus de vues. Une autre cumule davantage de visionnage. Un changement entre deux périodes vous surprend.

Comparer ces chiffres sans connaître leur contexte peut conduire à une mauvaise interprétation. Il faut aussi vérifier les données absentes et les groupes choisis.

Voir un écart, puis vérifier ce qu’il signifie

## 01:00 — Une solution destinée aux créateurs

Sujet A8 : performance du contenu numérique

Notre observatoire s’adresse aux créateurs et aux équipes qui souhaitent préparer leurs décisions à partir de statistiques YouTube.

Il ne publie pas à votre place et ne promet pas de rendre une vidéo virale. Il aide à structurer les questions, comparer les mesures et conserver les résultats.

Un outil d’analyse pour éclairer votre travail

## 01:30 — Un seul parcours pour analyser vos données

Charger → comparer → vérifier → consulter

Vous choisissez le fichier et confirmez sa période. Le système prépare le scénario, réalise les calculs et conserve une trace de l’analyse.

Vous consultez ensuite les résultats, leurs limites et les graphiques dans une interface. Vous pouvez revenir sur les étapes sans relancer le modèle.

Les résultats et leurs preuves restent liés

## 02:00 — Commencer avec un fichier CSV

Des exports YouTube Studio et des périodes explicites

Le point de départ est un export statistique. Le programme contrôle les colonnes, les identifiants et la présence des mesures utiles.

La période statistique doit être confirmée : elle ne se confond pas avec la date de publication de la vidéo. Les données manquantes restent signalées.

Une analyse utile commence par des données comprises

## 02:30 — Quatre rôles pour organiser l’analyse

Le coordonnateur intervient au début et à la fin

Le Coordonnateur cadre la demande. Le Chercheur consulte les données. L’Analyste demande les calculs. Le Vérificateur contrôle les résultats.

Le Coordonnateur prépare ensuite une synthèse. Ce sont quatre rôles configurés avec le même modèle local, pour cinq tâches successives.

Une répartition explicite des responsabilités

## 03:00 — Une application full-stack en Python

Une interface et une logique de traitement réunies par Streamlit

Le frontend est la partie visible : Streamlit présente les contrôles et Plotly affiche les graphiques. Le backend contient nos modules Python, les calculs et l’orchestration CrewAI, reliée à Ollama et Qwen3.

SQLite conserve les données et les traces. Streamlit relie interface et traitements dans la même application ; nous n’avons pas créé un frontend React ni une API backend séparée.

Une seule application pour agir, analyser et consulter

## 03:30 — S1 : repérer les vidéos à examiner

Deux classements : vues et heures de visionnage

Le premier scénario classe l’ensemble du fichier par vues et par heures, séparément. Il fait ressortir les trois premières vidéos de chaque mesure.

L’exemple à gauche est fictif : 140, 120 et 100 vues. Les identifiants sont abrégés pour la lecture. Un bon classement ne démontre pas la cause du succès.

Deux mesures pour deux lectures complémentaires

## 04:00 — S2 : comparer deux groupes choisis

Une comparaison demande une question claire

Vous choisissez deux groupes et expliquez pourquoi ils méritent d’être comparés : sujet, format, durée et contexte d’exposition.

Dans notre exemple fictif, les médianes sont de 30 et 70 vues. La différence est descriptive. Elle ne prouve pas qu’un thème produit automatiquement plus de vues.

Comparer des groupes, sans inventer leur comparabilité

## 04:30 — S3 : suivre l’évolution entre deux périodes

Des fenêtres de même durée pour lire les changements

Vous comparez deux périodes en distinguant le total du canal des vidéos communes avec mesures connues. Les absences ne deviennent pas des zéros.

Le passage de 280 à 560 vues à gauche est un exemple fictif construit pour la démonstration. Ce doublement n’est pas une preuve de croissance réelle.

Lire l’évolution avec les bonnes populations

## 05:00 — S4 : situer une vidéo par rapport à une référence

Choisir une cible et justifier les vidéos de comparaison

Une vidéo vous interpelle ? Vous pouvez la comparer à un groupe de référence choisi explicitement, sans inclure la cible dans ce groupe.

L’exemple fictif montre 20 vues pour la cible et une médiane de référence de 70, soit un écart de moins 50. Cela ne constitue pas un diagnostic général d’échec.

Un écart à explorer, pas une étiquette définitive

## 05:30 — S5 : préparer une hypothèse à tester

Relier une action envisagée à une mesure et à une limite

L’intérêt d’une recommandation est de préparer une vérification : quelle action envisage-t-on, quelle mesure observera-t-on et quelle limite conservera-t-on ?

Dans notre campagne, ce scénario reste à améliorer : certaines formulations sont trop générales. Nous le présentons comme une piste à préciser, sans gain garanti.

Une hypothèse utile doit devenir assez précise pour être testée

## 06:00 — Explorer les résultats visuellement

Streamlit pour l’interface ; Plotly pour les graphiques

Les classements et comparaisons facilitent la lecture des mesures. Le graphe des agents, la chronologie et les indicateurs permettent aussi d’examiner le travail du système.

Les filtres et le survol aident à consulter un résultat. La relecture montre une étape déjà enregistrée ; elle ne signifie pas que l’agent travaille à nouveau.

Voir les données et comprendre le déroulement

## 06:30 — Retrouver la provenance d’une réponse

Données, outils, résultat et limites dans une même trace

Pour chaque exécution, le registre conserve un identifiant, des horaires, les agents, les tâches, les états, les outils et les réponses.

Les tokens décrivent les échanges avec le modèle. Les résultats des outils Python sont enregistrés séparément. Une réponse courte ne signifie pas que les calculs ont disparu.

La traçabilité aide à expliquer et à vérifier

## 07:00 — Un modèle exécuté sur le poste

Ollama et Qwen3, avec des frais d’API du modèle nuls

Notre configuration utilise Qwen3 4B localement sur CPU. L’installation et le téléchargement initial nécessitent Internet ; l’inférence reste sur le poste.

Les frais d’API du modèle sont de zéro dollar dans nos essais. Le matériel et l’électricité ne sont pas gratuits et n’ont pas été chiffrés. La vitesse dépend du poste.

Un coût API maîtrisé, avec des ressources locales à prévoir

## 07:30 — Un résumé technique externe avec AgentOps

Exigence du TP : une intégration limitée au résumé technique

AgentOps a été utilisé pour répondre à la spécification d’observabilité du TP. L’intégration reste limitée : après l’exécution, un processus séparé envoie un résumé technique autorisé. Un pilote a confirmé la réception de six spans.

Ce résumé ne remplace pas les traces locales. Les millisecondes des spans et les compteurs natifs à zéro ne décrivent pas toute l’activité du modèle. Les essais historiques ne sont pas réinstrumentés.

Observer davantage tout en comprenant ce qui est réellement mesuré

## 08:00 — Le prototype a été mis à l’épreuve

20 essais sur cinq scénarios et deux températures

La campagne combine cinq scénarios, deux températures du même Qwen3 et deux répétitions. Dix-neuf essais ont réussi les contrôles automatiques ; un refus est conservé.

La suite de 67 tests comprend des tests unitaires Python avec unittest et des tests d’interface Streamlit avec AppTest. Ils vérifient imports, calculs, valeurs absentes et contrôles ; ils ne prouvent pas une fiabilité universelle.

Des résultats documentés, avec une portée définie

## 08:30 — Les tests unitaires vérifient les fonctions

Python unittest · dossier tests/ · contrôles reproductibles

Un test unitaire vérifie un comportement ciblé avec un résultat attendu. Nos tests portent notamment sur l’import des CSV, les classements, les valeurs absentes, les vérifications et le stockage.

Exemple dans tests/test_s1.py : un jeu de données connu doit produire les bons leaders. Une valeur absente reste inconnue ; un identifiant erroné dans le classement doit entraîner un refus du vérificateur.

La suite de 67 tests inclut aussi des tests d’interface ; les 20 essais IA sont une campagne distincte.

## 09:00 — Une promesse qui reste honnête

Des constats vérifiables, sans promesse de viralité

Les vingt évaluations ont été proposées avec assistance IA, puis revues et saisies. Elles ne sont pas indépendantes en aveugle. Deux répétitions restent insuffisantes pour généraliser.

Les groupes doivent être mieux comparables et les recommandations plus précises. Le système conserve ces limites au lieu de transformer chaque résultat en certitude commerciale.

Vous gardez la décision ; le système apporte des éléments vérifiables

## 09:30 — Ce que vous recevez pour essayer

Sources, exemples fictifs, tests et guides en français

La livraison comprend le code, les exemples fictifs, le rapport, la présentation, le guide pas à pas et le dictionnaire des programmes. Elle est conservée dans un dépôt privé.

Le ZIP n’est pas un conteneur : il faut installer Python, les dépendances, Ollama et le modèle. Les données réelles, les bases privées et les clés ne sont pas fournies.

Un parcours de prise en main accompagné

## 10:00 — Et si vos chiffres devenaient plus faciles à expliquer ?

Une invitation à tester, pas une garantie de performance

Commencez avec les exemples fictifs. Vérifiez les résultats attendus. Passez ensuite à vos propres exports, avec des périodes et des groupes soigneusement définis.

Notre observatoire vous propose un cadre pour poser des questions, comparer vos statistiques et retrouver les preuves. Pour la suite : plus de répétitions, de meilleures références et des avis indépendants.

Observatoire multiagents · Comprendre, comparer et vérifier
