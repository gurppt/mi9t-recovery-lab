# Contrôles de l’archivage

Effectués le 27 octobre 2026, sans accès USB ni nouvelle écriture sur le téléphone :

- archive officielle copiée : 3 153 188 490 octets, SHA256 identique à la source ; MD5 recalculé ;
- manifeste SHA256 de 594 fichiers binaires et résultats d’analyse ;
- sauvegarde privée : taille et empreinte conformes à la session ;
- scripts historiques copiés à l’identique ;
- `miassistant/core.py` inclus identique à la bibliothèque installée lors du succès ;
- compilation Python des trois scripts et aide CLI des deux scripts USB réussies ;
- refus de `reset_frp.py` sans `--execute` vérifié avant accès USB ;
- exclusions Git vérifiées dans un dépôt de test temporaire extérieur au dossier de travail.

Pas de test matériel supplémentaire ni de réinstallation des dépendances dans un environnement neuf. Le dépôt Git a ensuite été initialisé pour préparer le premier commit.
