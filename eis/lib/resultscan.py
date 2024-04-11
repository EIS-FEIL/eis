# -*- coding: utf-8 -*- 
# $Id: resultscan.py 444 2016-03-11 16:18:31Z ahti $
"""Ülesannete vastuste skannimise andmebaasi laadimine

Skannitud failide kataloogis on fail nimega test.csv, milles on testi toimumisaja kõigi sooritajate vastused tuvastatud kujul. Faili igal real on semikooloniga eraldatult:
•	Soorituse tähis (6-kohaline, ilma sisekriipsuta soorituskoha koodi ja õpilase koodi vahel)
•	Alatesti tähis
•	Testiülesande järjekorranumber alatestis
•	Ülesandekomplekti tähis
•	Küsimuse kood
•	Küsimuse vastuse järjekorranumber
•	Vastuse kood

Iga soorituskoha kohta on oma kataloog, mille nimeks on soorituskoha tähis (KKK).
Soorituskoha kataloogis on failid:
KKKSSS.pdf - sooritaja testitöö
SSS/ - sooritaja alamkataloog

Sooritaja alamkataloogis on failid nimedega:
A_Y_V.jpg – ühe ülesande vastuse väljalõige
A_Y_V_K_N.jpg – ühe küsimuse ühe vastuse väljalõige

Kus:
KKK – soorituskoha tähis
SSS – sooritaja tähis
A – alatesti tähis
Y – testiülesande järjekorranumber alatestis
K – küsimuse kood
V – ülesandekomplekti tähis
N – küsimuse vastuse järjekorranumber (kui küsimusel on ainult üks vastus, siis 1).
"""

from PIL import Image

from eis.lib.base import *
from eis.lib.helpers import fstr
from eis.lib.resultentry import ResultEntry
from eis.lib.blockentry import BlockEntry

log = logging.getLogger(__name__)

class ResultScan(object):
    
    def __init__(self, handler, toimumisaeg, sisestuskogum):
        self.handler = handler
        self.toimumisaeg = toimumisaeg
        self.sisestuskogum = sisestuskogum
        #self.errors = {} # väljade veateated, mis takistavad salvestamist
        self.warnings = {} # kasutab BlockEntry

    def load_scan(self, kataloog):
        """Skannitud failid laaditakse andmebaasi.
        """
        self.cnt_img = 0 # laaditud piltide arv
        self.cnt_sooritus = 0 # laaditud soorituste arv, kelle vastused on tuvastatud
        error = None
        total = n = 0
        notfound = 0

        # CSV-failis olevate ylesannete tähiste ja andmebaasis olevate ID-de vastavus
        self.map_k = {}
        for komplekt in self.toimumisaeg.komplektid:
            self.map_k[komplekt.tahis] = komplekt

        self.map_y = {}
        on_digiteerimine = False
        for hk in self.sisestuskogum.hindamiskogumid:
            log.debug('hindamiskogum %s' % hk.id)
            on_digiteerimine |= hk.on_digiteerimine
            for ty in hk.testiylesanded:
                log.debug('ylesanne: %s.%s' % (ty.alatest_seq, ty.seq))
                self.map_y[(ty.alatest_seq, ty.seq)] = (ty, hk)

        if not len(self.map_y):
            error = 'Sisestuskogumis %s ei ole ühtki ülesannet' % (self.sisestuskogum.tahis)
            return error

        # tuvastatud vastuste laadimine
        if on_digiteerimine:
            fn = os.path.join(kataloog, 'test.csv')
            if os.path.exists(fn):
                error = self._read_csv(fn)
                if error:
                    return error
            else:
                error = 'Puudub tuvastatud vastuste fail test.csv'
                return error

        # soorituskohtade kataloogidest piltide laadimine
        try:
            li = os.listdir(kataloog)
        except OSError as e:
            error = 'Kataloogi ei saa lugeda'
            return error
        for basename in li:
            fn = os.path.join(kataloog, basename)
            if os.path.isdir(fn):
                # soorituskoha kataloog
                error = self._load_koht(fn, basename)
                if error:
                    return error

        #if not error:
        #    error = u'Ei olnud midagi viga'
        return error
    
    def _read_csv(self, fn):
        """Tuvastatud vastuste laadimine andmebaasi
        """
        error = None
        total = 0
        #notfound = 0

        # loeme faili test.csv, kus on tuvastatud vastused
        prev_tahis = None
        sooritus = None # jooksev sooritus
        data = {} # yhe sooritaja vastused
        f = open(fn, 'r')
        for line in f.readlines():
            line = line.strip()
            if not line:
                continue
            li_line = line.split(';')
            if len(li_line) != 7:
                error = 'Vigane rida: %s' % line
                return error

            tahis, alatest_t, ty_seq, komplekt_tahis, kysimus_kood, kv_seq, vastus_kood = li_line
            try:
                alatest_t = int(alatest_t)
                ty_seq = int(ty_seq)
            except:
                error = 'Vigane ülesande tähis: %s' % line
                return error
            
            if len(tahis) != 6:
                error = 'Vigasel kujul soorituse tähis: %s' % tahis
                return error

            if tahis != prev_tahis:
                if data:
                    error = self._save_sooritus(sooritus, data, komplekt_tahis)
                    if error:
                        return error

                sooritus = self._get_sooritus(tahis)
                if not sooritus:
                    error = 'Sooritust %s ei leitud' % tahis
                    return error
                if sooritus.staatus != const.S_STAATUS_TEHTUD:
                    msg = 'Sooritust %s ei ole tehtud' % tahis
                    log.error(msg)
                    if self.handler:
                        self.handler.notice(msg)

                data = {}
                prev_tahis = tahis
                prev_komplekt_tahis = komplekt_tahis

            alatest_seq = int(alatest_t)
            m = self.map_y.get((alatest_seq, ty_seq))
            if not m:
                error = 'Ülesannet %s.%s sisestuskogumis ei ole' % (alatest_seq, ty_seq)
                return error
            ty, hk = m
            if not hk.on_digiteerimine:
                error = 'Hindamiskogum %s pole märgitud vastuste tuvastamiseks' % (hk.tahis)
                return error

            if komplekt_tahis != prev_komplekt_tahis:
                error = 'Sooritusel %s on korraga mitu komplekti (%s, %s)' % \
                    (tahis, prev_komplekt_tahis, komplekt_tahis)
                return error

            if ty.id not in data:
                data[ty.id] = {}
            if kysimus_kood not in data[ty.id]:
                data[ty.id][kysimus_kood] = []
            data[ty.id][kysimus_kood].append({'kood1':vastus_kood})

        f.close()
        if data:
            error = self._save_sooritus(sooritus, data, komplekt_tahis)
            return error
    
    def _save_sooritus(self, sooritus, data, komplekt_tahis):
        """Ühe soorituse kokku kogutud vastuste salvestamine
        """
        komplekt = self.map_k.get(komplekt_tahis)
        if not komplekt:
            error = 'Komplekt %s ei ole sellel toimumisajal kasutatavate komplektide seas' % komplekt_tahis
            return error
        
        hindamiskogumid = set()
        for ty_id, params in data.items():
            # salvestame ylesande vastused
            ty = model.Testiylesanne.get(ty_id)
            vy_seq = 1
            vy = ty.get_valitudylesanne(komplekt, vy_seq)
                
            ylesandevastus = sooritus.give_ylesandevastus(ty.id, vy.id)

            log.debug('Vastuse salvestamine: sooritus %d (%s), vy %d, y %d' %\
                          (sooritus.id, sooritus.tahised, vy.id, vy.ylesanne_id))
            #log.debug(params)

            blockentry = BlockEntry(self, True)
            responses = blockentry.save_entry(ylesandevastus, vy, params, 1, 
                                              const.SISESTUSVIIS_VASTUS,
                                              validate=True)
            if blockentry.error:
                log.debug(blockentry.error)
                return blockentry.error

            #sisestamata = blockentry.sisestamata
            if blockentry.sisestamata:
                log.debug('sooritus %s, ty %s: sisestamata' % (sooritus.id, ty.id))

            hindamiskogumid.add(ty.hindamiskogum)

        # arvutame tulemuse
        testiosa = sooritus.testiosa
        test = testiosa.test
        rs = ResultEntry(self.handler, const.SISESTUSVIIS_VASTUS, test, testiosa)
        sooritaja = sooritus.sooritaja
        for hk in hindamiskogumid:
            holek = sooritus.give_hindamisolek(hk)
            holek.komplekt = komplekt
            rs.update_hindamisolek(sooritaja, sooritus, holek)

        self.cnt_sooritus += 1

        return None   

    def _load_koht(self, kataloog, testikoht_tahis):
        """Laadime PDFid
        """
        try:
            li = os.listdir(kataloog)
        except OSError as e:
            error = 'Kataloogi ei saa lugeda'
            return error

        for basename in li:        
            fn = os.path.join(kataloog, basename)
            log.debug('FAIL: %s' % fn)

            # sooritaja vastused kogu sisestuskogumile on failis KKKSSS.pdf

            # kas on PDF?
            m = re.search('(\d{6})\.pdf', basename)
            if m:
                tahis = m.group(1)
                sooritus = self._get_sooritus(tahis)
                if not sooritus:
                    error = 'Sooritust %s ei leitud' % tahis
                    return error
                if sooritus.staatus != const.S_STAATUS_TEHTUD:
                    msg = 'Sooritust %s ei ole tehtud' % tahis
                    log.error(msg)
                    if self.handler:
                        self.handler.notice(msg)

                solek = sooritus.give_sisestusolek(self.sisestuskogum, const.VASTUSTESISESTUS)
                solek.skann = self._read_file(fn)    
                solek.staatus = const.H_STAATUS_HINNATUD
                continue

            # kas on sooritaja kataloog?
            m = re.search('(\d{3})', basename)
            if m and os.path.isdir(fn):
                tahis = '%s%s' % (testikoht_tahis, basename)
                sooritus = self._get_sooritus(tahis)
                if not sooritus:
                    error = 'Sooritust %s ei leitud' % tahis
                    return error
                if sooritus.staatus != const.S_STAATUS_TEHTUD:
                    msg = 'Sooritust %s ei ole tehtud' % tahis
                    log.error(msg)
                    if self.handler:
                        self.handler.notice(msg)

                error = self._load_sooritus_img(sooritus, fn)
                if error:
                    return error
                continue

            log.info('Arusaamatu failinimi: %s' % fn)

    def _load_sooritus_img(self, sooritus, kataloog):    
        """Ühe soorituse piltide laadimine
        """
        # A_Y_V.jpg – ühe ülesande vastuse väljalõige
        # A_Y_V_K_N.jpg – ühe küsimuse ühe vastuse väljalõige
        try:
            li = os.listdir(kataloog)
        except OSError as e:
            error = 'Kataloogi ei saa lugeda'
            return total, error

        for basename in li:        
            fn = os.path.join(kataloog, basename)

            # kysimuse vastuse pilt
            m = re.search('(\d+)\_(\d+)\_([^_]+)\_([^_]+)\_(\d+)\.jpg', basename)
            on_kysimus = m
            if not m:
                # kas on ylesande pilt
                m = re.search('(\d+)\_(\d+)\_([^_]+).jpg', basename)

            if m:
                alatest_seq = int(m.group(1))
                ty_seq = int(m.group(2))
                komplekt_tahis = m.group(3)

                r = self.map_y.get((alatest_seq, ty_seq))
                if not r:
                    error = 'Failinimi %s: ei leia ülesannet %s.%s' % (basename, alatest_seq, ty_seq)
                    return error
                
                komplekt = self.map_k.get(komplekt_tahis)
                if not komplekt:
                    error = 'Failinimi %s: ei leia komplekti %s' % (basename, komplekt_tahis)
                    return error
                #sooritus.komplekt = komplekt
                
                ty, hk = r
                vy_seq = 1
                vy = ty.get_valitudylesanne(komplekt, vy_seq)
                ylesandevastus = sooritus.give_ylesandevastus(ty.id, vy.id)
                ylesandevastus.valitudylesanne = vy

                holek = sooritus.give_hindamisolek(ty.hindamiskogum)
                holek.komplekt = komplekt

                self.cnt_img += 1
                if on_kysimus:
                    kysimus_kood = m.group(4)
                    kv_seq = int(m.group(5))

                    kysimus = vy.ylesanne.get_kysimus(kysimus_kood)
                    kv = ylesandevastus.give_kysimusevastus(kysimus.id)
                    item = kv.give_skann(kv_seq)
                else:
                    item = ylesandevastus

                try:
                    image = Image.open(fn)
                except Exception as e: # IOError
                    # pole pildifail
                    raise
                    width = height = None
                else:
                    width, height = image.size
                log.debug('  pilt: %s' % fn)
                item.skann = self._read_file(fn)
                item.laius_orig = width
                item.korgus_orig
            else:
                # kataloogis on fail Thumbs.db
                log.info('Arusaamatu failinimi %s' % fn)

    def _get_sooritus(self, tahised):
        """Leiame soorituse. 
        Parameetriks on sooritus skannitud failides esineval kujul, st ilma sidekriipsuta.
        """
        tahised = tahised[:3] + '-' + tahised[3:]
        rcd = model.Sooritus.query.\
            filter_by(toimumisaeg_id=self.toimumisaeg.id).\
            filter_by(tahised=tahised).\
            first()
        return rcd

    def _read_file(self, fn):
        f = open(fn, 'rb')
        try:
            data = ''
            while True:
                bytes = f.read()
                if not bytes:
                    break
                data += bytes
            return data
        finally:
            f.close()
