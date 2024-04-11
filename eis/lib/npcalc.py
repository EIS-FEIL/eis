"""Normipunktide arvutused
"""
import random
from eiscore.recordwrapper import RecordWrapper
from eis.lib.base import *
from eis.lib.blockresponse import BlockResponse
from eis.lib.blockentry import BlockEntry
from eis.lib.helpers import fstr
from eis.lib.feedbacklocals import feedbacklocals_for_np
log = logging.getLogger(__name__)
_ = i18n._

class Grupivastus:
    def __init__(self, pallid, max_pallid):
        self.pallid = pallid
        self.max_pallid = max_pallid

class Npcalc:
    e_locals = None # testiosa vastused TASK_N.K ja funktsioonid pt(), lenval(), ltase()
    n_locals = {} # praegu arvutatud npvastused
    
    def __init__(self, handler, test, testiosa, sooritaja, sooritus, sooritus_id=None):
        self.sooritaja = sooritaja
        self.test = test
        self.testiosa = testiosa
        self.request = handler and handler.request # tõlkimise jaoks
        self.handler = handler
        self.tos = sooritus
        # sooritus_id puudub ilma testita lahendamisel
        self.sooritus_id = sooritus_id or sooritus and sooritus.id
        try:
            self.npvastused = [nv for nv in sooritus.npvastused]
        except Exception as ex:
            self.npvastused = [] # soorituse npvastused (mitte ylesande omad)
            log.error(f'Npcalc.npvastused viga: {ex}')
        
    def calc_npvastused(self):
        "Normipunktide väärtuste arvutamine ja salvestamine"
        lang = self.sooritaja.lang
        self._calc_ty_np()
        self._calc_ala_np()
        self._calc_osa_np(lang)

    def calc_diag_ty(self, ty, vy, yv, grupid, ylesandevastused, y_locals):
        "Diagnoosivas testis tagasiside arvutamine kohe peale ülesande sooritamist"
        # arvutatakse ylesande normipunktide väärtused
        # koostatakse tagasiside
        # tagastatakse järgmise ylesande ty.id

        # leiame ylesandegrupid, mis said selle ylesandega tehtuks
        def get_done_grupid():
            done_grupid_id = []
            gruppidevastused = {}
            if grupid:
                for grupp_id, vyy_id in grupid.items():
                    is_done = True
                    grupivastused = {}
                    for vy1_id in vyy_id:
                        # kas ylesanne on tehtud?
                        yv = ylesandevastused.get(vy1_id)
                        if yv:
                            # ylesanne on tehtud
                            grupivastused[vy1_id] = yv
                        else:
                            # ylesande vastust ei ole veel
                            is_done = False
                            break
                        # if yv1.lopp and yv.lopp and yv1.lopp > yv.lopp:
                        #     # ylesanne on vastatud peale antud ylesannet (tagantjärele tagasiside yle arvutamise korral)
                        #     is_done = False
                        #     break
                    if is_done:
                        # grupi kõik ylesanded on tehtud
                        done_grupid_id.append(grupp_id)
                        gruppidevastused[grupp_id] = grupivastused
            return done_grupid_id, gruppidevastused
        
        # leiame normipunktid kirjeldamise järjekorras
        def get_normipunktid(done_grupid_id):
            q = (model.Session.query(model.Normipunkt)
                 .filter(model.Normipunkt.testiosa_id==self.testiosa.id)
                 )
            if done_grupid_id:
                q = q.filter(model.sa.or_(
                    model.Normipunkt.ylesandegrupp_id.in_(done_grupid_id),
                    model.Normipunkt.testiylesanne_id==ty.id))
            else:
                q = q.filter(model.Normipunkt.testiylesanne_id==ty.id)
            return q.order_by(model.Normipunkt.seq).all()


        done_grupid_id, gruppidevastused = get_done_grupid()
        next_ty_id = None
        # arvutame kõik normipunktid, mille arvutamise võimalus praegu tekkis
        for np in get_normipunktid(done_grupid_id):
            if np.ylesandegrupp_id:
                gvastused = gruppidevastused[np.ylesandegrupp_id]
                # gvastused on {vy_id: {pallid: N}, vy2_id: {pallid: N}, ...}
                g_pallid = sum([yv['pallid'] for yv in gvastused.values()])
                vastus = self._get_grupivastus(np.ylesandegrupp_id, g_pallid)
                npv = self._calc_npv(np, vastus)
            else:
                npv = self._calc_npv(np, yv, y_locals=y_locals)
            log.debug('  npv %s=%s/%s' % (np.kood, npv.nvaartus, npv.svaartus))
            if not next_ty_id:
                ns_id = npv.nptagasiside_id
                nts = ns_id and model.Nptagasiside.getR(ns_id)
                next_ty_id = nts and nts.uus_testiylesanne_id or None

        return next_ty_id

    def calc_ylesanne_np(self, ylesanne, np, yv, npv):
        "Ühe normipunkti väärtuse arvutamine testivälist ülesannet lahendades (tagasisidega ülesanne)"

        def _get_normipunkt_value(np, pallid):
            npvalue = None
            if np.normityyp == const.NORMITYYP_PALLID:
                npvalue = pallid
            elif np.normityyp == const.NORMITYYP_PROTSENT:
                max_pallid = ylesanne.max_pallid
                if not max_pallid:
                    log.debug('puudub max_pallid')
                else:
                    npvalue = (pallid or 0) * 100. / max_pallid
            else:
                log.debug('vale normityyp %s' % np.normityyp)
            return npvalue

        assert not np.kysimus_kood, "Ülesande tagasiside ühe küsimuse kohta ei ole teostatud"
        nvalue = _get_normipunkt_value(np, yv.toorpunktid)
        self._set_npvalue(npv, nvalue)
        log.debug('yv %s np %s (%s) %s vastus=%s' % (yv.id, np.id, np.nimi or np.normityyp_nimi or '', np.kysimus_kood, nvalue))

        nts = None
        if nvalue is not None:
            log.debug('nvalue=%s' % nvalue)
            for r in np.nptagasisided:
                log.debug('npts %s' % r.id)
                # kontrollime, kas tingimus on täidetud
                if ns_eval_value(r, nvalue):
                    # tingimus on täidetud
                    nts = r
                    break
        npv.nptagasiside_id = nts and nts.id or None
        return nts
    
    def calc_ylesanne_tagasiside(self, yv, ylesanne, lang, force=False):
        "Testivälise ülesande tagasiside (tagasisidega ülesanne)"
        msg = ''
        jatka = False
        nts_id = None
        if ylesanne.kuva_tulemus:
            pallid = yv.toorpunktid
            max_pallid = ylesanne.get_max_pallid()
            msg = _("Tulemus: {s1} punkti {s2}-st võimalikust").format(s1=fstr(pallid), s2=fstr(max_pallid))

        npvastused = {nv.normipunkt_id: nv for nv in yv.npvastused}
        sooritus_id = yv.sooritus_id

        for np in ylesanne.normipunktid:
            npv = npvastused.get(np.id)        
            if not npv:
                npv = self._add_npvastus(sooritus_id, yv, np.id)
            if not force:
                # kasutame olemasolevat
                nts = None
                for r in np.nptagasisided:
                    if r.id == npv.nptagasiside_id:
                        nts = r
                        break
            else:
                # arvutame
                nts = self.calc_ylesanne_np(ylesanne, np, yv, npv)
            if ylesanne.kuva_tulemus:
                npvalue = npv.nvaartus
                if npvalue is not None and np.normityyp == const.NORMITYYP_PROTSENT:
                    msg = '%s: %s%%' % (_("Tulemus"), fstr(npvalue, 0))
                msg += '<br/>'
            if nts:
                tsbuf = nts.tran(lang).tagasiside or ''
                if tsbuf:
                    msg += tsbuf
                jatka = nts.jatka
            break

        tsbuf = ylesanne.tran(lang).yl_tagasiside
        if tsbuf:
            if msg:
                msg += '<div style="padding:5px"></div>'
            msg += tsbuf
        return msg, jatka

    def _calc_ty_np(self):
        # testiylesannete normipunktid
        q = (model.Session.query(model.Normipunkt,
                                 model.Testiylesanne)
             .join(model.Normipunkt.testiylesanne)
             .filter(model.Testiylesanne.testiosa_id==self.testiosa.id)
             .order_by(model.Testiylesanne.alatest_seq,
                       model.Testiylesanne.seq,
                       model.Normipunkt.seq))
        for np, ty in q.all():
            yv = self.tos.get_ylesandevastus(ty.id)
            if yv:
                npv = self._calc_npv(np, yv)                

    def _calc_ala_np(self):
        # alatestide normipunktid
        q = (model.Session.query(model.Normipunkt, model.Alatest)
             .join(model.Normipunkt.alatest)
             .filter(model.Normipunkt.testiylesanne_id==None)
             .filter(model.Alatest.testiosa_id==self.testiosa.id)
             .order_by(model.Alatest.seq,
                       model.Normipunkt.seq))
        for np, ala in q.all():
            atos = self.tos.get_alatestisooritus(ala.id)
            if atos:
                npv = self._calc_npv(np, atos)

    def _calc_osa_np(self, lang):
        # testiosa normipunktid, sh ylesandegruppide normipunktid
        q = (model.Normipunkt.query
             .filter(model.Normipunkt.testiosa_id==self.testiosa.id)
             .filter(model.Normipunkt.alatest_id==None)
             .filter(model.Normipunkt.testiylesanne_id==None)
             .filter(model.sa.or_(model.Normipunkt.lang=='',
                                  model.Normipunkt.lang==None,
                                  model.Normipunkt.lang==lang))
             .order_by(model.Normipunkt.seq))
        #model.log_query(q)
        for np in q.all():
            ygrupp_id = np.ylesandegrupp_id
            if ygrupp_id:
                # ylesandegrupi normipunkt
                g_pallid = self._q_grupivastus_pallid(self.sooritaja.id, ygrupp_id)
                vastus = self._get_grupivastus(ygrupp_id, g_pallid)
            else:
                # testiosasooritus
                vastus = self.tos
            log.debug('calc np %s...' % np.id)
            npv = self._calc_npv(np, vastus)

    def set_locals(self, e_locals):
        self.e_locals = e_locals
        
    def _init_locals(self):
        # valemis võib kasutada TASK_N.K ja funktsioone, leiame need
        if self.e_locals is None:
            self.e_locals = get_np_task_locals(self.handler, self.sooritaja, self.test)

    def _calc_npv(self, np, vastus, y_locals=None):
        # normipunkti vastuse kirje loomine ja väärtustamine
        # vastus on Grupivastus või y_responses
        if np.normityyp == const.NORMITYYP_VALEM:
            # valemis võib kasutada TASK_N.K ja funktsioone
            self._init_locals()
            # lisame arvutatud normipunktid
            self.e_locals.update(self.n_locals)

        value, err = self.get_normipunkt_value(np, vastus, e_locals=self.e_locals, y_locals=y_locals)
        npv = self._give_npvastus(self.sooritus_id, np.id)            
        log.debug('np %s %s (%s) %s vastus=%s' % (np.id, np.kood, np.nimi or np.normityyp_nimi or '', np.kysimus_kood, value))
        self._set_npvalue(npv, value, err)
        if np.kood:
            # jätame vastuse meelde, et hiljem valemites kasutada
            self.n_locals[np.kood] = value

        # leiame esimese sellise tagasiside, mille tingimus on täidetud
        nts = None
        for r in np.nptagasisided:
            # kui tingimus käib ahela kohta, siis 
            # kontrollime, kas ahelas eespool olev ylesanne on tehtud
            if not r.ahel_testiylesanne_id or \
                   self.tos.get_ylesandevastus(r.ahel_testiylesanne_id):
                # kui ahel on õige, siis kontrollime, kas tingimus on täidetud
                if ns_eval_value(r, value):
                    # tingimus on täidetud
                    nts = r
                    break
        npv.nptagasiside_id = nts and nts.id or None
        return npv

    def _set_npvalue(self, npv, value, err=None):
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            npv.nvaartus = value
            npv.svaartus = None
        else:
            npv.nvaartus = None
            npv.svaartus = value
        npv.viga = err and err[:256] or None
    
    def _give_npvastus(self, sooritus_id, normipunkt_id):
        # soorituse normipunkti vastuse kirje loomine
        rcd = None
        for npv in self.npvastused:
            if npv.normipunkt_id == normipunkt_id:
                rcd = npv
                break
        if not rcd:
            rcd = self._add_npvastus(sooritus_id, None, normipunkt_id)
        return rcd

    def _add_npvastus(self, sooritus_id, yv, np_id):
        if yv:
            # ylesande npvastus
            if isinstance(yv, model.EntityHelper):
                npv = model.Npvastus(sooritus_id=sooritus_id,
                                     ylesandevastus=yv,
                                     normipunkt_id=np_id)
            else:
                npv = RecordWrapper(sooritus_id=sooritus_id,
                                    normipunkt_id=np_id,
                                    nptagasiside_id=None)
                yv.npvastused.append(npv)
        else:
            # soorituse npvastus
            if isinstance(self.tos, model.EntityHelper):
                npv = model.Npvastus(sooritus_id=sooritus_id,
                                     normipunkt_id=np_id)
            else:
                npv = RecordWrapper(sooritus_id=sooritus_id,
                                    normipunkt_id=np_id,
                                    nptagasiside_id=None)
            self.npvastused.append(npv)
        return npv
    
    def _get_grupivastus(self, ygrupp_id, g_pallid):
        # grupi saadud pallide ja max pallide leidmine
        g_max = None
        if ygrupp_id:
            q = (model.Session.query(model.sa.func.sum(model.Testiylesanne.max_pallid))
                 .join(model.Testiylesanne.valitudylesanded)
                 .filter(model.Valitudylesanne.grupiylesanded.any(
                     model.Grupiylesanne.ylesandegrupp_id==ygrupp_id))
                 )
            g_max = q.scalar()
        return Grupivastus(g_pallid, g_max)

    def _q_grupivastus_pallid(self, sooritaja_id, ygrupp_id):
        "Leitakse gruppi kuuluvate ülesannete pallide kogusumma"
        # leiame ylesanded
        q = (model.SessionR.query(model.Valitudylesanne.testiylesanne_id)
             .filter(model.Valitudylesanne.grupiylesanded.any(
                 model.Grupiylesanne.ylesandegrupp_id==ygrupp_id))
             )
        tyy_id = [r[0] for r in q.all()]
        if tyy_id:
            # grupis on ylesandeid
            # leiame soorituste ID
            q = (model.SessionR.query(model.Sooritus.id).filter_by(sooritaja_id=sooritaja_id))
            sooritused_id = [v for v, in q.all()]
            # leiame vastuste pallid
            q = (model.SessionR.query(model.sa.func.sum(model.Ylesandevastus.pallid))
                 .filter(model.Ylesandevastus.sooritus_id.in_(sooritused_id))
                 .filter(model.Ylesandevastus.loplik==True)
                 .filter(model.Ylesandevastus.testiylesanne_id.in_(tyy_id))
                 )
            g_pallid = q.scalar()
            return g_pallid
    
    def get_normipunkt_value(self, np, vastus, e_locals={}, y_locals=None):
        # vastus - sooritus või alatestisooritus või ylesandevastus
        protsent1 = protsent2 = value = err = q = None
        if not vastus:
            value = None
        elif np.normityyp == const.NORMITYYP_VASTUS:
            #if np.kysimus_kood and isinstance(vastus, model.TempYlesandevastus):
            if np.kysimus_kood and y_locals is not None:
                # diagnoosiva testi ylesanne
                value = y_locals.get(np.kysimus_kood)
                #if isinstance(value, list) and len(value) == 1:
                #    value = value[0]
            elif np.kysimus_kood:
                nvalue = svalue = None
                q = (model.Session.query(model.Kvsisu.sisu, model.Tulemus.baastyyp)
                     .join(model.Kvsisu.kysimusevastus)
                     .join((model.Kysimus,
                            model.Kysimus.id==model.Kysimusevastus.kysimus_id))
                     .filter(model.Kysimus.kood==np.kysimus_kood)
                     .join(model.Kysimus.tulemus)
                     )
                if isinstance(vastus, model.Sooritus):
                    q = (q.join(model.Kysimusevastus.ylesandevastus)
                         .filter(model.Ylesandevastus.sooritus_id==vastus.id)
                         )
                elif isinstance(vastus, model.Alatestisooritus):
                    q = (q.join(model.Kysimusevastus.ylesandevastus)
                         .filter(model.Ylesandevastus.sooritus_id==vastus.sooritus_id)
                         .join((model.Testiylesanne,
                                model.Testiylesanne.id==model.Ylesandevastus.testiylesanne_id))
                         .filter(model.Testiylesanne.alatest_id==vastus.alatest_id)
                         )
                elif isinstance(vastus, model.Ylesandevastus):
                    q = q.filter(model.Kysimusevastus.ylesandevastus_id==vastus.id)
                    if q.count() == 0:
                        # kas on tabamuste loendur?
                        q1 = (model.Session.query(model.Loendur.tabamuste_arv)
                              .filter_by(ylesandevastus_id=vastus.id)
                              .filter_by(tahis=np.kysimus_kood))
                        for cnt, in q1.all():
                            nvalue = cnt
                            q = None
                            break
                else:
                    # Grupivastus?
                    log.error('Test %s: vastuse tyyp np %s vastus=%s' % (self.testiosa.test_id, np.id, vastus))
                    q = None

                if q:
                    if not q.count():
                        log.error('Test %s: ei leia kysimust %s (np %s)' % (self.testiosa.test_id, np.kysimus_kood, np.id))
                    for kvalue, baastyyp in q.all():
                        if baastyyp in (const.BASETYPE_INTEGER, const.BASETYPE_FLOAT):
                            if nvalue is None:
                                nvalue = 0
                            if kvalue:
                                try:
                                    nvalue += float(kvalue)
                                except:
                                    pass
                        else:
                            svalue = kvalue
                if nvalue is None:
                    value = svalue
                else:
                    value = nvalue

        elif np.normityyp == const.NORMITYYP_KPALLID:
            # kysimuse keskmised pallid?
            q = (model.Session.query(model.sa.func.count(model.Kysimus.id))
                 .filter(model.Kysimus.kood!=None)
                 .join(model.Kysimus.tulemus)
                 .join(model.Kysimus.sisuplokk)
                 .filter(model.Sisuplokk.tyyp!=const.BLOCK_FORMULA)
                 .join((model.Valitudylesanne,
                        model.Valitudylesanne.ylesanne_id==model.Sisuplokk.ylesanne_id))
                 .join((model.Ylesandevastus,
                        model.Ylesandevastus.valitudylesanne_id==model.Valitudylesanne.id))
                 )
            if isinstance(vastus, model.Sooritus):
                q = q.filter(model.Ylesandevastus.sooritus_id==vastus.id)
            elif isinstance(vastus, model.Alatestisooritus):
                q = (q.filter(model.Ylesandevastus.sooritus_id==vastus.sooritus_id)
                     .join(model.Valitudylesanne.testiylesanne)
                     .filter(model.Testiylesanne.alatest_id==vastus.alatest_id)
                     )
            elif isinstance(vastus, model.Ylesandevastus):
                q = q.filter(model.Ylesandevastus.id==vastus.id)
            cnt = q.scalar()
            if cnt > 0:
                value = vastus.pallid / cnt
                
        elif np.normityyp == const.NORMITYYP_PALLID:
            if np.kysimus_kood and isinstance(vastus, model.Ylesandevastus):
                # kysimuse pallid
                q = (model.Session.query(model.sa.func.sum(model.Kysimusevastus.pallid))
                     .join((model.Kysimus,
                            model.Kysimus.id==model.Kysimusevastus.kysimus_id))
                     .filter(model.Kysimus.kood==np.kysimus_kood)
                     )
                q = q.filter(model.Kysimusevastus.ylesandevastus_id==vastus.id)
                value = q.scalar()
            else:
                # testiosa/alatesti/ylesande pallid
                value = vastus.pallid

        elif np.normityyp == const.NORMITYYP_PUNKTID:
            # kysimuse toorpunktid
            assert np.kysimus_kood, "Punktide korral on vaja küsimust"
            if isinstance(vastus, model.Ylesandevastus):
                q = (model.Session.query(model.sa.func.sum(model.Kysimusevastus.toorpunktid))
                     .join((model.Kysimus,
                            model.Kysimus.id==model.Kysimusevastus.kysimus_id))
                     .filter(model.Kysimus.kood==np.kysimus_kood)
                     )
                q = q.filter(model.Kysimusevastus.ylesandevastus_id==vastus.id)
                value = q.scalar()
            else:
                raise Exception("Küsimuse pallid on teostatud ainult ülesandesiseselt")
                
        elif np.normityyp == const.NORMITYYP_PROTSENT:
            if isinstance(vastus, Grupivastus):
                # grupi pallide protsent
                if vastus.pallid is not None and vastus.max_pallid:
                    value = vastus.pallid * 100. / vastus.max_pallid
            elif isinstance(vastus, model.Ylesandevastus):
                # ylesande protsent
                max_p = vastus.valitudylesanne.ylesanne.max_pallid
                if max_p:
                    value = (vastus.toorpunktid or 0) * 100. / max_p
        elif np.normityyp == const.NORMITYYP_SUHE:
            value = vastus.oigete_suhe
        elif np.normityyp == const.NORMITYYP_AEG:
            value = vastus.ajakulu
        elif np.normityyp == const.NORMITYYP_VEAD:
            value = vastus.valede_arv

        elif np.normityyp == const.NORMITYYP_VALEM:
            value, err0, err, buf = model.eval_formula(np.kysimus_kood, e_locals)
            if value == '':
                value = None
        if value is None or isinstance(value, (str, bool, int, float)):
            return value, err
        else:
            msg = 'test %s np %d (%s) nptyyp %s sooritus %s vigane vastus: %s' % \
                  (self.test.id, np.id, np.kood, np.normityyp, self.sooritus_id, value)
            if np.normityyp == const.NORMITYYP_VALEM:
                err = _("Vigane valem (tulemus pole tekst, tõeväärtus ega arv)")
                log.error(err + '\n' + msg)
                return None, err
            raise Exception(msg)

def get_np_task_locals(handler, sooritaja, test):
    return feedbacklocals_for_np(handler, test, sooritaja)

def get_dummy_osa_np(test, osa_seq, max_seq):
    """Normipunktide kirjeldamisel tehtava kontrolli jaoks
    leitakse sama testiosa varasemad normipunktid,
    kuna neid võidakse olla valemis kasutatud
    """
    p_locals = {}
    q = (model.Normipunkt.query
         .join(model.Normipunkt.testiosa)
         .filter(model.Testiosa.test_id==test.id)
         .filter(model.Testiosa.seq <= osa_seq)
         .filter(model.Normipunkt.alatest_id==None)
         .filter(model.Normipunkt.testiylesanne_id==None)
         .filter(model.Normipunkt.kood!=None)
         )   
    if max_seq is not None:
        q = q.filter(model.Normipunkt.seq<max_seq)
    for np in q.order_by(model.Normipunkt.seq).all():
        if np.kood:
            p_locals[np.kood] = 1
    return p_locals

def ns_eval_value(npts, npvalue):
    "Leitakse, kas normipunkti väärtus npvalue vastab tingimusele"
    rc = False
    if npvalue is None:
        value = None

    elif npts.tingimus_vaartus is not None:
        # arvude võrdlemine
        value = npts.tingimus_vaartus
        diff = 1e-9
        if not isinstance(npvalue, (int, float)):
            log.error('nps %s: npvalue pole arv: %s' % (npts.id, npvalue))
            rc = None
        elif npts.tingimus_tehe == '<':
            rc = npvalue < value
        elif npts.tingimus_tehe == '<=':
            rc = npvalue < value + diff
        elif npts.tingimus_tehe == '==':
            rc = (npvalue > value - diff) and (npvalue < value + diff)
        elif npts.tingimus_tehe == '>=':
            rc = npvalue > value - diff
        elif npts.tingimus_tehe == '>':
            rc = npvalue > value

    else:
        # tekstide võrdlemine
        value = [npts.tingimus_valik]
        
        if npts.tingimus_tehe == '<':
            rc = npvalue < value
        elif npts.tingimus_tehe == '<=':
            rc = npvalue <= value
        elif npts.tingimus_tehe == '==':
            rc = npvalue == value
        elif npts.tingimus_tehe == '>=':
            rc = npvalue >= value
        elif npts.tingimus_tehe == '>':
            rc = npvalue > value
            
    log.debug('NPS %s %s %s == %s' % (npvalue, npts.tingimus_tehe, value, rc))
    return rc

