# S2 et S4 — paramètres enregistrés et quatre agents locaux

Dans « Contenu par vidéo », charger l’export et confirmer sa période. Sous la préparation des groupes, la section **Charger les paramètres enregistrés — S2 et S4** détecte les fichiers `youtube_csv/parametres_s2_s4*.json` (y compris un espace avant `.json`). Cliquer sur **Charger et vérifier les paramètres S2/S4**. Le chargement ne lance aucune inférence.

Le fichier, l’empreinte SHA-256, l’origine et la période doivent correspondre exactement à l’import courant. Les identifiants sont vérifiés ; les groupes S2 doivent être non vides, sans doublon ni intersection. La cible S4 est exclue des références et doit avoir une valeur connue pour la mesure choisie. Les calculs présents dans le JSON téléchargé sont ignorés et recalculés depuis le CSV.

Deux boutons distincts permettent ensuite de lancer **S2** ou **S4**. Ils utilisent Qwen3 4B sur le CPU, sans API externe, avec les quatre rôles et cinq tâches : cadrage, provenance, calcul, vérification, synthèse. Les trois outils sont `lire_import`, `comparer_groupes` et `verifier_groupes`. Le vérificateur recalcule les médianes, sommes et effectifs indépendamment du calculateur.

S2 compare les deux groupes par vues et heures : effectif total, valeurs connues, absentes, somme et médiane connues. S4 compare la valeur cible à la médiane connue des références. Sans valeur connue, aucune somme n’est assimilée à zéro. Une référence unique reste exploratoire.

Le coordonnateur recopie une formulation factuelle autorisée par un schéma JSON. Le texte est préparé en Python, pas une analyse libre du modèle. Les chiffres et le verdict doivent être identiques au rapport vérifié. La comparabilité des contenus et la qualité éditoriale restent soumises à revue humaine.

Les paramètres sont figés dans `missions_groupes`, associés à l’instantané vidéo. Leur signature inclut scénario, groupes/cible, justification, provenance et période. La relecture ne montre que les exécutions correspondant à cette signature et à ce scénario. Modifier un sélecteur de préparation ne change pas une mission chargée : exporter et recharger le nouveau JSON.

Les traces réelles sont conservées dans `executions_reelles`, avec durées et compteurs réellement retournés par Ollama. Échecs conservés ; `eligible_campagne_reelle=false` et absence de note humaine. Les pilotes ne remplacent pas les vingt essais évalués.

## Recette du 16 octobre 2026

54 tests logiciels réussis. Les pilotes réels S2 `b64672ae` (182,85 secondes) et S4 `126f9838` (122,27 secondes) terminent les cinq tâches, appellent les quatre rôles et les trois outils, puis passent tous les contrôles d’intégration et de synthèse. Frais API externes : 0 USD. Le premier démarrage S2 `4f810b7a` échoue avant toute réponse du modèle (accès local refusé) ; cette trace est conservée après redémarrage du serveur Ollama avec accès à ses fichiers.

S2 : médianes connues A/B de 329,5/219,5 vues et 3,60865/3,64125 heures, deux vidéos connues par groupe. S4 : une vue cible, référence unique à 25 vues, écart −24 vues. La justification enregistrée reconnaît les sujets différents et l’absence de vérification de proximité de durée et d’ancienneté. Ce résultat reste exploratoire.
