# Procédure — Mi 9T / V12.1.4.0.RFJMIXM

Cette procédure correspond au profil [documenté et testé](compatibilite.md). Toutes les commandes sont exécutées depuis la racine du dépôt. Les lectures et les écritures USB passent directement par PyUSB ; le débogage USB Android et une autorisation ADB dans Android ne sont pas nécessaires à ce mode recovery.

## 1. Préparer l’environnement

Installer l’environnement décrit dans le [README](../README.md). Vérifier les interfaces des scripts :

```sh
.venv/bin/python scripts/read_config.py --help
.venv/bin/python scripts/reset_frp.py --help
```

Créer le dossier de sauvegarde s’il n’existe pas :

```sh
mkdir -p private
chmod 700 private
```

Les scripts ne créent pas les dossiers parents du fichier de sauvegarde. La sauvegarde est créée avec le mode `0600` et ne peut pas écraser un fichier existant.

## 2. Connecter le recovery

1. Démarrer Mi Recovery avec Power + Volume haut.
2. Sélectionner **Connect with MiAssistant**.
3. Brancher le câble USB de données ; laisser l’écran MiAssistant affiché.
4. Vérifier l’énumération USB :

```sh
lsusb -d 18d1:4e11
```

Le libellé de la base USB peut être « Google Nexus One ». Il ne remplace pas l’identification du téléphone : les descripteurs de l’appareil testé indiquent Xiaomi / Mi 9T.

Brancher un seul appareil correspondant à cet identifiant. Les scripts sélectionnent la première correspondance USB, puis vérifient éventuellement son numéro de série ; ils ne recherchent pas un numéro parmi plusieurs appareils connectés.

Fermer les autres outils utilisant cette interface. Si un serveur ADB la monopolise, l’arrêter avec `adb kill-server` avant de lancer les scripts. Aucun serveur ADB n’est nécessaire au transfert direct.

## 3. Identifier l’appareil

Relever le numéro de série USB dans les descripteurs :

```sh
lsusb -v -d 18d1:4e11
```

La valeur recherchée est celle du champ `iSerial`, après l’index numérique du descripteur. Si les descripteurs ne sont pas accessibles, régler les permissions USB du système avant de poursuivre.

Dans les exemples suivants, remplacer `SERIAL_USB_A_REMPLACER` par cette valeur :

```sh
PHONE_SERIAL='SERIAL_USB_A_REMPLACER'
```

Le numéro reste local ; il n’est pas nécessaire de le publier dans un rapport.

## 4. Contrôler le firmware, les droits et la partition

```sh
.venv/bin/python scripts/read_config.py /prop.default --serial "$PHONE_SERIAL"
.venv/bin/python scripts/read_config.py /proc/self/status --serial "$PHONE_SERIAL"
.venv/bin/python scripts/read_config.py /sys/fs/selinux/enforce --serial "$PHONE_SERIAL"
.venv/bin/python scripts/read_config.py /sys/class/block/sda9/uevent --serial "$PHONE_SERIAL"
```

| Lecture | Valeurs attendues pour le profil testé |
|---|---|
| `/prop.default` | `ro.build.version.incremental=V12.1.4.0.RFJMIXM`, release 11, SDK 30 |
| `/proc/self/status` | `Name: recovery`, UID et GID tous à 0 |
| `/sys/fs/selinux/enforce` | `0` |
| `/sys/class/block/sda9/uevent` | `DEVNAME=sda9`, `DEVTYPE=partition`, `PARTN=9`, `PARTNAME=frp` |

`SYNC_OPEN` confirme l’ouverture du service. `READ_OK` confirme la réception complète d’un fichier et affiche sa taille ainsi que son SHA256.

Les lectures constituent un contrôle manuel. Le script d’écriture ne compare pas la version du firmware et ne mesure pas SELinux. Si ces valeurs diffèrent, la compatibilité doit être réévaluée avant d’utiliser ce profil.

## 5. Créer une sauvegarde fraîche

Choisir un nouveau nom de fichier pour chaque intervention :

```sh
FRP_BACKUP='private/frp-avant-reset.bin'
.venv/bin/python scripts/read_config.py /dev/block/sda9 \
  --serial "$PHONE_SERIAL" \
  --backup "$FRP_BACKUP"
sha256sum "$FRP_BACKUP"
wc -c < "$FRP_BACKUP"
```

La taille doit être **524288 octets**. Le script refuse toute autre taille. Il affiche `BACKUP_SAVED` après l’écriture locale et la synchronisation du fichier sur disque.

Relever le SHA256 :

```sh
FRP_SHA256='SHA256_DE_LA_SAUVEGARDE_A_REMPLACER'
```

Cette sauvegarde doit provenir de l’appareil connecté, dans son état actuel. Avant toute écriture, le script relit la partition et compare tous ses octets à ce fichier. Une sauvegarde d’un autre appareil ou d’un état précédent sera refusée si son contenu diffère.

## 6. Remettre la partition à zéro

Cette commande efface le contenu complet de la partition FRP :

```sh
.venv/bin/python scripts/reset_frp.py \
  --serial "$PHONE_SERIAL" \
  --backup "$FRP_BACKUP" \
  --backup-sha256 "$FRP_SHA256" \
  --execute
```

Le script effectue les opérations suivantes, dans cet ordre :

1. Vérification de `--execute`, de la taille du fichier et de son SHA256.
2. Connexion au périphérique `18d1:4e11` et comparaison du numéro de série.
3. Ouverture de `sync:` et lecture de l’identité sysfs de `sda9`.
4. Vérification de `PARTNAME=frp`.
5. Lecture de la partition et comparaison intégrale avec la sauvegarde.
6. Envoi de 128 blocs de 4096 octets nuls, soit 524 288 octets.
7. Vérification de la réponse de fin de transfert.
8. Relecture complète et comparaison avec 524 288 octets nuls.

La sortie de réussite est :

```text
IDENTITY_AND_BACKUP_VERIFIED
WRITE_ACCEPTED
VERIFIED_ZEROED_524288_BYTES
```

`WRITE_ACCEPTED` seul ne suffit pas. Attendre la confirmation de relecture et la fin normale du processus. Le script ne redémarre pas le téléphone.

L’écriture n’est pas atomique et il n’y a pas de reprise automatique. Une erreur pendant le transfert peut laisser une partition partiellement écrite. Conserver la sauvegarde et examiner l’état de la partition avant toute autre opération ; aucun script de restauration n’est fourni ni validé dans ce dépôt.

## 7. Redémarrer et vérifier la configuration

Quitter MiAssistant et choisir **Reboot → Reboot to System**. Refaire la configuration Android et vérifier que l’ancien compte Google n’est plus exigé.

La relecture de la partition valide le transfert. La configuration Android terminée valide le résultat fonctionnel. Ce résultat a été obtenu sur le [profil testé](validation.md), sans flash ni réinitialisation supplémentaire.

## Diagnostic des erreurs

| Symptôme | Vérification |
|---|---|
| Aucun appareil dans `lsusb` | Écran MiAssistant, câble de données, port USB et connecteur |
| Erreurs noyau `-110` ou `-71` | Échec de communication/énumération ; changer câble ou port et vérifier à nouveau |
| Accès USB refusé | Permissions du périphérique USB ou règles udev de la machine |
| Interface occupée | Autre outil ou serveur ADB utilisant le téléphone |
| `Unexpected device` | Numéro attendu différent de celui du premier périphérique détecté |
| `Sync rejected` / `Recovery rejected sync service` | Service indisponible sur ce recovery ; profil non confirmé |
| Timeout / lecture incomplète | Connexion interrompue, service fermé ou différence de protocole |
| Fichier de sauvegarde déjà existant | Choisir un nouveau chemin ; le fichier existant est préservé |
| `Partition identity mismatch` | Le chemin fixé ne porte pas le nom `frp` |
| `Partition differs from backup` | L’état actuel ne correspond pas à la sauvegarde fournie |
| `Verification mismatch` | L’écriture n’est pas validée ; ne pas la considérer comme réussie |

Les scripts utilisent la configuration USB active et ne déclenchent pas de `set_configuration`. Ils appliquent des délais et des limites de lecture fixes, sans reconnexion automatique.
