from eis.lib.baseresource import *
_ = i18n._
from eis.lib.basegrid import BaseGridController
from eis.lib.xtee import rahvastikuregister
from eis.handlers.ekk.otsingud.labiviijateated import send_labiviija_maaramine
log = logging.getLogger(__name__)

class LabiviijadController(BaseResourceController):
    _permission = 'korraldamine'
    _MODEL = model.Labiviija
    _INDEX_TEMPLATE = '/ekk/korraldamine/koht.labiviijad.mako' 
    _LIST_TEMPLATE = '/ekk/korraldamine/koht.labiviijad_list.mako'
    _DEFAULT_SORT = 'testiruum.algus,testiruum.tahis,labiviija.kasutajagrupp_id'

    def _query(self):
        q = (model.SessionR.query(model.Labiviija, 
                                 model.Kasutaja, 
                                 model.Testiruum.algus,
                                 model.Testiruum.tahis, 
                                 model.Ruum.tahis)
             .filter(model.Labiviija.testikoht_id==self.c.testikoht.id)
             .outerjoin(model.Labiviija.kasutaja)
             .outerjoin(model.Labiviija.testiruum)
             .outerjoin(model.Testiruum.ruum)
             )
        if self.c.toimumisaeg.ruum_noutud:
            # kui määramata ruumi ei või kasutada,
            # siis ei või lubada läbiviijaid määrata määramata ruumi (ES-1186)
            q = q.filter(sa.or_(
                model.Labiviija.kasutaja_id!=None,
                model.Testiruum.id==None,
                model.Testiruum.ruum_id!=None))
        return q
    
    def _create(self, **kw):
        toimumisaeg = self.c.toimumisaeg
        labiviija_id = self.request.params.get('labiviija_id')
        if not labiviija_id:
            # uue kirje lisamine
            grupp_id = int(self.request.params.get('grupp_id'))
            if grupp_id in (const.GRUPP_KOMISJON_ESIMEES, const.GRUPP_KOMISJON) \
                    and not toimumisaeg.on_ruumiprotokoll:
                item = self.c.testikoht.create_labiviija(grupp_id)
            else:
                # testiruumi läbiviija
                testiruum_id = self.request.params.get('testiruum_id')
                testiruum = model.Testiruum.get(testiruum_id)
                assert testiruum.testikoht_id == self.c.testikoht.id, 'Testiruum valest testikohast'
                item = testiruum.create_labiviija(grupp_id)

                # hindaja rolli korral leitakse hindamiskogum
                hindamiskogum_id = self._get_hindamiskogum_id(grupp_id)
                if hindamiskogum_id:
                    item.hindamiskogum_id = hindamiskogum_id
        else:
            item = model.Labiviija.get(labiviija_id)
            if self.request.params.get('uus'):
                # uue läbiviija kirje lisamine
                testiruum = item.testiruum
                if testiruum:
                    new_item = testiruum.create_labiviija(item.kasutajagrupp_id)
                    new_item.hindamiskogum_id = item.hindamiskogum_id
                    new_item.liik = item.liik
                else:
                    new_item = item.testikoht.create_labiviija(item.kasutajagrupp_id)                    
                return new_item
            
        kasutaja_id = None
        for key in self.request.params:
            # submit-nupu "Vali" nimi oli "valik_id_ID", siit saame uue kasutaja ID
            prefix = 'valik_id_'
            if key.startswith(prefix):
                kasutaja_id = int(key[len(prefix):])
                break

        # kontrollime, et kasutaja sellel toimumisajal pole veel rakendatud
        if model.Labiviija.query.filter_by(kasutaja_id=kasutaja_id).\
                filter_by(toimumisaeg_id=toimumisaeg.id).\
                count() > 0:
            self.notice(_("Valitud läbiviija on juba määratud sellel toimumisajal osalema!"))

        # olemasolevas läbiviija kirjes isiku muutmine
        kasutaja = kasutaja_id and model.Kasutaja.get(kasutaja_id)
        item.set_kasutaja(kasutaja, toimumisaeg)
        if kasutaja:
            send_labiviija_maaramine(self, item, kasutaja, toimumisaeg)
        return item

    def _get_hindamiskogum_id(self, grupp_id):
        # (suulise) hindaja rollil peab olema ka hindamiskogum
        if grupp_id in (const.GRUPP_HINDAJA_S,
                        const.GRUPP_HINDAJA_S2,
                        const.GRUPP_HINDAJA_K):
            testiosa_id = self.c.toimumisaeg.testiosa_id
            q = (model.SessionR.query(model.Hindamiskogum.id)
                 .filter(model.Hindamiskogum.testiosa_id==testiosa_id)
                 .filter(model.Hindamiskogum.staatus==const.B_STAATUS_KEHTIV)
                 )
            for hk_id, in q.all():
                return hk_id
    
    def _create_suunamine(self):
        """Läbiviija suunamine siit kohast teise kohta
        """
        for key in self.request.params:
            # submit-nupu "Vali" nimi oli "valik_id_ID", siit saame uue testiruumi ID
            prefix = 'valik_id_'
            if key.startswith(prefix):
                testiruum_id = key[len(prefix):]
                break
        toimumisaeg = self.c.toimumisaeg
        testiruum = model.Testiruum.get(testiruum_id)
        assert testiruum.testikoht.toimumisaeg_id == toimumisaeg.id, _("vale toimumisaeg")

        labiviijad_id = self.request.params.get('labiviijad_id').split(',')
        for labiviija_id in labiviijad_id:
            if not labiviija_id:
                continue

            # läbiviija kirje vanas kohas, kust kasutaja suunatakse mujale
            lv = model.Labiviija.get(labiviija_id)
            if not lv:
                continue
            
            kasutaja_id = lv.kasutaja_id
            if not kasutaja_id:
                continue

            # eemaldame kasutaja vanast kohast
            lv.remove_labiviija()

            # uues kohas läbiviija kirje
            uus_lv = None
            # vaatame, kas uues kohas on samas rollis mõni kirje täitmata
            for rcd in testiruum.labiviijad:
                if rcd.kasutajagrupp_id == lv.kasutajagrupp_id \
                        and rcd.kasutaja_id is None:
                    uus_lv = rcd
                    break
            if not uus_lv:
                # loome vajadusel uue kirje
                uus_lv = testiruum.create_labiviija(lv.kasutajagrupp_id)

            # lisame kasutaja uude kohta
            kasutaja = model.Kasutaja.get(kasutaja_id)
            uus_lv.set_kasutaja(kasutaja, toimumisaeg)
            send_labiviija_maaramine(self, uus_lv, kasutaja, toimumisaeg)
            
        model.Session.commit()
        self.success()

        return self._redirect('index')

    def _new_mail(self):
        """Teate koostamise dialoogiakna avamine
        """
        koht = self.c.testikoht.koht
        testiruum = self.c.testikoht.testiruumid[0]

        data = {
            'test_nimi': self.c.toimumisaeg.testimiskord.test.nimi,
            'testiosa_nimi': self.c.toimumisaeg.testiosa.nimi,
            'aeg': self.h.str_from_datetime(testiruum.algus),
            'koht_nimi': koht.nimi,
            'tais_aadress': koht.tais_aadress or '',
            'user_nimi': self.c.user.fullname,
            }

        self.c.subject, self.c.body = self.render_mail('mail/test.labiviijateade.mako', data)
        return self.render_to_response('/ekk/korraldamine/labiviijad.mail.mako')

    def _create_mail(self):
        """Teate saatmine
        """
        labiviijad_id = self.request.params.get('labiviijad_id').split(',')
        self.form = Form(self.request, schema=forms.ekk.korraldamine.LabiviijaMailForm)
        if not self.form.validate():
            self.c.dialog_mail = True
            return Response(self.form.render(self._INDEX_TEMPLATE,
                                             extra_info=self._index_d()))
        else:
            msg_success = []
            for labiviija_id in labiviijad_id:
                if not labiviija_id:
                    continue
                rcd = model.Labiviija.get(labiviija_id)
                assert rcd.toimumisaeg_id == self.c.toimumisaeg.id, _("Vale toimumisaeg")
                kasutaja = rcd.kasutaja
                if kasutaja:
                    to = kasutaja.epost
                    if not to:
                        self.error(_("Kasutajal {s} pole e-posti aadressi").format(s=kasutaja.nimi))
                    else:
                        subject = self.form.data['subject']
                        body = self.form.data['body']
                        body += '\n\nTeate saatja: %s' % self.c.user.fullname
                        body = Mailer.replace_newline(body)
                        if not Mailer(self).send(to, subject, body):
                            msg_success.append(to)
                            kiri = model.Kiri(saatja_kasutaja_id=self.c.user.id,
                                              tyyp=model.Kiri.TYYP_MUU,
                                              sisu=body,
                                              teema=subject,
                                              teatekanal=const.TEATEKANAL_EPOST)
                            model.Labiviijakiri(labiviija=rcd, kiri=kiri)
                            model.Kirjasaaja(kiri=kiri, kasutaja_id=kasutaja.id, epost=to)
                            model.Session.commit()

            if len(msg_success):
                self.success('Teade on saadetud aadressidele: %s' % ', '.join(msg_success))
            else:
                self.error(_("Teadet ei saadetud"))
            
        return self._redirect('index')

    def _delete(self, item):
        if self.request.params.get('kasutaja_id'):
            # eemaldame kasutaja, aga kirje jääb alles
            item.kasutaja_id = None
            item.staatus = const.L_STAATUS_MAARAMATA
            self.success(_("Läbiviija on eemaldatud!"))
        else:
            # kui sama rolli on veel, siis eemaldame kirje
            if item.remove_labiviija():
                self.success(_("Läbiviija kirje on eemaldatud!"))
            else:
                self.success(_("Kirjet ei eemaldatud, sest see on ainuke selle rolli kirje"))

        model.Session.commit()

    def _after_update(self, parent_id=None):
        """Kuhu peale läbiviija kirje muutmist minna
        """
        return self._redirect('index')

    def _after_delete(self, parent_id=None):
        """Kuhu peale läbiviija kirje kustutamist minna
        """
        return self._redirect('index')

    def __before__(self):
        self.c.toimumisaeg = model.Toimumisaeg.get(self.request.matchdict.get('toimumisaeg_id'))
        #self.c.testiruum = model.Testiruum.get(self.request.matchdict.get('testiruum_id'))
        self.c.testikoht = model.Testikoht.get(self.request.matchdict.get('testikoht_id'))

    def _perm_params(self):
        return {'obj':self.c.testikoht}
