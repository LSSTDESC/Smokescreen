# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

# flake8: noqa

project = 'Smokescreen'
copyright = 'LSST Dark Energy Science Collaboration '
author = 'LSST DESC (Maintainer: Arthur Loureiro <arthur.loureiro@fysik.su.se>)'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx_rtd_theme",
    "sphinx.ext.autodoc",
    'sphinx.ext.napoleon',
    'sphinxcontrib.autoprogram',
    'sphinxcontrib.datatemplates'
]

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# Set the theme
html_theme = 'sphinx_rtd_theme'
html_logo = '_static/bkp_logo.png'
# Optionally, you can customize the theme further with theme-specific options
# These are options specifically for the Wagtail Theme.
# more info here: https://sphinx-wagtail-theme.readthedocs.io/en/latest/index.html
html_theme_options = {
    'display_version': True,
    'titles_only': False,
    'sticky_navigation': True,
    'navigation_depth': 4,
}

html_css_files = [
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css',
]
html_static_path = ['_static']
html_js_files = [
    'custom.js',
]
