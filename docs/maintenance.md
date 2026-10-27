# Conservation locale

`private/` contient des données propres au téléphone et n’est pas versionné. `artifacts/` contient les images officielles et les résultats dérivés, également exclus de Git pour éviter d’y stocker plusieurs gigaoctets de binaires. Garder une sauvegarde séparée de ces répertoires.

Aucun fichier de firmware n’est soumis à la licence de MiAssistantTool du seul fait de sa présence ici. La licence tierce Apache-2.0 concerne le code sous `vendor/MiAssistantTool/`. Aucune licence de redistribution globale n’est ajoutée au projet.

Pour préparer un dépôt, examiner `git status --short` après son initialisation, puis les fichiers réellement ajoutés à l’index. Les scripts exacts, l’identité USB et la sauvegarde originale doivent rester hors des commits, même pour un dépôt privé.

Les copies sources historiques sous `/home/gurp/security-audit-skill/` ne sont pas supprimées automatiquement ; elles peuvent servir à vérifier cette migration. Les caches Ghidra et traces volumineuses n’ont pas été recopiés ; les décompilations utiles, le projet et le rapport décrivant leurs limites ont été conservés.
