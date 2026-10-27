# MiAssistantTool

Source : https://github.com/MiForge/MiAssistantTool
Commit conservé : `4ac7b307d46265c382b971122ef65d162319e92f`.
Version du paquet : 1.4.4. Licence Apache-2.0 conservée dans MiAssistantTool/LICENSE.
Copie du code source utile, sans .git, build, egg-info ni caches.
Les scripts locaux utilisent les primitives de paquet USB de `miassistant.core`.
Ils évitent `connect_normal()` et son `set_configuration`, qui a perturbé la connexion pendant cette session.
Les scripts ne lancent pas la CLI tierce et ne dépendent pas de ses commandes de flash.
