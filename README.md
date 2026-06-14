# fusionvol

Projet de session MGA802. On reconstruit la trajectoire d'une fusée à partir de
deux capteurs seulement : un baromètre (altitude) et un accéléromètre (axe
vertical). Aucun des deux n'est suffisant tout seul. L'accéléromètre est précis
sur l'instant mais dès qu'on l'intègre pour remonter à la vitesse puis à
l'altitude, l'erreur s'accumule et le résultat part en vrille au bout de
quelques dizaines de secondes. Le baromètre lui reste juste sur la durée mais il
est bruité et un peu en retard. L'idée du projet, c'est de fusionner les deux
pour récupérer le meilleur de chacun.

À partir de là, le programme détecte les phases du vol (décollage, fin de
poussée, apogée, descente), calcule des indicateurs (apogée, vitesse max, Mach,
pression dynamique max) et sort plusieurs visualisations dont un replay animé du
vol.

## Données

On part de vrais journaux de vol de fusées étudiantes européennes (compétition
EuRoC), récupérés depuis le dépôt RocketPy. Les fichiers donnent le temps,
l'altitude au-dessus du sol et l'accélération verticale, échantillonnés à
100 Hz. Pour chacun on connaît l'apogée réelle, ce qui sert à vérifier que notre
reconstruction tient la route.

## Installation

On conseille un environnement virtuel.

```
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -e .
```

## Utilisation

Tout se règle dans `deck.yaml` (fichier d'entrée, site de lancement, réglage du
filtre, masse de la fusée, sorties voulues). Ensuite :

```
python main.py
```

ou avec un autre deck :

```
python main.py mon_deck.yaml
```

Les graphiques et le GIF arrivent dans le dossier `sorties/`.

## Organisation du code

Le paquet est découpé en sous-paquets, un par grande tâche :

- `capteurs` : lecture et mise en forme des CSV
- `atmosphere` : modèle d'atmosphère ISA
- `fusion` : les estimateurs d'état (filtre complémentaire et références)
- `analyse` : détection de phases et indicateurs
- `visu` : graphiques, replay animé, spectrogramme
- `interface` : lecture du deck YAML

## Équipe

Théo Malavieille, Pierre-Jean Tulasne, Yann Bouroullec