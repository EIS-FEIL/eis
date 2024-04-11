from simplejson import dumps
from eis.lib.baseresource import *
_ = i18n._
from eis.lib.block import BlockController
from eis.lib.resultentry import ResultEntry
from eis.handlers.avalik.lahendamine.esitlus import EsitlusController
from eis.lib.estnltkclient import EstnltkClient
from .hindamiskogumid import HindamisteArv
from .vastajad import new_hindamine

import logging
log = logging.getLogger(__name__)

class HkhindamineController(BaseResourceController, EsitlusController):
    """Labiviija hindab lahendaja kirjalikku lahendust.
    """
    _permission = 'khindamine'
    _MODEL = model.Testiylesanne
    _INDEX_TEMPLATE = 'avalik/khindamine/hkhindamine.mako'
    _EDIT_TEMPLATE = 'avalik/khindamine/hindamine.ylesanne.mako'    
    _ITEM_FORM = forms.avalik.hindamine.KHindamineForm
    _is_small_header = True
    _get_is_readonly = False
    _actions = 'index,update,create,edit,show' # võimalikud tegevused
    _actionstask = 'showtask'
    _TASK_TEMPLATE = '/avalik/khindamine/hindamine.esitlus.mako'
    
    def index(self):
        # hindamise lehe avamine või
        # hindamiskriteeriumitega hindamiskogumis teise ylesande avamine
        op = self.request.params.get('op')
        ty_id = self._get_next_id(op) or None
        res = self._ty_edit(ty_id)
        if res:
            return res
        if not self.request.params.get('partial'):
            template = self._INDEX_TEMPLATE
        else:
            if ty_id:
                # ylesande vahetamisel: ylesande osa 
                self.c.ainult_yl_vahetub = True
                # muul juhul ylesande osa + kriteeritumite osa
            template = self._EDIT_TEMPLATE
        return self.render_to_response(template)

    def _get_ylesanded(self):
        c = self.c
        if not c.komplekt:
            # komplekt pole määratud
            return
        komplektis_ty_id = c.komplekt.get_testiylesanded_id(c.hindamiskogum)
        log.debug('hk %s komplektis ty: %s' % (c.hindamiskogum.id, komplektis_ty_id))
        if c.ignore_ty_id:
            # jätame välja need testiylesanded, mida ei ole vaja hindajale kuvada
            log.debug('  ignore: %s' % c.ignore_ty_id)
            komplektis_ty_id = [ty_id for ty_id in komplektis_ty_id \
                                if ty_id not in c.ignore_ty_id]
            log.debug('  ty: %s' % komplektis_ty_id)            
        c.testiylesanded_id = komplektis_ty_id           
                
    def _redirect_to_index(self, is_json):
        c = self.c
        url = self.url('khindamine_vastajad', toimumisaeg_id=c.toimumisaeg.id, hindaja_id=c.hindaja_id)
        if is_json:
            return Response(json_body={'redirect': url})
        else:
            return HTTPFound(location=url)

    def _redirect_new(self):
        # võetakse järgmine töö hindamiseks
        c = self.c
        
        if c.lst:
            # leitakse minu tööde loetelus järgmine
            holek = self._get_next_in_list(c.sooritus.id, c.lst)
        else:
            # võetakse uus töö
            holek, error = new_hindamine(self, c.toimumisaeg, c.testiosa, c.hindamiskogum, c.hindaja, c.sooritus.id)
            if error:
                self.error(error)
        if holek:
            partial = self.request.params.get('partial') or None                
            url = self.url_current('index',
                                   toimumisaeg_id=c.toimumisaeg.id, 
                                   hindaja_id=c.hindaja.id, 
                                   sooritus_id=holek.sooritus_id,
                                   lst=c.lst,
                                   partial=partial)
            return HTTPFound(location=url)
        else:
            return self._redirect_to_index(True)

    def _edit(self, item):
        return self._ty_edit(item.id)

    def _show(self, item):
        return self._edit(item)
    
    def _ty_edit(self, ty_id):
        c = self.c
        c.show_tulemus = True
        c.prepare_correct = True
        if c.sooritus.staatus != const.S_STAATUS_TEHTUD and not c.test.on_jagatudtoo:
            self.error(_("Testi pole sooritatud"))
        sooritaja = c.sooritus.sooritaja    
        if c.sooritus.klastrist_toomata:
            exapi_host = model.Klaster.get_host(sooritaja.klaster_id)
            ExamSaga(self).from_examdb(exapi_host, c.sooritus, sooritaja, c.test, c.testiosa, c.toimumisaeg, sooritaja.lang, False)
            
        c.hindamine = self._give_hindamine()
        if not c.hindamine or c.toimumisaeg and not c.toimumisaeg.on_hindamise_luba:
            # polnud õigust hinnata
            is_json = self.request.params.get('partial')
            return self._redirect_to_index(is_json)
        
        if c.testiosa.vastvorm_kood in (const.VASTVORM_KP, const.VASTVORM_SP):
            self._set_ptest_komplekt()
        else:
            holek = c.hindamine.hindamisolek
            c.hindamine.komplekt_id = holek.komplekt_id
            if c.sooritus.staatus == const.S_STAATUS_TEHTUD:
                # anname vastamata küsimustele automaatselt 0p
                model.Session.flush()
                self._set_etest_unresponded()

        c.test = c.testiosa.test
        c.komplekt = c.hindamine.komplekt
        self._get_ylesanded()
        if c.testiylesanded_id:
            # on ylesandeid, mida hinnata
            if not ty_id:
                for ty_id in c.testiylesanded_id:
                    break
            c.ty = model.Testiylesanne.get(ty_id)
            c.ylesandevastus = self._get_ylesandevastus(ty_id)
            if c.ylesandevastus:
                c.vy = c.ylesandevastus.valitudylesanne
                c.ylesanne = c.vy.ylesanne                
                self._tekstianalyys(c.ylesandevastus, c.ylesanne.id)
            else:
                # sooritaja pole ylesannet sooritanud
                if not c.komplekt:
                    c.komplekt = c.sooritus.get_komplekt(c.ty.alatest_id)
                c.vy = c.ty.getq_valitudylesanne(c.komplekt.id)
                c.ylesanne = c.vy.ylesanne
        else:
            # miskipärast ei ole sooritajal yhtki ylesannet vaja hinnata
            # tyhistame asjatu hindamise
            c.hindamine.tyhistatud = True
            if not c.app_ekk:
                # kui pole eelvaade
                model.Session.commit()
            is_json = self.request.params.get('partial')
            if not is_json:
                self.error(_("Hinnatavaid ülesandeid ei ole"))
            return self._redirect_to_index(is_json)
        
        if not c.app_ekk:
            # kui pole eelvaade, siis salvestame hindamise kirje
            model.Session.commit()

        # funktsioonid mako sees kasutamiseks
        c.BlockController = BlockController
        if sooritaja:
            c.lang = sooritaja.lang
        if not c.test.on_jagatudtoo:
            assert c.sooritus.staatus >= const.S_STAATUS_TEHTUD, _("Vale olek")
        c.read_only = True
        self._get_tab_urls()
        # kas kuvada järgmise töö nuppu
        c.is_next = self._is_next(c.sooritus)
        # hindamiste arvud
        self._get_hindamiste_arvud()

    def _tekstianalyys(self, yv, ylesanne_id, force=False):
        "Kui vaja, siis tehakse tekstianalyys"
        #force = True
        q = (model.Session.query(model.Kysimus)
             .join(model.Kysimus.sisuplokk)
             .filter(model.Sisuplokk.ylesanne_id==ylesanne_id)
             .filter(model.Kysimus.tekstianalyys==True)
             )
        modified = False
        for k in q.all():
            kv = yv.get_kysimusevastus(k.id)
            if not kv.vastuseta:
                # leiame automaatse tekstianalyysi kirjed
                ksmarkused = {ksm.seq: ksm for ksm in kv.ksmarkused if not ksm.ylesandehinne_id}
                for ks in kv.kvsisud:
                    # kontrollime, kas on juba analyysitud
                    ksm = ksmarkused.get(ks.seq)
                    if not ksm or force:
                        # peab uuesti analyysima
                        if not ksm:
                            ksm = model.Ksmarkus(seq=ks.seq)
                            kv.ksmarkused.append(ksm)
                        log.debug(f'generate ESTNLTK {k.kood}')
                        items = EstnltkClient(self).analyze(ks.sisu, k.rtf)
                        #log.debug('\n'.join([str(item) for item in items]))
                        ksm.markus = dumps(items)
                        modified = True
        if modified and not self.c.app_ekk:
            model.Session.commit()
            
    def _get_hindamiste_arvud(self):
        c = self.c
        harv = HindamisteArv(c.hindaja, c.toimumisaeg)
        c.alustamata = harv.alustamata
        c.cnt_pooleli = harv.lv_pooleli
        c.cnt_valmis = harv.lv_valmis
        c.cnt_hinnatud = harv.lv_hinnatud
        
    def _is_next(self, sooritus):
        # kas on veel töid saadaval ja on vaja järgmise töö nuppu
        c = self.c
        check_s_id = sooritus.id
        if c.lst:
            next_holek = self._get_next_in_list(check_s_id, c.lst)
        else:
            next_holek, next_error = new_hindamine(self, c.toimumisaeg, c.testiosa, c.hindamiskogum, c.hindaja, check_s_id)        
            if next_error:
                log.debug('is_next: %s' % next_error)
        return next_holek is not None

    def _get_next_in_list(self, check_s_id, lst):
        # otsime mulle suunatud pooleli tööde seast
        c = self.c
        q = (model.Hindamisolek.query
             .join(model.Hindamisolek.sooritus)
             .filter(model.Sooritus.staatus==const.S_STAATUS_TEHTUD)
             .filter(model.Sooritus.toimumisaeg_id==c.toimumisaeg.id)
             .filter(model.Hindamisolek.hindamiskogum_id==c.hindamiskogum.id)
             .join(model.Hindamisolek.hindamised)
             .filter(model.Hindamine.labiviija_id==c.hindaja.id)
             .filter(model.Hindamine.staatus==const.H_STAATUS_POOLELI)
             .filter(model.Hindamine.tyhistatud==False)
             .filter(model.Hindamisolek.hindamisprobleem!=const.H_PROBLEEM_TOOPUUDU)             
             )
        try:
            lst = int(lst)
        except:
            lst = ''
        if lst == const.H_STAATUS_POOLELI_VALMIS:
            q = q.filter(model.Hindamine.sisestatud==True)
        else:
            q = q.filter(model.Hindamine.sisestatud==False)
        q = q.order_by(sa.desc(model.Hindamine.on_probleem),model.Sooritus.id)
        # leiame antud tööle järgneva töö
        found = False
        for _holek in q.all():
            if found:
                return _holek
            elif _holek.sooritus_id == check_s_id:
                found = True

    def _get_tab_urls(self):
        get_tab_urls(self, self.c)
        
    def _set_etest_unresponded(self):
        # e-testi korral: leitakse ülesanded, mis tuleb hindamiselt välja jätta, kuna pole käsitsi hinnatavaid vastuseid
        c = self.c
        resultentry = ResultEntry(self, const.SISESTUSVIIS_PALLID, c.test, c.testiosa)
        self.c.ignore_ty_id = resultentry.unresponded_zero(c.sooritus, c.hindamine, c.hindamine.hindamisolek, c.hindamiskogum)

    def _set_ptest_komplekt(self):
        # p-testi korral - salvestatakse komplekt
        c = self.c
        c.opt_komplektid = c.hindamiskogum.get_komplektivalik().get_opt_komplektid(c.toimumisaeg)
        komplekt_id = self.request.params.get('komplekt_id')
        if komplekt_id:
            komplekt_id = int(komplekt_id)
            if komplekt_id in [r[0] for r in c.opt_komplektid]:
                c.hindamine.komplekt_id = komplekt_id
        if not c.hindamine.komplekt_id:
            if len(c.opt_komplektid) == 1:
                c.hindamine.komplekt_id = c.opt_komplektid[0][0]
            else:
                c.hindamine.komplekt_id = c.hindamine.hindamisolek.komplekt_id

    def _update_mcomments(self, id):
        "Tekstis märgitud vigade ja kommentaaride automaatne salvestamine"
        c = self.c
        params = self.request.json_body
        yv = model.Ylesandevastus.get(params['yv_id'])
        assert yv.sooritus_id == c.sooritus.id, 'Vale sooritus'
        vy = yv.valitudylesanne
        if params.get('k_id'):
            k_id = int(params['k_id'])
            ksseq = int(params['ksseq'])
            kysimus = model.Kysimus.get(k_id)
            kv = yv.get_kysimusevastus(kysimus.id)
            hindamine = self._give_hindamine()
        else:
            # ei tea, kuidas
            kv = hindamine = None
            log.error('update_mcomments k_id? params=%s' % params)
        if kv and hindamine:
            yhinne = hindamine.give_ylesandehinne(yv, vy)
            ksm = yhinne.give_ksmarkus(kv, ksseq)
            ksm.markus = dumps(params['items'])
            model.Session.commit()
            res = {'result':'OK'}
        else:
            res = {'result':'NOK'}
        return Response(json_body=res)

    def showtask(self):
        "Ülesande kuvamine"
        c = self.c
        c.read_only = True
        c.ty = ty = self._checkty()

        c.ylesandevastus = self._get_ylesandevastus(ty.id)
        if not c.ylesandevastus:
            self.error(_("Ülesannet pole lahendatud"))
            return self.render_to_response('/avalik/lahendamine/esitlus.message.mako')
        c.vy = vy = c.ylesandevastus.valitudylesanne
        c.ylesanne = vy.ylesanne
        c.lang = c.sooritus.sooritaja.lang
        c.responses = {kv.kood: kv for kv in c.ylesandevastus.kysimusevastused}
        c.correct_responses = c.ylesanne.correct_responses(c.ylesandevastus,
                                                           lang=c.lang,
                                                           naide_only=True,
                                                           hindaja=True,
                                                           naidistega=True,
                                                           as_tip=True)
        hindamine = self._give_hindamine()
        return self._gentask(yv=c.ylesandevastus,
                             hindaja=c.hindaja,
                             hindamine_id=hindamine.id,
                             pcorrect=c.test.oige_naitamine,
                             bcorrect=False,
                             can_commit=not c.app_ekk)

    def _get_ylesandevastus(self, ty_id, komplekt_id=None):
        return self.c.sooritus.getq_ylesandevastus(ty_id, komplekt_id)

    def _checkty(self):
        ty_id = self.request.matchdict.get('ty_id')
        ty = model.Testiylesanne.get(ty_id)
        assert ty.testiosa_id == self.c.testiosa.id, 'vale testiosa'
        return ty

    def _update(self, item):
        # ylesande hindamise salvestamine
        c = self.c
        params = self.request.params
        op = params.get('op')
        hindamine = self._give_hindamine()
        if not hindamine:
            # polnud õigust hinnata
            log.debug('ei või hinnata')
            return self._redirect_to_index(True)

        self._save_probleem(hindamine, params)

        if op == 'lykka':
            hindamine.staatus = const.H_STAATUS_LYKATUD
            hindamine.lykkamispohjus = self.request.params.get('lykkamispohjus')
            # hindamine.tyhistatud = True
            model.Session.commit()
            self.success(_("Testitöö hindamine on tagasi lükatud"))
            self._lykkamisteade(hindamine)
            return self._redirect_to_index(True)
        self._save_hindamine(hindamine)
        return self._after_update(op)

    def _lykkamisteade(self, hindamine):
        "Hindamisjuhile saadetakse teade, et hindaja lükkas töö hindamise tagasi"
        toimumisaeg_id = self.c.toimumisaeg.id
        today = date.today()
        q = (model.Session.query(model.Kasutaja.id,
                                 model.Kasutaja.epost,
                                 model.Kasutaja.nimi)
             .filter(model.Kasutaja.epost!=None)
             .filter(model.Kasutaja.epost!='')
             .join(model.Testiisik.kasutaja)
             .filter(model.Testiisik.kasutajagrupp_id==const.GRUPP_T_HINDAMISJUHT)
             .filter(model.Testiisik.test_id==self.c.test.id)
             .filter(model.Testiisik.kehtib_alates<=today)
             .filter(model.Testiisik.kehtib_kuni>=today)
             )
        li_epost = []
        li_nimi = []
        kasutajad = list(q.all())
        li_epost = [r[1] for r in kasutajad]
        li_nimi = [r[2] for r in kasutajad]
        if len(li_epost):
            to = li_epost
            hkasutaja = self.c.hindaja.kasutaja
            data = {'isik_nimi': hkasutaja.nimi,
                    'test_nimi': self.c.test.nimi,
                    'user_nimi': self.c.user.fullname,
                    'ta_tahised': self.c.toimumisaeg.tahised,
                    'lykkamispohjus': hindamine.lykkamispohjus,
                    'hk_tahis': self.c.hindamiskogum.tahis,
                    'tahised': self.c.sooritus.tahised,
                    }
            subject, body = self.render_mail('mail/tagasilykkamine.hindamisjuhile.mako', data)
            body = Mailer.replace_newline(body)
            if not Mailer(self).send(to, subject, body):
                kiri = model.Kiri(tyyp=model.Kiri.TYYP_MUU,
                                  sisu=body,
                                  teema=subject,
                                  teatekanal=const.TEATEKANAL_EPOST)
                for k_id, epost, nimi in kasutajad:
                    model.Kirjasaaja(kiri=kiri, kasutaja_id=k_id, epost=epost)
            model.Session.commit()
            
    def _after_update(self, op):
        c = self.c
        if op == 'jargminetoo':
            # võetakse järgmine töö ette
            response = self._redirect_new()
            if response:
                return response
        else:
            next_ty_id = self._get_next_id(op)
            if next_ty_id:
                # on antud eelmine, järgmine või sakist valitud ylesanne, kuhu edasi minna
                url = self.url_current('edit', id=next_ty_id, lst=c.lst)
                return HTTPFound(location=url)

            next_tos_id = self._get_next_tos(op)
            if next_tos_id:
                # on antud järgmine töö (ylesandehindamine.py)
                url = self.url_current('edit', sooritus_id=next_tos_id, lst=c.lst)
                return HTTPFound(location=url)

        # loetellu
        return self._redirect_to_index(True)

    def _save_probleem(self, hindamine, params):
        hindamine.on_probleem = params.get('on_probleem') and True or None
        if hindamine.on_probleem:
            hindamine.probleem_sisu = params.get('probleem_sisu')
            hindamine.probleem_varv = params.get('probleem_varv')
        else:
            hindamine.probleem_sisu = None
            hindamine.probleem_varv = None
            
    def _create(self, **kw):
        # hindamiskriteeriumitega hindamiskogumi hindamise salvestamine
        return self._update(None)

    def _error_create(self):
        res = self._ty_edit(None)
        html = self.form.render(self._EDIT_TEMPLATE, extra_info=self.response_dict)
        return Response(html)

    def _get_next_id(self, op):
        if op:
            m = re.match(r'(prev|next|tab-ty)\_([0-9]+)', op)
            if m:
                # on antud eelmine, järgmine või sakist valitud ylesanne, kuhu edasi minna
                ty_id = m.groups()[1]
                return ty_id

    def _get_next_tos(self, op):
        if op:
            m = re.match(r'tos\_([0-9]+)', op)
            if m:
                # valikust valiti järgmine töö, mida hinnata
                tos_id = m.groups()[0]
                return tos_id
        
    def _save_hindamine(self, hindamine):
        c = self.c
        holek = hindamine.hindamisolek
        self._set_hindamine_komplekt(hindamine, holek)
            
        hindamine.hindaja_kasutaja_id = c.user.id
        hindamine.ksm_naeb_hindaja = self.form.data['ksm_naeb_hindaja']
        hindamine.ksm_naeb_sooritaja = self.form.data['ksm_naeb_sooritaja']        
        hindamine.staatus = const.H_STAATUS_POOLELI
        resultentry = ResultEntry(self, const.SISESTUSVIIS_PALLID, c.test, c.testiosa)
        prefix = ''
        lopeta = False # ei kinnita hindamist
        sooritaja = c.sooritus.sooritaja
        resultentry.save_ty_hindamine(sooritaja, self.form.data, lopeta, prefix, c.sooritus, holek, c.testiosa, hindamine, None, False)

        if resultentry.errors:
            err = self._desc_errors(resultentry.errors)
            raise ValidationError(self, resultentry.errors, message=err)

        model.Session.commit()

    def _set_hindamine_komplekt(self, hindamine, holek):
        # p-testi korral ei ole komplekt algul teada, hindaja peab sisestama
        komplekt = hindamine.komplekt or holek.komplekt
        if not komplekt:
            komplekt_id = self.form.data.get('komplekt_id')
            if not komplekt_id:
                if self.c.testiosa.vastvorm_kood in (const.VASTVORM_KE, const.VASTVORM_SE, const.VASTVORM_I):
                    err = _("Testi pole sooritatud")
                else:
                    err = _("Palun vali ülesandekomplekt")
                raise ValidationError(self, {}, err)
            komplekt = model.Komplekt.get(komplekt_id)
            hindamine.komplekt = komplekt
        if komplekt and holek.komplekt != komplekt:
            holek.komplekt = komplekt

    def _desc_errors(self, errors):
        "Kirjutame veateatesse info selle kohta, millises ylesandes on viga"
        err = _("Palun kõrvalda vead")
        self.log_add(const.LOG_USER, err, str(errors))
        return err

    def _give_hindamine(self):
        c = self.c
        liik = c.hindaja and c.hindaja.liik or const.HINDAJA1
        holek = c.sooritus.give_hindamisolek(c.hindamiskogum)
        # EKK hindaja eelvaate korral võetakse kasutaja id hindaja kirjest ja see ei pruugi olla user.id
        user_id = c.hindaja and c.hindaja.kasutaja_id or c.user.id
        # leiame jooksva hindaja ja
        # kontrollime, et keegi teine pole vahepeal selle töö hindajaks hakanud        
        if c.hindaja:
            hindamine1 = holek.get_hindamine(liik)
            if hindamine1 and hindamine1.labiviija_id and hindamine1.labiviija_id != c.hindaja.id:
                # leiti kehtiv hindamise kirje
                # kui see on lykatud või suunatud, siis on ok, see tyhistatakse kohe järgmisel sammul
                if hindamine1.staatus not in (const.H_STAATUS_LYKATUD, const.H_STAATUS_SUUNATUD):
                    self.error(_("Testitööd {s} hindab keegi teine").format(s=c.sooritus.tahised or ''))
                    log.error('hindamine=%s, hindamine.labiviija_id=%s, hindaja=%s, liik=%s' % \
                              (hindamine1.id, hindamine1.labiviija_id, c.hindaja.id, liik))
                    return

        c.hindamine = holek.give_hindamine(liik, hindaja_kasutaja_id=user_id)
        if c.hindaja:
            mkh = c.toimumisaeg.muu_koha_hindamine(c.hindaja.valimis, c.hindaja.liik)
            if c.hindaja.testikoht_id and c.sooritus.testikoht_id != c.hindaja.testikoht_id and not mkh:
                self.error(_("Testitöö {s} on teisest soorituskohast").format(s=c.sooritus.tahised or ''))
                return
            elif c.hindaja.testikoht_id and c.sooritus.testikoht_id == c.hindaja.testikoht_id and mkh:
                self.error(_("Testitöö {s} on minu soorituskohast").format(s=c.sooritus.tahised or ''))
                return            
            if c.hindamine.labiviija_id and c.hindamine.labiviija_id != c.hindaja.id:
                self.error(_("Testitööd {s} hindab keegi teine").format(s=c.sooritus.tahised or ''))
                log.error('hindamine=%s, hindamine.labiviija_id=%s, hindaja=%s, liik=%s' % \
                         (c.hindamine.id, c.hindamine.labiviija_id, c.hindaja.id, liik))
                return

        c.hindamine.hindaja_kasutaja_id = user_id
        if c.hindaja:
            c.hindamine.labiviija = c.hindaja
            model.Session.flush()
            c.hindaja.calc_toode_arv()
        return c.hindamine

    def __before__(self):
        c = self.c
        sooritus_id = self.request.matchdict.get('sooritus_id')
        c.sooritus = model.Sooritus.get(sooritus_id)
        toimumisaeg_id = self.request.matchdict.get('toimumisaeg_id')
        c.toimumisaeg = model.Toimumisaeg.get(toimumisaeg_id)
        c.testiosa = c.toimumisaeg.testiosa
        c.test = c.testiosa.test
       
        c.hindaja_id = int(self.request.matchdict.get('hindaja_id'))
        if c.hindaja_id:
            c.hindaja = model.Labiviija.get(c.hindaja_id)
            c.hindamiskogum_id = c.hindaja.hindamiskogum_id
            c.hindamiskogum = c.hindaja.hindamiskogum
            c.on_kriteeriumid = c.hindamiskogum.on_kriteeriumid

        # lst - loetelu filtris kasutatud staatus, kust töö hindamine avati
        # kasutusel järgmise töö valimisel
        c.lst = self.request.params.get('lst')

    def _has_permission(self):
        c = self.c
        if c.hindaja and c.hindaja.kasutaja_id != c.user.id:
            return False
        if c.sooritus.toimumisaeg_id != c.toimumisaeg.id:
            return False
        return bool(self.c.hindaja)

def get_tab_urls(handler, c):
    h = handler.h
    
    # vasakul poolel ylesande avamise (GET) või hindamise salvestamise (POST) URL
    def f_submit_url(ty_id):
        if ty_id:
            # ylesande hindamine
            return h.url('khindamine_hkhindamine', sooritus_id=c.sooritus.id, 
                         toimumisaeg_id=c.toimumisaeg.id, hindaja_id=c.hindaja_id, id=ty_id)
        else:
            # hindamiskogumi hindamiskriteeriumite hindamine
            return h.url('khindamine_hkhindamised', sooritus_id=c.sooritus.id, 
                         toimumisaeg_id=c.toimumisaeg.id, hindaja_id=c.hindaja_id)
        
    c.f_submit_url = f_submit_url
        
    # paremal poolel ylesandega seotud sakkide andmed
    def f_r_tabs_data(vy, ylesanne, indlg):
        data = []
        indlg = indlg and 1 or None

        if c.r_tab == 'juhend' or ylesanne.on_hindamisjuhend or c.hindamiskogum.on_kriteeriumid:
            url = h.url('khindamine_juhendid', toimumisaeg_id=c.toimumisaeg.id, vy_id=vy.id, lang=c.lang, indlg=indlg)
            label = _("Hindamisjuhend")
            if ylesanne.hindamisjuhist_muudetud():
                label = label + ' ' + h.mdi_icon('mdi-flag')
            data.append(('juhend', url, label))

        url = h.url('khindamine_edit_lahendamine', toimumisaeg_id=c.toimumisaeg.id, vy_id=vy.id, id=vy.ylesanne_id, lang=c.lang, correct=1, indlg=indlg)
        data.append(('correct', url, _("Õige vastus")))      

        url = h.url('khindamine_edit_lahendamine', toimumisaeg_id=c.toimumisaeg.id, vy_id=vy.id, id=vy.ylesanne_id, lang=c.lang, indlg=indlg)
        data.append(('lahendamine', url, _("Lahendaja vaade")))

        url = h.url('khindamine_hindamiskysimused', toimumisaeg_id=c.toimumisaeg.id, vy_id=vy.id, lang=c.lang, indlg=indlg)
        data.append(('hindamiskysimused', url, _("Küsimused")))

        q = (model.Session.query(sa.func.count(model.Kysimus.id))
             .join(model.Kysimus.sisuplokk)
             .filter(model.Sisuplokk.ylesanne_id==ylesanne.id)
             .filter(model.Kysimus.tekstianalyys==True)
             )
        if q.scalar() > 0:
            url = h.url('khindamine_tekstianalyys', toimumisaeg_id=c.toimumisaeg.id, vy_id=vy.id, lang=c.lang, indlg=indlg)
            data.append(('tekstianalyys', url, _("Tekstianalüüs")))
            
        return data
    
    c.f_r_tabs_data = f_r_tabs_data
    if c.vy:
        c.r_tabs_data = f_r_tabs_data(c.vy, c.vy.ylesanne, c.indlg)
