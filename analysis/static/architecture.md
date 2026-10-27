# Architecture du recovery et du transfert USB

## Périmètre

Firmware Xiaomi Mi 9T `davinci_global`, build `V12.1.4.0.RFJMIXM`, Android 11. L’image `recovery.img` contient un exécutable ARM64 `recovery`, la bibliothèque `librecovery_ui_ext.so`, un exécutable `adbd` distinct et les fichiers d’initialisation du recovery.

Le point d’entrée de `recovery` appelle `minadbd_main`. L’analyse concerne ce miniadbd intégré, exposé dans le mode MiAssistant. Les propriétés du daemon ADB Android ordinaire ne suffisent pas à décrire ses droits.

## Transport

```text
Script Python
  → PyUSB / libusb
  → interface USB 18d1:4e11
  → paquets ADB CNXN, OPEN, WRTE, OKAY, CLSE
  → service sync:
  → commandes SYNC RECV / SEND / DATA / DONE
  → accès aux fichiers du recovery et aux périphériques bloc
```

Les paquets ADB assurent la connexion et le transport des flux. Le protocole SYNC, encapsulé dans ce flux, porte les opérations de fichiers. Une réponse ADB `OKAY` accuse réception d’un paquet ; le résultat SYNC final et la relecture de la partition apportent des contrôles supplémentaires.

## Deux chemins de traitement

`service_mi_fd` distribue les noms de services. La commande Xiaomi `format-frp` rejoint un traitement du recovery parent qui vérifie un jeton et une réponse RSA. Le service `sync:` rejoint directement `file_sync_service` dans le chemin examiné, sans appliquer cette vérification de jeton.

La commande `RECV` lit le chemin demandé ; `SEND` ouvre le chemin d’écriture. Les restrictions de taille des messages n’impliquent pas une restriction des chemins aux fichiers ordinaires. L’accès au périphérique bloc FRP a été confirmé par lecture puis écriture.

## Droits et partition

Le processus mesuré par `/proc/self/status` est `recovery`, UID/GID 0. SELinux est permissif. Le nom `frp` de la partition `sda9` a été confirmé par sysfs ; sa lecture complète retourne 524 288 octets.

La table `rawprogram0.xml` de la ROM décrit une partition FRP sur le LUN 0, à partir du secteur 384, avec des secteurs de 4096 octets. Cette table est une référence statique ; le chemin Linux utilisé pour l’écriture a été vérifié indépendamment sur l’appareil.

La validation de signature d’une ROM, le verrouillage du bootloader et l’autorisation d’une commande Xiaomi sont des mécanismes distincts des permissions du service de transfert. L’intervention n’a pas nécessité de modifier ces mécanismes.
