# Firmware et analyse hors appareil

## Archive de référence

| Champ | Valeur |
|---|---|
| Variante | `davinci_global` |
| Version | `V12.1.4.0.RFJMIXM` |
| Build de l’archive | `20210727.0000.00`, Android 11, Global |
| Taille de l’archive | 3 153 188 490 octets |
| MD5 calculé | `9ce20c36aaef598af2c24c205ac72a79` |
| SHA256 calculé | `f6b3a5dbdc926f78ab25ac032ab65d1d11874f19dd7ce233be4a237c774a9835` |

[Archive Fastboot officielle Xiaomi](https://cdnorg.d.miui.com/V12.1.4.0.RFJMIXM/davinci_global_images_V12.1.4.0.RFJMIXM_20210727.0000.00_11.0_global_9ce20c36aa.tgz).

L’archive sert de référence pour l’analyse ; elle n’a pas été flashée sur le téléphone. Elle n’est pas incluse dans Git.

## Téléchargement et intégrité

Depuis la racine du dépôt :

```sh
mkdir -p artifacts/firmware
curl --fail --location --output artifacts/firmware/davinci_global_V12.1.4.0.RFJMIXM_fastboot.tgz \
  'https://cdnorg.d.miui.com/V12.1.4.0.RFJMIXM/davinci_global_images_V12.1.4.0.RFJMIXM_20210727.0000.00_11.0_global_9ce20c36aa.tgz'
sha256sum artifacts/firmware/davinci_global_V12.1.4.0.RFJMIXM_fastboot.tgz
```

Comparer le résultat à l’empreinte ci-dessus avant extraction. Le fichier compressé fait environ 3,15 Go ; prévoir de l’espace supplémentaire pour les images et la base Ghidra.

Ces empreintes identifient les octets étudiés. Elles ne constituent pas une vérification indépendante de la signature du firmware.

## Image recovery

Lister les membres de l’archive pour relever le chemin exact de `recovery.img` :

```sh
tar -tzf artifacts/firmware/davinci_global_V12.1.4.0.RFJMIXM_fastboot.tgz
```

Dans l’archive de référence, extraire ce membre vers le chemin attendu par l’outil :

```sh
tar -xOzf artifacts/firmware/davinci_global_V12.1.4.0.RFJMIXM_fastboot.tgz \
  'davinci_global_images_V12.1.4.0.RFJMIXM_20210727.0000.00_11.0_global/images/recovery.img' > artifacts/firmware/recovery.img
sha256sum artifacts/firmware/recovery.img
```

SHA256 attendu :

```text
25ed5c983692afe6f7d05eb9c5fd538ab75897cc8f03c6b1566b943c715346ab
```

La redirection remplace le fichier local `recovery.img` s’il existe déjà. Ces opérations ne communiquent pas avec le téléphone.

## Extraction du ramdisk

```sh
.venv/bin/python scripts/unpack_recovery.py
```

L’outil lit `artifacts/firmware/recovery.img`, repère le ramdisk à partir de l’en-tête de boot Android, puis décompresse son contenu gzip. Les sorties sont :

| Chemin | Contenu |
|---|---|
| `artifacts/firmware/ramdisk.bin` | Ramdisk compressé extrait de l’image |
| `artifacts/firmware/ramdisk.cpio` | Archive CPIO décompressée |
| `artifacts/ramdisk/` | Fichiers réguliers extraits |

Les liens symboliques sont signalés mais pas créés. Les chemins absolus et les chemins contenant `..` sont refusés. L’outil est adapté au format de cette image ; il ne gère pas tous les formats de boot Android. Utiliser un répertoire de sortie propre : les fichiers réguliers existants peuvent être remplacés.

## Analyse Ghidra

Importer l’exécutable ARM64 `artifacts/ramdisk/system/bin/recovery` et examiner la bibliothèque `artifacts/ramdisk/system/lib64/librecovery_ui_ext.so`. Le projet de référence utilise une base d’import de `0x100000` ; les adresses du [rapport](../analysis/static/REPORT.md) se rapportent à cette base.

Les scripts Java sous `analysis/ghidra-scripts/` permettent de rechercher les chaînes et références pertinentes, d’extraire des décompilations et de consulter les instructions des fonctions sélectionnées. Leurs arguments sont définis dans chaque fichier source ; les chemins de sortie doivent être choisis localement.

Le jeu de référence conserve également `rawprogram*.xml`, le chargeur firehose inclus dans la ROM, les décompilations et le projet Ghidra `artifacts/analysis/recovery-analysis.gpr` avec son dossier `.rep`. La présence du chargeur firehose ne constitue pas une validation du mode EDL : il n’a pas été utilisé pour cette méthode.

Le ramdisk extrait lors de l’analyse initiale est conservé dans `artifacts/analysis/ramdisk/`. Une nouvelle extraction par le script utilise `artifacts/ramdisk/` ; les deux chemins ont le même rôle mais restent distincts.

## Manifeste de référence

[artifacts.sha256](artifacts.sha256) répertorie les images et résultats locaux de l’analyse :

```sh
sha256sum -c docs/artifacts.sha256
```

Cette commande suppose que le jeu complet de fichiers est présent. Un clone du dépôt ne suffit pas. Les bases Ghidra sont mutables et leurs empreintes ne sont pas un objectif de reproductibilité d’une nouvelle analyse ; utiliser les empreintes du firmware pour identifier les entrées.

## Sources examinées

- [MiForge/MiAssistantTool](https://github.com/MiForge/MiAssistantTool) : primitives de transport USB ; copie incluse sous `vendor/`.
- [Mi-Acccount-Bypass-in-sideload-mode](https://github.com/Alephgsm/Mi-Acccount-Bypass-in-sideload-mode) : référence étudiée statiquement ; son batch et ses exécutables ne sont pas utilisés par la procédure.
- [XiaomiADB](https://www.xiaomitool.com/adb) : contexte du client ADB Xiaomi.
