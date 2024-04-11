"""Statistika arvutamine
"""
import sqlalchemy as sa
from sqlalchemy.ext.compiler import compiles

from math import sqrt

from eis.lib.base import *
_ = i18n._

log = logging.getLogger(__name__)

class ResultStat(object):
    """Vastuste ja tulemuste statistika arvutamine
    """
    def __init__(self, handler, protsess, tkorraga, spec=None):
        self.handler = handler
        self.request = handler.request
        self.protsess = protsess
        self.protsess_id = protsess and protsess.id or None
        self.error = None
        self.tkorraga = tkorraga

        # kas arvutada kõik hindamiskogumid?
        self.spec = spec

    def _query_specify(self, q, has_ty, lotv):
        "Päringu tingimustesse lisatakse hindamiskogumid või testiylesanded"
        # päring peab sisaldama Valitudylesanne
        # has_ty - kas Testiylesanne on juba päringus 
        spec = self.spec
        if spec and not spec.koik_kogumid:
            if spec.tyy_id:
                q = q.filter(model.Valitudylesanne.testiylesanne_id.in_(spec.tyy_id))
            elif spec.kogumid_id:
                if lotv:
                    q = q.filter(model.Valitudylesanne.hindamiskogum_id.in_(spec.kogumid_id))
                else:
                    if not has_ty:
                        q = q.join(model.Valitudylesanne.testiylesanne)
                    q = q.filter(model.Testiylesanne.hindamiskogum_id.in_(spec.kogumid_id))
        return q
        
    def calc_y(self, test, testimiskord):
        """Ülesannete statistika arvutamine.
        """
        def _calc_filter(q, testiosa_id, toimumisaeg_id, testikoht_id, kool_koht_id):
            q = (q.join((model.Valitudylesanne,
                         model.Valitudylesanne.id==model.Ylesandevastus.valitudylesanne_id))
                 .filter(model.Valitudylesanne.ylesanne_id!=None)
                 .join((model.Sooritus,
                        model.Sooritus.id==model.Ylesandevastus.sooritus_id))
                 .join(model.Sooritus.sooritaja)
                 )
            if test.on_jagatudtoo:
                q = q.filter(model.Ylesandevastus.kehtiv==True)
            else:
                q = q.filter(model.Sooritus.staatus==const.S_STAATUS_TEHTUD)
            if toimumisaeg_id:
                q = q.filter(model.Sooritus.toimumisaeg_id==toimumisaeg_id)
            else:
                q = q.filter(model.Sooritus.testiosa_id==testiosa_id)
                if self.tkorraga:
                    # ekk vaate statistika kogu testimiskordade kohta kogu testi kaupa
                    q = (q.join(model.Sooritaja.testimiskord)
                         .filter(model.Testimiskord.analyys_eraldi==False))
                elif test.testiliik_kood != const.TESTILIIK_DIAG2:
                    # avaliku vaate statistika ainult testimiskorrata testide kohta
                    q = q.filter(model.Sooritus.toimumisaeg_id==None)
            if testikoht_id:
                q = q.filter(model.Sooritus.testikoht_id==testikoht_id)
            elif kool_koht_id:
                q = q.filter(model.Sooritaja.kool_koht_id==kool_koht_id)

            lotv = model.Session.query(model.Testiosa.lotv).filter_by(id=testiosa_id).scalar()
            q = self._query_specify(q, False, lotv)
            return q
        
        def _calc(testiosa_id, toimumisaeg_id, progress_step, testikoht_id, kool_koht_id, komplektis):
            if self.protsess:
                progress_start = self.protsess.edenemisprotsent
                progress_end = progress_start + progress_step

            selects = [sa.func.avg(model.Ylesandevastus.toorpunktid),
                       sa.func.count(model.Ylesandevastus.toorpunktid),
                       sa.func.avg(model.Ylesandevastus.ajakulu),
                       sa.func.min(model.Ylesandevastus.ajakulu),
                       sa.func.max(model.Ylesandevastus.ajakulu),
                       sa.func.corr(model.Ylesandevastus.pallid, model.Sooritaja.pallid),
                       sa.func.corr(model.Ylesandevastus.pallid, model.Sooritaja.pallid - model.Ylesandevastus.pallid),
                       model.Valitudylesanne.ylesanne_id,
                       ]
            if komplektis:
                # statistika komplekti piires
                selects.append(model.Ylesandevastus.valitudylesanne_id)
            q = model.Session.query(*selects)
            q = _calc_filter(q, testiosa_id, toimumisaeg_id, testikoht_id, kool_koht_id)
            #if valimis is not None:
            #    q = q.filter(model.Sooritaja.valimis==valimis)
            if komplektis:
                q = q.group_by(model.Valitudylesanne.ylesanne_id,
                               model.Ylesandevastus.valitudylesanne_id)
            else:
                q = q.group_by(model.Valitudylesanne.ylesanne_id)

            if self.protsess:
                self._save_protsess(progress_start)
            n_total = q.count()
            n_rcd = 0
            calc_vy_id = [] # ylesanded, mille statistika on arvutatud
            for rcd in q.all():
                n_rcd += 1
                if komplektis:
                    keskmine, cnt, aeg_avg, aeg_min, aeg_max, rit, rir, y_id, vy_id = rcd
                    calc_vy_id.append(vy_id)
                else:
                    keskmine, cnt, aeg_avg, aeg_min, aeg_max, rit, rir, y_id = rcd
                    vy_id = None
                    calc_vy_id.append(y_id)
                    
                ylesanne = model.Ylesanne.get(y_id)
                item = model.Ylesandestatistika.give_by_keys(vy_id, y_id, self.tkorraga, toimumisaeg_id, None, testikoht_id, kool_koht_id)
                item.keskmine = keskmine
                item.sooritajate_arv = cnt
                item.aeg_avg = aeg_avg
                item.aeg_min = aeg_min
                item.aeg_max = aeg_max
                item.rit = rit
                item.rir = rir
                max_punktid = ylesanne.max_pallid
                if max_punktid and keskmine is not None:
                    item.lahendatavus = keskmine / max_punktid * 100
                else:
                    item.lahendatavus = None
                if self.protsess:
                    self._save_protsess(progress_start + (progress_end - progress_start) * n_rcd / n_total)

            # leiame kõik selle testiosa valitudylesanded,
            # mille statistikat me praegu ei arvutanud
            if komplektis:
                qd = model.Session.query(model.Valitudylesanne.id)
            else:
                qd = model.Session.query(model.Valitudylesanne.ylesanne_id).distinct()
            qd = (qd.join(model.Valitudylesanne.testiylesanne)
                  .filter(model.Testiylesanne.testiosa_id==testiosa_id)
                  )
            lotv = model.Session.query(model.Testiosa.lotv).filter_by(id=testiosa_id).scalar()            
            qd = self._query_specify(qd, True, lotv)
            if calc_vy_id:
                if komplektis:
                    qd = qd.filter(~ model.Valitudylesanne.id.in_(calc_vy_id))
                else:
                    qd = qd.filter(~ model.Valitudylesanne.ylesanne_id.in_(calc_vy_id))
            for vy_id, in qd.all():
                if komplektis:
                    item = model.Ylesandestatistika.get_by_keys(vy_id, None, self.tkorraga, toimumisaeg_id, None, testikoht_id, kool_koht_id)
                else:
                    y_id = vy_id
                    item = model.Ylesandestatistika.get_by_keys(None, y_id, self.tkorraga, toimumisaeg_id, None, testikoht_id, kool_koht_id)
                if item:
                    item.delete()

        progress_end = 2.
        progress_step = progress_end / len(test.testiosad) / 2
            
        if testimiskord:
            # ekk testi statistika
            # kokku, mitte-valim ja valim eraldi arvutada (ES-2545)
            for ta in testimiskord.toimumisajad:
                # ylesannete statistika kogu toimumisaja kohta
                _calc(ta.testiosa_id, ta.id, progress_step, None, None, True)
                _calc(ta.testiosa_id, ta.id, progress_step, None, None, False)
        else:
            # avaliku vaate testi statistika või ekk testi statistika testi kaupa
            for testiosa in test.testiosad:
                _calc(testiosa.id, None, progress_step, None, None, True)
                _calc(testiosa.id, None, progress_step, None, None, False)
                
        model.Session.commit()

    def calc_test_y(self, test):
        return self.calc_testiruum_y(None, test)

    def calc_testiruum_y(self, testiruum, test):
        """Ülesannete statistika arvutamine avaliku vaate nimekirja kohta.
        """
        q = (model.Session.query(sa.func.avg(model.Ylesandevastus.toorpunktid),
                                 sa.func.count(model.Ylesandevastus.toorpunktid),
                                 sa.func.avg(model.Ylesandevastus.ajakulu),
                                 sa.func.min(model.Ylesandevastus.ajakulu),
                                 sa.func.max(model.Ylesandevastus.ajakulu),
                                 sa.func.corr(model.Ylesandevastus.pallid, model.Sooritaja.pallid),
                                 sa.func.corr(model.Ylesandevastus.pallid,
                                              model.Sooritaja.pallid - model.Ylesandevastus.pallid),
                                 model.Ylesandevastus.valitudylesanne_id,
                                 model.Valitudylesanne.ylesanne_id)
             .join((model.Sooritus,
                    model.Sooritus.id==model.Ylesandevastus.sooritus_id))
             .join((model.Valitudylesanne,
                    model.Valitudylesanne.id==model.Ylesandevastus.valitudylesanne_id))
             .filter(model.Valitudylesanne.ylesanne_id!=None)
             .join(model.Sooritus.sooritaja))
        if test.on_jagatudtoo:
            q = q.filter(model.Ylesandevastus.kehtiv==True)
        else:
            q = q.filter(model.Sooritus.staatus==const.S_STAATUS_TEHTUD)
        if testiruum:
            q = q.filter(model.Sooritus.testiruum_id==testiruum.id)
        else:
            q = (q.filter(model.Sooritaja.test_id==test.id)
                 .filter(model.Sooritus.toimumisaeg_id==None))
        q = q.group_by(model.Ylesandevastus.valitudylesanne_id,
                       model.Valitudylesanne.ylesanne_id)

        for rcd in q.all():
            # iga ylesande kohta tekib Ylesandestatistika kirje
            keskmine, cnt, aeg_avg, aeg_min, aeg_max, rit, rir, vy_id, y_id = rcd
            testiruum_id = testiruum and testiruum.id or None
            item = model.Ylesandestatistika.give_by_keys(vy_id, y_id, self.tkorraga, None, testiruum_id)
            item.keskmine = keskmine
            item.sooritajate_arv = cnt
            item.aeg_avg = aeg_avg
            item.aeg_min = aeg_min
            item.aeg_max = aeg_max
            item.rit = rit
            item.rir = rir
            vy = model.Valitudylesanne.get(vy_id)
            ylesanne = vy.ylesanne
            if ylesanne and ylesanne.max_pallid and keskmine is not None:
                item.lahendatavus = keskmine / ylesanne.max_pallid * 100
            else:
                item.lahendatavus = None
        model.Session.commit()

    def calc_testikoht_y(self, toimumisaeg_id, testikoht_id=None, kool_koht_id=None):
        """Ülesannete statistika arvutamine soorituskohtade või koolide kaupa.
        """
        # jagatud tööde korral siia ei tulda
        # hakkame uut statistikat arvutama
        q = (model.Session.query(sa.func.avg(model.Ylesandevastus.toorpunktid),
                                 sa.func.count(model.Ylesandevastus.toorpunktid),
                                 sa.func.corr(model.Ylesandevastus.pallid, model.Sooritaja.pallid),
                                 sa.func.corr(model.Ylesandevastus.pallid, model.Sooritaja.pallid - model.Ylesandevastus.pallid),
                                 model.Ylesandevastus.valitudylesanne_id,
                                 model.Valitudylesanne.ylesanne_id)
             .join((model.Sooritus,
                    model.Sooritus.id==model.Ylesandevastus.sooritus_id))
             .filter(model.Sooritus.staatus==const.S_STAATUS_TEHTUD)
             .filter(model.Sooritus.toimumisaeg_id==toimumisaeg_id)
             .join((model.Valitudylesanne,
                    model.Valitudylesanne.id==model.Ylesandevastus.valitudylesanne_id))
             .join(model.Sooritus.sooritaja)
             .filter(model.Valitudylesanne.ylesanne_id!=None)
             )
        if testikoht_id:
            q = q.filter(model.Sooritus.testikoht_id==testikoht_id)
        elif kool_koht_id:
            q= q.filter(model.Sooritaja.kool_koht_id==kool_koht_id)

        q = q.group_by(model.Ylesandevastus.valitudylesanne_id,
                       model.Valitudylesanne.ylesanne_id)
        #model.log_query(q)
        for rcd in q.all():
            keskmine, cnt, rit, rir, vy_id, y_id = rcd
            item = model.Ylesandestatistika.give_by_keys(vy_id, y_id, self.tkorraga, toimumisaeg_id, None, testikoht_id, kool_koht_id)
            item.keskmine = keskmine
            item.sooritajate_arv = cnt
            item.rit = rit
            item.rir = rir

            vy = model.Valitudylesanne.get(vy_id)
            ylesanne = vy.ylesanne
            if ylesanne and ylesanne.max_pallid and keskmine is not None:
                item.lahendatavus = keskmine / ylesanne.max_pallid * 100
            else:
                item.lahendatavus = None
        model.Session.commit()

    def calc_kysimused_data(self, test, testimiskord):
        """Küsimuste loetelu kogumine, mida kasutatakse küsimuste statistika arvutamisel
        """
        # arvutatame protsessi edenemise kuvamise tarvis, mitu küsimust on kokku
        data = []
        for testiosa in test.testiosad:
            q = (model.Session.query(model.Sisuplokk.ylesanne_id,
                                     model.Komplektivalik.kursus_kood,
                                     model.Kysimus.id,
                                     model.Valitudylesanne.id,
                                     model.Valitudylesanne.komplekt_id)
                 .join(model.Sisuplokk.kysimused)
                 .join((model.Valitudylesanne,
                        model.Valitudylesanne.ylesanne_id==model.Sisuplokk.ylesanne_id))
                 .join(model.Valitudylesanne.komplekt)
                 .join(model.Komplekt.komplektivalik)
                 .filter(model.Komplektivalik.testiosa_id==testiosa.id)
                 .filter(model.Valitudylesanne.test_id==test.id)
                 .filter(~ model.Sisuplokk.tyyp.in_(const.interaction_block))
                 )
            if testimiskord:
                # ekk testi statistika ainult testimiskorral kasutatud komplektide kohta
                q1 = (model.Session.query(model.Toimumisaeg.id)
                      .filter_by(testiosa_id=testiosa.id)
                      .filter_by(testimiskord_id=testimiskord.id))
                ta_id, = q1.first()
                q = q.join((model.Toimumisaeg_komplekt,
                            sa.and_(model.Toimumisaeg_komplekt.komplekt_id==model.Valitudylesanne.komplekt_id,
                                    model.Toimumisaeg_komplekt.toimumisaeg_id==ta_id)))
            else:
                ta_id = None
                
            q = self._query_specify(q, False, testiosa.lotv)
            for ylesanne_id, kursus, kysimus_id, vy_id, komplekt_id in q.all():
                # komplektisisene statistika
                data.append((ta_id, ylesanne_id, kursus, vy_id, kysimus_id))
                # komplektiylene statistika, vy_id=None
                row = (ta_id, ylesanne_id, kursus, None, kysimus_id)
                if row not in data:
                    data.append(row)

        return data
    
    def calc_kysimused(self, test, testimiskord, progress_end=99, nimekiri_id=None):
        """Küsimuste statistika arvutamine"""
        if self.protsess:
            progress_start = self.protsess.edenemisprotsent
        # leitakse kysimused
        data = self.calc_kysimused_data(test, testimiskord)
        total = len(data)
        # arvutame
        cnt = 0 # juba arvutatud küsimuste koguarv
        for ta_id, ylesanne_id, kursus, vy_id, kysimus_id in data:
            ta = ta_id and model.Toimumisaeg.get(ta_id) or None
            ylesanne = model.Ylesanne.get(ylesanne_id)
            kysimus = model.Kysimus.get(kysimus_id)
            log.debug('Ül %d kysimuse %s %d statistika %s (%d/%d)...' % \
                      (ylesanne_id, kysimus.kood, kysimus.id, vy_id and '(vy %s)' % vy_id or '(komplektita)', cnt+1, total))
            # küsimuse statistika arvutamine:
            # iga kysimuse kohta tekib Kysimusestatistika kirje
            # kysimuse iga tulemuse kohta tekib eraldi Khstatistika kirje
            # kysimuse iga vastuse kohta tekib eraldi Kvstatistika kirje
            self.calc_kysimus(kysimus, test, testimiskord, ta, kursus, nimekiri_id, vy_id)
            cnt += 1
            if self.protsess:
                self._save_protsess(progress_start + (progress_end - progress_start) * cnt / total)
        model.Session.flush()
        
    def _save_protsess(self, protsent):
        if self.protsess.lopp:
            raise ProcessCanceled()
        self.protsess.edenemisprotsent = max(1, protsent)
        model.Session.commit()

    def calc_kysimus(self, kysimus, test, testimiskord, ta, kursus, nimekiri_id, vy_id):
        if ta:
            kysimusestatistika = ta.give_kysimusestatistika(kysimus.id, vy_id)
            self.calc_kstat(test, testimiskord, kysimus, kysimusestatistika)
        else:
            for testiosa in test.testiosad:
                kysimusestatistika = testiosa.give_kysimusestatistika(kysimus.id, vy_id, self.tkorraga, nimekiri_id)
                self.calc_kstat(test, testimiskord, kysimus, kysimusestatistika)

    def calc_kstat(self, test, testimiskord, kysimus, kysimusestatistika):
        """Küsimuse statistika arvutamine, sh sooritajate arv ja eristusjõud (Rit, Rir)
        """
        kysimusestatistika.modified = datetime.now()
        nimekiri_id = kysimusestatistika.nimekiri_id
        vy_id = kysimusestatistika.valitudylesanne_id

        def _filter(q, kysimus_id, test_id, testimiskord_id, join_kv=True, hinnatud=True):
            q1 = (q.filter(model.Kysimusevastus.kysimus_id==kysimus_id)
                  .filter(model.Kysimusevastus.sisestus==1)
                  .join(model.Kysimusevastus.ylesandevastus)
                  .join((model.Sooritus,
                         model.Sooritus.id==model.Ylesandevastus.sooritus_id))
                  .join(model.Sooritus.sooritaja)
                  )
            if test.on_jagatudtoo:
                q1 = q1.filter(model.Ylesandevastus.kehtiv==True)
            else:
                q1 = q1.filter(model.Sooritaja.staatus==const.S_STAATUS_TEHTUD)
            if hinnatud:
                q1 = q1.filter(model.Sooritaja.hindamine_staatus==const.H_STAATUS_HINNATUD)
            if join_kv:
                q1 = (q1.join(model.Kysimusevastus.kvsisud)
                      .filter(model.Kvsisu.analyysitav==True))
            if vy_id:
                q1 = q1.filter(model.Ylesandevastus.valitudylesanne_id==vy_id)
            if nimekiri_id:
                q1 = q1.filter(model.Sooritaja.nimekiri_id==nimekiri_id)
            elif testimiskord_id:
                q1 = q1.filter(model.Sooritaja.testimiskord_id==testimiskord_id)
            else:
                q1 = q1.filter(model.Sooritaja.test_id==test_id)
                if self.tkorraga:
                    q1 = (q1.join(model.Sooritaja.testimiskord)
                          .filter(model.Testimiskord.analyys_eraldi==False))
                elif test.testiliik_kood != const.TESTILIIK_DIAG2:
                    q1 = q1.filter(model.Sooritaja.testimiskord_id==None)
            return q1

        testimiskord_id = testimiskord and testimiskord.id or None

        # arvutame punktide statistika
        q = model.Session.query(model.Kysimusevastus.toorpunktid,
                                model.Kysimusevastus.pallid,
                                model.Kysimusevastus.nullipohj_kood,
                                sa.func.count(model.Kysimusevastus.id))
        q = _filter(q, kysimus.id, test.id, testimiskord_id, join_kv=False, hinnatud=False).\
            group_by(model.Kysimusevastus.toorpunktid,
                     model.Kysimusevastus.pallid,
                     model.Kysimusevastus.nullipohj_kood)
        self._insert_khstatistika(kysimusestatistika, q, test.id, testimiskord_id)

        q = model.Session.query(sa.func.count(model.Kysimusevastus.id))
        q = _filter(q, kysimus.id, test.id, testimiskord_id, join_kv=False, hinnatud=False)
        kysimusestatistika.vastajate_arv = q.scalar()
        
        q = model.Session.query(sa.func.count(model.Kysimusevastus.id))
        q = _filter(q, kysimus.id, test.id, testimiskord_id, join_kv=False, hinnatud=True)
        kysimusestatistika.test_hinnatud_arv = q.scalar()        

        tulemus = kysimus.tulemus
        if kysimus.rtf and tulemus and not tulemus.tyhikud:
            sisu_field = sa.func.html_resp(model.Kvsisu.sisu)
        else:
            sisu_field = model.Kvsisu.sisu

        # arvutame vastuste statistika
        q = model.Session.query(sisu_field,
                                model.Kvsisu.kood1,
                                model.Kvsisu.kood2,
                                model.Kvsisu.oige,
                                model.Kvsisu.tyyp,
                                model.Kvsisu.maatriks,
                                model.Kvsisu.hindamismaatriks_id,
                                sa.func.count(model.Kvsisu.id))
        q = _filter(q, kysimus.id, test.id, testimiskord_id, hinnatud=False).\
            group_by(sisu_field,
                     model.Kvsisu.kood1,
                     model.Kvsisu.kood2,
                     model.Kvsisu.oige,
                     model.Kvsisu.tyyp,
                     model.Kvsisu.maatriks,
                     model.Kvsisu.hindamismaatriks_id)   
        self._insert_kvstatistika(kysimusestatistika, q, test.id, testimiskord_id)
        
        q = model.Session.query(model.Kysimusevastus.id)
        q = _filter(q, kysimus.id, test.id, testimiskord_id, hinnatud=False)

        cnt_total = q.count() # vastuste koguarv, sh ka hindamata tööde vastused
        tracelist = []
        tracelist.append(('vastuste koguarv', cnt_total, q))
        
        if kysimus.max_vastus:
            # arvestame ka andmata vastuseid
            vastuste_arv = kysimusestatistika.vastajate_arv * kysimus.max_vastus
            vastamata_arv = vastuste_arv - cnt_total
            cnt_total = vastuste_arv
            tracelist.append(('arvestades andmata vastuseid', cnt_total, 'vastajate arv %d * ühe vastaja max vastuste arv %d' % (kysimusestatistika.vastajate_arv, kysimus.max_vastus)))
            
            # lisame vastamata vastuste arvu
            if vastamata_arv > 0:
                kvst = (model.Kvstatistika.query
                        .filter(model.Kvstatistika.kysimusestatistika_id==kysimusestatistika.id)
                        .filter(model.Kvstatistika.oige==const.C_VASTAMATA)
                        .first())
                if kvst:
                    kvst.vastuste_arv += vastamata_arv
                else:
                    model.Kvstatistika(kysimusestatistika=kysimusestatistika,
                                       oige=const.C_VASTAMATA,
                                       vastuste_arv=vastamata_arv)

        kysimusestatistika.vastuste_arv = cnt_total

        # keskmine lahendusprotsent
        klahp = None
        if tulemus:
            max_p = tulemus.get_max_pallid()
            if max_p:
                q = model.Session.query(sa.func.avg(model.Kysimusevastus.toorpunktid))
                q = _filter(q, kysimus.id, test.id, testimiskord_id, join_kv=False, hinnatud=False)
                q = q.filter(model.Kysimusevastus.toorpunktid != None)
                avg_p = q.scalar()
                if avg_p is not None:
                    klahp = avg_p * 100 / max_p
        kysimusestatistika.klahendusprotsent = klahp

        # eristusjõud
        q = model.Session.query(sa.func.corr(model.Kysimusevastus.pallid, model.Sooritaja.pallid),
                                sa.func.corr(model.Kysimusevastus.pallid, model.Sooritaja.pallid - model.Kysimusevastus.pallid))
        q = _filter(q, kysimus.id, test.id, testimiskord_id, join_kv=False)        
        r = q.first()
        kysimusestatistika.rit, kysimusestatistika.rir = r

        #log.debug('k %s lahp=%s rit=%s rir=%s' % (kysimus.id, kysimusestatistika.klahendusprotsent, kysimusestatistika.rit, kysimusestatistika.rir))
        
    def _insert_kvstatistika(self, kysimusestatistika, q, test_id, testimiskord_id):
        #if kysimusestatistika.kysimus_id == 335428:
        #    # anomaalia Yl 43494 kysimus TeU4_s2 
        #    return
        # kustutame võimaliku varasema statistika
        model.Kvstatistika.query.\
            filter_by(kysimusestatistika_id=kysimusestatistika.id).\
            delete()
        
        model.Session.flush()
        q = model.Session.query(model.Kysimusestatistika.created,
                                model.Kysimusestatistika.creator,
                                model.Kysimusestatistika.modified,
                                model.Kysimusestatistika.modifier,
                                model.Kysimusestatistika.id,
                                q.subquery())
        q = q.filter(model.Kysimusestatistika.id==kysimusestatistika.id)

        # m = model.Kvstatistika
        # model.sa.insert(model.Kvstatistika).from_select(
        #     (m.created,m.creator,m.modified,m.modifier,
        #      m.kysimusestatistika_id,m.sisu,m.kood1,m.kood2,m.oige,m.tyyp,m.maatriks,m.vastuste_arv),
        #     q)
        sql = 'INSERT INTO kvstatistika (created, creator, modified, modifier, '+\
            'kysimusestatistika_id, sisu, kood1, kood2, oige, tyyp, maatriks, hindamismaatriks_id, vastuste_arv) '+\
            model.str_query(q)
        model.Session.execute(sa.text(sql))
        # # parameetrid tuleks väärtustada dünaamiliselt, aga püüame kasutada q objekti,
        # # et päring oleks sama kui Kysimusestatistika puhul
        # # parameetrid peaks olema võimalik saada q seest kätte, aga praegu kordame väärtustamist
        # params = {'kysimus_id_1': kysimusestatistika.kysimus_id,
        #           'sisestus_1': 1,
        #           'staatus_1': const.S_STAATUS_TEHTUD,
        #           'hindamine_staatus_1': const.H_STAATUS_HINNATUD,
        #           'test_id_1': test_id,
        #           'testimiskord_id_1': testimiskord_id,
        #           'id_1' : kysimusestatistika.id,
        #           }
        # model.session.execute(sa.text(sql % params))

    def _insert_khstatistika(self, kysimusestatistika, q, test_id, testimiskord_id):
        # kustutame võimaliku varasema statistika
        model.Khstatistika.query.\
            filter_by(kysimusestatistika_id=kysimusestatistika.id).\
            delete()
        model.Session.flush()
        q = model.Session.query(model.Kysimusestatistika.created,
                                model.Kysimusestatistika.creator,
                                model.Kysimusestatistika.modified,
                                model.Kysimusestatistika.modifier,
                                model.Kysimusestatistika.id,
                                q.subquery())
        q = q.filter(model.Kysimusestatistika.id==kysimusestatistika.id)

        # m = model.Khstatistika
        # model.sa.insert(m).from_select(
        #     (m.created,m.creator,m.modified,m.modifier,
        #      m.kysimusestatistika_id,m.toorpunktid,m.pallid,m.nullipohj_kood,m.vastuste_arv),
        #     q)
        sql = 'INSERT INTO khstatistika (created, creator, modified, modifier, '+\
            'kysimusestatistika_id, toorpunktid, pallid, nullipohj_kood, vastuste_arv) '+\
            model.str_query(q)
        model.Session.execute(sa.text(sql))

    def refresh_statvastus_t(self, test_id, testimiskord_id, progress_end):
        "Vastuste Exceli väljavõtte puhvertabeli sisu uuendamine"
        # töö jagatakse testiosade kaupa
        if testimiskord_id:
            testimiskord = model.Testimiskord.get(testimiskord_id)
            li = [(ta.testiosa_id, ta.id) for ta in testimiskord.toimumisajad]
        else:
            test = model.Test.get(test_id)
            li = [(o.id, None) for o in test.testiosad]

        # leitakse iga testiosa ylesanded
        # (tykeldame protsessi, et kuvada edenemisprotsenti)
        li2 = []
        cnt = 0
        for testiosa_id, toimumisaeg_id in li:
            q = (model.Session.query(model.Valitudylesanne.id)
                 .join(model.Valitudylesanne.testiylesanne)
                 .filter(model.Testiylesanne.testiosa_id==testiosa_id)
                 )
            lotv = model.Session.query(model.Testiosa.lotv).filter_by(id=testiosa_id).scalar()            
            q = self._query_specify(q, True, lotv)
            
            vyy_id = [vy_id for vy_id, in q.all()]
            cnt += len(vyy_id)
            li2.append((testiosa_id, toimumisaeg_id, vyy_id))

        if self.protsess:
            progress_curr = self.protsess.edenemisprotsent
            step = (progress_end - progress_curr) / cnt

        for testiosa_id, toimumisaeg_id, vyy_id in li2:
            sts = model.Statvastus_t_seis(protsess_id=self.protsess_id,
                                          testiosa_id=testiosa_id,
                                          toimumisaeg_id=toimumisaeg_id,
                                          seisuga=datetime.now())
            model.Session.flush()
            sts_id = sts.id
            for vy_id in vyy_id:
                self._refresh_statvastus_t(testiosa_id, toimumisaeg_id, vy_id, sts_id)
                if self.protsess:
                    progress_curr += step
                    self._save_protsess(progress_curr)

    def _refresh_statvastus_t(self, testiosa_id, toimumisaeg_id, vy_id, sts_id):

        sql = """INSERT INTO statvastus_t
        (statvastus_t_seis_id,
        kood1, selgitus1, kysimus_seq, valik1_seq, ks_punktid, svpunktid,
        kv_punktid, max_punktid, oige, vastus, selgitus, kvsisu_seq, kvsisu_id,
        kysimus_id, kysimusevastus_id, ylesandevastus_id, max_vastus,
        valik1_id, valik2_id, valitudylesanne_id, testiylesanne_id,
        tulemus_id, ylesanne_id, sooritus_id, sooritaja_id, toimumisaeg_id,
        testiosa_id, testikoht_id, staatus)
        SELECT
        :statvastus_t_seis_id,
        kood1, selgitus1, kysimus_seq, valik1_seq, ks_punktid, svpunktid,
        kv_punktid, max_punktid, oige, vastus, selgitus, kvsisu_seq, kvsisu_id,
        kysimus_id, kysimusevastus_id, ylesandevastus_id, max_vastus,
        valik1_id, valik2_id, valitudylesanne_id, testiylesanne_id,
        tulemus_id, ylesanne_id, sooritus_id, sooritaja_id, toimumisaeg_id,        
        testiosa_id, testikoht_id, staatus
        FROM statvastus
        WHERE valitudylesanne_id=:vy_id
        """
        params = {'statvastus_t_seis_id': sts_id,
                  'vy_id': vy_id,
                  }
        if toimumisaeg_id:
            sql += " AND toimumisaeg_id=:toimumisaeg_id"
            params['toimumisaeg_id'] = toimumisaeg_id
        else:
            sql += " AND testiosa_id=:testiosa_id AND toimumisaeg_id IS NULL"
            params['testiosa_id'] = testiosa_id

        model.Session.execute(sa.text(sql), params)
        model.Session.commit()
        
        q = (model.Session.query(model.Statvastus_t)
             .filter_by(toimumisaeg_id=toimumisaeg_id)
             .filter_by(testiosa_id=testiosa_id)
             .filter_by(valitudylesanne_id=vy_id)
             .filter(model.Statvastus_t.statvastus_t_seis_id<sts_id)
             )
        q.delete()
        model.Session.commit()
