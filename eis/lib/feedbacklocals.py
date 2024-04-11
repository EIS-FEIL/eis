import sqlalchemy as sa
import operator
from eis.lib.base import *
from eis.lib.helpers import fstr, literal
from eis.model import Tagasisidevorm
from .feedbackdgm import FeedbackDgmBarnp
from .feedbackstat import FeedbackStat
_ = i18n._
    
def feedbacklocals_for_report(handler, liik, test, sooritaja, stat, lang):
    "Tagasisidevormides kasutatav kontekst, kus on T, TK, OPTEST"
    fl = feedbacklocals_init(handler, liik, test, sooritaja, stat, lang)
    f_locals = UtilLocals(handler, lang)._as_dict()
    f_locals['T'] = fl
    f_locals['OPTEST'] = fl.OPTEST
    f_locals['TK'] = fl.TK
    # < ja > asendamiseks HTMLis nii, et ei peaks kasutama kujule &lt; ja &gt; kodeeritavaid märke
    f_locals['operator'] = operator
    return f_locals

def feedbacklocals_for_np(handler, test, sooritaja):
    "Tagasisidetunnuste valemites kasutatav kontekst"
    # T sisu on otse saadaval ja muid teste pole
    liik = model.Tagasisidevorm.LIIK_OPILANE
    lang = sooritaja and sooritaja.lang or None
    fl = FeedbackLocals1(handler, liik, test, sooritaja, None, lang)
    f_locals = UtilLocals(handler, lang)._as_dict()

    # klassi meetodid lisatakse dicti 
    for key in dir(fl):
        if key[0] != '_' and key not in f_locals:
            f_locals[key] = fl.__getattribute__(key)
    
    # ylesannete ja kysimuste muutujad lisatakse dicti
    for key, value in fl._e_locals.items():
        if key not in f_locals:
            f_locals[key] = value
    return f_locals
    
def feedbacklocals_init(handler, liik, test, sooritaja, stat, lang):
    "Luuakse õige klassiga objekt sõltuvalt tagasisidevormi liigist"
    is_individual = model.Tagasisidevorm.is_individual(liik)
    if not is_individual:
        # grupi tagasiside funktsioonid
        cls = FeedbackLocalsN
    else:
        # individuaalse tagasiside funktsioonid
        cls = FeedbackLocals1
    return cls(handler, liik, test, sooritaja, stat, lang)

class FeedbackLocalsInternal:
    "Tagasiside tunnuste valemite abifunktsioonid"

    def __init__(self, handler, liik, test, sooritaja, stat, lang):
        self.handler = handler
        self.test_id = test.id
        self._cache = {}
        self.test_nimi = test.tran(lang).nimi
        if model.Tagasisidevorm.is_individual(liik):
            if sooritaja:
                self.sooritaja_id = sooritaja.id
                self.RESULT = sooritaja.pallid
                self.nimi = f'{sooritaja.eesnimi} {sooritaja.perenimi}'
                self.sugu = sooritaja.kasutaja.sugu
                self.sooritamiskpv = sooritaja.millal
                self.kasutaja_id = sooritaja.kasutaja_id
                tookood = None
                for tos in sooritaja.sooritused:
                    tookood = tos.tahised
                self.tookood = tookood
            else:
                self.sooritaja_id = None
                self.RESULT = None
                self.nimi = 'Eesnimi Perekonnanimi'
                self.sugu = const.SUGU_N
                self.sooritamiskpv = 'pp.kk.aaaa'
                self.kasutaja_id = 1
                self.tookood = None
                
        self.stat = stat
        self.lang = lang
        self.liik = liik
        test = model.Test.getR(test.id)
        self.task_map = self._get_task_map(test)

        # täidetakse _e_locals, _res_y, _res_k, _res_a
        self._get_kpallid(test, sooritaja)
        # ylesannete ja kysimuste muutujad lisatakse dicti
        di = dir(self)
        for key, value in self._e_locals.items():
            if key not in di:
                self.__setattr__(key, value)

        # alatestigruppide andmed 
        self._get_atgrupid(test)
                
    def _get_task_map(self, test):
        "Leiame testiylesannete tähistele vastavaid testiylesanne.id väärtused"
        q = (model.SessionR.query(model.Testiosa.seq,
                                 model.Testiylesanne.id,
                                 model.Testiylesanne.tahis,
                                 model.Testiylesanne.liik)
             .filter(model.Testiosa.test_id==self.test_id)
             .join(model.Testiosa.testiylesanded)
             )
        task_map = {}
        for osa_seq, ty_id, _ty_tahis, ty_liik in q.all():
            ty_tahis = None
            if _ty_tahis:
                ty_tahis = _ty_tahis.replace('.', '_')
            if ty_liik == const.TY_LIIK_K:
                if not ty_tahis:
                    ty_tahis = 'Q'
            if ty_tahis:
                key = 'TASK_%s' % ty_tahis
                if osa_seq > 1:
                    key = 'PART_%d.%s' % (osa_seq, key)
                task_map[key] = ty_id
        return task_map

    def _get_tykood_id(self, tykood):
        "Leiame ty ja kysimuse tähise TASK_X.Y järgi ty.id"
        try:
            kood, k_kood = tykood.rsplit('.', 1)
        except:
            return [], None
        li = []
        for key, ty_id in list(self.task_map.items()):
            if re.match('%s$' % kood, key):
                li.append(ty_id)
        return li, k_kood

    def _get_ty_id(self, tykood):
        "Leiame ty tähise TASK_X järgi ty.id"
        li = []
        for key, ty_id in list(self.task_map.items()):
            if re.match('%s$' % tykood, key):
                li.append(ty_id)
        if not li:
            log.error('Testi %s tagasiside ei leia ülesannet %s' % (self.test_id, tykood))
        return li

    def _g_kv_query(self, tykood, q, total=False):
        "Grupi statistika päringu koostamine kysimusevastuse kohta"
        # total - kas teha kogu Eesti päring või oma grupi päring
        # q on eeldatavalt päring Kysimusevastuse tabelist
        ty_id, k_kood = self._get_tykood_id(tykood)
        if ty_id:
            q = (q.join((model.Kysimus,
                         model.Kysimus.id==model.Kysimusevastus.kysimus_id))
                 .filter(model.Kysimus.kood==k_kood)
                 .join(model.Kysimusevastus.ylesandevastus)
                 .join((model.Sooritus,
                        model.Sooritus.id==model.Ylesandevastus.sooritus_id))
                 .join(model.Sooritus.sooritaja)
                 )
            if len(ty_id) == 1:
                q = q.filter(model.Ylesandevastus.testiylesanne_id==ty_id[0])
            else:
                q = q.filter(model.Ylesandevastus.testiylesanne_id.in_(ty_id))
            group_type = total and const.FBR_RIIK or const.FBR_GRUPP
            q = self.stat.g_filter(q, group_type)
            return q

    def _kv_query(self, tykood, q):
        "Kv filter õpilase oma andmete kohta otsides - õpilase tagasisides kasutamiseks"
        # q on eeldatavalt päring Kysimusevastuse tabelist
        ty_id, k_kood = self._get_tykood_id(tykood)
        q = (q.join((model.Kysimus,
                     model.Kysimus.id==model.Kysimusevastus.kysimus_id))
             .filter(model.Kysimus.kood==k_kood)
             .join(model.Kysimusevastus.ylesandevastus)
             .join((model.Sooritus,
                    model.Sooritus.id==model.Ylesandevastus.sooritus_id))
             .join(model.Sooritus.sooritaja)
             )
        if self.sooritaja_id:
            # sooritaja puudub vormi sisu salvestamise korral
            q = q.filter(model.Sooritaja.id==self.sooritaja_id)
        else:
            q = q.filter(model.Sooritaja.id==-1)
        if ty_id:
            if len(ty_id) == 1:
                q = q.filter(model.Ylesandevastus.testiylesanne_id==ty_id[0])
            else:
                q = q.filter(model.Ylesandevastus.testiylesanne_id.in_(ty_id))
        return q

    def _mcnt_query(self, tykood, q):
        "Tabamuste loenduri filter õpilase oma andmete kohta otsides - õpilase tagasisides kasutamiseks"
        # q on eeldatavalt päring tabelist Loendur
        ty_id, k_kood = self._get_tykood_id(tykood)
        q = (q.filter(model.Loendur.tahis==k_kood)
             .join(model.Loendur.ylesandevastus)
             .join((model.Sooritus,
                    model.Sooritus.id==model.Ylesandevastus.sooritus_id))
             .join(model.Sooritus.sooritaja)
             )
        if self.sooritaja_id:
            # sooritaja puudub vormi sisu salvestamise korral
            q = q.filter(model.Sooritaja.id==self.sooritaja_id)
        else:
            q = q.filter(model.Sooritaja.id==-1)
        if ty_id:
            if len(ty_id) == 1:
                q = q.filter(model.Ylesandevastus.testiylesanne_id==ty_id[0])
            else:
                q = q.filter(model.Ylesandevastus.testiylesanne_id.in_(ty_id))
        return q

    def _yv_query(self, tykood, q):
        "Ylesandevastuse filter õpilase oma andmete kohta otsides - õpilase tagasisides kasutamiseks"
        # q on eeldatavalt päring Ylesandevastuse tabelist
        ty_id = self._get_ty_id(tykood)
        q = (q.join((model.Sooritus,
                     model.Sooritus.id==model.Ylesandevastus.sooritus_id))
             .join(model.Sooritus.sooritaja)
             )
        if self.sooritaja_id:
            # sooritaja puudub vormi sisu salvestamise korral
            q = q.filter(model.Sooritaja.id==self.sooritaja_id)
        else:
            q = q.filter(model.Sooritaja.id==-1)
        if not ty_id:
            # viidatud ylesannet ei leitud, päring ei peaks andma vastust
            q = q.filter(model.Ylesandevastus.testiylesanne_id==0)
        elif len(ty_id) == 1:
            q = q.filter(model.Ylesandevastus.testiylesanne_id==ty_id[0])
        else:
            q = q.filter(model.Ylesandevastus.testiylesanne_id.in_(ty_id))
        return q

    def _g_np_query(self, kood, q, total=False):
        "Grupi statistika päringu koostamine normipunkti kohta"
        # q on eeldatavalt päring Npvastuse tabelist
        q = (q.join((model.Normipunkt, model.Npvastus.normipunkt_id==model.Normipunkt.id))
             .filter(model.Normipunkt.kood==kood)
             .join((model.Sooritus, model.Sooritus.id==model.Npvastus.sooritus_id))
             .join(model.Sooritus.sooritaja)
             )
        group_type = total and const.FBR_RIIK or const.FBR_GRUPP
        q = self.stat.g_filter(q, group_type)
        return q

    def _g_npid_query(self, np_id, q, total=False):
        "Grupi statistika päringu koostamine normipunkti kohta"
        # q on eeldatavalt päring Npvastuse tabelist
        q = (q.join((model.Normipunkt, model.Npvastus.normipunkt_id==model.Normipunkt.id))
             .filter(model.Normipunkt.id==np_id)
             .join((model.Sooritus, model.Sooritus.id==model.Npvastus.sooritus_id))
             .join(model.Sooritus.sooritaja)
             )
        group_type = total and const.FBR_RIIK or const.FBR_GRUPP        
        q = self.stat.g_filter(q, group_type)
        return q


    def _get_kpallid(self, test, sooritaja):
        # moodustatakse muutujad TASK_N (alatestide korral TASK_M_N)
        # ning PART_X.TASK_N 
        # ülesannete arvuliste vastustega
        # kasutamiseks normipunktide valemites
        # muutuja on objekt, millel on elemendid:
        # - küsimuse kood - küsimuse väärtus 

        class ResItem:
            "Ylesande/kysimuse/aspekti tulemus"
            # toorpunktid (aspekti korral kaaluga korrutatud)
            punktid = None
            # max toorpunktid            
            max_punktid = None 
            # toorpunktid jagatud max punktidega
            suhe = None
            # pallid
            pallid = None
            # max pallid
            max_pallid = None
            # null punkti põhjus
            nullipohj_kood = None

        def set_task_k_responses(yv, ty):
            # leiame iga kysimuse esimese vastuse
            if yv:
                # leiame soorituses olevad vastused
                q = (model.SessionR.query(model.Kysimus.kood,
                                         model.Kvsisu.sisu,
                                         model.Tulemus.baastyyp)
                     .join(model.Kvsisu.kysimusevastus)
                     .filter(model.Kvsisu.sisu!=None)
                     .filter(model.Kysimusevastus.ylesandevastus_id==yv.id)
                     .join((model.Kysimus,
                            model.Kysimus.id==model.Kysimusevastus.kysimus_id))
                     )
            else:
                # leiame võimalikud muutujad (avaldise sisestamise kontrolliks)
                q = (model.SessionR.query(model.Kysimus.kood,
                                         model.sa.sql.expression.literal_column("0"),
                                         model.Tulemus.baastyyp)
                     .join(model.Kysimus.sisuplokk)
                     .join((model.Valitudylesanne,
                            model.sa.and_(model.Valitudylesanne.ylesanne_id==model.Sisuplokk.ylesanne_id,
                                          model.Valitudylesanne.testiylesanne_id==ty.id)))
                     )
            q = q.join(model.Kysimus.tulemus)
            di = {}
            for k_kood, ks_sisu, baastyyp in q.all():
                if baastyyp == const.BASETYPE_INTEGER:
                    try:
                        value = int(ks_sisu)
                    except:
                        value = None
                elif baastyyp == const.BASETYPE_FLOAT:
                    try:
                        value = float(ks_sisu)
                    except:
                        value = None
                else:
                    # tekstiline väärtus
                    value = ks_sisu
                di[k_kood] = value
            return di

        def set_task_k_pallid(testiosa, ty_tahis, yv, ty, res_k):
            # leiame kysimuste pallid
            if yv:
                # leiame soorituses olevad vastused
                q = (model.SessionR.query(model.Kysimus.kood,
                                         model.Kysimusevastus.pallid,
                                         model.Kysimusevastus.toorpunktid,
                                         model.Kysimusevastus.nullipohj_kood,
                                         model.Tulemus.max_pallid,
                                         model.Tulemus.max_pallid_arv)
                     .join((model.Kysimus,
                            model.Kysimus.id==model.Kysimusevastus.kysimus_id))
                     .filter(model.Kysimusevastus.ylesandevastus_id==yv.id)
                     .outerjoin(model.Kysimus.tulemus)
                     )
            else:
                # leiame võimalikud muutujad (avaldise sisestamise kontrolliks)
                q = (model.SessionR.query(model.Kysimus.kood,
                                         model.sa.sql.expression.literal_column("0"),
                                         model.sa.sql.expression.literal_column("0"),
                                         model.sa.sql.expression.literal_column("0"),
                                         model.Tulemus.max_pallid,
                                         model.Tulemus.max_pallid_arv)
                     .join(model.Kysimus.sisuplokk)
                     .join((model.Valitudylesanne,
                            model.sa.and_(model.Valitudylesanne.ylesanne_id==model.Sisuplokk.ylesanne_id,
                                          model.Valitudylesanne.testiylesanne_id==ty.id)))
                     .outerjoin(model.Kysimus.tulemus)
                     )

            if yv and model.is_temp_id(yv.id):
                # eelvaates testi lahendamine
                li = []
                for kv in yv.kysimusevastused:
                    k = kv.kysimus
                    t = k.tulemus
                    if t:
                        r = (k.kood, kv.pallid, kv.toorpunktid, kv.nullipohj_kood, t.max_pallid, t.max_pallid_arv)
                        li.append(r)
            else:
                li = q.all()
            for k_kood, kv_pallid, kv_punktid, nullip, max_p, max_p_arv in li:
                key = 'TASK_%s.%s' % (ty_tahis, k_kood)
                if testiosa.seq > 1:
                    key = 'PART_%d.%s' % (testiosa.seq, key)
                if max_p is None:
                    max_p = max_p_arv
                res_k[key] = item = ResItem()
                item.punktid = kv_punktid or 0
                item.max_punktid = max_p
                item.nullipohj_kood = nullip
                item.pallid = kv_pallid or 0
                if max_p:
                    item.suhe = (kv_punktid or 0) / max_p
                
        def set_task_a_pallid(testiosa, ty_tahis, yv, ty, res_a):
            # leiame ylesannete hindamisaspektide pallid
            if yv:
                # leiame soorituses olevad vastused
                q = (model.SessionR.query(model.Hindamisaspekt.aspekt_kood,
                                         model.Vastusaspekt.pallid,
                                         model.Vastusaspekt.toorpunktid,
                                         model.Vastusaspekt.nullipohj_kood,
                                         model.Hindamisaspekt.max_pallid,
                                         model.Hindamisaspekt.kaal)
                     .join(model.Vastusaspekt.hindamisaspekt)
                     .filter(model.Vastusaspekt.ylesandevastus_id==yv.id)
                     )
            else:
                # leiame võimalikud muutujad (avaldise sisestamise kontrolliks)
                q = (model.SessionR.query(model.Hindamisaspekt.aspekt_kood,
                                         model.sa.sql.expression.literal_column("0"),
                                         model.sa.sql.expression.literal_column("0"),
                                         model.sa.sql.expression.literal_column("0"),
                                         model.Hindamisaspekt.max_pallid,
                                         model.Hindamisaspekt.kaal)
                     .join((model.Valitudylesanne,
                            model.sa.and_(model.Valitudylesanne.ylesanne_id==model.Hindamisaspekt.ylesanne_id,
                                          model.Valitudylesanne.testiylesanne_id==ty.id)))
                     )
            for a_kood, va_pallid, va_punktid, nullip, max_p, kaal in q.all():
                key = 'TASK_%s.%s' % (ty_tahis, a_kood)
                if testiosa.seq > 1:
                    key = 'PART_%d.%s' % (testiosa.seq, key)
                p = va_punktid or 0
                res_a[key] = item = ResItem()
                item.punktid = p
                item.max_punktid = max_p
                item.nullipohj_kood = nullip
                item.pallid = p * kaal
                item.max_pallid = max_p * kaal
                
        def set_for_task(testiosa, yv, ty, e_locals, res_y, res_k, res_a):
            ty_tahis = ty.tahis
            if not ty_tahis:
                if ty.liik == const.TY_LIIK_K:
                    ty_tahis = 'Q'
                else:
                    return
            ty_tahis = ty_tahis.replace('.', '_')

            if yv:
                # leiame aspektide pallid
                set_task_a_pallid(testiosa, ty_tahis, yv, ty, res_a)

                # leiame kysimuste pallid
                set_task_k_pallid(testiosa, ty_tahis, yv, ty, res_k)
            
                # leiame kysimuste vastused
                di = set_task_k_responses(yv, ty)
            else:
                # sooritaja pole ylesannet sooritanud
                di = {}
                
            # ylesande arvuliste kysimuste vastused
            key = f'TASK_{ty_tahis}'
            value = NewItem.create_from_dict(di)
            if testiosa.seq > 1:
                partkey = f'PART_{testiosa.seq}'
                if partkey not in e_locals:
                    e_locals[partkey] = NewItem()
                e_locals[partkey][key] = value
                itemkey = f'{partkey}.{key}'
            else:
                e_locals[key] = value
                itemkey = key
            
            # ylesande pallide arv
            key = f'PT_{ty_tahis}'
            value = yv and yv.pallid or 0
            if testiosa.seq > 1:
                partkey = f'PART_{testiosa.seq}'
                if partkey not in e_locals:
                    e_locals[partkey] = NewItem()
                e_locals[partkey][key] = value
            else:
                e_locals[key] = value

            res_y[itemkey] = item = ResItem()
            item.pallid = value
            item.max_pallid = yv and yv.max_pallid or 0

        # muutujad PT_N (alatestide korral PT_M_N) - ülesande pallid
        e_locals = {} # tagasisides kasutatavad väärtused
        res_y = {} # ylesannete tulemused
        res_k = {} # kysimuste tulemused
        res_a = {} # aspektide tulemused
        npvariables = [] # tagasisidetunnuste väärtused
        nptagasisided_id = {}
        staatused = {}
        if sooritaja:
            for ind, tos in enumerate(sooritaja.sooritused):
                testiosa = tos.testiosa
                staatused[ind+1] = tos.staatus
                # lisame PART_n ja PT_n muutujad juhuks, kui sooritaja testiosa ei teinud
                if testiosa.seq > 1:
                    partkey = 'PART_%d' % testiosa.seq
                    o_locals = e_locals[partkey] = NewItem()
                else:
                    o_locals = e_locals

                ylesandevastused = {yv.testiylesanne_id: yv for yv in tos.ylesandevastused}
                for ty in testiosa.testiylesanded:
                    ty_tahis = ty.tahis
                    if not ty_tahis:
                        if ty.liik == const.TY_LIIK_K:
                            ty_tahis = 'Q'
                    if ty_tahis:
                        ty_tahis = ty_tahis.replace('.', '_')
                        key = 'PT_%s' % ty_tahis
                        o_locals[key] = 0

                    yv = ylesandevastused.get(ty.id)
                    # lisame tegelikud muutujad
                    set_for_task(testiosa, yv, ty, e_locals, res_y, res_k, res_a)

                if sooritaja.staatus == const.S_STAATUS_TEHTUD:
                    # lisame normipunktide vastused
                    for npv in tos.npvastused:
                        np = npv.normipunkt
                        if np and np.kood:
                            value = npv.get_value()
                            e_locals[np.kood] = value
                            npvariables.append((np.kood, value))
                            if npv.nptagasiside_id:
                                nptagasisided_id[np.kood] = npv.nptagasiside_id
        else:
            # eelvaade
            for testiosa in test.testiosad:
                for ty in testiosa.testiylesanded:
                    set_for_task(testiosa, None, ty, e_locals, res_y, res_k, res_a)

                for np in testiosa.normipunktid:
                    if np.kood:
                        value = None
                        e_locals[np.kood] = value
                        npvariables.append((np.kood, value)) 

        # jätame meelde muudes funktsioonides kasutamiseks            
        self._e_locals = e_locals
        self._res_y = res_y
        self._res_k = res_k
        self._res_a = res_a
        self._npvariables = npvariables
        self._nptagasisided_id = nptagasisided_id
        self._staatused = staatused
        
    def _get_htunnused(self):
        htunnused = self._cache.get('htunnused')
        if htunnused is None:
            aine_kood, testiklass = (model.SessionR.query(model.Test.aine_kood,
                                                         model.Test.testiklass_kood)
                                     .filter_by(id=self.test_id)
                                     .first()
                                     )
            aine = model.Klrida.get_by_kood('AINE', aine_kood)
            aine_id = aine and aine.id
            q = (model.SessionR.query(model.Klrida.kood,
                                    model.Klrida.nimi,
                                    model.Klrida.kirjeldus,
                                    model.Klrida.kirjeldus2,
                                    model.Klrida.kirjeldus3,
                                    model.Klrida.kirjeldus_t)
                .filter(model.Klrida.klassifikaator_kood==const.KL_HTUNNUS)
                .filter(model.Klrida.ylem_id==aine_id)
                .filter(model.Klrida.testiklass_kood==testiklass)
                )
            htunnused = {}
            for kood, nimi, kirjeldus, kirjeldus2, kirjeldus3, kirjeldus_t in q.all():
                htunnused[kood] = (nimi, kirjeldus, kirjeldus2, kirjeldus3, kirjeldus_t)
            self._cache['htunnused'] = htunnused
        return htunnused

    def _get_atgrupid(self, test):
        atgrupid = self._cache.get('atgrupid')
        if atgrupid is None:
            atgrupid = []
            osanp = {}
            for osa in test.testiosad:
                for grupp in osa.alatestigrupid:
                    atgrupid.append(grupp)
                for np in osa.normipunktid:
                    osanp[np.id] = np
            self._cache['atgrupid'] = atgrupid
            self._cache['osanp'] = osanp
            
class UtilLocals:
    "Funktsioonid, mis pole seotud testi või sooritaja kontekstiga"
    def __init__(self, handler, lang):
        self.handler = handler
        self.lang = lang
        
    def _as_dict(self):
        di = {}
        for key in dir(self):
            if not key.startswith('_'):
                di[key] = self.__getattribute__(key)
        return di
    
    def fstr(self, f, digits=1):
        return fstr(f, digits)

    # funktsioon teisendab arvulise taseme (0,1,2,3,4) täheks (0,A,B,C,D)
    def cltase(self, tase, tahed='0ABCDE'):
        try:
            n = int(tase)
            if 0 <= n < len(tahed):
                return tahed[n]
        except:
            pass

    # funktsioon leiab elemendile vastava järjekorranumbri jadas (algab 1-st) või 0
    def indexin(self, li, elem):
        if elem is None:
            return 0
        try:
            #log.debug('INDEXIN(%s),%s' % (li, elem))
            n = li.index(elem)
            return n+1
        except ValueError:
            return 0

    # funktsioon leiab nende jada liikmete arvu, millel on antud väärtus
    # nt:
    #   lenval([3,2,0,2]) = 3
    #   lenval([3,2,0,2],2) = 2
    def lenval(self, li, value=None):
        if value:
            f = lambda x: x==value
        else:
            f = bool
        return len(list(filter(f, li)))

    # funktsioon tagastab -1 (kui a < b) või 0 (kui a == b) või 1 (kui a > b)
    def cmp(self, a, b):
        if a is None and b is None:
            return 0
        elif a is None:
            return -1
        elif b is None:
            return 1
        else:
            return (a > b) - (a < b)
        
    # funktsioon asendab reavahetuse HTML reavahetusega
    def nl2br(self, txt):
        return literal((txt or '').replace('\n','<br/>'))

    # funktsioon teisendab arvulise taseme (0,1,2,3,4) sõnaliseks
    def sltase(self, tase):
        request = self.handler.request
        arr = ('nulltase','algtase','kesktase','kõrgtase','tipptase')
        try:
            n = int(tase)
            if 0 <= n < len(arr):
                return _(arr[n], locale=self.lang)
        except:
            pass

    # funktsioon teisendab arvulised tasemed (0,1,2,3,4) sõnaliseks
    def sltase2(self, tasemed, d_tasemed):
        # tasemed - taseme kood või jada, nt [2,3]
        # d_tasemed - võimalikud tasemed, nt:
        # {0: 'nulltase', 2: 'alg- kuni kesktase', 3: 'kõrgtase', 4: 'tipptase'}
        request = self.handler.request
        if not isinstance(tasemed, list):
            return d_tasemed.get(tasemed)
        else:
            li = [_f for _f in [d_tasemed.get(tase) for tase in tasemed] if _f]
            buf = ''
            for ind, s in enumerate(reversed(li)):
                if ind == 0:
                    buf = s
                elif ind == 1:
                    buf = s + _(' ja ', locale=self.lang) + buf
                elif ind > 1:
                    buf = s + ', ' + buf
            return buf
    # loodusteaduse taseme arvutamise funktsioon 2017
    # Ta, Tb, Tc - tasemete A, B ja C tunnuste väärtused
    # Algoritm:
    # - kui Tipp > 0,5, siis on tipptase;
    # - kui Korg+Tipp > 0,5, siis on kõrgtase;
    # - kui Kesk+Korg+Tipp > 0,5, siis on kesktase;
    # - kui Alg+Kesk+Korg+Tipp> 0,5, siis on algtase;
    # - muidu on nulltase.
    def ltase(self, Ta, Tb, Tc=0, Td=0):
        log.debug('ltase(%s, %s, %s, %s)' % (Ta,Tb,Tc,Td))
        if Td > .5:
            return 4 # tipptase D
        elif Tc + Td > .5:
            return 3 # tase C
        elif Tb + Tc + Td > .5:
            return 2 # tase B
        elif Ta + Tb + Tc + Td > .5:
            return 1 # tase A
        else:
            return 0 # tase 0

    # loodusteaduse taseme arvutamise funktsioon 2018
    # Ta, Tb, Tc, Td - tasemete Alg,Kesk,Korg,Tipp tunnuste väärtused
    # Algoritm:
    # - kui Tipp ≥ 0,5 , siis on tipptase;
    # - kui Korg ≥ 0,5 , siis on kõrgtase;
    # - kui Kesk ≥ 0,5 , siis on kesktase;
    # - kui Alg ≥ 0,5 , siis on algtase;
    # - muidu on nulltase.
    def ltase2(self, Ta, Tb, Tc=0, Td=0, Te=0):
        log.debug('ltase2(%s, %s, %s, %s, %s)' % (Ta,Tb,Tc,Td,Te))
        limit = .4999999
        if Te > limit:
            return 5 # tipptase
        elif Td > limit:
            return 4 # kõrgtase        
        elif Tc > limit:
            return 3 # kesktase
        elif Tb > limit:
            return 2 # baastase
        elif Ta > limit:
            return 1 # algtase
        else:
            return 0 # nulltase
                    
class FeedbackLocals(FeedbackLocalsInternal):    
    # Tagasisidevormides ja tagasisidetunnuste valemites kasutatavad funktsioonid

    # funktsioon, mis leiab Eesti keskmise vastuse sisu väljalt (sobib arvutatud väärtusele)
    def a_resp_avg(self, tykood):
        q = (model.SessionR.query(sa.func.avg(sa.cast(model.Kvsisu.sisu, sa.Float)))
             .join(model.Kvsisu.kysimusevastus))
        q = self._g_kv_query(tykood, q, True)
        if q:
            return q.scalar()

    # funktsioon, mis leiab Eesti min vastuse sisu väljalt (sobib arvutatud väärtusele)
    def a_resp_min(self, tykood):
        q = (model.SessionR.query(sa.func.min(sa.cast(model.Kvsisu.sisu, sa.Float)))
             .join(model.Kvsisu.kysimusevastus))
        q = self._g_kv_query(tykood, q, True)
        if q:
            return q.scalar()

    # funktsioon, mis leiab Eesti max vastuse sisu väljalt (sobib arvutatud väärtusele)
    def a_resp_max(self, tykood):
        q = (model.SessionR.query(sa.func.max(sa.cast(model.Kvsisu.sisu, sa.Float)))
             .join(model.Kvsisu.kysimusevastus))
        q = self._g_kv_query(tykood, q, True)
        if q:
            return q.scalar()

    # funktsioon, mis leiab grupi keskmise vastuse sisu väljalt (sobib arvutatud väärtusele)
    def g_resp_avg(self, tykood):
        q = (model.SessionR.query(sa.func.avg(sa.cast(model.Kvsisu.sisu, sa.Float)))
             .join(model.Kvsisu.kysimusevastus))
        q = self._g_kv_query(tykood, q)
        if q:
            return q.scalar()

    # funktsioon, mis leiab normipunkti moodi jadana
    # (jada normipunkti nendest vastustest, mida esines kõige rohkem)
    def g_np_resp_modes(self, npkood):
        q = model.SessionR.query(model.Npvastus.nvaartus,
                                 model.Npvastus.svaartus,
                                 sa.func.count())
        q = (self._g_np_query(npkood, q)
             .group_by(model.Npvastus.nvaartus,
                       model.Npvastus.svaartus)
             .order_by(sa.desc(sa.func.count()),
                       model.Npvastus.nvaartus,
                       model.Npvastus.svaartus)
                    )
        li = []
        prev_cnt = None
        for r in q.all():
            nv, sv, cnt = r
            if prev_cnt is not None and prev_cnt != cnt:
                break
            else:
                prev_cnt = cnt
                if nv is None:
                    value = sv
                else:
                    value = nv
                li.append(value)
        return li

    # funktsioon, mis leiab normipunkti moodi ühe arvuna
    def g_np_resp_mode(self, npkood):
        li = self.g_np_resp_modes(npkood)
        if li:
            return li[0]

    # funktsioon, mis leiab tunnuse koodi järgi (võib olla reg av) koodide listi
    def keys(self, kood):
        li = []
        for key, value in self._npvariables:
            if re.match('%s$' % kood, key):
                li.append(key)
        return li

    def nptunnus_desc(self, kood):
        self._get_htunnused()
        r = self._cache['htunnused'].get(kood)
        if r:
            return r[1]

    def nptunnus_desc2(self, kood):
        self._get_htunnused()            
        r = self._cache['htunnused'].get(kood)
        if r:
            return r[2]

    def nptunnus_desc3(self, kood):
        self._get_htunnused()
        r = self._cache['htunnused'].get(kood)
        if r:
            return r[3]

    def nptunnus_tasemed(self, kood):
        self._get_htunnused()
        r = self._cache['htunnused'].get(kood)
        if r:
            return r[4]

    def get_np_id(self, np_kood):
        # normipunkti id
        for np_id, np in self._cache.get('osanp').items():
            if np.kood == np_kood:
                return np_id

    def np_name(self, np_kood):
        # normipunkti nimi
        for np_id, np in self._cache.get('osanp').items():
            if np.kood == np_kood:
                return np.tran(self.lang).nimi
        
    @property
    def OPTEST(self):
        "Õpetaja test, kui jooksev test on õpilase taustaküsitlus"
        key = 'OPTEST'
        fl = self._cache.get(key)
        if not fl and self.stat:
            # self.stat puudub np valemite korral, siis pole teisi teste vaja
            tky = (model.SessionR.query(model.Taustakysitlus)
                   .filter_by(opilase_test_id=self.test_id)
                   .first())
            if tky:
                test = tky.opetaja_test
                nimekiri_id = self.stat.nimekiri_id
                sooritaja = None
                if nimekiri_id:
                    sooritaja = (model.SessionR.query(model.Sooritaja)
                                .filter_by(test_id=test.id)
                                .filter_by(nimekiri_id=nimekiri_id)
                                .first())
                else:
                    sooritaja = None

                stat = self.stat.stat_for(test.id, sooritaja)
                stat.liik = model.Tagasisidevorm.LIIK_OPETAJA
                fl = feedbacklocals_init(self.handler, stat.liik, test, sooritaja, stat, self.lang)
                self._cache[key] = fl
        return fl

    def TK(self, tk_tahis):
        "Taustaküsitluse täitjate tulemused mingil muul testil, mille ID on ette antud"
        key = f'TK_{tk_tahis}'
        fl = self._cache.get(key)
        if not fl and self.stat:
            # teise testi andmed
            def get_tk(tk_tahis):
                tk_id = test_id = error = None
                try:
                    test_id, tahis = tk_tahis.split('-')
                    test_id = int(test_id)
                except:
                    error = _("Vigane testimiskorra tähis {s}").format(s=tk_tahis)
                else:
                    tk_id = (model.SessionR.query(model.Testimiskord.id)
                        .filter_by(test_id=test_id)
                        .filter_by(tahis=tahis)
                        .scalar())
                    if not tk_id:
                        error = _("Testimiskord {s} puudub").format(s=tk_tahis)
                return tk_id, test_id, error

            tk_id, test_id, error = get_tk(tk_tahis)
            if error:
                raise Exception(error)
            if self.stat.sooritaja:
                kasutaja_id = self.stat.sooritaja.kasutaja_id
                q = (model.SessionR.query(model.Sooritaja)
                     .filter(model.Sooritaja.kasutaja_id==kasutaja_id)
                     .filter(model.Sooritaja.testimiskord_id==tk_id))
                sooritaja = q.first()
            else:
                sooritaja = None

            test = model.Test.getR(test_id)
            stat = self.stat.stat_for(test_id, sooritaja, testimiskord_id=tk_id)
            fl = feedbacklocals_init(self.handler, stat.liik, test, sooritaja, stat, self.lang)
            self._cache[key] = fl
        return fl
        
    def dgm_bar_np(self, np_kood, colorlist):
        # np_kood - tagasiside tunnuse kood, mille väärtust kuvatakse
        # colorlist - list tupledest (x, värv), kus on x on arv, millest suurema väärtuse korral kasutatakse antud värvi
        dgm = FeedbackDgmBarnp(self.handler, self)
        colornivs = [r[0] for r in colorlist]
        colors = [r[1] for r in colorlist]
        width, height = 500, 500
        fig = dgm.figure(np_kood, colors, colornivs, width, height)
        return dgm.draw_inline(fig)
        
        
class FeedbackLocals1(FeedbackLocals):
    "Individuaalse tagasisidevormi funktsioonid"

    @property
    def AJAKULU(self):
        value = self._cache.get('AJAKULU')
        if value is None:
            totaltime = 0
            if self.sooritaja_id:
                q = (model.SessionR.query(sa.func.sum(model.Sooritus.ajakulu))
                     .join(model.Sooritus.sooritaja)
                     .filter(model.Sooritaja.id==self.sooritaja_id)
                     .filter(model.Sooritaja.staatus==const.S_STAATUS_TEHTUD))
                totaltime = q.scalar() or 0
            value = int(totaltime / 60) # sekundit minutiteks
            self._cache['AJAKULU'] = value
        return value
    
    # funktsioon leiab tagasiside teksti
    def ns_txt(self, kood, seq=None):
        # kui seq on antud, siis soovitakse tagasiside ainult juhul,
        # kui sooritaja sai antud jrk nr-iga tagasiside
        ns_id = self._nptagasisided_id.get(kood)
        if ns_id:
            ns = model.Nptagasiside.getR(ns_id)
            if ns and (seq is None or ns.seq == seq):
                return literal(ns.tran(self.lang).tagasiside)

    # funktsioon leiab tagasiside teksti õpetajale
    def ns_txt_op(self, kood, seq=None):
        ns_id = self._nptagasisided_id.get(kood)
        if ns_id:
            ns = model.Nptagasiside.getR(ns_id)
            if ns and (seq is None or ns.seq == seq):
                nst = ns.tran(self.lang)
                txt = nst.op_tagasiside or nst.tagasiside
                return literal(txt)

    # funktsioon, mis leiab tunnuse koodi järgi (võib olla reg av) vastuste listi
    def np_val(self, kood):
        li = []
        for key, value in self._npvariables:
            if re.match('%s$' % kood, key):
                li.append(value)
        if not li and self.handler.c.ekk_preview_rnd:
            li = ['1']
        return li

    # funktsioon, mis leiab tunnuse koodi järgi (võib olla reg av) yhe vastuse
    def np_val1(self, kood):
        li = self.np_val(kood)
        if li:
            return li[0]

    # funktsioon, mis leiab tunnuse koodi järgi (võib olla reg av) yhe vastuse täisarvuna
    def np_val1n(self, kood):
        value = self.np_val1(kood)
        try:
            return int(value)
        except:
            if value is None and self.handler.c.ekk_preview_rnd:
                return 1

    # funktsioon, mis leiab tunnuse koodi järgi (võib olla reg av) yhe vastuse reaalarvuna
    def np_val1f(self, kood):
        value = self.np_val1(kood)
        try:
            return float(value)
        except:
            if value is None and self.handler.c.ekk_preview_rnd:
                return 1.            

    # funktsioon, mis leiab tunnuse koodi järgi (võib olla reg av) yhe vastuse protsendina vahemiku maksimumist
    # (eeldusel, et on antud tunnuse min ja max väärtused)
    def np_val1p(self, kood):
        value = self.np_val1f(kood)
        if value is not None:
            q = (model.SessionR.query(model.Normipunkt)
                 .filter(model.Normipunkt.kood==kood)
                 .join(model.Normipunkt.testiosa)
                 .filter(model.Testiosa.test_id==self.test_id))
            np = q.first()
            if np:
                min_v = np.min_vaartus or 0
                max_v = np.max_vaartus
                if max_v is not None:
                    return (value - min_v) * 100 / (max_v - min_v)


    # Ainult õpilase tagasisidevormil ja tagasiside tunnuste valemites
    # kasutatavad funktsioonid

    # funktsioon, mis leiab testiosa jrk nr järgi testiosasoorituse oleku
    def status(self, osa_seq):
        return self._staatused.get(osa_seq)

    # funktsioon, mis leiab tunnuse koodi järgi (võib olla reg av) vastuste listi
    def val(self, tykood):
        li = []
        q = (model.SessionR.query(model.Kvsisu)
             .join(model.Kvsisu.kysimusevastus))
        q = self._kv_query(tykood, q)
        if q:
            for kvs in q.all():
                li.append(kvs.kood1 or kvs.sisu)
        return li

    # funktsioon, mis leiab tunnuse koodi järgi (võib olla reg av) yhe vastuse
    def val1(self, kood):
        li = self.val(kood)
        if li:
            return li[0]

    # funktsioon, mis leiab tunnuse koodi järgi (võib olla reg av) yhe vastuse täisarvuna
    def val1n(self, kood):
        value = self.val1(kood)
        try:
            return int(value)
        except:
            return None

    # funktsioon, mis leiab tunnuse koodi järgi (võib olla reg av) yhe vastuse reaalarvuna
    def val1f(self, kood):
        value = self.val1(kood)
        try:
            return float(value)
        except:
            return None

    # funktsioon, mis leiab tabamuste loenduri koodi järgi loenduri väärtuse
    def match_count(self, tykood):
        li = []
        q = model.SessionR.query(sa.func.sum(model.Loendur.tabamuste_arv))
        q = self._mcnt_query(tykood, q)
        value = q.scalar()
        return value

    # funktsioon, mis leiab ylesande koodi (TASK_X) järgi ylesande ajakulu
    def tasktime(self, tykood):
        q = (model.SessionR.query(sa.func.sum(model.Ylesandevastus.ajakulu))
             .filter(model.Ylesandevastus.ajakulu!=None))
        q = self._yv_query(tykood, q)
        return q.scalar() or 0
    
    # funktsioon, mis leiab hindamisaspekti koodi järgi aspekti eest antud pallid (kaaluga korrutatud)
    # (aspekti kood võib olla regulaaravaldis)
    def pta(self, tykood):
        total = 0
        for key, item in self._res_a.items():
            if re.fullmatch(tykood, key):
                total += item.pallid or 0
        return total

    # funktsioon, mis leiab hindamisaspekti koodi järgi aspekti eest antud punktid (kaaluga korrutamata)
    # (aspekti kood võib olla regulaaravaldis)
    def rpta(self, tykood):
        total = 0
        for key, item in self._res_a.items():
            if re.fullmatch(tykood, key):
                total += item.punktid or 0
        return total

    # funktsioon, mis leiab kysimuse koodi järgi kysimuse eest antud pallid
    # (kysimuse kood võib olla regulaaravaldis)
    def pt(self, tykood):
        total = 0
        for key, item in self._res_k.items():
            if re.fullmatch(tykood, key):
                total += item.pallid or 0
        return total

    # funktsioon, mis leiab kysimuse koodi järgi kysimuse eest antud punktid
    # (kysimuse kood võib olla regulaaravaldis)
    def rpt(self, tykood):
        total = 0
        for key, item in self._res_k.items():
            if re.fullmatch(tykood, key):
                total += item.punktid or 0
        return total

    # funktsioon, mis leiab kysimuse koodi järgi kysimuse eest antud punktid
    # jagatud kysimuse max punktide arvuga
    # (kysimuse kood võib olla regulaaravaldis - siis jagatakse summa ka kysimuste arvuga)
    def rptmax1(self, tykood):
        total = 0
        cnt = 0
        for key, item in self._res_k.items():
            if re.fullmatch(tykood, key):
                total += item.suhe or 0
                cnt += 1
            elif re.fullmatch(r'[a-zA-Z0-9]+', tykood) and re.fullmatch(r'.*\.'+tykood, key):
                # kui parameetriks antakse ainult kysimuse kood,
                # siis otsime seda kysimust kõigist ylesannetest
                total += item.suhe or 0
                cnt += 1
        if cnt:
            total = total/cnt
        return total

    def ptmax1(self, tykood):
        # ptmax1 on eksitav nimetus, parem oleks rptmax1        
        return self.rptmax1(tykood)

    # funktsioon, mille argumentideks on ülesannete või küsimuste või aspektide koodid
    # ja mis arvutab nende ülesannete või küsimuste või aspektide tulemuste keskmise
    # (vastava ülesande või küsimuse või aspekti max punktide arvu kaaluna kasutades)
    # milles ei esinenud nulli põhjusena tehnilist viga
    # (tehnilise vea tõttu üleni hindamata jäänud ülesanded/küsimused/aspektid jäetakse arvestamata)
    def respn(self, tykoodid):
        sum_p = 0
        cnt = 0
                
        for tykood in tykoodid:
            # kas on ylesande kood?
            item = self._res_y.get(tykood)
            if item:
                is_tehn = False
                # kas ylesandes on mõne kysimuse hindamisel olnud tehniline probleem?
                for key, item_k in self._res_k.items():
                    nullip = item_k.nullipohj_kood
                    if nullip == const.NULLIPOHJ_TEHN and key.startswith(tykood + '.'):
                        is_tehn = True
                        break
                if not is_tehn:
                    # kas ylesandes on mõne aspekti hindamisel olnud tehniline probleem?
                    for key, item_a in self._res_a.items():
                        nullip = item_a.nullipohj_kood
                        if nullip == const.NULLIPOHJ_TEHN and key.startswith(tykood + '.'):
                            is_tehn = True
                            break
                if not is_tehn:
                    sum_p += item.pallid or 0
                    cnt += item.max_pallid
            else:
                # kas on kysimuse kood?
                item_k = self._res_k.get(tykood)
                if item_k:
                    nullip = item_k.nullipohj_kood
                    if nullip != const.NULLIPOHJ_TEHN:
                        sum_p += item_k.punktid or 0
                        cnt += item_k.max_punktid
                else:
                    # kas on aspekti kood?
                    item_a = self._res_a.get(tykood)
                    if item_a:
                        nullip = item_a.nullipohj_kood
                        if nullip != const.NULLIPOHJ_TEHN:
                            sum_p += item_a.pallid or 0
                            cnt += item_a.max_pallid
        log.debug(f'  respn={sum_p}*100/{cnt}')
        if cnt > 0:
            return (sum_p * 100.)/ cnt

class FeedbackLocalsN(FeedbackLocals):

    @property
    def AJAKULU(self):
        value = self._cache.get('AJAKULU')
        if value is None:
            # sooritamise keskmine ajakulu
            q2 = (model.SessionR.query(sa.func.sum(model.Sooritus.ajakulu).label('sum_ajakulu'),
                                      model.Sooritaja.id)
                  .join(model.Sooritus.sooritaja))            
            q2 = self.stat.g_filter(q2)
            q2 = q2.group_by(model.Sooritaja.id).subquery()
            q = model.SessionR.query(sa.func.avg(q2.c.sum_ajakulu))
            totaltime = q.scalar()
            if totaltime is None:
                totaltime = 0
            value = int(totaltime / 60) # sekundit minutiteks
            self._cache['AJAKULU'] = value
        return value

    # neid ei kasutata praegu individuaalsetel vormidel, aga vajadusel saaks kasutada

    # funktsioon, mis leiab grupi min vastuse sisu väljalt (sobib arvutatud väärtusele)
    def g_resp_min(self, tykood):
        q = (model.SessionR.query(sa.func.min(sa.cast(model.Kvsisu.sisu, sa.Float)))
             .join(model.Kvsisu.kysimusevastus))
        q = self._g_kv_query(tykood, q)
        if q:
            return q.scalar()

    # funktsioon, mis leiab grupi max vastuse sisu väljalt (sobib arvutatud väärtusele)
    def g_resp_max(self, tykood):
        q = (model.SessionR.query(sa.func.max(sa.cast(model.Kvsisu.sisu, sa.Float)))
             .join(model.Kvsisu.kysimusevastus))
        q = self._g_kv_query(tykood, q)
        if q:
            return q.scalar()

    # funktsioon, mis leiab küsimuse antud vastuse osakaalu protsentides kõigist vastanutest
    def g_resp_pro(self, tykood, kood1):
        q = model.SessionR.query(sa.func.count(model.Kysimusevastus.id))
        q = self._g_kv_query(tykood, q)
        if q:
            total = q.scalar()
            if total:
                cnt = q.filter(model.Kysimusevastus.kvsisud.any(model.Kvsisu.kood1==kood1)).scalar()
                return cnt * 100. / total

    # funktsioon, mis leiab küsimuse antud vastuse vastajate arvu
    def g_resp_cnt(self, tykood, kood1=None):
        q = model.SessionR.query(sa.func.count(model.Kysimusevastus.id))
        q = self._g_kv_query(tykood, q)
        if q:
            if kood1:
                q = q.filter(model.Kysimusevastus.kvsisud.any(model.Kvsisu.kood1==kood1))
            else:
                q = q.filter(model.Kysimusevastus.kvsisud.any())
            cnt = q.scalar()
            return cnt

    # funktsioon, mis leiab normipunkti antud vastuse osakaalu protsentides kõigist vastanutest
    def g_np_resp_pro(self, npkood, value):
        q = model.SessionR.query(sa.func.count(model.Npvastus.id))
        q = self._g_np_query(npkood, q)
        if q:
            total = q.scalar()
            if total:
                if isinstance(value, (int, float)):
                    q = q.filter(model.Npvastus.nvaartus==value)
                else:
                    q = q.filter(model.Npvastus.svaartus==value)
                cnt = q.scalar()
                return cnt * 100. / total
            return 0

    # funktsioon, mis leiab normipunkti keskmise väärtuse
    def g_np_resp_avg(self, npkood):
        if self.handler.c.ekk_preview_rnd:
            return 0
        q = model.SessionR.query(sa.func.avg(model.Npvastus.nvaartus))
        q = self._g_np_query(npkood, q)
        return q.scalar()

    # grupis leitakse korrelatsioon normipunkti väärtuse ja valikküsimuse vastuse vahel
    # eeldusel, et normipunkti väärtus on arvuline ja küsimuse vastus on arvuline
    def g_corr_np_k(self, np_kood, tykood):
        if self.handler.c.ekk_preview_rnd:
            return 0
        q = model.SessionR.query(sa.func.corr(model.Npvastus.nvaartus, sa.cast(model.Kvsisu.sisu, sa.Float)))
        q = self._g_kv_query(tykood, q)
        if q:
            q = q.join(model.Kysimusevastus.kvsisud)
            q = (q.join((model.Npvastus,
                         model.Npvastus.sooritus_id==model.Sooritus.id))
                 .join((model.Normipunkt,
                        model.Npvastus.normipunkt_id==model.Normipunkt.id))
                 .filter(model.Normipunkt.kood==np_kood)
                 )
            return q.scalar()

    # funktsioon, mis leiab kysimuse moodi jadana (populaarseimad vastused)
    def g_resp_modes(self, tykood):
        li = []
        q = model.SessionR.query(model.Kvsisu.kood1, sa.func.count())
        q = self._g_kv_query(tykood, q)
        if q:
            q = (q.join(model.Kysimusevastus.kvsisud)
                 .group_by(model.Kvsisu.kood1)
                 .order_by(sa.desc(sa.func.count()),
                           model.Kvsisu.kood1)
                )
            prev_cnt = None
            for r in q.all():
                value, cnt = r
                if prev_cnt is not None and prev_cnt != cnt:
                    break
                else:
                    prev_cnt = cnt
                    li.append(value)
        return li

    # funktsioon, mis leiab kysimuse vastuse moodi yhe arvuna
    def g_resp_mode(self, tykood):
        li = self.g_resp_modes(tykood)
        if li:
            return li[0]

    # ainult tagasisidevormil kasutatavad funktsioonid
    @property
    def is_total(self):
        return not self.stat.kool_koht_id  # kas on yle Eesti

    # funktsioon, mis leiab sooritajate arvu
    def g_count(self, sugu=None):
        q = model.SessionR.query(sa.func.count(model.Sooritaja.id))
        q = self.stat.g_filter(q)
        if sugu:
            q = q.join(model.Sooritaja.kasutaja).filter(model.Kasutaja.sugu==sugu)
        return q.scalar()

    # funktsioon, mis leiab keskmise testitulemuse protsentides
    def g_result_pro(self):
        if self.handler.c.ekk_preview_rnd:
            return 0
        q = (model.SessionR.query(sa.func.avg(model.Sooritaja.tulemus_protsent))
             .filter(model.Sooritaja.tulemus_protsent!=None))
        q = self.stat.g_filter(q)
        return q.scalar()

    # õpipädevustesti grupi profiililehe jaoks

    def list_atgrupid_id(self):
        # alatestigruppide loetelu
        return [grupp.id for grupp in self._cache.get('atgrupid')]

    def list_atgrupp_np_id(self, grupp_id, on_opilane=None, on_grupp=None):
        # grupi normipunktide loetelu
        q = model.SessionR.query(model.Sooritaja.lang).distinct()
        q = self.stat.g_filter(q)
        langs = [lang for lang, in q.all()]

        li = []
        for np_id, np in self._cache.get('osanp').items():
            if np.alatestigrupp_id == grupp_id:
                if on_opilane is None or on_opilane == np.on_opilane:
                    if on_grupp is None or on_grupp == np.on_grupp:
                        if not np.lang or np.lang in langs or np.lang == self.lang:
                            li.append(np.id)
        return li

    def is_npid_sryhm(self, np_id):
        # kas normipunktil on sooritusryhmad
        np = self._cache.get('osanp').get(np_id)
        if np:
            for ps in np.sooritusryhmad:
                return True
        return False

    def is_npid_sryhm_pooratud(self, np_id):
        # kas normipunktil on sooritusryhmad ja kas värvid on pööratud järjekorras
        np = self._cache.get('osanp').get(np_id)
        if np:
            for ps in np.sooritusryhmad:
                return True, np.pooratud_varv
        return False, None

    def npval_range(self):
        # leitakse sooritusryhmadeta normipunktide võimalikud väärtused,
        # et kuvada grupi profiililehe parempoolsed veerud
        q = (model.SessionR.query(model.sa.func.min(model.Normipunkt.min_vaartus),
                                 model.sa.func.max(model.Normipunkt.max_vaartus))
             .join(model.Normipunkt.testiosa)
             .filter(model.Normipunkt.on_grupp==True)
             .filter(model.Testiosa.test_id==self.test_id)
             .filter(~ model.Normipunkt.sooritusryhmad.any())
             )
        min_v, max_v = q.first()
        if min_v is not None and max_v is not None:
            return list(range(int(min_v), int(max_v)+1))
        else:
            return []

    def g_npid_sryhm_cnt(self, np_id, ps_protsent):
        # leiame sooritajate arvu antud sooritusrühmas
        # sooritajad, kes on mitmes ryhmas, liigitatakse:
        # - vaikimisi keskmisse ryhma,
        # - kui on seatud varv2_mk, siis äärmisesse rühma
        PS = model.Sooritusryhm
        PSKorge = sa.orm.aliased(model.Sooritusryhm, name='korge')
        PSKesk = sa.orm.aliased(model.Sooritusryhm, name='kesk')
        q = model.SessionR.query(sa.func.count(model.Npvastus.id))
        q = self._g_npid_query(np_id, q)
        q = (q.join((PSKesk,
                     sa.and_(PSKesk.normipunkt_id==model.Normipunkt.id,
                             PSKesk.ryhm==PS.OPIP_KESK)))
             .join((PSKorge,
                    sa.and_(PSKorge.normipunkt_id==model.Normipunkt.id,
                            PSKorge.ryhm==PS.OPIP_KORGE)))
                    )
        if ps_protsent == PS.OPIP_KORGE:
            # yletab kõrgema ryhma läve ja
            # kas kõrge lävi on suurem kui keskmise lävi
            # või on märgitud varv2_mk
            q = (q.filter(model.Npvastus.nvaartus >= PSKorge.lavi)
                 .filter(sa.or_(PSKorge.lavi > PSKesk.lavi,
                                model.Normipunkt.varv2_mk==True))
                        )
        elif ps_protsent == PS.OPIP_KESK:
            # yletab keskmise ryhma läve
            # aga ei yleta kõrgema ryhma läve juhul, kui kõrgema ryhma lävi on suurem keskmise ryhma lävest ja pole seatud varv2_mk
            # ja ei ole nii, et keskmise lävi võrdub miinimumiga on ja on seatud varv2_mk
            q = (q.filter(model.Npvastus.nvaartus >= PSKesk.lavi)
                 .filter(sa.or_(model.Npvastus.nvaartus < PSKorge.lavi,
                                sa.and_(PSKorge.lavi == PSKesk.lavi,
                                        model.Normipunkt.varv2_mk==False)))
                 .filter(~ sa.and_(model.Normipunkt.varv2_mk==True,
                                   PSKesk.lavi == model.Normipunkt.min_vaartus))
                        )
        elif ps_protsent == PS.OPIP_MADAL:
            # ei yleta keskmise ryhma läve
            # või ei yleta kõrge ryhma läve ja keskmise lävi on võrdne miinimumiga ja on seatud varv2_mk
            q = q.filter(sa.or_(model.Npvastus.nvaartus < PSKesk.lavi,
                                sa.and_(model.Npvastus.nvaartus < PSKorge.lavi,
                                        model.Normipunkt.varv2_mk==True,
                                        PSKesk.lavi == model.Normipunkt.min_vaartus)
                                        )
                                )
        else:
            # tundmatu ryhm
            return None
        return q.scalar()

    def g_npid_resp_cnt(self, np_id, value):
        # leitakse antud normipunkti vastusega sooritajate arv
        q = model.SessionR.query(sa.func.count(model.Npvastus.id))
        q = self._g_npid_query(np_id, q)
        if q:
            if isinstance(value, (int, float)):
                q = q.filter(model.Npvastus.nvaartus==value)
            else:
                q = q.filter(model.Npvastus.svaartus==value)
            cnt = q.scalar()
            return cnt

    def g_npid_ns_txt_op(self, np_id, seq):
        # leitakse tagasiside tekst õpetajale
        q = (model.SessionR.query(model.Nptagasiside)
             .filter(model.Nptagasiside.normipunkt_id==np_id)
             .filter(model.Nptagasiside.seq==seq))
        ns = q.first()
        if ns:
            nst = ns.tran(self.lang)
            txt = nst.op_tagasiside or nst.tagasiside
            return literal(txt)

    def g_npid_ns_cnt(self, np_id, seq):
        # leitakse antud tagasiside saanud sooritajate arv
        # nptagasiside outerjoin selleks, et seq=None korral leida nende arv, kellel tagasisided pole
        # (sõltuvalt tunnuse valemist võib mõnel juhul eeldada, et need on tehnilise veaga tööd)
        q = (model.SessionR.query(sa.func.count(model.Npvastus.id))
             .outerjoin((model.Nptagasiside,
                         model.Npvastus.nptagasiside_id==model.Nptagasiside.id))
             .filter(model.Nptagasiside.seq==seq))
        q = self._g_npid_query(np_id, q)
        if q:
            cnt = q.scalar()
            return cnt

    def g_np_ns_txt_op(self, np_kood, seq):
        # leitakse tagasiside tekst õpetajale
        q = (model.SessionR.query(model.Nptagasiside)
             .join(model.Nptagasiside.normipunkt)
             .filter(model.Normipunkt.kood==np_kood)
             .filter(model.Nptagasiside.seq==seq)
             .join(model.Normipunkt.testiosa)
             .filter(model.Testiosa.test_id==self.test_id))
        ns = q.first()
        if ns:
            nst = ns.tran(self.lang)
            txt = nst.op_tagasiside or nst.tagasiside
            return literal(txt)

    def g_np_ns_pro(self, np_kood, seq):
        # leitakse antud tagasiside saanud sooritajate protsent
        q = (model.SessionR.query(sa.func.count(model.Npvastus.id))
             .outerjoin((model.Nptagasiside,
                         model.Npvastus.nptagasiside_id==model.Nptagasiside.id))
             )
        q = self._g_np_query(np_kood, q)
        if q:
            total = q.scalar()
            if total:
                q = q.filter(model.Nptagasiside.seq==seq)
                cnt = q.scalar()
                return cnt * 100. / total                    
        
    def g_np_ns_cnt(self, np_kood, seq):
        # leitakse antud tagasiside saanud sooritajate arv
        q = (model.SessionR.query(sa.func.count(model.Npvastus.id))
             .outerjoin((model.Nptagasiside,
                         model.Nptagasiside.id==model.Npvastus.nptagasiside_id))
             .filter(model.Nptagasiside.seq==seq))
        q = self._g_np_query(np_kood, q)
        if q:
            cnt = q.scalar()
            return cnt

    def g_lnk_np_ns_cnt(self, np_kood, seq):
        # leitakse antud tagasiside saanud sooritajate arv ja kuvatakse lingina,
        # mis avab dialoogi, kus on sooritajate nimed
        # ja kust saab edasi liikuda töö vaatamisele (ES-3137)
        q = (model.SessionR.query(model.Sooritaja.id,
                                  model.Sooritaja.eesnimi,
                                  model.Sooritaja.perenimi,
                                  model.Npvastus.id)
             .join((model.Nptagasiside,
                    model.Npvastus.nptagasiside_id==model.Nptagasiside.id))
             .filter(model.Nptagasiside.seq==seq))
        q = self._g_np_query(np_kood, q)
        if q:
            q = q.order_by(model.Sooritaja.eesnimi, model.Sooritaja.perenimi).limit(200)
            li = []
            for j_id, eesnimi, perenimi, nv_id in q.all():
                li.append((j_id, f'{eesnimi} {perenimi}'))
            cnt = len(li)
            tk_id = self.stat.testimiskord_id
            if cnt:
                bubble_id = f'bbln_{np_kood}_{seq}'
                buf = f'<div id="{bubble_id}" style="display:none" class="mr-3">'
                for j_id, nimi in li:
                    perm = f'ts-{j_id}-{tk_id}' # vt Sooritaja.has_permission_ts
                    if not tk_id or self.handler.c.user.has_permission(perm, const.BT_SHOW, sooritaja_id=j_id):
                        buf += f'<div><a class="lnk-opilane" data-j="{j_id}">{nimi}</a></div>'
                    else:
                        buf += f'<div>{nimi}</div>'
                buf += '</div>'
                buf = self.handler.h.link_to_bubble(cnt, None, bubble_id=bubble_id, class_="p-0") + literal(buf)
                return buf
            else:
                return 0

    @property
    def sooritamiskpv(self):
        q = (model.SessionR.query(sa.func.min(model.Sooritus.algus),
                                  sa.func.max(model.Sooritus.lopp))
             .join(model.Sooritus.sooritaja))
        q = self.stat.g_filter(q)
        alates, kuni = q.first()
        if not alates or not kuni:
            millal = ''
        else:
            s_alates = alates.strftime('%d.%m.%Y')
            s_kuni = kuni.strftime('%d.%m.%Y')
            if s_alates != s_kuni:
                millal = '%s - %s' % (s_alates, s_kuni)
            else:
                millal = s_alates
        return millal

    @property
    def klass(self):
        value = self._cache.get('klass') or self.stat.klass or ''
        if not value:
            # statistika pole tehtud klassi kohta
            # leiame kõik klassid, mille õpilasi grupis esineb
            q = model.SessionR.query(model.Sooritaja.klass).distinct()
            q = self.stat.g_filter(q).order_by(model.Sooritaja.klass)
            klassid = [r for r, in q.all() if r]
            value = self._cache['klass'] = ', '.join(klassid)

    @property
    def kool(self):
        value = self._cache.get('kool_nimi') or ''
        if value:
            return value
        if self.stat.kool_koht_id:
            koht = model.Koht.getR(self.stat.kool_koht_id)
            value = koht.nimi
        else:
            # kui kool pole tingimustena antud, siis leiame muude andmete järgi
            q = model.SessionR.query(model.Sooritaja.kool_koht_id).distinct()
            q = self.stat.g_filter(q)
            if q.count() == 1:
                koht_id, = q.first()
                if koht_id:
                    koht = model.Koht.getR(koht_id)
                    value = koht.nimi

        self._cache['kool_nimi'] = value
        return value

    @property
    def nimi(self):
        value = self._cache.get('nimi') or ''
        if not value:
            value = self.kool
            klass = self.klass
            if klass == model.KlassID.KANDIDAADID:
                nimi += ' ' + _("Sisseastujad")
            elif klass:
                value += ' ' + _("{klass}.{paralleel} klass").format(klass=klass, paralleel=self.stat.paralleel or '')
            elif self.stat.klassidID:
                b = ', '.join(["%s klass" % k.name for k in self.stat.klassidID])
                value += ' ' + b
            self._cache['nimi'] = value
        return value

    @property
    def opetaja(self):
        value = None
        if self.stat.opetajad_id:
            op_nimed = [model.Kasutaja.getR(op_id).nimi for op_id in self.stat.opetajad_id]
            value = ', '.join(op_nimed)
        return value

    @property
    def nimekiri(self):
        if self.stat.nimekiri_id:
            return model.Nimekiri.getR(self.stat.nimekiri_id).nimi

    def atgrupp_nimi(self, grupp_id):
        # grupi nimi
        grupp = model.Alatestigrupp.getR(grupp_id)
        if grupp:
            return grupp.tran(self.lang).nimi or ''

    def np_nimi(self, np_id):
        # normipunkti nimi
        np = model.Normipunkt.getR(np_id)
        if np:
            return np.tran(self.lang).nimi or ''

