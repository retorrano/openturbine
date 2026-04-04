import os
import sys
sys.path.insert(0, os.path.abspath('../src'))

project = 'OpenTurbine'
copyright = '2025, Romano E. Torrano'
author = 'Romano E. Torrano'
version = '0.1.0'
release = '0.1.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', '_build']

html_theme = 'sphinx_rtd_theme'
