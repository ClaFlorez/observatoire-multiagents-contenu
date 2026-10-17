# Dictionnaire des programmes et des processus

## Les programmes et leur rôle

Comprendre qui fait quoi dans notre observatoire et à quel moment chaque élément intervient.

### Le parcours des données

YouTube Studio → export CSV → import et contrôles Python → calculs et scénarios S1 à S5.

La personne choisit et confirme les fichiers, les périodes, les groupes et la cible dans Streamlit. Les données manquantes restent signalées.

### Le parcours de l’intelligence artificielle

Bouton dans Streamlit → processus Python isolé → CrewAI → tâches des agents → API locale Ollama → modèle Qwen3 → réponse structurée.

Les outils autorisés réalisent les lectures, calculs et vérifications en Python. Qwen3 intervient dans le workflow, mais ne remplace pas les calculs de référence.

### Le parcours des résultats

Traces locales → SQLite → lecture par Streamlit → graphiques Plotly et consultation du résultat.

Après l’exécution : un processus séparé transmet un résumé technique autorisé vers AgentOps, si la connexion est configurée.

La notation humaine est saisie séparément. Un contrôle automatique réussi ne crée aucune note humaine.

### Comment lire ce dictionnaire

Programme : logiciel exécuté, par exemple Ollama. Langage : manière d’écrire le code, par exemple Python. Bibliothèque : code utilisé par Python, par exemple CrewAI.

Modèle : paramètres appris qui produisent les réponses, ici Qwen3. Format : organisation d’un fichier ou d’un message, par exemple CSV ou JSON.

Versions : environnement testé du projet, vérifié le 17 octobre 2026. Les noms des quatre agents désignent des rôles configurés, pas quatre logiciels séparés.

## Le socle qui exécute le projet

Ces éléments servent à installer, lancer et faire fonctionner le code sur Windows.

### Windows et PowerShell

Windows : système d’exploitation du poste ; il gère les fichiers, les processus et les ressources. Diagnostic conservé : Windows 10 Pro 22H2, build 19045.

PowerShell : terminal dans lequel nous exécutons les commandes d’installation, de lancement et de test. Il lance Python et le serveur Ollama ; il ne réalise pas l’analyse à leur place.

Interaction : personne → commande PowerShell → programme demandé. La version précise de PowerShell n’a pas été inventoriée dans cette livraison.

### Python 3.12.14

Nature : langage et interpréteur. Fonction : exécuter app.py et les modules observatoire, lire les CSV, calculer les indicateurs, orchestrer les appels et enregistrer les traces.

Intervient pendant l’import, les scénarios, les agents, les contrôles, le stockage et les tests. Les outils métier sont écrits en Python.

Exemple : Python calcule une médiane ; Qwen3 n’est pas utilisé comme calculatrice de référence.

### venv et pip

venv : module Python qui crée le dossier .venv avec un environnement propre au projet. Ce dossier n’est pas inclus dans le ZIP.

pip : outil qui installe les bibliothèques déclarées dans requirements.txt ; requirements-agentops.txt ajoute le SDK facultatif AgentOps.

Interaction : PowerShell lance le Python de .venv ; ce Python utilise les bibliothèques installées par pip. Les dépendances directes sont fixées, pas toutes les dépendances transitives.

### Navigateur web

Le navigateur affiche l’interface Streamlit à http://127.0.0.1:8501. Il permet de choisir les paramètres, cliquer sur les boutons et lire les graphiques.

L’interface est web, mais le serveur de notre application fonctionne sur le poste. Ouvrir la page n’équivaut pas à lancer une nouvelle exécution IA.

## L’équipe qui réalise les tâches IA

Quatre rôles CrewAI utilisent le même modèle local ; ils ne nécessitent pas quatre modèles chargés.

### CrewAI 1.15.28

Nature : bibliothèque Python d’orchestration. Elle définit et enchaîne agents, tâches et outils.

Dans notre processus : Coordonnateur pour le cadrage → Chercheur → Analyste → Vérificateur → Coordonnateur pour la synthèse. Quatre rôles, cinq tâches.

CrewAI reçoit la mission préparée en Python et utilise notre adaptateur local pour solliciter Qwen3 via Ollama.

### Ollama portable 0.40.5

Nature : moteur et serveur local de modèles. Il charge qwen3:4b et répond aux requêtes de l’application sur 127.0.0.1:11434.

Interaction : adaptateur Python → requête HTTP locale → Ollama → Qwen3 → réponse et compteurs retournés à Python.

Notre configuration utilise le CPU, un modèle chargé, une requête parallèle et le cloud désactivé. Les téléchargements initiaux nécessitent Internet.

### Qwen3 4B et les instructions

Nature : modèle de langage, appelé avec le tag qwen3:4b et une quantification Q4_K_M. Il produit des réponses à partir des instructions et données autorisées.

Les rôles et les tâches donnent des instructions différentes au même modèle. Coordonnateur n’est donc pas le nom d’un autre modèle.

Les sorties sont fortement contraintes : l’adaptateur transforme notamment une sélection d’outil en appel autorisé ; des schémas et outils Python encadrent le résultat.

### Les outils et le vérificateur

Lecture : récupérer les données et leur provenance. Calcul : obtenir des mesures exactes. Vérification indépendante : contrôler les chiffres et les limites.

Le rôle Vérificateur fait partie de CrewAI ; les règles de vérification sont aussi du code Python. La personne reste responsable de relire et noter le résultat.

Une réponse bien structurée ou un contrôle réussi ne prouve ni une causalité ni la qualité générale de toutes les recommandations.

## Afficher conserver et observer

Ces composants montrent les résultats et permettent de retrouver ce qui s’est passé.

### Streamlit 1.66.0

Nature : bibliothèque Python pour l’interface. app.py assemble les vues de l’application.

Avant l’analyse : chemins des fichiers, périodes, groupes, cible et lancement. Après l’analyse : résultat, filtres, relecture et formulaire d’évaluation humaine.

Streamlit appelle notre logique Python et lit les traces locales ; le déplacement du curseur de relecture ne relance pas les agents.

### Plotly 7.1.0

Nature : bibliothèque de graphiques interactifs. Elle représente les statistiques et les traces sélectionnées dans Streamlit.

Intervient après les calculs ou pendant la consultation des exécutions : barres, graphe des rôles, chronologie, Sankey et carte thermique.

Survoler ou filtrer aide à lire les résultats ; un graphique ne constitue pas une preuve automatique de la cause d’une différence.

### SQLite 3.53.1

Nature : moteur de base de données embarqué accessible par le module Python sqlite3. Notre code enregistre et relit les traces, résultats et évaluations.

Interaction : Python → fichier de base local → Python → interface Streamlit. Aucun serveur SQLite séparé n’est nécessaire.

La base privée contenant la campagne historique n’est pas livrée. Une installation neuve ne retrouve pas automatiquement ses vingt exécutions.

### AgentOps SDK 0.4.21 et tableau de bord

Nature : SDK Python et service distant d’observabilité. Dans notre intégration, il reçoit un résumé de métadonnées après l’exécution, depuis un processus séparé.

Un pilote complet peut produire six spans : une session et cinq étapes. Les quelques millisecondes affichées mesurent le résumé exporté, pas le travail réel de plusieurs minutes.

LLM Calls et Tool Calls restent à zéro car nous ne les instrumentons pas comme événements natifs. Le détail local demeure dans SQLite. Les vingt essais historiques ne sont pas réinstrumentés rétroactivement.

## Les fichiers et les outils de livraison

Distinguer les données, les formats et les logiciels qui organisent ou distribuent le travail.

### YouTube Studio CSV et JSON

YouTube Studio : point de départ des exports statistiques. Notre application lit les fichiers exportés et ne modifie pas le compte YouTube.

CSV : format de tableau, pas un programme. Il contient les mesures par vidéo ou par pays. Les périodes statistiques doivent être confirmées séparément.

JSON : format structuré pour les paramètres S2/S4, les manifestes et des échanges internes. Il permet de conserver des sélections explicites et leur provenance.

### Git et GitHub

Git : historique des versions du code et de la documentation. Il permet de conserver un état et de retrouver les modifications.

GitHub : hébergement distant du dépôt privé. Il reçoit les fichiers autorisés après commit et push ; il n’exécute pas automatiquement notre application sur le poste du professeur.

Le fichier .gitignore exclut notamment les environnements, clés, données réelles et bases privées. Un fichier déjà suivi demande une gestion spécifique.

### ZIP DOCX PPTX et Markdown

ZIP : archive pour transporter les sources et livrables ; les dépendances et le modèle doivent être installés sur le nouveau poste. Ce n’est pas un conteneur.

DOCX : rapport et guides modifiables dans un traitement de texte compatible. PPTX : présentation. Markdown (.md) : documentation lisible dans GitHub et un éditeur.

Le manifeste SHA-256 du ZIP sert à contrôler l’intégrité des fichiers. Une empreinte identique ne prouve pas, à elle seule, la qualité de l’analyse.

### Asana Docker et autres outils évoqués

Asana : gestion des tâches humaines, responsables et échéances. Il a été exploré, mais n’est pas connecté au pipeline du TP. Il n’analyse pas nos CSV à la place des agents.

Docker : conteneurisation évoquée pour faciliter la reproduction ; aucun conteneur n’est fourni dans notre livraison actuelle.

ChatGPT et Codex ont servi d’assistance à la conception, au développement et à la documentation. Ils ne sont pas le modèle appelé par notre workflow local.

## Retrouver chaque processus dans le code

Lire de gauche à droite : entrée → traitement → sortie. Les chemins ci-dessous sont relatifs à la racine du projet.

### Importer et préparer

app.py et observatoire/vue_videos.py : interface et choix du rapport. observatoire/import_videos.py : import et contrôles des tableaux vidéo.

observatoire/analyse_videos.py et scenarios_groupes.py : calculs et sélections. comparaison_periodes.py : comparaison entre les deux fenêtres.

Sortie : données contrôlées, provenance, résultats de référence et mission préparée pour le scénario.

### Exécuter et conserver

observatoire/lancement_local.py : lancement du processus isolé. execution_locale.py : CrewAI, appels locaux, outils et étapes. securite_locale.py : restrictions du worker.

observatoire/configurations.py : paramètres T0/T04. campagne.py : plan figé et progression des essais. stockage.py : persistance SQLite.

Sortie : trace de l’exécution avec résultats, durées, jetons, outils, état et erreurs éventuelles.

### Consulter et transmettre

Les modules vue_*.py affichent les résultats et les traces dans Streamlit avec Plotly. vue_campagne.py présente aussi les indicateurs et l’évaluation humaine.

observatoire/connexion_agentops.py : configuration de la clé, test et export du résumé autorisé après exécution.

tests/ : vérifications automatisées avec unittest et les outils de test Streamlit. La suite contient 67 tests ; elle ne remplace pas l’évaluation humaine.

### Sources et vérification

Preuves du projet : requirements.txt ; requirements-agentops.txt ; docs/agents_locaux.md ; docs/campagne.md ; docs/connexion_agentops.md ; guide pas à pas, pages 12 à 14.

Documentation officielle : docs.python.org/3.12/ ; docs.crewai.com ; docs.ollama.com ; ollama.com/library/qwen3:4b.

Interface et observation : docs.streamlit.io ; plotly.com/python/ ; docs.agentops.ai. Les fonctions décrites ici correspondent à notre code, pas à toutes les possibilités de ces produits.
