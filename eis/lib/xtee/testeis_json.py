"Oma JSON teenuste testimine"
import requests
from datetime import datetime, timedelta
from eis.lib.xtee.xroadclientjson import XroadClientJSON
import logging
log = logging.getLogger(__name__)
import eiscore.i18n as i18n
_ = i18n._

class EISJSON(XroadClientJSON):
    producer = 'eis'

    def __init__(self, handler=None, userid=None, settings=None):
        XroadClientJSON.__init__(self, handler, userid, settings)

    def _args(self, issue=None):
        headers = {'Content-Type': 'application/json; charset=utf-8',
                   'X-Road-Client': self._callerid,
                   }
        if self.userid:
            headers['X-Road-UserId'] = self.userid
        if issue:
            headers['X-Road-Issue'] = issue
        # timeout: connect, read
        timeout = (5,60)
        args = {'headers': headers,
                'timeout': timeout,
                }
        return args

    def opirada_testisooritused(self, test_id, isikukoodid):
        url = f'{self.baseurl}/opirada/testisooritused' + f'?test_id={test_id}'
        for ik in isikukoodid:
            url += f'&isikukood={ik}'
        args = self._args()
        log.debug(url)
        call_started = datetime.now()
        try:
            res = requests.get(url, **args)
            text = res.text
        except Exception as ex:
            text = str(ex)
            self.on_fault(ex, 'opirada_tulemused', url)
        else:
            data = res.json()
            return data

    def hsilm_tulemused(self, aasta, testiliik, alates, min_sooritaja_id, max_arv):
        url = f'{self.baseurl}/hsilm/tulemused' + f'?aasta={aasta}&testiliik={testiliik}'
        if alates:
            url += f'&alates={alates.isoformat()}'
        if min_sooritaja_id:
            url += f'&min_sooritaja_id={min_sooritaja_id}'
        if max_arv:
            url += f'&max_arv={max_arv}'
        args = self._args()
        log.debug(url)
        call_started = datetime.now()
        try:
            res = requests.get(url, **args)
            text = res.text
        except Exception as ex:
            text = str(ex)
            self.on_fault(ex, 'hsilm_tulemused', url)
        else:
            data = res.json()
            return data

    def hsilm_rvtunnistused(self, aasta):
        url = f'{self.baseurl}/hsilm/rvtunnistused' + f'?aasta={aasta}'
        args = self._args()
        log.debug(url)
        call_started = datetime.now()
        try:
            res = requests.get(url, **args)
            text = res.text
        except Exception as ex:
            text = str(ex)
            self.on_fault(ex, 'hsilm_rvtunnistused', url)
        else:
            data = res.json()
            return data

if __name__ == '__main__':
    # testeis_json.py -test_id 3232 -ik 30101010007,33003300303
    import pprint
    import logging
    logging.basicConfig(level=logging.DEBUG)
    from eis.scripts.scriptuser import *
    reg = EISJSON(handler=handler)
    reg.baseurl = 'http://localhost:5200/adapter'

    if 0:
        test_id = named_args.get('test_id')
        isikukoodid = named_args.get('ik').split(',')
        res = reg.opirada_testisooritused(test_id, isikukoodid)
        pprint.pprint(res)
    if 1:
        aasta = named_args.get('aasta')
        testiliik = named_args.get('testiliik')
        alates = datetime(2011,1,1)
        min_sooritaja_id = None
        max_arv = named_args.get('max_arv')
        res = reg.hsilm_tulemused(aasta, testiliik, alates, min_sooritaja_id, max_arv)
        pprint.pprint(res)
    if 1:
        aasta = named_args.get('aasta')
        res = reg.hsilm_rvtunnistused(aasta)
        pprint.pprint(res)
        
        
