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

class LahendamineController(BaseResourceController, EsitlusController):
    _permission = 'lahendamine'
    _MODEL = model.Ylesanne
    _INDEX_TEMPLATE = 'avalik/lahendamine/avalikotsing.mako'
    _EDIT_TEMPLATE = 'avalik/lahendamine/lahendamine.mako' 
    _LIST_TEMPLATE = 'avalik/lahendamine/avalikotsing_list.mako'
    _SEARCH_FORM = forms.avalik.lahendamine.AvalikotsingForm 
    _authorize = False
    _get_is_readonly = False
    _log_params_post = True
    _sort_options = ('ylesanne.id','ylesanne.nimi','ylesanne.aste_mask')
    _DEFAULT_SORT = 'ylesanne.id' # vaikimisi sortimine
    _TASK_TEMPLATE = '/avalik/lahendamine/lahendamine.esitlus.mako'
    _actions = 'index,edit,show,update'
    
    def _query(self):
        "Päring avalike ülesannete seas"
        q = (self._MODEL.query
             .filter_by(etest=True)
             .filter_by(adaptiivne=False)
             )
        if self.c.user.on_pedagoog:
            q = q.filter(model.Ylesanne.staatus.in_((const.Y_STAATUS_AVALIK, const.Y_STAATUS_PEDAGOOG)))
        else:
            q = q.filter_by(staatus=const.Y_STAATUS_AVALIK)
        return q

    def _search(self, q):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        c = self.c
        id = self.request.params.get('id')
        if id:
            q = q.filter_by(id=id)
            if q.count() == 0:
                item = model.Ylesanne.get(id)
                if item:
                    self.error(_("Ülesanne {id} ei ole avalik").format(id=id))
        if c.aine:
            f_aine = model.Ylesandeaine.aine_kood==c.aine
            if c.teema:
                teema = model.Klrida.get_by_kood('TEEMA', kood=c.teema, ylem_kood=c.aine)            
                c.teema_id = teema and teema.id
                if c.alateema:
                    f_teema = (model.Ylesandeaine.ylesandeteemad
                               .any(sa.and_(model.Ylesandeteema.teema_kood==c.teema,
                                            model.Ylesandeteema.alateema_kood==c.alateema)
                                    )
                               )
                else:
                    f_teema = (model.Ylesandeaine.ylesandeteemad
                               .any(model.Ylesandeteema.teema_kood==c.teema))
                f_aine = sa.and_(f_aine, f_teema)
            q = q.filter(model.Ylesanne.ylesandeained.any(f_aine))
            
        if c.aste:
            aste_bit = c.opt.aste_bit(c.aste) or 0
            q = q.filter(model.Ylesanne.aste_mask.op('&')(aste_bit) > 0)
            
        if c.kvaliteet:
            q = q.filter(model.Ylesanne.kvaliteet_kood==c.kvaliteet)
        if c.testiliik:
            q = q.filter(model.Ylesanne.testiliigid
                         .any(model.Testiliik.kood==c.testiliik))

        if c.keeletase:
            q = q.filter_by(keeletase_kood=c.keeletase)
        if c.ylkogu_id:
            q = q.filter(model.Ylesanne.koguylesanded.any(
                model.Koguylesanne.ylesandekogu_id==c.ylkogu_id))            
        if c.lang:
            q = q.filter(model.Ylesanne.skeeled.like('%' + c.lang + '%'))

        if c.kysimus:
            q = q.filter(model.Ylesanne.sisuplokid\
                             .any(model.Sisuplokk.tyyp==c.kysimus))
        return q

    def update(self):
        """Ylesande avamine loetelust LISTPOST abil
        """
        return self.edit()

    def correct(self):
        c = self.c
        self._get_tempvastus()
        if c.yv_id and c.exapi_host:
            r = ExamClient(self, c.exapi_host).edittask_temp(c.yv_id)
            c.ylesandevastus, responses = self.decode_yv(r)        
        return super().correct()

    def _show_d(self):
        id = self.request.matchdict.get('id')
        self.c.item = self._MODEL.get(id)
        if not self.c.item:
            self.error(_("Ülesannet ei leitud!"))
            return self._redirect('index')
        self._show(self.c.item)
        return self.response_dict

    def _edit_d(self):
        "Ülesande ümbritsev osa"
        c = self.c
        id = self.request.matchdict.get('id')
        c.list_url = self.request.params.get('list_url')
        c.item = item = c.ylesanne
        if not item:
            self.error(_("Ülesannet ei leitud!"))
            return self._redirect('index')
        
        c.prev_id, c.next_id = self._get_next(id)
        lang = self.params_lang() or item.lang
        c.lang = lang in item.keeled and lang or None
        self._edit(item)
        return self.response_dict

    def _edit(self, item):
        c = self.c
        if not self._check_status(item):
            self.error(_("Ülesanne pole avalik!"))
            raise self._redirect('index')

        self._get_tempvastus()
        if not c.yv_id:
            self._create_tempvastus()

    def edittask(self):
        c = self.c
        id = self.request.matchdict.get('id')
        c.item = item = c.ylesanne
        if not self._check_status(item):
            err = _("Ülesanne pole avalik!")
            self.error(err)
            return Response(err)
        lang = self.params_lang() or item.lang
        c.lang = lang in item.keeled and lang or None
        self._get_tempvastus()
        if not c.yv_id or not c.klaster_id:
            log.error(f'Vigane URL, puudub yv_id {c.yv_id} või klaster_id {c.klaster_id}')
            return Response(_("Vigane URL"))

        # leitakse senised vastused
        r = ExamClient(self, c.exapi_host).edittask_temp(c.yv_id)
        c.ylesandevastus, c.responses = self.decode_yv(r)
        c.correct_responses = c.ylesanne.correct_responses(None,
                                                           lang=c.lang,
                                                           naide_only=True,
                                                           hindaja=False,
                                                           naidistega=False,
                                                           as_tip=True)
        bcorrect = self._edittask_bcorrect()
        c.sooritaja_eesnimi = c.user.eesnimi
        response = self._gentask(yv=c.ylesandevastus,
                                 pcorrect=c.read_only,
                                 bcorrect=bcorrect)
        if c.new_responses:
            # esimesel kuvamisel genereeriti juhuarvud,
            # need tuleb salvestada vastustena
            self._save_new_random_responses(c.ylesanne.id, c.new_responses, None, None)
        return response

    def _edittask_bcorrect(self):
        # kas kuvada õige vastuse nupp
        return True
    
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
                                    varparams={},
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
        lang = self.params_lang()
        yv_id = self.request.params.get('yv_id')        
        c.refresh_showtask_url = self.h.url_current('showtask', lang=lang, yv_id=yv_id, kl_id=c.klaster_id)
        return self.edittask()
    
    def updatetask(self):
        """Lahendaja salvestab oma vastuse
        """
        c = self.c
        id = self.request.matchdict.get('id')
        params = self.request.params.mixed()
        sop = params.get('sop')
        # sop: file, endtask
        self._get_tempvastus()
        
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

        # kui ylesandes on juhuarv, siis tuleb enne vastuste arvutamist laadida juhuarvu väärtus
        vaja_ks = ylesanne.on_juhuarv
        
        # kui oli faile, siis peab esmalt looma kirjed, et oleks ID
        # seejärel salvestatakse, tekib fileversion
        # hiljem salvestatakse klastris fileversion
        self._save_files(temp_yv, responses, vaja_ks, mresponses)

        c.list_url = self.request.params.get('list_url')
        item = c.ylesanne

        lang = self.params_lang()
        c.lang = lang in item.keeled and lang or None

        self._set_response(buf)
        c.read_only = True
        if c.ylesanne.has_solution:
            c.prepare_correct = True
            c.btn_correct = True
        c.show_response = c.prepare_response = True
        jatka = False
        if item.tulemused:
             # on olemas hindamismaatriksid
             blockcalc = BlockCalc(self)
             total, arvuti, kasitsi, max_pallid, msg, buf, jatka = \
                 blockcalc.calculate_temp(item, mresponses, c.lang, temp_yv)
        else:
             msg = _("Vastus on vastu võetud")

        self._set_calculation(buf)
        self._copy_search_params()
            
        sop = self.request.params.get('sop')
        r, error = self._updatetask(sop, temp_yv)        
        
        if jatka:
             # peab jätkama sama ylesande lahendamist
             c.read_only = c.prepare_correct = c.btn_correct = c.show_response = False

        # eemaldame kõik seni lisatud sõnumid (soovitud ES-1290)
        messages = self.request.session.pop_flash('notice')
        self.notice(msg)

        if sop == 'file':
            res = {'rc': 'ok'}
            return Response(json_body=res)
        return self.showtask()


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
        r, error = ExamClient(self, c.exapi_host).updatetask(sooritus_id,
                                                      ty_id,
                                                      vy_id,
                                                      data)
        return r, error
    
    def _save_files(self, temp_yv, responses, vaja_ks, mresponses):
        # peab genereerima kirjed, et saaks salvestada faile        
        c = self.c

        is_file = False
        for kv in responses:
            for ks in kv.kvsisud:
                if ks._unsaved_filedata:
                    is_file = True
                    break
        if not vaja_ks and not is_file:
            # pole vaja midagi teha
            return

        sop = self.request.params.get('sop')
        r, error = self._updatetask(sop, temp_yv)
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
                    mresponses[kv.kood] = kv
                    
    def _set_response(self, buf):
        "Kui on vaja antud vastust tekstina näidata, siis pannakse c.vastus sisse"
        pass

    def _set_calculation(self, buf):
        "Kui on vaja arvutuskäiku näidata, siis siis pannakse c.calculation sisse"
        pass

    def _get_next_otsingust(self, params, current_id):
        # muudame dicti form_resultiks
        form_data = self._ITEM_FORM.to_python(params)
        # jätame otsinguparameetrid meelde (neid kasutab _search)
        self._copy_search_params(form_data)
        # koostame päringu
        q = self._search(self._query())
        # lisame sortimise
        q = self._order(q, params.get('sort'))
        return q
        
    def _get_next(self, id):
        """Leitakse järgmine ülesanne
        """
        prev_id = self.request.params.get('prev_id')
        next_id = self.request.params.get('next_id')
        if next_id:
            # on juba varasemast teada
            try:
                next_id = int(next_id)
            except:
                next_id = None
            try:
                prev_id = int(prev_id)
            except:
                prev_id = None
            return prev_id, next_id

        if self.c.list_url:
            # loetleme loetelu
            # muudame loetelu URLi dictiks
            params = url_to_dict(self.c.list_url)
            current_id = int(id)
            q = self._get_next_otsingust(params, current_id)
            get_id = lambda r: r.id

            if q:
                step_id = None
                found = False
                for r in q.all():
                    y_id = get_id(r)
                    if y_id == current_id:
                        # leiti praegune ylesanne
                        found = True
                        prev_id = step_id
                    elif found:
                        # leiti järgmine ylesanne
                        next_id = y_id
                        break
                    else:
                        # jätame meelde
                        step_id = y_id
        # järgmist ei leitud
        return prev_id, next_id

    def _get_tempvastus(self):
        c = self.c
        c.yv_id = self.request.matchdict.get('yv_id') or self.request.params.get('yv_id')
        c.klaster_id = self.request.params.get('kl_id')
        c.exapi_host = model.Klaster.get_host(c.klaster_id)
        
    def _create_tempvastus(self):
        c = self.c
        klaster_id, host = model.Klaster.get_klaster(None)
        c.klaster_id = klaster_id
        c.exapi_host = host
        c.yv_id = ExamClient(self, host).create_tempvastus(c.ylesanne.id)
        
    def _check_status(self, item):
        if item and self.c.user.has_permission('lahendamine', const.BT_SHOW, obj=item):
            return True

    def __before__(self):
        c = self.c
        c.lang = self.params_lang()
        ylesanne_id = self.request.matchdict.get('id')
        if ylesanne_id:
            c.ylesanne = model.Ylesanne.get(ylesanne_id)

def url_to_dict(url):
    from urllib.parse import urlparse
    u = urlparse(url)
    if u[4]:
        return dict([part.split('=') for part in u[4].split('&')])
    else:
        return {}
