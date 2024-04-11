# MinIO S3 failide kirjutamine ja lugemine
import random
import string
import io
import time
import minio
import os
import fcntl
import mimetypes
import re
import pymediainfo
import eiscore.const as const
from eis.model.usersession import get_threading_data, get_request

import logging
log = logging.getLogger(__name__)

CACHE_PATH = '/srv/eis/var/filecache'

def create_s3client(settings):
    endpoint = settings.get('minio.endpoint')
    access_key = settings.get('minio.access_key')
    secret_key = settings.get('minio.secret_key')
    bucket_name = settings.get('minio.bucket_name')
    if not endpoint or not access_key or not secret_key or not bucket_name:
        raise Exception('Minio konfimata')
    client = minio.Minio(endpoint, access_key, secret_key, secure=False)
    return client, bucket_name

class S3File:
    "Failide kirjutamine/lugemine MinIO S3-s"
    # peavad olema atribuudid: filename, filesize, fileversion, id, _cache_dir
    # (kui id=None, siis ka funktsioon: give_seq_id)

    def _get_threading_data(self):
        return get_threading_data()

    def _get_request(self):
        # yle laadida, vajab Sessioni
        return get_request()

    def _get_s3client(self):
        # yle laadida, vajab Sessioni
        data = self._get_threading_data()
        try:
            client = data.s3client
            bucket_name = data.s3bucket_name
        except AttributeError:
            client = None
        if not client:
            request = self._get_request()
            settings = request.registry.settings
            client, bucket_name = create_s3client(settings)
            data.s3client = client
            data.s3bucket_name = bucket_name
        return client, bucket_name

    @property
    def filedata(self):
        "Faili sisu lugemine failist"
        if not self.fileversion:
            return
        client, bucket_name = self._get_s3client()        
        path = self._filedata_path
        response = None
        try:
            log.debug('MINIO read %s' % path)
            response = client.get_object(bucket_name, path)
            filedata = response.read()
            return filedata
        except minio.error.S3Error as ex:
            raise
        finally:
            if response is not None:
                response.close()
                response.release_conn()

    @filedata.setter
    def filedata(self, value):
        "Faili sisu salvestamine failis"
        if self.fileversion:
            # kui varem oli fail, siis märgitakse see kustutamiseks
            self.set_file_deleted()

        if value is None:
            # tühi fail
            if self.fileversion:
                self.fileversion = None
                self.filename = None
                self.filesize = None
        else:
            # faili sisu
            client, bucket_name = self._get_s3client()        
            fsize = self.filesize = len(value)
            fbuf = io.BytesIO(value)
            self.fileversion = self.gen_version()
            path = self._filedata_path
            log.debug(f'minio {self.id} put {path}')
            client.put_object(bucket_name, path, fbuf, fsize)

    def set_file_deleted(self):
        "Fail märgitakse kustutamiseks"
        from eis.model.deletefile import Deletefile
        path = self._filedata_path
        Deletefile(path)

    def copy_file(self, src):
        "Kopeeritakse kirjes src olev fail"
        assert src.id != self.id, 'oma faili kopeerimine'
        client, bucket_name = self._get_s3client()        
        self.filesize = src.filesize
        try:
            self.filename = src.filename
        except AttributeError as ex:
            # filename puudub T_Sisuobjekt jms korral
            pass
        self.fileversion = self.gen_version()
        path = self._filedata_path
        orig_path = src._filedata_path
        log.debug(f'minio {self.id} copy {orig_path} to {path}')
        cps = minio.commonconfig.CopySource(bucket_name, orig_path)
        client.copy_object(bucket_name, path, cps)

    @property
    def _filedata_path(self):
        "Faili asukoht S3 kataloogis"
        obj_id = self.id or self.give_seq_id()

        # ID jagatakse kahe tasemega kataloogideks
        a = '%09d' % obj_id
        obj_path = a[:-6]+'/'+a[-6:-3]+'/'+a[-3:]
        
        path = '{}/{}.{}'.format(self._cache_dir,
                                 obj_path,
                                 self.fileversion)
        return path

    @classmethod
    def decompose_path(cls, path):
        m = re.match(r'(.+)/(\d+)/(\d+)/(\d+)\.(.*)', path)
        tblname, id1, id2, id3, fileversion = m.groups()
        obj_id = int(id1 + id2 + id3)
        return tblname, obj_id, fileversion
    
    @property
    def has_file(self):
        return self.fileversion is not None
   
    @property
    def fileext(self):
        if self.filename:
            return self.filename.split('.')[-1]
   
    @property
    def mimetype(self):
        filename = self.filename
        if filename:
            fileext = filename.split('.')[-1]
            ctypes = {const.ASICE: const.CONTENT_TYPE_ASICE,
                      const.ASICS: const.CONTENT_TYPE_ASICS,
                      const.BDOC: const.CONTENT_TYPE_BDOC,
                      const.DDOC: const.CONTENT_TYPE_DDOC,
                      'm4a': 'audio/mpeg', # mimetypes pakub video/mp4
                      }
            mimetype = ctypes.get(fileext)
            if not mimetype:
                (mimetype, encoding) = mimetypes.guess_type(filename)
            return mimetype

    def gen_version(self):
        buf = string.ascii_letters + string.digits
        len = 8
        rnd = ''.join(random.Random().sample(buf, len))
        return rnd

    def audio_duration(self, filedata):
        "Leitakse helifaili pikkus sekundites"
        try:
            info = pymediainfo.MediaInfo.parse(io.BytesIO(filedata))
            return int(info.tracks[0].duration / 1000)
        except Exception as ex:
            log.error(ex)
            
    # puhvri funktsioonid
    
    @property
    def _filedata_cache_path(self):
        "Faili asukoht rakendusserveri puhvris"
        obj_id = self.id or self.give_seq_id()
        path = '{}/{}/{}.{}.{}'.format(CACHE_PATH,
                                       self._cache_dir,
                                       obj_id,
                                       self.fileversion,
                                       self.fileext or '')
        return path

    @property
    def path_for_response(self):
        "Tagastab puhvri failinime ja tagab, et fail on puhvris olemas"
        if not self.has_file:
            # faili ei ole
            return
        path = self._filedata_cache_path
        log.debug(f'path_for_response: {path}')
        for cnt in range(3):
            # teeme mitu katset
            # võimalusel loeme puhvrist
            if os.path.exists(path):
                return path
            else:
                # puhvris ei olnud
                # lukustame puhvrifaili, et see luua
                data = self._set_cached_filedata(path)
                if not data:
                    return

    def _set_cached_filedata(self, path):
        data = None
        with CacheFileLock(path) as lock:
            if lock:
                data = self.filedata
                if data is not None:
                    lock.fd.write(data)
                    lock.is_data = True
                    log.debug(f'WRITE cache {path}')
            elif lock is None:
                # ootame veidi, et teine saaks faili kirjutada
                time.sleep(3)
                log.info(f'WRITE cache lock sleep {path}')
        return data

class CacheFileLock:
    def __init__(self, fn):
        self.fd = None
        self.fn = fn
        self.is_data = False
        
    def __enter__(self):
        try:
            self.fd = open(self.fn, 'wb')
        except IOError:
            # kui faili ei saanud teha, kuna kataloogi pole, siis loome kataloogi
            # e.errno == 13 - Permission denied
            parent = os.path.dirname(self.fn)
            if not os.path.exists(parent):
                os.mkdir(parent)
                try:
                    self.fd = open(self.fn, 'wb')
                except IOError:
                    pass
            if self.fd is None:
                return False
        try:
            fcntl.flock(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except IOError:
            # keegi on juba lukustanud
            # e.errno == 11 - Resource temporarily unavailable
            return None
        return self

    def release(self):
        if self.fd:
            fcntl.flock(self.fd, fcntl.LOCK_UN)
            self.fd.close()
            if not self.is_data:
                # faili ei saanud kirjutada, vbl oli S3 maas
                os.remove(self.fn)
        self.fd = None

    def __exit__(self, type, value, traceback):
        self.release()
  
    def __del__(self):
        self.release()    

def get_s3_row_by_path(path):
    import eis.model as model
    import eis.model_s as model_s
    
    tblname, obj_id, fileversion = S3File.decompose_path(path)
    sess = model.Session
    tbl_map = {'avalehepilt': model.Avalehepilt,
               'toorvastus': model_s.Toorvastus,
               'toimumisprotokoll': model.Toimumisprotokoll,
               'testifail': model.Testifail,
               'toofail': model.Toofail,
               'tunnistus': model.Tunnistus,
               'helivastusfail': model.Helivastusfail,
               'kogufail': model.Kogufail,
               'kvsisu': model.Kvsisu,
               'ruumifail': model.Ruumifail,
               'vaidefail': model.Vaidefail,
               'sisuobjekt': model.Sisuobjekt,
               'skannfail': model.Skannfail,
               'statistikaraport': model.Statistikaraport,
               't_sisuobjekt': model.T_Sisuobjekt,
               't_ylesandefail': model.T_Ylesandefail,
               'yhisfail': model.Yhisfail,
               'ylesandefail': model.Ylesandefail,
               }
    if tblname == 'toorvastus':
        sess = model_s.DBSession
    else:
        sess = model.Session
    tbl = tbl_map[tblname]
    q = (sess.query(tbl)
         .filter_by(id=obj_id)
         .filter_by(fileversion=fileversion)
         )
    rcd = q.first()
    return rcd

def s3file_init(tblname, item):
    obj = S3File()
    obj.id = int(item.id)
    obj.filename = item.filename
    obj.fileversion = item.fileversion
    obj._cache_dir = tblname    
    return obj

def s3file_save(tblname, item, filedata):
    "Faili salvestamine ilma SQLAlchemy objektita"
    obj = s3file_init(tblname, item)
    # salvestame minios
    obj.fileversion = None
    obj.filedata = filedata
    # jätame andmed meelde
    item.fileversion = obj.fileversion
    item.filesize = obj.filesize

def s3file_get(tblname, item):
    "Faili lugemine ilma SQLAlchemy objektita"
    obj = s3file_init(tblname, item)
    return obj.filedata

class S3FileBuf:
    "Digitempliga suhtlemise failid"
    def __init__(self):
        obj = S3File()
        self.client, self.bucket_name = obj._get_s3client()
        
    def s3file_put(self, filedir, filename, filedata):
        "Faili salvestamine sama nime all antud kataloogis, ilma kirjeta (digitempli jaoks)"
        fsize = len(filedata)
        fbuf = io.BytesIO(filedata)
        path = f'{filedir}/{filename}'
        log.debug(f'minio put {path}')
        self.client.put_object(self.bucket_name, path, fbuf, fsize)

    def s3file_list(self, filedir):
        "Failide loetelu kataloogis (digitempli jaoks)"
        return self.client.list_objects(self.bucket_name, prefix=filedir + '/')

    def s3file_get(self, path):
        response = self.client.get_object(self.bucket_name, path)
        filedata = response.read()
        return filedata

    def s3file_remove(self, path):
        self.client.remove_object(self.bucket_name, path)
        
