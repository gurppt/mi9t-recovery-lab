# Constats techniques

## Accès à la partition FRP depuis le service de transfert

Sur le recovery testé, un hôte USB connecté au mode MiAssistant peut ouvrir `sync:`, lire `/dev/block/sda9` et y écrire sans fournir la réponse cryptographique exigée par `format-frp:`.

Le processus a les droits root et SELinux est permissif. Après confirmation du nom `frp`, sauvegarde et comparaison de l’état courant, l’écriture de 524 288 octets nuls a été acceptée. La relecture intégrale a confirmé le contenu écrit et la configuration Android a pu être terminée sans l’ancien compte Google.

Le résultat est établi pour un Mi 9T M1903F10G sous V12.1.4.0.RFJMIXM. L’accès USB physique et le mode MiAssistant sont nécessaires au scénario testé.

## Contrôle cryptographique de la commande Xiaomi

`format-frp:` refuse les demandes sans jeton ou sans réponse RSA valide. Aucun défaut du traitement RSA n’a été établi. Le service de transfert constitue un chemin distinct ; son résultat ne prouve pas que le contrôle cryptographique ait été cassé.

## Limites

Aucun test sur d’autres versions, aucune évaluation exhaustive du recovery, aucun test de restauration après interruption et aucun contournement du verrouillage de compte Xiaomi ne sont documentés.

Les fonctions et leurs adresses sont dans le [rapport technique](REPORT.md). Les preuves dynamiques sont décrites dans [Validation](../../docs/validation.md).
