# Intégrité des fichiers et contrôles hors appareil

## Contrôles effectués

| Contrôle | Résultat |
|---|---|
| Archive officielle | 3 153 188 490 octets ; SHA256 identique entre source et copie ; MD5 recalculé |
| Manifeste local | 594 fichiers répertoriés dans `artifacts.sha256` |
| Sauvegarde FRP originale | Taille et empreinte vérifiées |
| Scripts de test originaux | Copies identiques, conservées hors Git |
| `miassistant/core.py` | Identique à la bibliothèque utilisée pour le test matériel |
| Scripts Python du projet | Compilation syntaxique réussie |
| CLI des scripts USB | `--help` vérifié |
| Protection d’exécution | Refus de `reset_frp.py` sans `--execute`, avant accès USB |
| Exclusions Git | `private/` et `artifacts/` exclus |

Ces contrôles ne constituent pas un deuxième test matériel. L’installation des dépendances dans un environnement vierge n’a pas été validée lors de la préparation initiale du dépôt.

## Refaire les contrôles locaux

Depuis la racine, avec les dépendances installées :

```sh
.venv/bin/python -m py_compile scripts/read_config.py scripts/reset_frp.py scripts/unpack_recovery.py
.venv/bin/python scripts/read_config.py --help
.venv/bin/python scripts/reset_frp.py --help
git check-ignore private/frp-test.bin artifacts/firmware/recovery.img
```

La compilation et l’aide CLI n’établissent aucune connexion USB.

Pour le jeu complet de fichiers binaires archivé :

```sh
sha256sum -c docs/artifacts.sha256
```

Un clone seul ne contient pas ces fichiers. Le manifeste inclut aussi des fichiers du projet Ghidra qui peuvent changer après ouverture ou analyse. Une nouvelle extraction ou une nouvelle base Ghidra ne reproduira pas nécessairement leurs empreintes ; celles des images officielles servent à identifier le firmware étudié.
