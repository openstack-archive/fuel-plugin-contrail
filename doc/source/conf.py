from distutils.version import LooseVersion
from sphinx import __version__ as sphinx_version

mypreamble=ur'''
\renewcommand{\Verbatim}[1][1]{%
  % list starts new par, but we don't want it to be set apart vertically
  \bgroup\parskip=0pt%
  \smallskip%
  % The list environement is needed to control perfectly the vertical
  % space.
  \list{}{%
  \setlength\parskip{0pt}%
  \setlength\itemsep{0ex}%
  \setlength\topsep{0ex}%
  \setlength\partopsep{0pt}%
  \setlength\leftmargin{10pt}%
  }%
  \item\MakeFramed {\FrameRestore}%
  \small  % <---------------- To be changed!
  \OriginalVerbatim[#1]%
}
'''




source_suffix = '.rst'
master_doc = 'index'

project = u'Contrail plugin for Fuel'
copyright = u'2016, Mirantis Inc.'

version = '5.1-5.1.0-1'
release = '5.1-5.1.0-1'

pygments_style = 'sphinx'

latex_documents = [
  ('index','fuel-plugin-contrail-doc.tex',
   u'Contrail plugin for Fuel Documentation',
   u'Mirantis Inc.', 'manual')
]

# Configuration for the latex/pdf docs.
latex_elements = {
    'papersize': 'a4paper',
    'pointsize': '11pt',
    # remove blank pages
    'classoptions': ',openany,oneside',
    'babel': '\\usepackage[english]{babel}',
    'preamble':mypreamble,
    'fontpkg': '\usepackage[T1]{fontenc}'
}

if LooseVersion(sphinx_version) >= LooseVersion('1.3.1'):
    html_theme = "sphinx_rtd_theme"

html_add_permalinks = ""
html_show_copyright = False
highlight_language = 'none'
