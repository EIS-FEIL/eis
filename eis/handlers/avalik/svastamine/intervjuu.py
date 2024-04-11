from eis.lib.baseresource import *
_ = i18n._
from eis.lib.resultentry import ResultEntry

log = logging.getLogger(__name__)

class IntervjuuController(BaseResourceController):
    """Suulise vastamise intervjuude salvestamine"""

    _permission = 'intervjuu'
    _INDEX_TEMPLATE = 'avalik/svastamine/intervjuu.mako' 
    _EDIT_TEMPLATE = 'avalik/svastamine/intervjuu.mako'     
    _HVF_TEMPLATE = 'avalik/svastamine/helivastus.mako'
    _DEFAULT_SORT = 'kasutaja.nimi'
    _get_is_readonly = False
    _actions = 'index,create,download'
    
    def _index_d(self):
        c = self.c
        # leiame sooritused
        c.sooritused_id = map(int, self.request.params.getall('sooritus_id'))
        q = (model.Session.query(model.Sooritus)
             .filter_by(testiruum_id=c.testiruum_id)
             .filter(model.Sooritus.id.in_(c.sooritused_id))
             .join(model.Sooritus.sooritaja)
             )
        q = q.order_by(model.Sooritaja.eesnimi,
                       model.Sooritaja.perenimi)
        c.sooritused = list(q.all())

        # märgime sooritamise alguse
        modified = False
        intervjueerijad = set([c.labiviija.id])
        for tos in c.sooritused:
            now = datetime.now()
            if tos.staatus in (const.S_STAATUS_REGATUD, const.S_STAATUS_ALUSTAMATA, const.S_STAATUS_KATKESTATUD):
                tos.set_staatus(const.S_STAATUS_POOLELI)
                if not tos.algus:
                    tos.algus = now
                tos.seansi_algus = now
                tos.sooritaja.update_staatus()
                modified = True
            elif tos.staatus != const.S_STAATUS_POOLELI:
                self.error(_("Sooritus on juba {s}").format(s=tos.staatus_nimi.lower()))
                return self._after_create()

            # märgime intervjueerija sooritusele
            old_lv_id = tos.intervjuu_labiviija_id
            if old_lv_id != c.labiviija.id:
                intervjueerijad.add(old_lv_id)
                tos.intervjuu_labiviija_id = c.labiviija.id
                modified = True

        if modified:
            model.Session.flush()
            for lv_id in intervjueerijad:
                if lv_id:
                    lv = model.Labiviija.get(lv_id)
                    lv.calc_toode_arv()
            model.Session.commit()
            
        # kasutaja tehtud valikud
        c.alatest_id = self.request.params.get('alatest_id')
        c.komplekt_id = self.request.params.get('komplekt_id')
        
        # leiame alatestid ja ylesanded
        c.alatestid_opt = c.testiosa.opt_alatestid
        if not c.alatestid_opt:
            kv = c.testiosa.komplektivalikud[0]
        elif c.alatest_id:
            c.alatest = model.Alatest.get(c.alatest_id)
            assert c.alatest.testiosa_id == c.testiosa.id, 'vale alatest'
            kv = c.alatest.komplektivalik
        else:
            # alatest on valimata
            kv = None
        if kv:
            komplektid = kv.get_opt_komplektid(c.toimumisaeg, True)
            log.debug('KOMPLEKTID:%s' % komplektid)
            c.opt_komplektid = [(k.id, k.tahis) for k in komplektid]

            komplekt = None
            if len(komplektid) == 1:
                # ainult 1 komplekt on valida
                komplekt = komplektid[0]
                c.komplekt_id = komplekt.id
            else:
                if c.komplekt_id:
                    # kasutaja just valis komplekti
                    komplekt = model.Komplekt.get(c.komplekt_id)
                    if komplekt and komplekt.id not in [r[0] for r in c.opt_komplektid]:
                        komplekt = None

                if not komplekt:
                    # kasutame esimest komplekti, mis on juba valitud
                    for tos in c.sooritused:
                        komplekt = tos.get_komplekt_by_kv(kv.id)
                        if komplekt:
                            break
            if komplekt:
                c.komplekt_id = komplekt.id
                c.komplekt = komplekt
                
                # märgime komplekti
                hkogumid_id = [hk.id for hk in kv.hindamiskogumid]
                for tos in c.sooritused:
                    tos.give_hindamisolekud()
                    for ho in tos.hindamisolekud:
                        if ho.hindamiskogum_id in hkogumid_id and ho.komplekt_id != komplekt.id:
                            ho.komplekt_id = komplekt.id
                model.Session.commit()

                if c.alatest:
                    c.testiylesanded = list(c.alatest.testiylesanded)
                else:
                    c.testiylesanded = list(c.testiosa.testiylesanded)
        
        return self.response_dict

    def _download(self, id, format=None):
        """Laadi helifail alla"""
        item = model.Helivastusfail.get(id)
        if not item:
            raise NotFound('Kirjet %s ei leitud' % id)        
        q = (model.Session.query(model.Helivastus.id)
             .filter_by(helivastusfail_id=item.id)
             .join(model.Helivastus.sooritus)
             .filter(model.Sooritus.testiruum_id==self.c.testiruum.id)
             )
        if not q.count():
            if not (item.filename.startswith('helikontroll') \
                    and item.creator == self.c.user.isikukood \
                    and not len(item.helivastused)):
                raise NotFound('Puudub ligipääsuõigus')

        mimetype = item.mimetype
        if not mimetype:
            (mimetype, encoding) = mimetypes.guess_type(item.filename)
        return utils.download(item.filedata, item.filename, mimetype)

    def _create(self):
        c = self.c
        params = self.request.params
        if params.get('katkesta'):
            staatus = const.S_STAATUS_KATKESTATUD
        elif params.get('lopeta'):
            staatus = const.S_STAATUS_TEHTUD
        for sooritus_id in params.getall('sooritus_id'):
            tos = model.Sooritus.get(sooritus_id)
            assert tos and tos.testiruum_id == c.testiruum_id, 'vale sooritus'
            if tos.staatus == const.S_STAATUS_POOLELI:
                tos.set_staatus(staatus)
                model.Session.flush()
                tos.sooritaja.update_staatus()
            else:
                self.error(_("Sooritus on juba {s}").format(s=tos.staatus_nimi.lower()))
                break
        if not self.has_errors():
            model.Session.flush()
            c.labiviija.calc_toode_arv()
            model.Session.commit()

    def _after_create(self, id=None):
        return HTTPFound(self.url('svastamine_vastajad', testiruum_id=self.c.testiruum_id))        
        
    def _error_create(self):
        html = self.form.render(self._INDEX_TEMPLATE,
                                extra_info=self._index_d())            
        return Response(html)

    def _create_file(self):
        c = self.c
        params = self.request.params
        s_sooritused_id = params.get('sooritused_id')
        if s_sooritused_id:
            sooritused_id = s_sooritused_id.split(',')
        else:
            sooritused_id = []
            
        y_id = params.get('y_id')
        ty_id = params.get('ty_id')
        ty = model.Testiylesanne.get(ty_id)

        # kas brauser on kaasa andnud kirje ID (võib-olla on faili algus varem juba salvestatud)
        try:
            hvfid = params.get('hvf_id') # hvf_NNN
            hvf_id = int(hvfid.split('_')[-1])
        except:
            hvf_id = None

        # helifail
        response = params.get('audio')
        if isinstance(response, cgi.FieldStorage):
            # kontrollime, et kõik sooritajad kuuluvad testiruumi
            sooritused2_id = []
            tahised = []
            for sooritus_id in sooritused_id:
                tos = model.Sooritus.get(sooritus_id)
                assert tos.testiruum_id == c.testiruum.id, 'vale ruum'
                sooritused2_id.append(tos.id)
                if tos.tahis:
                    tahised.append(tos.tahis)

            filename = 'v.mp3'
            filedata = response.value
            filesize = len(filedata)

            hvf = None
            if hvf_id:
                # brauser arvab, et sama faili algus on varem juba salvestatud
                hvf3 = model.Helivastusfail.get(hvf_id)
                # kontrollime, et see fail sobib
                if hvf3 and hvf3.creator == c.user.isikukood and hvf3.filesize <= filesize:
                    sooritused3_id = set()
                    tyy3_id = set()
                    for hv in hvf3.helivastused:
                        sooritused3_id.add(hv.sooritus_id)
                        tyy3_id.add(hv.testiylesanne_id)
                    if sooritused3_id and sooritused3_id == set(sooritused2_id) and len(tyy3_id) == 1 and list(tyy3_id)[0] == ty.id or \
                       not sooritused3_id and not sooritused2_id:
                        # kõik sooritused on samad või ei ole kummalgi sooritusi (on helikontroll)
                        hvf = hvf3
            if hvf:
                # fail oli juba olemas
                hvf.filedata = filedata
                hvf.filesize = filesize
            else:
                # loome uue faili
                hvf = model.Helivastusfail(filename=filename,
                                           filedata=filedata,
                                           filesize=filesize)
                model.Session.flush()
                if not sooritused_id:
                    hvf.filename = 'helikontroll-%s.mp3' % str(hvf.id)
                else:
                    hvf.filename = str(hvf.id) + '.mp3'
                    for sooritus_id in sooritused2_id:
                        hv = model.Helivastus(sooritus_id=sooritus_id,
                                              helivastusfail_id=hvf.id,
                                              ylesanne_id=y_id,
                                              testiylesanne_id=ty_id)
            hvf.valjast = False
            hvf.kestus = hvf.audio_duration(filedata)
            model.Session.commit()
            self.c.helivastusfail = hvf
            return self.render_to_response(self._HVF_TEMPLATE)
        else:
            return Response('')

    def __before__(self):
        c = self.c
        c.testiruum = model.Testiruum.get(self.request.matchdict.get('testiruum_id'))
        c.testiruum_id = c.testiruum.id
        c.toimumisaeg = c.testiruum.testikoht.toimumisaeg
        c.testiosa = c.toimumisaeg.testiosa
        c.test = c.testiosa.test
        # leitakse kasutaja roll selles testiruumis
        q = (model.Labiviija.query
             .filter(model.Labiviija.toimumisaeg_id==c.toimumisaeg.id)
             .filter(model.Labiviija.testiruum_id==c.testiruum.id)
             .filter(model.Labiviija.kasutaja_id==c.user.id)
             .filter(model.Labiviija.kasutajagrupp_id==const.GRUPP_INTERVJUU)
             )
        c.labiviija = q.first()

    def _has_permission(self):
        dt = date.today()
        return self.c.labiviija is not None and \
               self.c.testiruum.algus.date() == dt
