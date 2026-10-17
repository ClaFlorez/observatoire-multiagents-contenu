# S3 — quatre agents locaux et deux périodes

Après chargement du rapport courant et comparaison avec le rapport précédent, la section **Quatre agents CrewAI locaux — exécution IA réelle — S3 périodes** propose son propre bouton. Le chargement et la relecture restent sans appel IA. Le bouton vidéo habituel reste une mission distincte.

1. Le coordonnateur cadre la comparaison, les deux populations et les absences.
2. Le chercheur appelle `lire_import` pour consulter les deux instantanés, SHA-256, dates déclarées et avertissements.
3. L’analyste appelle `comparer_periodes` : totaux canal, cohorte de paires connues, effectifs, écarts et variations.
4. Le vérificateur appelle `verifier_periodes` : recalcul indépendant depuis les deux tables, sans réutiliser le calculateur de l’analyste ; comparaison de chaque indicateur, effectif et dénominateur. Une variation relative est indisponible si la base est nulle ou absente. Les pourcentages sont comparés après arrondi à quatre décimales.
5. Le coordonnateur fournit des champs structurés et choisit une synthèse parmi deux formulations factuelles préparées en Python : écarts des deux populations ou couverture des données. Il ne rédige pas une explication libre. Ce choix contraint ne constitue pas une évaluation de qualité éditoriale générale.

Le rapport détaillé est sauvegardé ; le contexte du coordonnateur conserve les mesures, avertissements et contrôles échoués, avec un compte des contrôles réussis. La synthèse est comparée aux mesures vérifiées et à la liste des formulations autorisées. Un refus du vérificateur ne devient jamais une exécution validée.

Les traces portent `type_rapport=periodes`, `scenario=S3 — Comparaison de deux périodes`, les deux identifiants d’import et les deux périodes. Elles utilisent la même table d’exécutions réelles, mais leur sélection est séparée de la géographie et des missions par vidéo. La vue ne propose que les traces correspondant exactement aux deux instantanés choisis, dans le même ordre.

Les périodes sont validées avant le lancement : même longueur, ordre sans chevauchement, origine identique et fichiers distincts. Les dates restent déclarées par l’utilisateur ; le CSV ne prouve pas seul la période.

Le modèle est Qwen3 4B via Ollama local, sans fournisseur externe. Les compteurs et durées sont réels. Les pilotes restent marqués `eligible_campagne_reelle=false`, sans score de qualité humain attribué. Ils ne remplissent pas automatiquement les vingt essais du cours.

## Recette locale

Pilote réel a8f4e9c8 : 231.50 secondes, 3969 jetons d’entrée et 300 de sortie, quatre rôles, trois outils et cinq tâches terminées. Les 25 contrôles du vérificateur et les contrôles de synthèse passent. La synthèse distingue les écarts canal (−2 677 vues, +54,7599 heures) et cohorte (−6 693 vues, +16,9921 heures). Frais API externes : 0 USD. Les 46 tests logiciels passent. Relecture de l’interface vérifiée sans nouvel appel au modèle. Ce pilote ne remplace pas la campagne ni sa notation humaine.
