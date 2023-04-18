# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import statgis

v = statgis.__version__

autodoc_mock_imports = ["ee", "statgis"]

# -- Project information -----------------------------------------------------
project = u"statgis"
copyright = u"2023, Sebástian Narváez-Salcedo, Brayan Navarro-Londoño"
author = u"Sebástian Narváez-Salcedo, Brayan Navarro-Londoño"

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "myst_nb",
    "autoapi.extension",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "pydata_sphinx_theme",
    "sphinx_material",
]
autoapi_dirs = ["../src"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_title = f"StatGIS Python Package ({v})"
html_theme = "pydata_sphinx_theme"
# html_theme = "sphinx_material"

html_theme_options = {
    # "nav_title": "StatGIS Python Package 1.0.1",

    # "color_primary": "blue",
    # "color_accent": "light-blue",

    # "repo_url": "https://github.com/srnarvaez/statgis",
    # "repo_name": "StatGIS",

    # "globaltoc_depth": 3,
    # "nav_links": [],
    # "globaltoc_collapse": True,
    # "globaltoc_includehidden": True,
    "icon_links": [
    {
        "name": "GitHub",
        "url": "https://github.com/srnarvaez/statgis",
        "icon": "fa-brands fa-github",
        "type": "fontawesome",
    },
    {
        "name": "PyPI",
        "url": "https://pypi.org/project/statgis",
        "icon": "fa-solid fa-box",
        "type": "fontawesome",
    },
    {
        "name": "Instagram",
        "url": "https://www.instagram.com/statgisorg/",
        "icon": "fa-brands fa-instagram",
        "type": "fontawesome",
    },
   ]
}
