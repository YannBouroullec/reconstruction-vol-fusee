"""Lecture et normalisation des journaux de vol (CSV)."""

import numpy as np
import pandas as pd

# Correspondance entre les colonnes brutes des fichiers et nos noms internes.
# Les quatre vols EuRoC partagent ces noms ; pour une autre source (export
# OpenRocket par exemple) il suffira d'ajouter une entrée dans ce dictionnaire.
MAPPING_PAR_DEFAUT = {
    "ts": "temps",
    "filtered_altitude_AGL": "altitude",
    "filtered_acceleration": "acceleration",
}


class DonneesCapteurs:
    """Conteneur des données capteurs d'un vol, déjà mises en forme.

    Après lecture, les attributs :attr:`temps`, :attr:`altitude` et
    :attr:`acceleration` sont des tableaux numpy alignés sur une grille de
    temps régulière. Les conventions des fichiers EuRoC sont prises en compte :
    le temps vaut 0 au décollage (les valeurs négatives correspondent au
    pré-lancement sur la rampe), l'altitude est exprimée en mètres au-dessus du
    sol et l'accélération est verticale, gravité déjà retirée (proche de 0 au
    repos), donc directement intégrable.

    :ivar temps: instants de mesure en secondes.
    :ivar altitude: altitude au-dessus du sol en mètres.
    :ivar acceleration: accélération verticale en m/s^2.
    :ivar dt: pas de temps médian en secondes.
    :ivar frequence: fréquence d'échantillonnage en Hz.
    """

    def __init__(self, temps, altitude, acceleration, nom="vol"):
        """Construit un conteneur à partir de tableaux déjà alignés.

        En général on n'appelle pas directement le constructeur mais la méthode
        de classe :meth:`depuis_csv`.

        :param temps: instants de mesure (s).
        :type temps: numpy.ndarray
        :param altitude: altitude au-dessus du sol (m).
        :type altitude: numpy.ndarray
        :param acceleration: accélération verticale (m/s^2).
        :type acceleration: numpy.ndarray
        :param nom: étiquette du vol, utilisée pour les titres de graphiques.
        :type nom: str
        """
        self.temps = np.asarray(temps, dtype=float)
        self.altitude = np.asarray(altitude, dtype=float)
        self.acceleration = np.asarray(acceleration, dtype=float)
        self.nom = nom
        self.dt = float(np.median(np.diff(self.temps)))
        self.frequence = 1.0 / self.dt

    @classmethod
    def depuis_csv(cls, chemin, mapping=None, nom=None):
        """Lit un fichier CSV et renvoie un conteneur mis en forme.

        :param chemin: chemin vers le fichier CSV.
        :type chemin: str
        :param mapping: correspondance colonnes brutes -> noms internes. Si
            ``None``, on utilise :data:`MAPPING_PAR_DEFAUT`.
        :type mapping: dict or None
        :param nom: étiquette du vol. Si ``None``, on déduit le nom du fichier.
        :type nom: str or None
        :return: les données mises en forme.
        :rtype: DonneesCapteurs
        :raises FileNotFoundError: si le fichier n'existe pas.
        :raises KeyError: si une colonne attendue est absente du fichier.
        """
        if mapping is None:
            mapping = MAPPING_PAR_DEFAUT

        try:
            brut = pd.read_csv(chemin)
        except FileNotFoundError:
            raise FileNotFoundError("Fichier introuvable : " + str(chemin))

        manquantes = [col for col in mapping if col not in brut.columns]
        if manquantes:
            raise KeyError("Colonnes absentes du fichier : " + ", ".join(manquantes))

        donnees = brut.rename(columns=mapping)
        if nom is None:
            nom = str(chemin).split("/")[-1].replace(".csv", "")

        return cls(
            temps=donnees["temps"].to_numpy(),
            altitude=donnees["altitude"].to_numpy(),
            acceleration=donnees["acceleration"].to_numpy(),
            nom=nom,
        )

    def est_regulier(self, tolerance=1e-4):
        """Indique si l'échantillonnage est régulier.

        :param tolerance: écart-type maximal toléré sur le pas de temps (s).
        :type tolerance: float
        :return: ``True`` si la grille de temps est régulière.
        :rtype: bool
        """
        return float(np.std(np.diff(self.temps))) < tolerance

    def estimer_biais(self, duree=0.1):
        """Estime le biais de l'accéléromètre sur la fenêtre de repos initiale.

        Attention : on ne se sert que des toutes premières mesures. La fenêtre
        de pré-lancement complète (temps négatif) contient déjà la montée en
        poussée du moteur et donnerait un biais faux.

        :param duree: durée de la fenêtre de repos analysée (s).
        :type duree: float
        :return: biais moyen de l'accélération au repos (m/s^2).
        :rtype: float
        """
        nb = max(1, int(duree / self.dt))
        return float(np.mean(self.acceleration[:nb]))

    def corriger_biais(self, duree=0.1):
        """Retire le biais de repos de l'accélération, en place.

        :param duree: durée de la fenêtre de repos analysée (s).
        :type duree: float
        :return: le biais retiré (m/s^2).
        :rtype: float
        """
        biais = self.estimer_biais(duree)
        self.acceleration = self.acceleration - biais
        return biais

    def rogner_queue(self, seuil=1e-9):
        """Supprime la queue de zéros ajoutée après l'atterrissage, en place.

        Les journaux sont complétés par des zéros une fois le vol terminé. On
        coupe à la dernière mesure d'accélération non nulle.

        :param seuil: valeur en dessous de laquelle on considère un zéro.
        :type seuil: float
        :return: le nombre d'échantillons retirés.
        :rtype: int
        """
        non_nuls = np.where(np.abs(self.acceleration) > seuil)[0]
        if len(non_nuls) == 0:
            return 0
        dernier = int(non_nuls[-1])
        retires = len(self.temps) - (dernier + 1)
        self.temps = self.temps[: dernier + 1]
        self.altitude = self.altitude[: dernier + 1]
        self.acceleration = self.acceleration[: dernier + 1]
        return retires

    def vers_dataframe(self):
        """Renvoie les données sous forme de tableau pandas.

        :return: tableau à colonnes ``temps``, ``altitude``, ``acceleration``.
        :rtype: pandas.DataFrame
        """
        return pd.DataFrame(
            {
                "temps": self.temps,
                "altitude": self.altitude,
                "acceleration": self.acceleration,
            }
        )

    def __len__(self):
        """Renvoie le nombre d'échantillons."""
        return len(self.temps)

    def __str__(self):
        """Renvoie un résumé lisible du vol."""
        return (
            "DonneesCapteurs('{nom}' : {n} points, {f:.0f} Hz, "
            "{d:.1f} s, altitude max {a:.0f} m)".format(
                nom=self.nom,
                n=len(self),
                f=self.frequence,
                d=self.temps[-1] - self.temps[0],
                a=float(np.max(self.altitude)),
            )
        )