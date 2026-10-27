# Analyse du recovery MIUI V12.1.4.0.RFJMIXM

L’analyse du recovery du Xiaomi Mi 9T met en évidence un service de transfert de fichiers accessible dans le mode MiAssistant, distinct de la commande Xiaomi de remise à zéro FRP. L’accès à la partition FRP par ce service a ensuite été confirmé sur appareil : lecture, sauvegarde, écriture, relecture et configuration Android terminée.

## Image étudiée

| Élément | Référence |
|---|---|
| Firmware | `davinci_global V12.1.4.0.RFJMIXM` |
| Système | Android 11, correctif annoncé 2021-06-01 |
| Archive | Fastboot officielle, détails dans [Firmware](../../docs/firmware.md) |
| MD5 de l’archive | `9ce20c36aaef598af2c24c205ac72a79` |
| SHA256 de `recovery.img` | `25ed5c983692afe6f7d05eb9c5fd538ab75897cc8f03c6b1566b943c715346ab` |
| SHA256 de l’exécutable `recovery` | `0158e00793e5ae0559e98a00284a2c31a1d59520dcae8702a9d185dbce42e1c5` |

Les adresses indiquées ci-dessous sont les adresses virtuelles du projet Ghidra, avec une base d’import de `0x100000`. Elles ne sont pas des offsets USB ni des offsets dans les partitions.

## 1. Commande `format-frp`

Le répartiteur `service_mi_fd` transmet cette commande à un traitement qui communique avec le processus recovery parent. Dans `prompt_and_wait_adb_install`, le code autour de `0x1c2510` vérifie la présence d’un jeton. Une réponse décodée est ensuite transmise à `rsa_decrypt`, en `0x26296c`.

La branche d’échec autour de `0x1c2794` produit `failed_decrypt_error`, avant le chemin d’effacement. La décompilation montre des contrôles de longueur, un traitement RSA, une vérification du bourrage et une comparaison avec le jeton attendu.

Les réponses mesurées sont cohérentes avec ce code : `failed_mitoken_is_NULL` sans initialisation du jeton, puis `failed_decrypt_error` sans réponse valide. Lire le jeton ne suffit pas à produire la réponse attendue. Aucun défaut cryptographique exploitable n’a été établi dans les fonctions examinées.

## 2. Service `sync:`

| Fonction | Adresse | Rôle observé |
|---|---|---|
| `minadbd_main` | `0x1c61b0` | Configure le banner sideload et met `auth_required` à zéro |
| `service_mi_fd` | `0x1d291c` | Route `sync:` vers le service de transfert |
| `file_sync_service` | `0x1d646c` | Interprète les commandes de métadonnées, lecture et écriture |
| `recv_impl` | `0x1d92e8` | Ouvre le chemin fourni en lecture |
| `send_impl` | `0x1d7890` | Ouvre le chemin fourni en écriture, y compris un chemin existant |

Dans la branche examinée, l’ouverture de `sync:` n’applique pas la vérification du jeton de `format-frp`. Des limites de longueur de chemin et de blocs sont présentes. Aucune liste de chemins autorisés excluant le périphérique bloc FRP n’a été identifiée dans ces fonctions.

La présence de ce code a servi d’hypothèse de travail. La confirmation dynamique porte sur l’ouverture du service, la lecture des fichiers de configuration et de la partition FRP, puis l’écriture et la relecture de cette même partition. Elle ne démontre pas l’accès à tous les chemins possibles du recovery.

## 3. Configuration et droits effectifs

L’image contient `androidboot.selinux=permissive` dans sa ligne de commande. Le ramdisk indique également `ro.adb.secure=1` et `ro.debuggable=0`. Ces propriétés ne doivent pas être confondues avec le réglage d’authentification explicite du miniadbd intégré.

Le service `recovery` est déclaré avec le contexte `u:r:recovery:s0` dans `system/etc/init/hw/init.rc`, séparément du service `adbd`. Le point d’entrée `main` appelle `minadbd_main`, avec une référence autour de `0x1b550c`.

Sur l’appareil, la lecture de `/proc/self/status` par `sync:` retourne le processus `recovery`, UID/GID 0. La lecture de `/sys/fs/selinux/enforce` retourne `0`. Ces mesures confirment les droits effectifs utilisés pour le transfert ; le contexte SELinux du processus n’a pas été relevé séparément.

## 4. Partition FRP

`rawprogram0.xml` décrit une partition FRP de 128 secteurs de 4096 octets, soit 524 288 octets, sur le LUN 0 à partir du secteur 384.

Le mapping Linux a été vérifié sur l’appareil : `/sys/class/block/sda9/uevent` indique `DEVNAME=sda9` et `PARTNAME=frp`. La lecture de `/dev/block/sda9` retourne exactement 524 288 octets. L’écriture n’a été lancée qu’après sauvegarde et comparaison intégrale avec l’état courant.

## 5. Référence externe

Le projet [Mi-Acccount-Bypass-in-sideload-mode](https://github.com/Alephgsm/Mi-Acccount-Bypass-in-sideload-mode) contient une branche pour `davinci` utilisant des transferts ADB. L’examen du client embarqué retrouve le nom de service `sync:` sans ajout de jeton dans le constructeur de connexion étudié.

Ce rapprochement a orienté l’analyse ; la compatibilité du build exact repose sur les mesures matérielles décrites dans ce dépôt. Le batch tiers modifie aussi modem/persist et supprime ses sauvegardes. Il n’a pas été exécuté. Les scripts Python limitent l’écriture à la partition FRP identifiée.

## Résultats et limites

| Point | Résultat |
|---|---|
| Contrôle de `format-frp` | Présent ; les demandes testées sont refusées |
| Service `sync:` | Identifié statiquement et ouvert sur appareil |
| Lecture FRP | Validée, 524 288 octets sauvegardés |
| Écriture FRP | Acceptée, contenu nul confirmé par relecture complète |
| Configuration Android | Terminée sans l’ancien compte Google |
| Autres modèles ou builds | Non testés |

Le décompilateur n’a pas produit de résultat exploitable pour la grande fonction `prompt_and_wait_adb_install`. Les branches pertinentes ont été examinées en assembleur. Les avertissements Ghidra sur les données d’exception et les types limitent l’interprétation automatique ; les signatures de fonctions reconstruites ne sont pas toutes garanties.

L’analyse est ciblée sur ces chemins du recovery. Elle ne constitue pas une revue exhaustive, une validation indépendante complète ou une matrice de compatibilité. Les sorties de décompilation sont conservées localement dans `artifacts/analysis/` ; les scripts Ghidra utilisés sont versionnés dans `analysis/ghidra-scripts/`.
