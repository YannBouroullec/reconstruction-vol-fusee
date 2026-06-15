"""Replay animé du vol, exporté en GIF."""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
import numpy as np


class ReplayVol:
    """Construit une animation du vol reconstruit et l'enregistre en GIF.

    Un marqueur suit la trajectoire altitude-temps pendant que des indicateurs
    (vitesse, Mach) défilent. Les images sont sous-échantillonnées pour garder
    un fichier de taille raisonnable.

    :ivar fps: nombre d'images par seconde du GIF.
    :ivar duree_max: durée maximale de l'animation (s).
    """

    def __init__(self, fps=25, duree_max=12.0):
        """Initialise le générateur d'animation.

        :param fps: images par seconde.
        :type fps: int
        :param duree_max: durée cible de l'animation (s).
        :type duree_max: float
        """
        self.fps = int(fps)
        self.duree_max = float(duree_max)

    def animer(self, etat, analyse, phases, chemin="replay.gif"):
        """Crée l'animation et l'enregistre.

        :param etat: état de vol reconstruit.
        :type etat: fusionvol.fusion.base.EtatVol
        :param analyse: analyse de performance configurée.
        :type analyse: fusionvol.analyse.performance.AnalysePerformance
        :param phases: phases détectées.
        :type phases: fusionvol.analyse.phases.Phases
        :param chemin: chemin du GIF de sortie.
        :type chemin: str
        :return: le chemin du fichier écrit.
        :rtype: str
        """
        fin = phases.indices["atterrissage"]
        t = etat.temps[:fin]
        alt = etat.altitude[:fin]
        vit = etat.vitesse[:fin]
        mach = analyse.mach(etat)[:fin]

        # Nombre d'images visé, et pas de sous-échantillonnage associé.
        nb_images = max(1, int(self.fps * self.duree_max))
        pas = max(1, len(t) // nb_images)
        cadre = range(0, len(t), pas)

        fig, ax = plt.subplots(figsize=(9, 6))
        ax.plot(t, alt, color="#bdbdbd", lw=1.2)
        ax.set_xlim(t[0], t[-1])
        ax.set_ylim(min(0, alt.min()) - 50, alt.max() * 1.1)
        ax.set_xlabel("Temps [s]")
        ax.set_ylabel("Altitude AGL [m]")
        ax.set_title("Replay du vol : " + etat.nom, fontweight="bold")
        ax.grid(alpha=0.25)

        (trace,) = ax.plot([], [], color="#1a237e", lw=2)
        marqueur = ax.scatter([], [], color="#c62828", s=80, zorder=5)
        texte = ax.text(0.02, 0.95, "", transform=ax.transAxes, fontsize=11,
                        va="top", family="monospace",
                        bbox=dict(boxstyle="round", fc="white", alpha=0.8))

        def dessiner(i):
            """Met à jour une image de l'animation."""
            trace.set_data(t[: i + 1], alt[: i + 1])
            marqueur.set_offsets([[t[i], alt[i]]])
            texte.set_text(
                "t     {:6.1f} s\nalt   {:6.0f} m\nv     {:6.0f} m/s\nMach  {:5.2f}".format(
                    t[i], alt[i], vit[i], mach[i]
                )
            )
            return trace, marqueur, texte

        animation = FuncAnimation(fig, dessiner, frames=cadre, blit=True)
        animation.save(chemin, writer=PillowWriter(fps=self.fps))
        plt.close(fig)
        return chemin