"""Modèle d'atmosphère normalisée internationale (ISA), troposphère."""

import numpy as np


class Atmosphere:
    """Atmosphère normalisée ISA limitée à la troposphère (0 à 11 km).

    Le modèle donne la température, la pression, la masse volumique et la
    vitesse du son en fonction de l'altitude. Comme les journaux fournissent
    une altitude au-dessus du sol (AGL), on ajoute l'altitude du site de
    lancement pour retrouver l'altitude réelle au-dessus du niveau de la mer
    (ASL), seule grandeur valable dans les formules ISA.

    :ivar elevation_sol: altitude du site de lancement au-dessus du niveau de
        la mer (m).
    """

    #: Température au niveau de la mer (K).
    T0 = 288.15
    #: Gradient thermique troposphérique (K/m).
    L = 0.0065
    #: Pression au niveau de la mer (Pa).
    P0 = 101325.0
    #: Accélération de la pesanteur (m/s^2).
    G = 9.80665
    #: Constante spécifique de l'air sec (J/(kg.K)).
    R = 287.05
    #: Rapport des chaleurs massiques de l'air.
    GAMMA = 1.4

    def __init__(self, elevation_sol=160.0):
        """Initialise le modèle pour un site de lancement donné.

        :param elevation_sol: altitude du site au-dessus du niveau de la mer
            (m). La valeur par défaut correspond au champ de tir EuRoC de
            Ponte de Sor.
        :type elevation_sol: float
        """
        self.elevation_sol = float(elevation_sol)

    def _altitude_asl(self, altitude_agl):
        """Convertit une altitude sol en altitude au-dessus du niveau de la mer.

        :param altitude_agl: altitude au-dessus du sol (m).
        :type altitude_agl: float or numpy.ndarray
        :return: altitude au-dessus du niveau de la mer (m).
        :rtype: float or numpy.ndarray
        """
        return np.asarray(altitude_agl, dtype=float) + self.elevation_sol

    def temperature(self, altitude_agl):
        """Température de l'air à une altitude donnée.

        :param altitude_agl: altitude au-dessus du sol (m).
        :type altitude_agl: float or numpy.ndarray
        :return: température (K).
        :rtype: float or numpy.ndarray
        """
        return self.T0 - self.L * self._altitude_asl(altitude_agl)

    def pression(self, altitude_agl):
        """Pression de l'air à une altitude donnée.

        :param altitude_agl: altitude au-dessus du sol (m).
        :type altitude_agl: float or numpy.ndarray
        :return: pression (Pa).
        :rtype: float or numpy.ndarray
        """
        temp = self.temperature(altitude_agl)
        return self.P0 * (temp / self.T0) ** (self.G / (self.R * self.L))

    def densite(self, altitude_agl):
        """Masse volumique de l'air à une altitude donnée.

        :param altitude_agl: altitude au-dessus du sol (m).
        :type altitude_agl: float or numpy.ndarray
        :return: masse volumique (kg/m^3).
        :rtype: float or numpy.ndarray
        """
        return self.pression(altitude_agl) / (self.R * self.temperature(altitude_agl))

    def vitesse_son(self, altitude_agl):
        """Vitesse du son à une altitude donnée.

        :param altitude_agl: altitude au-dessus du sol (m).
        :type altitude_agl: float or numpy.ndarray
        :return: vitesse du son (m/s).
        :rtype: float or numpy.ndarray
        """
        return np.sqrt(self.GAMMA * self.R * self.temperature(altitude_agl))

    def __str__(self):
        """Renvoie un résumé lisible du modèle."""
        return "Atmosphere(ISA, site a {:.0f} m ASL)".format(self.elevation_sol)