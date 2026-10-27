# Portée et adaptation

La méthode dépend de l’implémentation du recovery : exposition de `sync:`, absence de restriction bloquant le chemin visé, droits du processus, état SELinux et disposition des partitions. Elle n’est ni strictement liée au nom commercial du Mi 9T, ni démontrée sur tous les modèles similaires.

| Élément | Vérifié dans cette session |
|---|---|
| Modèle | M1903F10G, Mi 9T, davinci |
| Firmware | V12.1.4.0.RFJMIXM, Android 11 |
| Correctif annoncé | 2021-06-01 |
| Recovery affiché | Mi-Recovery 5.0 |
| Valeur API getrecoveryversion | 2 ; ne pas confondre avec l’interface 5.0 |
| Bootloader | verrouillé avant intervention |
| USB | 18d1:4e11, mode MiAssistant |
| Processus qui lit les fichiers | recovery, UID/GID 0 |
| SELinux | permissif, enforce=0 |
| Partition confirmée sur appareil | sda9, PARTNAME=frp, 524 288 octets |
| Résultat | lecture/écriture/relecture puis configuration réussie |

Pour un autre téléphone : récupérer et identifier sa version exacte, analyser son recovery, confirmer l’accès en lecture et le mapping réel, puis sauvegarder sa propre partition. Le nom `sda9` et la taille ne doivent jamais être déduits du seul modèle commercial. Les scripts fournis ne font pas cette adaptation automatiquement.

Même appareil après mise à jour : refaire les vérifications. Aucun test des MIUI plus récents, du verrouillage de compte Xiaomi, du mode EDL ou d’une récupération de données utilisateur n’a été effectué. La sauvegarde FRP n’est pas une sauvegarde complète du téléphone.
