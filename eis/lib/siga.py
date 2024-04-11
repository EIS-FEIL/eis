import requests
import json
import urllib
from datetime import datetime
import hmac
import hashlib
import base64
import pprint
import logging
log = logging.getLogger(__name__)
import eiscore.const as const

class Siga:
    "SiGa allkirjastamisteenuse kasutamine"

    handler = None
    settings = None
    log_dir = None
    
    def __init__(self, handler=None, settings=None):
        if handler:
            self.handler = handler
            if not settings:
                settings = handler.request.registry.settings
            
        self.settings = settings
        self.url = settings.get('siga.url')
        self.service_uuid = settings.get('siga.service_uuid')
        self.secret = settings.get('siga.secret')
        self.http_proxy = settings.get('http_proxy') or None
            
    def new_hashcodecontainers(self, files):
        # uude konteinerisse failide lisamine
        return self.add_hashcodecontainers(None, files)

    def add_hashcodecontainers(self, container_id, files):
        # juba moodustamisel olevasse konteinerisse failide lisamine
        dataFiles = []
        for filename, filedata in files:
            filesize = len(filedata)
            hash256 = base64.b64encode(hashlib.sha256(filedata).digest()).decode('ascii')
            hash512 = base64.b64encode(hashlib.sha512(filedata).digest()).decode('ascii')
            datafile = {'fileName': filename,
                        'fileHashSha256': hash256,
                        'fileHashSha512': hash512,
                        'fileSize': filesize,
                        }
            dataFiles.append(datafile)
        data = {'dataFiles': dataFiles}
        if container_id:
            # konteiner on juba loodud
            uri = '/hashcodecontainers/{containerId}/datafiles'.format(containerId=container_id)
        else:
            # uue konteineri loomine
            uri = '/hashcodecontainers'
        return self._call('POST', uri, data)

    def upload_hashcodecontainers(self, b64_filedata):
        # olemasoleva konteineri sisu saatmine
        data = {'container': b64_filedata}
        return self._call('POST', '/upload/hashcodecontainers', data)

    def get_hashcodecontainers(self, container_id):
        uri = '/hashcodecontainers/{containerId}'.format(containerId=container_id)
        err, res = self._call('GET', uri)        
        return err, res
    
    def delete_hashcodecontainers(self, container_id):
        uri = '/hashcodecontainers/{containerId}'.format(containerId=container_id)
        err, res = self._call('DELETE', uri)        
        #res['result'] = 'OK'
        return err, res

    def validationreport(self, container_id):
        uri = '/hashcodecontainers/{containerId}/validationreport'.format(containerId=container_id)
        err, res = self._call('GET', uri)        
        return err, res

    def smartid_certificatechoice(self, container_id, isikukood, country):
        if not container_id or not isikukood or not country:
            log.error('certificatechoice - parameetrid puuduvad')
            return 'Päringu parameetrid puuduvad', None
        
        data = {'personIdentifier': isikukood,
                'country': country,
                }
        uri = f'/hashcodecontainers/{container_id}/smartidsigning/certificatechoice'
        err, res = self._call('POST', uri, data)
        if err == 'NOT_FOUND':
            err = 'Smart-ID leping puudub'
        return err, res
            
    def smartid_certificatechoice_status(self, container_id, cert_id):
        if not container_id:
            log.error('smartid_certificatechoice_status - parameetrid puuduvad')
            return 'Päringu parameetrid puuduvad', None

        uri = f'/hashcodecontainers/{container_id}/smartidsigning/certificatechoice/{cert_id}/status'
        err, res = self._call('GET', uri)
        if not err:
            status = res['sidStatus']
            if status == 'CERTIFICATE':
                # sert on valitud
                err = None
            elif status == 'OUTSTANDING_TRANSACTION':
                # toiming veel kestab
                err = False
            else:
                # viga
                errors = {
                    'CERTIFICATE': 'Sert valitud',
                    'OUTSTANDING_TRANSACTION': 'Toiming kestab,staatuse päringut tuleb korrata',
                    'EXPIRED_TRANSACTION': 'Tegevus aegus enne, kui kasutaja jõudis allkirjastada',
                    'USER_CANCEL': 'Kasutaja katkestas telefonil allkirjastamise',
                    'DOCUMENT_UNUSABLE': 'Allkirjastamist ei saa lõpule viia',
                    }
                err = errors.get(status)
        return err, res
    
    def smartidsigning(self, container_id, doc_no, profile, msg=None):
        
        data = {'documentNumber': doc_no,
                }
        if not msg and self.handler:
            if self.handler.c.inst_name == 'clone':
                msg = "Testide keskkond"
            else:
                msg = "Eksamite infosüsteem"
        if msg:
            data['messageToDisplay'] = msg
        data['signatureProfile'] = profile

        uri = f'/hashcodecontainers/{container_id}/smartidsigning'
        err, res = self._call('POST', uri, data)
        return err, res

    def smartidsigning_status(self, container_id, signature_id):
        if not container_id:
            log.error('smartidsinging_status - parameetrid puuduvad')
            return 'Päringu parameetrid puuduvad', None

        uri = f'/hashcodecontainers/{container_id}/smartidsigning/{signature_id}/status'
        err, res = self._call('GET', uri)
        if not err:
            status = res['sidStatus']
            if status == 'SIGNATURE':
                # allkiri antud
                err = None
            elif status == 'OUTSTANDING_TRANSACTION':
                # toiming veel kestab
                err = False
            else:
                # viga
                errors = {
                    'SIGNATURE': 'Allkiri antud',
                    'OUTSTANDING_TRANSACTION': 'Toiming kestab,staatuse päringut tuleb korrata',
                    'EXPIRED_TRANSACTION': 'Tegevus aegus enne, kui kasutaja jõudis allkirjastada',
                    'USER_CANCEL': 'Kasutaja katkestas telefonil allkirjastamise',
                    'DOCUMENT_UNUSABLE': 'Allkirjastamist ei saa lõpule viia',
                    'USER_SELECTED_WRONG_VC': 'Verifitseerimiskood valiti valesti',
                    'NOT_SUPPORTED_BY_APP': 'Kasutaja Smart-ID rakendus ei võimalda seda tegevust',
                    }
                err = errors.get(status)
        return err, res
    
    def mobileidsigning(self, container_id, isikukood, phoneno, profile):
        language = 'EST'
        if not isikukood or not container_id:
            log.error('mobileidsigning - parameetrid puuduvad')
            return 'Päringu parameetrid puuduvad', None
        if not phoneno:
            log.error('mobileidsigning - telefon puudub')
            return 'Ilma telefoninumbrita ei saa allkirjastada', None
        
        data = {'personIdentifier': isikukood,
                'phoneNo': phoneno,
                'language': language,
                'signatureProfile': profile,
                }
        uri = '/hashcodecontainers/{containerId}/mobileidsigning'.format(containerId=container_id)
        err, res = self._call('POST', uri, data)
        if err == 'NOT_FOUND':
            err = 'Mobiil-ID leping puudub'
        return err, res
            
    def mobileidsigning_status(self, container_id, signature_id):
        if not container_id:
            log.error('mobileidsinging_status - parameetrid puuduvad')
            return 'Päringu parameetrid puuduvad', None

        uri = '/hashcodecontainers/{containerId}/mobileidsigning/{signatureId}/status'.format(containerId=container_id, signatureId=signature_id)
        err, res = self._call('GET', uri)
        if not err:
            status = res['midStatus']
            if status == 'SIGNATURE':
                # allkiri antud
                err = None
            elif status == 'OUTSTANDING_TRANSACTION':
                # toiming veel kestab
                err = False
            else:
                # viga
                errors = {
                    'SIGNATURE': 'Allkiri antud',
                    'OUTSTANDING_TRANSACTION': 'Toiming kestab,staatuse päringut tuleb korrata',
                    'EXPIRED_TRANSACTION': 'Tegevus aegus enne, kui kasutaja jõudis allkirjastada',
                    'USER_CANCEL': 'Kasutaja katkestas telefonil allkirjastamise',
                    'MID_NOT_READY': 'Telefoni Mobiil-ID funktsionaalsus ei ole veel kasutatav, proovida mõne aja pärast uuesti',
                    'INTERNAL_ERROR': 'Allkirjastamisteenuse tehniline viga',
                    'NOT_VALID': 'Tekkinud signatuur ei valideeru',
                    'SENDING_ERROR': 'Muu sõnumi saatmise viga (telefon ei suuda sõnumit vastu võtta, sõnumikeskus häiritud)',
                    'SIM_ERROR': 'SIM rakenduse viga',
                    'PHONE_ABSENT': 'Sõnumi saatmine ebaõnnestus, telefon ei ole levis',
                    }
                err = errors.get(status)
        return err, res

    def start_remotesigning(self, container_id, profile, certificate):
        if not container_id or not certificate:
            log.error('remotesigning - parameetrid puuduvad')
            return 'Päringu parameetrid puuduvad', None

        data = {'signingCertificate': certificate,
                'signatureProfile': profile,
                }
        uri = '/hashcodecontainers/{containerId}/remotesigning'.format(containerId=container_id)
        # dataToSign, digestAlgorithm, generatedSignatureId
        return self._call('POST', uri, data)

    def finalize_remotesigning(self, container_id, signature_id, signature):
        if not container_id or not signature_id:
            log.error('remotesigning - parameetrid puuduvad')
            return 'Päringu parameetrid puuduvad', None

        data = {'signatureValue': signature,
                }
        uri = '/hashcodecontainers/{containerId}/remotesigning/{signatureId}'.format(containerId=container_id, signatureId=signature_id)
        err, res = self._call('PUT', uri, data)
        if err:
            code = res and res.get('errorCode')
            if code == 'SIGNATURE_CREATION_EXCEPTION':
                # Unable to finalize signature
                err = 'Ei saa allkirjastada'
        return err, res
    
    def _headers(self, method, uri, body):
        # UTC ajahetk
        #ts = str(int(datetime.utcnow().timestamp()))
        ts = str(int(datetime.now().timestamp()))

        # koostame sõnumi allkirja
        uri = urllib.parse.quote(uri)
        sig_msg = ':'.join((self.service_uuid, ts, method, uri, body))
        sig_b = hmac.new(self.secret.encode(),
                         msg=sig_msg.encode(),
                         digestmod=hashlib.sha256)
        signature = sig_b.hexdigest().upper()

        # sõnumi päis
        headers = {'X-Authorization-Timestamp': ts,
                   'X-Authorization-ServiceUUID': self.service_uuid,
                   'X-Authorization-Signature': signature,
                   }
        if method in ('POST', 'PUT'):
            headers['Content-Type'] = 'application/json; charset=UTF-8'
        return headers
            
    def _call(self, method, uri, params=None):
        response = ''
        timeout = (5,20)
        if params:
            data = json.dumps(params)
        else:
            data = ''
        headers = self._headers(method, uri, data)
        url = self.url + uri

        def _err(ex, response):
            msg = 'Autentimisteenuse viga'
            buf = '%s (%s) %s' % (msg, url, ex.__class__.__name__) +\
                  '\n' + str(ex) + \
                  '\n' + response +\
                  '\nSisend:\n' + str(data)
            if self.handler:
                self.handler._error_mail(buf, msg=buf)
            log.error(buf)
            return msg, None

        self._trace_msg(method, uri, headers, params, 'in')
        
        try:
            args = {'headers': headers,
                    'timeout': timeout,
                    }
            if self.http_proxy:
                args['proxies'] = {'https': self.http_proxy}
                
            if method == 'GET':
                response = requests.get(url, **args)
            elif method == 'POST':
                response = requests.post(url, data=data, **args)
            elif method == 'PUT':
                response = requests.put(url, data=data, **args)
            elif method == 'DELETE':
                response = requests.delete(url, **args)
            else:
                raise Exception('Unsupported method %s' % method)
        except requests.exceptions.HTTPError as ex:
            return _err(ex, response)
        except requests.exceptions.Timeout as ex:
            return _err(ex, response)
        else:
            res = response.json()
            self._trace_msg(method, uri, None, res, 'out')
            code = res.get('errorCode')
            if code:
                err = res.get('errorMessage')
                return err, res
            else:
                return None, res

    def _trace_msg(self, method, uri, headers_json, params_json, ext):
        if headers_json:
            headers_txt = pprint.pformat(headers_json, width=120)
        else:
            headers_txt = ''
        txt = pprint.pformat(params_json, width=120)
        userik = self.handler and self.handler.c.user.isikukood
        log.info(f'{ext} {method} {uri} ({userik})\n{headers_txt}\n{txt}\n')

        if self.handler:
            c = self.handler.c
            request = self.handler.request
            log_label = f'{ext} {method} {uri}'
            self.handler.log_add(const.LOG_JSON, txt, log_label)

if __name__ == '__main__':
    from eis.scripts.scriptuser import *
    log.setLevel(logging.DEBUG)
    for log_h in log.handlers:
        log_h.setLevel(logging.DEBUG)
        
    srv = Siga(settings=registry.settings,
               handler=handler)
    if True:
        files = [('proov.txt', b'ABCD')]
        err, res = srv.new_hashcodecontainers(files)
        if err:
            print(err)
        else:
            container_id = res['containerId']
            err, res = srv.delete_hashcodecontainers(container_id)
            if err:
                print(err)
        
