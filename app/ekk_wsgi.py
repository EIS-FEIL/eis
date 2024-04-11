"Plankide mooduli rakendus"
from pyramid.paster import get_app, setup_logging
INIFILE = '/srv/eis/etc/config.ini'
setup_logging(INIFILE)
application = get_app(INIFILE, 'ekk')
