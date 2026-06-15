"""Configuration Sphinx pour la documentation de fusionvol."""

import os
import sys

sys.path.insert(0, os.path.abspath(".."))

project = "fusionvol"
author = "Théo Malavieille, Pierre-Jean Tulasne, Yann"
release = "0.1.0"

extensions = ["sphinx.ext.autodoc", "sphinx.ext.napoleon"]
templates_path = ["_templates"]
exclude_patterns = ["_build"]

html_theme = "alabaster"