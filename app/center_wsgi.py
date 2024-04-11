"ATS EKK vaate rakendus"
from pyramid.paster import get_app, setup_logging
INIFILE = '/srv/eis/etc/ats.ini'
setup_logging(INIFILE)
application = get_app(INIFILE, 'ekk')
