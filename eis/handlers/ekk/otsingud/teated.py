from eis.lib.baseresource import *
_ = i18n._
from eis.lib.pdf.labiviijateade import LabiviijateadeDoc
from eis.lib.pdf.vaatlejateade import VaatlejateadeDoc
from eis.lib.pdf.tulemus import TulemusDoc

log = logging.getLogger(__name__)

class TeatedController(BaseResourceController):
    """Teadete ülevaade
    saab vaadata saadetud teateid
    """
    _permission = 'aruanded-teated'
    _MODEL = model.Kiri
    _INDEX_TEMPLATE = 'ekk/otsingud/teated.mako'
    _LIST_TEMPLATE = 'ekk/otsingud/teated_list.mako'
    _EDIT_TEMPLATE = 'ekk/otsingud/teade.mako'
    _SEARCH_FORM = forms.ekk.otsingud.TeatedForm
    _ITEM_FORM = forms.ekk.otsingud.TeadeSaadaForm
    _DEFAULT_SORT = '-kiri.created,kasutaja.perenimi,kasutaja.eesnimi' 
            
    def _query(self):
        return None

    def _search_default(self, q):
        return None

    def _search(self, q1):
        c = self.c

        if c.toimumisaeg_id and not c.testimiskord_id:
            # juhuks, kui tuldi korraldamiselt otselingiga
            ta = model.Toimumisaeg.get(c.toimumisaeg_id)
            if ta:
                tk = ta.testimiskord
                c.testimiskord_id = tk.id
                c.sessioon_id = tk.testsessioon_id
                c.testiliik = tk.test.testiliik_kood

        c.on_tseis = on_tseis = c.testiliik in (const.TESTILIIK_TASE, const.TESTILIIK_SEADUS)

        # hargnemine:
        # sooritajakirjad / läbiviijakirjad / igasugused kirjad
        # yhe testi kirjad (tseis) / mitme testi kirjad (riigieksamid)

        # igal juhul päritakse need asjad
        self.li_select = [model.Kasutaja.id, 
                          model.Kasutaja.isikukood,
                          model.Kasutaja.synnikpv,
                          model.Kasutaja.nimi, 
                          model.Kirjasaaja.epost,
                          model.Kirjasaaja.isikukood,
                          model.Kirjasaaja.koht_id,
                          model.Kiri,
                          ]

        # saadetud kirjade vaatamine
        if c.styyp:
            if on_tseis:
                q = self._search_saadetud_sooritaja_testikaupa()
            else:
                q = self._search_saadetud_sooritaja_kasutajakaupa()
        elif c.ltyyp:
            q = self._search_saadetud_labiviija_kasutajakaupa()
        else:
            q = self._search_saadetud_kasutajakaupa()

        if c.saadetud_alates:
            q = q.filter(model.Kiri.created>=c.saadetud_alates)
        if c.saadetud_kuni:
            q = q.filter(model.Kiri.created<c.saadetud_kuni + timedelta(1))
        if c.teatekanal:
            q = q.filter(model.Kiri.teatekanal==c.teatekanal)
        if c.isikukood:
            usp = validators.IsikukoodP(self.c.isikukood)
            q = q.filter(usp.filter(model.Kasutaja))

        if c.eesnimi:
            q = q.filter(model.Kasutaja.eesnimi.ilike(c.eesnimi))
        if c.perenimi:
            q = q.filter(model.Kasutaja.perenimi.ilike(c.perenimi))

        if c.saatmata:
            c.arv = q.count()

        if c.csv:
            return self._index_csv(q)
        c.header = self._prepare_header()
        c.prepare_item = self._prepare_item

        return q

    def _search_saadetud_sooritaja_testikaupa(self):
        "TSEISi teated sooritajale"
        self.li_select += [model.Sooritaja.id,
                           model.Sooritaja.algus,
                           model.Test.nimi,
                           ]
        if self.c.testiliik == const.TESTILIIK_TASE:
            self.li_select.append(model.Testitase.keeletase_kood)

        q = (model.Session.query(*self.li_select)
             .join(model.Kasutaja.sooritajad)
             .join(model.Sooritaja.test)
             .filter(model.Test.testiliik_kood==self.c.testiliik)
             .join(model.Sooritaja.sooritajakirjad)
             .join(model.Sooritajakiri.kiri)
             .outerjoin((model.Kirjasaaja,
                         sa.and_(model.Kirjasaaja.kiri_id==model.Kiri.id,
                                 model.Kirjasaaja.kasutaja_id==model.Kasutaja.id)))
             )

        if self.c.testiliik == const.TESTILIIK_TASE:
            q = q.outerjoin((model.Testitase,
                             sa.and_(model.Testitase.test_id==model.Test.id,
                                     model.Testitase.seq==1)))
        q = q.filter(model.Kiri.tyyp==self.c.styyp)

        f_sooritus = []
        if self.c.toimumisaeg_id:
            f_sooritus.append(model.Sooritus.toimumisaeg_id==int(self.c.toimumisaeg_id))
        elif self.c.testimiskord_id:
            q = q.filter(model.Sooritaja.testimiskord_id==self.c.testimiskord_id)
        else:
            if self.c.sessioon_id:
                q = q.join(model.Sooritaja.testimiskord).\
                    filter(model.Testimiskord.testsessioon_id==int(self.c.sessioon_id))
            if self.c.test_id:
                q = q.filter(model.Sooritaja.test_id==self.c.test_id)
              
        if self.c.koht_id:
            # päring koha järgi
            f = sa.exists().\
                where(model.Sooritus.testikoht_id==model.Testikoht.id).\
                where(model.Testikoht.koht_id==self.c.koht_id)

            # kitsendame alampäringut samade tingimustega, mis on peapäringus juba olemas
            # nii saab kokkuvõttes kiiremini
            Sooritus2 = sa.orm.aliased(model.Sooritus)
            f = f.where(Sooritus2.testikoht_id==model.Testikoht.id).\
                where(Sooritus2.id==model.Sooritus.id)
            if self.c.toimumisaeg_id:
                f = f.where(Sooritus2.toimumisaeg_id==self.c.toimumisaeg_id)
            else:
                Sooritaja2 = sa.orm.aliased(model.Sooritaja)
                f = f.where(Sooritus2.sooritaja_id==Sooritaja2.id)
                if self.c.sessioon_id:
                    Testimiskord2 = sa.orm.aliased(model.Testimiskord)
                    f = f.where(Sooritaja2.testimiskord_id==Testimiskord2.id).\
                        where(Testimiskord2.testsessioon_id==self.c.sessioon_id)
                if self.c.test_id:
                    f = f.where(Sooritaja2.test_id==self.c.test_id)

            f_sooritus.append(f)

        elif self.c.piirkond_id:
            piirkond = model.Piirkond.get(self.c.piirkond_id)
            piirkonnad_id = piirkond.get_alamad_id()
            if len(piirkonnad_id) > 1:
                f_sooritus.append(model.Sooritus.piirkond_id.in_(piirkonnad_id))
            else:
                f_sooritus.append(model.Sooritus.piirkond_id==self.c.piirkond_id)

        if len(f_sooritus):
            q = q.filter(model.Sooritaja.sooritused.any(sa.and_(*f_sooritus)))

        return q

    def _search_saadetud_sooritaja_kasutajakaupa(self):
        "Riigieksamite teated sooritajale"
        q = (model.Session.query(*self.li_select)
             .join(model.Kasutaja.kirjasaajad)
             .join(model.Kirjasaaja.kiri)
             )

        q = q.filter(model.Kiri.tyyp==self.c.styyp)
        
        f = self._filter_sooritaja_kasutajakaupa(False)
        if f:
            q = q.filter(model.Kiri.sooritajakirjad.any(
                model.Sooritajakiri.sooritaja.has(sa.and_(*f))))
        return q

    def _search_saadetud_labiviija_kasutajakaupa(self):
        "Riigieksamite teated läbiviijale"
        q = (model.Session.query(*self.li_select)
             .join(model.Kasutaja.kirjasaajad)
             .join(model.Kirjasaaja.kiri)
             )

        q = q.filter(model.Kiri.tyyp==self.c.ltyyp)
        if self.c.ltyyp == model.Kiri.TYYP_LABIVIIJA_LEPING:
            # läbiviija lepingute korral ei ole Labiviijakiri kirjet
            # ja seda ei saa filtris kasutada
            if self.c.sessioon_id:
                self.notice(_('Lepingu sõlmimise teavituste otsimisel ei arvestata testsessiooni ja testi otsinguparameetreid'))
        else:
            f = self._filter_labiviija_kasutajakaupa(False)
            if f:
                q = q.filter(model.Kiri.labiviijakirjad.any(
                    model.Labiviijakiri.labiviija.has(sa.and_(*f))))

        return q

    def _search_saadetud_kasutajakaupa(self):
        "Riigieksamite teated sooritajale või läbiviijale"
        c = self.c
        q = (model.Session.query(*self.li_select)
             .join(model.Kasutaja.kirjasaajad)
             .join(model.Kirjasaaja.kiri)
             )

        li = []
        
        f1 = self._filter_sooritaja_kasutajakaupa(False)
        if f1:
            li.append(model.Kiri.sooritajakirjad.any(
                model.Sooritajakiri.sooritaja.has(sa.and_(*f1))))
            
        f2 = self._filter_labiviija_kasutajakaupa(False)
        if f2:
            li.append(model.Kiri.labiviijakirjad.any(
                model.Labiviijakiri.labiviija.has(sa.and_(*f2))))

        f3 = self._filter_soorituskoht()
        if f3 is not None:
            li.append(f3)
            
        if li:
            q = q.filter(sa.or_(*li))

        if self.c.atyyp:
            q = q.filter(model.Kiri.tyyp==self.c.atyyp)

        return q

    def _filter_soorituskoht(self):
        """Filter soorituskohta toimumisaja alusel saadetud kirjade otsimiseks,
        kui ei saadetud läbiviijale ega sooritajale
        """
        f = None
        if self.c.toimumisaeg_id:
            f = model.Kirjasaaja.toimumisaeg_id==self.c.toimumisaeg_id
        elif self.c.testimiskord_id:
            f = model.Kirjasaaja.toimumisaeg.has(
                model.Toimumisaeg.testimiskord_id==self.c.testimiskord_id)
        return f
    
    def _filter_sooritaja_kasutajakaupa(self, saatmata):
        f = []
        f_sooritus = []
        if self.c.toimumisaeg_id:
            f_sooritus.append(model.Sooritus.toimumisaeg_id==int(self.c.toimumisaeg_id))
        if self.c.testimiskord_id:
            f.append(model.Sooritaja.testimiskord_id==self.c.testimiskord_id)
        else:
            if self.c.sessioon_id and self.c.test_id:
                f.append(model.Sooritaja.testimiskord.has(\
                        sa.and_(model.Testimiskord.testsessioon_id==int(self.c.sessioon_id),
                                model.Testimiskord.test_id==self.c.test_id,
                                model.Testimiskord.test.has(model.Test.testiliik_kood==self.c.testiliik)),
                        ))
            elif self.c.sessioon_id:
                f.append(model.Sooritaja.testimiskord.has(\
                        sa.and_(model.Testimiskord.testsessioon_id==int(self.c.sessioon_id),
                                model.Testimiskord.test.has(model.Test.testiliik_kood==self.c.testiliik))))
            elif self.c.testiliik:
                f.append(model.Sooritaja.test.has(model.Test.testiliik_kood==self.c.testiliik))
                
        if self.c.koht_id:
            f_sooritus.append(model.Sooritus.testikoht.has(\
                    model.Testikoht.koht_id==self.c.koht_id))

        elif self.c.piirkond_id:
            piirkond = model.Piirkond.get(self.c.piirkond_id)
            piirkonnad_id = piirkond.get_alamad_id()
            f_sooritus.append(model.Sooritus.piirkond_id.in_(piirkonnad_id))

        if len(f_sooritus):
            f.append(model.Sooritaja.sooritused.any(sa.and_(*f_sooritus)))

        if saatmata and not self.c.kordus:
            f.append(~ model.Sooritaja.sooritajakirjad.any(\
                    model.Sooritajakiri.kiri.has(model.Kiri.tyyp==self.c.styyp)))

        return f

    def _filter_labiviija_kasutajakaupa(self, saatmata):
        f = []
        if self.c.grupp_id:
            if self.c.grupp_id == const.GRUPP_HINDAJA_S:
                f.append(model.Labiviija.kasutajagrupp_id.in_(
                    (const.GRUPP_HINDAJA_S, const.GRUPP_HINDAJA_S2)))
            else:
                f.append(model.Labiviija.kasutajagrupp_id==self.c.grupp_id)
        if self.c.toimumisaeg_id:
            f.append(model.Labiviija.toimumisaeg_id==int(self.c.toimumisaeg_id))
        elif self.c.testimiskord_id:
            f.append(model.Labiviija.toimumisaeg.has(\
                    model.Toimumisaeg.testimiskord_id==self.c.testimiskord_id))
        else:
            if self.c.sessioon_id and self.c.test_id:
                f.append(model.Labiviija.toimumisaeg.has(\
                        model.Toimumisaeg.testimiskord.has(\
                            sa.and_(model.Testimiskord.testsessioon_id==int(self.c.sessioon_id),
                                    model.Testimiskord.test_id==self.c.test_id,
                                    model.Testimiskord.test.has(model.Test.testiliik_kood==self.c.testiliik)),
                            )))
            elif self.c.sessioon_id:
                f.append(model.Labiviija.toimumisaeg.has(\
                        model.Toimumisaeg.testimiskord.has(\
                            sa.and_(model.Testimiskord.testsessioon_id==int(self.c.sessioon_id),
                                    model.Testimiskord.test.has(model.Test.testiliik_kood==self.c.testiliik)))))
            elif self.c.testiliik:
                f.append(model.Labiviija.toimumisaeg.has(\
                    model.Toimumisaeg.testimiskord.has(\
                        model.Testimiskord.test.has(model.Test.testiliik_kood==self.c.testiliik))))

        if self.c.koht_id:
            f.append(model.Labiviija.testikoht.has(\
                    model.Testikoht.koht_id==self.c.koht_id))

        elif self.c.piirkond_id:
            piirkond = model.Piirkond.get(self.c.piirkond_id)
            piirkonnad_id = piirkond.get_alamad_id()
            f.append(model.Labiviija.testikoht.has(\
                model.Testikoht.koht.has(\
                    model.Koht.piirkond_id.in_(piirkonnad_id))))

        if saatmata and not self.c.kordus:
            # otsime ainult need, kellele ei ole veel kirja saadetud
            if self.c.ltyyp == const.TYYP_LABIVIIJA_MEELDE:
                f.append(model.Labiviija.meeldetuletusaeg==None)
            elif self.c.ltyyp == const.TYYP_LABIVIIJA_TEADE:
                f.append(model.Labiviija.teateaeg==None)
            else:
                f.append(~ model.Labiviija.labiviijakirjad.any(\
                    model.Labiviijakiri.kiri.has(model.Kiri.tyyp==self.c.ltyyp)))
        return f
            
    def _prepare_header(self):
        c = self.c
        header = [('kasutaja.isikukood,kasutaja.synnikpv', _("Isikukood või sünniaeg")),
                  ('kasutaja.perenimi,kasutaja.eesnimi', _("Nimi")),
                  ('kiri.teatekanal', _("Edastuskanal")),
                  ('kirjasaaja.epost,kirjasaaja.isikukood', _("Saatmisaadress")),
                  ('kiri.created', _("Saatmise või loomise aeg")),
                  ('kiri.tyyp', _("Kirja tüüp")),
                  ]
        if not c.csv:
            header.append((None, _("Fail")))
        header.append((None, _("Soorituskoht")))
        if c.on_tseis and c.styyp:
            header.append(('sooritaja.algus', _("Testi aeg")))
            header.append(('test.nimi', _("Test")))
            if c.testiliik == const.TESTILIIK_TASE:
                header.append(('testitase.keeletase_kood', _("Keeleoskuse tase")))
        return header
    
    def _prepare_item(self, row, n, is_html=False):
        def get_koht_nimi(k_id, kiri_id, koht_id):
            # kui kirjasaaja juures on koht näidatud, siis kasutame seda
            if koht_id:
                koht = model.Koht.get(koht_id)
                return koht.nimi
            
            # leiame sooritajaga seotud koha
            q = (model.Session.query(model.Koht.nimi)
                 .join(model.Koht.testikohad)
                 .join(model.Testikoht.sooritused)
                 .join(model.Sooritus.sooritaja)
                 .join(model.Sooritaja.sooritajakirjad)
                 .filter(model.Sooritajakiri.kiri_id==kiri_id)
                 .filter(model.Sooritaja.kasutaja_id==k_id)
                 )
            for nimi, in q.all():
                return nimi

            # kui ei olnud, siis leiame läbiviijaga seotud koha
            q = (model.Session.query(model.Koht.nimi)
                 .join(model.Koht.testikohad)
                 .join(model.Testikoht.labiviijad)
                 .join(model.Labiviija.labiviijakirjad)
                 .filter(model.Labiviijakiri.kiri_id==kiri_id)
                 .filter(model.Labiviija.kasutaja_id==k_id)
                 )
            for nimi, in q.all():
                return nimi
            
        c = self.c
        k_id, k_isikukood, k_synnikpv, k_nimi, epost, saaja_ik, koht_id, kiri = row[:8]
        item = [k_isikukood or self.h.str_from_date(k_synnikpv),
                k_nimi,
                kiri.teatekanal_nimi,
                epost or saaja_ik,
                self.h.str_from_datetime(kiri.created),
                kiri.teema or kiri.tyyp_nimi,
                ]
        if not c.csv:
            item.append(None)
        item.append(get_koht_nimi(k_id, kiri.id, koht_id))

        if c.on_tseis and c.styyp:
            j_id, j_algus, t_nimi = row[7:10]
            item.append(self.h.str_from_datetime(j_algus))
            item.append(t_nimi)
            if c.testiliik == const.TESTILIIK_TASE:
                tase = row[10]
                item.append(tase)

        url_dlg = url_pdf = None
        if is_html:
            url_dlg = self.url('otsing_edit_teade', id=kiri.id)
            if kiri.has_file:
                url_pdf = self.url('otsing_teade_format', id=kiri.id, format='pdf')
            return item, url_dlg, url_pdf, kiri.teema
        else:
            return item

    def _edit(self, item):
        # kirjal võib olla mitu saajat, eeldame, et meid huvitab neist esimene
        for r in item.kirjasaajad:
            self.c.kasutaja = r.kasutaja
            break

    def _update(self, item):        
        "Kirja (uuesti) saatmine"
        self._send_epost(item)

    def _send_epost(self, item):
        to = self.form.data['epost']
        if not to:
            self.error(_("Ei saa kirja saata, kui aadressi ei tea!"))
            return
        k_id = self.form.data['k_id']
        subject = (item.teema or '') + _(" (kordusteade)")
        body = item.sisu or ''
        if item.has_file:
            attachments = [(item.filename, item.filedata)]
        else:
            attachments = []

        if not Mailer(self).send(to, subject, body, attachments):
            kiri = model.Kiri(saatja_kasutaja_id=self.c.user.id,
                              tyyp=item.tyyp,
                              sisu=item.sisu,
                              teema=subject,
                              filename=item.filename,
                              filedata=item.filedata,
                              teatekanal=const.TEATEKANAL_EPOST)
            for skiri in item.sooritajakirjad:
                model.Sooritajakiri(sooritaja_id=skiri.sooritaja_id, kiri=kiri)
            model.Kirjasaaja(kiri=kiri, kasutaja_id=k_id, epost=to)
            self.success(_("Kiri saadetud"))    
            log.debug(_("Saadetud kiri aadressile {s}").format(s=to))
            model.Session.commit()
            
