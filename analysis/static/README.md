# Archive historique avant intervention

Tous les fichiers de ce dossier décrivent l’état de l’analyse statique avant les essais sur appareil. `findings.json` est le résultat vide de ce premier passage, pas le bilan final.

Le résultat dynamique final et la récupération réussie sont dans [validation.md](../../docs/validation.md).

Les chemins relatifs du rapport initial correspondent désormais à :

- `firmware/` → `../../artifacts/firmware/`
- `ramdisk/` → `../../artifacts/analysis/ramdisk/`
- décompilations C et assembleur → `../../artifacts/analysis/`

La référence tierce Windows est citée par son URL dans le rapport ; elle n’est pas nécessaire à la reproduction et ses exécutables n’ont pas été conservés dans le projet.
