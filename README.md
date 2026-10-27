# Mi 9T Recovery Lab

Analyse du recovery MIUI et scripts Python pour réinitialiser la partition FRP d’un **Xiaomi Mi 9T — M1903F10G, codename `davinci`**, depuis le mode **Connect with MiAssistant**.

La méthode a été validée sur **MIUI Global V12.1.4.0.RFJMIXM / Android 11**, avec un bootloader verrouillé. Elle utilise le service de transfert `sync:` du recovery pour sauvegarder la partition FRP, la remettre à zéro et vérifier le contenu écrit. Après redémarrage, la configuration Android a pu être terminée sans l’ancien compte Google.

**Un seul appareil et une seule version de firmware ont été testés.** Le profil de partition est fixé dans les scripts : `/dev/block/sda9`, **524 288 octets**. La référence du téléphone ou la présence de Mi-Recovery 5.0 ne suffisent pas à garantir la compatibilité.

## Fonctionnement

L’analyse de `recovery.img` avec Ghidra a mis en évidence deux chemins distincts :

| Chemin | Comportement observé |
|---|---|
| Commande Xiaomi `format-frp:` | Vérifie un jeton et une réponse RSA ; les appels sans réponse valide sont refusés. |
| Service `sync:` de miniadbd | Accepte des transferts de fichiers ; permet ici de lire et d’écrire le périphérique bloc de la partition FRP. |

Sur le recovery testé, le service tourne avec l’UID **0** et SELinux est **permissif**. Le script ouvre une connexion USB directe, utilise les paquets ADB et transfère les données via le protocole SYNC. Aucune modification du binaire de recovery n’est nécessaire.

Ghidra sert à comprendre et vérifier l’implémentation du firmware. L’opération sur le téléphone est effectuée par les scripts Python. La ROM n’est pas reflashée, le bootloader reste verrouillé et les partitions `persist` et modem ne sont pas modifiées.

## Configuration testée

| Élément | Valeur |
|---|---|
| Téléphone | Xiaomi Mi 9T, M1903F10G |
| Codename | `davinci` ; variante firmware `davinci_global` |
| MIUI | `V12.1.4.0.RFJMIXM` |
| Android | 11 / API 30 |
| Correctif de sécurité annoncé | 2021-06-01 |
| Interface recovery | Mi-Recovery 5.0 → Connect with MiAssistant |
| Identifiant USB | `18d1:4e11` |
| Processus du service de transfert | `recovery`, UID/GID 0 |
| SELinux | `enforce=0` |
| Partition | `sda9`, nom GPT `frp`, 512 Kio |

Les différences entre versions, les conditions à vérifier et les limites des scripts sont détaillées dans [Compatibilité](docs/compatibilite.md).

## Installation

Environnement de référence : Linux, Python 3.12, bibliothèque système libusb et accès utilisateur à l’interface USB. Un câble de données fonctionnel est nécessaire. Ghidra et l’archive du firmware sont nécessaires pour l’analyse, mais pas pour exécuter les scripts USB sur le profil déjà vérifié.

```sh
git clone https://github.com/gurppt/mi9t-recovery-lab.git
cd mi9t-recovery-lab
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
mkdir -p private
chmod 700 private
```

`requirements.txt` fixe les versions des dépendances Python et installe la copie locale de MiAssistantTool. Les dépendances système, dont libusb, ne sont pas installées par pip.

## Utilisation

Démarrer le téléphone dans Mi Recovery, sélectionner **Connect with MiAssistant**, puis vérifier la connexion :

```sh
lsusb -d 18d1:4e11
.venv/bin/python scripts/read_config.py /prop.default
.venv/bin/python scripts/read_config.py /proc/self/status
.venv/bin/python scripts/read_config.py /sys/fs/selinux/enforce
.venv/bin/python scripts/read_config.py /sys/class/block/sda9/uevent
```

Ces commandes lisent le recovery sans modifier le téléphone. La procédure complète décrit ensuite l’identification USB, la sauvegarde et les contrôles avant écriture : **[Procédure détaillée](docs/procedure.md)**.

`reset_frp.py` est destructif : il écrit des zéros sur toute la partition FRP. Il exige une sauvegarde fraîche, son SHA256, le numéro de série attendu et l’option `--execute`. Il contrôle le nom de la partition et compare son contenu à la sauvegarde avant l’écriture, puis relit intégralement le résultat. Il ne vérifie pas automatiquement la version MIUI ni l’état SELinux ; ces vérifications font partie de la procédure.

## Documentation et code

| Chemin | Contenu |
|---|---|
| [scripts/read_config.py](scripts/read_config.py) | Lectures limitées aux chemins du profil et sauvegarde FRP locale |
| [scripts/reset_frp.py](scripts/reset_frp.py) | Vérifications, remise à zéro et relecture de la partition FRP |
| [scripts/unpack_recovery.py](scripts/unpack_recovery.py) | Extraction du ramdisk gzip de l’image recovery étudiée |
| [docs/procedure.md](docs/procedure.md) | Installation, opérations USB et diagnostic des erreurs |
| [docs/compatibilite.md](docs/compatibilite.md) | Profil validé et limites de transposition |
| [docs/validation.md](docs/validation.md) | Mesures et résultat du test matériel |
| [docs/firmware.md](docs/firmware.md) | Archive officielle, empreintes et extraction |
| [analysis/static/REPORT.md](analysis/static/REPORT.md) | Analyse du recovery et fonctions examinées dans Ghidra |
| [analysis/ghidra-scripts/](analysis/ghidra-scripts/) | Scripts Java utilisés pour la décompilation et l’inspection |
| [vendor/PROVENANCE.md](vendor/PROVENANCE.md) | Origine et version de MiAssistantTool |

## Fichiers locaux et validation

`private/` contient les sauvegardes et les informations propres à chaque appareil. `artifacts/` contient les images de firmware et les résultats d’analyse. Ces dossiers sont exclus de Git et ne sont pas fournis par un clone. Voir [Conservation des fichiers](docs/maintenance.md).

Le transfert USB, la remise à zéro et la relecture ont été validés sur matériel. Les scripts publiés exposent en arguments les paramètres qui étaient fixés dans les scripts de ce test. Cette adaptation a été vérifiée hors appareil ; elle n’a pas fait l’objet d’un second effacement matériel. Le détail des contrôles est dans [Vérification des fichiers](docs/verification-archivage.md).

MiAssistantTool est inclus sous sa [licence Apache-2.0](vendor/MiAssistantTool/LICENSE). Cette licence ne s’étend pas aux images Xiaomi ni automatiquement au reste du dépôt.
