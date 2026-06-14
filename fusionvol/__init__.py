"""fusionvol : reconstruction de trajectoire de vol de fusée par fusion de capteurs.

Le paquet combine une altitude barométrique et une accélération verticale pour
reconstruire l'état de vol (altitude, vitesse, accélération), détecter les phases
de vol et calculer des indicateurs de performance (apogée, vitesse max, nombre de
Mach, max-Q, coefficient de traînée).

Organisation (une responsabilité par sous-paquet) :

* ``capteurs``   : lecture et mise en forme des données capteurs (Personne A)
* ``atmosphere`` : modèle d'atmosphère normalisée ISA (Personne A)
* ``fusion``     : estimateurs d'état, dont le filtre complémentaire (Personne B)
* ``analyse``    : détection de phases et indicateurs de performance (Personne C)
* ``visu``       : graphiques, replay animé et spectrogramme (Personne C)
* ``interface``  : lecture du fichier de configuration YAML (Personne C)
"""

__version__ = "0.1.0"