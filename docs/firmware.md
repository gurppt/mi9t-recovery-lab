# Firmware et références conservées

Archive officielle utilisée :

https://cdnorg.d.miui.com/V12.1.4.0.RFJMIXM/davinci_global_images_V12.1.4.0.RFJMIXM_20210727.0000.00_11.0_global_9ce20c36aa.tgz

Copie locale : `artifacts/firmware/davinci_global_V12.1.4.0.RFJMIXM_fastboot.tgz`.
MD5 recalculé sur l’archive conservée : `9ce20c36aaef598af2c24c205ac72a79`.

Les empreintes SHA256 calculées pendant l’archivage sont dans `docs/artifacts.sha256` ; depuis la racine :

```sh
sha256sum -c docs/artifacts.sha256
```

Ce contrôle d’intégrité ne constitue pas une vérification indépendante de la signature Xiaomi.

Conservés également : recovery.img, tables rawprogram, chargeur firehose présent dans la ROM, ramdisk compressé et cpio, fichiers réguliers extraits, projet Ghidra et décompilations. Le chargeur firehose a été conservé pour complétude ; il n’a pas servi à déverrouiller le téléphone et aucune compatibilité EDL n’a été établie.

Les scripts Ghidra se trouvent dans `analysis/ghidra-scripts/`. Le projet est `artifacts/analysis/recovery-analysis.gpr` et son répertoire compagnon `.rep`. `scripts/unpack_recovery.py` travaille sur `artifacts/firmware/recovery.img`, décompresse le ramdisk gzip et extrait seulement les fichiers réguliers dans `artifacts/ramdisk/`. Les liens symboliques ne sont pas créés. Cette extraction est spécifique au format de l’image archivée, pas un extracteur Android universel.

Références étudiées :

- https://github.com/MiForge/MiAssistantTool : primitives USB utilisées, source incluse avec licence.
- https://github.com/Alephgsm/Mi-Acccount-Bypass-in-sideload-mode : comparaison statique ; son batch et ses exécutables n’ont pas été exécutés ni inclus dans les outils opérationnels.
- https://www.xiaomitool.com/adb : contexte de l’outil XiaomiADB.

Le téléchargement incomplet `fastboot.tgz` et les caches de compilation ne sont pas nécessaires. L’archive officielle complète suffit à retrouver les images qui n’ont pas été extraites ici.
