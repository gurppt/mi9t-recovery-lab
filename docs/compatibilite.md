# Compatibilité

## Profil validé

| Paramètre | Valeur mesurée ou relevée |
|---|---|
| Modèle | Mi 9T / M1903F10G |
| Codename | `davinci` |
| Variante de ROM | `davinci_global` |
| Build | `V12.1.4.0.RFJMIXM` |
| Android | 11, SDK 30 |
| Correctif annoncé | 2021-06-01 |
| Interface recovery | Mi-Recovery 5.0 |
| Réponse de `getrecoveryversion:` | `2` ; valeur distincte du nom affiché par l’interface |
| Bootloader et partitions critiques | Verrouillés avant intervention |
| USB en MiAssistant | `18d1:4e11` |
| Processus de transfert | `recovery`, UID/GID 0 |
| SELinux | Permissif (`enforce=0`) |
| Partition | `/dev/block/sda9`, `PARTNAME=frp` |
| Taille | 524 288 octets / 512 Kio |
| Résultat | Écriture et relecture validées ; configuration Android terminée |

Le test matériel porte sur un seul appareil. Aucune matrice de compatibilité couvrant d’autres builds ou modèles n’est établie.

## Conditions techniques

La méthode dépend du recovery installé : disponibilité de `sync:`, accès aux périphériques bloc, droits du processus et restrictions effectivement appliquées. La disposition des partitions détermine le chemin et la taille à utiliser.

Le nom commercial, la version majeure de MIUI ou le libellé « Recovery 5.0 » ne prouvent pas que ces conditions sont réunies. Une mise à jour peut modifier le service de transfert sans changer la référence matérielle.

Les propriétés `ro.adb.secure=1` et `ro.debuggable=0` ne décrivent pas à elles seules les restrictions du miniadbd intégré au recovery. Les droits ont été mesurés en lisant `/proc/self/status` par le service lui-même.

## Limites du profil fourni

Les scripts fixent l’identifiant USB, l’interface `(0, 0)`, le chemin `sda9` et la taille de 512 Kio. Ils ne découvrent pas automatiquement la partition FRP et ne sélectionnent pas un profil selon la ROM.

Le contrôle de `PARTNAME=frp` avant écriture évite d’écrire sur une partition portant un autre nom. Il ne prouve pas que la remise à zéro soit appropriée pour n’importe quel firmware utilisant ce nom.

La sauvegarde FRP couvre uniquement cette partition. Elle ne remplace pas une sauvegarde complète de l’appareil.

## Autres appareils ou autres builds

Avant toute adaptation, identifier le build exact, examiner son recovery, vérifier le service en lecture, relever les droits effectifs et confirmer le mapping des partitions sur l’appareil. La sauvegarde doit toujours provenir de l’appareil concerné et de son état courant.

Remplacer uniquement le numéro de série dans les commandes ne constitue pas une adaptation du profil. Les modifications de chemins, de tailles ou de protocole doivent être validées séparément.

Aucun résultat n’est établi pour le verrouillage de compte Xiaomi, le mode EDL, les versions ultérieures de MIUI ou la récupération de données utilisateur.
