from eis.lib.baseresource import *
_ = i18n._
from eis.lib.block import BlockController
from eis.lib.blockcalc import BlockCalc
from eis.lib.blockresponse import BlockResponse
from eis.handlers.avalik.lahendamine.esitlus import EsitlusController
from eis.s3file import s3file_save
from eiscore.recordwrapper import RecordWrapper
from eiscore.examwrapper import MemYlesandevastus, MemKV, MemKS
from eis.lib.examclient import ExamClient
log = logging.getLogger(__name__)

class TooylesandedController(BaseResourceController, EsitlusController):
    # lahendamine.py eeskujul
    _MODEL = model.Valitudylesanne
    _INDEX_TEMPLATE = 'avalik/sooritamine/tooylesanded.mako'
    _EDIT_TEMPLATE = 'avalik/sooritamine/tooylesanne.mako'    
    _TASK_TEMPLATE = '/avalik/sooritamine/tooylesanne.esitlus.mako'
    _actions = 'index,edit,show,update'

    def _index_d(self):
        c = self.c
        c.testiylesanded = list(c.testiosa.testiylesanded)
        if c.sooritaja.klaster_id:
            self._give_klaster()
            c.pooleli_tyy_id = ExamClient(self, c.exapi_host).pooleli_toovastused(c.sooritus.id)        
        return self.response_dict
       
    def correct(self):
        c = self.c
        self._get_toovastus_id()            
            
        return super().correct()

    def _show_d(self):
        c = self.c
        id = self.request.matchdict.get('id')
        if not c.vy:
            self.error(_("Ülesannet ei leitud!"))
            return self._redirect('index')
        self._show(c.vy)

        return self.response_dict

    def _edit_d(self):
        "Ülesande ümbritsev osa"
        c = self.c
        if not c.vy:
            self.error(_("Ülesannet ei leitud!"))
            return self._redirect('index')

        self._edit(c.vy)

        return self.response_dict

    def _edit(self, item):
        c = self.c
        today = date.today()
        if (not c.nimekiri.alates or c.nimekiri.alates <= today) and \
           (not c.nimekiri.kuni or c.nimekiri.kuni >= today):
            c.url_try = self.url_current('edit', id=c.vy.id)

    def edittask(self):
        c = self.c

        # leitakse senised vastused
        if c.read_only:
            # kuvame antud vastust
            c.ylesandevastus = c.sooritus.get_ylesandevastus(c.ty.id)
            c.responses = {kv.kood: kv for kv in c.ylesandevastus.kysimusevastused}
        else:
            # lahendame
            r = self._edit_toovastus()        
            c.ylesandevastus, c.responses = self.decode_yv(r)
        c.yv_id = c.ylesandevastus.id
        
        c.correct_responses = c.ylesanne.correct_responses(None,
                                                           lang=c.lang,
                                                           naide_only=True,
                                                           hindaja=False,
                                                           naidistega=False,
                                                           as_tip=True)
        response = self._gentask(yv=c.ylesandevastus, pcorrect=c.read_only)
        if c.new_responses and not c.read_only:
            # esimesel kuvamisel genereeriti juhuarvud,
            # need tuleb salvestada vastustena
            self._save_new_random_responses(c.ylesanne.id, c.new_responses, None, None)

        self._onedittask()            
        return response

    def _save_new_random_responses(self, ylesanne_id, new_responses, ty, vy):
        "Genereeritud juhuarvude salvestamine enne ylesande esimest avamist"
        c = self.c
        # ilma testita lahendamine
        piiraeg = komplekt_id = ty_id = vy_id = None

        kysimusevastused = list(new_responses.values())
        temp_yv = MemYlesandevastus(id=c.yv_id,
                                    sooritus_id=None,
                                    ylesanne_id=ylesanne_id,
                                    alatest_id=None,
                                    tahis=None,
                                    max_pallid=None,
                                    vastuseta=False,
                                    finished=False,
                                    varparams=[],
                                    kysimusevastused=kysimusevastused,
                                    sisuvaatamised=[],
                                    npvastused=[],
                                    piiraeg=None)
        sop = 'random'
        r, error = self._updatetask(sop, temp_yv)
        return error
    
    def showtask(self):
        c = self.c
        c.read_only = True
        # lehe uuendamise URL (krati korral, ilma testita lahendamisel)
        yv_id = self.request.params.get('yv_id')        
        c.refresh_showtask_url = self.h.url_current('showtask', lang=c.lang, yv_id=yv_id, kl_id=c.klaster_id)
        return self.edittask()
    
    def updatetask(self):
        """Lahendaja salvestab oma vastuse
        """
        c = self.c
        id = self.request.matchdict.get('id')
        params = self.request.params.mixed()
        sop = params.get('sop')
        # sop: file, endtask
        self._get_toovastus_id()
        
        form = Form(self.request, schema=forms.avalik.testid.TestilahendamineForm)
        form.validate()
        y_params = form.data
        ylesanne = c.ylesanne
        blockresponse = BlockResponse(self)
        mresponses, buf, yv_vastuseta, varparams = blockresponse.format_response(ylesanne, y_params, sop)
        responses = [kv for kv in mresponses.values()]

        # kas kõik kohustuslikud kysimused vastati ära
        finished = self.request.params.get('finished')=='1'       
        temp_yv = MemYlesandevastus(id=c.yv_id,
                                    sooritus_id=None,
                                    ylesanne_id=ylesanne.id,
                                    alatest_id=None,
                                    tahis=None,
                                    max_pallid=None,
                                    vastuseta=yv_vastuseta,
                                    finished=finished,
                                    varparams=varparams,
                                    kysimusevastused=responses,
                                    sisuvaatamised=[],
                                    npvastused=[],
                                    piiraeg=None)
        
        log.debug('Ülesande %s vastused: %s' % (ylesanne.id, mresponses))

        r = error = None
        item = c.ylesanne

        # kui oli faile, siis peab esmalt looma kirjed, et oleks ID
        # seejärel salvestatakse, tekib fileversion
        # hiljem salvestatakse klastris fileversion
        self._save_files(temp_yv, responses)
        r, error = self._updatetask(sop, temp_yv)        
        if r and r.errcode == 'NODATA':
            # sop=auto korral samal ajal jõuti kirje kustutada, kõik on korras
            error = 'NA'

        if sop == 'file':
            res = {'rc': 'ok'}
            return Response(json_body=res)
        if not error:
            self._postupdatetask(sop, r)
        return self._after_save(error, {}, sop)

    def _updatetask(self, sop, yv):
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
        komplekt_id = None
        # update andmed
        data = {'sop': sop,
                'alatestid': [],
                'piiraeg': None,
                'testiarvuti_id': None,
                'alatest_id': None,
                'tingimus': None,
                'test': None,
                'testiosa': None,
                # updatetask andmed
                'loadtm': loadtm,
                'savetm': savetm,
                'cdupd': cdupd,
                'komplekt_id': None,
                'ylesandevastus': yv,
                }
        # vastuste salvestamine
        
        sooritus_id = ty_id = vy_id = 0
        #try:
        r, error = ExamClient(self, c.exapi_host).updatetask(sooritus_id,
                                                                 ty_id,
                                                                 vy_id,
                                                                 data)
        return r, error
    
    def _save_files(self, temp_yv, responses):
        # peab genereerima kirjed, et saaks salvestada faile        
        c = self.c

        is_file = False
        for kv in responses:
            for ks in kv.kvsisud:
                if ks._unsaved_filedata:
                    is_file = True
                    break
        if not is_file:
            # pole vaja midagi teha
            return

        sop = self.request.params.get('sop')
        r, error = self._updatetask(sop, temp_yv)
        if not error:
            # tekstvastused on salvestatud ja vastuste kirjete ID-d on olemas
            # salvestame failid ka
            kvastused2 = r['ylesandevastus']['kysimusevastused']
            di_kvastused2 = {kv['kood']: kv for kv in kvastused2}
            for kv in responses:
                for ks in kv.kvsisud:
                    filedata = ks._unsaved_filedata
                    if filedata:
                        kv2 = di_kvastused2.get(kv.kood)
                        for ks2 in kv2['kvsisud']:
                            if ks2['seq'] == ks.seq:
                                ks.id = ks2['id']
                                break
                        if ks.id:
                            # siin salvestatakse fail MinIOs
                            s3file_save('kvsisu', ks, filedata)
    
    def _after_save(self, error, res_data, sop):
        c = self.c
        is_json = self.request.params.get('datatype') == 'json'
        if is_json:
            # vorm ei vahetu
            if error:
                res_data['error'] = error
            if sop == 'cnctask':
                # katkestati, suuname ülesandest välja
                res_data['redirect_top'] = self.url_current('index')
            return Response(json_body=res_data)

        else:
            # lõpetati, kuvame vastust
            if error and error != 'NA':
                self.error(error)
            # kuvame vastuse, nagu avaliku ylesande lahendamisel
            return self.showtask()
    

    ########### testi soorituse muutmine 
    
    def _onedittask(self):
        "Soorituse oleku muutmine ülesande avamisel"
        c = self.c
        self._set_testiosa_aeg(c.sooritus)
        self._set_komplekt(c.sooritus)
        if c.sooritus.staatus != const.S_STAATUS_TEHTUD:
            c.sooritus.staatus = const.S_STAATUS_POOLELI
        now = datetime.now()
        if not c.sooritus.algus:
            c.sooritus.algus = now
        if not c.preview:
            if not c.sooritaja.algus:
                c.sooritaja.algus = now
            c.sooritaja.update_staatus()
        c.sooritus.autentimine = c.user.auth_type
        c.sooritus.remote_addr = self.request.environ.get('REMOTE_ADDR')
        model.Session.commit()

    def _set_testiosa_aeg(self, item):
        "Testiosa ajakontroll"
        c = self.c
        now = datetime.now()
        if item.algus and not item.seansi_algus:
            log.error('sooritus %s: algus=%s, seansi_algus puudub' % (item.id, item.algus))
            item.algus = None
        if item.staatus in (const.S_STAATUS_ALUSTAMATA, const.S_STAATUS_KATKESTATUD):
            item.seansi_algus = now

        if item.algus:
            ajakulu = _calc_ajakulu(now, item.algus)

            if item.peatus_algus:
                viimane_peatus = _calc_ajakulu(now, item.peatus_algus)
                item.peatatud_aeg = (item.peatatud_aeg or 0) + viimane_peatus
                item.peatus_algus = None
                #log.info('%s peatatud %ss' % (item.id, viimane_peatus))

            if c.testiosa.aeg_peatub and item.peatatud_aeg:
                ajakulu = max(0, ajakulu - item.peatatud_aeg)

            piiraeg = item.piiraeg
            if piiraeg and piiraeg < ajakulu:
                item.lopp = now
                if not item.ajakulu:
                    item.ajakulu = piiraeg
                item.set_staatus(const.S_STAATUS_TEHTUD)
                if not c.preview:
                    c.sooritaja.staatus = const.S_STAATUS_TEHTUD
                model.Session.commit()
                self.error(_("Sooritamise piiraeg on täis saanud"))
                raise HTTPFound(location=self.url_current('index'))
        else:
            item.algus = item.seansi_algus
        
    def _set_komplekt(self, tos):
        # tagame, et iga hindamiskogumi kohta on olemas hindamisolek
        c = self.c
        tos.give_hindamisolekud(True)
        komplekt_id = None
        for kvalik in c.testiosa.komplektivalikud:
            sk = ExamSaga(self).give_soorituskomplekt(tos.id, kvalik.id)
            if not sk.komplekt_id:
                for k in kvalik.komplektid:
                    komplekt_id = k.id
                    break
                sk.komplekt_id = komplekt_id
        for holek in tos.hindamisolekud:
            holek.komplekt_id = komplekt_id
    
    def _postupdatetask(self, sop, r):
        "Soorituse oleku muutmine ülesande vastuste kinnitamisel"
        c = self.c
        if sop == 'endtask':
            # salvestatakse vastus keskserveris ja eemaldatakse eksamiserverist
            ryv = r.ylesandevastus
            yv = ExamSaga(self).yv_from_examdb(c.exapi_host, c.sooritus, c.testiosa, ryv, c.lang, c.ty, c.vy, c.ylesanne)

            # vastuse hindamine
            on_arvuti = yv.pallid_arvuti is not None
            on_kasitsi = yv.staatus == const.B_STAATUS_KEHTETU
            msg, jatka = BlockCalc(self).gen_res_msg(yv, c.ylesanne, c.ylesanne.max_pallid, on_arvuti, on_kasitsi, c.lang)
            # Tulemus: 1 punkti 1-st võimalikust
            self.notice(msg)

            # vastuse kuvamine
            c.read_only = True
            if c.ylesanne.has_solution:
                c.prepare_correct = True
                c.btn_correct = True
            c.show_response = c.prepare_response = True
            
            # kui kõik ylesanded on tehtud, siis märgime töö tehtuks
            staatus = self._get_too_staatus(c.sooritus.id, c.testiosa.id)
            if staatus == const.S_STAATUS_TEHTUD:
                # töö lõpp
                c.sooritus.set_staatus(staatus)
                c.sooritus.lopp = datetime.now()
                c.sooritaja.staatus = staatus
            model.Session.flush()
            
            # kogu töö punktid kokku loetakse ka siis, kui kogu töö pole veel tehtud
            ExamSaga(self)._calculate_total(c.sooritus, c.sooritaja, c.test, c.testiosa, False, True)
            model.Session.commit()
            # eksamiserverist kustutatakse ylesandevastuse kirje
            ExamClient(self, c.exapi_host).delete_ylesandevastus(c.sooritus.id, ryv.id)

    def _get_too_staatus(self, sooritus_id, testiosa_id):
        # kas kõik ylesanded on vastatud?
        model.Session.flush()
        q = (model.Session.query(model.sa.func.count(model.Testiylesanne.id))
             .filter(model.Testiylesanne.testiosa_id==testiosa_id)
             .filter(~ sa.exists().where(
                 sa.and_(model.Testiylesanne.id==model.Ylesandevastus.testiylesanne_id,
                        model.Ylesandevastus.sooritus_id==sooritus_id,
                         model.Ylesandevastus.kehtiv==True)))
             )
        if q.scalar() == 0:
            # kõik ylesanded on vastatud
            staatus = const.S_STAATUS_TEHTUD
        else:
            staatus = const.S_STAATUS_POOLELI
        return staatus

    ################ ylesandevastuse leidmine
    def _get_toovastus_id(self):
        c = self.c
        c.yv_id = self.request.matchdict.get('yv_id') or self.request.params.get('yv_id')
        self._give_klaster()
        
    def _give_klaster(self):
        c = self.c
        oli_id = c.sooritaja.klaster_id
        klaster_id, c.exapi_host = model.Klaster.give_klaster(c.sooritaja)
        if klaster_id != oli_id:
            model.Session.commit()

    def _edit_toovastus(self):
        "Luuakse või leitakse muudetav vastus"
        c = self.c
        self._give_klaster()
        r = ExamClient(self, c.exapi_host).edit_toovastus(c.sooritus.id, c.ty.id, c.vy.id)
        return r
        
    @property
    def is_error_fullpage(self):
        "Kas ootamatu vea korral kuvada kogu kujundusega avaleht"
        if self.c.action in ('edittask', 'updatetask'):
            return False
        else:
            return True
        
    def __before__(self):
        c = self.c
        test_id = self.request.matchdict.get('test_id')
        c.test = model.Test.get(test_id)
        c.testiosa = c.test.testiosad[0]
        c.sooritus_id = self.request.matchdict.get('sooritus_id')
        c.sooritus = model.Sooritus.get(c.sooritus_id)
        if c.sooritus:
            c.sooritaja = c.sooritus.sooritaja
            c.testiosa = c.sooritus.testiosa
            c.nimekiri = c.sooritaja.nimekiri
            
        vy_id = self.request.matchdict.get('id')
        if vy_id:
            c.vy = model.Valitudylesanne.get(vy_id)
            c.ty = c.vy and c.vy.testiylesanne
            c.ylesanne = c.vy and c.vy.ylesanne
        
    def _has_permission(self):
        c = self.c
        action = c.action
        if c.sooritus:
            if c.ty and c.ty.testiosa_id != c.sooritus.testiosa_id:
                log.error('vale testiosa')
                return False
            if c.nimekiri and c.sooritaja.kasutaja_id == c.user.id:
                if not c.nimekiri.alates or c.nimekiri.alates <= date.today():
                    if not c.nimekiri.kuni or c.nimekiri.kuni >= date.today():
                        return True
        return False
            
def _calc_ajakulu(lopp, algus):
    # arvutame testi algusest saadik kulunud aja sekundites
    if lopp > algus:
        d = lopp - algus
        return d.seconds + d.days * 86400
    else:
        # algus salvestati sellises rakendusserveris, mille kell oli ees
        return 0
