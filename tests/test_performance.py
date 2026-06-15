"""Tests de la détection de phases et de l'analyse de performance."""

import numpy as np

from fusionvol.analyse import AnalysePerformance, DetecteurPhases
from fusionvol.atmosphere import Atmosphere
from fusionvol.fusion import EtatVol


def _etat_synthetique():
    """Construit un EtatVol synthétique simple."""
    t = np.linspace(0, 10, 1001)
    alt = 1000.0 * t * (10 - t) / 25.0
    vit = np.gradient(alt, t)
    acc = np.gradient(vit, t)
    return EtatVol(t, alt, vit, acc, nom="test")


def test_detection_phases():
    """Les événements sont ordonnés dans le temps."""
    phases = DetecteurPhases().detecter(_etat_synthetique())
    i = phases.indices
    assert i["decollage"] <= i["burnout"] <= i["apogee"] <= i["atterrissage"]


def test_indicateurs():
    """L'analyse renvoie les indicateurs attendus."""
    etat = _etat_synthetique()
    phases = DetecteurPhases().detecter(etat)
    analyse = AnalysePerformance(Atmosphere())
    indicateurs = analyse.analyser(etat, phases)
    assert "apogee_m" in indicateurs
    assert "mach_max" in indicateurs
    assert indicateurs["apogee_m"] > 100.0