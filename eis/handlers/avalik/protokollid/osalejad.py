from eis.lib.baseresource import *
from eis.lib.examclient import ExamClient
from eis.lib.resultentry import ResultEntry
_ = i18n._
log = logging.getLogger(__name__)

class OsalejadController(BaseResourceController):
    """Protokollide otsing soorituskohas
    """
    _INDEX_TEMPLATE = 'avalik/protokollid/osalejad.mako'
    _DEFAULT_SORT = 'sooritus.tahis'
    _log_params_post = True
    _MODEL = model.Sooritus
    _EDIT_TEMPLATE = 'ekk/sisestamine/protokoll.osalejad.ylesanded.mako' # testiosa ylesannete hinnete salvestamine

    @property
    def _ITEM_FORM(self):
        if self.c.action == 'update':
            # yhe sooritaja ylesannete tulemuste salvestamine
            return forms.avalik.admin.ProtokollOsalejadYlesandedForm
        elif self.c.testimiskord.prot_tulemusega:
            # protokolli salvestamine koos testiosade tulemustega 
            return forms.avalik.admin.ProtokollOsalejadTulemusegaForm
        else:
            # protokolli salvestamine
            return forms.avalik.admin.ProtokollOsalejadForm

    _index_after_create = True
    _no_paginate = True

    def _query(self):
        q = (model.Sooritus.query
             .join(model.Sooritus.testiprotokoll)
             .join(model.Sooritus.sooritaja)
             .filter(model.Sooritaja.staatus>const.S_STAATUS_REGAMATA)
             )
        if not self.voib_koik_ruumid:
            q = q.filter(model.Sooritus.testiruum_id.in_(self.voib_testiruumid_id))
        return q

    def _search_default(self, q):
        return self._search(q)

    def _search(self, q):
        if self.c.testiruum:
            # protokoll käib testiruumi kohta
            q = q.filter(model.Sooritus.testiruum_id==self.c.testiruum.id)
            q = q.filter(model.Sooritus.staatus!=const.S_STAATUS_VABASTATUD)
        else:
            q = q.filter(model.Sooritus.testikoht_id==self.c.testikoht.id)
            if self.c.testiruum_id:
                # mitme testiruumiga protokollist täidetakse ainult yhe testiruumi andmed
                q = q.filter(model.Sooritus.testiruum_id==self.c.testiruum_id)
                q = q.filter(model.Sooritus.staatus!=const.S_STAATUS_VABASTATUD)                
                if not self.voib_koik_ruumid and int(self.c.testiruum_id) not in self.voib_testiruumid_id:
                    self.error('Kasutajal pole valitud testiruumile ligipääsu')

        if self.c.toimumisprotokoll.lang:
            q = q.filter(model.Sooritaja.lang==self.c.toimumisprotokoll.lang)

        if self.c.ei_nae_koiki:
            # aineõpetaja näeb ainult oma õpilasi
            q = q.filter(model.Sooritaja.testiopetajad.any(
                model.Testiopetaja.opetaja_kasutaja_id==self.c.ainult_opetaja_id))

        if self.c.protokoll_id:
            q = q.filter(model.Sooritus.testiprotokoll_id==self.c.protokoll_id)

        if self.c.testimiskord.prot_tulemusega:
            # protokoll kogu testi sooritamise kohta
            qp = q.filter(model.Sooritaja.staatus==const.S_STAATUS_POOLELI)
        else:
            # protokoll testiosa sooritamise kohta
            qp = q.filter(model.Sooritus.staatus==const.S_STAATUS_POOLELI)
        pooleli = qp.count()        
        if pooleli:
            self.error(_("{n} sooritajal on test veel pooleli. Peale protokolli salvestamist loetakse pooleli testid lõppenuks ja hiljem salvestatud vastuseid ei arvestata.").format(n=pooleli))
        self._get_labiviijad()
        if self.c.testimiskord.prot_vorm == const.PROT_VORM_ALATULEMUS:
            self._get_alatestid()
        #model.log_query(q)
        return q

    def _get_alatestid(self):
        "Alatestide tulemusega protokolli korral leiame alatestid"
        toimumisaeg = self.c.testikoht.toimumisaeg
        testiosa = toimumisaeg.testiosa
        q = (model.Session.query(model.Alatest.id,
                                 model.Alatest.seq,
                                 model.Alatest.max_pallid,
                                 model.Alatest.komplektivalik_id)
             .filter(model.Alatest.testiosa_id==testiosa.id)
             .order_by(model.Alatest.seq)
             )
        prev_kv_id = None
        data = []
        for a_id, a_seq, a_max_pallid, kv_id in q.all():
            if kv_id != prev_kv_id:
                prev_kv_id = kv_id
                data.append((_("Komplekt"), 'K%s' % kv_id))
            label = "%s (%sp)" % (a_seq, self.h.fstr(a_max_pallid or 0))
            data.append((label, 'A%s' % a_id))
        label = "%s (%sp)" % (_("Kokku"), self.h.fstr(testiosa.max_pallid or 0))
        data.append((label, 'O'))
        self.c.alatestid_col = data
        self.c.get_alatestitulemused = self._get_alatestitulemused
        
    def _get_alatestitulemused(self, sooritus):
        "Kutseeksami (alatestide tulemustega prot) korral leitakse alatestide tulemused"
        data = {}
        sooritus_id = sooritus.id

        if self.c.testimiskord.tulemus_koolile or self.c.app_ekk:
            if sooritus.staatus == const.S_STAATUS_TEHTUD and sooritus.pallid is not None:
                label = '%sp (%s%%)' % (self.h.fstr(sooritus.pallid,1), self.h.fstr(sooritus.tulemus_protsent,1))
                data = {'O': label}
            
            q = (model.Session.query(model.Alatestisooritus.alatest_id,
                                     model.Alatestisooritus.pallid,
                                     model.Alatestisooritus.tulemus_protsent)
                 .filter(model.Alatestisooritus.sooritus_id==sooritus_id)
                 .filter(model.Alatestisooritus.staatus==const.S_STAATUS_TEHTUD)
                 .filter(model.Alatestisooritus.pallid!=None))
            for a_id, pallid, prot in q.all():
                label = '%sp (%s%%)' % (self.h.fstr(pallid,1), self.h.fstr(prot,1))
                data['A%s' % a_id] = label

        q = (model.Session.query(model.Komplekt.tahis,
                                 model.Komplekt.komplektivalik_id)
             .distinct()
             .filter(model.Hindamisolek.sooritus_id==sooritus_id)
             .join(model.Hindamisolek.komplekt)
             )
        for k_tahis, kv_id in q.all():
            data['K%s' % kv_id] = k_tahis
        return data
        
    def _get_labiviijad(self):
        # testikoha läbiviijate loetelu
        if not self.c.testimiskord.prot_tulemusega:
            # prot_tulemusega korral läbiviijaid ei sisestata
            lvgrupid_id = (const.GRUPP_T_ADMIN,
                           const.GRUPP_VAATLEJA,
                           const.GRUPP_HINDAJA_S,
                           const.GRUPP_HINDAJA_S2,
                           const.GRUPP_INTERVJUU,
                           const.GRUPP_HIND_INT,
                           const.GRUPP_KOMISJON,
                           const.GRUPP_KOMISJON_ESIMEES,
                           const.GRUPP_KONSULTANT)
            q1 = (model.Labiviija.query
                  .filter(model.Labiviija.kasutajagrupp_id.in_(lvgrupid_id))
                  )
            if self.c.testiruum:
                q1 = q1.filter(model.Labiviija.testiruum_id==self.c.testiruum.id)
            elif self.c.testikoht:
                q1 = q1.filter(model.Labiviija.testikoht_id==self.c.testikoht.id)
                if self.c.testiruum_id:
                    q1 = q1.filter(model.Labiviija.testiruum_id==self.c.testiruum_id)                
                if not self.voib_koik_ruumid:
                    q1 = q1.filter(model.Labiviija.testiruum_id.in_(self.voib_testiruumid_id))
            
            q1 = q1.order_by(model.Labiviija.tahis)
            self.c.labiviijad = q1.all()

    def _get_opt_testiruumid(self):
        c = self.c
        self.voib_testiruumid_id = []
        if not c.testiruum and not c.testimiskord.prot_tulemusega:
            # kui protokoll ei käi yhe testiruumi kohta
            # aga käib yhe testikoha (yks toimumisaeg) kohta, 
            # siis leiame ruumide loetelu, et saaks protokolli täita ka ainult yhe ruumi kaupa
            perm_bit = c.is_edit and const.BT_UPDATE or const.BT_VIEW
            koht = c.testikoht.koht
            ta = c.testikoht.toimumisaeg
            self.voib_koik_ruumid = c.user.has_permission('tprotsisestus', perm_bit, obj=koht) or \
                                    c.user.has_permission('toimumisprotokoll', perm_bit, obj=c.toimumisprotokoll)
            q = (model.Session.query(model.Testiruum, model.Ruum.tahis, model.Toimumispaev.aeg)
                 .filter(model.Testiruum.testikoht_id==c.testikoht.id)
                 .join(model.Testiruum.toimumispaev)
                 .outerjoin(model.Testiruum.ruum)
                 )
            if not self.voib_koik_ruumid:
                if not ta.prot_admin:
                    # ei või midagi
                    return
                else:
                    # ei või kõiki ruume sisestada, võib oma administreeritud ruume sisestada
                    q = q.filter(model.Testiruum.labiviijad.any(
                        sa.and_(model.Labiviija.kasutaja_id==c.user.id,
                                model.Labiviija.staatus>const.L_STAATUS_KEHTETU,
                                model.Labiviija.kasutajagrupp_id==const.GRUPP_T_ADMIN))
                                 )
            q = q.order_by(model.Testiruum.tahis)
            li = []
            for testiruum, r_tahis, tp_aeg in q.all():
                tr_id, tr_tahis, tr_algus = testiruum.id, testiruum.tahis, testiruum.algus
                title = tr_tahis
                if r_tahis:
                    title += ' (%s)' % r_tahis
                title += ' %s' % self.h.str_from_datetime(tr_algus or tp_aeg)
                li.append((tr_id, title))
                self.voib_testiruumid_id.append(tr_id)

            c.opt_testiruumid = li
        else:
            self.voib_koik_ruumid = True

    def _prepare_header(self):
        "Loetelu päis"
        c = self.c
        if c.testimiskord.prot_vorm == const.PROT_VORM_ALATULEMUS:
            header = [_("Isikukood"),
                      _("Nimi"),
                      _("Olek"),
                      ]
            for label, col_id in c.alatestid_col:
                header.append(label)
        else:
            header = [_("Isikukood"),
                      _("Nimi"),
                      _("Tulemus"),
                      ]
            if c.testimiskord.prot_tulemusega:
                header.append(_("Tulemus protsentides"))
            header.append(_("Hinne"))
            testiosad = c.testimiskord.test.testiosad
            for testiosa in testiosad:
                header.append(testiosa.tahis)
                header.append('%s, %s' % (testiosa.tahis, _("osalemine")))
        return header

    def _prepare_item(self, rcd, n=None):
        "Loetelu rida"
        c = self.c
        avaldatud = c.testimiskord.tulemus_koolile
        sooritus = rcd
        sooritaja = sooritus.sooritaja
        kasutaja = sooritaja.kasutaja
        if c.testimiskord.prot_vorm == const.PROT_VORM_ALATULEMUS:
            item = [kasutaja.isikukood or '',
                    sooritaja.nimi,
                    sooritaja.staatus_nimi,
                    ]
            tos_data = self._get_alatestitulemused(sooritus)
            for label, col_id in c.alatestid_col:                
                item.append(tos_data.get(col_id))
        else:
            item = [kasutaja.isikukood or '',
                    sooritaja.nimi,
                    avaldatud and self.h.fstr(sooritaja.pallid) or '',
                    ]
            if c.testimiskord.prot_tulemusega:
                prot = sooritaja.tulemus_protsent
                if avaldatud and prot is not None:
                    prot = round(prot)
                else:
                    prot = ''
                item.append(prot)
            item.append(str(avaldatud and sooritaja.hinne or ''))

            testiosad = c.testimiskord.test.testiosad
            for testiosa in testiosad:
                tos = sooritaja.get_sooritus(testiosa_id=testiosa.id)
                item.append(tos and avaldatud and self.h.fstr(tos.pallid) or '')
                item.append(tos and tos.staatus_nimi or '')
                
        return item
            
    def download(self):
        c = self.c
        q = self._query()
        q = self._search(q).order_by(model.Sooritus.tahis)
        header, items = self._prepare_items(q)
        data = self._csv_data(header, items)
        data = utils.encode_ansi(data)
        fn = 'protokoll.csv'
        return utils.download(data, fn, const.CONTENT_TYPE_CSV)

    def _create(self):
        """Salvestamine
        """
        if not self.c.is_edit:
            return

        self._warnings = {}
        toimumisaeg = self.c.testikoht.toimumisaeg
        testiosa = toimumisaeg.testiosa

        if not self.c.ainult_opetaja_id:
            self.c.toimumisprotokoll.markus = self.form.data['markus']
        if not self.c.is_edit:
            self.error(_("Muudatusi ei saa enam teha"))
            return self._redirect('index')
               
        if self.c.testimiskord.prot_tulemusega:
            self._save_sooritajad()
        else:
            # c.testiruum on siis, kui protokoll käib testiruumi kohta
            if not self.c.testiruum:
                testiruum_id = self.form.data.get('testiruum_id')
                # testiruum_id on siis, kui mitme testiruumi protokollist täidetakse ühe testiruumi andmed
                if testiruum_id:
                    testiruum = model.Testiruum.get(testiruum_id)
                    assert testiruum.testikoht_id == self.c.testikoht.id, 'Vale testiruum'
                    self.c.testiruum = testiruum
                    
            self._save_sooritused()
            self._save_labiviijad()

        if self.c.testiruum:
            li = self.c.testiruum.labiviijad
        else:
            li = self.c.testikoht.labiviijad
        for lv in li:
            lv.calc_toode_arv()

        # salvestame tehtud tööde arvu, seda kasutatakse hindajatele ümbrike väljastamisel
        for pakett in self.c.toimumisprotokoll.testipaketid:
            pakett.calc_tehtud_toodearv()
        model.Session.flush()

        if self._warnings:
            model.Session.commit()
            err = _("Kõik andmed pole sisestatud. Sisestatud andmed on salvestatud.")
            raise ValidationError(self, self._warnings, message=err)
        return self.c.toimumisprotokoll

    def _save_sooritajad(self):
        "Tulemustega protokoll, mitme testiosaga"

        test = self.c.testimiskord.test
        resultentry = ResultEntry(self, None, test, None)
        errors = {}
        
        def _save_sooritus(sooritaja, tos, rcd_tos, prefix=None, muuda_pallid=True):
            pallid = rcd_tos['pallid']
            if tos.klastrist_toomata and sooritaja.klaster_id:
                if pallid == const.PUNKTID_VASTAMATA:
                    staatus = rcd_tos['staatus']
                elif pallid is not None:
                    staatus = const.S_STAATUS_TEHTUD
                toimumisaeg = tos.toimumisaeg
                testiosa = tos.testiosa
                self._end_test(sooritaja, tos, toimumisaeg, testiosa, staatus, None)

            # soorituse juurde viide, mille järgi saab kontrollida, et protokoll on kinnitatud
            tos.toimumisprotokoll_id = self.c.toimumisprotokoll.id
                
            if pallid == const.PUNKTID_VASTAMATA:
                # puudus, kõrvaldati või eemaldati
                tos.staatus = rcd_tos['staatus']
                tos.hindamine_staatus = const.H_STAATUS_HINDAMATA
                tos.pallid = tos.tulemus_protsent = None
            elif pallid is None:
                # sooritaja, kelle kohta andmeid ei sisestatud
                self._warnings['%s.staatus_err' % prefix] = _("Väärtus puudub")
                return
            else:
                tos.staatus = const.S_STAATUS_TEHTUD
                if muuda_pallid:
                    if pallid is None:
                        tos.hindamine_staatus = const.H_STAATUS_HINDAMATA
                    else:
                        tos.hindamine_staatus = const.H_STAATUS_HINNATUD
                    tos.pallid = pallid
                    tos_max_pallid = tos.max_pallid
                    if tos_max_pallid is not None:
                        if pallid > tos_max_pallid + .00001:
                            errors[prefix + '.pallid'] = _("Lubatud max {p}p").format(p=self.h.fstr(tos_max_pallid))
                            return
                    if pallid is not None and tos_max_pallid:
                        tos.tulemus_protsent = pallid * 100. / tos_max_pallid
                    else:
                        tos.tulemus_protsent = None
                        
            if muuda_pallid and self.c.testimiskord.prot_vorm == const.PROT_VORM_YLTULEMUS \
                   and tos.staatus == const.S_STAATUS_TEHTUD:
                # kontrollitakse ylesannete pallide summa
                total = 0
                for ty in tos.testiosa.testiylesanded:
                    yv = tos.get_ylesandevastus(ty.id)
                    if not yv or yv.pallid is None:
                        total = None
                        break
                    else:
                        total += yv.pallid
                if total != None and total != tos.pallid and prefix:
                    errors[prefix + '.pallid'] = _("Erineb ülesannete punktide summast")
                    return
                
            # seame alatestisoorituste olekud
            for alatest in tos.alatestid:
                atos = tos.give_alatestisooritus(alatest.id)
                if atos and atos.staatus == const.S_STAATUS_VABASTATUD:
                    # vabastatud alatestis ei saa soorituse olekut panna
                    continue
                atos.staatus = tos.staatus
            model.Session.flush()
            # loome hindamisolekud või kustutame, kui puudus
            tos.give_hindamisolekud()
            return True
        
        def _save_sooritaja(sooritaja, rcd):
            model.Session.flush()
            sooritaja.markus = rcd.get('markus')
            if not auto_hinded:
                sooritaja.hinne = rcd.get('hinne')

            sooritaja.update_staatus()
            # arvutame tulemuse protsendi ja hinde
            resultentry.update_sooritaja(sooritaja)
            
        def _get_valimid(tkord, li):
            "Leiame antud testimiskorrast moodustatud valimid ja neist omakorda moodustatud valimid jne"
            for r in tkord.valimid:
                if r not in li:
                    li.append(r)
                    _get_valimid(r, li)

        valimid = list()
        _get_valimid(self.c.testimiskord, valimid)

        auto_hinded = len(self.c.testimiskord.test.testihinded)
        testikohad_id = [r.id for r in self.c.testikohad]
        valim_protokollid = set()
        
        for n_s, rcd in enumerate(self.form.data['s']):
            # salvestame sooritaja osalemise ja tulemuse
            sooritaja = model.Sooritaja.get(rcd['id'])
            tos_rc = True
            for n_ta, rcd_tos in enumerate(rcd.get('tos')):
                prefix = 's-%s.tos-%s' % (n_s, n_ta)
                tos = model.Sooritus.get(rcd_tos['id'])
                testiosa = tos.testiosa
                toimumisaeg = tos.toimumisaeg
                assert tos.sooritaja_id == sooritaja.id, 'Vale sooritus'
                assert tos.testikoht_id in testikohad_id, 'Vale koht (sooritus "%s", lubatud "%s")' % (tos.testikoht_id, str(testikohad_id))
                tos.ylesanneteta_tulemus = True
                rc = _save_sooritus(sooritaja, tos, rcd_tos, prefix)
                if rc and tos.staatus == const.S_STAATUS_TEHTUD:
                    if testiosa.vastvorm_kood in (const.VASTVORM_KE, const.VASTVORM_SE, const.VASTVORM_I) and \
                           not tos.seansi_algus:
                        # ei luba märkida tehtuks e-sooritust, mida pole alustatudki
                        errors[prefix + '.pallid'] = _("Testi pole sooritatud")
                        rc = False
                if not rc:
                    tos_rc = False

            if tos_rc:
                model.Session.flush()
                _save_sooritaja(sooritaja, rcd)

                # muudame osalemise ja tulemuse sellest testimiskorrast moodustatud valimites 2015-06-30
                kasutaja_id = sooritaja.kasutaja_id
                for valim in valimid:
                    sooritaja = valim.get_sooritaja(kasutaja_id)
                    if sooritaja:
                        for rcd_tos in rcd.get('tos'):
                            orig_tos = model.Sooritus.get(rcd_tos['id'])                        
                            tos = sooritaja.get_sooritus(testiosa_id=orig_tos.testiosa_id)
                            _save_sooritus(sooritaja, tos, rcd_tos, muuda_pallid=tos.ylesanneteta_tulemus)
                        _save_sooritaja(sooritaja, rcd)
                        if tos.testiprotokoll_id:
                            valim_protokollid.add(tos.testiprotokoll_id)
        if errors:
            raise ValidationError(self, errors)
        
        # muudame läbiviijate oleku antud testimiskorral
        for testikoht in self.c.testikohad:
            for lv in testikoht.labiviijad:
                if lv.staatus in (const.L_STAATUS_MAARATUD,
                                  const.L_STAATUS_OSALENUD,
                                  const.L_STAATUS_PUUDUNUD):
                    lv.staatus = const.L_STAATUS_OSALENUD

        for tpr_id in valim_protokollid:
            tpr = model.Testiprotokoll.get(tpr_id)
            tpr.tehtud_toodearv = len([r for r in tpr.sooritused if r.staatus==const.S_STAATUS_TEHTUD])

    def _end_test(self, sooritaja, sooritus, toimumisaeg, testiosa, staatus, stpohjus):
        "Lõpetame pooleliolevad testid"
        test = self.c.test
        if sooritaja.klaster_id and sooritus.klastrist_toomata:
            host = model.Klaster.get_host(sooritaja.klaster_id)
            if host:
                # lõpetame testi
                sooritused_id = [sooritus.id]
                alatestid = []
                kirjalik = jatk_voimalik = None
                ExamClient(self, host).set_staatus(sooritus.testiruum_id,
                                                   sooritused_id,
                                                   staatus,
                                                   stpohjus,
                                                   testiosa,
                                                   alatestid,
                                                   kirjalik,
                                                   jatk_voimalik)
                # toome soorituse kirje keskserverisse
                ExamSaga(self).from_examdb(host, sooritus, sooritaja, test, testiosa, toimumisaeg, sooritaja.lang, True)
                
    def _save_sooritused(self):
        "Tulemusteta protokoll, ühe testiosaga"
        toimumisaeg = self.c.testikoht.toimumisaeg
        testiosa = toimumisaeg.testiosa
        test = testiosa.test
        errors = {}
        # kui osa on p-test, siis leiame teised sama testi p-testi osad
        p_osad_id = []
        if testiosa.vastvorm_kood in (const.VASTVORM_KP, const.VASTVORM_SP):
            for osa in test.testiosad:
                if osa.id != testiosa.id and osa.vastvorm_kood in (const.VASTVORM_KP, const.VASTVORM_SP):
                    p_osad_id.append(osa.id)

        for ind_s, rcd in enumerate(self.form.data['s']):
            prefix = 's-%d' % (ind_s)

            tos = model.Sooritus.get(rcd['id'])
            assert tos.testikoht_id == self.c.testikoht.id, 'Vale koht'
            if self.c.testiruum and tos.testiruum_id != self.c.testiruum.id:
                log.debug(f'vale ruum {self.c.testiruum.id} / sooritus {tos.id} ({tos.staatus}) testiruum {tos.testiruum_id}')
                continue
            if not self.voib_koik_ruumid and tos.testiruum_id not in self.voib_testiruumid_id:
                log.debug('testiruum pole lubatud')
                continue
            sooritaja = tos.sooritaja
            staatus = rcd['staatus']
            if staatus == const.S_STAATUS_TEHTUD:
                if testiosa.vastvorm_kood in (const.VASTVORM_KE, const.VASTVORM_SE, const.VASTVORM_I) and \
                       not tos.seansi_algus:
                    # ei luba märkida tehtuks e-sooritust, mida pole alustatudki
                    errors[prefix + '.staatus'] = _("Testi pole sooritatud")
                    continue

            if staatus:
                # konsultatsiooni korral ei ole vaja osaleja staatust märkida

                # katkestatuks või eemaldatuks märkimisel kysitakse avalikus vaates põhjust ES-3745
                if staatus in (const.S_STAATUS_KATKESPROT,
                               const.S_STAATUS_EEMALDATUD):
                    stpohjus = rcd.get('stpohjus')
                    if not stpohjus and self.c.app_eis:
                        errors[prefix + '.stpohjus'] = _("Palun sisestada põhjus")
                        continue
                else:
                    stpohjus = None
                # vajadusel lõpetame klastris
                self._end_test(sooritaja, tos, toimumisaeg, testiosa, staatus, stpohjus)
                    
                if tos.staatus != staatus or stpohjus:
                    tos.set_staatus(staatus, stpohjus)

                # p-testiosa korral täidame puudujad ja osalejad ka teistes
                # sama testi p-testiosades, kus veel pole protokollitud
                # (bugzilla 70, ES-317)
                if p_osad_id and \
                  staatus in (const.S_STAATUS_PUUDUS,
                              const.S_STAATUS_PUUDUS_VANEM,
                              const.S_STAATUS_PUUDUS_HEV,
                              const.S_STAATUS_TEHTUD):
                    for tos2 in sooritaja.sooritused:
                        if tos2.testiosa_id in p_osad_id:
                            if tos2.testiosa.vastvorm_kood in (const.VASTVORM_KP, const.VASTVORM_SP) and \
                                   tos2.staatus <= const.S_STAATUS_ALUSTAMATA:
                                tos2.set_staatus(staatus, stpohjus)
                                for alatest2 in tos2.alatestid:
                                    atos2 = tos2.give_alatestisooritus(alatest2.id)
                                    if atos2.staatus != const.S_STAATUS_VABASTATUD:
                                        atos2.staatus = tos2.staatus

            else:
                self._warnings[prefix + '.staatus_err'] = _("Väärtus puudub")

            tos.markus = rcd['markus'] or None
            tos.isikudok_nr = rcd['isikudok_nr'] or None
            tos.ylesanneteta_tulemus = False
            if not tos.algus and testiosa.vastvorm_kood in (const.VASTVORM_KP, const.VASTVORM_SP):
                tos.algus = tos.kavaaeg

            # soorituse juurde viide, mille järgi saab kontrollida, et protokoll on kinnitatud
            tos.toimumisprotokoll_id = self.c.toimumisprotokoll.id
            
            if staatus:
                # kui kasutaja sisestas soorituse staatuse
                # seame alatestisoorituste olekud
                a_staatused = []
                for alatest in tos.alatestid:
                    atos = tos.give_alatestisooritus(alatest.id)
                    if atos and atos.staatus == const.S_STAATUS_VABASTATUD:
                        # vabastatud alatestis ei saa soorituse olekut panna
                        continue
                    a_staatus = None
                    # kas kasutaja on staatuse sisestanud
                    for ats in rcd['ats']:
                        alatest_id = ats['id']
                        if alatest_id == alatest.id:
                            a_staatus = ats['staatus']
                    # kui kasutaja on midagi sisestanud, siis see saab staatuseks
                    if not a_staatus:
                        # kui ei ole kasutaja alatesti staatust sisestanud, aga sisestas testiosa staatuse,
                        # siis on sama staatus, mis sooritusel
                        a_staatus = staatus
                    if atos.staatus != a_staatus:
                        atos.staatus = a_staatus
                    a_staatused.append(a_staatus)

                if a_staatused:
                    if staatus == const.S_STAATUS_TEHTUD and staatus not in a_staatused or \
                           staatus == const.S_STAATUS_PUUDUS and const.S_STAATUS_TEHTUD in a_staatused:
                        # testiosas osales, aga yhelgi alatestil ei osalenud
                        # või testiosast puudus, aga mõnel alatestil osales
                        errors[prefix + '.staatus'] = _("Kontrolli lisainfo all alatestide sooritamise olekuid")
                        continue
                model.Session.flush()
                sooritaja.update_staatus()
                if p_osad_id:
                    # e-testi korral ei kuluta sellele aega
                    tos.give_hindamisolekud()

        if errors:
            raise ValidationError(self, errors)
        
    def _save_labiviijad(self):
        for rcd in self.form.data['lv']:
            lv_id = rcd['id']
            if lv_id:
                lv = model.Labiviija.get(lv_id)
                if lv and lv.testikoht_id == self.c.testikoht.id:
                    if not self.c.testiruum or lv.testiruum_id == self.c.testiruum.id:
                        lv.staatus = rcd['staatus']
                        lv.yleaja = rcd['yleaja']
                        if lv.yleaja and rcd['toolopp']:
                            minutes, seconds = rcd['toolopp']
                            lv.toolopp = datetime.combine(lv.toimumisaeg.alates, 
                                                          time(minutes, seconds))


    def _update(self, item, lang=None):
        is_delf = 'DELFscolaire' in self.c.testimiskord.test.nimi
        if self.c.testimiskord.prot_vorm == const.PROT_VORM_YLTULEMUS:
            # toimumisajal lubatud komplektid
            ta_komplektid_id = []
            for ta in self.c.testimiskord.toimumisajad:
                for k in ta.komplektid:
                    ta_komplektid_id.append(k.id)
            #ta_komplektid_id = [k.id for k in self.c.testikoht.toimumisaeg.komplektid]
            total = 0
            for n_ty, ydata in enumerate(self.form.data.get('ty')):
                ty_id = ydata['id']
                ty_pallid = ydata.get('pallid')
                yv = item.get_ylesandevastus(ty_id)
                if ty_pallid == None:
                    total = None
                else:
                    ty = model.Testiylesanne.get(ty_id)
                    if ty_pallid == const.PUNKTID_VASTAMATA:
                        ty_pallid = 0
                    if ty_pallid > ty.max_pallid:
                        message = _("Ühel ülesandel on liiga suur tulemus")
                        errors = {'ty-%d.pallid' % n_ty: 'Max %s' % self.h.fstr(ty.max_pallid)}
                        raise ValidationError(self, errors, message)
                    if total != None:
                        total += ty_pallid

                    # loome seose valitudylesandega
                    # valikylesande jrknr
                    vy_id = None
                    vy_seq = ydata.get('vy_seq')
                    if not vy_seq and not ty.on_valikylesanne:
                        vy_seq = 1
                    if vy_seq:
                        komplektivalik = ty.get_komplektivalik()
                        # toimumisajal lubatud komplektid selle ylesande jaoks
                        komplektid = [k for k in komplektivalik.komplektid if k.id in ta_komplektid_id]
                        if len(komplektid) == 1:
                            komplekt = komplektid[0]
                            vy = ty.get_valitudylesanne(komplekt, vy_seq)
                            vy_id = vy.id
                        else:
                            self.error(_("Ei saa määrata ülesandekomplekti"))
                    else:
                        errors = {'ty-%d.vy_seq' % n_ty: _("Väärtus puudub")}
                        raise ValidationError(self, errors)

                    if yv:
                        yv.valitudylesanne_id = vy.id
                    else:
                        yv = item.give_ylesandevastus(ty.id, vy_id)

                if yv:
                    yv.pallid = ty_pallid
            item.pallid = self.c.total = total
            if total is None:
                self.c.total = ''
            if item.testiosa.on_alatestid:
                item.calc_alatestitulemus(None, is_delf)
                
    def _after_update(self, id):
        """Mida teha peale õnnestunud salvestamist
        """        
        if self.c.action == 'update':
            # ylesannete tulemuste salvestamine
            # muudame ka testiosa pallid vormil
            buf = "<script> $('input.pallid-%s').val('%s').change();  close_dialog(); </script>" % (id, self.h.fstr(self.c.total))
            return Response(buf)
        else:
            # protokolli salvestamine
            if not self.has_errors():
                self.success()
            return self._redirect('index')

    def _error_create(self):
        self.c.testiruum_id = self.request.params.get('testiruum_id')
        form_save = self.form
        self.form = None
        extra_info = self._index_d()
        html = form_save.render(self._INDEX_TEMPLATE, extra_info=extra_info)            
        return Response(html)

    def __before__(self):
        c = self.c
        toimumisprotokoll_id = self.request.matchdict.get('toimumisprotokoll_id')
        c.toimumisprotokoll = model.Toimumisprotokoll.get(toimumisprotokoll_id)
        c.testimiskord = c.toimumisprotokoll.testimiskord
        c.test = c.testimiskord.test
        c.testikohad = list(c.toimumisprotokoll.testikohad)
        c.testikoht = c.toimumisprotokoll.testikoht
        c.testiruum = c.toimumisprotokoll.testiruum
        c.toimumisaeg1 = c.toimumisprotokoll.testikoht.toimumisaeg
        self._get_opt_testiruumid()
            
    def _perm_params(self):
        return {'obj': self.c.toimumisprotokoll}

    def _has_permission(self):
        c = self.c
        permissions = ('toimumisprotokoll','tprotsisestus')
        perm_bit = self._get_perm_bit()
        is_modify = self._is_modify()
        
        # leiame, kas on olemas praegu vajalik õigus
        rc = can_edit = False
        for permission in permissions:
            rc = c.user.has_permission(permission, perm_bit, obj=c.toimumisprotokoll)
            if rc:
                break

        if is_modify:
            # toimub muutmine
            # kui protokolli mõnel toimumisajal pole hindamiskirjed loodud, siis ei saa muuta
            for testikoht in c.testikohad:
                ta = testikoht.toimumisaeg
                if not ta.on_hindamisprotokollid:
                    log.debug('toimumisaeg(%s).on_hindamisprotokollid=%s' % (ta.id, ta.on_hindamisprotokollid))
                    rc = False
                    break
            can_edit = rc
        else:
            # kas on olemas muutmisõigus
            if not rc or is_modify:
                can_edit = rc
            else:
                for permission in permissions:
                    can_edit = c.user.has_permission(permission, const.BT_UPDATE, obj=c.toimumisprotokoll)
                    if can_edit:
                        break
        
        c.can_edit = can_edit
        if not rc:
            c.ei_nae_koiki = True

        if not can_edit and c.testimiskord.prot_tulemusega:
            # kui pole õigust protokollile, siis õpetajal on õigus oma õpilaste punktide sisestamiseks
            rc = c.user.has_permission('tprotopetaja', perm_bit, obj=c.toimumisprotokoll)
            if rc:
                # saab muuta ainult selle õpetaja õpilaste andmeid
                c.ainult_opetaja_id = c.user.id

        if rc and c.is_edit:
            self._check_is_edit()
        return rc

    def _check_is_edit(self):
        c = self.c
        not_yet = True
        for testikoht in c.testikohad:
            toimumisaeg = testikoht.toimumisaeg
            if not toimumisaeg.on_kogused:
                self.error(_("Toimumisaja {s} kogused on eksamikeskuses veel arvutamata").format(s=toimumisaeg.tahised))
                c.is_edit = False
            if not toimumisaeg.on_hindamisprotokollid:
                self.error(_("Toimumisaja hindamiskirjed on eksamikeskuses veel loomata"))
                c.is_edit = False            
            if testikoht.alates.date() <= date.today():
                not_yet = False
        if not_yet:
            self.error(_("Test ei ole veel toimunud"))
            c.is_edit = False
        if c.toimumisprotokoll.staatus in (const.B_STAATUS_KINNITATUD, const.B_STAATUS_EKK_KINNITATUD):
            c.is_edit = False
        elif not c.ainult_opetaja_id \
             and not c.user.has_permission('toimumisprotokoll', const.BT_UPDATE, c.toimumisprotokoll) \
             and not c.user.has_permission('tprotsisestus', const.BT_UPDATE, c.toimumisprotokoll) \
             and not c.user.has_permission('tprotadmin', const.BT_UPDATE, obj=c.toimumisprotokoll):                 
            c.is_edit = False

    def edit(self):
        id = self.request.matchdict.get('id')
        if self.c.ei_nae_koiki:
            # aineõpetaja näeb ainult oma õpilasi
            item = model.Sooritus.get(id)
            found = False
            for top in item.sooritaja.testiopetajad:
                if top.opetaja_kasutaja_id == self.c.ainult_opetaja_id:
                    found = True
                    break
            if not found:
                self.c.is_edit = False
        return BaseResourceController.edit(self)

    def _show_eri(self, id):
        return self._edit_eri(id)
    
    def _edit_eri(self, id):
        "Erivajaduste dialoogiaken, kus märgitakse, milliseid erivajadusi kasutati"
        self.c.item = model.Sooritus.get(id)
        return self.render_to_response('avalik/protokollid/osaleja.erivajadused.mako')

    def _update_eri(self, id):
        "Kasutatud erivajaduste märkimine"

        self.c.item = model.Sooritus.get(id)
        self.form = Form(self.request, schema=forms.avalik.admin.ProtokollOsalejadErivajadusedForm)
        if self.form.validate():
            for row in self.form.data['ev']:
                rcd = model.Erivajadus.get(row['id'])
                assert rcd.sooritus_id == self.c.item.id, 'Vale kirje'
                rcd.kasutamata = row['kasutamata']
            model.Session.commit()
            self.c.must_close = True
        return self._edit_eri(id)
                
