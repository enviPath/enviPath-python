# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

main_folder_path = os.path.abspath('../..')
if main_folder_path not in sys.path:
    sys.path.insert(0, main_folder_path)


# Removing the classes that are not documented according to new standards
autodoc_default_options = {
    'exclude-members': 'Endpoint, ClassifierType, FingerprinterType, AssociationType, EvaluationType, Permission,'
                       'ModelPredictionProbabilityAdditionalInformation, '
                       'ModelBayesPredictionProbabilityAdditionalInformation, '
}

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'enviPath-python'
copyright = '2023, enviPath UG & Co. KG'
author = 'Albert Anguera Sempere'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration
source_suffix = ".rst"
master_doc = "index"

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.coverage', 'sphinx.ext.napoleon',
              'sphinx.ext.autosectionlabel', "myst_nb", "IPython.sphinxext.ipython_console_highlighting",
              'sphinx_copybutton'
              ]

myst_enable_extensions = ["dollarmath", "colon_fence"]
suppress_warnings = ["mystnb.unknown_mime_type"]
nb_execution_timeout = -1


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
html_title = 'enviPath-python'
html_theme = 'sphinx_book_theme'
html_favicon = "assets/enviPath_LOGO.ico"
html_js_files = ["https://cdnjs.cloudflare.com/ajax/libs/require.js/2.3.4/require.min.js"]
