"""Calcul des indicateurs de performance du vol."""

import numpy as np

#: Accélération de la pesanteur utilisée pour le bilan des forces (m/s^2).
G = 9.80665


class AnalysePerformance:
    """Calcule les indicateurs de performance d'un vol reconstruit.

    S'appuie sur l'état de vol (altitude, vitesse, accélération) et sur le
    modèle d'atmosphère pour produire l'apogée, la vitesse maximale, le nombre
    de Mach, la pression dynamique maximale (max-Q) et la courbe du coefficient
    de traînée en fonction du Mach.

    :ivar atmosphere: modèle d'atmosphère.
    :ivar masse: masse de la fusée (kg), pour le coefficient de traînée.
    :ivar surface_ref: surface de référence (m^2), pour le coefficient de
        traînée.
    """

    def __init__(self, atmosphere, masse=None, surface_ref=None):
        """Initialise l'analyse.

        :param atmosphere: modèle d'atmosphère.
        :type atmosphere: fusionvol.atmosphere.isa.Atmosphere
        :param masse: masse de la fusée (kg). Nécessaire seulement pour le
            coefficient de traînée.
        :type masse: float or None
        :param surface_ref: surface de référence (m^2). Nécessaire seulement
            pour le coefficient de traînée.
        :type surface_ref: float or None
        """
        self.atmosphere = atmosphere
        self.masse = masse
        self.surface_ref = surface_ref

    def mach(self, etat):
        """Renvoie le nombre de Mach au cours du vol.

        :param etat: état de vol reconstruit.
        :type etat: fusionvol.fusion.base.EtatVol
        :return: nombre de Mach pour chaque instant.
        :rtype: numpy.ndarray
        """
        return np.abs(etat.vitesse) / self.atmosphere.vitesse_son(etat.altitude)

    def pression_dynamique(self, etat):
        """Renvoie la pression dynamique au cours du vol.

        :param etat: état de vol reconstruit.
        :type etat: fusionvol.fusion.base.EtatVol
        :return: pression dynamique pour chaque instant (Pa).
        :rtype: numpy.ndarray
        """
        return 0.5 * self.atmosphere.densite(etat.altitude) * etat.vitesse ** 2

    def courbe_cd_mach(self, etat, phases, vitesse_min=30.0):
        """Renvoie le coefficient de traînée en fonction du Mach (phase balistique).

        On l'estime pendant la montée balistique (entre l'extinction du moteur
        et l'apogée), où la seule force en jeu (hors gravité) est la traînée :
        ``F = -m (a + g)``. Résultat expérimental, à interpréter avec prudence.

        :param etat: état de vol reconstruit.
        :type etat: fusionvol.fusion.base.EtatVol
        :param phases: phases détectées.
        :type phases: fusionvol.analyse.phases.Phases
        :param vitesse_min: vitesse en dessous de laquelle le calcul est ignoré
            (m/s), pour éviter la division par une vitesse trop faible.
        :type vitesse_min: float
        :return: couple (mach, coefficient de traînée).
        :rtype: tuple(numpy.ndarray, numpy.ndarray)
        :raises ValueError: si la masse ou la surface de référence est absente.
        """
        if self.masse is None or self.surface_ref is None:
            raise ValueError("masse et surface_ref sont requises pour le Cd")

        debut = phases.indices["burnout"]
        fin = phases.indices["apogee"]
        alt = etat.altitude[debut:fin]
        vit = etat.vitesse[debut:fin]
        acc = etat.acceleration[debut:fin]

        densite = self.atmosphere.densite(alt)
        force_trainee = -self.masse * (acc + G)
        cd = 2.0 * force_trainee / (densite * vit ** 2 * self.surface_ref)
        mach = vit / self.atmosphere.vitesse_son(alt)

        valides = vit > vitesse_min
        return mach[valides], cd[valides]

    def analyser(self, etat, phases):
        """Calcule l'ensemble des indicateurs de performance.

        :param etat: état de vol reconstruit.
        :type etat: fusionvol.fusion.base.EtatVol
        :param phases: phases détectées.
        :type phases: fusionvol.analyse.phases.Phases
        :return: dictionnaire des indicateurs.
        :rtype: dict
        """
        i_apogee = phases.indices["apogee"]
        montee = slice(0, i_apogee + 1)

        mach = self.mach(etat)
        q = self.pression_dynamique(etat)

        i_vmax = int(np.argmax(etat.vitesse[montee]))
        i_maxq = int(np.argmax(q[montee]))

        resultats = {
            "apogee_m": float(etat.altitude[i_apogee]),
            "temps_apogee_s": float(etat.temps[i_apogee]),
            "vitesse_max_ms": float(etat.vitesse[i_vmax]),
            "mach_max": float(np.max(mach[montee])),
            "max_q_pa": float(q[i_maxq]),
            "altitude_max_q_m": float(etat.altitude[i_maxq]),
            "mach_max_q": float(mach[i_maxq]),
            "acceleration_max_ms2": float(np.max(etat.acceleration[montee])),
        }
        resultats.update(
            {"duree_" + nom + "_s": val for nom, val in phases.resume().items()}
        )
        return resultats