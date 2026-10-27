# Validation du 27 octobre 2026

Ce document complète le rapport statique historique, dont les mentions « non testé » décrivent l’état AVANT les essais sur l’appareil.

1. Détection Mi 9T en MiAssistant après résolution d’erreurs physiques de communication USB.
2. Ouverture de `sync:` et lecture de `/prop.default` : 31 499 octets, SHA256 `09a80cf6f96168e034bdb880f72c633d3883a7746b9e7a2570ef0ac58fb78ce0`.
3. `/proc/self/status` : Name=recovery, UID/GID=0, CapEff=0000003fffffffff, NoNewPrivs=0, Seccomp=0.
4. `/sys/fs/selinux/enforce` : `0`.
5. `/sys/class/block/sda9/uevent` : DEVNAME=sda9, DEVTYPE=partition, PARTN=9, PARTNAME=frp.
6. Sauvegarde locale de la partition complète, 524 288 octets, droits 0600. Identité et empreinte conservées dans `private/device.json`.
7. Relecture avant écriture égale à la sauvegarde ; remise à zéro ; relecture complète égale à 524 288 octets nuls.
8. Retour utilisateur après redémarrage et configuration : « ça marche ».

La commande propriétaire `format-frp:` avait échoué précédemment avec `failed_mitoken_is_NULL`, puis `failed_decrypt_error`. Aucun jeton valide n’a été obtenu, aucune clé RSA n’a été cassée. Le chemin utilisé avec succès est le transfert de fichiers du recovery.

Les scripts ont été écrits pendant cette session en Python, avec les primitives de paquets de MiAssistantTool. Le batch Windows tiers n’a pas été exécuté : il modifiait également modem/persist, hors de l’intervention nécessaire.

## Archivage et reproductibilité

`private/original-scripts/` conserve exactement les deux scripts exécutés avec succès, avec leurs paramètres propres au premier appareil. Ne pas les relancer tels quels : leurs anciens chemins de travail sont volontairement conservés comme preuve historique.

`scripts/` contient les versions portables : chemins de sauvegarde et identité explicitement passés en arguments, contrôle destructif `--execute`, et vérifications d’empreinte explicites (non supprimées par `python -O`). Le protocole de transfert et le profil de partition restent ceux de la session. Les changements d’interface sont vérifiés hors matériel ; aucune seconde intervention n’a été lancée pour tester l’archivage.
