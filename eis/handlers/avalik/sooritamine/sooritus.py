import random
from simplejson import dumps

from eis.lib.baseresource import *
_ = i18n._
from eis.lib.block import BlockController
from eis.lib.blockresponse import BlockResponse
from eis.lib.blockcalc import BlockCalc
from eis.lib.resultentry import ResultEntry
from eis.lib.npcalc import Npcalc
from eis.handlers.avalik.lahendamine.esitlus import EsitlusController
from eiscore.examwrapper import MemYlesandevastus
from eiscore.recordwrapper import RecordWrapper
from eis.lib.testclient import TestClient, MemYlesanne
from eis.lib.examclient import ExamClient
from eis.lib.testsaga import TestSaga
from eis.s3file import s3file_save
log = logging.getLogger(__name__)

# andmete seansi puhvris meeles pidamise versioon
ALLOWED_VER = 2
# veateade, mida ei kuvata, sest kasutaja juba teab
ERROR_NA = "NA"

class SooritusController(BaseResourceController, EsitlusController):
    """Testiosa sooritamine ja soorituse salvestamine
    """
    _EDIT_TEMPLATE = 'avalik/sooritamine/sooritus.mako'
    _MODEL = model.Sooritus
    _log_params_post = True
    _log_params_get = True
    _ignore_alatest = False
    _get_is_readonly = False
    _TASK_TEMPLATE = '/avalik/sooritamine/sooritus.esitlus.mako'

    _actions = 'create,edit,update'
    _actionstask = 'edittask,updatetask,showtool'
    _is_prf = True
    _on_eelvaade = False
    
    def create(self):
        # sooritamise alustamine
        # loome uue soorituse kirje ja SALVESTAME ka
        # uut sooritajat saab lisada ainult siis, kui test on kõigile vabalt lahendamiseks
        c = self.c
        test = model.Test.get(c.test_id)
        self.prf()

        # otsime pooleli/katkestatud/alustamata sooritajakirje ja kas on võimalik lahendada
        is_permitted, sooritaja, error = TestSaga(self).get_sooritaja_for(test, c.user.id)
        if not is_permitted:
            # seda testi ei saa lahendada
            self.error(error)
            return HTTPFound(location=self.url('sooritamised'))
        
        if not sooritaja:
            # avalikus kasutuses olev test, mida saab ise sooritama hakata
            if c.user.testpw_id:
                # testiparooliga ei saa uut registreeringut luua
                self.error(_("Testiparooliga sisenenult ei saa teisi teste sooritada"))
                return HTTPFound(location=c.user.testpw_home_url())
            # loome uus sooritajakirje
            lang = self.params_lang() or test.lang
            kursus = self.request.params.get('kursus') or None
            added, sooritaja = \
                model.Sooritaja.registreeri(c.user.get_kasutaja(),
                                            test.id,
                                            None,
                                            lang,
                                            None,
                                            const.REGVIIS_SOORITAJA,
                                            c.user.id,
                                            c.user.koht_id or None,
                                            alustamata=True,
                                            mittekorduv=False)
            sooritaja.kursus_kood = kursus
            
        sooritus = sooritaja.get_sooritus(c.testiosa_id)
        if not sooritus:
            self.error(_("Testi struktuur on muutunud"))
        elif c.user.testpw_id and c.user.testpw_id != sooritaja.id:
            self.error(_("Testiparooliga sisenenult ei saa teisi teste sooritada"))
            return HTTPFound(location=c.user.testpw_home_url())
        elif sooritus.staatus not in (const.S_STAATUS_POOLELI, const.S_STAATUS_KATKESTATUD) \
             and not sooritus.saab_alustada():
            # test on pooleli, aga seda testiosa ei saa sooritada
            self.error(_("Testiosa on {s}, ei saa sooritada").format(s=sooritus.staatus_nimi))
        else:
            # testiosa soorituse kirje on olemas ja seda võib lahendama hakata
            c.item = sooritus

        if not c.item:
            if sooritaja:
                url = self.url('sooritamine_alustamine', test_id=test.id, sooritaja_id=sooritaja.id)
            else:
                url = self.url('sooritamine_test', test_id=test.id)
            return HTTPFound(location=url)
           
        c.item = sooritus       
        sooritaja = c.item.sooritaja
        if sooritaja:
            c.lang = sooritaja.lang
        c.item.autentimine = c.user.auth_type
        c.item.remote_addr = self.request.remote_addr        

        model.Session.commit()

        if not sooritaja.testimiskord_id and not test.korduv_sailitamine:
            # kui ei ole säilitamist, siis kustutame varasemad avalikud sooritused
            q = (model.Sooritaja.query
                 .filter(model.Sooritaja.kasutaja_id==c.user.id)
                 .filter(model.Sooritaja.test_id==test.id)
                 .filter(model.Sooritaja.testimiskord_id==None)
                 .filter(model.Sooritaja.id!=sooritaja.id)
                 )
            for rcd in q.all():
                rcd.delete()
            model.Session.commit()

        # suuname testi tegema
        # tahame, et loodud soorituse ID oleks URLi sees, et kasutaja saaks refreshi korral samasse sooritusse
        # lisaks veebiliikluse analyysi huvides soovime, et URL oleks "alusta" või "jatka"
        url = self.url('sooritamine_alusta_osa', test_id=c.test_id, testiosa_id=c.testiosa_id, id=sooritus.id)
        return HTTPFound(location=url)

    def _show_d(self):
        c = self.c
        id = self.request.matchdict.get('id')
        c.sooritus_id = int(id)
        # pärime ms kaudu test, testiosa, alatest
        error = self._get_test()
        if error:
            raise HTTPFound(location=self._url_quit(c.sooritus_id))            
        self._show(None)
        return self.response_dict
    
    def _show(self, item):
        """Testiosa sisu näitamine nii lahendajale kui ka vaatajale
        """
        c = self.c
        self.prf(True)
        self.c.pagesm = True
        
        if c.read_only:
            # pärime andmebaasist juba tehtud soorituse andmed
            if not self._ignore_alatest:
                if not c.alatest_id and c.alatestid:
                    # alatesti pole URLis näidatud
                    # sooritust vaadates avame kohe mõne alatesti
                    c.alatest = c.alatestid[0]
                    c.alatest_id = c.alatest.id
                    self.prf()

            c.sooritus = model.Sooritus.get(c.sooritus_id)
            if not c.sooritus:
                self.error(_("Vigane URL"))
                return HTTPFound(location=self._url_quit(c.sooritus_id))
            c.sooritus_staatus = c.sooritus.staatus
            c.sooritus_ajakulu = c.sooritus.ajakulu
            c.sooritaja = c.sooritus.sooritaja
            if c.sooritus.staatus != const.S_STAATUS_TEHTUD:
                if not c.test:
                    c.test = c.sooritaja.test
                if c.test.testityyp != const.TESTITYYP_TOO:
                    self.error(_("Testisooritus pole veel lõpetatud!"))
                    raise HTTPFound(location=self._url_quit(c.sooritus_id))
            
            self.what_to_show()

            # toome klastrist, kui pole veel toodud
            if c.sooritus.klastrist_toomata:
                ta = self._get_toimumisaeg()
                if not c.test:
                    c.test = c.sooritaja.test
                if not c.testiosa:
                    c.testiosa = c.sooritus.testiosa
                exapi_host = model.Klaster.get_host(c.sooritaja.klaster_id)
                ExamSaga(self).from_examdb(exapi_host, c.sooritus, c.sooritaja, c.test, c.testiosa, ta, c.lang, False)

            # leiame komplekti
            if (not c.sooritus.klastrist_toomata or not c.exapi_host):
                # andmed juba põhibaasis või on sooritatud enne klastreid
                q = (model.Session.query(model.Soorituskomplekt.komplekt_id)
                     .filter_by(sooritus_id=c.sooritus_id))
                if c.alatest:
                    kv_id = c.alatest.komplektivalik_id
                    q = q.filter_by(komplektivalik_id=kv_id)
                for k_id, in q.all():
                    c.komplekt_id = k_id
                    break

            # alatestisooritused samal viisil nagu examapi.edit teeb
            # (alatestisoorituste olekute kuvamiseks)
            c.alatestisooritused = {}
            for atos in c.sooritus.alatestisooritused:
                c.alatestisooritused[atos.alatest_id] = atos
        self.prf()

        # funktsioonid mako sees kasutamiseks
        c.BlockController = BlockController
        # ylesanderibal olevad ylesanded
        error, c.testiylesanded, c.sooritusjrk, c.ty = self.get_testiylesanded(c.komplekt_id)
        if error:
            self.error(error)
            raise HTTPFound(location=self._url_quit(c.sooritus_id))
        self.prf()

    def what_to_show(self):
        c = self.c
        if c.sooritaja:
            # kui ei ole testi eelvaade, siis on olemas sooritaja
            c.testimiskord = c.sooritaja.testimiskord
            r = c.sooritus.can_show(c.test, c.sooritaja, c.testimiskord, c.app_ekk)
            c.show_sooritus_tulemus, c.show_alatestitulemus, c.show_ylesandetulemus = r
  
        c.show_yl_oige = c.sooritus.staatus == const.S_STAATUS_TEHTUD and \
            (c.test.diagnoosiv or \
             not c.testimiskord or c.testimiskord.ylesandetulemused_avaldet or c.app_ekk) and \
             c.test.testiliik_kood != const.TESTILIIK_KOOLIPSYH and \
                 c.test.naita_p

        if c.prepare_correct == 'Y':
            # tuldud avalik/testitulemused/sooritus.mako
            c.prepare_correct = c.show_ylesandetulemus or c.app_ekk
            c.btn_correct = c.prepare_correct
        
    def alusta(self):
        if self.c.sooritus_id:
            return self.edit()
        else:
            return self.create()

    def jatka(self):
        return self.edit()

    def edit(self):
        response = BaseResourceController.edit(self)
        response.cache_control = 'no-cache, no-store, must-revalidate'
        response.cache_expires(0)
        return response

    def _edit_d(self):
        # väldime c.item päringut andmebaasist
        id = self.request.matchdict.get('id')
        self.c.sooritus_id = self.convert_id(id)
        rc = self._edit(None)
        if isinstance(rc, Response):
            return rc
        return self.response_dict
    
    def _edit(self, item):
        """Testiosa sisu näitamine lahendajale
        (item on None, et mitte teha liigseid andmebaasipäringuid)
        """
        c = self.c
        # päritakse andmed: test, testiosa, alatest, komplektid
        error = self._get_test()
        if error:
            self.error(error)
            raise HTTPFound(location=self._url_quit(c.sooritus_id))            
        # kas õigus on juba kontrollitud?
        # kui ei, siis kontrollitakse testi sooritamise õigust
        rc, item = self._check_edit_permission()
        if not rc:
            raise HTTPFound(location=self._url_quit(c.sooritus_id))

        error = None
        
        # kas on edit või update (mõjutab veateate sisu, kui testi ei saa sooritada)
        is_update = False
        # proctorio kontrollimiseks
        url_id = self.request.matchdict.get('id')

        # siin ei tea komplekti
        data = {'remote_addr': self.request.remote_addr,
                'testiarvuti_id': c.testiarvuti_id,
                'url_id': url_id,
                'auth_type': c.user.auth_type,
                'is_update': is_update,
                'tingimus': self._get_tingimus(c.testiosa),
                'alatest_id': c.alatest_id or None,
                'testiosa': self._data_testiosa(c.testiosa),
                'alatestid': c.alatestid,
                }
        for n in range(2):
            # esimesel korral eeldame, et soorituse kirje on eelnevalt klastris loodud
            # kui ei ole, siis lisame ja teeme teise päringu
            r = ExamClient(self, c.exapi_host).edit(c.sooritus_id, data)
            if r.get('errcode') == 'NODATA':
                # lisame soorituskirje klastrisse
                item = model.Sooritus.get(c.sooritus_id)
                if not item:
                    error = _("Sooritus puudub")
                    break
                sooritaja = item.sooritaja
                ExamSaga(self).init_klaster(item, sooritaja)
                # proovime teist korda
                continue
            # veateade või None
            error = r.get('error')
            staatus = self._change_status(r)
            break

        if error:
            self.error(error)
            raise HTTPFound(location=self._url_quit(c.sooritus_id))
        else:
            error = r.get('error')
            c.sooritus_staatus = staatus = self._change_status(r)

            c.piiraeg = r.get('piiraeg')
            c.ajakulu = r.get('ajakulu')
            c.kasutamata = r.get('kasutamata')
            alatest_id = r.get('alatest_id')
            if alatest_id and alatest_id != c.alatest_id:
                # muudame c.alatest
                c.alatest_id = alatest_id
                error = self._get_test()
                
            # alatestide nimetuste juures olekute kuvamiseks
            c.alatestisooritused = {}
            for r1 in r.get('alatestisooritused') or []:
                rec = RecordWrapper.create_from_dict(r1)
                c.alatestisooritused[rec.alatest_id] = rec

            c.komplekt_id = r.get('komplekt_id')
            if r.get('read_only'):
                c.read_only = True

            # leitakse komplektide valik ja
            # kas lahendaja saab komplekti ise valida
            c.saab_valida_komplekti = self._komplektid()
            
        if error:
            log.error('%s sooritus %s: %s' % \
                      (c.user.isikukood, c.sooritus_id, error))
            self._error_log(error)
            self.error(error)
            url = self._url_kysitlus(c.sooritus_id, True)
            raise HTTPFound(location=url)
        else:
            # päritakse andmebaasist ylesannete andmed
            self._show(item)
  
    def _check_intervjuu_lv(self, item):
        "Testimiskorraga intervjuu vormis testi intervjueerija kontroll"
        testiruum_id = item.testiruum_id
        q = (model.Session.query(model.Labiviija.id)
             .filter(model.Labiviija.testiruum_id==testiruum_id)
             .filter(model.Labiviija.kasutaja_id==self.c.user.id)
             )
        for lv_id, in q.all():
            # märgime intervjueerija soorituse juurde
            if item.intervjuu_labiviija_id != lv_id:
                item.intervjuu_labiviija_id = lv_id
            return lv_id

    def _check_test_staatus(self):
        c = self.c
        return c.test.staatus == const.T_STAATUS_KINNITATUD

    def _check_vastvorm(self, item, sooritaja):
        rc = error = False
        c = self.c
        if c.testiosa.vastvorm_kood == const.VASTVORM_I:
            # intervjueerija kontroll
            if item.toimumisaeg_id and c.test.avaldamistase != const.AVALIK_MAARATUD:
                # testimiskorraga suuline test, vastuseid sisestab intervjueerija
                rc = self._check_intervjuu_lv(item) and True or False
            else:
                # testimiskorrata suuline test, vastuseid sisestab läbiviija
                testiruum = item.testiruum
                rc = testiruum.has_permission('testiadmin', const.BT_UPDATE, c.user)
            if not rc:
                error = _("Sooritamiseks on vaja intervjueerijat")
        elif c.testiosa.vastvorm_kood in (const.VASTVORM_KE, const.VASTVORM_SE):
            if item.tugiisik_kasutaja_id and item.tugiisik_kasutaja_id != c.user.id:
                # kasutaja pole tugiisik
                rc = False
                error = _("Sooritamiseks on vaja tugiisikut")
            elif not item.tugiisik_kasutaja_id and sooritaja.kasutaja_id != c.user.id:
                # kasutaja pole sooritaja
                rc = False
                error = _("Vale sooritaja")
            elif c.user.testpw_id and c.user.testpw_id != item.sooritaja_id:
                # testiparooliga kasutajal on vale test
                error = _("Testiparool pole selle testi jaoks")
                rc = False
            else:
                rc = True
        return rc, error

    def _check_reg(self, item, ta, testiruum):
        error = None
        rc = True

        on_seb = ta and ta.verif_seb and not item.luba_veriff
        if on_seb:
            if not self._check_seb(item):
                error = _("Testi sooritamiseks on vajalik Safe Exam Browser")
                rc = False
            # see on SEB, põhibrauser on regatud

        # kontrollime arvuti regamist
        if rc and not on_seb and testiruum:
            error = self._check_arvuti(item, testiruum)
            if error:
                rc = False
                arvuti_reg = testiruum.arvuti_reg
            else:
                arvuti_reg = False
            
        # kontrollime veriffi
        if rc and not on_seb and ta and ta.on_veriff:
            if c.user.verified_id:
                # jätame meelde, milline verifitseerimine lubas viimast seanssi alustada
                item.verifflog_id = c.user.verified_id                
            elif not item.luba_veriff:
                # veriff on vajalik ja erandit pole tehtud
                error = _("Enne sooritamist on vaja tõendada oma isik")
                rc = False

        return rc, error, on_seb

    def _check_sooritus(self, sooritus_id, testiosa_id):
        item = model.Sooritus.get(sooritus_id)
        if item and item.testiosa_id == testiosa_id:
            return item
    
    def _check_edit_permission(self):
        "Testi sooritamise õiguse kontroll kogu testilehe avamisel"
        c = self.c
        rc = error = item = None
        if self._is_allowed_tos(c.sooritus_id):
            # õigus on juba kontrollitud
            # klastris kontrollitakse veel, et õigus pole kadunud
            rc = True
            return rc, None
        elif not c.testiosa or not c.test:
            error = _("Testiosa puudub")
            rc = False
        elif not self._check_test_staatus():
            error = _("Test pole veel sooritamiseks valmis")
            self.error(error)
            rc = False
        else:
            self.prf()
            # kui õigust pole veel kontrollitud, siis teeme päringu andmebaasist
            item = self._check_sooritus(c.sooritus_id, c.testiosa_id)
            sooritaja = item and item.sooritaja
            if not item and c.preview:
                error = _("Eelvaade on aegunud")
                rc = False
            elif not item:
                error = _("Vale URL")
                rc = False
            else:
                c.sooritaja_id = item.sooritaja_id
                rc, error = self._check_vastvorm(item, sooritaja)

        if not error:
            ta = item.toimumisaeg
            testiruum = item.testiruum
            rc, error, on_seb = self._check_reg(item, ta, testiruum)
        if not rc:
            # õigus puudub
            # unustame õiguse, kui see peaks olema meeles
            if c.user.rm_allowed_tos(c.sooritus_id):
                msg = "Kustutatud sooritusluba {id}".format(id=c.sooritus_id)
                self.log_add(const.LOG_USER, msg, error)
            if error:
                self.error(error)
        elif self.request.method != 'POST' \
          and item.staatus != const.S_STAATUS_ALUSTAMATA \
          and not c.on_proctorio and not on_seb \
          and not c.alatest_id and not self.request.params.get('agm'):
            # õigus on olemas, aga selline päring pole lubatud
            # kui tuldi GET-meetodil, siis ei luba ja suuname kasutaja sinna, kus on link POST-meetodile
            # POST-päringuga eksamile tulek on vajalik selleks, et brauseris oleks tylikam hiljem back-nuppu kasutada
            # sest cache_control mõjub paremini POST päringutele
            # (get-päringu võimalus on vajalik selleks, et tulla siia peale eelmise alatesti salvestamist)
            error = 'Selline päring pole lubatud'
            rc = False
        else:
            # kui siia on jõudnud, siis on õiguste kontroll läbitud, jätame selle meelde
            # uuesti kontrollitakse siis, kui uuesti test avatakse            
            c.exapi_host = ExamSaga(self).init_klaster(item, sooritaja)
            self._set_allowed(item, sooritaja, ta, testiruum)
        self.prf()
        if error:
            log.error(error)
        return rc, item

    def _check_arvuti(self, sooritus, testiruum):
        c = self.c
        error = None
        toimumisaeg = self._get_toimumisaeg()
        if toimumisaeg and toimumisaeg.on_proctorio:
            # proctorio korral arvutite registreerimist ei kasutata
            return
        if toimumisaeg and toimumisaeg.verif_seb and sooritus.id == c.user.get_seb_id():
            # SEBi korral regatakse tavaline brauser, mitte SEB
            return
        if testiruum and (testiruum.arvuti_reg or (toimumisaeg and toimumisaeg.on_arvuti_reg)):
            # sooritaja arvuti peab olema registreeritud
            arvuti, error = model.Testiarvuti.get_by_request(c.test.id, testiruum, toimumisaeg, self.request)
            if not error:
                # cookie on olemas ja arvuti on olemas
                remote_addr = self.request.remote_addr
                vana_arvuti = sooritus.testiarvuti
                if vana_arvuti:
                    if vana_arvuti.id != arvuti.id:
                        error_param = 'vana arvuti %s (%s), uus %s (%s)' % \
                          (vana_arvuti and vana_arvuti.seq,
                           vana_arvuti and vana_arvuti.id or '-',
                           arvuti.seq,
                           arvuti.id)
                        error = _("Arvuti vahetamine pole lubatud")
                        log.error('%s %s' % (c.user.isikukood, error_param))
                    elif vana_arvuti.ip != remote_addr:
                        log.error('%s ip muutus %s > %s' % (c.user.isikukood, vana_arvuti.ip, remote_addr))
                        #error = _(u"Arvuti vahetamine pole lubatud")                        
                if not error and not sooritus.testiarvuti_id:
                    sooritus.testiarvuti_id = arvuti.id
                    sooritus.remote_addr = remote_addr
            
        return error

    def _get_tingimus(self, testiosa):
        c = self.c
        return {'arvuti_reg': c.arvuti_reg or False,
                'on_proctorio': c.on_proctorio or False,
                'lang': c.lang,
                'aeg_peatub': c.aeg_peatub or False,
                'piiraeg': testiosa.piiraeg,
                'algusaja_kontroll': c.algusaja_kontroll or False,
                'algus': c.testiruum_algus,
                'aja_jargi_alustatav': c.aja_jargi_alustatav,
                'alustamise_lopp': c.alustamise_lopp,
                'lopp': c.lopp,
                'vastvorm': testiosa.vastvorm_kood,
                }
            
    def update(self):
        """Testi katkestamine või lõpetamine.
        Siin toimub ainult oleku muutmine ja tulemuste arvutamine.
        Viimase ylesande vastused salvestatakse eelneva eraldi päringuga.
        (Tervesse aknasse postitav päring on eraldi seetõttu, et ylesande iframe seest
        otse top-aknasse postitades annaks brauser Leave site hoiatuse.)
        """
        c = self.c
        error = staatus = next_alatest_id = None

        sop = self.request.params.get('sop')
        # Tervesse aknasse postitatavad päringud soorituse oleku muutmiseks või testi avamiseks
        #  sop=exit - testi lõpetamine
        #  sop=endsub - alatesti lõpetamine
        #  sop=cnc - katkestamine
        #  sop=expire - testiosa piiraeg sai täis
        #  sop=expirety - viimase ylesande piiraeg sai täis
        #  sop=cnt - komplekti muutmine
        is_json = False        

        # uue komplekti ID või None
        try:
            uus_k_id = int(self.request.params.get('komplekt_id'))
        except Exception:
            uus_k_id = None
            
        # päritakse testi ja testiosa ja alatesti andmed
        error = self._get_test(uus_k_id)
        
        data = {'sop': sop,
                'alatestid': c.alatestid,
                'piiraeg': c.testiosa.piiraeg,
                'testiarvuti_id': c.testiarvuti_id,
                'alatest_id': c.alatest_id,
                'tingimus': self._get_tingimus(c.testiosa),
                'test': self._data_test(c.test),
                'testiosa': self._data_testiosa(c.testiosa),
                }
        if sop == 'cnt':
            # komplekti muutmine
            error, kv_id = self._check_uus_komplekt(uus_k_id)
            data['uus_komplekt_id'] = uus_k_id
            data['komplektivalik_id'] = kv_id
            
        if not error:
            r = ExamClient(self, c.exapi_host).update(c.sooritus_id, data)
            error = r.get('error')
            next_alatest_id = r.get('next_alatest_id')
            staatus = self._change_status(r)
                
        return self._after_save(error, staatus, next_alatest_id, sop)

    def _change_status(self, r):
        "edit või update korral muudetakse keskserveri staatus, kui see erineb eksamiserveri omast"
        c = self.c
        # staatus edit või update päringu vastusest
        staatus = r.get('staatus')
        oli_staatus = r.get('oli_staatus') # silumiseks
        data_staatus = c.allowed_data.get('staatus')
        
        # kysitluse URL, kui on vaja kysitlusele minna
        url_k = None

        if staatus and (data_staatus != staatus):
            # staatus muutus, muudame ka keskserveris
            # või lõppes testiväline kysitlus
            self._get_toimumisaeg()
            item = model.Sooritus.get(c.sooritus_id)
            sooritaja = item.sooritaja
            log.debug(f'{c.user.isikukood}: change_status {oli_staatus}/{data_staatus}/{staatus}/{item.staatus}')
            if staatus == const.S_STAATUS_TEHTUD and item.staatus != staatus:
                hiljem = c.arvutada_hiljem
                if not c.testivaline:
                    url_k = self._url_kysitlus(c.sooritus_id, False)
                    if url_k:
                        # kui kysitlus on ees, siis ei arvuta kohe tulemusi
                        # ja ei kustuta andmeid eksamiserverist
                        hiljem = True
                # märgime testi kohalikus serveris tehtuks ja tõmbame eksamiserverist andmed
                ExamSaga(self).from_examdb(c.exapi_host, item, sooritaja, c.test, c.testiosa, c.toimumisaeg, c.lang, hiljem)
            item.staatus = staatus
            item.sooritaja.update_staatus()
            model.Session.commit()

            # salvestame muudetud staatuse seansis
            c.allowed_data['staatus'] = staatus
            c.user.set_allowed_tos(c.sooritus_id, c.allowed_data)
            
            if url_k:
                # saadame kysitlusele vastama
                raise HTTPFound(location=url_k)
            
        return staatus
    
    def _check_uus_komplekt(self, uus_komplekt_id):
        c = self.c
        err = None
        kv_id = None
        if not c.komplekt_valitav:
            err = _("Komplekti ei saa muuta")
            log.error('Ei saa komplekti valida, kuna pole lubatud komplekti valida')
        elif c.ta_komplektid_id and uus_komplekt_id not in c.ta_komplektid_id:
            err = _("Komplekti ei saa muuta")
            log.error('Ei saa seda komplekti valida, kuna pole lubatud komplektide seas')
        if not err:
            # leiame komplektivaliku
            for k in c.komplektid:
                if k.id == uus_komplekt_id:
                    kv_id = k.komplektivalik_id
        return err, kv_id
    
    def _data_test(self, test):
        d = {'id': test.id,
             'on_tseis': test.on_tseis,
             'testiliik_kood': test.testiliik_kood,
             'testityyp': test.testityyp,
             }
        return d
    
    def _data_testiosa(self, testiosa):
        d = {'id': testiosa.id,
             'yhesuunaline': testiosa.yhesuunaline,
             }
        return d
    
    def showtask(self):
        "Ülesande kuvamine - ei kasutata sooritamisel, aga on kasutusel päritud klassides, kus käib vaatamine"
        c = self.c
        c.read_only = True
        ty_id = self.request.matchdict.get('ty_id')
        error, ty, vyy = self._get_test_ty(ty_id, False)
        if not error:
            c.ty = ty
            kv_id = c.alatest and c.alatest.komplektivalik_id or None
            sooritus = model.Sooritus.get(c.sooritus_id)
            komplekt_id = sooritus and sooritus.get_komplekt_id_by_kv(kv_id)
            if not komplekt_id:
                error = _("Ülesannet pole lahendatud")
        if error:
            self.error(error)
            return self.render_to_response(self._TASK_MSG_TEMPLATE)
        
        c.ylesandevastus = yv = sooritus.getq_ylesandevastus(ty_id, komplekt_id)
        if yv:
            c.responses = {kv.kood: kv for kv in yv.kysimusevastused}
            vy_id = yv.valitudylesanne_id
        else:
            c.responses = {}
            vy_id = None

        c.vy, c.ylesanne, c.correct_responses = self._get_vy(ty.id, vy_id, komplekt_id)

        # valikylesannete jaoks tekitame c.vyy
        c.vyy = [r for r in vyy if r.komplekt_id == komplekt_id]
        for r in c.vyy:
            r.id = r.vy_id

        show_y = True
        sooritaja = sooritus.sooritaja
        c.sooritaja_eesnimi = sooritaja.eesnimi        
        return self._gentask(yv=c.ylesandevastus,
                             pcorrect=c.test.oige_naitamine,
                             showres=show_y)

    def correct(self):
        "Õige vastuse vaatamine"
        c = self.c
        ty_id = int(self.request.matchdict.get('ty_id'))
        ylesanne_id = int(self.request.matchdict.get('task_id'))
        q = (model.SessionR.query(model.Ylesandevastus)
             .filter_by(sooritus_id=c.sooritus_id)
             .filter_by(testiylesanne_id=ty_id)
             .join((model.Valitudylesanne, model.Valitudylesanne.id==model.Ylesandevastus.valitudylesanne_id))
             .filter(model.Valitudylesanne.ylesanne_id==ylesanne_id))
        c.ylesandevastus = q.first()
        return EsitlusController.correct(self)
    
    def edittask(self):
        "Ülesande avamine"
        c = self.c

        try:
            # vaatame, kas on do_authorize() käigus meelde jäetud viga
            error = self.request.error
        except AttributeError:
            # ei olnud
            pass
        else:
            log.error(error)
            return Response(error)

        if c.read_only:
            # kasutatakse sooritamisel valitud vy
            vy_id = None
        else:
            # valikylesande valiku võimalus
            try:
                vy_id = int(self.request.params.get('vyid'))
            except:
                vy_id = None

        try:
            self.prf()
            ty_id = int(self.request.matchdict.get('ty_id'))
        except Exception as ex:
            log.error(ex)
            return Response(_('URLi viga'))

        return self._edittask(ty_id, vy_id)

    def _edittask(self, ty_id, vy_id):
        "Ülesande kuvamine vastamisel"
        c = self.c
        self.prf()
        error, ty, vyy = self._get_test_ty(ty_id, False)

        if not error:
            # teame, mis komplektivalik on,
            # aga ei tea veel, milline komplekt ja ylesanne sooritajal on
            kv_id = c.alatest and c.alatest.komplektivalik_id or None
            self.prf()
            # leitakse komplekt, ylesanne ja senised vastused
            try:
                r = ExamClient(self, c.exapi_host).edittask(c.sooritus_id, ty.id, vy_id, kv_id, vyy, c.alatest_id)
            except APIIntegrationError as ex:
                # siin pyytakse viga kinni, et ei väljastaks suurt lehte
                self._error(ex, 'ExamClient.edittask')
                error = _("Tehniline viga")
            else:
                error = r.get('error')
                
        if not error:
            c.ylesandevastus, c.responses = self.decode_yv(r)
            komplekt_id = r['komplekt_id']
            vy_id = r['vy_id']
            tos_st = r['sooritus_st']
            self.prf()

            # nyyd on teada komplekt ja ylesande ID, päritakse ylesande andmed
            vy, ylesanne, c.correct_responses = self._get_vy(ty.id, vy_id, komplekt_id)
            if not ylesanne:
                error = _("Ülesannet ei leitud")
        if error:
            srvdata = '<div id="error">%s</div>' % error 
            srvdata += '<div id="redirect">%s</div>' % self._url_quit(c.sooritus_id)
            html = f'<html><body class="jscmd"><script>is_response_dirty=false;dirty=false;</script>{srvdata}</body></html>'
            return Response(html)

        c.ylesanne = ylesanne
        self.prf()
        c.ty = ty
        c.vy = vy
        c.testivaline = tos_st == const.S_STAATUS_TEHTUD and c.alatest and c.alatest.testivaline or False
        self.prf()
        # valikylesannete jaoks tekitame c.vyy
        c.vyy = [r for r in vyy if r.komplekt_id == komplekt_id]
        for r in c.vyy:
            r.id = r.vy_id

        # sooritaja nimi alustekstis asendamiseks
        c.sooritaja_eesnimi = c.user.eesnimi
        
        # genereeritakse ekraanivorm
        # juhuarvudega ylesandes genereeritakse juhuarvud, kui veel polnud
        response = self._gentask(yv=c.ylesandevastus)
        if c.new_responses:
            # esimesel kuvamisel genereeriti juhuarvud ja valikute jrk
            # need tuleb salvestada vastustena
            self._save_new_random_responses(ylesanne.id, c.new_responses, ty, vy)
        self.prf()
        return response
    
    def _save_new_random_responses(self, ylesanne_id, new_responses, ty, vy):
        "Genereeritud juhuarvude salvestamine enne ylesande esimest avamist"
        c = self.c
        # testis lahendamine
        piiraeg = ty.piiraeg
        komplekt_id = vy.komplekt_id
        ty_id = ty.id
        vy_id = vy.id

        kysimusevastused = list(new_responses.values())
        temp_yv = MemYlesandevastus(sooritus_id=c.sooritus_id,
                                    ylesanne_id=ylesanne_id,
                                    alatest_id=c.alatest_id,
                                    tahis=ty.tahis,
                                    max_pallid=ty.max_pallid,
                                    vastuseta=False,
                                    finished=False,
                                    varparams={},
                                    kysimusevastused=kysimusevastused,
                                    sisuvaatamised=[],
                                    npvastused=[],
                                    piiraeg=None)
        sop = 'random'
        r, error = self._updatetask(sop, temp_yv, komplekt_id, ty_id, vy_id)
        return error
        
    def updatetask(self):
        "Ülesande vastuste salvestamine"
        c = self.c
        matchdict = self.request.matchdict
        error = None
        res_data = {}

        sop = self.request.params.get('sop')
        # AJAX päring ylesande yhe kysimuse salvestamiseks
        #  sop=file - audiofaili salvestamine
        # AJAX päringud ylesande vastuste salvestamiseks
        #  sop=auto - automaatne muudatuste salvestamine iga 60s tagant
        #  sop=chg  - faili salvestamine kohe peale faili muutmist
        #  sop=next[+n] - salvestamine ylesandelt lahkumisel
        #  sop=end  - alatesti või testi lõpetamine või katkestmaine (järgneb terve akna päring)

        try:
            # vaatame, kas on do_authorize() käigus meelde jäetud viga
            error = self.request.error
        except AttributeError:
            # ei olnud
            pass

        if not error:
            st = c.allowed_data.get('staatus')
            if st and st not in (const.S_STAATUS_ALUSTAMATA, const.S_STAATUS_POOLELI):
                # juhtub, kui sop=auto ja samal ajal lõpetati 
                log.debug(f'soorituse staatus {st}')
                error = ERROR_NA
        
        self.prf()
        if not error:
            # URLi põhjal leitakse ty ja vy
            vy_id = int(self.request.matchdict.get('vy_id'))
            ty_id = int(self.request.matchdict.get('ty_id'))
            vy, ylesanne, correct = self._get_vy(ty_id, vy_id, None)
            self.prf()
            error, ty, vyy = self._get_test_ty(ty_id, vy.komplekt_id)
            self.prf()

        if not error:
            
            form = Form(self.request, schema=forms.avalik.testid.TestilahendamineForm)
            form.validate()
            y_params = form.data

            # vastustest tehakse dict andmestruktuurile vastavatest objektidest
            mresponses, buf, yv_vastuseta, varparams = \
                BlockResponse(self).format_response(ylesanne, y_params, sop)
            responses = [kv for kv in mresponses.values()]
        
            log.debug('Ülesande %s vastused: %s' % (ylesanne.id, responses))
            if c.alatest:
                alatest_id = c.alatest.id
            else:
                alatest_id = None

            # kas kõik kohustuslikud kysimused vastati ära
            finished = self.request.params.get('finished')=='1'
            # ylesandevastuse objekt
            temp_yv = MemYlesandevastus(id=None,
                                        sooritus_id=c.sooritus_id,
                                        ylesanne_id=ylesanne.id,
                                        tahis=ty.tahis,
                                        max_pallid=ty.max_pallid,
                                        alatest_id=c.alatest_id,
                                        vastuseta=yv_vastuseta,
                                        finished=finished,
                                        varparams=varparams,
                                        kysimusevastused=responses,
                                        sisuvaatamised=[],
                                        npvastused=[],
                                        piiraeg=ty.piiraeg)

            # kas peab kohe midagi arvutama?
            on_diag, on_tagasiside = self._task_needs_calc(sop, ylesanne)

            # kui on juhuarvuga ylesanne ja vaja kohe arvutada tulemused,
            # siis peab kysima eksamiserverist vastused, et saada sooritajale genereeritud juhuarv
            vaja_ks = ylesanne.on_juhuarv and (on_diag or on_tagasiside)

            # kui oli faile, siis peab esmalt looma kirjed, et oleks ID
            # seejärel salvestatakse, tekib fileversion
            # hiljem salvestatakse klastris fileversion
            self._save_files(temp_yv, responses, vy.komplekt_id, ty.id, vy.id, vaja_ks)
            if on_diag or on_tagasiside:
                # tagasiside andmiseks peame kohe arvutama tulemuse
                f_locals = ExamSaga(self).calculate_yv(temp_yv, ylesanne, vy, ty, c.testiosa, c.lang) 

            # vastuse salvestamine klastris
            r, error = self._updatetask(sop, temp_yv, vy.komplekt_id, ty.id, vy.id)
            if r and r.errcode == 'NODATA':
                error = _("Test on katkestatud")
            elif error and sop == 'auto':
                # automaatse salvestamise viga ignoreerime,
                # sest enne selle käivitumist või kasutaja testi lõpetada
                error = ERROR_NA
                
            if on_diag or on_tagasiside:
                res_data = self._diagnose(temp_yv, ty.id, vy.id, f_locals, on_diag, ylesanne.normipunktid)

            # jagatud töös on midagi veel vaja teha
            if not error:
                ryv = r.ylesandevastus
                error = self._postupdatetask(sop, ryv)
            
        self.prf()
        return self._after_save_y(error, res_data, sop)

    def _task_needs_calc(self, sop, ylesanne):
        on_diag = on_tagasiside = False
        if sop == 'next':            
            # kas on d-test
            on_diag = self.c.test.diagnoosiv
            # korraga ei saa olla d-test ja tagasisidega ylesanne
            on_tagasiside = not on_diag and self._on_tagasiside(ylesanne)
        return on_diag, on_tagasiside

    def _postupdatetask(self, sop, ryv):
        pass
    
    def _save_files(self, temp_yv, responses, komplekt_id, ty_id, vy_id, vaja_ks):
        # failvastustega ylesandes peab genereerima kirjed, et saaks salvestada faile
        # juhuarvuga ylesandes peab kysima sooritajale varem genereeritud juhuarvu 
        c = self.c
        is_file = False
        # kontrollime, kas on failvastuseid
        for kv in responses:
            for ks in kv.kvsisud:
                if ks._unsaved_filedata:
                    is_file = True
                    break
        if not vaja_ks and not is_file:
            # pole vaja midagi teha
            return

        sop = self.request.params.get('sop')
        r, error = self._updatetask(sop, temp_yv, komplekt_id, ty_id, vy_id)
        if not error:
            # tekstvastused on salvestatud ja vastuste kirjete ID-d on olemas
            # salvestame failid ka
            yv = r.ylesandevastus
            kvastused2 = yv.kysimusevastused
            di_kvastused2 = {kv.kood: kv for kv in kvastused2}
            for kv in responses:
                for ks in kv.kvsisud:
                    filedata = ks._unsaved_filedata
                    if filedata:
                        kv2 = di_kvastused2.get(kv.kood)
                        for ks2 in kv2.kvsisud:
                            if ks2.seq == ks.seq:
                                ks.id = ks2.id
                                break
                        if ks.id:
                            # siin salvestatakse fail MinIOs
                            s3file_save('kvsisu', ks, filedata)

            # lisame juhuarvud omale
            for kv in kvastused2:
                if kv.sptyyp == const.BLOCK_RANDOM:
                    temp_yv.kysimusevastused.append(kv)
                            
    def _updatetask(self, sop, yv, komplekt_id, ty_id, vy_id):
        c = self.c
        params = self.request.params
        # Kui brauser kuvab uut ylesannet, siis muudab testiosa piiraja ja loob parameetri cdupd,
        # mille järgi saab server järgmisel vastuste salvestamisel aru, et piiraeg on brauseris muudetud.        
        try:
            cdupd = int(params.get('cdupd'))
        except:
            cdupd = None

        try:
            # ylesande laadimise ja salvestamise hetk brauseris
            loadtm = int(params.get('vbloadtm'))
            savetm = int(params.get('vbsavetm'))
        except:
            loadtm = savetm = 0

        # update andmed
        data = {'sop': sop,
                'alatestid': c.alatestid,
                'piiraeg': c.testiosa.piiraeg,
                'testiarvuti_id': c.testiarvuti_id,
                'alatest_id': c.alatest_id,
                'tingimus': self._get_tingimus(c.testiosa),
                'test': self._data_test(c.test),
                'testiosa': self._data_testiosa(c.testiosa),
                # updatetask andmed
                'loadtm': loadtm,
                'savetm': savetm,
                'cdupd': cdupd,
                'komplekt_id': komplekt_id,
                'ylesandevastus': yv,
                }
        # vastuste salvestamine
        r, error = ExamClient(self, c.exapi_host).updatetask(c.sooritus_id,
                                                             ty_id,
                                                             vy_id,
                                                             data)
        return r, error

    def _vy_grupid(self, ty_id, vy_id):
        "Leitakse teised ylesanded, mis on antud ylesandega samas grupis"
        c = self.c
        cl = TestClient(self)
        r = cl.vy_grupid(c.test_id, c.testiosa_id, ty_id, vy_id)
        return r

    def _calc_npts(self, npvastused):
        "Normipunktide väärtused on arvutatud, nende põhjal leitakse tagasiside"
        c = self.c
        cl = TestClient(self)
        r = cl.calc_npts(c.test_id, c.testiosa_id, npvastused)
        return r
    
    def _after_save_y(self, error, res_data, sop):
        c = self.c

        if error:
            res_data['error'] = error
            res_data['redirect'] = self._url_kysitlus(c.sooritus_id, True)
            self.set_log_error(error)
        
        is_json = self.request.params.get('datatype') == 'json'
        if not is_json:
            # tagastame HTML vormi
            jscmd = ''
            srvdata = ''
            if error:
                if error != ERROR_NA:
                    srvdata = '<div id="error">%s</div>' % error 
                srvdata += '<div id="redirect">%s</div>' % res_data['redirect']
            else:
                # leiame järgmise ylesande, kuhu minna
                if c.test.diagnoosiv:
                    # diagnoositud järgmine ylesanne või lineaarne või järgmine järjekorrast
                    n_ty_id = res_data.get('next_ty_id')
                elif sop == 'next':
                    # järgmine ylesanne brauserist
                    n_ty_id = self.request.params.get('n_ty_id')
                else:
                    n_ty_id = None
                
                if not n_ty_id and c.test.diagnoosiv:
                    # diagnoosivas testis pole kuhugi edasi minna
                    jscmd = 'top.end_diag_test();'
                elif not  n_ty_id:
                    # HTML vorm, aga puudub ylesanne, kuhu minna
                    jscmd = 'top.location="%s";' % self._url_quit(c.sooritus_id)
            if jscmd or srvdata:
                html = f'<html><body class="jscmd"><script>is_response_dirty=false;dirty=false;{jscmd}</script>{srvdata}</body></html>'
                return Response(html)
            # d-testi põhiylesande ID
            c.ptyid = res_data.get('ptyid') 
            return self._edittask(n_ty_id, None)
        else:
            # vorm ei vahetu, tagastame JSON
            # kontrollime erakorralise teadaande olemasolu
            modified, sisu = self.c.user.get_emergency(True)
            if modified:
                res_data['emergency'] = [modified, sisu]
            return Response(json_body=res_data)

    def _after_save(self, error, staatus, next_alatest_id, sop):
        c = self.c
        
        if error:
            self.error(error)
        if sop == 'cnt':
            # kasutaja valis teise komplekti
            return HTTPFound(location=self.url_current('edit', agm='k', rid=True))
        elif sop in ('exit','cnc') or staatus == const.S_STAATUS_TEHTUD:
            # katkestati või lõpetati, suuname testist välja
            if staatus == const.S_STAATUS_TEHTUD and not c.testivaline:
                # vaatame, kas on olemas testiväline küsitlus
                url = self._url_kysitlus(c.sooritus_id, True)
            else:
                url = self._url_quit(c.sooritus_id)

            # suuname testist välja
            return HTTPFound(location=url)
        else:
            # alatesti salvestamine nii, et testiosa sooritamise olek ei muutunud
            # leiame järgmise alatesti id
            next_alatest_id = self.request.params.get('next_alatest_id') or next_alatest_id
            if next_alatest_id:
                # järgmist alatesti sooritama
                return HTTPFound(location=self.url_current('edit', alatest_id=next_alatest_id, rid=True))
            else:
                # alatestide indeksisse, kui kõik alatestid on sooritatud
                return HTTPFound(location=self.url_current('edit', alatest_id='', agm='i', rid=True))

    def _url_kysitlus(self, sooritus_id, or_quit=True):
        "Kui kysitlus on veel sooritamata, siis tagastab kysitluse alatesti URLi"
        c = self.c
        # eelvaates sooritamisel võib sooritus vahepeal olla kustutatud
        if sooritus_id:
            # otsitakse viimase alatesti viimane ülesanne
            cl = TestClient(self)
            tv_alatest_id = cl.kysitlus_alatest(c.test_id, c.testiosa_id)
            if tv_alatest_id:
                st = ExamClient(self, c.exapi_host).alatest_staatus(c.sooritus_id, tv_alatest_id)
                if not st or st < const.S_STAATUS_TEHTUD:
                    # suuname testivälisele kysitlusele
                    return self.url_current('edit', alatest_id=tv_alatest_id, rid=True)
        if or_quit:
            return self._url_quit(sooritus_id)
        
    def _url_quit(self, sooritus_id):
        "URL, mida kasutatakse kasutaja testi sooritamiselt välja viimisel"
        c = self.c
        if c.on_intervjuu and c.toimumisaeg_id and c.test.avaldamistase != const.AVALIK_MAARATUD:
            # testimiskorraga suuline test
            return self.url('svastamine_vastajad', testiruum_id=c.testiruum_id)
        elif c.on_intervjuu:
            # testimiskorrata suuline test
            return self.url('testid_edit_labiviimine', test_id=c.test_id, id=c.testiruum_id)
        else:
            # kirjalik test
            if not c.sooritaja_id:
                item = model.Sooritus.getR(sooritus_id)
                c.sooritaja_id = item and item.sooritaja_id or 0
            return self.url('sooritamine_alustamine', test_id=c.test_id, sooritaja_id=c.sooritaja_id)

    def _on_tagasiside(self, ylesanne):
        "Kas on tagasisidega ylesanne yhesuunalises testis"
        c = self.c
        on_tagasiside = False
        if ylesanne.on_tagasiside and ylesanne.arvutihinnatav:
            yhesuunaline = c.testiosa.yhesuunaline
            if not yhesuunaline and c.alatest:
                yhesuunaline = c.alatest.yhesuunaline
            on_tagasiside = yhesuunaline
        return on_tagasiside
    
    def _diagnose(self, yv, ty_id, vy_id, y_locals, on_diag, y_normipunktid):
        """D-testi tagasiside koostamine peale ylesande vastamist (ainult d-testis)
        """
        c = self.c
        res_data = {}

        grupid = []
        grupid_id = []
        if on_diag:
            # leiame grupid, kuhu antud ylesanne kuulub
            for r in c.ylesandegrupid:
                # {grupp_id, max_pallid, vyy_id}
                if vy_id in r.vyy_id:
                    grupid.append(r)
                    grupid_id.append(r.grupp_id)

            # nende gruppide ja selle ylesande normipunktid
            normipunktid = [np for np in c.normipunktid if \
                            (np.testiylesanne_id==ty_id or \
                             np.ylesandegrupp_id in grupid_id)]
        else:
            # tagasisidega ylesanne
            normipunktid = y_normipunktid
            
        # arvutatakse np väärtused
        npvastused = ExamClient(self, c.exapi_host)\
            .diagnose(c.sooritus_id, vy_id, normipunktid, grupid, c.task_map)

        #txt, jatka = npc.calc_ylesanne_tagasiside(yv, ylesanne, c.lang, True)
        def get_ns(np_id, ns_id):
            if np_id and ns_id:
                for np in normipunktid:
                    if np.id == np_id:
                        for ns in np.nptagasisided:
                            if ns.id == ns_id:
                                return ns
                
        res_data = {}
        for npv in npvastused:
            ns = get_ns(npv.normipunkt_id, npv.nptagasiside_id)
            if ns:
                if on_diag:
                    next_ty_id = ns.uus_testiylesanne_id
                    if next_ty_id:
                        res_data['next_ty_id'] = next_ty_id
                        break
                else:
                    res_data['tagasiside'] = ns.tagasiside
                    res_data['jatka'] = ns.jatka

        if on_diag:
            # kui ei diagnoositud, siis võetakse järjekorrast
            self._get_next_ty_id(res_data, ty_id)
        log.debug(f'DIAG:' + str(res_data))
        return res_data
    
    def _get_next_ty_id(self, diag_data, ty_id):
        c = self.c
        # diagnoositud jrgm yl (võib-olla on, võib-olla pole)
        next_ty_id = diag_data.get('next_ty_id')
        # põhiylesande ID, mille juures oleme
        ptyid = self.request.params.get('ptyid')
        if c.is_linear:
            # lineaarse eelvaate korral ei järgita diagnoosi
            next_ty_id = self.request.params.get('n_ty_id')
            log.debug('lineaarne jrgm yl %s' % next_ty_id)
        elif next_ty_id:
            log.debug('diagnoositud jrgm yl %s' % next_ty_id)
            # jätame meelde põhiylesande ID (kui jätkuylesanded läbi saavad,
            # siis jätkub sooritamine põhiylesande asukohast testi struktuuris)
            diag_data['ptyid'] = ptyid or ty_id
        else:
            # kui diagnoos ei määranud järgmist ylesannet, 
            # siis võtame järgmise ylesande järjekorrast
            # (mitte-jätkuylesannete seast)
            cl = TestClient(self)
            next_ty_id = cl.get_next_ty_id(c.test_id, c.testiosa_id, ptyid or ty_id)
            log.debug('jrk jrgm yl %s' % next_ty_id)
        diag_data['next_ty_id'] = next_ty_id

    def _get_toimumisaeg(self):
        c = self.c
        self.prf()
        if not c.toimumisaeg and c.toimumisaeg_id:
            c.toimumisaeg = model.Toimumisaeg.get(c.toimumisaeg_id)
            self.prf()
        return c.toimumisaeg

    def _get_test(self, komplekt_id=None, ty_id=None):
        "Testi andmete päring"
        c = self.c
        error = None
        cl = TestClient(self)
        try:
            e_komplekt_id = int(c.e_komplekt_id)
        except Exception as ex:
            # väärtuseta või L (lineaarne)
            e_komplekt_id = None

        r = cl.get_test(c.test_id, c.testiosa_id, c.alatest_id, komplekt_id, c.lang, ty_id, e_komplekt_id, bool(c.preview))
        error = r.get('error')
        if r.get('errcode') == 'STRUCT':
            # testi struktuur on muutunud
            error = _("Testi on muudetud, palun alusta uuesti")
        if error:
            if not ty_id:
                return error
            else:
                return error, None, None

        c.test = r.test
        c.testiosa = r.testiosa
        c.mitu_osa = r.mitu_osa > 1
        
        # kui komplekt on teada, siis saab alatestide andmetest
        # selle komplekti valitudylesanded
        # kui komplekt ei ole teada, siis on vaja alatestide infot selleks,
        # et leida komplektivalikusse kuuluvad alatestid
        c.alatestid = r.alatestid
        if not ty_id:
            # leiame alatesti
            c.alatest = ''
            if c.alatest_id:
                for r1 in r.alatestid:
                    if r1.id == c.alatest_id:
                        c.alatest = r1
                        break
            c.alatest_id = c.alatest and c.alatest.id or None

            # kõik komplektid
            if c.ta_komplektid_id:
                # toimumisajal lubatud komplektid
                c.komplektid = [k for k in r.komplektid if k.id in c.ta_komplektid_id]
            else:
                # kõik komplektid
                c.komplektid = r.komplektid
        else:
            if c.test.diagnoosiv:
                # [(grupp_id, max_p, vyy_id)]
                c.ylesandegrupid = r.ylesandegrupid
                # [np]
                c.normipunktid = r.normipunktid
                c.task_map = r.task_map
            ty = r.ty
            vyy = r.vyy
            
            # leiame alatesti
            c.alatest = ''
            c.alatest_id = None
            if ty.alatest_id:
                for r1 in r.alatestid:
                    if r1.id == ty.alatest_id:
                        c.alatest = r1
                        c.alatest_id = r1.id
            return None, ty, vyy

    def _get_test_ty(self, ty_id, komplekt_id):
        "Testi ja ülesande andmete päring (edittask/updatetask)"
        return self._get_test(komplekt_id, ty_id)

    def _get_vy(self, ty_id, vy_id, komplekt_id):
        c = self.c
        vy, ylesanne, correct = TestClient(self).get_valitudylesanne(c.test_id, c.testiosa_id, ty_id, vy_id, komplekt_id, c.lang)
        return vy, ylesanne, correct

    def _get_gruppide_normipunktid(self, grupid_id):
        c = self.c
        normipunktid = TestClient(self).normipunktid(c.test_id, c.testiosa_id, grupid_id)
        return normipunktid
    
    def __before__(self):
        """Väärtustame testimiskorra id
        """
        c = self.c
        self.prf()
        c.test_id = int(self.request.matchdict.get('test_id'))
        try:
            c.testiosa_id = int(self.request.matchdict.get('testiosa_id'))
        except:
            c.testiosa_id = ''
        c.log_testiosa_id = c.testiosa_id        
        c.sooritus_id = self.convert_id(self.request.matchdict.get('id'))
        self.prf()
        try:
            c.alatest_id = int(self.request.matchdict.get('alatest_id'))
        except:
            c.alatest_id = ''
        BaseResourceController.__before__(self)
        
    def _log_params_end(self):
        # testi sooritamisel lisame logisse ka testi ID
        c = self.c
        testiosa_id = None
        if c.is_edit or c.action in ('edittask','updatetask'):
            testiosa_id = c.log_testiosa_id or None
        super()._log_params_end(testiosa_id=testiosa_id)
        
    def _has_permission(self):
        c = self.c
        action = c.action
        if action in ('create', 'alusta', 'jatka', 'edit'):
            return True # kontroll toimub meetodi sees
        else:
            return self._is_allowed_tos(c.sooritus_id)

    def _do_authorize(self):
        "Kasutaja autoriseerimise kontroll"
        # vajalikud eelnevad tegevused
        self.__before__()
        # kontrollime õigusi
        is_authenticated = self.c.user.is_authenticated
        rc = is_authenticated and self._has_permission()
        if not rc:
            if self.c.action in ('edittask','updatetask'):
                # viga jäetakse meelde ja käsitletakse hiljem meetodi sees
                if not is_authenticated:
                    self.request.error = _("Kasutaja on vahepeal välja logitud!")
                else:
                    self.request.error = _("Testi ei saa sooritada!")
                return
                
            # muul juhul visatakse erind
            self._raise_not_authorized(is_authenticated)
        
    def _is_allowed_tos(self, sooritus_id):
        "Kontrollitakse, kas on ligipääsuõigus"
        c = self.c
        data = c.user.is_allowed_tos(sooritus_id)
        if data:
            # õigus eelnevalt meeles

            # õiguse versiooni kontroll
            if data['ver'] < ALLOWED_VER:
                return False
            c.allowed_data = data
            vastvorm = data['vastvorm']
            c.kursus_nimi = data['kursus_nimi']
            c.sooritaja_id = data['sooritaja_id']
            c.sooritaja_nimi = data['sooritaja_nimi']
            c.arvuti_reg = data['arvuti_reg']
            c.lang = data['sooritaja_lang']
            c.on_proctorio = data['on_proctorio']
            c.exapi_host = data['exapi_host']
            c.testiarvuti_id = data['testiarvuti_id']
            c.toimumisaeg_id = data['toimumisaeg_id']
            c.testiruum_id = data['testiruum_id']
            c.on_tugiisik = data['on_tugiisik']
            c.on_katse = data['on_katse']
            c.komplekt_valitav = data['komplekt_valitav']
            c.ta_komplekt_valitav_y1 = data['komplekt_valitav_y1']
            c.ta_komplektid_id = data['ta_komplektid_id']
            c.aeg_peatub = data['aeg_peatub']
            c.algusaja_kontroll = data['ta_algusaja_kontroll']
            c.testiruum_algus = data['testiruum_algus']
            c.aja_jargi_alustatav = data['aja_jargi_alustatav']
            c.alustamise_lopp = data['alustamise_lopp']
            c.lopp = data['lopp']
            c.arvutada_hiljem = data['arvutada_hiljem']
            c.tulemus_avaldet = data['tulemus_avaldet']
            ui_lang = data['ui_lang']
            c.on_intervjuu = vastvorm == const.VASTVORM_I
            log.debug(f'is_allowed host={c.exapi_host}/{data}')
            if ui_lang:
                # sooritamise ajal peab kasutama soorituskeelset kasutajaliidest
                self.request._LOCALE_ = c.lang
                self._set_locale()
            return True
        else:
            return False

    def _set_allowed(self, item, sooritaja, ta, testiruum):
        "Testi sooritamise õiguse meelde jätmine"
        c = self.c
        arvuti_reg = ta and ta.on_arvuti_reg and \
                not (ta.on_proctorio or ta.verif_seb)
        on_proctorio = ta and ta.on_proctorio
        lopp = testiruum and testiruum.lopp
        aeg_peatub = c.testiosa.aeg_peatub or False
        aja_jargi_alustatav = alustamise_lopp = None
        if ta:
            aja_jargi_alustatav = ta.aja_jargi_alustatav
        elif testiruum:
            aja_jargi_alustatav = testiruum.aja_jargi_alustatav
        if testiruum:
            if testiruum.algus:
                alustamise_lopp = testiruum.alustamise_lopp
            else:
                tpaev = testiruum.toimumispaev
                if tpaev:
                    alustamise_lopp = tpaev.alustamise_lopp

        ta_komplektid_id = None
        if ta:
            komplekt_valitav = ta.komplekt_valitav
            komplekt_valitav_y1 = ta.komplekt_valitav_y1
            # toimumisajal lubatud komplektid
            q = (model.Session.query(model.Toimumisaeg_komplekt.komplekt_id)
                 .filter_by(toimumisaeg_id=ta.id))
            ta_komplektid_id = [k_id for k_id, in q.all()]
        elif c.test.testiliik_kood == const.TESTILIIK_KUTSE:
            komplekt_valitav = False
            komplekt_valitav_y1 = False
        else:
            komplekt_valitav = True
            komplekt_valitav_y1 = True

        tkord = ta and ta.testimiskord
        arvutada_hiljem = tkord and tkord.arvutada_hiljem or False
        on_katse = tkord and tkord.tahis == 'KATSE'
        # kas d-testi lõpus kuvada "Vaata tagasisidet"
        tulemus_avaldet = not tkord or tkord.koondtulemus_avaldet
        data = {'ver': ALLOWED_VER,
                'staatus': item.staatus,
                'vastvorm': c.testiosa.vastvorm_kood,
                'kursus_nimi': sooritaja.kursus_nimi,
                'sooritaja_id': sooritaja.id,
                'sooritaja_nimi': sooritaja.nimi,
                'sooritaja_lang': sooritaja.lang,
                'arvuti_reg': arvuti_reg,
                'on_proctorio': on_proctorio,
                'exapi_host': c.exapi_host,
                'testiarvuti_id': item.testiarvuti_id,
                'toimumisaeg_id': item.toimumisaeg_id,
                'testiruum_id': item.testiruum_id,
                'on_tugiisik': item.tugiisik_kasutaja_id,
                'on_katse': on_katse,
                'komplekt_valitav': komplekt_valitav,
                'komplekt_valitav_y1': komplekt_valitav_y1,
                'ta_komplektid_id': ta_komplektid_id,
                'aeg_peatub': c.testiosa.aeg_peatub or False,
                'ta_algusaja_kontroll': ta and ta.algusaja_kontroll or False,
                'testiruum_algus': testiruum and testiruum.algus,
                'aja_jargi_alustatav': aja_jargi_alustatav,
                'alustamise_lopp': alustamise_lopp,
                'lopp': lopp,
                'arvutada_hiljem': arvutada_hiljem,
                'tulemus_avaldet': tulemus_avaldet,
                'ui_lang': c.test.ui_lang,
                }
        if c.test.ui_lang:
            # sooritamise ajal peab kasutama soorituskeelset kasutajaliidest
            self.request._LOCALE_ = sooritaja.lang
            self._set_locale()
        c.user.set_allowed_tos(item.id, data)
        self._is_allowed_tos(item.id)
       
    def _check_seb(self, sooritus):
        "Kontrollitakse, kas kasutajal on SEB"
        return self.c.user.get_seb_id() == sooritus.id
        
    def convert_id(self, value_id, on_esitlus=False):
        "Jätame välja url_key"
        # id võimalikud kujud:
        # T\d+ - koormustesti soorituse ID 
        # \d+ - soorituse ID
        # \d+\.[a-z0-9]+ - soorituse ID, punkt ja Proctorio url_key
        if value_id:
            value_id = value_id.split('-')[0]
            return super().convert_id(value_id)

    def get_testiylesanded(self, komplekt_id):
        # leiame kuvatavad ylesanded (show?)
        c = self.c
        error = None
        # pärime ylesannete loetelu
        hk_id = c.hindamiskogum and c.hindamiskogum.id or None
        if not komplekt_id:
            log.error('puudub komplekt_id!')
            error = _("Komplekt puudub")
            return error, [], {}, None
        testiylesanded = TestClient(self).get_testiylesanded(c.test_id, c.testiosa_id, c.alatest_id, komplekt_id, hk_id, c.ignore_ty_id, c.lang)
        
        li_testiylesanded = [{'id': ty.id,
                              'liik': ty.liik} for ty in testiylesanded]
        d_testiylesanded = {ty.id: ty for ty in testiylesanded}

        # leiame personaalse ylesannete järjekorra ja sooritamise järje
        if c.read_only and not c.sooritus.klastrist_toomata:
            # andmed on keskserveris olemas
            # tehtud töö vaatamine või jagatud töö vaatamine (jagatud töö võib ka pooleli olla)
            if c.sooritus.valikujrk:
                # kasutame segamisjärjekorda
                def _sortfunc(ty):
                    try:
                        return jrk.index(ty.id)
                    except ValueError:
                        return 0
                    testiylesanded.sort(key=_sortfunc)

            # d-testis jätame alles ainult vastusega ylesanded
            if not c.is_linear and c.test.diagnoosiv:
                li = []
                for ty in testiylesanded:
                    yv = c.sooritus.get_ylesandevastus(ty.id, komplekt_id)
                    if yv:
                        li.append(ty)
                testiylesanded = li

            segatud_tyy_id = [ty.id for ty in testiylesanded]

            c.ylesandevastused = {}
            q = (model.SessionR.query(model.Ylesandevastus)
                 .filter_by(sooritus_id=c.sooritus.id)
                 .filter(model.Ylesandevastus.testiylesanne_id.in_(segatud_tyy_id))
                 )
            for yv in q.all():
                c.ylesandevastused[yv.testiylesanne_id] = yv
                
        else:
            # vajadusel järjestatakse
            # ja tehtud soorituses leitakse tehtud ylesanded
            # ja viimane vaadatud testiylesanne
            error, segatud_tyy_id, viimane_ty_id, viimane_vy_id, li_yv = ExamClient(self, c.exapi_host).testiylesanded(c.sooritus_id, c.alatest_id, li_testiylesanded, c.testiosa.yl_segamini, c.read_only)
            c.ylesandevastused = {r.testiylesanne_id: r for r in li_yv}

        if not error:
            if c.read_only and segatud_tyy_id:
                viimane_ty_id = segatud_tyy_id[0]

            testiylesanded = []
            sooritusjrk = {}
            jrk = 0 
            current_ty = None
            for ty_id in segatud_tyy_id:
                ty = d_testiylesanded.get(ty_id)
                if not ty.on_jatk or c.is_linear or c.read_only:
                    testiylesanded.append(ty)
                    if c.testiosa.yl_segamini:
                        # ylesannete segamisel genereerime uued tähised
                        tahis, jrk = model.gen_ty_tahis(ty, c.alatest, jrk, c.testiosa.yl_jrk_alatestiti)
                        sooritusjrk[ty.id] = tahis

                if viimane_ty_id == ty.id:
                    current_ty = ty

            # viimane vaadatud ylesanne
            if not current_ty and testiylesanded:
                current_ty = testiylesanded[0]
            log.debug(f'TESTIYLESANDED: {len(testiylesanded)} {testiylesanded}\nc_ty={current_ty}')
        if error:
            return error, None, None, None
        else:
            return None, testiylesanded, sooritusjrk, current_ty
        
    def _komplektid(self):
        # kui muidu on lubatud komplekti valida, siis kas praegu ka saab valida
        c = self.c
        if not c.komplektid:
            err = _("Ülesandekomplekte pole")
            self.error(err)
            raise HTTPFound(location=self._url_quit(c.sooritus_id))

        valitav = c.komplekt_valitav \
            and not (c.testiosa.on_alatestid and (not c.alatest or c.alatest.testivaline))
        c.y1alatest1_id = None
                
        if c.alatest:
            # antud alatesti komplektivalik
            kv_id = c.alatest.komplektivalik_id
        elif c.alatestid:
            # alatestidega test, kus alatesti pole valitud
            c.opt_komplekt = []
            return False
        else:
            # alatestideta test, kus on ainult yks komplektivalik
            kv_id = c.komplektid[0].komplektivalik_id

        # komplektide valikuvälja sisu
        c.opt_komplekt = [(k.id, k.tahis) for k in c.komplektid if k.komplektivalik_id == kv_id]

        if not c.opt_komplekt:
            err = _("Ülesandekomplekte pole määratud")
            self.error(err)
            raise HTTPFound(location=self._url_quit(c.sooritus_id))
            
        if not c.komplekt_id:

            # komplekti pole veel määratud, määrame komplekti
            komplektid_id = [r[0] for r in c.opt_komplekt]
            c.komplekt_id = ExamClient(self, c.exapi_host).give_komplekt(c.sooritus_id, kv_id, valitav, komplektid_id)

            # märgime komplekti lukustatuks
            if not c.preview:
                lukus = c.on_katse and const.LUKUS_KATSE_SOORITATUD or const.LUKUS_SOORITATUD
                TestClient(self).lukusta_komplekt(c.test_id, c.testiosa_id, c.komplekt_id, lukus)

        # täpsustame, kas lahendaja võib ise komplekti valida
        if valitav:
            if len(c.opt_komplekt) <= 1:
                # pole millegi seast valida
                valitav = False
            else:
                # kas varianti võib valida ainult variandi esimesel ylesandel olles?
                on_y1 = c.ta_komplekt_valitav_y1 or c.testiosa.yhesuunaline or c.alatest and c.alatest.yhesuunaline
                # leitakse sama komplekti kõik alatestid    
                if c.alatestid:
                    c.teised_alatestid = []
                    for alatest in c.alatestid:
                        if alatest.komplektivalik_id == kv_id:
                            if on_y1 and not c.y1alatest1_id:
                                c.y1alatest1_id =  alatest.id
                            if alatest.id != c.alatest_id:
                                # kas alatesti on alustatud?
                                a2 = c.alatestisooritused.get(alatest.id)
                                if a2 and a2.staatus in (const.S_STAATUS_POOLELI, const.S_STAATUS_TEHTUD):
                                    if alatest.yhesuunaline or alatest.on_yhekordne:
                                        # komplekt sisaldab tehtud alatesti, mida ei saa uuesti teha
                                        valitav = False
                                        break
                                    # jätame meelde, millised alatestid on vaja uuesti sooritada, kui komplekti muudetakse
                                    c.teised_alatestid.append(alatest.tran(c.lang).nimi)

        return valitav
