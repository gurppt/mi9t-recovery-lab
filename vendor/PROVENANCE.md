# Provenance de MiAssistantTool

| Élément | Valeur |
|---|---|
| Projet | [MiForge/MiAssistantTool](https://github.com/MiForge/MiAssistantTool) |
| Commit importé | `4ac7b307d46265c382b971122ef65d162319e92f` |
| Version du paquet | `miasst` 1.4.4 |
| Licence | [Apache-2.0](MiAssistantTool/LICENSE) |

La copie contient le paquet Python, son fichier de construction, sa documentation et sa licence. Les métadonnées Git, les sorties de construction et les caches ne sont pas inclus.

Les scripts du projet utilisent les primitives de paquets ADB de `miassistant.core`. Ils ouvrent eux-mêmes l’interface PyUSB et utilisent la configuration active, sans appeler `connect_normal()` ni son `set_configuration`. Une reconfiguration USB a provoqué des déconnexions pendant les essais.

La CLI tierce et ses commandes de flash ne sont pas utilisées par la procédure. `miassistant/core.py` a été comparé à la bibliothèque installée lors du test matériel : les fichiers sont identiques.
