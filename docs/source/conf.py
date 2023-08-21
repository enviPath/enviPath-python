# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

# Removing the constant variables that are defined within classes, apparently autodocs recognizes upper cased variables
# and documents them
autodoc_default_options = {
    'exclude-members': 'ENDPOINT_OBJECT_MAPPING, CALCULATED, DATABASED, ECC, MLCBMAD, RULEBASED, COMPOUND, COMPOUNDSTRUCTURE,'
                       'EDGE, GROUP, NODE, PACKAGE, PARALLELCOMPOSITERULE, PATHWAY, REACTION, RELATIVEREASONING, RULE, header,'
                       'SCENARIO, SEQUENTIALCOMPOSITERULE, SETTING, SIMPLERULE, USER, MULTI_GEN, SINGLE_GEN, NONE, READ, WRITE,'
                       'ENVIPATH_FINGERPRINTER'
}

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'enviPath-python'
copyright = '2023, enviPath UG & Co. KG'
author = 'Albert Anguera Sempere'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

main_folder_path = os.path.abspath('../..')
if main_folder_path not in sys.path:
    sys.path.insert(0, main_folder_path)

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.coverage', 'sphinx.ext.napoleon']

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
