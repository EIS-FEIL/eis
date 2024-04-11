import os
import sys
import re
from setuptools import setup, find_packages

with open('eis/__init__.py', 'r') as f:
    VERSION = re.search("__version__ = '([0-9\.]+)'", f.read()).groups()[0]

here = os.path.abspath(os.path.dirname(__file__))

requires = [
    'argon2',
    'babel',
    'cffi',
    'captcha',
    'chameleon==4.5.2',
    #'cryptography==38.0.4',
    'jellyfish',
    'jwt',
    'pyOpenSSL==21.0.0',
    'ndg-httpsclient==0.5.1', 
    'FormEncode==2.0.1',
    'latex2sympy2==1.7.8',
    'lxml',
    'httplib2==0.20.2',
    'minio',
    #'m2secret==0.1.1',
    'Mako>=1.1.6',
    'py3DNS',
    'paginate_sqlalchemy',
    'pandas',
    'Pillow>=8.1.2', # cygwinis kasutada python39-imaging
    'Paste==3.7.1',
    'PasteDeploy==3.1.0',
    'PasteScript==3.3.0',
    'psutil',
    'psycopg2-binary',
    'pymediainfo==5.1.0',
    'pyramid==2.0.2',
    'pyramid_debugtoolbar==4.9',
    'pyramid_beaker==0.8',
    'pyramid_handlers==0.5',
    'pyramid_mako==1.1.0',
    'pyramid_simpleform==0.7.dev0',
    'pypdf',
    'pyrtf3',
    'reportlab==4.0.7',
    'requests==2.27.1',
    'rncryptor==3.3.0',
    'svglib',
    'SQLAlchemy==1.4.27',
    'WebHelpers2==2.1',
    'WebOb==1.8.7',
    'WebTest==2.0.33',
    'Beaker==1.11.0',
    'simplejson',
    'pytz',
    'unidecode',
    'xlsxwriter',
    'weasyprint',
    'sympy',
    'plotly',
    'pycha==0.8.1',
    ]
test_requires = [
    'WebTest==2.0.33',
    'WSGIProxy2',
    ]

setup(name='EIS',
      version=VERSION,
      description='Eksamite infosüsteem',
      author='HTM',
      author_email='',
      url='',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='eis.tests',
      install_requires = requires,
      entry_points = """\
      [paste.app_factory]
      main = eis:main
      """,
      )

