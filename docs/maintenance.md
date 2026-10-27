# Organisation des fichiers et sauvegardes

## Contenu versionné

Le dépôt contient les scripts Python, la documentation, les scripts Ghidra, le manifeste des empreintes et le code source de MiAssistantTool avec sa licence.

## Données locales

| Dossier | Usage | Versionné |
|---|---|---|
| `private/` | Sauvegardes FRP, informations d’identification, paramètres propres à un appareil | Non |
| `artifacts/firmware/` | Archive officielle et images extraites | Non |
| `artifacts/analysis/` | Projet Ghidra, décompilations et fichiers de référence | Non |
| `artifacts/ramdisk/` | Sortie de `unpack_recovery.py` | Non |
| `.venv/` | Environnement Python local | Non |

Ces dossiers sont exclus par `.gitignore`. Un clone ne les recrée pas et ne contient pas les sauvegardes privées. Créer `private/` avant la première sauvegarde ; conserver une copie séparée des données nécessaires à une restauration ou à une reprise de l’analyse.

La sauvegarde FRP n’est pas distribuée comme fichier générique de remise en état. Elle correspond au contenu d’une partition sur un appareil précis, avant une intervention précise.

## Vérifier les fichiers à publier

```sh
git status --short
git diff --cached --stat
git ls-files private artifacts
```

La dernière commande ne doit retourner aucun fichier. Ne pas utiliser `git add -f` sur ces dossiers. Vérifier également les sorties de diagnostic avant de les ajouter à un rapport : elles peuvent contenir un numéro de série ou un chemin personnel.

## Dépendances et licences

La copie de MiAssistantTool est identifiée dans [PROVENANCE.md](../vendor/PROVENANCE.md). Sa licence Apache-2.0 est conservée dans le dossier du composant. Elle ne couvre pas les images du firmware Xiaomi ni automatiquement les autres fichiers du dépôt.

Toute mise à jour de ce composant ou des dépendances Python doit être distinguée de la configuration validée. Les fichiers sous `vendor/MiAssistantTool/` sont conservés tels qu’importés ; les scripts propres au projet se trouvent sous `scripts/`.
