# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

# -- Path setup --------------------------------------------------------------
# The documentation folder is meant to live at the root of the phantom
# repository, so the package sits two levels above this file. Putting it first on sys.path
# makes autodoc read the docstrings from the source tree you are editing.
#
# phantom must also be installed in the same environment as Sphinx
# (``pip install -e .`` from the repository root), because
# phantom/__init__.py reads its own version from the installed metadata.
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'phantom'
author = 'Bruno Constanzo'
copyright = '2018-2026, Bruno Constanzo'

try:
    release = version('phantom')
except PackageNotFoundError:
    release = '0.8.3'
version = '.'.join(release.split('.')[:2])

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',   # pulls the API reference from the docstrings
    'sphinx.ext.viewcode',  # adds [source] links next to each function
]

templates_path = ['_templates']
exclude_patterns = []

# -- autodoc -----------------------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html

autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',   # same order as in the source code
    'undoc-members': True,        # list functions even if they lack a docstring
}
autoclass_content = 'both'        # class docstring + __init__ docstring
autodoc_preserve_defaults = True  # show default values as written in the code
add_module_names = False          # show detect() instead of phantom.faces.faces.detect()

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']
html_theme_options = {
    'description': 'Forensic image processing in Python',
    'extra_nav_links': {
        'phantom on GitHub': 'https://github.com/bconstanzo/phantom',
    },
}
