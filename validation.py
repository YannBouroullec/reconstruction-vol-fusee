"""Validation des estimateurs sur un vol synthétique à vérité connue.

On simule une trajectoire dont on connaît exactement l'altitude et la vitesse,
on fabrique des mesures bruitées (baromètre bruité, accéléromètre biaisé et
bruité), puis on fait tourner les trois estimateurs et on mesure l'écart de
chacun à la vérité. C'est la seule façon de prouver que la fusion fait mieux,
puisque sur un vrai vol le baromètre est déjà la référence.

Utilisation :

    python validation.py
"""

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from fusionvol.fusion import EstimateurAccel, EstimateurBaro, FiltreComplementaire

G = 9.80665


def generer_vol_synthetique(dt=0.01, a_boost=70.0, t_burn=3.0, v_terminal=25.0):
    """Simule un vol vertical et renvoie sa vérité (temps, accel, vitesse, altitude).

    Trois phases : poussée à accélération constante, montée balistique sous la
    seule gravité, puis descente freinée jusqu'à une vitesse terminale.

    :param dt: pas de temps (s).
    :type dt: float
    :param a_boost: accélération pendant la poussée (m/s^2).
    :type a_boost: float
    :param t_burn: durée de la poussée (s).
    :type t_burn: float
    :param v_terminal: vitesse de descente terminale visée (m/s).
    :type v_terminal: float
    :return: temps, accélération, vitesse et altitude vraies.
    :rtype: tuple(numpy.ndarray, numpy.ndarray, numpy.ndarray, numpy.ndarray)
    """
    n = int(200.0 / dt)
    t = np.arange(n) * dt
    a = np.zeros(n)
    v = np.zeros(n)
    h = np.zeros(n)
    coef_trainee = G / v_terminal
    a[0] = a_boost
    fin = n
    for i in range(1, n):
        if t[i] < t_burn:
            acc = a_boost
        elif v[i - 1] > 0.0:
            acc = -G
        else:
            acc = -G - coef_trainee * v[i - 1]
        v[i] = v[i - 1] + acc * dt
        h[i] = h[i - 1] + v[i] * dt
        a[i] = acc
        if h[i] <= 0.0 and t[i] > t_burn:
            fin = i + 1
            break
    return t[:fin], a[:fin], v[:fin], h[:fin]


def fabriquer_mesures(temps, accel_vrai, altitude_vraie, sigma_baro=8.0,
                      biais_accel=0.15, sigma_accel=1.5, graine=0):
    """Fabrique des mesures bruitées à partir de la vérité.

    :param temps: instants (s).
    :type temps: numpy.ndarray
    :param accel_vrai: accélération vraie (m/s^2).
    :type accel_vrai: numpy.ndarray
    :param altitude_vraie: altitude vraie (m).
    :type altitude_vraie: numpy.ndarray
    :param sigma_baro: écart-type du bruit barométrique (m).
    :type sigma_baro: float
    :param biais_accel: biais constant de l'accéléromètre (m/s^2).
    :type biais_accel: float
    :param sigma_accel: écart-type du bruit de l'accéléromètre (m/s^2).
    :type sigma_accel: float
    :param graine: graine aléatoire pour la reproductibilité.
    :type graine: int
    :return: altitude barométrique mesurée et accélération mesurée.
    :rtype: tuple(numpy.ndarray, numpy.ndarray)
    """
    rng = np.random.default_rng(graine)
    baro = altitude_vraie + rng.normal(0.0, sigma_baro, len(altitude_vraie))
    accel = accel_vrai + biais_accel + rng.normal(0.0, sigma_accel, len(accel_vrai))
    return baro, accel


def rmse(estime, vrai):
    """Renvoie l'erreur quadratique moyenne entre un estimé et la vérité.

    :param estime: valeurs estimées.
    :type estime: numpy.ndarray
    :param vrai: valeurs vraies.
    :type vrai: numpy.ndarray
    :return: erreur quadratique moyenne.
    :rtype: float
    """
    return float(np.sqrt(np.mean((estime - vrai) ** 2)))


def executer(dossier_sortie="sorties"):
    """Lance la validation et affiche le tableau d'erreurs.

    :param dossier_sortie: dossier où enregistrer la figure.
    :type dossier_sortie: str
    """
    os.makedirs(dossier_sortie, exist_ok=True)

    temps, accel_vrai, vitesse_vraie, altitude_vraie = generer_vol_synthetique()
    baro, accel = fabriquer_mesures(temps, accel_vrai, altitude_vraie)

    estimateurs = [
        FiltreComplementaire().estimer(temps, baro, accel),
        EstimateurBaro().estimer(temps, baro, accel),
        EstimateurAccel().estimer(temps, baro, accel),
    ]

    apogee_vrai = float(altitude_vraie.max())
    print("Vol synthétique : apogée vraie = {:.0f} m, vitesse max vraie = {:.0f} m/s\n".format(
        apogee_vrai, float(vitesse_vraie.max())))
    print("{:<14} {:>14} {:>16} {:>16}".format(
        "Méthode", "Err. apogée [m]", "RMSE altitude [m]", "RMSE vitesse [m/s]"))
    print("-" * 62)
    for est in estimateurs:
        err_apogee = abs(float(est.altitude.max()) - apogee_vrai)
        err_alt = rmse(est.altitude, altitude_vraie)
        err_vit = rmse(est.vitesse, vitesse_vraie)
        print("{:<14} {:>14.1f} {:>16.1f} {:>16.1f}".format(
            est.nom, err_apogee, err_alt, err_vit))

    # Figure : vérité contre les trois estimations, en altitude et en vitesse.
    fusion_e, baro_e, accel_e = estimateurs
    coul = {"Fusion": "#1f77b4", "Baro seul": "#ff7f0e", "Accel seul": "#2ca02c"}

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 9), sharex=True)
    ax1.plot(temps, accel_e.altitude, lw=1.3, color=coul["Accel seul"], label="Accel seul")
    ax1.plot(temps, baro_e.altitude, lw=1.3, color=coul["Baro seul"], alpha=0.7, label="Baro seul")
    ax1.plot(temps, fusion_e.altitude, lw=1.7, color=coul["Fusion"], label="Fusion")
    ax1.plot(temps, altitude_vraie, "k--", lw=2, label="Vérité", zorder=5)
    ax1.set_ylabel("Altitude AGL [m]")
    ax1.set_ylim(-50, apogee_vrai * 1.3)
    ax1.set_title("Validation sur vol synthétique", fontweight="bold")
    ax1.grid(alpha=0.25)
    ax1.legend()

    ax2.plot(temps, baro_e.vitesse, lw=0.8, color=coul["Baro seul"], alpha=0.35, label="Baro seul")
    ax2.plot(temps, accel_e.vitesse, lw=1.3, color=coul["Accel seul"], label="Accel seul")
    ax2.plot(temps, fusion_e.vitesse, lw=1.7, color=coul["Fusion"], label="Fusion")
    ax2.plot(temps, vitesse_vraie, "k--", lw=2, label="Vérité", zorder=5)
    ax2.set_xlabel("Temps [s]")
    ax2.set_ylabel("Vitesse [m/s]")
    ax2.set_ylim(-60, float(vitesse_vraie.max()) * 1.3)
    ax2.grid(alpha=0.25)
    ax2.legend()

    fig.tight_layout()
    chemin = os.path.join(dossier_sortie, "validation_synthetique.png")
    fig.savefig(chemin, dpi=140, bbox_inches="tight")
    plt.close(fig)
    print("\nFigure écrite : " + chemin)


if __name__ == "__main__":
    executer()