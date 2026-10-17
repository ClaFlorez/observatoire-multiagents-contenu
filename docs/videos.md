# Import et exploration des statistiques par vidéo

## Périmètre actuel

Le sélecteur **Type de rapport** distingue **Audience par pays** et **Contenu par vidéo**. Les schémas sont incompatibles et ne sont pas fusionnés. La vue vidéo dispose de sa propre mission CrewAI locale : provenance, comparaison des vues et heures, vérification indépendante et hypothèse éditoriale à tester. Aucun appel IA ne démarre lors du simple chargement ou de la relecture.

L’import vidéo lit uniquement `Table data.csv`. Les fichiers `Chart data.csv` et `Totals.csv` présents dans le nouveau dossier décrivent des playlists et des vidéos ajoutées ; ils ne constituent pas une série quotidienne des vues de chaque contenu.

Les anciens exports par pays existent toujours dans le dossier source `Visualisation_des_donnees/youtube_csv`, extérieur à ce dépôt, et leurs imports sauvegardés restent consultables dans SQLite. Aucun fichier d’origine n’a été déplacé ou remplacé par l’application.

## Constat sur le nouvel export

Le fichier local comporte **88 vidéos**, avec des identifiants distincts et une ligne Total. La période du **17 septembre au 14 octobre 2026** a été confirmée par la capture YouTube Studio fournie par l’utilisatrice. Le CSV ne contient pas cette période : l’import conserve donc une provenance `declaration_utilisateur` et exige une confirmation explicite dans l’interface.

| Mesure | Ligne Total | Somme des valeurs connues | Valeurs vidéo absentes |
|---|---|---|---|
| Vues | 9 737 | 9 737 | 17 |
| Visionnage en heures | 129,1472 | 129,1473 | 17 |
| Impressions de miniature | 13 867 | 13 798 | 0 |

Quatre dates de publication sont absentes ; toutes les durées vidéo sont renseignées. Les cellules vides restent indisponibles. L’égalité de la somme connue et du total ne permet pas de remplacer les 17 vues absentes par zéro.

L’écart de visionnage est de −0,0001 heure entre total et somme connue. Les arrondis peuvent intervenir, sans qu’une cause soit affirmée. L’écart de 69 impressions demeure signalé sans explication attribuée.

## Champs et unités

| Colonne source | Champ interne et unité |
|---|---|
| Content | id, identifiant de vidéo de 11 caractères |
| Video title | titre, texte |
| Video publish time | publication, date ISO ou absence conservée |
| Duration | duree_video_s, secondes |
| Views | vues, nombre de vues ; distinct des vues engagées |
| Watch time (hours) | heures, décimal exact |
| Subscribers | abonnes, entier dont la définition d’origine reste conservée |
| Average view duration | duree_moyenne_s, secondes |
| Thumbnail impressions | impressions, nombre d’impressions |
| Thumbnail click-through rate (%) | ctr_pct, pourcentage |

Le parseur accepte les dates ISO et les noms de mois anglais de l’export, indépendamment de la langue de Windows. La date de publication n’est pas la période statistique : une vidéo plus ancienne peut produire des vues pendant la période étudiée. La durée seule ne détermine pas le format Short.

## Utilisation

Les dossiers locaux sont désormais `youtube_csv/setp-oct` (17 septembre–14 octobre 2026) et `youtube_csv/aout-sept` (20 août–16 septembre 2026). L’orthographe du dossier `setp-oct` est conservée. La vue propose le premier fichier comme chemin par défaut, avec repli vers l’ancien chemin s’il n’existe pas.

Après chargement du rapport courant, ouvrir **Comparer deux périodes — préparation S3**, confirmer les dates du fichier de référence puis cliquer sur **Comparer les deux périodes**. Les deux instantanés sont enregistrés séparément dans SQLite. Aucun appel IA ne démarre lors de la comparaison Python. Le bouton distinct de la section S3 lance ensuite les quatre agents (voir agents_s3.md). Les périodes doivent avoir une longueur égale, être ordonnées sans chevauchement et provenir de fichiers distincts de même origine.

La comparaison distingue les lignes Total du canal, les identifiants communs et les paires connues pour chaque mesure. Les identifiants présents dans un seul fichier ne reçoivent pas un zéro dans l’autre. Les cellules absentes rendent la paire indisponible ; aucune variation relative n’est calculée avec une base nulle. Les filtres du classement ne modifient pas la comparaison.

Recette des exports : 67 vidéos avant et 88 après, 67 identifiants communs et 21 uniquement après ; 50 paires connues pour les vues et les heures. Total canal : vues −2 677 (−21,56 %), heures +54,7599 (+73,61 %). Cohorte appariée connue : vues 12 375 vers 5 682, heures 73,9386 vers 90,9307. Ce sont des observations descriptives, pas des causes démontrées. La mission CrewAI S3 est maintenant connectée ; la campagne évaluée reste à réaliser. Les 43 tests logiciels passent.

1. Choisir **Contenu par vidéo** dans **Type de rapport**.
2. Vérifier le fichier `youtube_csv/Table data.csv` et l’origine réelle ou fictive.
3. Définir et confirmer la période statistique, puis cliquer sur **Charger le rapport par vidéo**.
4. Examiner les avertissements et rapprochements avant le classement.
5. Filtrer par titre ou identifiant et choisir vues, heures ou impressions, puis le nombre maximal de résultats.

Le graphique ne classe que les valeurs connues. Le tableau complet conserve aussi les cellules absentes. Les indicateurs globaux de la ligne Total ne changent pas avec le filtre de recherche. Les moyennes et taux ne sont pas additionnés.

Le rapport affiché reste dans la session Streamlit. Lors du lancement des agents, un instantané est conservé dans la table SQLite imports_videos ; son identité inclut le fichier, la période déclarée et l’origine. Les traces vidéo et géographiques sont sélectionnées séparément. Les CSV et la base réelle restent ignorés par Git.

## Vérification

Le logiciel refuse les colonnes absentes, playlists utilisées comme table vidéo, identifiants dupliqués, valeurs négatives de comptage, fractions de vues et dates invalides. Les tests vérifient aussi la confirmation de période et l’absence du bouton des agents géographiques dans la vue vidéo.

Les 40 tests automatisés du projet passent. Ces tests logiciels ne sont pas les vingt exécutions de campagne du cours.

## Quatre agents connectés

Le pipeline 4 exige une vidéo de référence issue des leaders vérifiés et un indicateur de test (vues ou heures). Un contrôle lexical rejette certaines formulations trompeuses sur les absences ; ce contrôle limité ne comprend pas toutes les contradictions possibles. Le rapport complet reste sauvegardé ; le contexte transmis au coordonnateur résume les contrôles réussis, conserve tous les échecs, mesures et avertissements. La recommandation doit proposer une action éditoriale concrète, distincte d’un audit des valeurs absentes.

Après chargement, descendre à **Quatre agents CrewAI locaux — exécution IA réelle — vidéos** et cliquer sur **Lancer les quatre agents IA locaux — 0 USD API**.

Le coordonnateur cadre la comparaison ; le chercheur appelle `lire_import`, l’analyste appelle `calculer_videos`, puis le vérificateur appelle `verifier_videos`. Ce dernier recalcule les mesures et les deux classements indépendamment de l’analyste. Le coordonnateur reçoit son rapport et produit une synthèse structurée avec une recommandation marquée `hypothese_a_tester`.

Les contrôles comparent les identifiants, valeurs, absences, ordre des trois premières vidéos et champs de la synthèse aux sources. Une synthèse incohérente reste un brouillon non validé. Les différences entre total et valeurs connues restent visibles ; aucune cause, aucun format Short ni gain futur ne sont déduits. La qualité du texte libre nécessite une revue humaine.

Les quatre rôles utilisent réellement Qwen3 4B via Ollama local et CrewAI. Les graphiques de communication, chronologie et circulation des messages relisent les traces enregistrées. Chaque lancement reste un pilote, exclu de la campagne évaluée tant que les scénarios et leur grille ne sont pas définis.

## Recette locale observée

Le pilote réel `52f1a5d7-0e8e-4fdf-afcf-9bf29beb99c9` a terminé en 183,59 secondes : cinq tâches, quatre rôles, trois outils, contrôles numériques et synthèse structurée cohérents. Le leader est YeDXi4z_Cqo avec 2 453 vues et 53,6046 heures. Frais API externes : 0 USD.

La proposition générée porte surtout sur les données manquantes, et non sur une stratégie éditoriale aboutie. Sa mention des vidéos « sans vues ou heures » doit se lire comme valeurs absentes, jamais comme zéros. Le passage des contrôles numériques ne valide pas cette formulation ni un lien entre les absences et l’écart de 0,0001 heure. Une première tentative échouée est conservée ; aucune trace n’a été effacée pour cette recette.

La recette éditoriale du pipeline 4 a aussi révélé une conversion erronée des heures dans le texte libre malgré des champs JSON corrects. Les contrôles exigent désormais le volume horaire exact suivi du mot heures, sans conversion en h/min/s. Une mention telle que « 17 vues et 17 heures absentes » est rejetée : ce sont les valeurs de 17 vidéos qui sont absentes, pas un volume connu de vues ou d’heures. La trace 74d0be47 conserve les contrôles de sa version et ne constitue pas une preuve de qualité éditoriale validée.

Pour éviter un groupe de test inventé depuis les 17 absences, la recommandation est désormais une sélection contrainte parmi des formulations préparées en Python : nouvel angle ou variante de présentation sur un futur contenu inspiré d’un leader vérifié, puis comparaison des vues ou heures sur une période de même longueur. Le modèle choisit une action ; il ne rédige plus librement ce champ. Cette restriction améliore la vérifiabilité mais ne démontre pas que le sujet du leader explique ses résultats, ni que l’action sera efficace.

Recette finale : pilote 3121b4a9, 95,77 secondes, quatre rôles, trois outils et cinq tâches. Le modèle a choisi un nouvel angle pour un futur contenu inspiré de YeDXi4z_Cqo, avec comparaison des vues sur une période de même longueur et sans gain garanti. Une revalidation explicite corrige le faux positif lexical ; les contrôles et l’état initiaux sont conservés. Aucun texte ni compteur d’inférence n’a été modifié. Les contrôles actuels passent ; le score humain de campagne reste non attribué.
