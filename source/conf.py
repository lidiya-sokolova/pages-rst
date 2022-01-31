# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))

import os


# -- Project information -----------------------------------------------------

project = 'lidiya.sokolova.github.io'
copyright = '2022, Lidiya Sokolova'
author = 'Lidiya Sokolova <lidiya.sokolova@mail.ru>'

# The full version, including alpha/beta/rc tags
release = '1.0'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinxcontrib.plantuml'
]

plantuml = 'plantuml.cmd'
plantuml_output_format = 'svg_img'

# Add any paths that contain templates here, relative to this directory.
templates_path = [
    '_templates'
]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

if not tags.has('MAKE_HTML') and not tags.has('MAKE_CHM') and not tags.has('MAKE_PDF'):
    tags.add('MAKE_HTML')


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme =    'haiku' if tags.has('MAKE_CHM') else (
                'haiku' if tags.has('MAKE_PDF') else \
                'furo')
html_title =    'Сайт учителя Соколовой Л.Ф.'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = [
    '_static'
]

html_extra_path = [
    '_other/'
]

html_css_files = [
    #'css/custom.css'
]

html_js_files = [
    #'js/custom.js',
]

html_favicon = '_static/favicon.ico'
html_logo = '_static/logo.svg'
html_copy_source = False
html_show_sourcelink = False


# -- Options for LaTeX output -------------------------------------------------

latex_elements = {
    'inputenc': '\\usepackage[utf8x]{inputenc}'
}
