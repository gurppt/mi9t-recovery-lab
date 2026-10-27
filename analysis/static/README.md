# Analyse du recovery

L’analyse porte sur le recovery du firmware **davinci_global V12.1.4.0.RFJMIXM**. Les résultats statiques sont rapprochés des mesures et de l’écriture vérifiée sur appareil.

- [Rapport technique](REPORT.md) : fonctions, contrôles et portée des résultats.
- [Architecture](architecture.md) : processus, transport USB et flux de données.
- [Constats](FINDINGS-DETAIL.md) : comportement observé et limites.
- [Validation matérielle](../../docs/validation.md) : valeurs mesurées et résultat fonctionnel.

Les scripts d’inspection Ghidra sont dans `../ghidra-scripts/`. Les images, décompilations et bases de travail sont des fichiers locaux exclus de Git, décrits dans [Firmware](../../docs/firmware.md).

`findings.json` conserve la sortie vide du premier passage statique, réalisé avant les tests USB. Ce fichier n’est pas un bilan des essais matériels et ne doit pas être interprété comme une absence du comportement confirmé par la suite.
