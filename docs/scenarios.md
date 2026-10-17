# Cinq scénarios et critères de campagne

Statut : protocole préparé, campagne non lancée. Missions locales disponibles : [S1, deux classements des trois premières vidéos](agents_s1.md), comparaison vues/heures par vidéo avec hypothèse éditoriale, S3 entre deux périodes, S2 et S4 depuis des paramètres JSON vérifiés. La section « Préparer les scénarios S2 et S4 » permet de choisir explicitement les groupes et la cible et d’exporter les paramètres. Le chargement reste sans inférence ; deux boutons distincts lancent ensuite les quatre agents. Voir [le parcours S2/S4](agents_s2_s4.md). Deuxième configuration et campagne évaluée restent à terminer.

## Sources communes

Utiliser un instantané identifié par SHA-256, origine et période statistique déclarée. Pour le rapport courant : 88 vidéos, période déclarée du 17 septembre au 14 octobre 2026. Ne jamais confondre vues et vues engagées. Une cellule absente reste inconnue. La date de publication ne définit pas la période statistique.

Les scénarios reprennent le protocole de validation existant. Les scénarios S2 à S4 exigent des paramètres ou données supplémentaires : aucune séparation de formats ou seconde période n’est inventée pour remplir la grille.

| ID | Consigne à transmettre aux quatre rôles | Préparation et disponibilité | Preuves attendues |
|---|---|---|---|
| S1 | Comparer les trois premières vidéos en vues et en heures ; distinguer les deux classements et les absences. | Export courant disponible. Tableaux, graphiques, mission locale dédiée et vérification indépendante connectés. | Identifiants, valeurs et unités exacts, ordre stable des ex æquo, nombres de valeurs absentes ; aucune causalité. |
| S2 | Comparer deux groupes de vidéos définis explicitement, selon vues et heures. | Fixer deux listes d’identifiants distinctes avant les essais. Une comparaison de formats exige des étiquettes vérifiées ; aucune déduction Short depuis le titre ou la durée. | Effectif de chaque groupe, effectif connu par mesure, médiane et somme connues, limites de comparabilité. Le groupe le plus grand ne devient pas automatiquement le plus performant. |
| S3 | Comparer deux périodes de même longueur pour un même ensemble de vidéos. | Deux exports disponibles : aout-sept et setp-oct. Comparaison Python et mission CrewAI S3 connectées avec trois outils et vérification indépendante. | Dates et longueurs égales, intersection des identifiants, différences absolues ; variation relative indisponible si base nulle ou absente. Aucune cause attribuée. |
| S4 | Décrire un contenu en dessous d’un groupe comparable, sans inventer pourquoi. | Choisir à l’avance un identifiant cible, un groupe de référence explicite et une mesure. Vérifier qu’ils ont des valeurs connues. | Valeur cible, médiane connue du groupe, taille du groupe, écart ; pas de qualification universelle d’échec ni explication causale. |
| S5 | Proposer une seule action éditoriale à tester, à partir des classements vérifiés. | Export courant disponible ; nouveau pilote de synthèse contrôlée. La validation éditoriale reste humaine. | Vidéo de référence présente dans les sources, fait chiffré, action concrète, vues ou heures comme indicateur et période comparable. Absences citées comme limites, jamais comme cause. Aucun gain promis. |

## Passage commun des quatre rôles

1. Coordonnateur : reformuler la mission et ses paramètres, ou constater une donnée indispensable absente.
2. Chercheur : lire l’instantané et transmettre sa provenance, les unités et les limites.
3. Analyste : appeler un outil de calcul adapté au scénario, avec résultat reproductible.
4. Vérificateur : recalculer indépendamment les résultats et signaler les écarts, sans remplacer un refus par une approbation textuelle.
5. Coordonnateur : produire une conclusion appuyée sur le rapport, ou une abstention explicite si la mission est impossible.

Un refus justifié pour données insuffisantes est un comportement correct, mais ne remplace pas une campagne comparative complète sur les cinq scénarios préparés.

## Grille humaine à remplir après chaque exécution

| Critère | 0 | 1 | 2 |
|---|---|---|---|
| Exactitude numérique | Valeur, unité ou classement faux | Résultat incomplet | Toutes les valeurs citées concordent avec les calculs indépendants |
| Traçabilité | Aucune preuve | Source ou identifiant partiel | Instantané, outils, identifiants et mesures permettent de reproduire la conclusion |
| Respect de la mission | Hors sujet | Réponse partielle ou action vague | Comparaison demandée ou action testable précise, adaptée au scénario |
| Limites | Cause inventée, absence assimilée à zéro ou gain promis | Réserves génériques | Absences, comparabilité et limites pertinentes explicites |

Seuil : au moins 6/8, avec exactitude et traçabilité à 2/2 et aucune erreur critique. Enregistrer les quatre notes, la justification et l’évaluateur. Ne jamais convertir automatiquement un verdict numérique accepté en score éditorial de 8/8.

## Plan des vingt essais

Le registre de campagne prépare cinq scénarios × deux configurations locales identifiées × deux répétitions. Qwen3 4B est utilisé avec températures 0 et 0,4 ; ce sont deux configurations du même modèle, pas deux modèles. Les paramètres, graines appariées, ordre alterné et preuves sont détaillés dans [le protocole de campagne](campagne.md). Aucun fournisseur payant n’est nécessaire.

Fixer les données, groupes, cible et consignes avant les essais. Alterner l’ordre des configurations ; conserver échecs, refus, versions, paramètres, durées, compteurs réels et avis humain. Distinguer temps de chargement et génération ; ne pas conclure à un gain de vitesse sur deux pilotes de consignes différentes. Les pilotes conservés restent exclus du compte des vingt essais.
