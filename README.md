# Mi 9T Recovery Lab

Dossier de reproduction d’une récupération FRP réussie le 27 octobre 2026 sur un **Xiaomi Mi 9T M1903F10G / davinci**, avec **MIUI V12.1.4.0.RFJMIXM**, Android 11 et l’écran **Mi-Recovery 5.0 → Connect with MiAssistant**. Le propriétaire a confirmé que la configuration fonctionnait après redémarrage.

## Méthode validée

Le service `sync:` du miniadbd intégré au recovery permettait ici de lire et d’écrire la partition FRP avec les droits root. SELinux était permissif. Après identification de la partition sur l’appareil, sauvegarde complète et vérification, seuls les 524 288 octets de cette partition ont été remis à zéro. Une relecture complète a confirmé l’écriture avant le redémarrage manuel.

Pas de ROM flashée, pas de déverrouillage du bootloader, pas de modification de modem/persist, pas d’ouverture du téléphone. La commande propriétaire `format-frp:` restait protégée ; elle n’a pas servi à l’intervention réussie.

**Compatibilité vérifiée : un seul appareil, avec la version ci-dessus.** Même référence matérielle ne signifie pas même recovery. Les scripts gardent le profil `sda9`, 512 Kio : ne pas les transposer à un autre modèle en remplaçant simplement le numéro de série. Voir [compatibilité](docs/compatibilite.md).

## Contenu

- `scripts/` : lecture, sauvegarde, remise à zéro contrôlée, extraction du ramdisk.
- `docs/procedure.md` : préparation et procédure.
- `docs/validation.md` : résultats réellement obtenus et limites.
- `docs/firmware.md` et `docs/artifacts.sha256` : provenance et intégrité des fichiers conservés.
- `analysis/static/` : rapport historique avant intervention.
- `analysis/ghidra-scripts/` : scripts d’analyse.
- `vendor/MiAssistantTool/` : source de la bibliothèque utilisée, avec sa licence.
- `artifacts/` : firmware officiel complet, images extraites, décompilations et projet Ghidra ; **conservés localement, exclus de Git**.
- `private/` : sauvegarde FRP originale, identité de l’appareil et scripts exacts de la session ; **exclus de Git**.

## Installation

Depuis ce dossier, sous Linux avec Python 3.12, libusb et les droits d’accès USB :

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/read_config.py --help
.venv/bin/python scripts/reset_frp.py --help
```

Les versions Python installées lors du succès sont figées dans `requirements.txt`. La bibliothèque tierce est conservée dans `vendor/`. L’installation des dépendances nécessite un accès au registre Python ; aucun environnement virtuel temporaire n’est requis par les chemins du projet.

## Git et sauvegarde

Dépôt : https://github.com/gurppt/mi9t-recovery-lab.
Le `.gitignore` est prêt pour un dépôt privé. Vérifier les fichiers proposés avant le premier commit. Ne pas forcer l’ajout de `private/` ou `artifacts/`.

Un clone Git ne contiendra ni les 3 Go de firmware ni la sauvegarde originale : sauvegarder séparément ces deux dossiers, avec un stockage privé pour `private/`. Le firmware peut aussi être retéléchargé avec l’URL et les empreintes documentées.

Les scripts locaux archivés sont des outils ponctuels, pas un utilitaire universel certifié. Les variantes portables n’ont pas été réexécutées en écriture sur le téléphone après sa récupération ; leur syntaxe et leurs interfaces CLI ont été vérifiées hors appareil.
