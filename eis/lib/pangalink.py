"Pangalink"

# Tehniline kirjeldus:
# https://www.luminor.ee/ee/pangalingi-paringute-tehniline-spetsifikatsioon#paringud
# http://www.seb.ee/ariklient/igapaevapangandus/maksete-kogumine/maksete-kogumine-internetis/pangalingi-tehniline-spetsifikatsioon. 
# https://partners.lhv.ee/et/banklink/
#
# SEB testpank:
# https://www.seb.ee/ariklient/igapaevapangandus/maksete-kogumine/maksete-kogumine-internetis#pangalink

import os
import glob
import string
from M2Crypto import RSA, Rand, m2, X509
import base64
import hashlib
import urllib.request, urllib.parse, urllib.error
from pytz import timezone
from datetime import datetime
from random import Random
import logging
log = logging.getLogger(__name__)

# kataloog, kus asuvad pankade alamkataloogid
BANKS_DIR = '/srv/eis/etc/pangalink'

# Kõigi pankade alamkataloogides peab olema konfifail config.ini.
# Pangalingi protokolliga liidestatud pankade alamkataloogides
# peavad olema failid eis_priv.pem ja pank_pub.pem.
# Nordea panga alamkataloogis peavad olema võtmefailid
# eis_priv.txt ja pank_pub.txt.

class Pangalink(object):
    "Eesti pankade pangalingi protokoll"

    encoding = 'UTF-8'
    #encoding = 'ISO-8859-1'
    
    @classmethod
    def get_list(cls):
        """Tagastatakse list nendest pankadest, millel on pankade
        kataloogis oma alamkataloog ning konfifail selle sees.
        """
        conf_template = '%s/*/config.ini' % BANKS_DIR
        items = []

        for fn in glob.glob(conf_template):
            pank_id = fn.split('/')[-2]
            items.append(cls.get_instance(pank_id, fn))
        return items

    @classmethod
    def get_instance(cls, pank_id, fn=None):
        """Tagastatakse panga objekt
        """
        pank = Pangalink(pank_id, fn)
        return pank

    # Konfifailist saadavad andmed:
    # logo pildifaili URL
    logo = None
    # panga nimi kasutajale logo alt atribuudina kuvamiseks
    alt = None
    # panga URL, kuhu päringud postitada
    url = None
    # infosüsteemi ID pangaga sõlmitud lepingus
    pos_id = None
    ## makse saaja konto (kui pole lepingus)
    #acc = None
    ## makse saaja nimi (kui pole lepingus)
    #name = None
    
    # infosysteemi salajase võtme fail pangakataloogis
    _priv_key = 'eis_priv.pem'
    # panga avaliku võtme fail pangakataloogis
    _pub_key = 'pank_pub.pem' 
    
    def __init__(self, pank_id, fn=None):
        """Panga objekti loomine
        pank_id - panga identifikaator, panga kataloogi nimi
        fn - panga kataloogis oleva config.ini täielik rada
        """
        if not fn:
            fn = '%s/%s/config.ini' % (BANKS_DIR, pank_id)
        f = open(fn, 'r')
        for line in f.readlines():
            arr = line.split('=',1)
            if len(arr) == 2:
                key = arr[0].strip()
                value = arr[1].strip()
                #if key in ('logo', 'url', 'pos_id', 'acc', 'name'):
                if key in ('logo', 'url', 'pos_id', 'alt'):
                    self.__setattr__(key, value)
        f.close()
        self.id = pank_id
        self.priv_key = os.path.join(BANKS_DIR, pank_id, self._priv_key)
        self.pub_key = os.path.join(BANKS_DIR, pank_id, self._pub_key)

    def is_configured(self):
        """Kontrollitakse, kas võtmefailid on olemas
        """
        return os.path.isfile(self.priv_key) and \
            os.path.isfile(self.pub_key)

    def gen_1012(self, kasutaja_id, tasu, mille_eest, ret_url, stamp):
        """Lepingus näidatud kontoga makse päringu koostamine
        """
        return self._gen_payment(kasutaja_id, tasu, mille_eest, '1012', ret_url, stamp)

    def _gen_payment(self, kasutaja_id, tasu, mille_eest, service, ret_url, stamp):
        """Makse päringu koostamine
        """
        assert service == '1012', 'Vale teenus'
        vk_datetime = datetime.now(timezone('Europe/Tallinn')).strftime('%Y-%m-%dT%H:%M:%S%z')
        params = {'VK_SERVICE': service,
                  'VK_VERSION': '008',
                  'VK_SND_ID': self.pos_id,
                  'VK_STAMP': stamp,
                  'VK_AMOUNT': '%s' % tasu,
                  'VK_CURR': 'EUR',
                  'VK_REF': '2900082401',
                  'VK_MSG': mille_eest,
                  'VK_RETURN': ret_url,
                  'VK_CANCEL': ret_url,
                  'VK_DATETIME': vk_datetime,                  
                  'VK_ENCODING': self.encoding,
                  'VK_LANG': 'EST',
                }
        params['VK_MAC'] = self._sign(params)
        return params

    def verify(self, request):
        """Pangast tulnud sõnumi allkirja kontrollimine
        """
        # 1111 - makse toimumise teade
        # 1911 - ebaõnenstunud tehingu teade
        
        #params = self._get_encoded_params(request, self.encoding)
        params = request.params
        service = params.get('VK_SERVICE')
        mac = params.get('VK_MAC')
        if not service:
            # pangast tulnud kasutaja on välja logitud ja peale uut sisenemist tagasi tulles ei ole enam parameetreid
            return False, 'Viga maksmisandmete kättesaamisel', params
        if self._verify(params, mac):
            if service == '1111':
                return True, None, params
            else:
                return False, 'Tehing ebaõnnestus', params
        else:
            return False, 'Sõnumi valideerimine ebaõnnestus', params

    def get_msg(self, params):
        # pangast tulnud vastusest makse selgituse väljalugemine 
        return params.get('VK_MSG')

    def get_stamp(self, params):
        # pangast tulnud vastusest makse id väljalugemine 
        return params.get('VK_STAMP')    

    def get_return_stamp(self, params):
        # pangast tulnud vastusest makse id väljalugemine 
        return params.get('VK_STAMP')    

    def gen_stamp(self, makse_id):
        assert makse_id, 'ID on null'
        return str(makse_id)

    def _gen_message_str(self, data):
        """Moodustame stringi, mis allkirjastatakse
        """
        # väljad (sõnumi numbri järgi), mille sisu kasutatakse MACi arvutamisel
        MAC_FIELDS = {
            #'1001':('VK_SERVICE', 'VK_VERSION', 'VK_SND_ID', 'VK_STAMP', 'VK_AMOUNT', 'VK_CURR', 'VK_ACC', 'VK_NAME', 'VK_REF', 'VK_MSG'),
            '1012':('VK_SERVICE', 'VK_VERSION', 'VK_SND_ID', 'VK_STAMP', 'VK_AMOUNT', 'VK_CURR', 'VK_REF', 'VK_MSG', 'VK_RETURN', 'VK_CANCEL', 'VK_DATETIME'),
            #'1101':('VK_SERVICE', 'VK_VERSION', 'VK_SND_ID', 'VK_REC_ID', 'VK_STAMP', 'VK_T_NO', 'VK_AMOUNT', 'VK_CURR', 'VK_REC_ACC', 'VK_REC_NAME', 'VK_SND_ACC', 'VK_SND_NAME', 'VK_REF', 'VK_MSG', 'VK_T_DATE'),
            #'1901':('VK_SERVICE', 'VK_VERSION', 'VK_SND_ID', 'VK_REC_ID', 'VK_STAMP', 'VK_REF', 'VK_MSG'),
            '1111':('VK_SERVICE', 'VK_VERSION', 'VK_SND_ID', 'VK_REC_ID', 'VK_STAMP', 'VK_T_NO', 'VK_AMOUNT', 'VK_CURR', 'VK_REC_ACC', 'VK_REC_NAME', 'VK_SND_ACC', 'VK_SND_NAME', 'VK_REF', 'VK_MSG', 'VK_T_DATETIME'),
            '1911':('VK_SERVICE', 'VK_VERSION', 'VK_SND_ID', 'VK_REC_ID', 'VK_STAMP', 'VK_REF', 'VK_MSG'),            
            }

        service = data.get('VK_SERVICE')
        fields = MAC_FIELDS.get(service)
        if not fields:
            raise Exception('Vale teenuse number %s' % service)

        buf = ''
        for key in fields:
            value = data[key] or ''
            buf += '%03d%s' % (len(value), value)

        #return buf
        return buf.encode(self.encoding)

    def _sign(self, params):
        """Päringu allkirjastamine, MACi arvutamine
        """   
        buf = self._gen_message_str(params)
        h = hashlib.new('sha1')
        h.update(buf)
        digest = h.digest()
        rsa = RSA.load_key(self.priv_key)
        signature = rsa.sign(digest, 'sha1')
        return base64.b64encode(signature).decode('ascii').replace('\n','')

    def _verify(self, params, mac):
        """Pangast tulnud sõnumi allkirja kontrollimine
        """
        buf = self._gen_message_str(params)
        signature = base64.b64decode(mac)

        # serdiga verifitseerimine käib nii
        # pub_cert = BANKS_DIR+'/seb/pank_cert.pem'
        # x509 = X509.load_cert(pub_cert)
        # pubkey = x509.get_pubkey()
        # pubkey.reset_context(md='sha1')
        # pubkey.verify_init()
        # pubkey.verify_update(buf)
        # verify = pubkey.verify_final(signature)
        # return verify == 1

        # panga võti peab algama reaga, kus on BEGIN PUBLIC KEY
        # kui pank annab oma serdi (BEGIN CERTIFICATE), siis 
        # tuleb sellest esmalt või välja võtta:
        # openssl x509 -pubkey -noout -in pank_cert.pem > pank_pub.pem

        # avaliku võtmega verifitseerimine käib nii
        h = hashlib.new('sha1')
        h.update(buf)
        digest = h.digest()
        rsa = RSA.load_pub_key(self.pub_key)
        try:
            verify = rsa.verify(digest, signature, 'sha1')
        except RSA.RSAError as e:
            raise
        return verify == 1

