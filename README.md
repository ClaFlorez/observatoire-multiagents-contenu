# Observatoire multiagents de contenu numérique

Projet individuel du cours **420-VD2-ID — Visualisation et interprétation des données 2**, enseignant **Haythem Rehouma**. Sujet proposé : **A8 — Observatoire de performance du contenu numérique**.

L’application doit analyser des statistiques YouTube et permettre d’observer comment quatre agents collaborent, consomment des ressources et produisent des recommandations vérifiées. Elle vise les créateurs de contenu qui souhaitent préparer leurs prochaines décisions éditoriales à partir de mesures.

## Période de réalisation

Le projet a été réalisé sur trois jours calendaires, du **15 au 17 octobre 2026**. Le temps de travail en heures n’a pas été comptabilisé. Cette période ne correspond pas à trois jours de travail continu ni à la seule durée des exécutions IA.

## État du projet

**État au 16 octobre 2026 : campagne réalisée et évaluée.** Vingt exécutions sur cinq scénarios et vingt évaluations sont conservées localement. Dix-neuf essais sont automatiquement validés ; un refus lexical reste documenté. Les vues comprennent graphe, timeline, Sankey, comparaisons, carte thermique et indicateurs de campagne. Les 67 tests locaux passent. La connexion AgentOps est vérifiée sur un pilote fictif séparé : résumé après exécution avec une session et cinq étapes, sans instrumentation native LLM. Voir [la connexion et ses limites](docs/connexion_agentops.md).

Les notes ont été proposées avec assistance IA puis revues et saisies par l'étudiante. Elles ne constituent pas une évaluation indépendante en aveugle. Le rapport et la présentation distinguent les résultats mesurés des limites du protocole.

## Budget actuel et démonstration locale

Le budget autorisé est de **0 USD de frais API externes**. Le prototype ne lit pas `.env` et ne construit aucun client OpenAI. La simulation n’appelle aucun modèle ; un essai local distinct peut être lancé explicitement avec Ollama. La présence d’une clé locale ne constitue pas une autorisation de dépense. Aucun fournisseur gratuit ou crédit promotionnel n’est supposé disponible.

Après avoir chargé les CSV, descendre à **Laboratoire local des quatre rôles — simulation** et cliquer sur **Simuler les quatre rôles sans API**. Deux missions prédéfinies sont proposées : concentration géographique et évolution quotidienne. Le coordonnateur cadre la mission, le chercheur consulte l’import local, l’analyste calcule et le vérificateur applique des règles Python. Le coordonnateur assemble ensuite une synthèse prédéfinie.

Les traces sont enregistrées dans une table `demonstrations` distincte, avec `mode=simulation` et `eligible_campagne_reelle=false`. Les temps sont ceux des fonctions Python locales, les jetons et appels de modèles sont nuls. Les ressources matérielles locales ne sont pas chiffrées. Les filtres scénario, état et rôle et le curseur de relecture permettent d’examiner ces traces, sans relancer une simulation.

Ces démonstrations ne comptent jamais parmi les vingt exécutions réelles exigées. L’essai local et les pilotes CrewAI sont séparés. Les scénarios d’audience proposés ici ne remplacent pas les cinq scénarios éditoriaux de la campagne.

### Essai réel du modèle local

Sur ce poste, Ollama portable et Qwen3 4B sont installés dans `.local/`, exclu de Git. La configuration désactive le cloud et utilise le CPU sans modifier le pilote NVIDIA. L’installation n’est pas transportée par un clone Git : voir le [diagnostic et la procédure locale](docs/modele_local.md).

Pour redémarrer le moteur, depuis la racine du projet dans un terminal distinct :

```powershell
& ".\scripts\demarrer_ollama_local.ps1"
```

Après démarrage de Streamlit et chargement des CSV, ouvrir en bas de page **Premier essai IA réel sur ce poste — sans API payante**, puis cliquer sur **Tester le modèle local avec des données fictives**. Le test utilise uniquement CA=30 et FR=5, sans envoyer les CSV au modèle. Aucun appel n’est effectué au simple chargement de la page.

Le test est aussi accessible en ligne de commande :

```powershell
& ".\.venv\Scripts\python.exe" -m observatoire.essai_local
```

Cet essai vérifie une inférence et une sortie JSON ; il ne représente pas une exécution des quatre agents. Le coût API est nul, mais l’électricité et les ressources locales ne sont pas chiffrées.

### Quatre agents CrewAI réels

Après chargement des données, cliquer sur **Lancer les quatre agents IA locaux — 0 USD API** dans la section **Quatre agents CrewAI locaux — exécution IA réelle**. Prévoir plusieurs minutes sur CPU. Le chercheur consulte l’import SQLite, l’analyste appelle le calcul Python et les résultats sont transmis au vérificateur puis au coordonnateur.

Les traces, compteurs, outils, erreurs et résultats restent dans `executions_reelles`, séparée de `demonstrations`. Le worker ne lit pas `.env` et refuse les connexions externes ; aucun repli payant n’est configuré. Le graphe, la timeline, le Sankey et la relecture utilisent les traces du pilote choisi sans relancer le modèle.

La version 2 ajoute un troisième outil, `verifier_audience`. La section **Rapport du vérificateur** montre contrôles réussis, échoués ou non applicables, mesures attendues et observées et réserves. Le coordonnateur retourne aussi des champs numériques structurés ; ils sont comparés au rapport avant validation. Une incohérence affiche la synthèse comme brouillon non validé. Les anciennes traces restent inchangées et n’affichent pas ce nouveau rapport.

Deux pilotes de version 1 ont réussi les contrôles minimaux d’intégration : **87,58 s** sur exemple fictif (1 897 jetons d’entrée et 160 de sortie), puis **65,63 s** sur les exports réels (1 930 jetons d’entrée et 197 de sortie). Chacun comporte cinq tâches, quatre rôles, deux outils et quatre transmissions de contexte. Les essais de mise au point échoués restent conservés. Ces pilotes ne sont pas automatiquement comptés comme campagne conforme : revue de qualité et scénarios éditoriaux restent nécessaires.

Le sujet et la réalisation individuelle doivent être confirmés avec l’enseignant : l’énoncé prévoit initialement une équipe de deux. Le dépôt est destiné à rester privé au départ ; sa visibilité et l’accès du professeur doivent être vérifiés dans GitHub. L’invitation du professeur est prévue à la fin.

## Documentation

- [Architecture et flux](docs/architecture.md)
- [Données et règles de calcul](docs/donnees.md)
- [Validation et protocole expérimental](docs/validation.md)
- [Annexe sur les futures API](docs/annexe_api.md)
- [Faisabilité du modèle IA local](docs/modele_local.md)
- [Fonctionnement des quatre agents locaux](docs/agents_locaux.md)
- [Import et exploration par vidéo](docs/videos.md)
- [Cinq scénarios et grille de campagne](docs/scenarios.md)
- [Mission S3 avec quatre agents locaux](docs/agents_s3.md)

Les diagrammes utilisent Mermaid et sont lisibles directement sur GitHub.

## Choix techniques

| Fonction | Choix |
|---|---|
| Agents et orchestration | CrewAI |
| Observabilité technique | AgentOps |
| Interface locale | Streamlit |
| Graphiques | Plotly |
| Calculs | Python standard, Decimal et statistics |
| Stockage des traces | SQLite |

L’application originale doit montrer six visualisations et au moins trois filtres. AgentOps complète la vérification des traces ; il ne remplace pas ce tableau de bord.

## Données et confidentialité

Deux schémas sont maintenant disponibles : les anciens exports d’audience par pays et une nouvelle table de 88 vidéos. Choisir **Contenu par vidéo** dans **Type de rapport** pour charger cette table, confirmer sa période et explorer les vues, heures et impressions. Les quatre agents locaux sont aussi connectés aux vidéos : comparaison vues/heures, vérification numérique et hypothèse éditoriale à tester (voir docs/videos.md). Les CSV réels, bases locales, clés et jetons d’autorisation restent exclus du dépôt. Les exemples fictifs d’audience sont séparés des données réelles.

Les essais fictifs servent au développement et restent exclus de la campagne évaluée de vingt exécutions sur les exports réels.

## Installation et lancement

Le contrôle des CSV est exécutable sans dépendance externe, avec Python 3.12.14 testé sous Windows. L’interface nécessite Streamlit et Plotly ; leurs versions directes sont fixées dans `requirements.txt`.

Depuis la racine du dépôt, avec un interprète Python fonctionnel :

```powershell
python -m observatoire.import_youtube --source data/examples --origine fictive
python -m unittest discover -s tests -v
```

Pour les données réelles, remplacer la source par le dossier local des trois exports et utiliser `--origine reelle`. Le programme affiche un bilan, sans écrire de fichier ni modifier les sources. `--origine` est une déclaration explicite de provenance, pas une détection automatique. Un format invalide provoque un refus et un code de sortie 2 ; un écart statistique produit un avertissement sans correction arbitraire.

Sur le poste de développement, les alias Python Microsoft Store ne fonctionnent pas dans la session actuelle. Les essais ont donc été réalisés avec l’interprète fourni par Codex. Exemple local complet :

```powershell
Set-Location "C:\Users\H0PPR202\Documents\ChatGPT\TP_Visualisation_des_donnees"
& "C:\Users\H0PPR202\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -m observatoire.import_youtube --source data/examples --origine fictive
```

Ce chemin est propre à ce poste. L’environnement local `.venv` peut être créé avec cet interprète ou avec un Python 3.12 autonome fonctionnel. Depuis la racine du dépôt :

```powershell
python -m venv .venv
& ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt
& ".\.venv\Scripts\python.exe" -m streamlit run app.py
```

Ouvrir `http://127.0.0.1:8501` dans le navigateur. Les exemples fictifs sont sélectionnés au départ : cliquer sur **Charger et vérifier**. Pour les données réelles, choisir leur dossier et déclarer l’origine `reelle`. La sauvegarde est explicite et se fait dans `data/private/observatoire.sqlite`, ignoré par Git. Les imports peuvent être rechargés depuis la barre latérale ; ce ne sont pas des exécutions multiagents.

Les filtres pays et période concernent les séries quotidiennes. Le tableau agrégé par pays conserve la période complète et porte un avertissement explicite. Les données restent locales ; aucune requête vers un modèle IA ou vers YouTube n’est effectuée.

Pour exécuter les tests, y compris l’interface :

```powershell
& ".\.venv\Scripts\python.exe" -m unittest discover -s tests -v
```

Une installation sur un poste Windows vierge reste à vérifier ; le runtime et le modèle Ollama ne sont pas inclus dans le paquet. Voir docs/modele_local.md et docs/connexion_agentops.md.

## Étapes de réalisation

1. Confirmer le sujet et le travail individuel ; obtenir l’export par vidéo.
2. Implémenter l’import, les calculs et le stockage avec un exemple fictif.
3. Intégrer les quatre agents, deux outils et la collecte des traces.
4. Construire les six visualisations et les interactions.
5. Choisir les modèles et le budget ; réaliser au moins vingt exécutions sur cinq scénarios.
6. Analyser les résultats, rédiger le rapport et préparer la démonstration de dix à douze minutes.

## Missions S2 et S4 connectées

Dans la vue vidéo, charger le JSON des paramètres sauvegardés puis utiliser les boutons distincts S2/S4. La signature du CSV, sa période et les identifiants sont vérifiés avant tout appel IA. Les calculs du JSON sont recalculés ; le vérificateur contrôle indépendamment médianes, sommes et effectifs. Voir [le parcours et les limites](docs/agents_s2_s4.md). Les synthèses sont encadrées par un schéma avec formulations Python, pas une analyse éditoriale libre. Les pilotes restent exclus des vingt essais évalués.

## Référentiel

L’énoncé source est intitulé *Projet intégrateur — Observatoire interactif d’un système multiagents IA*. Une copie Word locale peut accompagner le travail ; son inclusion dans GitHub devra être décidée séparément. La documentation reprend ses exigences ; elle ne constitue pas une preuve de leur réalisation.

Auteur : **ClaFlorez**. L’identité visuelle CLAUD·IA utilisera le logo fourni sans modifier son point distinctif. Aucun fichier de logo n’est encore copié dans le dépôt.

## Livraison locale

Le paquet de remise contient le code, les tests, des CSV fictifs, le rapport et la présentation. Il exclut les clés, journaux, environnements, modèles et bases réelles. Les preuves de la campagne se trouvent dans le rapport ; la base privée complète n’est pas distribuée automatiquement. Voir VERIFICATION_REMISE.md pour les contrôles et réserves.
# Guide didactique et livraison

Commencer par [le guide pas à pas en français](docs/guide_didactique/Guide_pas_a_pas_Observatoire.docx) : 14 pages avec installation Windows, choix des vidéos, résultats attendus, versions logicielles, spécifications techniques et références officielles.

Le paquet complet est disponible dans `livraison/Observatoire_multiagents_remise_2026-10-17_avec_guide.zip`. Le rapport et la présentation sont dans `docs/rapport_projet/`. Les CSV réels, les bases privées, les clés et le modèle téléchargé sont exclus du dépôt et du paquet.

Voir aussi [le dictionnaire des programmes et de leurs interactions](docs/dictionnaire_programmes.md), avec sa [version Word illustrée en six pages](docs/guide_didactique/Dictionnaire_programmes_et_processus.docx).
