"""Estimateurs de référence, pour comparer avec le filtre complémentaire."""

import numpy as np

from fusionvol.fusion.base import EstimateurEtat, EtatVol, integrer, lisser


class EstimateurBaro(EstimateurEtat):
    """Estimateur n'utilisant que le baromètre.

    L'altitude est l'altitude barométrique telle quelle ; la vitesse est sa
    dérivée lissée. Altitude propre mais vitesse bruitée et en retard.

    :ivar fenetre_lissage: taille de la fenêtre de lissage de la dérivée.
    """

    def __init__(self, fenetre_lissage=21):
        """Initialise l'estimateur barométrique.

        :param fenetre_lissage: fenêtre de lissage (nombre d'échantillons).
        :type fenetre_lissage: int
        """
        self.fenetre_lissage = int(fenetre_lissage)

    def estimer(self, temps, altitude, acceleration):
        """Reconstruit l'état à partir du seul baromètre.

        :param temps: instants (s).
        :type temps: numpy.ndarray
        :param altitude: altitude barométrique (m).
        :type altitude: numpy.ndarray
        :param acceleration: accélération verticale (m/s^2).
        :type acceleration: numpy.ndarray
        :return: l'état de vol estimé.
        :rtype: EtatVol
        """
        temps = np.asarray(temps, dtype=float)
        altitude = np.asarray(altitude, dtype=float)
        dt = float(np.median(np.diff(temps)))
        vitesse = lisser(np.gradient(altitude, dt), self.fenetre_lissage)
        return EtatVol(temps, altitude, vitesse, acceleration, nom="Baro seul")


class EstimateurAccel(EstimateurEtat):
    """Estimateur n'utilisant que l'accéléromètre.

    La vitesse est l'intégrale de l'accélération et l'altitude sa double
    intégrale. Bon à court terme, mais dérive nettement sur la durée : c'est
    précisément ce que la fusion corrige.
    """

    def estimer(self, temps, altitude, acceleration):
        """Reconstruit l'état à partir du seul accéléromètre.

        :param temps: instants (s).
        :type temps: numpy.ndarray
        :param altitude: altitude barométrique (m), utilisée seulement pour
            l'altitude de départ.
        :type altitude: numpy.ndarray
        :param acceleration: accélération verticale (m/s^2).
        :type acceleration: numpy.ndarray
        :return: l'état de vol estimé.
        :rtype: EtatVol
        """
        temps = np.asarray(temps, dtype=float)
        acceleration = np.asarray(acceleration, dtype=float)
        dt = float(np.median(np.diff(temps)))
        vitesse = integrer(acceleration, dt)
        alt = altitude[0] + integrer(vitesse, dt)
        return EtatVol(temps, alt, vitesse, acceleration, nom="Accel seul")