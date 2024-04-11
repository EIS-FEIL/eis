from datetime import datetime, timedelta
from eis.lib.xtee.xroad import *

import logging
log = logging.getLogger(__name__)

import eiscore.const as const

class Ads(XroadClientEIS):
    """Aadressregistri teenuste kasutamine
    """
    producer = 'ads'
    namespace = 'http://www.maaamet.ee'    

    def kompklassif(self, alates, logId=None, maxarv=100):    
        param = E.Request(E.muudetudAlates(alates))
        if logId:
            param.append(E.logId(logId))
        param.append(E.maxarv(maxarv))
        list_path = ['/klassifTulem/muudatus',]
        try:
            res = self.call('ADSkompklassif.v2', param, list_path)
            if res:
                li = res.find('klassifTulem/muudatus')
                return None, li
        except SoapFault as e:
            return e.faultstring, []
        return None, []
    
    def aadrmuudatused(self, alates, logId=None, maxarv=100, muudetudPaevad=10):
        "Aadressimuudatuste päring"
        param = E.Request(E.muudetudAlates(alates),
                          E.muudetudPaevad(muudetudPaevad))
        if logId:
            param.append(E.logId(logId))
        param.append(E.maxarv(maxarv))
        list_path = ['/muudatused/muudatus',]
        try:
            res = self.call('ADSaadrmuudatused.v6', param, list_path)
            if res:
                li = res.find('muudatused/muudatus')
                return None, li
        except SoapFault as e:
            return e.faultstring, []
        return None, []
        
if __name__ == '__main__':
    import logging
    logging.basicConfig()
    log = logging.getLogger('xteeclient')
    
    from eis.scripts.scriptuser import *
    admin = named_args.get('admin')
    if admin:
        admin = 'EE%s' % admin  
    reg = Ads(settings=registry.settings,
              userId=admin)

    alates = date.today() - timedelta(days=637)
    if 1:
        msg, res = reg.aadrmuudatused(alates)
        print(msg or res)
        sys.exit(0)

    if 1:
        msg, res = reg.kompklassif(alates)
        print(msg or res)
        sys.exit(0)
        
    try:
        soap_li = reg.allowedMethods()
    except SoapFault as e:
        print(e.faultstring)
    else:
        li = [str(item) for item in list(soap_li)]
        li.sort()
        for item in li:
            print(item)

