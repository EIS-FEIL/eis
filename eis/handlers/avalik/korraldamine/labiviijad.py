from eis.lib.baseresource import *
_ = i18n._
from eis.lib.xtee import rahvastikuregister
from eis.handlers.ekk.otsingud.labiviijateated import send_labiviija_maaramine
log = logging.getLogger(__name__)

class LabiviijadController(BaseResourceController):
    _permission = 'avalikadmin'
    _MODEL = model.Labiviija
    _INDEX_TEMPLATE = '/avalik/korraldamine/labiviijad.mako' 
    _LIST_TEMPLATE = '/avalik/korraldamine/labiviijad_list.mako'
    _DEFAULT_SORT = 'kasutaja.isikukood'
    _no_paginate = True
    _perm_koht = True
    
    def _query(self):
        c = self.c
        q = (model.Session.query(model.Labiviija,
                                 model.Kasutaja,
                                 model.Testiruum.tahis,
                                 model.Ruum.tahis,
                                 model.Testiruum.algus)
             .filter(model.Labiviija.testikoht_id==self.c.testikoht.id)
             .outerjoin(model.Labiviija.kasutaja)
             .outerjoin(model.Labiviija.testiruum)
             .outerjoin(model.Testiruum.ruum)
             )
        if c.toimumisaeg.ruum_noutud:
            # kui määramata ruumi ei või kasutada,
            # siis määramata ruumiga testiruume ei kuva
            q = q.filter(sa.or_(
                model.Labiviija.kasutaja_id!=None,
                model.Testiruum.id==None,
                model.Testiruum.ruum_id!=None))

        # kas kuvada uue administraatori lisamise nupp
        if c.toimumisaeg.admin_maaraja:
            # kuvada uue lisamise nupp ainult siis, kui määramata isikuga rolle pole (ES-2774)
            q1 = (q.filter(model.Labiviija.kasutajagrupp_id==const.GRUPP_T_ADMIN)
                  .filter(model.Labiviija.kasutaja_id==None))
            c.on_lisa_admin = q1.count() == 0
            
        return q

    def _prepare_header(self):
        header = [_("Testi läbiviija"),
                  _("Tähis"),
                  _("Testiruum"),
                  _("Ruum"),
                  _("Algus"),
                  _("Roll"),
                  _("Olek"),
                  ]
        return header
    
    def _prepare_item(self, rcd, n):
        c = self.c
        lv, k, testiruum_tahis, ruum_tahis, testiruum_algus = rcd
        item = [k and k.nimi,
                lv.tahis,
                testiruum_tahis,
                ruum_tahis,
                self.h.str_from_datetime(testiruum_algus or c.testikoht.alates),
                lv.kasutajagrupp_nimi,
                lv.staatus_nimi,
                ]
        return item

    def _create(self, **kw):
        c = self.c

        # leiame valitud kasutaja, keda soovitakse määrata läbiviijaks
        kasutaja_id = kasutaja = None
        op = self.request.params.get('op')
        prefix = 'valik_id_'
        if op.startswith(prefix):
            kasutaja_id = int(op[len(prefix):])

        if kasutaja_id:
            # kontrollime, et kasutaja sellel toimumisajal pole veel rakendatud
            qk = (model.Labiviija.query.filter_by(kasutaja_id=kasutaja_id)
                  .filter_by(toimumisaeg_id=c.toimumisaeg.id))
            if qk.count() > 0:
                self.notice(_("Kasutaja on juba määratud sellel toimumisajal osalema!"))
            kasutaja = model.Kasutaja.get(kasutaja_id)

        # leiame kirje, millele isiku määrame
        labiviija_id = self.request.params.get('labiviija_id')
        labiviijad = []
        if labiviija_id:
            # isiku valimine olemasolevale läbiviija kirjele
            item = model.Labiviija.get(labiviija_id)
            assert item.kasutajagrupp_id in (c.lubatud_grupid_id), _("Vale grupp")
            assert item.testikoht_id == c.testikoht.id, 'vale testiruum'
            labiviijad.append(item)
        else:
            # uue läbiviija kirje lisamine
            grupp_id = int(self.request.params.get('grupp_id'))
            assert grupp_id in (c.lubatud_grupid_id), _("Vale grupp")

            if grupp_id == const.GRUPP_KOMISJON_ESIMEES and not c.toimumisaeg.on_ruumiprotokoll:
                # testikoha roll
                item = c.testikoht.create_labiviija(grupp_id)
                labiviijad.append(item)
            else:
                # testiruumi roll
                testiruumid_id = self.request.params.getall('testiruum_id')
                if not testiruumid_id:
                    raise ValidationError(self, {}, _("Palun valida ruum!"))
                # hindaja rolli korral leitakse hindamiskogum
                hindamiskogum_id = self._get_hindamiskogum_id(grupp_id)
                for testiruum_id in testiruumid_id:
                    testiruum = model.Testiruum.get(testiruum_id)
                    assert testiruum.testikoht_id == c.testikoht.id, 'vale testiruum'
                    item = testiruum.create_labiviija(grupp_id)
                    if hindamiskogum_id:
                        item.hindamiskogum_id = hindamiskogum_id
                    labiviijad.append(item)

        # määrame isiku läbiviija kirjesse
        for item in labiviijad:
            item.set_kasutaja(kasutaja, c.toimumisaeg)
            if kasutaja:
                send_labiviija_maaramine(self, item, kasutaja, c.toimumisaeg)
        return item

    def _get_hindamiskogum_id(self, grupp_id):
        # (suulise) hindaja rollil peab olema ka hindamiskogum
        if grupp_id in (const.GRUPP_HINDAJA_S,
                        const.GRUPP_HINDAJA_S2,
                        const.GRUPP_HINDAJA_K):
            testiosa_id = self.c.toimumisaeg.testiosa_id
            q = (model.Session.query(model.Hindamiskogum.id)
                 .filter(model.Hindamiskogum.testiosa_id==testiosa_id)
                 .filter(model.Hindamiskogum.staatus==const.B_STAATUS_KEHTIV)
                 )
            for hk_id, in q.all():
                return hk_id
    
    def _error_create(self):
        return self._redirect('index')

    def _delete(self, item):
        assert item.kasutajagrupp_id in (self.c.lubatud_grupid_id), _("Vale grupp")
        if item.remove_labiviija():
            self.success(_("Läbiviija on eemaldatud!"))
        else:
            self.success(_("Läbiviijat ei saanud eemaldada"))

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
        c = self.c
        c.testikoht = model.Testikoht.get(self.request.matchdict.get('testikoht_id'))
        c.toimumisaeg = c.testikoht.toimumisaeg

        c.lubatud_grupid_id = [const.GRUPP_KOMISJON, const.GRUPP_KOMISJON_ESIMEES, const.GRUPP_T_ADMIN]

        if c.toimumisaeg.labiviijate_jaotus:
            # kui läbiviijate määramine pole lõpetatud
            # ja soorituskohal on õigus läbiviijaid määrata
            if c.toimumisaeg.hindaja1_maaraja in const.MAARAJA_KOHAD:
                on_suuline = c.toimumisaeg.testiosa.vastvorm_kood in (const.VASTVORM_SH, const.VASTVORM_SP)
                if on_suuline:
                    c.lubatud_grupid_id.append(const.GRUPP_HINDAJA_S)
                else:
                    c.lubatud_grupid_id.append(const.GRUPP_HINDAJA_K)
            if c.toimumisaeg.hindaja2_maaraja in const.MAARAJA_KOHAD:
                c.lubatud_grupid_id.append(const.GRUPP_HINDAJA_S2)
            if c.toimumisaeg.intervjueerija_maaraja == const.MAARAJA_KOHT:
                c.lubatud_grupid_id.append(const.GRUPP_INTERVJUU)

    def _perm_params(self):
        if self.c.testikoht.koht_id != self.c.user.koht_id:
            return False
