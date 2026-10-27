# Procédure du profil validé

## 1. Préparer la connexion

Ouvrir Mi Recovery (Power + Volume haut), puis **Connect with MiAssistant**. Brancher un câble USB de données sur un port fiable. Pendant la session, le port arrière a fonctionné ; les erreurs noyau `-110` / `-71` sur un autre port empêchaient même l’identification USB.

`lsusb` doit montrer `18d1:4e11`. Son libellé générique « Google Nexus One » n’identifie pas le modèle : le journal noyau indiquait Xiaomi Mi 9T. Éviter qu’un serveur adb ou un autre utilitaire monopolise l’interface pendant l’accès direct PyUSB.

Les scripts n’appellent pas `set_configuration` : la configuration USB existante est utilisée. Ils ne fournissent pas de shell Android.

## 2. Vérifications en lecture

```sh
.venv/bin/python scripts/read_config.py /prop.default
.venv/bin/python scripts/read_config.py /proc/self/status
.venv/bin/python scripts/read_config.py /sys/fs/selinux/enforce
.venv/bin/python scripts/read_config.py /sys/class/block/sda9/uevent
```

Résultats du cas validé : MIUI `V12.1.4.0.RFJMIXM`, Android 11, UID/GID 0, SELinux `0`, `PARTNAME=frp`, `DEVNAME=sda9`.
Si le service n’est pas accessible ou si ces éléments divergent, arrêter la reproduction et réexaminer le firmware/mapping. Un nom de partition correct ne suffit pas à établir la compatibilité de toutes les autres versions.

## 3. Sauvegarde fraîche

Utiliser le numéro de série USB réellement relevé sur l’appareil et un nom de sauvegarde neuf. Les valeurs entre chevrons ci-dessous sont des paramètres à remplacer, pas des valeurs de la session à réutiliser.

```sh
.venv/bin/python scripts/read_config.py /dev/block/sda9 --serial '<SERIAL>' --backup private/frp-nouvelle-session.bin
sha256sum private/frp-nouvelle-session.bin
```

La création est exclusive : un fichier existant n’est pas écrasé. La taille attendue pour ce profil est exactement 524 288 octets. Conserver l’empreinte affichée. Une sauvegarde doit provenir de l’appareil concerné, au moment de cette intervention ; ne pas utiliser celle du premier téléphone sur un autre.

## 4. Écriture contrôlée

Uniquement après validation du profil ci-dessus et avec la sauvegarde fraîche :

```sh
.venv/bin/python scripts/reset_frp.py --serial '<SERIAL>' --backup private/frp-nouvelle-session.bin --backup-sha256 '<SHA256>' --execute
```

Le script vérifie le numéro de série USB, la taille et l’empreinte de la sauvegarde, le nom `frp` dans sysfs et l’égalité complète entre la partition actuelle et sa sauvegarde. Il écrit ensuite des zéros uniquement dans `/dev/block/sda9`, attend le résultat du service et relit les 524 288 octets.

Résultat attendu :

```text
IDENTITY_AND_BACKUP_VERIFIED
WRITE_ACCEPTED
VERIFIED_ZEROED_524288_BYTES
```

L’écriture n’est pas atomique. En cas d’erreur ou de déconnexion pendant cette phase, ne pas considérer l’opération comme réussie et ne pas redémarrer automatiquement. Préserver la sauvegarde et examiner l’état réel avant toute nouvelle écriture. Aucun outil de restauration automatique n’a été validé ici.

## 5. Validation utilisateur

Après le message de relecture réussie, quitter MiAssistant et choisir **Reboot → Reboot to System**. Refaire la configuration. Le succès final est l’absence de demande de l’ancien compte Google, pas seulement l’acceptation d’un paquet USB.

Dans la session archivée, le propriétaire a confirmé ce succès. Aucun effacement supplémentaire ni flash n’a été nécessaire.
