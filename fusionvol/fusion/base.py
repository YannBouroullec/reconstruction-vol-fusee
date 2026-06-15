"""Contrat commun des estimateurs d'état et conteneur de résultat."""

from abc import ABC, abstractmethod

import numpy as np


class EtatVol:
    """État de vol reconstruit (résultat d'un estimateur).

    Les quatre tableaux partagent la même grille de temps.

    :ivar temps: instants (s).
    :ivar altitude: altitude reconstruite (m).
    :ivar vitesse: vitesse verticale reconstruite (m/s).
    :ivar acceleration: accélération verticale (m/s^2).
    :ivar nom: étiquette de la méthode ayant produit cet état.
    """

    def __init__(self, temps, altitude, vitesse, acceleration, nom="etat"):
        """Construit un état de vol.

        :param temps: instants (s).
        :type temps: numpy.ndarray
        :param altitude: altitude reconstruite (m).
        :type altitude: numpy.ndarray
        :param vitesse: vitesse verticale reconstruite (m/s).
        :type vitesse: numpy.ndarray
        :param acceleration: accélération verticale (m/s^2).
        :type acceleration: numpy.ndarray
        :param nom: étiquette de la méthode.
        :type nom: str
        """
        self.temps = np.asarray(temps, dtype=float)
        self.altitude = np.asarray(altitude, dtype=float)
        self.vitesse = np.asarray(vitesse, dtype=float)
        self.acceleration = np.asarray(acceleration, dtype=float)
        self.nom = nom

    def __len__(self):
        """Renvoie le nombre d'échantillons."""
        return len(self.temps)

    def __str__(self):
        """Renvoie un résumé lisible de l'état."""
        return "EtatVol('{nom}' : alt max {a:.0f} m, v max {v:.0f} m/s)".format(
            nom=self.nom,
            a=float(np.max(self.altitude)),
            v=float(np.max(self.vitesse)),
        )


class EstimateurEtat(ABC):
    """Interface commune à tous les estimateurs d'état.

    Un estimateur reçoit le temps, l'altitude barométrique et l'accélération
    verticale, et renvoie un :class:`EtatVol`. Toutes les implémentations
    (filtre complémentaire, estimateurs de référence) respectent ce contrat,
    ce qui permet au reste du programme de les utiliser de façon
    interchangeable.
    """

    @abstractmethod
    def estimer(self, temps, altitude, acceleration):
        """Reconstruit l'état de vol à partir des mesures.

        :param temps: instants (s).
        :type temps: numpy.ndarray
        :param altitude: altitude barométrique (m).
        :type altitude: numpy.ndarray
        :param acceleration: accélération verticale (m/s^2).
        :type acceleration: numpy.ndarray
        :return: l'état de vol reconstruit.
        :rtype: EtatVol
        """
        raise NotImplementedError


def integrer(valeurs, dt):
    """Intègre un signal par la méthode des trapèzes, valeur initiale nulle.

    :param valeurs: signal à intégrer.
    :type valeurs: numpy.ndarray
    :param dt: pas de temps (s).
    :type dt: float
    :return: intégrale cumulée, de même taille que l'entrée.
    :rtype: numpy.ndarray
    """
    valeurs = np.asarray(valeurs, dtype=float)
    increments = 0.5 * (valeurs[1:] + valeurs[:-1]) * dt
    return np.concatenate(([0.0], np.cumsum(increments)))


def lisser(valeurs, fenetre):
    """Lisse un signal par moyenne glissante centrée.

    :param valeurs: signal à lisser.
    :type valeurs: numpy.ndarray
    :param fenetre: taille de la fenêtre (nombre d'échantillons).
    :type fenetre: int
    :return: signal lissé, de même taille que l'entrée.
    :rtype: numpy.ndarray
    """
    valeurs = np.asarray(valeurs, dtype=float)
    if fenetre < 2:
        return valeurs
    noyau = np.ones(fenetre) / fenetre
    return np.convolve(valeurs, noyau, mode="same")