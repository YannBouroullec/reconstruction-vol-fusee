"""Détection automatique des événements et des phases de vol."""

import numpy as np


class Phases:
    """Résultat de la détection de phases.

    Contient les indices et les instants des événements clés, et les bornes des
    trois grandes phases (propulsion, montée balistique, descente).

    :ivar indices: dictionnaire des indices des événements.
    :ivar instants: dictionnaire des instants (s) des événements.
    """

    def __init__(self, temps, indices):
        """Construit le résultat à partir des indices détectés.

        :param temps: grille de temps du vol (s).
        :type temps: numpy.ndarray
        :param indices: indices des événements ``decollage``, ``burnout``,
            ``apogee`` et ``atterrissage``.
        :type indices: dict
        """
        self.indices = indices
        self.instants = {nom: float(temps[i]) for nom, i in indices.items()}

    def duree(self, debut, fin):
        """Renvoie la durée entre deux événements.

        :param debut: nom de l'événement de début.
        :type debut: str
        :param fin: nom de l'événement de fin.
        :type fin: str
        :return: durée (s).
        :rtype: float
        """
        return self.instants[fin] - self.instants[debut]

    def resume(self):
        """Renvoie un dictionnaire des durées des grandes phases.

        :return: durées de la propulsion, de la montée balistique et de la
            descente (s).
        :rtype: dict
        """
        return {
            "propulsion": self.duree("decollage", "burnout"),
            "montee_balistique": self.duree("burnout", "apogee"),
            "descente": self.duree("apogee", "atterrissage"),
        }

    def __str__(self):
        """Renvoie un résumé lisible des instants détectés."""
        return "Phases(" + ", ".join(
            "{}={:.1f}s".format(nom, t) for nom, t in self.instants.items()
        ) + ")"


class DetecteurPhases:
    """Détecte les événements de vol à partir d'un état reconstruit.

    Les événements sont repérés par des règles simples sur l'altitude et
    l'accélération : décollage au temps zéro, extinction du moteur (burnout)
    quand l'accélération repasse sous zéro après le pic de poussée, apogée au
    sommet de l'altitude, atterrissage au retour près du sol.

    :ivar seuil_sol: altitude en dessous de laquelle on considère le sol (m).
    """

    def __init__(self, seuil_sol=2.0):
        """Initialise le détecteur.

        :param seuil_sol: altitude seuil pour l'atterrissage (m).
        :type seuil_sol: float
        """
        self.seuil_sol = float(seuil_sol)

    def detecter(self, etat):
        """Détecte les événements de vol.

        :param etat: état de vol reconstruit.
        :type etat: fusionvol.fusion.base.EtatVol
        :return: les phases détectées.
        :rtype: Phases
        """
        temps = etat.temps
        altitude = etat.altitude
        acceleration = etat.acceleration

        # Décollage : premier instant à temps positif (convention des journaux).
        positifs = np.where(temps >= 0.0)[0]
        i_decollage = int(positifs[0]) if len(positifs) else 0

        # Apogée : altitude maximale.
        i_apogee = int(np.argmax(altitude))

        # Burnout : après le pic d'accélération, premier passage sous zéro.
        if i_apogee > i_decollage:
            i_pic = i_decollage + int(np.argmax(acceleration[i_decollage:i_apogee]))
            negatifs = np.where(acceleration[i_pic:i_apogee] < 0.0)[0]
            i_burnout = i_pic + int(negatifs[0]) if len(negatifs) else i_pic
        else:
            i_burnout = i_decollage

        # Atterrissage : après l'apogée, retour sous le seuil sol.
        apres = np.where(altitude[i_apogee:] < self.seuil_sol)[0]
        i_atterrissage = i_apogee + int(apres[0]) if len(apres) else len(temps) - 1

        indices = {
            "decollage": i_decollage,
            "burnout": i_burnout,
            "apogee": i_apogee,
            "atterrissage": i_atterrissage,
        }
        return Phases(temps, indices)