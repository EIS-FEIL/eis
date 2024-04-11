from eis.lib.baseresource import *
from eis.handlers.admin.ehisopetajad import opt_koolipedagoogid
_ = i18n._
log = logging.getLogger(__name__)

class AineopetajadController(BaseResourceController):
    _permission = 'avalikadmin'
    _index_after_create = True # et peale volitamata muutmiskatset mindaks indeksisse
    _get_is_readonly = False
    _EDIT_TEMPLATE = 'avalik/korraldamine/new.aineopetaja.mako'
    
    # sub roll on soorituskoha administraatori määramine
    def _new_roll(self):
        self.c.roll = self.c.new_item()
        self._get_opt()
        return self.render_to_response('/avalik/korraldamine/new.aineopetaja.mako')

    def _get_opt(self):
        self.c.opt_pedagoogid = opt_koolipedagoogid(self, self.c.user.koht_id)        
    
    def _create_roll(self):
        "Isik valiti otsingutulemustest"
        self.form = Form(self.request, schema=forms.admin.KoharollForm)
        if not self.form.validate():
            self.c.roll = self.c.new_item()
            self.c.nosub = True
            self._get_opt()
            return Response(self.form.render(self._EDIT_TEMPLATE,
                                             extra_info=self.response_dict))

        data = self.form.data
        kehtib_kuni = const.MAX_DATE
        kasutajagrupp_id = const.GRUPP_AINEOPETAJA
        aine_kood = self.c.testikoht.toimumisaeg.testimiskord.test.aine_kood

        rc = False
        for k_id in self.request.params.getall('oigus'):
            kasutaja = model.Kasutaja.get(k_id)
            if kasutaja:
                if model.Kasutajaroll.query.\
                        filter_by(kasutaja_id=kasutaja.id).\
                        filter_by(koht_id=self.c.koht.id).\
                        filter_by(aine_kood=aine_kood).\
                        filter_by(kasutajagrupp_id=kasutajagrupp_id).\
                        count() > 0:
                    self.error(_("Kasutaja {s} juba on antud rollis").format(s=kasutaja.nimi))
                    continue

            if not kasutaja:
                # RRist saadud nimi
                eesnimi = self.request.params.get('eesnimi')
                perenimi = self.request.params.get('perenimi')
                kasutaja = model.Kasutaja.add_kasutaja(isikukood, eesnimi, perenimi)
                kasutaja.on_labiviija = True
                model.Session.flush()
            if not kasutaja.on_labiviija:
                kasutaja.on_labiviija = True
            item = model.Kasutajaroll(kasutajagrupp_id=kasutajagrupp_id,
                                      kasutaja_id=kasutaja.id,
                                      koht_id=self.c.koht.id,
                                      aine_kood=aine_kood,
                                      kehtib_alates=date.today(),
                                      kehtib_kuni=kehtib_kuni)
            self._log_roll(item, False)
            rc = True
        if rc:
            model.Session.commit()
            self.success()
        return HTTPFound(location=self.url('korraldamine_sooritajad', testikoht_id=self.c.testikoht.id))
            
    def _create_rollped(self):
        "Isik valiti kooli pedagoogide valikust"
        pedagoogid_id = self.request.params.getall('pedagoog_id')
        if not pedagoogid_id:
            self.form = Form(self.request, schema=forms.NotYetImplementedForm)
            self.error(_("Palun valida õpetaja"))
            self.c.nosub = True
            self._get_opt()
            return Response(self.form.render(self._EDIT_TEMPLATE,
                                             extra_info=self.response_dict))

        kehtib_kuni = const.MAX_DATE
        kasutajagrupp_id = const.GRUPP_AINEOPETAJA
        aine_kood = self.c.testikoht.toimumisaeg.testimiskord.test.aine_kood

        rc = False
        for pedagoog_id in pedagoogid_id:
            pedagoog = model.Pedagoog.get(pedagoog_id)
            if pedagoog:
                kasutaja = model.Kasutaja.get_by_ik(pedagoog.isikukood)
                if not kasutaja:
                    kasutaja = model.Kasutaja.add_kasutaja(pedagoog.isikukood,
                                                           pedagoog.eesnimi,
                                                           pedagoog.perenimi)
                    kasutaja.on_labiviija = True
                    pedagoog.kasutaja = kasutaja
                    model.Session.flush()
                if not kasutaja.on_labiviija:
                    kasutaja.on_labiviija = True
                item = model.Kasutajaroll(kasutajagrupp_id=kasutajagrupp_id,
                                          kasutaja_id=kasutaja.id,
                                          koht_id=self.c.koht.id,
                                          aine_kood=aine_kood,
                                          kehtib_alates=date.today(),
                                          kehtib_kuni=kehtib_kuni)
                self._log_roll(item, False)
                rc = True
        if rc:
            model.Session.commit()
            self.success()
        return HTTPFound(location=self.url('korraldamine_sooritajad', testikoht_id=self.c.testikoht.id))

    def _log_roll(self, roll, is_delete):
        grupp_id = roll.kasutajagrupp_id
        if is_delete:
            sisu = 'Eemaldamine\n' + roll.get_str()
        else:
            old_values, new_values = roll._get_changed_values()
            if not new_values:
                return
            sisu = roll.get_str()
        krl = model.Kasutajarollilogi(kasutaja_id=roll.kasutaja_id,
                                      muutja_kasutaja_id=self.c.user.id,
                                      aeg=datetime.now(),
                                      sisu=sisu,
                                      kasutajagrupp_id=grupp_id,
                                      tyyp=const.USER_TYPE_KOOL)
        roll.kasutajarollilogid.append(krl)

    def _perm_params(self):
        if self.c.testikoht.koht_id != self.c.user.koht_id:
            return False

    def __before__(self):
        testikoht_id = self.request.matchdict.get('testikoht_id')
        self.c.testikoht = model.Testikoht.get(testikoht_id)
        self.c.koht = self.c.testikoht.koht

