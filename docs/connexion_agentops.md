# Connexion AgentOps facultative

Le SDK AgentOps 0.4.21 exporte un **résumé technique après chaque nouvelle
exécution**, depuis un processus séparé. Ce n'est pas une instrumentation
automatique des prompts, outils ou réponses du modèle. Les restrictions réseau
du worker CrewAI restent actives. Les vingt essais existants ne sont pas exportés
rétroactivement et les résultats historiques restent inchangés.

## Configuration

1. Créer un compte sur https://app.agentops.ai/ et obtenir une clé de projet.
2. Depuis la racine du projet, installer `requirements-agentops.txt`.
3. Exécuter `.\.venv\Scripts\python.exe -m observatoire.connexion_agentops --configurer`.
   La saisie est masquée. La clé reste dans `.local/agentops/connexion.key`,
   fichier local en clair ignoré par Git : ne pas le joindre à la remise.
4. Exécuter `.\.venv\Scripts\python.exe -m observatoire.connexion_agentops --tester`.
   Ce test émet une trace technique sans données réelles ni appel au modèle.
5. Vérifier la réception dans le tableau de bord AgentOps. Le retour local
   `envoye_a_verifier_dashboard` confirme l'authentification, la fin de la file
   et un résultat de transport `SpanExportResult.SUCCESS`. La visibilité
   effective reste à vérifier dans le tableau de bord.

## Périmètre transmis

États, durée mesurée localement, nombres de jetons, configuration T0/T04 et
cinq étapes aux noms fixes. Aucune sortie, aucun titre, CSV, chemin, nom de
personne, secret ou message d'erreur n'est inclus. L'auto-instrumentation et la
collecte d'environnement sont désactivées. Les durées des spans représentent
l'export ; les durées d'exécution sont des attributs explicitement identifiés.

Le dernier état d'envoi est conservé séparément dans
`.local/agentops/dernier_envoi.json`. Un échec AgentOps ne change pas le verdict
local. Supprimer `connexion.key` désactive les prochains envois.

## Validation du 16 octobre 2026

L'interface AgentOps a confirmé « Success! Traces received from your agent. »
après l'envoi d'une trace de test sans appel au modèle. Cette preuve est
conservée dans le complément du rapport, pages 129 et 130. La campagne initiale
de vingt essais reste historiquement sans AgentOps.

Le SDK AgentOps 0.4.21 supposait la présence des attributs internes `_headers`
et `_session`, absents du transport OpenTelemetry 1.45.1. L'adaptateur utilise
désormais le constructeur public `OTLPSpanExporter` et vérifie le résultat de
chaque export. Une régression couvre le cas où `force_flush` retourne vrai
alors que le transport retourne `FAILURE`. Les fichiers installés du SDK ne
sont pas édités. La collecte des bibliothèques et du poste, ainsi que la
transmission des journaux internes, sont neutralisées explicitement avant
l'initialisation, car l'option de refus du SDK ne suffisait pas à tout exclure.

Référence : https://docs.agentops.ai/v2/usage/sdk-reference

## Pilote complet du 16 octobre 2026 à 22 h 54 heure de Montréal

Un pilote CrewAI sur les CSV fictifs de `data/examples`, conservé dans une
base séparée `data/private/pilote_agentops.sqlite`, a terminé les cinq tâches
des quatre rôles en 179,26 secondes. Cinq appels au modèle local et trois
appels d'outils ont été enregistrés. Les six contrôles d'intégration sont vrais.
Ce pilote n'appartient pas à la campagne évaluée et ne reçoit aucune note
humaine implicite. Le SDK a confirmé l'acceptation du résumé technique à cinq
étapes. L'utilisatrice a ensuite confirmé dans le tableau de bord une trace
à 22 h 54, statut OK et six spans : une session et cinq étapes. Les captures
montrent environ 2 ms et zéro appel natif LLM ou outil, car le résumé est créé
après exécution. Ces nombres ne remplacent pas les mesures locales. La suite
complète compte désormais 67 tests réussis.
