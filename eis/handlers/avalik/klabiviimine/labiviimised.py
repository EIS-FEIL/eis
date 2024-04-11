from simplejson import dumps
from eis.lib.baseresource import *
from eis.lib.resultentry import ResultEntry
from eis.lib.examclient import ExamClient

_ = i18n._

log = logging.getLogger(__name__)

class LabiviimisedController(BaseResourceController):
    """Testi läbiviimise kontrollerite (testimiskordade testide jaoks: klabiviimine/toimumisajad,
    avalike testide jaoks: testid/labiviimine) ühine osa.
    """
    _MODEL = model.Testiruum
    _DEFAULT_SORT = 'testiruum.id' # vaikimisi sortimine
    _log_params_post = True
    _actions = 'index,show,update,edit,delete' # võimalikud tegevused
    
    def _get_sooritused(self):
        """Soorituste loetelu, üle laadida.
        """
        return []

    def _check_sooritus(self, rcd):
        """Kontrollitakse, kas parameeter on lubatud sooritus.
        Üle laadida.
        """
        return False

    def _edit(self, item):
        c = self.c
        c.items = self._get_sooritused()
        if self.request.params.get('debug'):
            c.debug = 1
        c.arvutid_header, c.arvutid_items = self._get_arvutid()
        c.info_msg = self._get_info_msg()

    def _get_info_msg(self):
        "Läbiviijale antav selgitus sooritamiskeskkonna nõuete kohta"
        c = self.c

        li = []
        if not c.toimumisaeg:
            return ''
        if c.toimumisaeg.on_arvuti_reg:
            li.append(_("Sooritajate arvutid peavad olema eelnevalt registreeritud."))
            if c.testiruum.arvuti_reg == const.ARVUTI_REG_ON:
                li.append(_("Arvutite registreerimine tuleks märkida lõppenuks kohe peale kõigi arvutite registreerimist."))
                li.append(_("Läbiviijad peavad arvutid registreerima ise, registreerimise parooli ei või sooritajatele avaldada."))
            if len(c.test.testiosad) > 1:
                li_ta = []
                if c.toimumisaeg.on_reg_test and c.testiruum.ruum_id:
                    # kas sama ruum on teistel toimumisaegadel kasutusel?
                    q = (model.SessionR.query(model.Testiosa.tahis)
                         .join(model.Testiosa.toimumisajad)
                         .filter(model.Toimumisaeg.testimiskord_id==c.toimumisaeg.testimiskord_id)
                         .filter(model.Toimumisaeg.id!=c.toimumisaeg.id)
                         .filter(model.Toimumisaeg.on_arvuti_reg==True)
                         .join(model.Toimumisaeg.testikohad)
                         .join(model.Testikoht.testiruumid)
                         .filter(model.Testiruum.ruum_id==c.testiruum.ruum_id)
                         .order_by(model.Testiosa.seq))
                    li_ta = [tahis for tahis, in q.all()]
                    if li_ta:
                        r_tahis = c.testiruum.ruum.tahis
                        osa_tahised = ', '.join(li_ta)
                        if len(li_ta) == 1:
                            li.append(_("Selles ruumis kehtivad ka sama testimiskorra testiosa {s1} ruumi {s2} registreeritud arvutid.").format(s1=osa_tahised, s2=r_tahis))
                        else:
                            li.append(_("Selles ruumis kehtivad ka sama testimiskorra testiosade {s1} ruumi {s2} registreeritud arvutid.").format(s1=osa_tahised, s2=r_tahis))
                if not li_ta:
                    li.append(_("Teiste testiosade jaoks registreeritud arvutid on selles ruumis kasutamiseks vaja uuesti registreerida."))
        if c.toimumisaeg.verif_seb:
            li.append(_("Sooritamiseks on vajalik SEB brauser."))
        if c.toimumisaeg.on_veriff:
            li.append(_("Sooritajad peavad enne sooritamist tõendama oma isiku Veriffi teenuse abil."))
        elif c.toimumisaeg.on_proctorio:
            li.append(_("Sooritamist kontrollitakse Proctorio abil."))

        return ' '.join(li)
        
    def _get_arvutid(self):
        "Registreeritud arvutite loetelu"
        c = self.c
        # kas muudes sama ruumi testiruumides regatud arvutid kehtivad siin
        on_reg_test = c.toimumisaeg and c.toimumisaeg.on_reg_test and c.testiruum.ruum_id
        header = [_("Jrk"),
                  _("IP"),
                  _("Kehtib kuni"),
                  _("Eemalda")]
        
        c.uniq_arvuti_id = set()
        
        def add_row(testikoht, testiruum, testiarvuti, can_del):
            if testiarvuti.algne_id:
                c.uniq_arvuti_id.add(testiarvuti.algne_id)
            li = [testiarvuti.id]
            if on_reg_test:
                jrk = testiarvuti.tahis
            else:
                jrk = testiarvuti.seq
            li.extend([jrk,
                       testiarvuti.ip,
                       self.h.str_from_datetime(testiarvuti.kehtib_kuni)])

            if can_del and not c.toimumisaeg:
                value = self.url('testid_delete_labiviimine', test_id=c.test.id, id=testiruum.id,
                                 arvuti_id=testiarvuti.id, sub='reg')
            elif can_del:
                value = self.url('klabiviimine_delete_toimumisaeg', id=testiruum.id,
                                 arvuti_id=testiarvuti.id, sub='reg')
            else:
                value = ''
            li.append(value)
            return li

        now = datetime.now()
        items = []
        for rcd in c.testiruum.testiarvutid:
            if rcd.staatus == const.B_STAATUS_KEHTIV and rcd.kehtib_kuni > now:
                li = add_row(c.testikoht, c.testiruum, rcd, True)
                items.append(li)

        if on_reg_test:
            for testiruum_id in c.testiruum.get_other_in_tk(c.toimumisaeg.testimiskord_id):
                testiruum = model.Testiruum.get(testiruum_id)
                testikoht = testiruum.testikoht
                for rcd in testiruum.testiarvutid:
                    if rcd.staatus == const.B_STAATUS_KEHTIV and rcd.kehtib_kuni > now:
                        li = add_row(testikoht, testiruum, rcd, False)
                        items.append(li)

        return header, items
        
    def _delete_reg(self, id):
        arvuti_id = self.request.params.get('arvuti_id')
        arvuti = model.Testiarvuti.get(arvuti_id)
        if arvuti and arvuti.staatus != const.B_STAATUS_KEHTETU:
            arvuti.staatus = const.B_STAATUS_KEHTETU
            model.Session.commit()
        return self._after_update()

    def _update_reg(self, id):
        """Arvutite registreerimise oleku muutmine
        """
        c = self.c
        arvuti_reg = int(self.request.params.get('arvuti_reg'))
        if arvuti_reg == const.ARVUTI_REG_ON:
            for n in range(100):
                parool = c.testiruum.parool = User.gen_pwd(5)
                model.Session.commit()
                if model.Testiruum.query.\
                        filter_by(parool=c.testiruum.parool).\
                        count() == 1:
                    # ükski teine teine testiruum pole sellise parooliga
                    break
        else:
            c.testiruum.parool = None
        c.testiruum.arvuti_reg = arvuti_reg
        model.Session.commit()
        return self._after_update()

    def delete(self):
        """DELETE /admin_ITEMS/id: Delete an existing item"""
        sub = self._get_sub()
        if sub:
            id = self.request.matchdict.get('id')
            return eval('self._delete_%s' % sub)(id)
        return self._after_delete(parent_id)
    
    def _update_ruum(self, id):
        """Kasutaja valis ruumide valikust ruumi
        """
        return HTTPFound(location=self.url('klabiviimine_edit_toimumisaeg', id=self.c.testiruum.id, 
                     testiruum_id=self.request.params.get('testiruum_id')))

    def _edit_markus(self, id):
        self.c.sooritus = model.Sooritus.get(self.request.params.get('sooritus_id'))
        assert self._check_sooritus(self.c.sooritus),  "Vale sooritus"
        return self.render_to_response('avalik/klabiviimine/markus.mako')        

    def _update_markus(self, id):
        sooritus_id = self.request.params.get('sooritus_id')
        markus = self.request.params.get('markus')
        tos = model.Sooritus.get(sooritus_id)
        assert self._check_sooritus(tos), "Vale sooritus"
        tos.markus = markus

        model.Session.commit()
        self.success(_("Märkus on salvestatud!"))
        return self._after_update()

    def _edit_lisaaeg(self, id):
        self._edit_lisaaeg_d(id)
        return self.render_to_response('avalik/klabiviimine/lisaaeg.mako')
    
    def _edit_lisaaeg_d(self, id):
        self.c.sooritus = model.Sooritus.get(self.request.params.get('sooritus_id'))
        assert self._check_sooritus(self.c.sooritus), "Vale sooritus"
        return self.response_dict
    
    def _update_lisaaeg(self, id):
        c = self.c
        sooritus_id = self.request.params.get('sooritus_id')
        c.sooritus = model.Sooritus.get(sooritus_id)
        self.form = Form(self.request, schema=forms.avalik.labiviimine.LisaaegForm)
        if not self.form.validate():
            c.dialog_lisaaeg = True
            return Response(self.form.render('avalik/klabiviimine/lisaaeg.mako',
                                             extra_info=self._edit_lisaaeg_d(id)))

        assert self._check_sooritus(c.sooritus), "Vale sooritus"

        lisaaeg = self.form.data.get('tos_lisaaeg')
        atsid = self.form.data.get('ats')
        rcd = model.Sooritus.get(sooritus_id)
        klaster_id = rcd.sooritaja.klaster_id
        if klaster_id:
            host = model.Klaster.get_host(klaster_id)
            if host:
                ExamClient(self, host).set_lisaaeg(sooritus_id, lisaaeg, atsid)
        else:
            for ats in atsid:
                alatest_id = ats['alatest_id']
                atos = c.sooritus.give_alatestisooritus(alatest_id)
                atos.lisaaeg = ats['lisaaeg']
            
        model.Session.commit()
        self.success()
        return self._after_update()

    def _edit_parool(self, id):
        c = self.c
        c.items = []
        sooritused_id = self.request.params.getall('sooritus_id')
        for sooritus_id in sooritused_id:
            sooritus = model.Sooritus.get(sooritus_id)
            if c.testiruum:
                assert sooritus.testiruum_id == c.testiruum.id, "Vale ruum"
            c.items.append(sooritus)

        return self.render_to_response('/avalik/klabiviimine/sooritajad.paroolid.mako')            

    def _update_parool(self, id):
        self.c.items = []
        sooritused_id = self.request.params.getall('pwd_id')
        for sooritus_id in sooritused_id:
            sooritus = model.Sooritus.get(sooritus_id)
            if self.c.testiruum:
                assert sooritus.testiruum_id == self.c.testiruum.id, "Vale ruum"
            sooritaja = sooritus.sooritaja
            kasutaja = sooritaja.kasutaja
            pwd = User.gen_pwd(6, True)
            sooritaja.set_password(pwd, userid=kasutaja.isikukood)
            self.c.items.append((kasutaja.isikukood, sooritaja.eesnimi, sooritaja.perenimi, pwd))
        model.Session.commit()
        return self.render_to_response('/avalik/klabiviimine/sooritajad.paroolid.print.mako')    

    def _show_refr(self, id):
        """Läbiviija vaate uuendamine
        """
        c = self.c
        if c.testiruum:
            # päritakse sooritajad ja arvutid
            self._edit(c.testiruum)
            template = '/avalik/klabiviimine/klabiviimine.refresh.mako'
            c.can_update = True
            return self.render_to_response(template)        
        
    def _update_tos2st(self, id):
        """Läbiviija muudab sooritajate staatust, kirjalik test
        """
        sooritused_id = self.request.params.getall('sooritus_id')
        staatus = self.request.params.get('staatus')
        stpohjus = self.request.params.get('stpohjus')
        set_sooritused_staatus(self, self.c.testiruum.id, sooritused_id, staatus, stpohjus, self.c.testiosa, True, self.c.toimumisaeg)
        model.Session.commit()
        self.success(_("Andmed on salvestatud"))
        return self._show_refr(id)

    def _update_tosst(self, id):
        """Läbiviija muudab sooritajate staatus, suuline test
        """
        sooritused_id = self.request.params.getall('sooritus_id')
        staatus = self.request.params.get('staatus')
        stpohjus = None
        set_sooritused_staatus(self, self.c.testiruum.id, sooritused_id, staatus, stpohjus, self.c.testiosa, False, self.c.toimumisaeg)
        model.Session.commit()
        return self._redirect('edit')
    
    def _update_chlang(self, id):
        """Läbiviija muudab sooritajate soorituskeelt
        """
        c = self.c
        sooritused_id = list(map(int, self.request.params.getall('sooritus_id')))
        sameerr = sterr = sterr2 = cnt = 0
        lang = self.request.params.get('lang')            
        if c.toimumisaeg and c.toimumisaeg.keel_admin:
            keeled = c.toimumisaeg.testimiskord.keeled
            if lang in keeled:
                for sooritus_id in sooritused_id:
                    rcd = model.Sooritus.get(sooritus_id)
                    assert self._check_sooritus(rcd), "Vale sooritus"
                    sooritaja = rcd.sooritaja
                    if sooritaja.lang == lang:
                        sameerr += 1
                    else:
                        klaster_id = sooritaja.klaster_id
                        if klaster_id:
                            host = model.Klaster.get_host(klaster_id)
                            if host:
                                rc = ExamClient(handler, host).set_lang(sooritus_id, lang)
                                if rc:
                                    # muudeti
                                    sooritaja.lang = lang
                                    cnt += 1
                
        if cnt:
            self.success(_("Muudeti {n} sooritaja soorituskeel").format(n=cnt))
            model.Session.commit()
        if sterr2:
            self.error(_("{n} sooritaja soorituskeelt ei saa enam muuta, sest mõni testiosa on juba lõpetatud").format(n=sterr+sterr2))
        elif sterr:
            self.error(_("{n} sooritaja soorituskeelt ei saa enam muuta, sest testi sooritamine on juba lõpetatud").format(n=sterr+sterr2))            
        return self._show_refr(id)                       
    
    def __before__(self):
        if self.c.testiruum:
            koht_id = self.c.user.koht and self.c.user.koht.id 
            self.c.testikoht = self.c.testiruum.testikoht
            self.c.testiosa = self.c.testikoht.testiosa
            self.c.test = self.c.testiosa.test

    def _is_log_params(self):
        sub = self.request.params.get('sub')
        if self.c.action == 'show' and sub == 'tos2st':
            # läbiviija vormi automaatne uuendamine, ei logi
            return False
        return BaseResourceController._is_log_params(self)

    def _raise_not_authorized(self, is_authenticated):
        sub = self.request.params.get('sub')
        if sub == 'refr':
            # automaatne lk uuendamine, vaja on vea staatust
            if is_authenticated:
                # 403
                raise HTTPForbidden()
            else:
                # 401
                raise HTTPUnauthorized()
            
        return super()._raise_not_authorized(is_authenticated)
    
def _get_testiosa(testiosa):
    d = {'id': testiosa.id,
         'yhesuunaline': testiosa.yhesuunaline,
         }
    return d
    
def _get_alatestid(testiosa_id):
    # alatestid
    q = (model.Session.query(model.Alatest.id,
                             model.Alatest.testivaline,
                             model.Alatest.on_yhekordne,
                             model.Alatest.piiraeg,
                             model.Alatest.alatest_kood,
                             model.Alatest.max_pallid,
                             model.Alatest.skoorivalem)
         .filter(model.Alatest.testiosa_id==testiosa_id)
         .order_by(model.Alatest.seq)
         )
    alatestid = []
    for a_id, testivaline, on_yhekordne, piiraeg, alatest_kood, a_max_p, skoorivalem in q.all():
        da = {'id': a_id,
              'testivaline': testivaline,
              'yhekordne': on_yhekordne,
              'piiraeg': piiraeg,
              'alatest_kood': alatest_kood,
              'max_pallid': a_max_p,
              'skoorivalem': skoorivalem,
              }
        q1 = (model.Session.query(model.Testiylesanne.id)
              .filter_by(alatest_id=a_id))
        da['testiylesanded_id'] = [ty_id for ty_id, in q1.all()]
        alatestid.append(da)
    return alatestid

def set_sooritused_staatus(handler, testiruum_id, sooritused_id, staatus, stpohjus, testiosa, kirjalik, toimumisaeg):
    jatk_voimalik = not toimumisaeg or toimumisaeg.jatk_voimalik
    sooritused_id = list(map(int, sooritused_id))
    klastrid = {}
    if staatus:
        # kontrollime, kas vaja muuta klastris või keskserveris
        for sooritus_id in sooritused_id:
            rcd = model.Sooritus.get(sooritus_id)
            assert handler._check_sooritus(rcd), "Vale sooritus"
            sooritaja = rcd.sooritaja
            klaster_id = sooritaja.klaster_id
            if klaster_id and rcd.klastrist_toomata:
                # jätame meelde, millised sooritused vajavad klastris muutmist
                if staatus in (const.S_STAATUS_ALUSTAMATA,
                               const.S_STAATUS_POOLELI,
                               const.S_STAATUS_KATKESTATUD):
                    rcd.klastrist_toomata = True
                if klaster_id not in klastrid:
                    klastrid[klaster_id] = [rcd.id]
                else:
                    klastrid[klaster_id].append(rcd.id)
            else:
                # muudame staatuse keskserveris
                set_sooritus_staatus(handler, rcd, staatus, stpohjus, kirjalik)
    log.debug(f'klastrid: {klastrid}')
    test = testiosa.test
    if klastrid:
        # sooritajad, kelle olek on vaja muuta klastris
        alatestid = _get_alatestid(testiosa.id)
        for klaster_id, sooritused_id in klastrid.items():
            host = model.Klaster.get_host(klaster_id)
            log.debug(f'host{host}/{klaster_id}')
            if host:
                res = ExamClient(handler, host).set_staatus(testiruum_id, sooritused_id, staatus, stpohjus, testiosa, alatestid, kirjalik, jatk_voimalik)
                updated = {r.get('id'): r for r in res}
                
            for sooritus_id in sooritused_id:
                rcd = model.Sooritus.get(sooritus_id)
                tor = updated.get(sooritus_id)
                if tor:
                    # kirje oli eksamiserveris
                    rcd.update(**tor)
                else:
                    # kirjet ei olnud veel eksamiserveris
                    set_sooritus_staatus(handler, rcd, staatus, stpohjus, kirjalik)
                    
                sooritaja = rcd.sooritaja
                if rcd.staatus == const.S_STAATUS_TEHTUD:
                    host = model.Klaster.get_host(sooritaja.klaster_id)
                    ExamSaga(handler).from_examdb(host, rcd, sooritaja, test, testiosa, toimumisaeg, sooritaja.lang)
                else:
                    sooritaja.update_staatus()

def set_sooritus_staatus(handler, rcd, staatus, stpohjus, kirjalik=True):
    if staatus == 'arvutita':
        # unusta arvuti ja luba sooritajal teine arvuti võtta
        rcd.testiarvuti_id = None
    elif staatus == 'ava':
        # sooritaja on kogemata vajutanud lõpetamise nupule
        # aga administraator lubab tal jätkata
        n_staatus = const.S_STAATUS_KATKESTATUD
        toimumisaeg = rcd.toimumisaeg
        sooritaja = rcd.sooritaja
        if rcd.staatus in (const.S_STAATUS_TEHTUD,
                           const.S_STAATUS_KATKESPROT,
                           const.S_STAATUS_PUUDUS,
                           const.S_STAATUS_EEMALDATUD):
            if toimumisaeg and not toimumisaeg.jatk_voimalik:
                log.error('testi avamine pole lubatud')
            elif not rcd.seansi_algus:
                rcd.set_staatus(const.S_STAATUS_ALUSTAMATA, stpohjus)
            else:
                if kirjalik:
                    rcd.pallid = None
                    rcd.hindamine_staatus = const.H_STAATUS_HINDAMATA
                rcd.set_staatus(n_staatus, stpohjus)

                # arvutame tehtud alatestide tehtud ylesannete arvu
                for ala in rcd.alatestisooritused:
                    if ala.staatus in (const.S_STAATUS_TEHTUD, const.S_STAATUS_KATKESPROT):
                        ala.staatus = n_staatus
                        komplekt = rcd.get_komplekt(ala.alatest_id)
                        if komplekt:
                            set_yl_arv(ala, komplekt.id, ala.alatest)

        sooritaja.update_staatus()
    elif staatus == 'veriff0':
        # tyhistatakse luba sooritada ilma isikut tõendamata
        rcd.luba_veriff = False
    elif staatus == 'veriff1':
        # antakse luba sooritada ilma isikut tõendamata
        rcd.luba_veriff = True
    else:
        # staatuse muutmine
        staatus = int(staatus)
        if rcd.staatus < staatus or rcd.staatus == const.S_STAATUS_EEMALDATUD:
            sooritaja = rcd.sooritaja
            if staatus == const.S_STAATUS_TEHTUD:
                if not rcd.seansi_algus:
                    # alustamata sooritajad märgitakse puudunuks
                    rcd.set_staatus(const.S_STAATUS_PUUDUS, stpohjus)
                else:
                    log.info(_("sooritus {s} märgitakse tehtuks").format(s=rcd.id))
                    rcd.lopp = datetime.now()         
                    rcd.set_staatus(staatus, stpohjus)
            else:
                rcd.set_staatus(staatus, stpohjus)

def get_tyy_vyy(alatest_id, komplekt_id):
    q1 = (model.SessionR.query(model.Testiylesanne.id)
          .filter_by(alatest_id=alatest_id))
    testiylesanded_id = [ty_id for ty_id, in q1.all()]

    # valitud komplekti ylesanded selles alatestis
    q1 = (model.SessionR.query(model.Valitudylesanne.id)
          .join(model.Valitudylesanne.testiylesanne)
          .filter(model.Testiylesanne.alatest_id==alatest_id)
          )
    if komplekt_id:
        q1 = q1.filter(model.Valitudylesanne.komplekt_id==komplekt_id)
    valitudylesanded_id = [vy_id for vy_id, in q1.all()]
    return testiylesanded_id, valitudylesanded_id


def set_yl_arv(atos, komplekt_id, alatest):
    "Leitakse, mitu ülesannet on tehtud (st vähemalt mõnele küsimusele vastatud) ja mitu on kokku"
    sooritus_id = atos.sooritus_id
    if not komplekt_id:
        return
    tyy_id, vyy_id = get_tyy_vyy(alatest.id, komplekt_id)
    atos.yl_arv = len(tyy_id)

    q = (model.SessionR.query(sa.func.count(model.Ylesandevastus.id))
         .filter(model.Ylesandevastus.loplik==True)
         .filter(model.Ylesandevastus.sooritus_id==sooritus_id)
         .filter(model.Ylesandevastus.valitudylesanne_id.in_(vyy_id))
         )
    q1 = q.filter(model.Ylesandevastus.vastuseta==False)
    atos.tehtud_yl_arv = q.scalar()

    q1 = q.filter(model.Ylesandevastus.lopetatud==True)
    atos.lopetatud_yl_arv = q.scalar()
        
    if alatest.testivaline:
        # kysitluse olekut ei tohi automaatselt seada
        # sest kui olek on "tehtud", siis kysitlust lahendajale ei kuvata
        return
    elif alatest.on_yhekordne:
        # yhekordset testi ei või automaatselt märkida tehtuks
        if atos.tehtud_yl_arv > 0 and atos.staatus == const.S_STAATUS_ALUSTAMATA:
            atos.staatus = const.S_STAATUS_POOLELI
    elif atos.staatus != const.S_STAATUS_TEHTUD and atos.yl_arv > 0:
        if atos.tehtud_yl_arv == atos.yl_arv:
            atos.staatus = const.S_STAATUS_TEHTUD
        elif atos.tehtud_yl_arv > 0:
            atos.staatus = const.S_STAATUS_POOLELI
        elif atos.tehtud_yl_arv == 0:
            atos.staatus = const.S_STAATUS_ALUSTAMATA
            
