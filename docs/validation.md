# Résultats du test matériel

Test réalisé le **27 octobre 2026** sur le [profil Mi 9T / V12.1.4.0.RFJMIXM](compatibilite.md).

## Accès au recovery

L’appareil est détecté en USB sous `18d1:4e11` avec les descripteurs Xiaomi / Mi 9T. L’ouverture du service `sync:` réussit depuis une connexion directe PyUSB.

La lecture de `/prop.default` retourne **31 499 octets**, avec le SHA256 suivant :

```text
09a80cf6f96168e034bdb880f72c633d3883a7746b9e7a2570ef0ac58fb78ce0
```

Les propriétés indiquent `V12.1.4.0.RFJMIXM`, Android 11, SDK 30 et le correctif `2021-06-01`.

## Droits effectifs

Lecture de `/proc/self/status` :

```text
Name:       recovery
Uid:        0  0  0  0
Gid:        0  0  0  0
CapEff:     0000003fffffffff
NoNewPrivs: 0
Seccomp:    0
```

Lecture de `/sys/fs/selinux/enforce` : `0`.

Ces valeurs proviennent du système en cours d’exécution. Elles complètent la configuration trouvée dans l’image du firmware.

## Identification et sauvegarde

Lecture de `/sys/class/block/sda9/uevent` :

```text
MAJOR=8
MINOR=9
DEVNAME=sda9
DEVTYPE=partition
PARTN=9
PARTNAME=frp
```

La lecture intégrale de `/dev/block/sda9` retourne **524 288 octets**. La sauvegarde est écrite localement avec le mode `0600`, puis utilisée pour une comparaison complète avant écriture. Le numéro de série et le contenu de cette sauvegarde ne sont pas publiés.

## Écriture et résultat

Le transfert écrit 524 288 octets nuls dans la partition identifiée. Le recovery accepte le transfert et la relecture complète correspond exactement au contenu attendu :

```text
IDENTITY_AND_BACKUP_VERIFIED
WRITE_ACCEPTED
VERIFIED_ZEROED_524288_BYTES
```

Après redémarrage, la configuration Android peut être terminée sans authentification avec l’ancien compte Google. Aucun flash, déverrouillage de bootloader ni modification de modem/persist n’a été nécessaire.

## Chemin non utilisé

La commande Xiaomi `format-frp:` retourne `failed_mitoken_is_NULL` sans jeton initialisé, puis `failed_decrypt_error` sans réponse cryptographique valide. La récupération repose sur le service de transfert `sync:`, pas sur la production d’un jeton accepté par cette commande.

Le batch Windows cité dans l’analyse n’a pas été exécuté. Les opérations ont été limitées à la partition FRP avec les scripts Python.

## Portée de la validation

Le protocole, les lectures, la sauvegarde, l’écriture et la relecture ont été exécutés avec les scripts de test dont les paramètres étaient fixés pour l’appareil. Les scripts publiés utilisent des arguments pour le numéro de série, le chemin de sauvegarde et son empreinte ; ils exigent également `--execute` pour l’écriture.

Cette adaptation a été vérifiée par compilation Python, contrôles de CLI et refus d’exécution sans l’option dédiée. Elle n’a pas été réexécutée en écriture sur un second appareil. Aucun test de coupure pendant transfert ni restauration de sauvegarde n’a été effectué.
