import sys
import os
import pickle
import re

from eis.lib.base import *
from eis.lib.importpackage import ImportPackage
from eis.lib.helpers import fstr
_ = model.usersession._

log = logging.getLogger(__name__)

class CsvImportPackage(ImportPackage):
    def __init__(self, filename, storage, aine, lang, imgdir=None, imgobjs=None, encoding=None):
        """Valikülesannete laadimine CSV-failist.
        imgdir - kataloogi nimi, kus on pildifailid (skriptist käivitamisel)
        imgobjs - dict kujul {fn: cgi.FileStorage} (veebist käivitamisel)
        Objekti atribuudid:
        is_error - kas õnnestus importimine või mitte
        messages - jada teadetest kasutajale (infoks)
        items - jada imporditud kirjetest        
        """
        super(CsvImportPackage, self).__init__()
        
        self.arhiveeritud_id = [] # arhiveeritud ylesanded
        if not model.Klrida.get_str('AINE', aine):
            self.error(_("Tundmatu õppeaine {s}").format(s=aine))
            self.is_error = True
            return

        if not model.Klrida.get_lang_nimi(lang):
            self.error(_("Tundmatu keel {s}").format(s=lang))
            self.is_error = True
            return
            
        self._set_teemad(aine)
        self._imgdir = imgdir
        self._imgobjs = imgobjs
        
        if filename:
            with open(filename, 'rb') as f:
                self._readfile(f, aine, lang, encoding)
        else:
            self._readfile(storage.file, aine, lang, encoding)

        if not self.is_error and self.arhiveeritud_id:
            msg = ', '.join([str(r) for r in self.arhiveeritud_id])
            self.notice(_("Arhiveeriti järgmised ülesanded:") + ' ' + msg)

    def _readfile(self, file, aine, lang, encoding):
        for n, line in enumerate(file):
            if encoding:
                try:
                    line = line.decode(encoding)
                except UnicodeDecodeError as e:
                    self.error("Fail pole %s kodeeringus" % encoding)
                    self.is_error = True
                    return
            else:
                line = utils.guess_decode(line)
            line = line.strip()
            if line:
                ylesanne = self._readline(n, line, aine, lang)
                if ylesanne:
                    self.items.append(ylesanne)
                elif self.is_error:
                    return

    def _readline(self, n_line, line, aine_kood, lang):
        cols = _split2(line)
        # Failis on iga ylesanne eraldi real, rea veerud on:
        #
        # ülesande nimetus
        # ülesande väline ID
        # teema (end valdkonna) kood või nimetus
        # alateema (end teema) kood või nimetus
        # küsimus või tööjuhend
        # tehniline töökäsk
        # pildi pealkiri
        # pildi failinimi (fail laaditakse samal ajal)
        # õigete valikute koodid, eraldatud komaga
        # õige valiku eest antavad punktid
        # valiku A tekst
        # valiku B tekst
        # valiku C tekst
        # valiku D tekst
        # valiku E tekst

        err = None

        class RowData(object):
            pass
        data = RowData()
        
        try:
            # peab olema vähemalt 2 valikut ehk vähemalt 10 veergu
            assert len(cols) >= 10, 'Liiga vähe veerge'
            data.y_nimi = _getstr(cols, 0, 256, True)
            data.y_kood = _getstr(cols, 1, 100) or None
            valdkond = _getstr(cols, 2)
            teema = _getstr(cols, 3)
            data.sp_nimi = _getstr(cols, 4, 256)
            data.sp_tookask = _getstr(cols, 5, 512)
            data.img_tiitel = _getstr(cols, 6, 256)
            data.img_filename = _getstr(cols, 7, 256)
            data.oige_koodid = _getstr(cols, 8, 1, islist=True)
            data.k_pallid = _getfloat(cols, 9, True)            

            v_nimed = [r.strip() for r in cols[10:]]
            # eemaldame lõpust tühjad valikud
            while v_nimed and not v_nimed[-1]:
                v_nimed.pop()
            assert len(v_nimed) > 1, _("Peab olema vähemalt 2 valikut")

            valikud = list()
            for v_seq, v_nimi in enumerate(v_nimed):
                # ASCIIs on 26 tähte, aga kokku on lepitud koodid A,B,C,...
                assert v_seq <= 26, _("Valikuid ei tohi olla rohkem kui {n}").format(n=26)
                v_kood = chr(65+v_seq)
                valikud.append((v_seq+1, v_kood, v_nimi))

            v_koodid = [r[1] for r in valikud]
            for kood in data.oige_koodid:
                assert kood in v_koodid, _("Õige valiku kood {s} ei ole võimalike valikute seas").format(s=kood)
            data.valikud = valikud
            
            assert not teema or valdkond, _("Teemat ei saa määrata ilma valdkonnata")
            data.teema_kood, data.alateema_kood = self._get_teema(aine_kood, valdkond, teema)
        except AssertionError as ex:
            err = str(ex)

        if not err:
            # leiame senise ylesande, vajadusel arhiveerime
            ylesanne = self._get_task(aine_kood, data.y_kood, lang)
            if ylesanne is None:
                # loome uue ylesande
                err, ylesanne = self._add_task(aine_kood, data, lang)
            else:
                # uuendame tõlget
                err = self._upd_task_tran(ylesanne, aine_kood, data, lang)
                if err:
                    err = '%s %d (%s). %s' % (_("Ülesanne"), ylesanne.id, ylesanne.kood, err)
        if err:
            self.is_error = True
            err = (_("Viga real {n}").format(n=n_line + 1)) + '. ' + err
            self.error(err)
            return
            
        ylesanne.check(None)
        return ylesanne

    def _get_task(self, aine_kood, y_kood, lang):
        ylesanne = None
        if y_kood:
            # leiame sama ylesande senised versioonid
            # kui laaditav keel on ylesande põhikeel, siis märgime vana ylesande arhiveerituks ja teeme uue
            # kui laaditav keel ei ole ylesande põhikeel, siis lisame olemasolevale ylesandele tõlke
            # kui ylesannet veel ei ole, siis loome uue ylesande ja laaditav keel saab põhikeeleks
            q = (model.Ylesanne.query
                 .filter_by(kood=y_kood)
                 .filter(model.Ylesanne.ylesandeained.any(
                     model.sa.and_(model.Ylesandeaine.aine_kood==aine_kood,
                                   model.Ylesandeaine.seq==0)))
                 .filter(model.Ylesanne.staatus!=const.Y_STAATUS_ARHIIV)
                 .order_by(model.Ylesanne.created)
                 )
            for y in q.all():
                if y.lang == lang:
                    # põhikeel - arhiveerime vana ylesande
                    y.staatus = const.Y_STAATUS_ARHIIV
                    self.arhiveeritud_id.append(y.id)
                else:
                    # tõlkekeel
                    ylesanne = y
        return ylesanne

    def _add_task(self, aine_kood, data, lang):
        err = None
        ylesanne = model.Ylesanne(nimi=data.y_nimi,
                                  kood=data.y_kood,
                                  staatus=const.Y_STAATUS_TEST,
                                  max_pallid=data.k_pallid,
                                  vastvorm_kood=const.VASTVORM_KE,
                                  hindamine_kood=const.HINDAMINE_OBJ,
                                  arvutihinnatav=True,
                                  adaptiivne=False,
                                  ptest=True,
                                  etest=True,
                                  lang=lang,
                                  kasutusmaar=0,
                                  ymardamine=False,
                                  pallemaara=False,
                                  skeeled=lang)
        ya = model.Ylesandeaine(aine_kood=aine_kood,
                                ylesanne=ylesanne,
                                seq=0)
        if data.teema_kood:
            yt = model.Ylesandeteema(teema_kood=data.teema_kood,
                                     alateema_kood=data.alateema_kood,
                                     ylesandeaine=ya)

        sp_seq = 0
        if data.img_filename:
            sp_seq += 1
            sp = model.Sisuplokk(ylesanne=ylesanne,
                                 seq=sp_seq,
                                 staatus=const.B_STAATUS_KEHTIV,
                                 naide=False,
                                 ymardamine=False,
                                 tyyp=const.BLOCK_IMAGE,
                                 nimi=None,
                                 tehn_tookask=None)
            ylesanne.sisuplokid.append(sp)
            mo = sp.give_taustobjekt()
            mo.tiitel = data.img_tiitel or None
            err = self._set_img(mo, data.img_filename, None)
            if err:
                return err, ylesanne

        sp_seq += 1
        sp = model.Sisuplokk(ylesanne=ylesanne,
                             seq=sp_seq,
                             staatus=const.B_STAATUS_KEHTIV,
                             naide=False,
                             ymardamine=False,
                             tyyp=const.INTER_CHOICE,
                             nimi=data.sp_nimi,
                             tehn_tookask=data.sp_tookask)
        ylesanne.sisuplokid.append(sp)
        sp.logging = False
        # õigete vastuste arv on max vastuste arv
        max_vastus = len(data.oige_koodid)
        # iga õige vastus annab failis antud pallid / max vastuste arv
        kv_pallid = data.k_pallid / max_vastus
        # kui on lubatud mitu vastust, siis vale vastus annab nii palju miinuspunkte,
        # et ylesande eest kokku tuleb 0
        vaikimisi_pallid = max_vastus > 1 and (0 - data.k_pallid) or 0
        
        kysimus = model.Kysimus(kood='K1',
                                seq=1,
                                segamini=False,
                                max_vastus=max_vastus,
                                sisuplokk=sp,
                                sonadearv=False,
                                pseudo=False)

        for (v_seq, v_kood, v_nimi) in data.valikud:
            v = model.Valik(seq=v_seq,
                            kood=v_kood,
                            nimi=v_nimi,
                            kysimus=kysimus)

        tulemus = model.Tulemus(kood=kysimus.kood,
                                baastyyp=const.BASETYPE_IDENTIFIER,
                                kardinaalsus=const.CARDINALITY_MULTIPLE,
                                min_pallid=0,
                                max_pallid=data.k_pallid,
                                vaikimisi_pallid=vaikimisi_pallid,
                                ylesanne=ylesanne,
                                arvutihinnatav=True)
        kysimus.tulemus = tulemus
        for kood in data.oige_koodid:
            hm = model.Hindamismaatriks(kood1=kood,
                                        oige=True,
                                        pallid=kv_pallid,
                                        maatriks=1,
                                        tulemus=tulemus)
        return None, ylesanne

    def _upd_task_tran(self, ylesanne, aine_kood, data, lang):
        "Uuendame olemasoleva ylesande tõlget"
        err = None

        if not ylesanne.has_lang(lang):
            ylesanne.skeeled = ylesanne.skeeled + ' ' + lang
            
        if ylesanne.max_pallid != data.k_pallid:
            err = 'Pallid erinevad (ülesanne %d põhikeeles %s, failis %s)' % (ylesanne.id, fstr(ylesanne.max_pallid), fstr(data.k_pallid))
            return err
        
        if data.teema_kood:
            found = False
            for ya in ylesanne.ylesandeained:
                if ya.aine_kood == aine_kood:
                    for r in ya.ylesandeteemad:
                        if r.teema_kood == data.teema_kood and (not data.alateema_kood or r.alateema_kood == data.alateema_kood):
                            found = True
            if not found:
                err = 'Teema või alateema erineb (ülesanne %d)' % (ylesanne.id) 
                return err

        sp = self._get_sisuplokk(ylesanne, const.BLOCK_IMAGE)
        if data.img_filename:
            if not sp:
                err = 'Ülesandel pole pildi sisuplokki'
                return err
            mo = sp.taustobjekt
            if not mo:
                err = 'Pildi sisuplokis pole pilti'
                return err
            mo_tran = mo.give_tran(lang)
            mo_tran.tiitel = data.img_tiitel or None
            err = self._set_img(mo, data.img_filename, lang)
            if err:
                return err
        elif sp:
            # eemaldame pildi tõlke
            mo = sp.taustobjekt
            mo_tran = mo and mo.tran(lang, False)
            if mo_tran:
                mo_tran.delete()

        sp = self._get_sisuplokk(ylesanne, const.INTER_CHOICE)
        if not sp:
            err = 'Ülesandel pole valiku sisuplokki'
            return err

        sp_tran = sp.give_tran(lang)
        sp_tran.nimi = data.sp_nimi
        sp_tran.tehn_tookask = data.sp_tookask

        kysimus = None
        for k in sp.kysimused:
            kysimus = k
            break

        if not kysimus:
            err = 'Ülesande sisuplokis puudub küsimus'
            return err

        k_valikud = list(kysimus.valikud)
        if len(k_valikud) != len(data.valikud):
            err = 'Valikute arv erineb (ülesanne %d põhikeeles %d, failis %d)' % (ylesanne.id, len(k_valikud), len(data.valikud))
            return err
        
        for ind, (v_seq, v_kood, v_nimi) in enumerate(data.valikud):
            k_valikud[ind].give_tran(lang).nimi = v_nimi

    def _get_sisuplokk(self, ylesanne, sp_tyyp):
        for r in ylesanne.sisuplokid:
            if r.tyyp == sp_tyyp:
                return r
    
    def _set_teemad(self, aine_kood):
        "Loeme antud aine valdkonnad ja teemad puhvrisse"
        self._valdkonnad = []
        q = model.Klrida.get_q_by_kood('TEEMA', ylem_kood=aine_kood)
        for r in q.all():
            teema_id = r[0]
            teema_kood = r[1]
            teema_nimi = r[2]
            teemad = []
            qt = model.Klrida.get_q_by_kood('ALATEEMA', ylem_id=teema_id)
            for rt in qt.all():
                alateema_kood = rt[1]
                alateema_nimi = rt[2]
                teemad.append((alateema_kood, alateema_nimi))
            self._valdkonnad.append((teema_kood, teema_nimi, teemad))
            
    def _get_teema(self, aine_kood, valdkond, teema):
        "Leiame valdkonna ja teema koodi"
        teema_kood = alateema_kood = None
        if valdkond:
            for r in self._valdkonnad:
                v_kood, v_nimi, v_teemad = r
                if v_kood == valdkond or v_nimi == valdkond:
                    teema_kood = v_kood
                    if teema:
                        for t_kood, t_nimi in v_teemad:
                            if t_kood == teema or t_nimi == teema:
                                alateema_kood = t_kood
                                break
                        assert alateema_kood, "Tundmatu alateema %s (teema %s)" % (teema, teema_kood)
                    break
            assert teema_kood, "Tundmatu teema %s" % valdkond
        return teema_kood, alateema_kood

    def _get_imgfile(self, fn):
        "Leitakse failinime järgi pildifaili sisu"
        return self._imgfiles.get(fn)

    def _set_img(self, mo, fn, lang):
        "Seatakse taustaobjekti andmed"
        err = None
        filedata = None
        fp = None
        if self._imgobjs:
            fstorage = self._imgobjs.get(fn)
            if fstorage != None:
                filedata = fstorage.value
                fp = fstorage.file
        elif self._imgdir:
            path = '%s/%s' % (self._imgdir, fn)
            f = open(path, 'rb')
            filedata = f.read()
            f.close()

        if not filedata:
            err = '%s: %s' % (_("Faili ei leitud"), fn)
            return err

        if lang:
            mo_tran = mo.give_tran(lang)
        else:
            mo_tran = mo
        mo_tran.filename = fn
        mo_tran.filedata = filedata
        mo_tran.pikkus = mo_tran.laius = None
        try:
            if fp:
                mo.set_image_size(None, fp, fn, lang)
            else:
                mo.set_image_size(filedata, None, fn, lang)
        except IOError as e:
            err = '%s: %s' % (_("Pole pildifail"), fn)
        return err

def _split2(line):
    """Tekstist luuakse jada. Eraldajaks on semikoolon.
    Semikoolonit sisaldav väärtus on ümbritsetud jutumärkidega.
    Jutumärkidega ümbritsevas väärtuses olev jutumärk on kahekordselt.
    """
    li = []
    word = ''
    in_quot = after_quot = False
    for ch in line:
        if word == '' and ch == '"':
            in_quot = True
            after_quot = False
        elif in_quot and ch == '"':
            in_quot = False
            after_quot = True
        elif after_quot and ch == '"':
            in_quot = True
            after_quot = False
            word += ch
        elif in_quot:
            after_quot = False
            word += ch
        elif not in_quot and ch == ';':
            li.append(word)
            word = ''
        elif not in_quot:
            word += ch
    li.append(word)
    return li

def _getstr(cols, ind, length=None, notnull=False, islist=False):
    value = cols[ind].strip() or None
    if notnull:
        assert value, _("Veerg {n} ei tohi olla tühi").format(n=ind+1)
    if islist:
        values = value.split(',')
        return values
    if length and value:
        assert len(value) <= length, _("Veeru {n1} pikkus võib olla kuni {n2} tähte").format(n1=ind+1, n2=length)
    return value

def _getfloat(cols, ind, notnull=False):
    value = cols[ind].strip().replace(',','.') or None
    if value is not None:
        try:
            return float(value)
        except:
            assert False, _("Veerus {n} peab olema arv").format(n=ind+1)
    elif notnull:
        assert True, _("Veerg {n} ei tohi olla tühi").format(n=ind+1)        
