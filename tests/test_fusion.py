"""Tests des estimateurs d'état."""

import numpy as np

from fusionvol.fusion import (
    EstimateurAccel,
    EstimateurBaro,
    EstimateurEtat,
    EtatVol,
    FiltreComplementaire,
)


def _signal_synthetique():
    """Construit un petit vol synthétique : montée puis descente."""
    t = np.linspace(0, 10, 1001)
    alt = 100.0 * t * (10 - t) / 25.0  # parabole, sommet à t=5
    acc = np.gradient(np.gradient(alt, t), t)
    return t, alt, acc


def test_fusion_produit_etat():
    """Le filtre complémentaire renvoie un EtatVol cohérent."""
    t, alt, acc = _signal_synthetique()
    etat = FiltreComplementaire().estimer(t, alt, acc)
    assert isinstance(etat, EtatVol)
    assert len(etat) == len(t)
    assert etat.altitude.max() > 50.0


def test_alpha_invalide():
    """Un coefficient hors de ]0,1[ lève une ValueError."""
    try:
        FiltreComplementaire(alpha=1.5)
        assert False, "une ValueError était attendue"
    except ValueError:
        pass


def test_interface_non_instanciable():
    """On ne peut pas instancier l'interface abstraite directement."""
    try:
        EstimateurEtat()
        assert False, "l'interface ne doit pas être instanciable"
    except TypeError:
        pass


def test_references():
    """Les estimateurs de référence respectent aussi le contrat."""
    t, alt, acc = _signal_synthetique()
    for estimateur in (EstimateurBaro(), EstimateurAccel()):
        etat = estimateur.estimer(t, alt, acc)
        assert isinstance(etat, EtatVol)
        assert len(etat) == len(t)