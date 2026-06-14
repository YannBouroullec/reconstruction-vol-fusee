"""Tests du modèle d'atmosphère ISA."""

import numpy as np

from fusionvol.atmosphere import Atmosphere


def test_niveau_mer():
    """Au niveau de la mer, on retrouve les valeurs de référence ISA."""
    atmo = Atmosphere(elevation_sol=0.0)
    assert np.isclose(atmo.temperature(0.0), 288.15)
    assert np.isclose(atmo.pression(0.0), 101325.0, rtol=1e-3)
    assert np.isclose(atmo.densite(0.0), 1.225, rtol=1e-2)
    assert np.isclose(atmo.vitesse_son(0.0), 340.3, rtol=1e-2)


def test_decroissance_altitude():
    """La densité et la pression diminuent avec l'altitude."""
    atmo = Atmosphere(elevation_sol=0.0)
    assert atmo.densite(3000.0) < atmo.densite(0.0)
    assert atmo.pression(3000.0) < atmo.pression(0.0)


def test_tableau():
    """Le modèle accepte un tableau d'altitudes."""
    atmo = Atmosphere()
    valeurs = atmo.densite(np.array([0.0, 1000.0, 2000.0]))
    assert valeurs.shape == (3,)