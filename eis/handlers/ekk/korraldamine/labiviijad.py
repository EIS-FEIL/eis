from eis.lib.baseresource import *
_ = i18n._
from eis.lib.basegrid import BaseGridController
from eis.lib.xtee import rahvastikuregister
from eis.handlers.ekk.otsingud.labiviijateated import send_labiviija_maaramine
log = logging.getLogger(__name__)

class LabiviijadController(BaseResourceController):
    _permission = 'korraldamine'

    _MODEL = model.Labiviija
    _INDEX_TEMPLATE = '/ekk/korraldamine/labiviijad.mako' 
    _EDIT_TEMPLATE = '/ekk/korraldamine/labiviija.muud.mako' # läbiviija kõik osalemised
    _LIST_TEMPLATE = '/ekk/korraldamine/labiviijad_list.mako'
    _DEFAULT_SORT = 'koht.nimi,testiruum.algus,testiruum.tahis,labiviija.kasutajagrupp_id,labiviija.id'
    _SEARCH_FORM = forms.ekk.korraldamine.LabiviijadForm
    
    def _query(self):
        q = (model.Labiviija.query
             .filter_by(toimumisaeg_id=self.c.toimumisaeg.id)
             .outerjoin(model.Labiviija.testiruum)
             .join(model.Labiviija.testikoht)
             .join(model.Testikoht.koht)
             .outerjoin(model.Koht.aadress)
             )
        if self.c.toimumisaeg.ruum_noutud:
            q = q.filter(sa.or_(
                model.Labiviija.kasutaja_id!=None,
                model.Testiruum.id==None,
                model.Testiruum.ruum_id!=None))
        self.c.opt_kuupaev = self._get_opt_kuupaev()
        return q
    
    def _search(self, q):
        c = self.c
        if c.piirkond_id:
            piirkond = model.Piirkond.get(c.piirkond_id)
            q = q.filter(model.Koht.piirkond_id.in_(piirkond.get_alamad_id()))

        if c.maakond_kood:
            tase, kood = c.maakond_kood.split('.')
            q = q.filter(model.Aadress.kood1==kood)
        if c.nimi:
            q = q.filter(model.Koht.nimi.ilike(c.nimi))
        if c.roll_id:
            q = q.filter(model.Labiviija.kasutajagrupp_id==c.roll_id)
        if c.kuupaev:
            q = q.filter(sa.or_(model.Testiruum.algus.cast(sa.Date)==c.kuupaev,
                                sa.and_(model.Testiruum.id==None,
                                        model.Testikoht.alates.cast(sa.Date)==c.kuupaev)))
        if c.csv:
            return self._index_csv(q)
        return q

    def _get_opt_kuupaev(self):
        q = (model.Session.query(model.Toimumispaev.aeg.cast(sa.Date)).distinct()
             .filter_by(toimumisaeg_id=self.c.toimumisaeg.id)
             .order_by(model.Toimumispaev.aeg))
        li = [self.h.str_from_date(d) for d, in q.all()]
        return li
    
    def _order(self, q, sort=None):
        # lisame sortimistingimustele läbiviija ID, sest muidu võib juhtuda,
        # et mitu kirjet vastab samadele sortimistingimustele
        # ja siis ei ole pagineerimisel tagatud, et iga lehe jaoks samamoodi sorditakse
        # ja selle tulemusena võib mõni esineda mitu korda ja mõni yldse mitte
        return BaseResourceController._order(self, q, sort).order_by(model.Labiviija.id)

    def _order_join(self, q, tablename):
        """Otsingupäringu sortimisel lisatakse päringule join 
        tabeliga, mille välja järgi tuleb sortida
        """
        if tablename == 'kasutaja':
            q = q.join(model.Labiviija.kasutaja)
        elif tablename == 'ruum':
            q = q.outerjoin(model.Testiruum.ruum)
        return q

    def _new_mail(self):
        """Teate koostamise dialoogiakna avamine
        """
        data = {
            'test_nimi': self.c.toimumisaeg.testimiskord.test.nimi,
            'testiosa_nimi': self.c.toimumisaeg.testiosa.nimi,
            'millal': self.c.toimumisaeg.millal,
            'user_nimi': self.c.user.fullname,
            }
        self.c.subject, self.c.body = self.render_mail('mail/labiviijateade.kohata.mako', data)
        return self.render_to_response('/ekk/korraldamine/labiviijad.mail.mako')

    def _create_mail(self):
        """Teate saatmine
        """
        labiviijad_id = self.request.params.get('labiviijad_id').split(',')
        self.form = Form(self.request, schema=forms.ekk.korraldamine.LabiviijaMailForm)
        if not self.form.validate():
            self.c.dialog_mail = True
            return Response(self.form.render(self._ITEM_TEMPLATE,
                                             extra_info=self.response_dict))
        
        else:
            msg_success = []
            for labiviija_id in labiviijad_id:
                if not labiviija_id:
                    continue
                rcd = model.Labiviija.get(labiviija_id)
                assert rcd.toimumisaeg_id == self.c.toimumisaeg.id, _("Vale toimumisaeg")
                if rcd.kasutaja:
                    if not rcd.kasutaja.epost:
                        self.error(_("Kasutajal {s} pole e-posti aadressi").format(s=rcd.kasutaja.nimi))
                    else:
                        to = rcd.kasutaja.epost
                        subject = self.form.data['subject']
                        body = self.form.data['body']
                        body = Mailer.replace_newline(body)
                        if not Mailer(self).send(to, subject, body):
                            msg_success.append(to)
                            kiri = model.Kiri(saatja_kasutaja_id=self.c.user.id,
                                              tyyp=model.Kiri.TYYP_LABIVIIJA_TEADE,
                                              sisu=body,
                                              teema=subject,
                                              teatekanal=const.TEATEKANAL_EPOST)
                            model.Labiviijakiri(labiviija=rcd, kiri=kiri)
                            model.Kirjasaaja(kiri=kiri, kasutaja_id=rcd.kasutaja_id, epost=to)
                            model.Session.commit()

            if len(msg_success):
                self.success('Teade on saadetud aadressidele: %s' % ', '.join(msg_success))
            else:
                self.error(_("Teadet ei saadetud"))
            return self._redirect('index')

    def new(self):
        """Avatakse dialoogiaken, et lisada täiendav läbiviija
        """
        sub = self._get_sub()
        if sub:
            log.debug("NEW sub=%s" % sub)
            return eval('self._new_%s' % sub)()
        labiviija_id = self.request.params.get('labiviija_id')
        # kirje, millest tehakse koopia
        self.c.item = model.Labiviija.get(labiviija_id)
        # list_url on peale lisamist loetelu taastamiseks
        self.c.list_url = self.request.params.get('list_url')
        return self.render_to_response('/ekk/korraldamine/labiviija.mako')

    def create(self):
        """Läbiviijate määramine
        """
        c = self.c
        sub = self._get_sub()
        if sub:
            log.debug("CREATE sub=%s" % sub)
            return eval('self._create_%s' % sub)()
        toimumisaeg = self.c.toimumisaeg
        testiruum_id = self.request.params.get('testiruum_id')
        if testiruum_id:
            # täiendava läbiviija kirje lisamine
            testiruum_id = int(testiruum_id)
            testiruum = model.Testiruum.get(testiruum_id)
            testikoht_id = testiruum.testikoht_id
            kasutajagrupp_id = int(self.request.params.get('kasutajagrupp_id'))
            hindamiskogum_id = self.request.params.get('hindamiskogum_id') or None
            kasutaja_id = self.request.params.get('kasutaja_id')
            if kasutaja_id:
                kasutaja_id = int(kasutaja_id)
                if self._check_kasutaja(kasutaja_id):
                    kasutaja = model.Kasutaja.get(kasutaja_id)
                    rcd = testiruum.create_labiviija(kasutajagrupp_id)
                    rcd.set_kasutaja(kasutaja, toimumisaeg)
                    send_labiviija_maaramine(self, rcd, kasutaja, toimumisaeg)
            else:
                # teeme määramata isikuga kirje
                rcd = testiruum.create_labiviija(kasutajagrupp_id)
            rcd.hindamiskogum_id = hindamiskogum_id
        else:
            # olemasolevatele rollidele läbiviijate määramine
            for key in self.request.params:
                # lv_ID_kasutaja_id
                if key.endswith('_kasutaja_id') and key.startswith('lv_'):
                    labiviija_id = int(key.split('_')[1])
                    rcd = model.Labiviija.get(labiviija_id)
                    assert rcd.toimumisaeg_id == c.toimumisaeg.id, _("Vale toimumisaeg")
                    kasutaja_id = self.request.params.get(key)
                    if kasutaja_id:
                        # läbiviija määramine
                        kasutaja_id = int(kasutaja_id)
                        if rcd.kasutaja_id != kasutaja_id:
                            kasutaja = model.Kasutaja.get(kasutaja_id)
                            if self._check_kasutaja(kasutaja_id):
                                rcd.set_kasutaja(kasutaja, toimumisaeg)
                                send_labiviija_maaramine(self, rcd, kasutaja, toimumisaeg)
                        elif rcd.staatus == const.L_STAATUS_KEHTETU:
                            rcd.staatus = const.L_STAATUS_MAARATUD
                    elif rcd.kasutaja_id:
                        # läbiviija eemaldamine
                        rcd.remove_labiviija()

        model.Session.commit()
        self.success()
        list_url = self.request.params.get('list_url') or \
            self.url_current('index')
        return HTTPFound(location=list_url)

    def _delete(self, item):
        # kui sama rolli on veel, siis eemaldame kirje
        if item.remove_labiviija():
            self.success(_("Läbiviija kirje on eemaldatud!"))
        else:
            self.success(_("Kirjet ei eemaldatud, sest see on ainuke selle rolli kirje"))

        model.Session.commit()
        return self._redirect('index')

    def _check_kasutaja(self, kasutaja_id):
        """Kontrollime, et kasutaja sellel toimumisajal pole veel rakendatud
        """
        if model.Labiviija.query.filter_by(kasutaja_id=kasutaja_id).\
                filter_by(toimumisaeg_id=self.c.toimumisaeg.id).\
                count() > 0:
            kasutaja = model.Kasutaja.get(kasutaja_id)
            self.notice(_("Kasutaja {s} on juba määratud sellel toimumisajal osalema").format(
                s=kasutaja.nimi))
        return True

    def _show(self, item):
        """Läbiviija teiste osalemiste kuvamine dialoogiaknas
        """
        self.c.kasutaja = item.kasutaja
        testsessioon_id = self.c.toimumisaeg.testimiskord.testsessioon_id
        q = model.Session.query(model.Labiviija, model.Toimumisaeg, model.Test).\
            filter(model.Labiviija.kasutaja_id==self.c.kasutaja.id).\
            join(model.Labiviija.toimumisaeg).\
            join(model.Toimumisaeg.testimiskord).\
            filter(model.Testimiskord.testsessioon_id==testsessioon_id).\
            join(model.Testimiskord.test)
        self.c.items = q.order_by(model.Test.nimi).all()

    def _prepare_header(self):
        header = [_("Soorituskoht"),
                  _("Testiruum"),
                  _("Ruum"),
                  _("Algus"),
                  _("Roll"),
                  _("Testi läbiviija"),
                  _("Läbiviija tähis"),
                  _("Läbiviija e-post"),
                  ]
        return header
    
    def _prepare_item(self, rcd, n):
        testiruum = rcd.testiruum
        testikoht = rcd.testikoht
        testiruum_algus = testiruum and testiruum.algus or testikoht.alates
        ruum = testiruum and testiruum.ruum
        koht = testikoht.koht
        kasutaja = rcd.kasutaja
        item = [koht.nimi,
                testiruum and testiruum.tahis,
                ruum and ruum.tahis,
                self.h.str_from_datetime(testiruum_algus),
                rcd.kasutajagrupp.nimi,
                kasutaja and kasutaja.nimi,
                rcd.tahis,
                kasutaja and kasutaja.epost
                ]
        return item

    def __before__(self):
        c = self.c
        c.toimumisaeg = model.Toimumisaeg.get(self.request.matchdict.get('toimumisaeg_id'))
        c.test = c.toimumisaeg.testiosa.test
        
    def _perm_params(self):
        return {'obj':self.c.test}
