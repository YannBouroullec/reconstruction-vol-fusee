"""Point d'entrée : reconstruit un vol à partir d'un deck de configuration.

Utilisation :

    python main.py            # utilise deck.yaml
    python main.py mon.yaml   # utilise un autre deck
"""

import os
import sys

from fusionvol.analyse import AnalysePerformance, DetecteurPhases
from fusionvol.atmosphere import Atmosphere
from fusionvol.capteurs import DonneesCapteurs
from fusionvol.fusion import EstimateurAccel, EstimateurBaro, FiltreComplementaire
from fusionvol.interface import LecteurDeck
from fusionvol.visu import GraphiquesVol, ReplayVol, Spectrogramme


def executer(chemin_deck="deck.yaml"):
    """Exécute la chaîne complète de reconstruction d'un vol.

    :param chemin_deck: chemin du fichier de configuration.
    :type chemin_deck: str
    """
    parametres = LecteurDeck().charger(chemin_deck)
    os.makedirs(parametres["dossier_sortie"], exist_ok=True)

    # 1. Lecture et mise en forme des données.
    donnees = DonneesCapteurs.depuis_csv(parametres["fichier"], nom=parametres["nom_vol"])
    donnees.corriger_biais()
    donnees.rogner_queue()
    print(donnees)

    # 2. Estimateurs d'état.
    atmosphere = Atmosphere(elevation_sol=parametres["elevation_sol"])
    fusion = FiltreComplementaire(alpha=parametres["alpha"], beta=parametres["beta"])
    etat = fusion.estimer(donnees.temps, donnees.altitude, donnees.acceleration)
    etat_baro = EstimateurBaro().estimer(donnees.temps, donnees.altitude, donnees.acceleration)
    etat_accel = EstimateurAccel().estimer(donnees.temps, donnees.altitude, donnees.acceleration)

    # 3. Détection de phases et indicateurs.
    phases = DetecteurPhases().detecter(etat)
    analyse = AnalysePerformance(atmosphere, parametres["masse"], parametres["surface_ref"])
    indicateurs = analyse.analyser(etat, phases)

    print("\nIndicateurs de performance")
    print("--------------------------")
    for nom, valeur in indicateurs.items():
        print("  {:<22} {:.2f}".format(nom, valeur))

    # 4. Visualisations.
    dossier = parametres["dossier_sortie"]
    graphiques = GraphiquesVol()
    if parametres["tracer_profil"]:
        graphiques.profil_complet(etat, analyse, phases, os.path.join(dossier, "profil.png"))
    if parametres["tracer_comparaison"]:
        graphiques.comparaison_estimateurs([etat, etat_baro, etat_accel],
                                           os.path.join(dossier, "comparaison.png"))
    if parametres["tracer_portrait"]:
        graphiques.portrait_phase(etat, analyse, phases, os.path.join(dossier, "portrait.png"))
    if parametres["tracer_spectrogramme"]:
        Spectrogramme().tracer(donnees.temps, donnees.acceleration,
                               os.path.join(dossier, "spectrogramme.png"))
    if parametres["creer_replay"]:
        ReplayVol(fps=parametres["fps_replay"]).animer(
            etat, analyse, phases, os.path.join(dossier, "replay.gif"))

    print("\nSorties écrites dans : " + dossier)


if __name__ == "__main__":
    deck = sys.argv[1] if len(sys.argv) > 1 else "deck.yaml"
    executer(deck)