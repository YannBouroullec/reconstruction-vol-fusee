"""Lecture et validation du fichier de configuration (deck YAML)."""

import yaml

# Valeurs par défaut utilisées quand une clé est absente du deck.
DEFAUTS = {
    "fichier": "flight_data_faraday.csv",
    "nom_vol": None,
    "elevation_sol": 160.0,
    "alpha": 0.98,
    "beta": 0.90,
    "masse": None,
    "surface_ref": None,
    "dossier_sortie": "sorties",
    "tracer_profil": True,
    "tracer_comparaison": True,
    "tracer_portrait": True,
    "tracer_spectrogramme": True,
    "creer_replay": True,
    "fps_replay": 25,
    "tracer_comparaison_vitesse": True,
    "tracer_portrait_montee": True,
}


class LecteurDeck:
    """Lit un fichier de configuration YAML et le complète avec les défauts.

    Le deck regroupe tous les paramètres réglables par l'utilisateur : fichier
    d'entrée, site de lancement, réglage du filtre, paramètres de la fusée et
    sorties souhaitées.
    """

    def charger(self, chemin):
        """Charge le deck et renvoie un dictionnaire de paramètres complet.

        :param chemin: chemin du fichier YAML.
        :type chemin: str
        :return: paramètres de configuration, complétés par les défauts.
        :rtype: dict
        :raises FileNotFoundError: si le fichier n'existe pas.
        :raises ValueError: si le contenu YAML est invalide.
        """
        try:
            with open(chemin, "r", encoding="utf-8") as flux:
                contenu = yaml.safe_load(flux)
        except FileNotFoundError:
            raise FileNotFoundError("Deck introuvable : " + str(chemin))
        except yaml.YAMLError as erreur:
            raise ValueError("Deck YAML invalide : " + str(erreur))

        if contenu is None:
            contenu = {}

        parametres = dict(DEFAUTS)
        parametres.update(contenu)
        return parametres