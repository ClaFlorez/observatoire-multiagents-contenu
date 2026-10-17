# Campagne expérimentale — cinq scénarios et vingt essais

## Portée

L’énoncé exige au moins vingt exécutions sur au moins cinq scénarios. Le protocole retenu est S1 à S5 × deux configurations × deux répétitions. **T0** et **T04** utilisent le même Qwen3 4B local avec températures 0 et 0,4 ; ce n’est pas une comparaison de deux modèles. Même contexte 4096, CPU, plafond 512 jetons générés par appel, douze appels et dix minutes par workflow. Les graines 4101 et 4102 sont partagées par les deux configurations d’une même répétition.

Les tâches, données et formulations restent identiques au sein d’un scénario. L’ordre des configurations alterne selon scénario et répétition. Le cache et le chargement peuvent varier : deux répétitions ne permettent pas d’attribuer causalement une différence de vitesse à la température. Les schémas contraignent fortement les réponses et les synthèses factuelles sont préparées en Python ; cette expérience porte sur le workflow instrumenté, pas sur une aptitude éditoriale générale du modèle.

## Préparation et lancement

Dans **Contenu par vidéo**, la section **Campagne évaluée — vingt essais à préparer et noter** se trouve en bas de page. Elle demande le JSON S2/S4 enregistré, le CSV précédent pour S3, ses dates et une confirmation des paramètres. **Figer le plan** sauvegarde les vingt emplacements sans inférence. Refaire le même gel réutilise le plan ; il ne crée pas un deuxième lot.

Le plan lie les instantanés, périodes, groupes, cible, justifications, configurations, empreinte SHA-256 du code Python, version Ollama et empreinte du modèle. Le lancement refuse une dérive du code ou du runtime. Les fichiers de travail n’ont donc pas à être modifiés au milieu de cette campagne. S4 reste explicitement exploratoire (sujets différents, référence unique) ; un succès numérique ne prouve pas la comparabilité.

**Exécuter le prochain essai de campagne** prend le prochain emplacement disponible. L’identifiant est attribué avant le lancement et réutilisé dans la trace. Une transaction SQLite empêche deux prises simultanées ; un identifiant déjà exécuté n’est jamais relancé. Une fin de worker non répercutée peut être synchronisée depuis sa trace avec le bouton dédié, sans réexécution. Une trace encore en cours ou une interruption non résolue n’est pas automatiquement remplacée.

Les essais réels utilisent `type=campagne_a_evaluer`, un `campagne_id`, la configuration, la répétition et les paramètres réels. Les anciens pilotes restent hors de ce plan. Les échecs restent visibles. Un incident sans trace n’est pas une exécution exploitable ; prévoir des essais supplémentaires documentés si le total requis n’est pas atteint. Le logiciel n’annonce pas la conformité au cours sur la seule base de vingt emplacements traités.

Un lancement séquentiel du plan enregistré est aussi possible depuis la racine du projet :

```powershell
& '.\.venv\Scripts\python.exe' -m observatoire.campagne --database '.\data\private\observatoire.sqlite' --id IDENTIFIANT_COMPLET_DU_PLAN --limite 20
```

Cette commande exécute les emplacements encore en attente, sans reprendre ceux déjà traités. Elle s’arrête sur incident de lancement. Ne pas lancer une deuxième session concurrente. Elle n’attribue aucune note humaine.

## Évaluation et graphiques

Chaque trace est consultable dans la section de campagne. Les notes ne sont pas présélectionnées : exactitude, traçabilité, respect de la mission et limites, de 0 à 2. L’évaluateur renseigne son nom, une justification et l’existence d’une erreur critique. Chaque enregistrement ajoute une version à l’historique ; le tableau affiche la dernière évaluation. Les contrôles numériques ne produisent jamais un 8/8 automatique.

La réussite de qualité exige au moins 6/8, exactitude et traçabilité à 2, aucune erreur critique. Elle doit être interprétée avec l’état réel du workflow et les contrôles d’intégration, pas comme une approbation du projet ou du professeur. `eligible_campagne_reelle` reste une précaution sur la trace brute ; le manifeste, les résultats exploitables et les avis humains apportent les preuves à examiner.

Filtres : scénario, état, configuration et agent pour les durées. Le tableau conserve les incidents, identifiants et notes absentes. Le graphique compare les durées mesurées ; la carte thermique affiche uniquement les moyennes des évaluations humaines enregistrées. Case vide = non noté. Le manifeste exportable contient le plan, les emplacements et les dernières évaluations. Les traces détaillées restent dans SQLite locale.

Frais d’API externe : 0 USD. Le temps, l’électricité et le matériel ne sont pas évalués en dollars. Aucun pilote n’est recyclé dans les vingt essais.
