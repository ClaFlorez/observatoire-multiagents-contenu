# Données et règles de calcul

## Inventaire vérifié

Les trois fichiers sources ont été lus intégralement le **15 octobre 2026**. Leur emplacement local est `C:\Users\H0PPR202\Documents\ChatGPT\Visualisation_des_donnees\youtube_csv`. Ils ne sont pas copiés dans le dépôt.

| Fichier | Granularité | Lignes de données |
|---|---|---|
| Chart data.csv | Date et pays, vues engagées | 280 |
| Table data.csv | Pays, statistiques agrégées ; une ligne Total | 11 |
| Totals.csv | Date, total des vues engagées | 28 |

La série quotidienne couvre le **17 septembre au 14 octobre 2026**, inclusivement. Dix codes pays sont présents : AR, CA, CO, EC, ES, IN, PE, US, UY et VE.

## Dictionnaire des exports actuels

| Colonne source | Sens conservé | Type et unité internes |
|---|---|---|
| Date | Date statistique de l’export | Date sans heure ; ne pas inventer un fuseau |
| Geography | Code pays ou ligne Total | Texte ; Total stocké séparément |
| Engaged views | Mesure nommée vues engagées dans l’export | Entier, vues engagées |
| Subscribers | Mesure d’abonnés de l’export | Entier ; signification exacte à confirmer avant interprétation |
| Average percentage viewed (%) | Pourcentage moyen regardé | Nombre décimal, pour cent |
| Playlist watch time (hours) | Durée de visionnage des playlists | Nombre décimal, heures ; valeur absente possible |
| Card clicks | Clics sur les fiches | Entier, clics |
| Views | Vues | Entier, vues ; distinct des vues engagées |
| Watch time (hours) | Durée de visionnage | Nombre décimal, heures |
| Average view duration | Durée moyenne de visionnage | Texte H:MM:SS converti en secondes |

Les CSV utilisent des virgules comme séparateurs et des points décimaux. Le format d’affichage français sera appliqué après conversion, sans changer les valeurs sources.

## Contrôles constatés et limites

La somme des vues engagées détaillées est **4 738** dans Chart data.csv comme dans les dix pays de Table data.csv. La somme de Totals.csv et la ligne Total indiquent toutes deux **6 083**. L’écart de **1 345** sera présenté comme une part non détaillée dans ces exports ; sa cause n’a pas été établie.

La ligne Total contient **9 738 vues**, contre **6 648** pour les pays détaillés. Les totaux et détails seront donc conservés dans des tables distinctes pour éviter les doubles comptes. Une jointure avec le total quotidien ne devra jamais multiplier ce total par le nombre de pays.

La valeur **493,09 %** du pourcentage moyen regardé pour ES sera conservée et signalée pour vérification de sa définition et de son contexte. Elle ne sera ni tronquée à 100 %, ni déclarée invalide automatiquement. Une cellule vide ne sera pas convertie en zéro. Les zéros présents seront conservés, sans conclure automatiquement à une absence certaine d’activité.

Les moyennes de pourcentages et de durées ne seront pas simplement additionnées ou moyennées entre pays. Si les poids ou dénominateurs pertinents ne sont pas disponibles, afficher la valeur source au bon niveau d’agrégation et expliquer l’impossibilité de recomposer le total.

## Export complémentaire par vidéo

Les fichiers actuels ne permettent pas d’identifier une vidéo, son sujet ou son format. Un nouvel export par contenu est nécessaire avant les scénarios éditoriaux complets.

Champs recherchés : identifiant de vidéo, titre, période statistique, vues et durée de visionnage. Date de publication, durée de la vidéo, impressions, taux de clics et interactions seront exploités seulement s’ils sont disponibles et définis. Le format et la catégorie éditoriale seront issus de métadonnées fiables ou d’un classement manuel documenté, jamais d’une supposition silencieuse.

L’import contrôlera les colonnes, types, dates, doublons selon la granularité, identifiants et unités. Les fichiers d’origine restent immuables. Le schéma définitif et les correspondances seront confirmés après inspection de ce nouvel export. Sans ce fichier, l’analyse reste limitée à l’audience et aucune performance par sujet ou format n’est annoncée.

## Indicateurs techniques

- Durée d’une exécution : fin moins début, mesurée au niveau de l’exécution ; ne pas sommer aveuglément des étapes qui se chevauchent.
- Taux de réussite : exécutions terminées avec validation réussie / exécutions terminées ; effectif et interruptions affichés séparément.
- Jetons : consommation rapportée par le fournisseur pour chaque appel unique. Une valeur inconnue reste indisponible.
- Coût estimé : jetons facturables multipliés par les tarifs applicables ; conserver modèle, devise et date du barème. Signaler les coûts partiels.
- Erreurs : événements d’erreur ; distinguer nombre d’événements, étapes touchées et exécutions échouées.
- Agent le plus sollicité : plus grand nombre d’activations ; agent le plus lent : plus forte durée moyenne d’activation, avec effectifs.

Les horodatages techniques sont stockés en UTC ; l’affichage peut utiliser America/Toronto avec libellé explicite. Les temps écoulés utilisent une horloge monotone.

## Provenance et partage

Chaque import conserve son empreinte, sa date, sa période, son niveau d’agrégation et ses avertissements. Les résultats indiquent le jeu de données et la version de configuration utilisés.

Les données fictives seront identifiées comme telles, stockées dans `data/examples/` et exclues des conclusions empiriques. Les données réelles seront chargées depuis l’extérieur du dépôt ou un dossier local ignoré. Les traces exportables seront relues et expurgées avant tout partage ; aucune base SQLite brute n’est destinée à GitHub.
