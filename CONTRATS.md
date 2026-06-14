# Contrats partagés (à figer avant de coder)

Ce fichier est la référence commune. Tant que chacun respecte ces interfaces,
les trois parties se développent sans se marcher dessus.

## Format des CSV d'entrée (les 4 vols EuRoC)

Colonnes brutes, identiques dans les 4 fichiers, échantillonnées à 100 Hz :

- `ts` : temps en secondes, 0 = décollage, commence à -0,75 s (pré-rampe)
- `filtered_altitude_AGL` : altitude au-dessus du sol en mètres
- `filtered_acceleration` : accélération verticale en m/s^2, **gravité déjà
  retirée** (proche de 0 au repos), donc directement intégrable

Pièges connus : la fenêtre `ts < 0` contient déjà l'allumage (ne pas calibrer
le biais dessus), et le fichier est complété par des zéros après l'atterrissage.

## Sortie de `DonneesCapteurs` (Personne A -> tout le monde)

Objet avec les attributs : `temps`, `altitude`, `acceleration` (tableaux numpy
alignés), `dt`, `frequence`, `nom`.

## API de `Atmosphere` (Personne A -> Personne C)

`Atmosphere(elevation_sol=160.0)` avec : `temperature(alt)`, `pression(alt)`,
`densite(alt)`, `vitesse_son(alt)`. L'altitude passée est AGL (au-dessus du sol).

## Contrat des estimateurs (Personne B -> Personne C)

Toute classe d'estimation hérite de `EstimateurEtat` et implémente :

    estimer(temps, altitude, acceleration) -> EtatVol

`EtatVol` expose : `temps`, `altitude`, `vitesse`, `acceleration`, `nom`.

## Important

Personne B n'importe PAS le code de Personne A et inversement. B teste son
filtre en lisant directement un des CSV avec pandas (renommage de colonnes).
C'est ce qui rend A et B totalement indépendants.