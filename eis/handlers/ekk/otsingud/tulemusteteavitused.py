from smtplib import SMTPRecipientsRefused

from eis.lib.baseresource import *
_ = i18n._
from eis.lib.pdf.tulemus import TulemusDoc
from eis.lib.xtee.notifications import Notifications

log = logging.getLogger(__name__)

class TulemusteteavitusedController(BaseResourceController):
    """Tulemuste teavituste saatmine
    """
    _permission = 'aruanded-tulemusteteavitused'
    _MODEL = model.Kiri
    _INDEX_TEMPLATE = 'ekk/otsingud/tulemusteteavitused.mako'
    _LIST_TEMPLATE = 'ekk/otsingud/tulemusteteavitused_list.mako'
    _SEARCH_FORM = forms.ekk.otsingud.TulemusteteavitusedForm
    _DEFAULT_SORT = 'kasutaja.perenimi kasutaja.eesnimi'
    _UNIQUE_SORT = False
    _get_is_readonly = False
    
    def _query(self):
        return None

    def _search_default(self, q):
        return None

    def _search_query_kanal(self, teatekanal):
        c = self.c
        if c.on_tseis:
            q = self._search_saatmata_sooritaja_testikaupa(teatekanal)
        else:
            q = self._search_saatmata_sooritaja_kasutajakaupa(teatekanal)

        if c.isikukood:
            usp = validators.IsikukoodP(self.c.isikukood)
            q = q.filter(usp.filter(model.Kasutaja))
        if c.eesnimi:
            q = q.filter(model.Kasutaja.eesnimi.ilike(c.eesnimi))
        if c.perenimi:
            q = q.filter(model.Kasutaja.perenimi.ilike(c.perenimi))
        return q
    
    def _search_query(self, q1):
        c = self.c
        c.on_tseis = c.testiliik in (const.TESTILIIK_TASE, const.TESTILIIK_SEADUS)
        if not self._has_search_params():
            return
        if not c.sessioon_id:
            if c.saatmata:
                self.error(_("Palun valida testsessioon"))
            return 

        q = self._search_query_kanal(const.TEATEKANAL_EPOST)
        f_epost = sa.and_(model.Kasutaja.epost != None,
                          model.Kasutaja.epost != '')
        q_epost = q.filter(f_epost)
        
        f_tpost = sa.and_(model.Kasutaja.aadress.has(model.Aadress.kood1!=None),
                          model.Kasutaja.postiindeks!=None)
        q = self._search_query_kanal(const.TEATEKANAL_POST)        
        q_tpost = q.filter(~ f_epost).filter(f_tpost)

        q = self._search_query_kanal(None)
        q_puudu = q.filter(~ f_epost)
        if c.on_tseis:
            q_puudu = q_puudu.filter(~ f_tpost)
        
        # päringu tegemise ajal kasutatud parameetrid kasutamiseks URLides
        c.search_args = {'sessioon_id': c.sessioon_id,
                         'testiliik': c.testiliik,
                         'testimiskord_id': c.testimiskord_id,
                         'toimumisaeg_id': c.toimumisaeg_id,
                         'test_id': c.test_id,
                         'piirkond_id': c.piirkond_id,
                         'koht_id': c.koht_id,
                         'isikukood': c.isikukood,
                         'eesnimi': c.eesnimi,
                         'perenimi': c.perenimi,
                         'kordus': c.kordus and 1 or '',
                         'sooritusteated': c.sooritusteated and 1 or '',
                         'mittesooritusteated': c.mittesooritusteated and 1 or '',
                         }
        return q_epost, q_tpost, q_puudu
    
    def _search(self, q):
        c = self.c
        r = self._search_query(q)
        if not r:
            return
        q_epost, q_tpost, q_puudu = r
        self._get_protsessid()

        c.arv_epost = q_epost.count()
        c.arv_tpost = q_tpost.count()
        c.arv_puudu = q_puudu.count()
        if c.naita == 'puudu':
            # kuvame sooritajad, kelle aadress puudub
            return q_puudu
        elif c.naita == 'epost':
            # kuvame sooritajad, kellele saadetakse teade e-postiga
            return q_epost
        elif c.naita == 'tpost':
            # kuvame sooritajad, kellele saadetakse teade tigupostiga
            return q_tpost
        return None

    def _search_saatmata_sooritaja_testikaupa(self, teatekanal):
        "TSEISi teated sooritajale"
        li_select = [model.Kasutaja.id, 
                     model.Kasutaja.isikukood,
                     model.Kasutaja.synnikpv,
                     model.Kasutaja.nimi, 
                     model.Kasutaja.epost,
                     model.Sooritaja.id,
                     model.Sooritaja.algus,
                     model.Test.nimi,
                     model.Sooritaja.test_id,
                     model.Testimiskord.tahis,
                     model.Sooritaja.pallid,
                     model.Sooritaja.tulemus_protsent,
                     ]

        if self.c.testiliik == const.TESTILIIK_TASE:
            li_select.append(model.Sooritaja.keeletase_kood)

        q = model.SessionR.query(*li_select).\
            join(model.Kasutaja.sooritajad).\
            join(model.Sooritaja.test).\
            join(model.Sooritaja.testimiskord).\
            filter(model.Test.testiliik_kood==self.c.testiliik)

        f_sooritus = []
        if self.c.toimumisaeg_id:
            f_sooritus.append(model.Sooritus.toimumisaeg_id==int(self.c.toimumisaeg_id))
        elif self.c.testimiskord_id:
            q = q.filter(model.Sooritaja.testimiskord_id==self.c.testimiskord_id)
        else:
            if self.c.sessioon_id:
                q = q.filter(model.Testimiskord.testsessioon_id==int(self.c.sessioon_id))
                if self.c.test_id:
                    q = q.filter(model.Sooritaja.test_id==self.c.test_id)
            if self.c.keeletase and not self.c.test_id:
                q = q.filter(model.Test.testitasemed.any(model.Testitase.keeletase_kood==self.c.keeletase))
                
        if self.c.koht_id:
            f_sooritus.append(model.Sooritus.testikoht.has(\
                model.Testikoht.koht_id==self.c.koht_id))

        elif self.c.piirkond_id:
            piirkond = model.Piirkond.get(self.c.piirkond_id)
            piirkonnad_id = piirkond.get_alamad_id()

            # soorituskoha piirkonna järgi
            f_sooritus.append(model.Sooritus.piirkond_id.in_(piirkonnad_id))

            # regamisel soovitud piirkond - otsime selle järgi, Hele lubas 2013-03-15 skypes
            # see eeldab, et iga sooritaja on regamisel näidanud piirkonna
            # ja ta on tegelikult sellesse piirkonda ka suunatud

        if len(f_sooritus):
            q = q.filter(model.Sooritaja.sooritused.any(sa.and_(*f_sooritus)))

        q = q.filter(model.Sooritaja.staatus==const.S_STAATUS_TEHTUD)
        q = q.filter(model.Sooritaja.hindamine_staatus==const.H_STAATUS_HINNATUD)
            
        if not self.c.kordus:
            if teatekanal:
                q = q.filter(~ model.Sooritaja.sooritajakirjad.any(\
                    model.Sooritajakiri.kiri.has(
                        sa.and_(model.Kiri.tyyp==model.Kiri.TYYP_TULEMUS,
                                model.Kiri.teatekanal==teatekanal))))
            else:
                q = q.filter(~ model.Sooritaja.sooritajakirjad.any(\
                    model.Sooritajakiri.kiri.has(model.Kiri.tyyp==model.Kiri.TYYP_TULEMUS)))
                
        if self.c.sooritusteated and not self.c.mittesooritusteated:
            q = q.filter(model.Sooritaja.tulemus_piisav==True)
        elif not self.c.sooritusteated and self.c.mittesooritusteated:
            q = q.filter(model.Sooritaja.tulemus_piisav==False)            

        return q

    def _search_saatmata_sooritaja_kasutajakaupa(self, teatekanal):
        "Riigieksami teated sooritajale"
        li_select = [model.Kasutaja.id, 
                     model.Kasutaja.isikukood,
                     model.Kasutaja.synnikpv,
                     model.Kasutaja.nimi, 
                     model.Kasutaja.epost,
                     ]

        q = model.SessionR.query(*li_select)
        f = self._filter_sooritaja_kasutajakaupa(True, teatekanal)

        f.append(model.Sooritaja.staatus==const.S_STAATUS_TEHTUD)
        f.append(model.Sooritaja.hindamine_staatus==const.H_STAATUS_HINNATUD)
        q = q.filter(model.Kasutaja.sooritajad.any(sa.and_(*f)))

        return q

    def _filter_sooritaja_kasutajakaupa(self, saatmata, teatekanal):
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
                                model.Testimiskord.test_id==self.c.test_id),
                        ))
            elif self.c.sessioon_id:
                f.append(model.Sooritaja.testimiskord.has(\
                        model.Testimiskord.testsessioon_id==int(self.c.sessioon_id)))
                
        if self.c.koht_id:
            f_sooritus.append(model.Sooritus.testikoht.has(\
                    model.Testikoht.koht_id==self.c.koht_id))

        elif self.c.piirkond_id:
            piirkond = model.Piirkond.get(self.c.piirkond_id)
            piirkonnad_id = piirkond.get_alamad_id()

            # soorituskoha piirkonna järgi
            f_sooritus.append(model.Sooritus.piirkond_id.in_(piirkonnad_id))

            # regamisel soovitud piirkond
            # see eeldab, et iga sooritaja on regamisel näidanud piirkonna
            # ja ta on tegelikult sellesse piirkonda ka suunatud

        if len(f_sooritus):
            f.append(model.Sooritaja.sooritused.any(sa.and_(*f_sooritus)))

        f.append(model.Sooritaja.test.has(model.Test.testiliik_kood==self.c.testiliik))

        if saatmata and not self.c.kordus:
            if teatekanal:
                f.append(~ model.Sooritaja.sooritajakirjad.any(\
                    model.Sooritajakiri.kiri.has(
                    sa.and_(model.Kiri.tyyp==model.Kiri.TYYP_TULEMUS,
                            model.Kiri.teatekanal==teatekanal))))
            else:
                f.append(~ model.Sooritaja.sooritajakirjad.any(\
                    model.Sooritajakiri.kiri.has(
                        model.Kiri.tyyp==model.Kiri.TYYP_TULEMUS)))

        return f

    def _get_saatmata_sooritajad(self, kasutaja, teatekanal):
        f = self._filter_sooritaja_kasutajakaupa(True, teatekanal)
        q = model.Sooritaja.query.\
            filter(model.Sooritaja.kasutaja_id==kasutaja.id).\
            filter(sa.and_(*f)).\
            order_by(model.Sooritaja.algus)
        return q.all()

    def create(self):
        self.form = Form(self.request, schema=self._SEARCH_FORM)
        if self.form.validate():
            self._copy_search_params(self.form.data, save=False)
            q = self._query()
            r = self._search_query(q)
            taiendavinfo = self.request.params.get('taiendavinfo')
            if r:
                teatekanal = None
                q_epost, q_tpost, q_puudu = r
                if self.c.testkiri:
                    testaadress = self.c.testaadress
                    if not testaadress:
                        self.error(_("Testkirja saatmiseks palun sisestada saaja e-posti aadress"))
                    else:
                        teatekanal = const.TEATEKANAL_EPOST
                        q = q_epost
                        cnt = q.all()
                        if not cnt:
                            self.error(_("Teavitusi pole"))
                        else:
                            self._send_childfunc(None,
                                                 q,
                                                 teatekanal,
                                                 taiendavinfo,
                                                 testaadress)
                else:
                    if self.request.params.get('epost'):
                        teatekanal = const.TEATEKANAL_EPOST
                        q = q_epost
                    elif self.request.params.get('tpost'):
                        if not self.c.on_tseis:
                            # riigieksamite tulemusi ei teavitata tigupostiga
                            self.error(_("Valitud testsessiooni testiliigi kohta paberil tulemuste teavitusi ei saadeta"))
                            return self._redirect('index')

                        teatekanal = const.TEATEKANAL_POST
                        q = q_tpost
                    elif self.request.params.get('puudu'):
                        # aadress puudub, teade ainult EISi
                        teatekanal = const.TEATEKANAL_EIS
                        q = q_puudu
                    if teatekanal:
                        # saatmine
                        resp = self._send_all(q, teatekanal, taiendavinfo)
                        if resp:
                            # debug
                            return resp
        else:
            # sisendparameetrid ei valideeru
            template = self._INDEX_TEMPLATE
            html = self.form.render(template, extra_info=self.response_dict)            
            return Response(html)

        return self._redirect('index', getargs=True)

    def _search_protsessid(self, q):
        sessioon_id = self.c.sessioon_id or self.request.params.get('sessioon_id')
        q = (q.filter(model.Arvutusprotsess.liik==model.Arvutusprotsess.LIIK_M_TULEMUS)
             .filter(model.Arvutusprotsess.testsessioon_id==sessioon_id)
             )
        return q

    def _send_all(self, q, teatekanal, taiendavinfo):
        cnt = q.count()
        if cnt:
            if self.c.toimumisaeg_id:
                ta = model.Toimumisaeg.get(self.c.toimumisaeg_id)
                tahised = ta.tahised
            elif self.c.testimiskord_id:
                tk = model.Testimiskord.get(self.c.testimiskord_id)
                tahised = tk.tahised
            elif self.c.test_id:
                tahised = self.c.test_id
            else:
                tahised = ''
            skanal = self.c.opt.TEATEKANAL.get(teatekanal)
            desc = _("Tulemuste teavituste saatmine {s} ({n} teadet, {s2})").format(s=tahised, n=cnt, s2=skanal)
            params = {'liik': model.Arvutusprotsess.LIIK_M_TULEMUS,
                      'kirjeldus': desc,
                      'test_id': self.c.test_id or None,
                      'testimiskord_id': self.c.testimiskord_id or None,
                      'toimumisaeg_id': self.c.toimumisaeg_id or None,
                      'testsessioon_id': self.c.sessioon_id or None,
                      }
            if teatekanal == const.TEATEKANAL_POST:
                childfunc = lambda rcd: self._gen_pdf_all(rcd, q, taiendavinfo)
            else:
                childfunc = lambda rcd: self._send_childfunc(rcd, q, teatekanal, taiendavinfo)
            debug = self.is_devel
            resp = model.Arvutusprotsess.start(self, params, childfunc, debug=debug)
            if debug:
                return resp
            self.success('Saatmise protsess käivitatud')

    def _send_childfunc(self, protsess, q, teatekanal, taiendavinfo, testaadress=None):
        total = q.count()
        
        def itemfunc(rcd):
            rc = err = None
            k_id, k_ik, k_synnikpv, k_nimi, k_epost = rcd[:5]
            if self.c.on_tseis:
                # TSEISi teated sooritajale
                sooritaja = model.Sooritaja.get(rcd[5])
                sooritajad = None
                kasutaja = sooritaja.kasutaja
            else:
                kasutaja = model.Kasutaja.get(k_id)
                sooritajad = list(self._get_saatmata_sooritajad(kasutaja, teatekanal))
                sooritaja = None
            if teatekanal in (const.TEATEKANAL_EPOST, const.TEATEKANAL_EIS):
                rc, err = send_epost_sooritaja(self,
                                               kasutaja,
                                               testaadress=testaadress,
                                               sooritaja=sooritaja,
                                               sooritajad=sooritajad,
                                               taiendavinfo=taiendavinfo)
            return rc, err

        if testaadress:
            n = random.randrange(total)
            q = q.slice(n, n+1)
        items = q.all()
        if not protsess:
            for r in items:
                itemfunc(r)
        else:
            model.Arvutusprotsess.iter_mail(protsess, self, total, items, itemfunc)
    
    def _gen_pdf_all(self, protsess, q, taiendavinfo):
        # ainult TE ja SE, testikaupa
        doc = TulemusDoc(self, self.c.testiliik, protsess)
        filedata = doc.generate(items=q.all(), taiendavinfo=taiendavinfo)

        # salvestame teate aja läbiviija kirjes
        model.Session.commit()

        if protsess:
            # tavaline arvutusprotsess
            if filedata:
                protsess.filename = 'tulemus.pdf'
                protsess.filedata = filedata
            if doc.error:
                protsess.set_viga(doc.error)
        else:
            # debug
            return utils.download(filedata, 'tulemus.pdf')

def compose_msg(handler, k, sooritaja, sooritajad, taiendavinfo, for_stateos=False):
    data = {'isik_nimi': k.nimi,
            'sooritaja': sooritaja,
            'sooritajad': sooritajad,
            'user_nimi': handler.c.user.fullname,
            'taiendavinfo': taiendavinfo,
            }

    if sooritaja:
        # yhe testi teade, st on_tseis
        # leiame tulemuste selgitused osade kaupa
        osasooritused = sooritaja.get_osasooritused()
        test = sooritaja.test
        vahemikud = []
        pallid = []
        for sooritus, osa, ylemsooritus in osasooritused:
            if sooritus and sooritus.staatus == const.S_STAATUS_TEHTUD:
                protsent = sooritus.tulemus_protsent
                n, vahemik_algus, vahemik_lopp = test.get_vahemik_by_protsent(protsent)
                buf = '%s %s (%d-%d%%)' % (osa.nimi.lower(),
                                           test.get_vahemiknimi_by_protsent(protsent),
                                           vahemik_algus,
                                           vahemik_lopp)
                vahemikud.append(buf)
                buf = _("{s} {p1} ({p2}-st)").format(s=osa.nimi.lower(), p1=round(sooritus.pallid), p2=round(osa.max_pallid))
                pallid.append(buf)
            elif sooritus and sooritus.staatus == const.S_STAATUS_VABASTATUD:
                vahemikud.append(_("{s} vabastatud").format(s=osa.nimi.lower()))
                pallid.append(_("{s} vabastatud").format(s=osa.nimi.lower()))
            elif not sooritus and ylemsooritus.staatus == const.S_STAATUS_VABASTATUD:
                vahemikud.append(_("{s} vabastatud").format(s=osa.nimi.lower()))
                pallid.append(_("{s} vabastatud").format(s=osa.nimi.lower()))                

        if sooritaja.tulemus_piisav: 
            tunnistus = model.Session.query(model.Tunnistus).\
                        join(model.Tunnistus.testitunnistused).\
                        filter(model.Tunnistus.staatus>const.N_STAATUS_KEHTETU).\
                        filter(model.Testitunnistus.sooritaja_id==sooritaja.id).\
                        first()
            if not tunnistus:
                buf = _("Ei saa tulemuste teadet saata, kuna pole tunnistust") + ' (%s)' % k.nimi
                return False, buf
            data['tunnistus'] = tunnistus

        data['s_vahemikud'] = vahemikud
        data['s_pallid'] = pallid
        data['test'] = test

        keeletase_nimi = sooritaja.test.keeletase_nimi
        if keeletase_nimi:
            if keeletase_nimi[-1].isdigit():
                # A2,B1,B2,C1
                data['taseme'] = '%s-taseme' % keeletase_nimi
            else:
                # alg, kesk, kõrg
                data['taseme'] = '%staseme' % keeletase_nimi

    mako = 'mail/tulemus.mako'
    if sooritaja:
        testiliik_kood = sooritaja.test.testiliik_kood
        if sooritaja.tulemus_piisav:
            mako = 'mail/tulemus_%s.sooritusteade.mako' % (testiliik_kood)
        else:
            mako = 'mail/tulemus_%s.mittesooritusteade.mako' % (testiliik_kood)
            
    subject, body = handler.render_mail(mako, data)    
    return subject, body

def send_epost_sooritaja(handler, k, testaadress=None, sooritaja=None, sooritajad=None, taiendavinfo=None):
    to = testaadress or k.epost
    if to:
        teatekanal = const.TEATEKANAL_EPOST
    else:
        teatekanal = const.TEATEKANAL_EIS
    subject, body = compose_msg(handler, k, sooritaja, sooritajad, taiendavinfo)
    if not subject:
        err = body
        return False, err
    log.debug('Saadan kirja aadressile %s kasutajale %s (%d)' % (to, k.nimi, k.id))

    if teatekanal == const.TEATEKANAL_EPOST:
        # saadame e-kirja
        body = Mailer.replace_newline(body)
        err = Mailer(handler).send(to, subject, body, out_err=False)
        if err:
            buf = '%s (%s %s)' % (err, k.nimi, to)
            model.Arvutusprotsess.trace(buf)
            return False, err
        else:
            log.debug(_("Saadetud kiri aadressile {s}").format(s=to))

    if not testaadress:
        kiri = model.Kiri(saatja_kasutaja_id=handler.c.user.id,
                          tyyp=model.Kiri.TYYP_TULEMUS,
                          sisu=body,
                          teema=subject,
                          teatekanal=teatekanal)
        for j in sooritajad or [sooritaja]:
            model.Sooritajakiri(sooritaja=j, kiri=kiri)
            j.teavitatud_epost = datetime.now()

        model.Kirjasaaja(kiri=kiri, kasutaja_id=k.id, epost=k.epost)
        # vaja teha commit
    return True, None
    
def send_epost_avaldet(handler, kord_tahised, testiliik):
    "Tulemuste avaldamisel (Muud toimingud > Tulemuste avaldamine) ametnikele teavituste saatmine"
    q = (model.SessionR.query(model.Kasutaja.id, model.Kasutaja.epost)
         .filter(model.Kasutaja.kasutajarollid.any(
             sa.and_(model.Kasutajaroll.kasutajagrupp_id==const.GRUPP_AVALDET,
                     sa.or_(model.Kasutajaroll.testiliik_kood==None,
                            model.Kasutajaroll.testiliik_kood==testiliik),
                     model.Kasutajaroll.kehtib_alates<=datetime.now(),
                     model.Kasutajaroll.kehtib_kuni>=datetime.now())))
         )
    kasutajad = [(k_id, epost) for (k_id, epost) in q.all()]
    to = [r[1] for r in kasutajad]
    log.debug('send_epost_avaldet %s' % to)
    if to:
        subject = 'Tulemuste avaldamine'
        body = 'Avaldati testimiskordade %s tulemused' % (', '.join(kord_tahised))
        log.debug('Saadan kirja aadressidele %s' % (', '.join(to)))
        body = Mailer.replace_newline(body)
        if not Mailer(handler).send(to, subject, body):
            kiri = model.Kiri(tyyp=model.Kiri.TYYP_MUU,
                              teema=subject,
                              sisu=body,
                              teatekanal=const.TEATEKANAL_EPOST)
            for k_id, epost in kasutajad:
                model.Kirjasaaja(kiri=kiri, kasutaja_id=k_id, epost=epost)
            model.Session.commit()
            return True
        else:
            return False

