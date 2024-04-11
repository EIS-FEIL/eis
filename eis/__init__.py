__version__ = '3.0.132'
__product_name__ = 'EIS'
__vendor__ = 'HTM'
__static_version__ = '3.0.132'
__cktimestamp__ = '3.0.95'

from sqlalchemy import engine_from_config, pool
from pyramid.config import Configurator
from pyramid_beaker import session_factory_from_settings
import pyramid_handlers
import pyramid_mako
from pyramid.events import BeforeRender, NewRequest
from pyramid.paster import get_appsettings, setup_logging
import pyramid.url as url
import eis.forms.validators as validators
import logging
log = logging.getLogger(__name__)
LOGCONF = '/srv/eis/etc/logging.ini'

from eiscore.i18n import locale_negotiator, add_localizer, add_renderer_trans

def main(global_config, **settings):
   """ WSGI rakenduse loomine
   """
   import eis.model as model
   import eis.model_s as model_s
   import eis.model_log as model_log
   
   setup_logging(LOGCONF)

   # võtame kasutusele globaalse konfi, mis on pärit konfifaili sektsioonist DEFAULTS
   d = global_config.copy()
   d.update(settings)
   settings = d

   # rakenduse nimi: eis, ekk, eksam
   app_name = settings.get('app_name')
   is_live = settings.get('live') != 'false'
   is_test = settings.get('test') == 'true'
   is_ext = settings.get('is_ext') == 'true'

   # andmebaasiühenduse loomine
   def _poolcls(dbkey):
      if settings.get('%s.pool_size' % dbkey):
         # SQLAlchemy pool
         return pool.QueuePool
      else:
         # ei kasuta oma pooli; kasutusel on pgbouncer
         return pool.NullPool

   # põhibaas
   engine = engine_from_config(
      settings,
      'sqlalchemy.',
      poolclass=_poolcls('sqlalchemy'))
   model.initialize_sql(engine)

   # põhibaasi read-only replica
   engine_r = engine_from_config(
      settings,
      'sqlalchemy_ro.',
      poolclass=_poolcls('sqlalchemy_ro'))
   model.initialize_read_sql(engine_r)
   
   engine_s = engine_from_config(
      settings,
      'sqlalchemy_s.',
      poolclass=_poolcls('sqlalchemy_s'),
      isolation_level='AUTOCOMMIT')
   model_s.DBSession.configure(bind=engine_s)

   engine_log = engine_from_config(settings,
                                   'sqlalchemy_log.',
                                   poolclass=_poolcls('sqlalchemy_log'))
   model_log.DBSession.configure(bind=engine_log)
   
   session_factory = session_factory_from_settings(settings)
   
   # session.type=ext:sqla korral
   session_factory._options['bind'] = model_s.DBSession.bind
   session_factory._options['table'] = model_s.Beaker_cache.__table__

   route_prefix = settings.get('route_prefix')
   config = Configurator(settings=settings,
                         session_factory=session_factory,
                         route_prefix=route_prefix)
   config.add_request_method(lambda x: is_ext, 'is_ext')

   config.include(pyramid_handlers.includeme)
   config.include(pyramid_mako.includeme)
   config.set_locale_negotiator(locale_negotiator)
   
   config.add_translation_dirs('eiscore:locale/')
   config.add_translation_dirs('formencode:i18n/')
   config.add_subscriber(add_localizer, NewRequest)

   config.add_subscriber(add_renderer_globals, BeforeRender)
   
   # isikukoodide valideerimise väljakeeramine, kui on nii konfitud
   # (et saaks EHISe vigaste isikukoodidega testandmeid kasutada)
   if settings.get('ehis.check_digit') == 'false':
       validators.isikukood.check_digit = False

   # URLide ruutingu seadistamine
   from . import routing
   routing.make_map(config, settings, app_name, is_live, is_test)

   if not is_live:
       # staatilisi faile serveerib live-is apache/nginx
       # aga järgnev on mõeldud ainult pserve kaudu kasutamise jaoks
       import os
       # staatiliste failide URLidel pole rakenduse prefiksit
       config.route_prefix = None
       staticapp_dir = os.getcwd().rsplit('/',1)[0] + '/staticapp'
       config.add_static_view('/modules', staticapp_dir + '/node_modules')
       config.add_static_view('static', staticapp_dir + '/static')
  
   app = config.make_wsgi_app()
   return app

# globaalsete muutujate lisamine makos kasutamiseks
def add_renderer_globals(event):
    event['model'] = model
    event['model_s'] = model_s
    event['const'] = model.const
    add_renderer_trans(event)

def none_unicode(value):
   """Mako filter (vt konfifailis mako.default_filters), mis teeb nii, 
   et None väärtuseid kuvatakse tühja stringina, mitte stringina 'None'
   """
   if value is None:
      return ''
   else:
      return str(value)
