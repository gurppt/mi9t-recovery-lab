> Archive de l’analyse statique AVANT intervention. Les conclusions ont été complétées par la réussite sur appareil décrite dans ../../docs/validation.md.

# Mi 9T — première analyse statique du recovery

Analyse du 27 octobre 2026. **Une piste technique distincte de la commande FRP a été identifiée, mais aucun déblocage ni vulnérabilité exploitable sur le téléphone n'est confirmé.** La ROM officielle exacte a été téléchargée, son empreinte vérifiée, son recovery extrait et les fonctions pertinentes examinées dans Ghidra. Aucun accès USB ni écriture sur le téléphone pendant cette analyse.

## Provenance et périmètre

- Firmware : davinci_global V12.1.4.0.RFJMIXM, Android 11.
- Archive officielle : https://cdnorg.d.miui.com/V12.1.4.0.RFJMIXM/davinci_global_images_V12.1.4.0.RFJMIXM_20210727.0000.00_11.0_global_9ce20c36aa.tgz
- MD5 calculé : `9ce20c36aaef598af2c24c205ac72a79`, correspondant au checksum publié. Ce contrôle d'intégrité n'est pas une vérification cryptographique indépendante de la signature Xiaomi.
- SHA256 recovery.img : `25ed5c983692afe6f7d05eb9c5fd538ab75897cc8f03c6b1566b943c715346ab`.
- SHA256 exécutable recovery : `0158e00793e5ae0559e98a00284a2c31a1d59520dcae8702a9d185dbce42e1c5`.
- Métadonnées de la ROM correspondante : correctif 2021-06-01.
- Binaire principal et bibliothèque `librecovery_ui_ext.so` examinés. Adresses ci-dessous : adresses virtuelles Ghidra, base d'import 0x100000.
- Baseline : AOSP recovery/minadbd, avec extensions propriétaires Xiaomi. L'absence d'authentification ADB est compatible avec un recovery limité à des opérations validées ; elle ne constitue donc pas, isolément, une preuve de vulnérabilité.

## Constats

### 1. Le refus de la commande FRP est expliqué

Le répartiteur `service_mi_fd` transmet `format-frp` à un handler qui communique avec le processus recovery parent. Dans `prompt_and_wait_adb_install`, les instructions autour de `0x1c2510` vérifient la présence du jeton, puis un bloc reçu est transmis à `rsa_decrypt` (`0x26296c`). Le chemin de retour non nul produit `failed_decrypt_error` (`0x1c2794`), avant la branche d'effacement.

`crypto-review.c` montre des contrôles de taille, un traitement RSA, la vérification du bourrage et une comparaison avec le jeton attendu. Aucune capacité à produire la réponse attendue ni défaut cryptographique exploitable n'a été établi. Lire le jeton ne suffit pas. Les réponses observées lors des essais précédents sont cohérentes avec ce code.

### 2. Un service de transfert distinct existe réellement dans cette ROM

- `minadbd_main` (`0x1c61b0`) configure le banner sideload et met `auth_required` à zéro.
- `service_mi_fd` (`0x1d291c`) route `sync:` vers `file_sync_service`, sans vérification du jeton FRP dans cette branche.
- `file_sync_service` (`0x1d646c`) interprète des requêtes de métadonnées, de lecture et d'écriture. Il limite les longueurs de chemins et de blocs.
- `recv_impl` (`0x1d92e8`) ouvre le chemin fourni en lecture.
- `send_impl` (`0x1d7890`) ouvre le chemin fourni en écriture, avec un traitement des fichiers déjà existants. Aucune liste de chemins autorisés ni vérification du jeton FRP n'a été identifiée dans les fonctions examinées.

**Portée de ce constat :** ce chemin est un candidat sérieux à examiner, distinct du refus de `format-frp`. La présence du code ne prouve pas que l'instance actuellement installée l'expose avec les permissions nécessaires. Il manque notamment une vérification en lecture seule de l'accessibilité du service, de la version du recovery installé, des droits effectifs et du mapping des partitions. Aucune requête d'écriture de validation n'a été envoyée.

### 3. Cartographie et configuration

`firmware/rawprogram0.xml:13` décrit une partition `frp` de 512 Kio, sur le LUN 0, secteur 384 (secteurs de 4096 octets). Le chemin Linux sur le téléphone doit être confirmé avant toute conclusion pratique ; un index copié depuis un script tiers n'est pas une preuve suffisante.

L'en-tête de recovery.img contient `androidboot.selinux=permissive`. C'est une configuration de l'image, pas une mesure de l'état SELinux réellement appliqué au démarrage. Les propriétés du ramdisk indiquent aussi `ro.adb.secure=1` et `ro.debuggable=0` : elles ne doivent pas être confondues avec le comportement explicite du minadbd intégré au recovery.

Le service `recovery` est déclaré avec le contexte `u:r:recovery:s0` dans `ramdisk/system/etc/init/hw/init.rc`, séparément du service `adbd`. Les règles USB distinguent les modes `adb` et `sideload`, tout en utilisant l'identifiant produit `4E11`, cohérent avec la détection antérieure du téléphone. Le point d'entrée `main` du binaire appelle `minadbd_main` (référence à `0x1b550c`). Cela conforte la pertinence du minadbd intégré au recovery, plutôt que d'extrapoler depuis le daemon ADB Android ordinaire. L'UID et le contexte effectifs du processus n'ont pas été mesurés sur l'appareil.

### 4. La référence publique est cohérente mais ne constitue pas une validation

Le projet https://github.com/Alephgsm/Mi-Acccount-Bypass-in-sideload-mode annonce davinci jusqu'à MIUI12. Son batch utilise les transferts ADB et ne passe pas par `format-frp`. Le constructeur de connexion du client embarqué contient le service `sync:` sans ajout de jeton dans la séquence examinée. Ces observations confortent la piste, sans prouver la compatibilité exacte du téléphone.

Le batch modifie aussi modem/persist et supprime ses sauvegardes. Il n'a pas été exécuté, et son exécution globale ne correspond pas au besoin de diagnostic FRP.

## Résultat et limites

| Résultat | Statut |
|---|---|
| Cause du refus FRP | Expliquée par les contrôles du binaire |
| Service alternatif de transfert | Présence et routage confirmés statiquement |
| Accès réel aux partitions du téléphone par ce service | Non testé |
| Déblocage FRP | Non obtenu |
| Vulnérabilité exploitable confirmée | Aucune à ce stade |

Le décompilateur a échoué sur la grande fonction parent `prompt_and_wait_adb_install`; les branches pertinentes ont donc été examinées en assembleur (`recovery-handler-assembly.txt`). Des avertissements Ghidra sur des données d'exception et types limitent la portée d'une analyse automatique exhaustive. Les déclarations de retour reconstruites peuvent être imparfaites et ont été recoupées avec les branches d'appel.

Une vérification indépendante des références publiques a été réalisée ; la seconde revue de chasse a été interrompue par un blocage de sous-agent. Aucun résultat n'est présenté comme ayant passé une validation indépendante complète. Premier passage d'analyse seulement : des examens supplémentaires peuvent couvrir les chemins et composants non étudiés.

Prochaine étape technique possible : vérifier uniquement en lecture l'accessibilité du service et les informations de fichiers sur le téléphone. L'analyse présente n'autorise aucune conclusion sur le succès d'un effacement et ne nécessite aucun démontage.
