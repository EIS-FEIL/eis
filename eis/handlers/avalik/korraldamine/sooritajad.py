from time import mktime
from eis.lib.baseresource import *
from eis.lib.basegrid import BaseGridController
from eis.handlers.ekk.otsingud.labiviijateated import send_labiviija_maaramine
from eis.handlers.avalik.korraldamine.testikohad import tkoht_on_ruumid, tkoht_on_labiviijad
_ = i18n._

log = logging.getLogger(__name__)

class SooritajadController(BaseResourceController):

    _permission = 'avalikadmin'
    _MODEL = model.Sooritus
    _INDEX_TEMPLATE = 'avalik/korraldamine/sooritajad.mako' 
    _LIST_TEMPLATE = 'avalik/korraldamine/sooritajad_list.mako'
    _DEFAULT_SORT = 'sooritus.tahis,sooritaja.perenimi sooritaja.eesnimi'
    _ITEM_FORM = forms.avalik.admin.KSooritajadForm
    _no_paginate = True
    _ignore_default_params = ['csv','xls','format','otsi']
    _perm_koht = True
    
    def _query(self):
        
        ta = self.c.testikoht.toimumisaeg
        li = [ta.vaatleja_maaraja and const.GRUPP_VAATLEJA,
              ta.hindaja1_maaraja and const.GRUPP_HINDAJA_S,
              ta.hindaja2_maaraja and const.GRUPP_HINDAJA_S2,
              #ta.hindaja_v_maaraja and const.GRUPP_HINDAJA_V,
              ta.intervjueerija_maaraja and const.GRUPP_INTERVJUU,
              const.GRUPP_T_ADMIN,
              ]
        self.c.grupid_id = [grupp_id for grupp_id in li if grupp_id]
        q = (model.SessionR.query(model.Sooritus, 
                                model.Sooritaja, 
                                model.Kasutaja,
                                model.Testiprotokoll.tahis,
                                model.Testiruum.tahis,
                                model.Ruum.tahis,
                                model.Koolinimi.nimi)
             .join(model.Sooritus.sooritaja)
             .filter(model.Sooritus.testikoht_id==self.c.testikoht.id)
             .join(model.Sooritaja.kasutaja)
             .outerjoin((model.Testiprotokoll,
                         model.Testiprotokoll.id==model.Sooritus.testiprotokoll_id))
             .join(model.Sooritus.testiruum)
             .outerjoin(model.Testiruum.ruum)
             .outerjoin(model.Sooritaja.koolinimi)
             .filter(model.Sooritus.staatus>const.S_STAATUS_REGAMATA)
             .filter(model.Sooritus.staatus!=const.S_STAATUS_VABASTATUD)
             )
        return q

    def _search_default(self, q):
        return self._search(q)

    def _search(self, q):
        c = self.c
        NULL = '-'
        self._get_opt(q)

        def _fnull(field, value, empty=False):
            if value != NULL:
                return field == value
            elif not empty:
                return field == None
            else:
                return sa.or_(field==None, field=='')

        if c.testiruum_id:
            q = q.filter(_fnull(model.Sooritus.testiruum_id, c.testiruum_id))
            c.otsi = True
        if c.ruum_id:
            c.otsi = True
            if c.ruum_id == NULL:
                q = q.filter(sa.or_(model.Sooritus.testiruum_id==None,
                                    model.Testiruum.ruum_id==None))
            else:
                q = q.filter(model.Testiruum.ruum_id==c.ruum_id)
        if c.tprotokoll_id:
            c.otsi = True
            q = q.filter(_fnull(model.Sooritus.testiprotokoll_id, c.tprotokoll_id))
        if c.koolinimi_id:
            c.otsi = True
            q = q.filter(_fnull(model.Sooritaja.koolinimi_id, c.koolinimi_id))
        if c.klass:
            c.otsi = True
            q = q.filter(_fnull(model.Sooritaja.klass, c.klass, True))
        if c.paralleel:
            c.otsi = True
            q = q.filter(_fnull(model.Sooritaja.paralleel, c.paralleel, True))
        if c.lang:
            c.otsi = True
            q = q.filter(_fnull(model.Sooritaja.lang, c.lang, True))
        if c.opetaja_id:
            c.otsi = True
            if c.opetaja_id == NULL:
                q = q.filter(~ model.Sooritaja.testiopetajad.any())
            else:
                q = q.filter(model.Sooritaja.testiopetajad.any(
                    model.Testiopetaja.opetaja_kasutaja_id==c.opetaja_id))
        if c.aeg:
            c.otsi = True            
            if c.aeg == NULL:
                aeg = None
            else:
                aeg = datetime.fromtimestamp(int(c.aeg))
            q = q.filter(model.Sooritus.kavaaeg==aeg)

        if self.c.csv:
            return self._index_csv(q)
        self.c.reg_kool_avatud = self._reg_kool_avatud()
        c.header = self._prepare_header()
        c.prepare_item = self._prepare_item
        return q

    def _order_join(self, q, tablename):
        """Otsingupäringu sortimisel lisatakse päringule join 
        tabeliga, mille välja järgi tuleb sortida
        """
        if tablename == 'opetaja':
            # lisame päringusse õpetaja,
            # kellest tähestikus eespool sel sooritajal muid õpetajaid pole
            Opetaja = sa.orm.aliased(model.Kasutaja, name='opetaja')
            Testiopetaja2 = sa.orm.aliased(model.Testiopetaja)
            Opetaja2 = sa.orm.aliased(model.Kasutaja, name='opetaja2')            
            q = (q.outerjoin(model.Sooritaja.testiopetajad)
                 .outerjoin((Opetaja, Opetaja.id==model.Testiopetaja.opetaja_kasutaja_id))
                 .filter(sa.or_(model.Testiopetaja.id==None,
                                ~ sa.exists().where(sa.and_(
                                    Testiopetaja2.sooritaja_id==model.Sooritaja.id,
                                    Testiopetaja2.opetaja_kasutaja_id==Opetaja2.id,
                                    Opetaja2.nimi<Opetaja.nimi))
                                )
                              )
                 )
        return q

    def _get_opt(self, q):
        "Leitakse filtri valikud vastavalt testikoha sooritajate andmetele"
        c = self.c
        NULL = '-'
        NULL_TITLE = _("puudub")
        def _opt(q, id_field, title_field=None, sort_field=None, ftitle=None, fid=None):
            if title_field is None:
                title_field = id_field
            if sort_field is None:
                sort_field = title_field
            q_opt = (q.with_entities(id_field, title_field)
                     .distinct()
                     .order_by(sort_field)
                     )
            li = []
            is_null = False
            for (id, title) in q_opt.all():
                if fid:
                    id = fid(id)
                if ftitle:
                    title = ftitle(title)
                if not id:
                    is_null = True
                else:
                    li.append((id, title or NULL_TITLE))
            if is_null:
                # et tyhi string ja None ei oleks eraldi valikud, lisame yhe korra
                li.append((NULL, NULL_TITLE))
            return li

        def _checkexists(value, opts):
            """Kui suunatakse kõik sooritajad ühest ruumist ära, siis seda ruumi ei jää enam valikusse
            ning tuleks ka filtrist maha võtta"""
            if value and value != NULL:
                idlist = [r[0] for r in opts]
                if value in idlist or int(value) in idlist:
                    # valitud valik on jätkuvalt valikute seas
                    return value
            
        c.opt_testiruum = _opt(q,
                               model.Sooritus.testiruum_id,
                               model.Testiruum.tahis)
        c.testiruum_id = _checkexists(c.testiruum_id, c.opt_testiruum)
        
        c.opt_ruum = _opt(q,
                          model.Testiruum.ruum_id,
                          ftitle=lambda r_id: r_id and model.Ruum.get(r_id).tahis)
        c.ruum_id = _checkexists(c.ruum_id, c.opt_ruum)        
        c.opt_tprotokoll = _opt(q,
                                model.Sooritus.testiprotokoll_id,
                                model.Testiprotokoll.tahis)
        c.opt_aeg = _opt(q,
                         model.Sooritus.kavaaeg,
                         ftitle=self.h.str_from_datetime,
                         fid=lambda d: d and int(mktime(d.timetuple())))
        c.aeg = _checkexists(c.aeg, c.opt_aeg)                
        c.opt_koolinimi = _opt(q,
                               model.Sooritaja.koolinimi_id,
                               model.Koolinimi.nimi)
        c.opt_klass = _opt(q, model.Sooritaja.klass)
        c.opt_paralleel = _opt(q, model.Sooritaja.paralleel)
        c.opt_soorituskeel = _opt(q,
                                  model.Sooritaja.lang,
                                  sort_field=sa.func.lang_sort(model.Sooritaja.lang),
                                  ftitle=model.Klrida.get_lang_nimi)
        Opetaja = sa.orm.aliased(model.Kasutaja, name='opetaja')
        q_opetajad = (q.outerjoin(model.Sooritaja.testiopetajad)
                      .outerjoin((Opetaja, Opetaja.id==model.Testiopetaja.opetaja_kasutaja_id)))
        c.opt_opetaja = _opt(q_opetajad,
                             model.Testiopetaja.opetaja_kasutaja_id,
                             Opetaja.nimi)

    def _prepare_items(self, q):
        "Loetelu ridade andmete väljastamine (CSV jaoks)"
        if self.c.csvr:
            # ruumid
            header = self._prepare_header_r()
            items = [self._prepare_item_r(rcd) for rcd in self.c.testikoht.testiruumid]
        else:
            # sooritajad
            header = self._prepare_header()
            items = [self._prepare_item(rcd) for rcd in q.all()]            
        return header, items
   
    def _prepare_header_r(self):
        c = self.c
        header = [_("Testiruum"),
                  _("Ruum"),
                  _("Kohti"),
                  _("Sooritajaid"),
                  ]
        c.sorted_paketid = sorted(c.testikoht.testipaketid,
                                  key=lambda r: model.lang_sort(r.lang))
        for tpakett in c.sorted_paketid:
            if len(c.sorted_paketid) == 1:
                header.append(_("Protokollirühmad"))
            else:
                header.append(_("Protokollirühmad") + ' (%s)' % tpakett.lang_nimi)
        for grupp_id in c.grupid_id:
            header.append(model.Kasutajagrupp.get(grupp_id).nimi)
        header.append(_("Algus"))
        return header
    
    def _prepare_item_r(self, rcd):
        c = self.c
        item = [rcd.tahis,
                rcd.ruum and rcd.ruum.tahis,
                rcd.kohti,
                len(rcd.sooritused),
                ]
        for tpakett in c.sorted_paketid:
            buf = ''
            for tpr in rcd.testiprotokollid:
                tpr_arv = tpr.soorituste_arv
                if tpr.testipakett_id == tpakett.id:
                    buf += tpr.tahis
                    if tpr.kursus_kood:
                        buf += ' (%s, %s)' % (tpr.kursus_nimi, tpr_arv)
                    else:
                        buf += ' (%s)' % (tpr_arv)
            item.append(buf)
        for grupp_id in c.grupid_id:
            buf = ''
            for lv in rcd.labiviijad:
                if lv.kasutajagrupp_id == grupp_id:
                    if lv.kasutaja_id:
                        buf += lv.kasutaja.nimi + ' '
            item.append(buf)
        item.append(self.h.str_from_datetime(rcd.algus))
        return item

    def _prepare_header(self):
        c = self.c
        header = [('sooritus.tahis', _("Tähis")),
                  ('kasutaja.isikukood', _("Isikukood")),
                  ('kasutaja.perenimi,kasutaja.eesnimi',_("Nimi")),
                  ('testiruum.tahis', _("Testiruum")),
                  ('ruum.tahis', _("Ruum")),
                  ('testiprotokoll.tahis', _("Protokollirühm")),
                  ('koolinimi.nimi', _("Õppeasutus")),
                  ('sooritaja.klass', _("Klass")),
                  ('sooritaja.paralleel', _("Paralleel")),
                  ('opetaja.nimi', _("Aineõpetaja")),
                  ('sooritaja.lang', _("Soorituskeel")),
                  ]
        testiosa = c.toimumisaeg.testiosa
        if testiosa.test.on_kursused:
            header.append(('sooritaja.kursus_kood', _("Kursus")))
        if c.vastvorm_kood in (const.VASTVORM_KE, const.VASTVORM_KP):
            header.append(('testiruum.algus', _("Aeg")))
        else:
            header.append(('sooritus.kavaaeg', _("Aeg")))
        return header
    
    def _prepare_item(self, rcd, n=None, is_html=False):
        c = self.c
        testiosa = c.toimumisaeg.testiosa
        peidus = c.toimumisaeg.testimiskord.sooritajad_peidus and '*'
        if peidus and is_html:
            peidus = '***********'            
        tos, s, k, tpr_tahis, tr_tahis, r_tahis, kool_nimi = rcd

        q_op = (model.Session.query(model.Kasutaja.nimi)
                .filter(model.Testiopetaja.sooritaja_id==tos.sooritaja_id)
                .join(model.Testiopetaja.opetaja_kasutaja)
                .order_by(model.Kasutaja.nimi))
        op_nimed = [nimi for nimi, in q_op.all()]
        if is_html:
            opetajad = op_nimed
        else:
            opetajad = ', '.join(op_nimed)

        if tr_tahis and not r_tahis:
            r_tahis = _("määramata")

        item = [tos.tahised,
                peidus or k.isikukood,
                peidus or s.nimi,
                tr_tahis,
                r_tahis,
                tpr_tahis,
                kool_nimi,
                s.klass,
                s.paralleel,
                ]
        n_opetajad = len(item)
        item.append(opetajad)
        item.append(model.Klrida.get_lang_nimi(s.lang))

        if testiosa.test.on_kursused:            
            item.append(s.kursus_nimi)
        testiruum = tos.testiruum
        if testiruum:
            algus = testiosa.vastvorm_kood in (const.VASTVORM_KE, const.VASTVORM_KP) and testiruum.algus or tos.kavaaeg
        else:
            algus = ''
        if is_html:
            n_aeg = len(item)
            item.append(self.h.str_from_datetime(algus, hour0=False))
            return item, tos, n_aeg, n_opetajad
        else:
            item.append(self.h.str_from_datetime(algus, hour0=False))
            return item

    def _index_ruumid(self):
        return self.render_to_response('avalik/korraldamine/sooritajad.ruumid.mako')

    def _index_markus(self):
        return self.render_to_response('avalik/korraldamine/sooritajad.markus.mako')

    def _index_keeled(self):
        li = self.request.params.getall('sooritus_id')
        for s_id in li:
            sooritus = model.Sooritus.get(s_id)
            self.c.default_lang = sooritus.sooritaja.lang
            break
        self.c.sooritused_id = ','.join(li)
        return self.render_to_response('avalik/korraldamine/sooritajad.keeled.mako')
    
    def _create(self):
        """Suunamine või aja salvestamine
        """
        if self.request.params.get('addr') or self.request.params.get('addp'):
            # vajutati nupule "Suuna valitud ruumi" või "Suuna valitud protokollirühma"
            return self._create_add()

        if self.request.params.get('addo'):
            # vajutati nupule "Märgi valitud aineõpetaja"
            return self._create_opetaja(True)        

        elif self.request.params.get('unseto'):
            # vajutati nupule "Eemalda aineõpetaja"
            return self._create_opetaja(False)

        elif self.request.params.get('proto'):
            # protokollide uuendamine
            return self._create_proto()

        # kellaaja salvestamine
        for rcd in self.form.data.get('s'):
            item = model.Sooritus.get(rcd.get('sooritus_id'))
            assert item.testikoht_id == self.c.testikoht.id and \
                   item.toimumisaeg_id == self.c.toimumisaeg.id, _("vale")
            kavaaeg = item.testiruum.algus
            kellaaeg = rcd.get('kellaaeg')
            if kellaaeg:
                kellaaeg = time(kellaaeg[0],kellaaeg[1])
                kavaaeg = datetime.combine(kavaaeg, kellaaeg)
            item.kavaaeg = kavaaeg
            #log.debug('item.kavaaeg=%s' % (item.kavaaeg.strftime('%d.%m.%Y %H:%I')))
        return self.c.testikoht

    def _create_proto(self):
        "Protokollirühmad luuakse uuesti"

        q = (model.Sooritus.query
             .filter_by(testikoht_id=self.c.testikoht.id)
             .join(model.Sooritus.sooritaja))
        if q.filter(model.Sooritus.klastrist_toomata==True).count() > 0:
            self.error(_("Enam ei saa protokollirühmi muuta, sest sooritamine juba käib!"))
            return self.c.testikoht
        
        list_sort = self.request.params.get('list_sort')
        if list_sort:
            # sorteerime sooritused selles järjekorras, milles kasutaja on loetelu järjestanud
            q = (q.join(model.Sooritaja.kasutaja)
                 .outerjoin(model.Sooritaja.koolinimi)
                 .outerjoin(model.Sooritaja.piirkond)
                 .join(model.Sooritus.testiruum)
                 .outerjoin(model.Testiruum.ruum)
                 .outerjoin(model.Sooritus.testiprotokoll)
                 )
            q = self._order(q, list_sort)
        else:
            # vaikimisi sordime nime järjekorras
            q = q.order_by(model.Sooritaja.perenimi,model.Sooritaja.eesnimi)
        sooritused = list(q.all())

        # tyhistame varasemad protokollidesse jaotamised
        for tos in sooritused:
            tos.testiprotokoll = None
            tos.tahis = tos.tahised = None
        self.c.testikoht.sooritused_seq = 0

        # valime kõigile sooritustele protokolli uuesti,
        # nii et protokollid järjest täituks
        for tos in sooritused:
            # suuname ruumi
            tos.suuna(tos.testikoht, tos.testiruum)
            if list_sort:
                # genereerime tähise selleks, et kasutaja valitud järjekorda säilitada
                tos.gen_tahis() 
                #tos.tahised = None # mitte lõpliku tähise mõttes

        # eemaldame tühjad protokollid 
        # ja tähistame alles jäävad protokollid uuesti
        self.c.testikoht.reset_testiprotokollid()

        return self.c.testikoht
            
    def _create_add(self):
        """Suunamine
        """
        errors = {}
        error = None
        
        # suunata saab kas üldiselt testiruumi või testiruumi sees olevasse testiprotokolli
        testiruum_id = self.request.params.get('testiruum_id')
        tpr_id = self.request.params.get('tpr_id')

        if not self.c.toimumisaeg.ruumide_jaotus:
            self.error(_("Soorituskohas ruumide määramine on lõpetatud"))
            return self.c.testikoht

        testiruum = None
        if testiruum_id:
            # suunamine ruumi
            testiruum = model.Testiruum.get(testiruum_id)
            if testiruum:
                assert testiruum.testikoht == self.c.testikoht, _("Vale koht")
            tpr = None
        elif tpr_id:
            # suunamine protokollirühma
            tpr = model.Testiprotokoll.get(tpr_id)
            testiruum = tpr.testiruum
            if testiruum:
                assert testiruum.testikoht == self.c.testikoht, _("Vale koht")

        if testiruum:
            testiruum.set_sooritajate_arv()
            testiruumid = set([testiruum])
            cnt = cnt_err = 0

            # mitu vaba kohta on ruumis
            r_vabukohti = vabukohti = testiruum.vabukohti
            if vabukohti is not None and vabukohti <= 0:
                self.error(_("Ruumis pole vabu kohti"))
                return self.c.testikoht                

            # mitu vaba kohta on protokollis
            if tpr:
                max_size = self.c.toimumisaeg.protok_ryhma_suurus
                if not max_size:
                    p_vabukohti = None
                else:
                    p_vabukohti = max_size - len(tpr.sooritused)
                    if p_vabukohti <= 0:
                        self.error(_("Protokollirühma sooritajate arv on täis"))
                        return self.c.testikoht

            tpv = testiruum.toimumispaev

            # tsykkel yle soorituste
            sooritused_id = self.request.params.getall('sooritus_id')
            for sooritus_id in sooritused_id:
                item = model.Sooritus.get(sooritus_id)
                # kontrollime, et on oma
                assert item.testikoht_id == self.c.testikoht.id and \
                    item.toimumisaeg_id == self.c.toimumisaeg.id, _("Vale koht")
                
                # kontrollime, et ruumis on vabu kohti
                if item.testiruum_id != testiruum.id:
                    if r_vabukohti is not None:
                        if r_vabukohti <= 0:
                            self.error(_("Ruumis oli ainult {n} vaba kohta").format(n=vabukohti))
                            log.info(_("Ruumis oli ainult {n} vaba kohta").format(n=vabukohti))
                            break
                        r_vabukohti -= 1
                
                # kontrollime, et testiprotokollis on vabu kohti
                if tpr and item.testiprotokoll_id != tpr.id:
                    if p_vabukohti is not None:
                        if p_vabukohti <= 0:
                            error = _("Protokollirühmas ei tohi olla üle {n} sooritaja").format(n=max_size)
                            break
                        p_vabukohti -= 1

                if item.testiruum_id != testiruum.id or tpr and item.testiprotokoll_id != tpr.id:
                    # suuname sooritaja ümber
                    if item.reg_toimumispaev_id and testiruum.toimumispaev_id != item.reg_toimumispaev_id:
                        msg = _("Sooritajale määratud toimumispäeva ei ole lubatud muuta")
                        errors['err_sooritus_%s' % sooritus_id] = msg
                        cnt_err += 1
                        continue
                    if tpv and (tpv.valim == False) and item.sooritaja.valimis:
                        # uus ruum on lubatud ainult mitte-valimi sooritajatele
                        msg = _("Valitud ruumi aeg pole valimi sooritajatele lubatud")
                        errors['err_sooritus_%s' % sooritus_id] = msg
                        cnt_err += 1
                        continue
                    old = item.testiruum
                    if old:
                        testiruumid.add(old)
                    if item.suuna(self.c.testikoht, testiruum, tpr):
                        cnt += 1
                    else:
                        cnt_err += 1

            if cnt:
                model.Session.flush()
                for testiruum in testiruumid:
                    testiruum.set_sooritajate_arv()
            if cnt_err:
                self.error(_("{n} sooritajat ei saanud ümber suunata").format(n=cnt_err))

        if errors or error:
            # kuvame vea värviga need sooritajad, keda ei saanud suunata
            model.Session.commit()
            raise ValidationError(self, errors, message=error)

        return self.c.testikoht

    def _create_opetaja(self, is_add):
        """Aineõpetaja määramine või eemaldamine
        """
        koht = self.c.testikoht.koht
        test = self.c.toimumisaeg.testiosa.test
        opetajad_id = []
        if is_add:
            # õpetaja määramine
            s_opetajad_id = self.request.params.getall('opetaja_id')
            for opetaja_id in s_opetajad_id:
                opetaja = koht.get_aineopetajad(test.aine_kood, opetaja_id)
                if opetaja:
                    opetajad_id.append(opetaja.id)
                    
        # tsykkel yle soorituste
        sooritused_id = self.request.params.getall('sooritus_id')
        for sooritus_id in sooritused_id:
            item = model.Sooritus.get(sooritus_id)
            # kontrollime, et on oma
            assert item.testikoht_id == self.c.testikoht.id and \
                   item.toimumisaeg_id == self.c.toimumisaeg.id, _("Vale koht")
            sooritaja = item.sooritaja
            # märgime õpetajad
            found_id = []
            for top in list(sooritaja.testiopetajad):
                if top.opetaja_kasutaja_id in opetajad_id:
                    # määratav õpetaja on juba varem määratud
                    found_id.append(top.opetaja_kasutaja_id)
                else:
                    # varem on määratud teine õpetaja, eemaldame varasema
                    top.delete()
            for opetaja_id in opetajad_id:
                if opetaja_id not in found_id:
                    # määrame uue õpetaja
                    top = model.Testiopetaja(opetaja_kasutaja_id=opetaja_id,
                                             sooritaja_id=sooritaja.id)
        return self.c.testikoht

    def _create_ruumid(self):
        """Ruumide valik dialoogiaknas, salvestamine
        """
        def _error_create(errors):
            e = ValidationError(self, errors)
            if errors:
                self.form.errors = errors
            log.debug(self.form.errors)
            model.Session.rollback()
            html = self.form.render('avalik/korraldamine/sooritajad.ruumid.mako', extra_info=self.response_dict)
            return Response(html)

        if not self.c.toimumisaeg.ruumide_jaotus:
            self.error(_("Soorituskohas ruumide määramine on lõpetatud"))
            return self._redirect('index')        

        self.form = Form(self.request, schema=forms.avalik.admin.TestiruumidForm)
        if not self.form.validate():
            self.c.nosub = True
            self.c.dialog_ruumid = True
            return _error_create(None)

        errors = dict()
        # testiruumid ruumide kaupa
        testiruumid = dict()
        for tr in self.c.testikoht.testiruumid:
            if tr.ruum_id in testiruumid:
                testiruumid[tr.ruum_id].append(tr)
            else:
                testiruumid[tr.ruum_id] = [tr]

        class TestiruumGridController(BaseGridController):
            def create_subitem(self, rcd, lang=None):
                subitem = model.Testiruum()
                subitem.from_form(rcd, lang=lang)
                self._COLLECTION.append(subitem)
                self.parent.testiruumid.append(subitem)
                subitem.testikoht = self.parent
                subitem.gen_tahis()
                subitem.algus = subitem.uus_algus = rcd.get('uus_algus')
                return subitem
            
            def update_subitem(self, subitem, rcd, lang=None):
                subitem.from_form(rcd, lang=lang)
                subitem.uus_algus = rcd.get('uus_algus')
                return subitem

            def can_delete(self, subitem):
                return subitem.sooritajate_arv == 0 and len(subitem.sooritused) == 0

        # loeme postitatud andmed ja jagame ruumide kaupa
        rdata = {}
        rlist = []
        rfwd = {}
        for n_ruum, row in enumerate(self.form.data.get('ruum')):
            ruum_id = row.get('id')
            if not ruum_id:
                # määramata ruum, kas on valitud valikust uus ruum?
                uus_ruum_id = row.get('uus_ruum_id')
                if uus_ruum_id:
                    ruum_id = rfwd[None] = uus_ruum_id
            if ruum_id:
                ruum = model.Ruum.get(ruum_id)
                assert ruum.koht_id == self.c.testikoht.koht_id, _("Vale koha ruum")
            tr_rows = row.get('tr')
            if ruum_id not in rdata:
                rdata[ruum_id] = []
                rlist.append(ruum_id)
            rdata[ruum_id].append((n_ruum, tr_rows))

        # jagame andmebaasis olevad testiruumid ruumide kaupa
        testiruumid = dict()
        for tr in self.c.testikoht.testiruumid:
            ruum_id = tr.ruum_id
            if ruum_id is None:
                # määramata ruum suunatakse kindlasse ruumi
                ruum_id = rfwd.get(ruum_id)
            if ruum_id in testiruumid:
                testiruumid[ruum_id].append(tr)
            else:
                testiruumid[ruum_id] = [tr]

        # salvestame muudatused
        voib_korduda = self.c.toimumisaeg.ruum_voib_korduda
        for ruum_id in rlist:
            paevad = set()
            tr_rows2 = [] # jada, kuhu on mitu jada kokku pandud, kui määramata ruum on teiseks ruumiks tõstetud
            for n_ruum, tr_rows in rdata[ruum_id]:
                for n_tr, tr_row in enumerate(tr_rows):
                    tr_row['ruum_id'] = ruum_id
                    toimumispaev_id = tr_row.get('toimumispaev_id')
                    if not voib_korduda:
                        if toimumispaev_id in paevad:
                            prefix = 'ruum-%d.tr-%d' % (n_ruum, n_tr)
                            errors['%s.toimumispaev_id' % prefix] = _("Üht ruumi ei tohi ühel toimumispäeval mitu korda kasutada")
                        paevad.add(toimumispaev_id)

                    tpv = model.Toimumispaev.get(toimumispaev_id)
                    if tpv:
                        kell = tr_row.get('kell')
                        if kell:
                            tr_row['uus_algus'] = datetime.combine(tpv.aeg, time(kell[0],kell[1]))
                        else:
                            tr_row['uus_algus'] = tpv.aeg

                        lopp = tr_row.get('t_lopp')
                        if lopp:
                            tr_row['lopp'] = datetime.combine(tpv.aeg, time(lopp[0],lopp[1]))
                        else:
                            tr_row['lopp'] = tpv.lopp

                    tr_rows2.append(tr_row)
                
            if ruum_id in testiruumid:
                ruumi_testiruumid = testiruumid[ruum_id]
            else:
                ruumi_testiruumid = list()
            g = TestiruumGridController(ruumi_testiruumid, model.Testiruum, parent=self.c.testikoht)
            g.save(tr_rows2)

            for testiruum in ruumi_testiruumid:
                if testiruum not in g.deleted:
                    self.c.testikoht.set_testiruum(testiruum)
                    testiruum.give_labiviijad()
                    try:
                        uus_algus = testiruum.uus_algus
                    except AttributeError:
                        pass
                    else:
                        if testiruum.algus != uus_algus:
                            testiruum.muuda_algus(uus_algus)
            
        if errors:
            return _error_create(errors)
                        
        ralgused = [tr.algus for tr in self.c.testikoht.testiruumid]
        if ralgused:
            self.c.testikoht.alates = min(ralgused)

        model.Session.commit()
        self.success()
        return self._redirect('index')        

    def _create_markus(self):
        """Märkuse salvestamine
        """
        self.c.testikoht.markus = self.request.params.get('markus')
        model.Session.commit()
        self.success()
        return self._redirect('index')        

    def _create_keeled(self):
        """Valitud sooritajate keele muutmine
        """
        err = None
        cnt = 0
        lang = self.params_lang()
        sooritused_id = self.request.params.get('sooritused_id')
        if not self._reg_kool_avatud():
            err = _("Registreerimisaeg on läbi, keelt muuta enam ei saa")
        elif lang in self.c.testimiskord.keeled:
            # toimumisajad, kus on kogused juba arvutatud
            kogustega_ta_id = [ta.id for ta in self.c.testimiskord.toimumisajad if ta.on_kogused]
            muudetud_ta_id = set()
            li = [r for r in sooritused_id.split(',') if r]
            for sooritus_id in li:
                sooritus = model.Sooritus.get(sooritus_id)
                if sooritus and sooritus.testikoht_id == self.c.testikoht.id:
                    sooritaja = sooritus.sooritaja
                    if sooritaja.lang != lang:
                        sooritaja.lang = lang
                        cnt += 1
                        for tos in sooritaja.sooritused:
                            if tos.staatus == const.S_STAATUS_TEHTUD:
                                err = _("Sooritaja {s1} on testiosa {s2} juba sooritanud, keelt muuta enam ei saa").format(s1=sooritaja.nimi, s2=tos.testiosa.tahis)
                                break
                            if tos.toimumisaeg_id in kogustega_ta_id:
                                # kui kogused on juba arvutatud, siis määrame
                                # peale keele muutmist uue testipaketi ja testiprotokolli
                                tos.suuna(tos.testikoht, tos.testiruum)
                                muudetud_ta_id.add(tos.toimumisaeg_id)
                                
                if err:
                    break

        if err:
            self.error(err)
        elif cnt:
            for ta_id in muudetud_ta_id:
                ta = model.Toimumisaeg.get(ta_id)
                if ta.on_ymbrikud:
                    ta.on_ymbrikud = 0
                if ta.on_kogused and ta.testiosa.vastvorm_kood in (const.VASTVORM_KP, const.VASTVORM_SP):
                    # p-testi korral tuleb kogused uuesti arvutada, kuna korraldajad
                    # soovivad, et osalejad oleks protokollis tähestiku järjekorras
                    ta.on_kogused = 0
            model.Session.commit()
            self.success('Muudetud %d sooritaja soorituskeel' % cnt)
        return self._redirect('index')        

    def _new_parool(self):
        self.c.items = []
        sooritused_id = self.request.params.getall('sooritus_id')
        for sooritus_id in sooritused_id:
            sooritus = model.Sooritus.get(sooritus_id)
            sooritaja = sooritus.sooritaja
            assert sooritus.testikoht_id == self.c.testikoht.id, _("Vale koht")            
            self.c.items.append(sooritus)
        return self.render_to_response('/avalik/korraldamine/sooritajad.paroolid.mako')            

    def _create_parool(self):
        self.c.items = []
        sooritused_id = self.request.params.getall('pwd_id')
        for sooritus_id in sooritused_id:
            sooritus = model.Sooritus.get(sooritus_id)
            assert sooritus.testikoht_id == self.c.testikoht.id, _("Vale koht")
            sooritaja = sooritus.sooritaja
            kasutaja = sooritaja.kasutaja
            pwd = User.gen_pwd(6, True)
            sooritaja.set_password(pwd, userid=kasutaja.isikukood)
            self.c.items.append((kasutaja.isikukood, sooritaja.eesnimi, sooritaja.perenimi, pwd))
        model.Session.commit()
        return self.render_to_response('/avalik/korraldamine/sooritajad.paroolid.print.mako')    

    def _reg_kool_avatud(self):
        "Kas registreerimine on veel avatud"
        if not self.c.toimumisaeg.on_kogused:
            return True
        tk = self.c.testimiskord
        dt = date.today()
        reg_kool = tk.reg_kool_eis or \
                   tk.reg_kool_valitud and tk.on_regkoht(self.c.testikoht.koht_id)                
        return reg_kool and tk.reg_kool_alates and tk.reg_kool_kuni and \
               tk.reg_kool_alates<=dt and tk.reg_kool_kuni>=dt

    def _index_kopeeri(self):
        """Teiste toimumisaegade valimine kopeerimiseks
        """
        # milliseid läbiviijaid saab kool antud toimumisajal määrata?
        self.c.lvrollid = self.c.toimumisaeg.get_labiviijagrupid_opt(True)
        lvr_id = [r[0] for r in self.c.lvrollid]
        self.c.ta_lvr_id = {}
        
        # leiame sama testimiskorra kõik toimumisajad
        # ning kas minu koolis on ruumid ja läbiviijad sellele määratud
        self.c.tadata = []
        for ta in self.c.toimumisaeg.testimiskord.toimumisajad:
            osa = ta.testiosa
            testikoht = (model.Session.query(model.Testikoht)
                         .filter_by(toimumisaeg_id=ta.id)
                         .filter_by(koht_id=self.c.user.koht_id)
                         .first())
            on_testikoht = testikoht is not None
            on_ruumid = on_testikoht and tkoht_on_ruumid(osa, ta, testikoht)       
            on_labiviijad = on_testikoht and tkoht_on_labiviijad(osa, ta, testikoht)
            self.c.tadata.append((osa, ta, on_testikoht, on_ruumid, on_labiviijad))

            # leiame antud toimumisaja ja praeguse toimumisaja läbiviijarollide ühisosa
            self.c.ta_lvr_id[ta.id] = [r[0] for r in ta.get_labiviijagrupid_opt(True) \
                                       if r[0] in lvr_id]
            
        return self.render_to_response('/avalik/korraldamine/kopeeri.toimumisajad.mako')

    def _create_kopeeri(self):
        """Teise toimumisaja andmete kopeerimine.
        ES-2544
        Kopeeritakse grupid, ruumid, ruumide kellaajad, kuupäev;
        salvestamiseks ei tohi aeg (kas kuupäev või kellaaeg) kattuda.
        Kopeeritakse ka testi administraatorid, ei kopeerita hindajaid.
        """
        err = None
        if not self.c.toimumisaeg.ruumide_jaotus:
            err = _("Ruumide määramine ei ole lubatud")
            self.error(err)
            return self._redirect('index')

        # leiame toimumisaja, mille andmed kopeerida
        ta_id = self.request.params.get('ta_id')
        ta = model.Toimumisaeg.get(ta_id)
        assert ta.testimiskord_id == self.c.testimiskord.id, _("Vale testimiskord")
        assert ta != self.c.toimumisaeg, _("Vale toimumisaeg")

        # kas kirjutada ruumidesse määramine üle
        koht_yle = True
        # millised läbiviijarollid kopeerida
        lvrollid_id = list(map(int, self.request.params.getall('lvr_id')))
        
        uus_testiosa = self.c.toimumisaeg.testiosa
        if self._copy_testikoht(self.c.testikoht, uus_testiosa, ta, koht_yle, lvrollid_id):
            model.Session.commit()
            self.success(_("Toimumisaja andmed on kopeeritud"))
        return self._redirect('index')

    def _copy_testikoht(self, uus_testikoht, uus_testiosa, ta, koht_yle, lvrollid_id):
        # kopeerime, käies kõik teise toimumisaja ruumid läbi
        q = (model.Session.query(model.Testikoht)
             .filter(model.Testikoht.toimumisaeg_id==ta.id)
             .filter(model.Testikoht.koht_id==uus_testikoht.koht_id)
             )
        testikoht = q.first()
        if not testikoht:
            koht = uus_testikoht.koht
            self.error(_("{s} ei ole kopeeritava toimumisaja soorituskoht, seetõttu ei saa andmeid sealt kopeerida").format(s=koht.nimi))
            return False

        # eemaldame olemasolevad testiprotokollid
        for tos in uus_testikoht.sooritused:
            if tos.testiprotokoll_id:
                tos.testiprotokoll_id = None
        model.Session.flush()
        
        m_labiviijad = []
        uus_toimumisaeg = uus_testikoht.toimumisaeg
        toimumispaevad = list(uus_toimumisaeg.toimumispaevad)

        # eri toimumisaegade toimumispäevade vastavus 
        map_tpv = {}
        for src, dst in zip(list(ta.toimumispaevad), toimumispaevad):
            map_tpv[src.id] = dst.id

        # senised ruumid
        senised = [tr.id for tr in uus_testikoht.testiruumid]
        
        # ruumide kopeerimine
        map_testiruumid = {}
        vanad_testiruumid = {tr.tahis: tr for tr in uus_testikoht.testiruumid}
        for testiruum in list(testikoht.testiruumid):
            # leiame toimumispäeva vaste
            uus_tpv_id = map_tpv.get(testiruum.toimumispaev_id)
            
            # leiame ja vajadusel loome testiruumi
            # kui sama tähisega ruum on juba olemas, siis seotakse see uue ruumiga
            tahis = testiruum.tahis
            ruum_id = testiruum.ruum_id
            uus_testiruum = uus_testikoht.give_testiruum(ruum_id, tahis, uus_tpv_id)
            map_testiruumid[testiruum.id] = uus_testiruum
            
        model.Session.flush()
        # kohaga seotud läbiviijate kopeerimine
        if uus_toimumisaeg.labiviijate_jaotus and uus_testikoht.id and lvrollid_id:
            li = self._copy_k_labiviijad(uus_toimumisaeg, uus_testikoht, testikoht, lvrollid_id)
            m_labiviijad.extend(li)
            
        # sooritajate kopeerimine
        for testiruum in testikoht.testiruumid:
            uus_testiruum = map_testiruumid[testiruum.id]

            # loome läbiviijate kirjed
            uus_testiruum.give_labiviijad()
            # ruumiga seotud läbiviijate kopeerimine
            if uus_toimumisaeg.labiviijate_jaotus and uus_testiruum.id and lvrollid_id:
                li = self._copy_r_labiviijad(uus_toimumisaeg, uus_testiruum, testiruum, lvrollid_id)
                m_labiviijad.extend(li)
                                    
            # lisame sooritajad sinna ruumi (ka siis, kui oli juba ruumi suunatud)
            for sooritus in testiruum.sooritused:
                sooritaja = sooritus.sooritaja
                if not sooritus.testiruum_id:
                    # kui sooritaja ei olnud lähte-toimumisajal ruumi suunatud,
                    # siis tema testiruumi ei muudeta
                    continue
                if sooritaja.staatus < const.S_STAATUS_REGATUD:
                    # pooleli registreeringut ei kopeeri
                    continue
                # leiame sama sooritaja soorituse kirje praegusel toimumisajal
                uus_sooritus = sooritaja.give_sooritus(uus_testiosa.id)
                if uus_sooritus.staatus > const.S_STAATUS_ALUSTAMATA:
                    # sooritaja on juba sooritamist alustanud, ei muuda midagi
                    continue

                if uus_testiruum.kohti is None or \
                        uus_testiruum.kohti > (uus_testiruum.sooritajate_arv or 0):
                    # kui on kohti, siis suuname
                    uus_tpr = None
                    if koht_yle:
                        # peab sama testiprotokolli tähis jääma
                        tpr = sooritus.testiprotokoll
                        if tpr:
                            tpakett = tpr.testipakett
                            if tpakett:
                                # p-test
                                paketiruum = tpakett.testiruum and uus_testiruum or None
                                uus_tpakett = uus_testikoht.give_testipakett(tpakett.lang, paketiruum)
                            else:
                                uus_tpakett = None
                            uus_tpr = uus_testikoht.give_testiprotokoll(uus_testiruum, uus_tpakett, tpr.tahis)

                    if not uus_sooritus.suuna(uus_testikoht, uus_testiruum, uus_tpr):
                        self.error(_("Suunamisi ei saa kopeerida (kontrollige protokollirühma suurust)"))
                        model.Session.rollback()
                        return False

                    uus_sooritus.kavaaeg = uus_testiruum.algus
                    if koht_yle:
                        # peab sama soorituse tähis jääma
                        uus_testikoht.sooritused_seq += 1
                        if sooritus.tahis:
                            uus_sooritus.tahis = sooritus.tahis
                            uus_sooritus.tahised = '%s-%s' % (uus_testikoht.tahis, sooritus.tahis)
                    #uus_testiruum.sooritajate_arv += 1
            model.Session.flush()
            uus_testiruum.set_sooritajate_arv()

        uued = [tr.id for tr in map_testiruumid.values()]
        for testiruum_id in senised:
            if testiruum_id:
                testiruum = model.Testiruum.get(testiruum_id)
                testiruum.set_sooritajate_arv()
                if testiruum.sooritajate_arv == 0 and testiruum_id not in uued:
                    testiruum.delete()
                
        # läbiviija määramise teadete saatmine
        for lv, k in m_labiviijad:
            send_labiviija_maaramine(self, lv, k, uus_toimumisaeg)
        return True

    def _copy_k_labiviijad(self, uus_toimumisaeg, uus_testikoht, testikoht, lvrollid_id):
        "Koha läbiviijate kopeerimine (komisjoni esimees või liige)"
        added = []
        q = (model.Session.query(model.Labiviija)
             .filter(model.Labiviija.kasutajagrupp_id.in_(lvrollid_id))
             .filter(model.Labiviija.testiruum_id==None)
             .filter(model.Labiviija.testikoht_id==testikoht.id)
             .filter(model.Labiviija.kasutaja_id!=None))                 
        for lv in q.all():
            grupp_id = lv.kasutajagrupp_id
            k_id = lv.kasutaja_id
            # rolli päring
            q1 = (model.Session.query(model.Labiviija)
                  .filter(model.Labiviija.testiruum_id==None)
                  .filter(model.Labiviija.testikoht_id==uus_testikoht.id)
                  .filter(model.Labiviija.kasutajagrupp_id==grupp_id))
            # kas antud kasutaja on selles rollis juba?
            q2 = q1.filter(model.Labiviija.kasutaja_id==k_id)
            uus_lv = q2.first()
            if not uus_lv:
                # lisada kasutaja rolli
                k = model.Kasutaja.get(k_id)
                # kas leidub läbiviija kirje ilma kasutajata?
                uus_lv = q1.filter(model.Labiviija.kasutaja_id==None).first()
                if not uus_lv:
                    # loome uue läbiviija kirje
                    uus_lv = uus_testikoht.create_labiviija(grupp_id)
                uus_lv.set_kasutaja(k, uus_toimumisaeg)
                added.append((uus_lv, k))
                log.debug(f'kopeeritud k lv {grupp_id} {k.nimi}')
                model.Session.flush()
        return added

    def _copy_r_labiviijad(self, uus_toimumisaeg, uus_testiruum, testiruum, lvrollid_id):
        "Ruumi läbiviijate kopeerimine (testi admin, intervjueerija, suuline hindaja)"
        added = []
        q = (model.Session.query(model.Labiviija)
             .filter(model.Labiviija.kasutajagrupp_id.in_(lvrollid_id))
             .filter(model.Labiviija.testiruum_id==testiruum.id)
             .filter(model.Labiviija.kasutaja_id!=None))
        for lv in q.all():
            grupp_id = lv.kasutajagrupp_id
            k_id = lv.kasutaja_id
            # rolli päring
            q1 = (model.Session.query(model.Labiviija)
                  .filter(model.Labiviija.testiruum_id==uus_testiruum.id)
                  .filter(model.Labiviija.kasutajagrupp_id==grupp_id))
            # kas antud kasutaja on selles rollis juba?
            q2 = q1.filter(model.Labiviija.kasutaja_id==k_id)
            uus_lv = q2.first()
            if not uus_lv:
                # lisada kasutaja rolli
                k = model.Kasutaja.get(k_id)
                # kas leidub läbiviija kirje ilma kasutajata?
                uus_lv = q1.filter(model.Labiviija.kasutaja_id==None).first()
                if not uus_lv:
                    # loome uue läbiviija kirje
                    uus_lv = uus_testiruum.create_labiviija(grupp_id)
                uus_lv.set_kasutaja(k, uus_toimumisaeg)
                added.append((uus_lv, k))
                log.debug(f'kopeeritud r lv {grupp_id} {k.nimi}')                        
                model.Session.flush()
        return added
    
    def _error_create(self):
        form = self.form
        self.form = None
        extra_info = self._index_d()
        if isinstance(extra_info, (HTTPFound, Response)):
            return extra_info    
        html = form.render(self._INDEX_TEMPLATE, extra_info=extra_info)            
        return Response(html)

    def _after_update(self, id):
        """Mida teha peale õnnestunud salvestamist
        """
        if not self.has_errors():
            self.success()
        url = self.request.params.get('list_url')
        if url:
            # säilitame otsingutingimused
            return HTTPFound(location=url)
        return self._redirect('index', id)

    def __before__(self):
        c = self.c
        testikoht_id = self.request.matchdict.get('testikoht_id')
        c.testikoht = model.Testikoht.get(testikoht_id)
        if c.testikoht:
            c.toimumisaeg = c.testikoht.toimumisaeg
            c.testimiskord = c.toimumisaeg.testimiskord

    def _perm_params(self):
        c = self.c
        if not c.testikoht or c.testikoht.koht_id != c.user.koht_id:
            return False
