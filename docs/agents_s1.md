# S1 — trois premières vidéos par vues et heures

Dans **Contenu par vidéo**, confirmer et charger le CSV. La section **S1 — trois premières vidéos par vues et par heures** apparaît avant S2/S4. Deux tableaux et deux graphiques affichent les classements, identifiants, titres, valeurs et unités. Ils utilisent l’import complet, indépendamment du filtre de recherche du classement exploratoire.

Le calcul Python n’appelle pas le modèle. Le bouton distinct **Quatre agents CrewAI locaux — exécution IA réelle — S1** lance quatre rôles et cinq tâches sur Qwen3 4B local : cadrage, provenance, calcul, vérification, synthèse. Les outils sont `lire_import`, `classer_videos_s1` et `verifier_s1`.

Le vérificateur calcule les rangs par comptage des valeurs supérieures et des égalités précédentes dans le fichier, indépendamment du tri du calculateur. Les 18 contrôles vérifient effectif, absences, nombre de vidéos classées, chaque identifiant et valeur, et unicité des identifiants. Les classements peuvent différer entre vues et heures. Les ex æquo conservent l’ordre du CSV, sans prétendre qu’une valeur égale est supérieure. S’il existe moins de trois valeurs connues, les rangs restants restent indisponibles. Zéro est connu ; une cellule absente ne l’est pas.

Le coordonnateur recopie une formulation factuelle autorisée par le schéma JSON, préparée en Python. Il ne rédige pas une explication causale libre. Une vérification refusée ne devient pas une validation. Le rapport complet, les appels et les résultats sont conservés dans SQLite ; la relecture utilise la signature du scénario et de l’import sélectionnés.

Cette mission est un pilote d’intégration à 0 USD d’API externe, sans note humaine attribuée et exclu des vingt essais évalués. Les deux configurations et la campagne complète restent à préparer.

## Recette du 16 octobre 2026

58 tests logiciels réussis. Pilote réel `75d4ddeb` terminé en 177,63 secondes : quatre rôles, cinq tâches, trois outils ; les 18 contrôles du vérificateur et les contrôles de synthèse passent. Aucune erreur enregistrée, 0 USD d’API externe.

Sur les 88 vidéos du rapport du 17 septembre au 14 octobre 2026 : classement vues `YeDXi4z_Cqo` (2453), `kBTZN_TGMoU` (1751), `tJ1eWg2_GvQ` (764). Classement heures `YeDXi4z_Cqo` (53,6046), `oZxDZjHcZUI` (15,3774), `kBTZN_TGMoU` (12,2093). Chaque mesure compte 17 valeurs absentes. Aucun lien causal déduit.
