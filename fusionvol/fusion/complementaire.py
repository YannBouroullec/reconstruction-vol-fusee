"""Filtre complémentaire : fusion de l'accéléromètre et du baromètre."""

import numpy as np

from fusionvol.fusion.base import EstimateurEtat, EtatVol, integrer, lisser


class FiltreComplementaire(EstimateurEtat):
    """Estimateur par filtre complémentaire.

    Le principe : l'accéléromètre est fiable à court terme mais dérive quand on
    l'intègre, alors que le baromètre est stable à long terme mais bruité et
    lent. Le filtre fait confiance à l'accéléromètre sur le court terme et
    recale progressivement vers le baromètre, réglé par deux coefficients
    proches de 1.

    Pour chaque pas de temps :

    * vitesse : ``v = alpha * (v_prec + a*dt) + (1 - alpha) * v_baro``
    * altitude : ``h = beta * (h_prec + v*dt) + (1 - beta) * h_baro``

    où ``v_baro`` est la dérivée lissée de l'altitude barométrique.

    :ivar alpha: confiance accordée à l'accéléromètre pour la vitesse.
    :ivar beta: confiance accordée à la vitesse intégrée pour l'altitude.
    :ivar fenetre_lissage: taille de la fenêtre de lissage de la dérivée baro.
    """

    def __init__(self, alpha=0.98, beta=0.90, fenetre_lissage=21):
        """Initialise le filtre.

        :param alpha: coefficient de fusion de la vitesse, dans ]0, 1[.
        :type alpha: float
        :param beta: coefficient de fusion de l'altitude, dans ]0, 1[.
        :type beta: float
        :param fenetre_lissage: fenêtre de lissage de la vitesse barométrique
            (nombre d'échantillons).
        :type fenetre_lissage: int
        :raises ValueError: si ``alpha`` ou ``beta`` n'est pas dans ]0, 1[.
        """
        if not 0.0 < alpha < 1.0:
            raise ValueError("alpha doit être dans ]0, 1[")
        if not 0.0 < beta < 1.0:
            raise ValueError("beta doit être dans ]0, 1[")
        self.alpha = float(alpha)
        self.beta = float(beta)
        self.fenetre_lissage = int(fenetre_lissage)

    def estimer(self, temps, altitude, acceleration):
        """Reconstruit l'état de vol par fusion complémentaire.

        :param temps: instants (s).
        :type temps: numpy.ndarray
        :param altitude: altitude barométrique (m).
        :type altitude: numpy.ndarray
        :param acceleration: accélération verticale (m/s^2).
        :type acceleration: numpy.ndarray
        :return: l'état de vol fusionné.
        :rtype: EtatVol
        """
        temps = np.asarray(temps, dtype=float)
        altitude = np.asarray(altitude, dtype=float)
        acceleration = np.asarray(acceleration, dtype=float)
        dt = float(np.median(np.diff(temps)))
        n = len(temps)

        # Vitesse de référence : dérivée de l'altitude baro, puis lissage.
        vitesse_baro = lisser(np.gradient(altitude, dt), self.fenetre_lissage)

        vitesse = np.zeros(n)
        alt_fusion = np.zeros(n)
        alt_fusion[0] = altitude[0]
        for i in range(1, n):
            vitesse[i] = (
                self.alpha * (vitesse[i - 1] + acceleration[i] * dt)
                + (1.0 - self.alpha) * vitesse_baro[i]
            )
            alt_fusion[i] = (
                self.beta * (alt_fusion[i - 1] + vitesse[i] * dt)
                + (1.0 - self.beta) * altitude[i]
            )

        return EtatVol(temps, alt_fusion, vitesse, acceleration, nom="Fusion")

    def __str__(self):
        """Renvoie un résumé lisible du réglage du filtre."""
        return "FiltreComplementaire(alpha={a}, beta={b})".format(
            a=self.alpha, b=self.beta
        )