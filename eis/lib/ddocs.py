# -*- coding: utf-8 -*-
"Digidoc-failidega tegelevad funktsioonid digiallkirjastamiseks"

import cgi
import binascii
import re
import base64
import hashlib
import json
from zipfile import ZipFile, ZIP_STORED
import io
import time
from datetime import datetime
from pyramid.response import Response
import logging
log = logging.getLogger(__name__)

from eis.lib.siga import Siga
from eis.lib.utils import guess_type
from eis.lib.inmemoryzip import InMemoryZip
import eiscore.const as const
from eis.forms import validators

class DdocS:
    "Digidoc-failide töötlemine SiGa allkirjastamisteenuse abil"

    @classmethod
    def prepare_signature(cls, handler, filedata, filename, error=None, test_params=None):
        """Allkirjastamise alustamine
        filedata - juba varem loodud konteiner, kuhu hakkame allkirja lisama
        filename - faili nimi või laiend, millest saadakse aru, mis fail see on
        """
        ddocs = DdocS(handler)
        
        if not error:
            ext = filename.rsplit('.')[-1].lower()
            files = None
            if ext == const.ZIP:
                # luua uus konteiner
                files = InMemoryZip(filedata).extract()
            elif ext not in ('bdoc','asice'):
                # luua uus konteiner
                files = [(filename, filedata)]
            if files:
                filedata = ddocs.create_bdoc_files(files)
                files = None
            elif ext not in (const.BDOC, const.ASICE):
                error = 'Ei saa jätkata allkirjastamist, fail on %s' % (ext)
        if not error:
            # allkirjastame olemasoleva konteineri
            error, container_id = ddocs._start_session(filedata)

        if error:
            res = {'error': error,
                   'hash_hex': ''}
        else:
            profile = 'LT' # BDOC-TS, time-stamp (.asice)
            dformat = const.ASICE

        params = test_params or handler.request.params
        op = params.get('op')

        if op == 'smartid':
            # smart-ID allkirjastamine
            if not error:
                error, challenge_id, signature_id = \
                    ddocs._smartid_sign(container_id, profile, params)   
                res = {'error': error,
                       'challengeID': challenge_id,
                       'container_id': container_id,
                       'signature_id': signature_id,
                       'dformat': dformat,
                       }
            res['h'] = handler.h
            if not test_params:
                res = handler.render_to_response('/sign_s.mako', res)
            return filedata, res
        
        elif op == 'mobile':
            # mobiil-ID allkirjastamine
            if not error:
                error, challenge_id, signature_id = \
                    ddocs._mobile_sign(container_id, profile, params)   
                res = {'error': error,
                       'challengeID': challenge_id,
                       'container_id': container_id,
                       'signature_id': signature_id,
                       'dformat': dformat,
                       }
            res['h'] = handler.h
            if not test_params:
                res = handler.render_to_response('/sign_m.mako', res)
            return filedata, res
        
        else:
            # ID-kaardiga allkirjastamine
            handler.request.override_renderer = 'json'            
            if not error:
                res = ddocs._start_remotesigning(container_id, profile, dformat, params)
            res = Response(json_body=res)
            return filedata, res

    @classmethod
    def finalize_signature(cls, handler, orig_doc, err=None, test_params=None):
        """Allkirjastamise lõpetamine: brauserilt on saadud allkiri,
        see lisatakse pooleli oleva konteineri sisse.
        Tagastab valmis faili või None.
        handler - kontroller
        err - veateade
        orig_doc - algne BDOC
        """
        if err:
            handler.error(err)
            return None, None

        ddocs = DdocS(handler)

        params = test_params or handler.request.params
        # DigiDocService seansi kood
        container_id = params.get('container_id')
        signature_id = params.get('signature_id')
        dformat = params.get('dformat')

        # allkirjastatud fail
        doc_data = signers = None
        op = params.get('op')

        if op == 'smartid':
            # smart-ID allkiri, ootame tulemuse ära
            time.sleep(16)
            while True:
                # pollida brauserist!                
                log.info(f'container_id={container_id}, signature_id={signature_id}')
                err, res = ddocs.srv.smartidsigning_status(container_id, signature_id)
                if err is False:
                    # toiming veel kestab
                    time.sleep(4)
                    continue
                else:
                    # toiming sai edukalt läbi või tuli veateade
                    break
            
        elif op == 'mobile':
            # mobiil-ID allkiri, ootame tulemuse ära
            time.sleep(16)
            while True:
                # pollida brauserist!                
                #log.info('GetStatusInfo, sesscode=%s...' % sesscode)
                log.info(f'container_id={container_id}, signature_id={signature_id}')
                err, res = ddocs.srv.mobileidsigning_status(container_id, signature_id)
                if err is False:
                    # toiming veel kestab
                    time.sleep(4)
                    continue
                else:
                    # toiming sai edukalt läbi või tuli veateade
                    break
        else:
            # ID-kaardiga antud allkiri
            # kasutaja antud allkiri
            signature = _hex2base64(params.get('signature'))            
            err, res = ddocs.srv.finalize_remotesigning(container_id, signature_id, signature)
            if not err and res['result'] != 'OK':
                err = 'Allkirjastamisteenuse viga: ' + res['result']

        if not err:
            # tõmbame kogu faili SK-st
            #log.info('GetSignedDoc, sesscode=%s...' % sesscode)
            err, res = ddocs.srv.get_hashcodecontainers(container_id)
            if not err:
                b64_doc_data = res['container'].encode('utf-8')
                doc_data = base64.b64decode(b64_doc_data)
                # teisendame hashcode-kujult tavalisele kujule
                doc_data = _hashcode_to_bdoc(doc_data, orig_doc) 

                err, res = ddocs.srv.validationreport(container_id)
                signers = ddocs._get_signers(res)                    

            err, res = ddocs.srv.delete_hashcodecontainers(container_id)
        if err:
            handler.error(err)
        return doc_data, signers, dformat

    def __init__(self, handler):
        self.handler = handler
        self.srv = Siga(handler)
        
    def _start_remotesigning(self, container_id, profile, dformat, params):
        err = hash_hex = sig_no = None
        # parameetrina on antud kasutaja ID-kaardi sert hexitud DER-kujul
        cert = _hex2base64(params.get('cert_hex'))
        err, res = self.srv.start_remotesigning(container_id, profile, cert)
        if not err:
            signature_id = res['generatedSignatureId']
            data_to_sign = res['dataToSign']
            data_xml = base64.b64decode(data_to_sign)
            hash_hex = hashlib.sha512(data_xml).digest().hex().upper()
        # väljastame tulemuse brauserile
        res = {'error': err or '',
               'hash_hex': hash_hex or '',
               'signature_id': signature_id,
               'container_id': container_id,
               'dformat': dformat,
               }
        return res
    
    
    def _start_session(self, doc_data):
        """Allkirjastamise alustamine: brauserilt on saadud sert,
        selle kohta arvutatakse allkirjastatav räsi.
        Tagastab pooleli faili ja vastuse jsoni.
        BDOCi korral on alati olemas doc_data, vajadusel loome eelnevalt
        """
        container_id = None
        # asendame andmefailid räsidega
        doc_data = _bdoc_to_hashcode(doc_data)
        b_doc_data = base64.b64encode(doc_data).decode()
        err, res = self.srv.upload_hashcodecontainers(b_doc_data)
        if not err:
            container_id = res['containerId']
            assert container_id, 'containerId puudub'
        return err, container_id

    def _smartid_sign(self, container_id, profile, params):
        "Mobiil-ID allkirjastamine"

        # kasutajalt kysitakse serdi valikut (kui tal on mitu smart-ID lepingut)
        err, cert_id = self._smartid_certificatechoice(container_id)
        if not err:
            # pollitakse, kuni saadakse valitud sert
            err, doc_no = self._smartid_certificatechoice_status(container_id, cert_id)
        if not err:
            # alustatakse allkirjastamist
            err, res = self.srv.smartidsigning(container_id, doc_no, profile)
        if not err:
            challenge_id = res['challengeId']
            signature_id = res['generatedSignatureId']
            return None, challenge_id, signature_id
        else:
            return err, None, None

    def _smartid_certificatechoice(self, container_id):
        "Kasutaja hakkab valima serti, millega allkirjastab"
        def split_country(ik):
            if ik[0].isnumeric():
                # Eesti isikukood, ilma riigi prefiksita
                country = const.RIIK_EE
                code = ik
            else:
                # riigi prefix + isikukood
                ountry = ik[:2]
                code = ik[2:]
            return country, code
        
        err = None
        user = self.handler.c.user
        
        isikukood = user.isikukood
        #isikukood = '30303039914'
        country, code = split_country(isikukood)

        err, res = self.srv.smartid_certificatechoice(container_id, code, country)
        if not err:
            # Certfificate id required to poll the status.
            cert_id = res['generatedCertificateId']
        else:
            cert_id = None
        return err, cert_id

    def _smartid_certificatechoice_status(self, container_id, cert_id):
        "Vaatame, kas kasutaja on serdi valinud?"
        doc_no = None
        while True:
            # pollida brauserist!
            log.info(f'container_id={container_id}, cert_id={cert_id}')
            err, res = self.srv.smartid_certificatechoice_status(container_id, cert_id)
            if err is None:
                doc_no = res['documentNumber']
                break
            if err is False:
                # toiming veel kestab
                time.sleep(4)
                continue
            else:
                # toiming sai edukalt läbi või tuli veateade
                break
        return err, doc_no
    
    def _mobile_sign(self, container_id, profile, params):
        "Mobiil-ID allkirjastamine"
        err = None

        user = self.handler.c.user
        phoneno = params.get('phoneno')
        if phoneno == 'test' and \
               (self.handler.is_devel or self.handler.is_test):
            # testkeskkonnas automaatne mobiil-allkirjastamine
            if phoneno != user.telefon:
                user.session['USER.PHONENO'] = user.telefon = phoneno
                user.session.changed()
            isikukood = '60001019906'
            phoneno = '+37200000766'
        else:
            isikukood = user.isikukood
            try:
                phoneno = validators.MIDphone(not_empty=True).to_python(phoneno)
            except validators.formencode.api.Invalid as ex:
                err = ex.msg
            else:
                if phoneno != user.telefon:
                    user.session['USER.PHONENO'] = user.telefon = phoneno
                    user.session.changed()
        if not err:
            err, res = self.srv.mobileidsigning(container_id, isikukood, phoneno, profile)
        if not err:
            challenge_id = res['challengeId']
            signature_id = res['generatedSignatureId']
            return None, challenge_id, signature_id
        else:
            return err, None, None

    def list_signed(self, filedata):
        signers = []
        err, container_id = self._start_session(filedata)
        if not err:
            err, res = self.srv.validationreport(container_id)
            if not err:
                signers = self._get_signers(res)

        if not err:
            #log.info('CloseSession, sesscode=%s...' % sesscode)
            err, res = self.srv.delete_hashcodecontainers(container_id)
        return signers

    def _get_signers(self, res):
        signers = []
        try:
            siginfo = res['validationConclusion']['signatures']
        except Exception as e:
            log.error(str(e))
        else:
            for signer in siginfo:
                aeg = signer['claimedSigningTime']
                cn = signer['signedBy']
                signers.append(cn)
        return signers

    def create_bdoc(self, filename, filedata):
        "Loome uue allkirjadeta BDOC-faili"
        files = [(filename, filedata)]
        return self.create_bdoc_files(files)

    def create_bdoc_files(self, files):
        "Loome uue allkirjadeta BDOC-faili"
        files = unique_filenames(files)
        xml = ''
        for filename, filedata in files:
            mimetype = guess_type(filename)
            xml += '<manifest:file-entry manifest:media-type="{}" manifest:full-path="{}" />'.format(mimetype, filename)
        
        manifest_xml = """<?xml version="1.0" encoding="utf-8"?>
<manifest:manifest xmlns:manifest="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0">
<manifest:file-entry manifest:media-type="application/vnd.etsi.asic-e+zip" manifest:full-path="/" />
""" + xml + '</manifest:manifest>'

        files = [('mimetype', 'application/vnd.etsi.asic-e+zip'),
                 ('META-INF/manifest.xml', manifest_xml),
                 ] + files
        return _files_to_zip(files)

def _hex2base64(hex_value):
    # hex-kodeeringu teisendamine base64-kodeeringuks
    return base64.b64encode(bytearray.fromhex(hex_value)).decode()

def unique_filenames(files):
    filenames = list()
    files2 = list()
    for filename, filedata in files:
        ind = 0
        parts = filename.rsplit('.', 1)
        parts.insert(1, '0')
        while filename in filenames:
            ind += 1
            parts[1] = str(ind)
            filename = '.'.join(parts)
        filenames.append(filename)
        files2.append((filename, filedata))
    return files2
            
def list_signed(handler, filedata, filename):
    ddocs = DdocS(handler)
    return ddocs.list_signed(filedata)

def _bdoc_to_hashcode(doc_data):
    "Teisendame päris-konteineri hashcode-kujul konteineriks"
    # eemaldada kõik allkirjastatavad failid
    # lisada allkirjastatavate failide räsid kahes failis:
    # - META-INF/hashcodes-sha256.xml
    # - META-INF/hashcodes-sha512.xml
    f_in = io.BytesIO(doc_data)
    zf_in = ZipFile(f_in, mode='r')

    f_out = io.BytesIO()
    zf_out = ZipFile(f_out, mode='w')

    hashes = [[hashlib.sha256, 'hashcodes-sha256.xml', ''],
              [hashlib.sha512, 'hashcodes-sha512.xml', '']]
    
    for zfile in zf_in.namelist():
        contents = zf_in.read(zfile)
        if zfile == 'mimetype':
            # mitte-andmefail lisatakse hashcode-faili pakkimata kujul
            zf_out.writestr(zfile, contents, ZIP_STORED) 
        elif zfile.startswith('META-INF'):
            # mitte-andmefail lisatakse hashcode-faili
            zf_out.writestr(zfile, contents)
        else:
            # andmefailist tehakse räsi
            size = len(contents)
            for params in hashes:
                sha = params[0]
                hash_value = base64.b64encode(sha(contents).digest()).decode('ascii')
                buf = '<file-entry full-path="{}" hash="{}" size="{}"/>\n'.\
                      format(zfile, hash_value, size)
                params[2] += buf
    zf_in.close()

    # lisame räsifailid uude zip-faili
    for sha, fn, xml in hashes:
        xml = '<?xml version="1.0" encoding="utf-8"?>\n<hashcodes>\n' + xml + '</hashcodes>'
        zf_out.writestr('META-INF/{}'.format(fn), xml.encode('utf-8'))
    zf_out.close()
    return f_out.getvalue()

def _hashcode_to_bdoc(hash_doc, orig_doc):
    "Teisendame hashcode-kujul konteineri päris-konteineriks"
    # lisada andmefailid tagasi konteinerisse
    # eemaldada META-INF/hashcodes-*.xml
    f_in = io.BytesIO(hash_doc)
    zf_in = ZipFile(f_in, mode='r')

    f_orig = io.BytesIO(orig_doc)
    zf_orig = ZipFile(f_orig, mode='r')
    
    f_out = io.BytesIO()
    zf_out = ZipFile(f_out, mode='w')

    # mitte-räsifailid võetakse hashcodes-kujul failist
    for zfile in zf_in.namelist():
        if not zfile.startswith('META-INF/hashcodes-'):
            contents = zf_in.read(zfile)
            if zfile == 'mimetype':
                zf_out.writestr(zfile, contents, ZIP_STORED)
            else:
                zf_out.writestr(zfile, contents)
    zf_in.close()

    # andmefailid võetakse vanast failist
    for zfile in zf_orig.namelist():
        if not (zfile == 'mimetype' or zfile.startswith('META-INF')):
            contents = zf_orig.read(zfile)
            zf_out.writestr(zfile, contents)
    zf_orig.close()
    
    zf_out.close()
    return f_out.getvalue()

def _files_to_zip(files):
    "Loome uue zip-faili"
    f_out = io.BytesIO()
    zf_out = ZipFile(f_out, mode='w')
    for filename, file_data in files:
        if filename == 'mimetype':
            try:
                zf_out.writestr(filename, file_data, ZIP_STORED)
            except TypeError:
                # python 2.6
                zf_out.writestr(filename, file_data)
        else:
            zf_out.writestr(filename, file_data)
    zf_out.close()
    return f_out.getvalue()

