import requests
import json
from datetime import datetime, date
import inspect, pprint
import eiscore.const as const
from eiscore.recordwrapper import RecordWrapper
import logging
log = logging.getLogger(__name__)
from eis.lib.exceptions import APIIntegrationError

import threading
thread_local = threading.local()
def get_rsession(key):
    key = f'{key}_session'
    if not hasattr(thread_local, key):
        setattr(thread_local, key, requests.Session())
    return getattr(thread_local, key)

def json_handler(x):
    if isinstance(x, datetime):
        return x.isoformat()
    raise TypeError("Unknown type")

class APIClient:
    apikey = None
    def __init__(self, handler):
        self.handler = handler
        request = handler.request
        host = request.registry.settings.get(f'{self.apikey}.host')
        if not host:
            raise Exception(f'{self.apikey}.host seadistamata')
        self.host = host
        
    def check(self):
        url = '/check'
        res = self.apicall(url, None)
        return res

    def _get_headers(self):
        headers = {}
        return headers

    def _decode_response(self, response):
        return response.json()
    
    def apicall(self, url, data, ok_status=200, post=None):
        headers = self._get_headers()
        if not self.host:
            raise Exception('Host puudub ({api})'.format(api=self.apikey))
        url = f'{self.host}{url}'
        if post is None:
            is_post = data and True or False
        else:
            is_post = post
        log.debug(f'{self.apikey} {is_post and "POST" or "GET"} {url}')        
        if data and is_post:
            data = RecordWrapper.to_dict_rec(data)
            #log.debug(f'{url} INPUT\n{pformat(data)}')

            # json
            class Encoder(json.JSONEncoder):
                def default(self, o):
                    if type(o) is date or type(o) is datetime:
                        return o.isoformat()
            data = Encoder().encode(data)

        # esinevad ConnectionErrorid - proovime mitu korda
        # ConnectionError(ProtocolError('Connection aborted.', OSError(9, 'Bad file descriptor'))
        # ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))
        # ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))
        # ConnectionError(MaxRetryError("HTTPConnectionPool(host='eisexam-4', port=8000): Max retries exceeded 
        MAX_TRY = 3
        for try_cnt in range(MAX_TRY):
            try:
                res = self._apicall_exec(url, data, headers, is_post, try_cnt + 1)
            except APIIntegrationError as ex:
                if isinstance(ex.orig_exc, requests.exceptions.ConnectionError):
                    if try_cnt < MAX_TRY:
                        # proovime uuesti
                        log.info(f'try #{try_cnt+1} {str(ex.orig_exc)}')
                        continue
                    else:
                        log.info(f'try max {str(ex.orig_exc)}')
                        raise
                else:
                    try:
                        log.info(f'notry {str(ex.orig_exc.__class__)}: {str(ex.orig_exc)}')
                    except:
                        pass
                    raise
            return res
            
    def _apicall_exec(self, url, data, headers, is_post, try_cnt):
        "API pöördumine"
        status = response = None
        call_started = datetime.now()        
        method = is_post and 'POST' or 'GET'
        try:
            rsession = get_rsession(self.apikey)
            if is_post:
                response = rsession.post(url, data=data, headers=headers, timeout=(5, None))
            else:
                response = rsession.get(url, params=data, headers=headers, timeout=(5, None))
            res = self._decode_response(response)
            status = response.status_code
        except Exception as ex:
            out = response and response.text or ''
            log.error(f'APIIntegrationError:\n{str(ex)} #{try_cnt}')
            raise APIIntegrationError(ex, method, url, out, status, data, try_cnt)
        else:
            try:
                # kas on olemas raamistiku genereeritud viga
                error = res.get('detail')
            except Exception as ex:
                # väljund ei ole dict
                error = None
            if error:
                out = response and response.text                
                raise APIIntegrationError(error, method, url, out, status, data)
        finally:
            duration = (datetime.now() - call_started).total_seconds()            
            param = data and str(data) or None
            sisu = response and (response.text or f'STATUS {response.status_code}') or ''
            c = self.handler.c
            self.handler.log_add(const.LOG_JSON, sisu, param, kestus=duration,
                                 url=url, method=method)

        # log.debug(f'{url} OUTPUT:\n{pformat(res)}')
        return res

def pformat(data):
    #return str(len(str(data)))
    return pprint.pformat(data)
    #return pprint.pformat(simplify(data))

def simplify(data):
    if isinstance(data, dict):
        data1 = {}
        for key, value in data.items():
            # skalaarsed elemendid jätame ära, välja arvatud id
            if key == 'id' or isinstance(value, (dict,list,tuple)):
                data1[key] = simplify(value)
        return data1
    elif isinstance(data, (list, tuple)):
        data1 = []
        for item in data:
            data1.append(simplify(item))
        return data1
    else:
        return data

