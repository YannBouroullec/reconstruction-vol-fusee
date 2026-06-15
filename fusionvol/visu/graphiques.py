"""Graphiques statiques du vol reconstruit."""

import matplotlib

matplotlib.use("Agg")  # backend sans fenêtre, pour enregistrer des fichiers
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import numpy as np


class GraphiquesVol:
    """Produit les graphiques statiques d'un vol.

    Regroupe le profil complet (altitude, vitesse/Mach, pression dynamique),
    la comparaison des estimateurs et le portrait de phase.
    """

    COULEURS_PHASES = {"propulsion": "#ff7043", "balistique": "#42a5f5", "descente": "#9ccc65"}

    def _ombrer_phases(self, axe, etat, phases):
        """Ombre les trois grandes phases sur un axe temporel.

        :param axe: axe matplotlib à décorer.
        :type axe: matplotlib.axes.Axes
        :param etat: état de vol reconstruit.
        :type etat: fusionvol.fusion.base.EtatVol
        :param phases: phases détectées.
        :type phases: fusionvol.analyse.phases.Phases
        """
        t = etat.temps
        idx = phases.indices
        axe.axvspan(t[idx["decollage"]], t[idx["burnout"]], color=self.COULEURS_PHASES["propulsion"], alpha=0.12)
        axe.axvspan(t[idx["burnout"]], t[idx["apogee"]], color=self.COULEURS_PHASES["balistique"], alpha=0.12)
        axe.axvspan(t[idx["apogee"]], t[idx["atterrissage"]], color=self.COULEURS_PHASES["descente"], alpha=0.12)

    def profil_complet(self, etat, analyse, phases, chemin=None):
        """Trace le profil de vol en trois panneaux.

        :param etat: état de vol reconstruit.
        :type etat: fusionvol.fusion.base.EtatVol
        :param analyse: analyse de performance configurée.
        :type analyse: fusionvol.analyse.performance.AnalysePerformance
        :param phases: phases détectées.
        :type phases: fusionvol.analyse.phases.Phases
        :param chemin: chemin de sauvegarde. Si ``None``, la figure n'est pas
            enregistrée.
        :type chemin: str or None
        :return: la figure produite.
        :rtype: matplotlib.figure.Figure
        """
        t = etat.temps
        fin = min(phases.indices["atterrissage"] + 300, len(t))
        mach = analyse.mach(etat)
        q = analyse.pression_dynamique(etat) / 1000.0  # kPa
        idx = phases.indices

        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(11, 11), sharex=True)

        # Panneau 1 : altitude et événements.
        self._ombrer_phases(ax1, etat, phases)
        ax1.plot(t[:fin], etat.altitude[:fin], color="#1a237e", lw=1.6)
        for nom, couleur in [("decollage", "#37474f"), ("burnout", "#e65100"),
                             ("apogee", "#283593"), ("atterrissage", "#33691e")]:
            i = idx[nom]
            ax1.axvline(t[i], color=couleur, ls="--", lw=1, alpha=0.7)
            ax1.annotate(nom, (t[i], etat.altitude[i]), textcoords="offset points",
                         xytext=(4, 6), fontsize=9, color=couleur)
        ax1.set_ylabel("Altitude AGL [m]")
        ax1.set_title("Profil de vol reconstruit : " + etat.nom, fontweight="bold")
        ax1.grid(alpha=0.25)

        # Panneau 2 : vitesse et Mach.
        self._ombrer_phases(ax2, etat, phases)
        ax2.plot(t[:fin], etat.vitesse[:fin], color="#6a1b9a", lw=1.6)
        ax2.set_ylabel("Vitesse [m/s]", color="#6a1b9a")
        ax2.tick_params(axis="y", labelcolor="#6a1b9a")
        ax2.grid(alpha=0.25)
        axm = ax2.twinx()
        axm.plot(t[:fin], mach[:fin], color="#00897b", lw=1.2, alpha=0.8)
        axm.axhline(1.0, color="#b71c1c", ls=":", lw=1)
        axm.set_ylabel("Mach", color="#00897b")
        axm.tick_params(axis="y", labelcolor="#00897b")

        # Panneau 3 : pression dynamique et max-Q.
        self._ombrer_phases(ax3, etat, phases)
        ax3.plot(t[:fin], q[:fin], color="#c62828", lw=1.6)
        i_q = int(np.argmax(q[: idx["apogee"] + 1]))
        ax3.scatter([t[i_q]], [q[i_q]], color="#c62828", zorder=5)
        ax3.annotate("max-Q {:.1f} kPa".format(q[i_q]), (t[i_q], q[i_q]),
                     textcoords="offset points", xytext=(10, -2), fontsize=9,
                     color="#c62828", fontweight="bold")
        ax3.set_ylabel("Pression dyn. [kPa]")
        ax3.set_xlabel("Temps [s]")
        ax3.grid(alpha=0.25)

        legende = [Patch(facecolor=c, alpha=0.4, label=n)
                   for n, c in [("Propulsion", self.COULEURS_PHASES["propulsion"]),
                                ("Balistique", self.COULEURS_PHASES["balistique"]),
                                ("Descente", self.COULEURS_PHASES["descente"])]]
        ax1.legend(handles=legende, loc="upper right", framealpha=0.9)

        fig.tight_layout()
        if chemin is not None:
            fig.savefig(chemin, dpi=140, bbox_inches="tight")
            plt.close(fig)
        return fig

    def comparaison_estimateurs(self, etats, chemin=None):
        """Superpose l'altitude reconstruite par plusieurs estimateurs.

        Met en évidence la dérive de l'estimateur accéléromètre seul face au
        baromètre et à la fusion.

        :param etats: liste des états à comparer.
        :type etats: list(fusionvol.fusion.base.EtatVol)
        :param chemin: chemin de sauvegarde. Si ``None``, pas d'enregistrement.
        :type chemin: str or None
        :return: la figure produite.
        :rtype: matplotlib.figure.Figure
        """
        fig, ax = plt.subplots(figsize=(11, 6))
        for etat in etats:
            ax.plot(etat.temps, etat.altitude, lw=1.4, label=etat.nom)
        ax.set_xlabel("Temps [s]")
        ax.set_ylabel("Altitude AGL [m]")
        ax.set_title("Comparaison des estimateurs d'altitude", fontweight="bold")
        ax.grid(alpha=0.25)
        ax.legend()
        fig.tight_layout()
        if chemin is not None:
            fig.savefig(chemin, dpi=140, bbox_inches="tight")
            plt.close(fig)
        return fig

    def portrait_phase(self, etat, analyse, phases, chemin=None):
        """Trace l'altitude en fonction de la vitesse, colorée par le Mach.

        :param etat: état de vol reconstruit.
        :type etat: fusionvol.fusion.base.EtatVol
        :param analyse: analyse de performance configurée.
        :type analyse: fusionvol.analyse.performance.AnalysePerformance
        :param phases: phases détectées.
        :type phases: fusionvol.analyse.phases.Phases
        :param chemin: chemin de sauvegarde. Si ``None``, pas d'enregistrement.
        :type chemin: str or None
        :return: la figure produite.
        :rtype: matplotlib.figure.Figure
        """
        fin = phases.indices["atterrissage"]
        vit = etat.vitesse[:fin]
        alt = etat.altitude[:fin]
        mach = analyse.mach(etat)[:fin]

        fig, ax = plt.subplots(figsize=(8, 7))
        nuage = ax.scatter(vit, alt, c=mach, cmap="viridis", s=4)
        fig.colorbar(nuage, ax=ax, label="Mach")
        ax.set_xlabel("Vitesse [m/s]")
        ax.set_ylabel("Altitude AGL [m]")
        ax.set_title("Portrait de phase altitude-vitesse : " + etat.nom, fontweight="bold")
        ax.grid(alpha=0.25)
        fig.tight_layout()
        if chemin is not None:
            fig.savefig(chemin, dpi=140, bbox_inches="tight")
            plt.close(fig)
        return fig