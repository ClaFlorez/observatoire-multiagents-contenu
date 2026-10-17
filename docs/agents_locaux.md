# Première intégration des quatre agents locaux

## Fonctionnement

CrewAI 1.15.28 organise cinq tâches séquentielles confiées à quatre agents : cadrage par le coordonnateur, consultation par le chercheur, calcul par l’analyste, vérification, puis synthèse par le coordonnateur. Chaque tâche reçoit le résultat de la précédente comme contexte. Les communications enregistrées correspondent à ces transmissions de résultats, pas à des conversations autonomes supplémentaires.

Tous les agents utilisent le même modèle Qwen3 4B sur le processeur, successivement. Ils ne nécessitent pas quatre modèles chargés simultanément. La mémoire persistante, la délégation libre et la planification additionnelle sont désactivées pour ce premier pilote.

## Outils effectivement disponibles

- `lire_import` consulte en SQLite l’import sélectionné et retourne sa provenance, les avertissements et les limites.
- `calculer_audience` lit cet import et calcule les volumes, le pays en tête, sa part dans le total et les écarts. Les dénominateurs et l’unité sont explicités.
- `verifier_audience`, ajouté dans la version 2 du pipeline, recalcule indépendamment les contrôles depuis les trois tables et compare les valeurs reçues de l’analyste. Il retourne les contrôles réussis, échoués ou non applicables, un verdict et les réserves.

Les agents doivent demander ces outils. L’adaptateur local fait générer la sélection d’outil par le modèle sous forme de JSON contraint, puis la convertit au protocole de fonctions de CrewAI. CrewAI exécute l’outil Python autorisé. Le résultat exact de l’outil est utilisé comme sortie de tâche avec `result_as_answer=True` ; les chiffres ne sont pas réécrits par le chercheur, l’analyste ou le vérificateur.

Les réponses de cadrage et synthèse sont générées par le modèle dans un format JSON bref. Le vérificateur demande un recalcul déterministe au lieu de reformuler les chiffres. Le préfixe technique `Final Answer:` est ajouté par l’adaptateur pour le parseur CrewAI ; il ne constitue pas un contenu analytique simulé. Aucun raisonnement interne détaillé n’est demandé ou sauvegardé.

## Isolation et budget

Le bouton Streamlit démarre un processus Python distinct. Il retire les variables de clés API de son environnement, désactive python-dotenv, la télémétrie CrewAI et le tracing distant, et travaille dans un dossier local sans `.env`.

Un audit Python refuse les connexions autres que `127.0.0.1:11434`, la résolution de noms externes et la lecture des principaux fichiers de secrets. Le canal interne `socketpair` utilisé par asyncio sous Windows est autorisé explicitement. Ces contrôles sont limités au worker, sans affecter Streamlit ou les autres applications. Ils protègent le chemin d’exécution configuré ; ils ne constituent pas une sandbox universelle pour du code tiers malveillant.

L’adaptateur fixe l’endpoint local, désactive les proxies et les redirections HTTP, impose `think=False` et `num_gpu=0`. Aucun repli OpenAI n’est configuré. Ollama reste lancé avec le cloud désactivé.

Limites du pilote : 512 jetons générés au maximum par appel, contexte de 4 096 jetons, douze appels locaux au maximum et dix minutes pour le processus. Les appels tronqués sont considérés comme échoués. Les dépenses API externes sont nulles ; le temps, la mémoire et l’électricité locaux restent des ressources consommées.

## Traces et contrôles

La table `executions_reelles` est distincte de `demonstrations`. Elle conserve un identifiant stable, le scénario, la provenance des données, la version du framework, les paramètres, les tâches, les appels au modèle, les appels aux outils, les contextes transmis et les erreurs.

Les jetons proviennent des compteurs retournés par Ollama. Une tentative sans compteurs conserve une consommation inconnue ; elle ne devient pas artificiellement gratuite en jetons. Les durées des segments vont du premier appel au retour de la tâche ; la durée globale inclut également le démarrage du framework. Le chargement des modèles est conservé séparément lorsqu’Ollama le rapporte.

Les premiers pilotes vérifiaient les quatre rôles appelés, les deux outils utilisés, les cinq tâches terminées, la cohérence des totaux sources et la présence du pays en tête et de son volume dans la synthèse. Ces contrôles ne remplacent pas la grille de qualité, la vérification humaine des conclusions ou l’analyse sémantique complète des nombres.

Depuis la version 2, le troisième outil de vérification est également exigé. Le contrôle par simple présence de chiffres dans un texte est remplacé par une comparaison des champs structurés de la synthèse : unité, pays, volume, total, écart et verdict source. Le texte doit aussi citer explicitement le code pays et son volume, pour refuser une formulation générique sans constat. Ce dernier contrôle ne constitue pas une analyse sémantique complète. Un échec rend l’exécution `non_validee` ; le texte généré est présenté uniquement comme brouillon non validé.

### Rapport détaillé du vérificateur

Les contrôles comparent total et somme quotidienne, détails par pays dans les deux exports, couverture des dates, bornes quotidiennes et globales, puis chaque mesure reçue de l’analyste aux données sources. La part du pays est vérifiée avec le total global comme dénominateur, avec une tolérance de 0,005 point liée à l’arrondi.

Un écart de couverture entre le total et les pays détaillés reste une réserve si les séries détaillées concordent. Les pourcentages de visionnage supérieurs à 100 % ne sont pas corrigés automatiquement. Un dénominateur nul produit un contrôle non applicable et exige un pourcentage absent, pas un zéro inventé.

Le verdict est `accepte_avec_reserves` lorsque tous les contrôles applicables passent, ou `refuse` dès qu’un contrôle échoue. Le modèle n’attribue pas lui-même ce verdict. La synthèse finale doit le recopier ; même si le modèle rédige un texte affirmatif après un refus, l’application le signale et masque cette conclusion dans un brouillon.

Ces règles vérifient la cohérence numérique. Elles ne démontrent ni la vérité commerciale d’une recommandation ni l’absence de contradiction dans le texte libre. La grille de qualité et la revue humaine restent nécessaires. Les anciennes traces n’ont pas de rapport ajouté rétroactivement : lancer une nouvelle mission pour tester cette version.

Une trace peut être `terminee`, `non_validee` ou `echouee`. Un échec reste visible avec les mesures partielles. Les pilotes portent `eligible_campagne_reelle=false` : il s’agit d’inférences IA réelles, mais pas d’une campagne évaluée déjà validée.

## Utilisation

1. Démarrer le serveur Ollama avec le script du projet, puis Streamlit.
2. Charger les CSV et vérifier leur provenance réelle ou fictive.
3. Ouvrir la section **Quatre agents CrewAI locaux — exécution IA réelle** en bas de page.
4. Cliquer sur **Lancer les quatre agents IA locaux — 0 USD API** et attendre la fin ; prévoir plusieurs minutes sur CPU.
5. Consulter résultat, validation, étapes, appels et relecture. Un lancement ne réalise qu’une mission.

Les données d’audience sont traitées localement. L’import chargé est utilisé sur sa période complète ; les filtres des autres graphiques ne modifient pas le périmètre de la mission.

## Recette réalisée

Deux pilotes ont réussi : exemple fictif en 87,58 secondes (1 897 jetons d’entrée et 160 de sortie), puis exports réels en 65,63 secondes (1 930 d’entrée et 197 de sortie). Les cinq tâches, quatre rôles, deux outils et quatre transmissions de contexte ont été constatés dans chaque trace. Sur les exports réels, la synthèse indique VE, 2 825 vues engagées sur 6 083, soit 46,44 %, et un écart non expliqué de 1 345. Le modèle abrège parfois l’unité en « vues » ; l’interface rappelle qu’il s’agit ici de vues engagées.

Les tentatives de mise au point échouées restent dans la base. Le passage à des réponses JSON contraintes a permis de terminer les tâches sans réponses excessivement longues. Les contrôles automatiques d’intégration ont réussi ; cela ne démontre pas une qualité générale sur les cinq scénarios du cours.

Vingt-sept tests automatisés du logiciel passent, dont sept cas dédiés à la vérification numérique et au respect du verdict. Ils ne constituent pas les vingt exécutions de la campagne IA. La relecture des traces enregistrées ne relance aucun appel au modèle.

Recette du vérificateur renforcé : un nouveau pilote sur les exports réels a terminé en **64,09 secondes**, avec **3 398 jetons d’entrée** et **195 de sortie**. Les trois outils ont été appelés et les **16 contrôles** ont réussi, avec verdict `accepte_avec_reserves`. Les champs de la synthèse correspondent au rapport et son texte cite VE et 2 825 vues engagées. La formulation reste très brève : ces contrôles ne prouvent pas la qualité d’une recommandation éditoriale complète. Les différences de durée entre pilotes ne démontrent pas un gain causal, notamment parce que le modèle peut être déjà chargé.

## Travail restant

Ce pilote couvre une mission géographique. Il ne fournit pas encore les cinq scénarios éditoriaux, les vingt exécutions de campagne, la comparaison de modèles, les six visualisations complètes ni l’intégration AgentOps. L’export par vidéo est maintenant disponible et connecté à une mission distincte. Un modèle local peut produire une formulation erronée malgré des calculs corrects ; la revue des sorties reste indispensable.

## Sources techniques

- [Implémentation d’un BaseLLM personnalisé](https://docs.crewai.com/v1.15.28/en/learn/custom-llm)
- [Sortie d’outil utilisée comme résultat](https://docs.crewai.com/en/learn/force-tool-output-as-result)
- [Désactivation de la télémétrie CrewAI](https://docs.crewai.com/en/telemetry)
- [Génération locale et compteurs Ollama](https://docs.ollama.com/api/generate)

## Mission par vidéo — pipeline 3

Voir [Import et mission vidéo](videos.md). Les instantanés vidéo sont séparés des imports géographiques ; la période déclarée entre dans leur identité. La mission utilise lire_import, calculer_videos et verifier_videos. Les vues et heures restent des unités distinctes des vues engagées. La recommandation est une hypothèse à tester, avec revue humaine nécessaire. Les 40 tests logiciels ne constituent pas une campagne de vingt missions.
