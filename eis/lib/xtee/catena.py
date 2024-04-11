# ei ole kasutusel
import hashlib
import requests
import base64
from datetime import datetime
import logging
log = logging.getLogger(__name__)

class CatenaClient(object):
    base_url = None

    def __init__(self, handler=None, settings=None):
        """Parameetrid:
        handler - BaseControlleri objekt, mille kaudu saadakse settings ja user
        turvaserver - HOST või HOST:PORT
        asutus - infosüsteemi registrikood
        isikukood - kasutaja isikukood, 11-kohaline, ilma riigi prefiksita
        cert - HTTPS korral serdifaili nimi, muidu None
        key - HTTPS korral võtmefaili nimi, muidu None
        """
        if handler:
            self.handler = handler
            if not settings:
                settings = handler.request.registry.settings
            
        if settings:
            self.settings = settings
            self.base_url = settings.get('catena.base_url')
            self.username = settings.get('catena.user')
            self.password = settings.get('catena.pass')

    def _auth(self):
        return requests.auth.HTTPBasicAuth(self.username, self.password)
    
    def sign(self, data_hash):
        response = jresponse = err = None
        params = {
            'dataHash': {
                'algorithm': 'SHA-256',
                'value': data_hash,
                },
            'metadata': {},
            }
        url = '%s/api/v1/signatures' % self.base_url
        try:
            r = requests.post(url, json=params, auth=self._auth())
            #print(r.status_code)
            #print 'text:%s' % r.text
        except Exception as e:
            err = str(r)
        else:
            response = r.text
            if r.status_code != 200:
                #{u'errorCode': u'INVALID_REQUEST', u'timestamp': 1495021852320, u'errorMessage': u"Field 'dataHash': Invalid hash format", u'requestId': u'eac2d50f-8188-4126-9b75-5ad7501e5527'}
                err = str(r)
                #err = r.errorMessage               
            else:
                jresponse = r.json()
        return response, jresponse, err

    def verify(self, signature_id):
        response = jresponse = err = None
        url = '%s/api/v1/signatures/%s' % (self.base_url, signature_id)
        try:
            r = requests.get(url, auth=self._auth())
        except Exception as e:
            err = str(e)
        else:
            response = r.text
            if r.status_code != 200:
                err = r.text
            else:
                jresponse = r.json()
        return response, jresponse, err
        
if __name__ == '__main__':
    data = b'proov'
    data_hash = base64.b64encode(hashlib.sha256(data).digest()).strip()
    srv = CatenaClient()
    srv.base_url = 'https://tryout-catena-db.guardtime.net'
    srv.username = "ot.rdwCwd"
    #srv password = "JiKHIUhbPHhm"
    
    response, jresponse, err = srv.sign(data_hash)
    if err:
        print(err)
    else:
        signature_id = jresponse['id']
        signature = jresponse['signature']
        print(('id=%s' % jresponse['id']))
        print(('createdAt=%s' % datetime.fromtimestamp(jresponse['createdAt']/1000.)))

        response, jresponse, err = srv.verify(signature_id)
        if err:
            print(err)
        else:
            if jresponse['verificationResult']['status'] == 'OK':
                print('staatus OK')
            if jresponse['signature'] == signature:
                print('signatuur sama')
            data_hash2 = jresponse['details']['dataHash']['value']
            if data_hash == data_hash2:
                print('hash sama')
            print(('createdAt=%s' % datetime.fromtimestamp(jresponse['createdAt']/1000.)))    
