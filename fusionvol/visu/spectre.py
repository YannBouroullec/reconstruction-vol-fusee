"""Spectrogramme du signal d'accélération (analyse fréquentielle)."""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


class Spectrogramme:
    """Calcule et trace le spectrogramme de l'accélération.

    Le signal est découpé en fenêtres successives qui se recouvrent ; sur
    chacune on applique une fenêtre de Hann puis une transformée de Fourier
    rapide. On obtient ainsi l'évolution du contenu fréquentiel au cours du
    temps (vibrations du moteur, oscillations sous parachute).

    :ivar taille_fenetre: nombre d'échantillons par fenêtre.
    :ivar recouvrement: fraction de recouvrement entre fenêtres, dans [0, 1[.
    """

    def __init__(self, taille_fenetre=256, recouvrement=0.5):
        """Initialise le spectrogramme.

        :param taille_fenetre: taille des fenêtres (nombre d'échantillons).
        :type taille_fenetre: int
        :param recouvrement: fraction de recouvrement, dans [0, 1[.
        :type recouvrement: float
        """
        self.taille_fenetre = int(taille_fenetre)
        self.recouvrement = float(recouvrement)

    def calculer(self, temps, signal):
        """Calcule le spectrogramme.

        :param temps: instants (s).
        :type temps: numpy.ndarray
        :param signal: signal à analyser (par exemple l'accélération).
        :type signal: numpy.ndarray
        :return: triplet (fréquences en Hz, instants en s, amplitudes en dB).
        :rtype: tuple(numpy.ndarray, numpy.ndarray, numpy.ndarray)
        """
        temps = np.asarray(temps, dtype=float)
        signal = np.asarray(signal, dtype=float)
        dt = float(np.median(np.diff(temps)))
        n = self.taille_fenetre
        pas = max(1, int(n * (1.0 - self.recouvrement)))
        fenetre = np.hanning(n)

        colonnes = []
        instants = []
        for debut in range(0, len(signal) - n, pas):
            morceau = signal[debut:debut + n] * fenetre
            spectre = np.abs(np.fft.rfft(morceau))
            colonnes.append(spectre)
            instants.append(temps[debut + n // 2])

        amplitudes = np.array(colonnes).T
        amplitudes_db = 20.0 * np.log10(amplitudes + 1e-9)
        freqs = np.fft.rfftfreq(n, dt)
        return freqs, np.array(instants), amplitudes_db

    def tracer(self, temps, signal, chemin=None):
        """Trace le spectrogramme sous forme de carte de chaleur.

        :param temps: instants (s).
        :type temps: numpy.ndarray
        :param signal: signal à analyser.
        :type signal: numpy.ndarray
        :param chemin: chemin de sauvegarde. Si ``None``, pas d'enregistrement.
        :type chemin: str or None
        :return: la figure produite.
        :rtype: matplotlib.figure.Figure
        """
        freqs, instants, amplitudes = self.calculer(temps, signal)
        fig, ax = plt.subplots(figsize=(11, 5))
        carte = ax.pcolormesh(instants, freqs, amplitudes, shading="auto", cmap="magma")
        fig.colorbar(carte, ax=ax, label="Amplitude [dB]")
        ax.set_xlabel("Temps [s]")
        ax.set_ylabel("Fréquence [Hz]")
        ax.set_title("Spectrogramme de l'accélération", fontweight="bold")
        fig.tight_layout()
        if chemin is not None:
            fig.savefig(chemin, dpi=140, bbox_inches="tight")
            plt.close(fig)
        return fig