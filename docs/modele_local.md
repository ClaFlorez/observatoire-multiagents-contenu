# Faisabilité d’un modèle IA local

## Diagnostic du poste

Contrôles en lecture seule réalisés le 15 octobre 2026, sans utilisation de la clé OpenAI, sans installation de moteur et sans téléchargement de modèle.

| Ressource | Valeur constatée |
|---|---|
| Système | Windows 10 Pro, 22H2, build 19045 |
| Mémoire vive | 16 Gio |
| Processeur | Intel Core i7-4770K, 4 cœurs et 8 processeurs logiques |
| Carte graphique | NVIDIA GeForce GTX 1080 |
| Mémoire graphique totale | 8 192 Mio |
| Mémoire graphique libre au contrôle | 7 095 Mio ; valeur variable |
| Pilote NVIDIA | 560.94 |
| Espace libre sur C | Environ 199,7 Gio au contrôle |

Aucun exécutable Ollama n’a été trouvé dans le PATH ou à son emplacement utilisateur habituel. Aucun serveur n’a répondu sur `127.0.0.1:11434`. Cela ne prouve pas l’absence de toute installation dans un autre dossier.

## Conclusion et limite GPU

La mémoire et l’espace disque rendent possible un premier essai de petit modèle quantifié. Le premier essai ci-dessous a réussi ; la qualité générale du français et la fiabilité sur plusieurs missions restent à mesurer.

La GTX 1080 est classée en capacité de calcul 6.1. La documentation Ollama actuelle exige un pilote 570 ou supérieur pour les capacités 5.0 à 6.2. Le pilote installé ne satisfait pas cette condition. Ne pas annoncer l’accélération GPU comme opérationnelle. Aucune mise à jour de pilote n’a été réalisée.

Sources : [support matériel Ollama](https://docs.ollama.com/gpu), [installation Windows](https://docs.ollama.com/windows), consultées le 15 octobre 2026.

## Premier essai proposé

Utiliser Ollama avec un modèle téléchargé localement, sans fonction cloud. Le candidat de départ est **qwen3:4b**, quantification Q4_K_M, téléchargement annoncé d’environ 2,5 Go ; sa mémoire en fonctionnement sera supérieure à la seule taille du fichier. La fiche indique une licence Apache 2.0 et des fonctions multilingues et d’outils. Ces capacités ne garantissent pas la réussite du workflow CrewAI.

Source : [fiche officielle du modèle](https://ollama.com/library/qwen3:4b).

Pour ne pas dépendre du pilote GPU, commencer par un essai CPU explicitement configuré. Limiter le contexte initial à 4 096 jetons, les réponses à quelques centaines de jetons et traiter les rôles séquentiellement avec un seul modèle chargé. Réduire le modèle si le temps de réponse devient incompatible avec la démonstration. Les quatre rôles ne nécessitent pas quatre modèles simultanément en mémoire.

Désactiver les fonctions cloud avec `OLLAMA_NO_CLOUD=1`, conserver l’écoute sur la boucle locale et vérifier la configuration effective. Une API HTTP sur `127.0.0.1` est une interface locale ; elle n’implique pas une facturation externe. Les téléchargements nécessitent Internet et de l’espace disque ; le calcul consomme les ressources et l’électricité du poste.

Source : [FAQ Ollama — contexte, CPU/GPU et désactivation du cloud](https://docs.ollama.com/faq).

## Validation avant intégration

1. Vérifier le téléchargement et l’identifiant exact du modèle, ainsi que son fonctionnement sans cloud.
2. Exécuter une question courte en français sur un exemple fictif, avec réponse et compteurs de jetons réellement retournés.
3. Mesurer durée de chargement, durée de génération, mémoire et processeur effectivement utilisés ; ne pas assimiler ce temps au temps de simulation Python.
4. Tester sortie structurée et appels aux deux outils, puis les quatre agents CrewAI. Ne pas déclarer l’intégration réussie à partir d’un simple dialogue.
5. Conserver la simulation existante séparément. Seules les traces d’appels réels au modèle local pourront alimenter la campagne IA.

## État et budget

**Budget autorisé : 0 USD de frais API externes.** La clé OpenAI reste inutilisée. Diagnostic, téléchargement et premier essai sont terminés. Une première intégration CrewAI locale est opérationnelle : voir [les quatre agents locaux](agents_locaux.md). La campagne évaluée est terminée ; ses vingt essais et vingt avis sont analysés dans le rapport.

## Installation et preuve du premier essai

Ollama portable **0.40.5** a été téléchargé depuis la [publication officielle](https://github.com/ollama/ollama/releases/tag/v0.40.5). La distribution Windows amd64 a été vérifiée avec la somme SHA256 publiée : `5134ce7e3bc8e94d0494721c799ec293b429450d0c52461b0ee3647dd3bb4bb7`.

Le moteur est extrait dans `.local/ollama/` et les modèles stockés dans `.local/models/`. Ces dossiers sont ignorés par Git. Ollama a également créé son identité technique standard dans le dossier utilisateur `.ollama` ; elle ne correspond pas à la clé OpenAI et n’est pas incluse dans le dépôt.

Le script `scripts/demarrer_ollama_local.ps1` configure le processus : écoute `127.0.0.1:11434`, cloud désactivé, contexte 4 096, une requête parallèle et un modèle chargé. La requête d’essai fixe également `num_gpu=0`. Le serveur peut détecter une carte graphique, mais la réponse `/api/ps` après l’essai indique **size_vram=0**, ce qui confirme que le modèle chargé n’utilise pas de mémoire GPU.

Essai effectué le **15 octobre 2026 à 22 h 23, heure de Toronto** :

| Mesure | Résultat observé |
|---|---|
| Modèle | qwen3:4b |
| Données | Deux nombres fictifs : CA=30, FR=5 |
| Sortie | JSON valide ; pays CA et justification en français |
| Jetons d’entrée | 79 |
| Jetons de sortie | 35 |
| Durée totale retournée par Ollama | 12,91 secondes |
| Chargement du modèle | 5,41 secondes |
| Génération | 4,91 secondes |
| Mémoire du modèle chargé rapportée par Ollama | Environ 3,19 Go ; ne représente pas toute la mémoire du processus |
| Frais API externes | 0 USD |

Le rapport détaillé est conservé localement dans `data/private/essai_local.json`, ignoré par Git. Une seule réponse correcte ne démontre ni la fiabilité de tous les agents ni une conformité à la campagne du cours.

## Reproduction sur un autre poste

1. Installer Python et les dépendances du projet selon le README.
2. Télécharger une distribution officielle Ollama Windows compatible et vérifier son empreinte avant extraction dans `.local/ollama/`.
3. Lancer le script PowerShell du serveur depuis le projet et laisser ce terminal ouvert ; vérifier le message de désactivation du cloud.
4. Dans un autre terminal, avec `OLLAMA_HOST=127.0.0.1:11434`, utiliser le CLI portable `ollama.exe pull qwen3:4b`. Le serveur place les modèles dans le chemin configuré ; prévoir la connexion Internet et l’espace requis.
5. Lancer `python -m observatoire.essai_local` dans l’environnement du projet et comparer le résultat attendu CA, les compteurs et les durées réellement retournés.

Ne pas remplacer un échec local par un appel OpenAI automatique. Pour arrêter le moteur lancé au premier plan, utiliser Ctrl+C dans son terminal.
