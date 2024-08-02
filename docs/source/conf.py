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
    "sphinx_wagtail_theme",
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
html_theme = "sphinx_wagtail_theme"

# Optionally, you can customize the theme further with theme-specific options
# These are options specifically for the Wagtail Theme.
# more info here: https://sphinx-wagtail-theme.readthedocs.io/en/latest/index.html
html_theme_options = dict(
    project_name = "DESC Smokescreen",
    logo = "logo.png",
    logo_alt = "DESC",
    logo_height = 59,
    logo_url = "index.html",
    logo_width = 45,
    #header_links = "Top 1|http://example.com/one, Top 2|http://example.com/two",
    footer_links = ",".join([
        "DESC LSST|https://lsstdesc.org/",
        "Vera C. Rubin Observatory|https://rubinobservatory.org/",
        "DESC Github|https://github.com/LSSTDESC",
    ]),
)

html_static_path = ['_static']
