from datetime import datetime, timedelta
from eis.lib.xtee.xroad import *
import logging
log = logging.getLogger(__name__)

from eis.lib.xtee.rahvastikuregister import Rahvastikuregister
from eis.lib.xtee.ads import Ads
from eis.lib.xtee.ehis import Ehis
from eis.lib.xtee.notifications import Notifications
from eis.lib.xtee.testeis import TestEis

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG)
    log = logging.getLogger()
    from eis.scripts.scriptuser import *
    
    for regcls in (Rahvastikuregister, Ads, Ehis, Notifications, TestEis):
       reg = regcls(settings=registry.settings)
       print('\n%s' % reg.producer)
       try:
          res = reg.allowedMethods()
          for s in res:
             print('/'.join([s['xRoadInstance'],s['memberClass'],s['memberCode'],s['subsystemCode'],s['serviceCode'],s['serviceVersion']])) 
       except SoapFault as e:
          print(e.faultstring)
          raise
