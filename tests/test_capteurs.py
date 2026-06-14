"""Tests du sous-paquet capteurs."""

import os

import numpy as np

from fusionvol.capteurs import DonneesCapteurs


def _ecrire_csv_exemple(chemin):
    """Écrit un petit CSV d'exemple au format attendu."""
    with open(chemin, "w", encoding="utf-8") as flux:
        flux.write("ts,filtered_altitude_AGL,filtered_acceleration\n")
        flux.write("-0.02,0.0,0.05\n")
        flux.write("-0.01,0.0,0.05\n")
        flux.write("0.00,0.0,20.0\n")
        flux.write("0.01,0.1,25.0\n")
        flux.write("0.02,0.3,0.0\n")
        flux.write("0.03,0.6,0.0\n")


def test_lecture_et_attributs(tmp_path):
    """La lecture produit des tableaux alignés et la bonne fréquence."""
    chemin = os.path.join(tmp_path, "exemple.csv")
    _ecrire_csv_exemple(chemin)
    donnees = DonneesCapteurs.depuis_csv(chemin)
    assert len(donnees) == 6
    assert np.isclose(donnees.dt, 0.01)
    assert np.isclose(donnees.frequence, 100.0)
    assert donnees.est_regulier()


def test_correction_biais(tmp_path):
    """La correction de biais s'appuie sur le repos initial, pas sur temps<0."""
    chemin = os.path.join(tmp_path, "exemple.csv")
    _ecrire_csv_exemple(chemin)
    donnees = DonneesCapteurs.depuis_csv(chemin)
    biais = donnees.corriger_biais(duree=0.02)
    assert np.isclose(biais, 0.05)


def test_rogner_queue(tmp_path):
    """La queue de zéros est retirée."""
    chemin = os.path.join(tmp_path, "exemple.csv")
    _ecrire_csv_exemple(chemin)
    donnees = DonneesCapteurs.depuis_csv(chemin)
    retires = donnees.rogner_queue()
    assert retires == 2
    assert len(donnees) == 4


def test_colonne_manquante(tmp_path):
    """Un fichier sans la bonne colonne lève une KeyError."""
    chemin = os.path.join(tmp_path, "mauvais.csv")
    with open(chemin, "w", encoding="utf-8") as flux:
        flux.write("ts,autre\n0.0,1.0\n")
    try:
        DonneesCapteurs.depuis_csv(chemin)
        assert False, "une KeyError était attendue"
    except KeyError:
        pass