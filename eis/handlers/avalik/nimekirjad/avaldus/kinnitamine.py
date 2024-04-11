from eis.lib.base import *
_ = i18n._
import eis.handlers.ekk.otsingud.kohateated as kt
import eis.lib.regpiirang as regpiirang
import eis.lib.xtee.ehis as ehis
log = logging.getLogger(__name__)

class KinnitamineController(BaseController):
    _permission = 'nimekirjad'
    def edit(self):
        c = self.c
        c.testiliik = self.request.params.get('testiliik')
        sooritajad = c.kasutaja.get_reg_sooritajad(c.testiliik)
        if len(sooritajad) == 0:
            self.error(_("Palun valida testid"))
            url = self.url('nimekirjad_avaldus_testid', id=c.kasutaja.id, testiliik=c.testiliik)            
            return HTTPFound(location=url)

        c.tasu = 0
        c.tasutud = True
        for rcd in sooritajad:
            if rcd.tasu and rcd.tasutud == False:
                c.tasu += rcd.tasu
                c.tasutud = False

        return self.render_to_response('avalik/nimekirjad/avaldus.kinnitamine.mako')

    def update(self):
        c = self.c
        testiliik = self.request.params.get('testiliik')
        regid = [(r, r.testimiskord) for r in c.kasutaja.get_reg_sooritajad(testiliik)]
        testimiskorrad = [r[1] for r in regid]
        for rcd, testimiskord in regid:
            if rcd.tasu:
                rcd.tasutud = bool(self.request.params.get('tasutud_%s' % rcd.id))
            else:
                rcd.tasutud = None

            test = rcd.test
            err = None
            if test.testiliik_kood == const.TESTILIIK_RIIGIEKSAM:
                # riigieksami lisaeksamile ei saa regada seda,
                # kes on samal testsessioonil samas aines põhieksamile registreeritud või tehtud
                err = regpiirang.reg_r_lisaeksam(self, c.kasutaja.id, test, testimiskord)
                if not err and test.aine_kood == const.AINE_EN:
                    # CAE rv ja ingl k riigieksamile korraga ei saa avalikus vaates regada
                    err = regpiirang.reg_rven_cae(self, c.kasutaja.id, test, testimiskorrad)

            elif test.testiliik_kood == const.TESTILIIK_RV:
                if testimiskord.cae_eeltest:
                    err = ehis.uuenda_opilased(self, [c.kasutaja.isikukood])
                    if not err:
                        # CAE rv ja ingl k riigieksamile korraga ei saa avalikus vaates regada
                        err = regpiirang.reg_rven_cae(self, c.kasutaja.id, test, testimiskorrad)
                    if not err:
                        err = regpiirang.reg_rv_cae(self, c.kasutaja.id, test, testimiskord)

            if not err and test.aine_kood == const.AINE_ET2:
                err = regpiirang.reg_et2(self, c.kasutaja, test, c.kasutaja.opilane)
            if err:
                self.error(err)
                break
            if not rcd.reg_aeg:
                rcd.reg_aeg = datetime.now()
            rcd.set_ehis_data()
            rcd.kinnita_reg()

        if not self.has_errors():
            model.Session.commit()
            if self.request.is_ext():
                if self.request.params.get('regteade'):
                    # saadame registreerimise teate
                    if kt.send_regteade(self, c.kasutaja, testiliik):
                        self.success(_("Registreerimise teade on saadetud"))
                model.Session.commit()

        kasutaja_id = self.request.matchdict.get('id')
        return HTTPFound(location=self.url('nimekirjad_testimiskorrad'))

    def delete(self):
        testiliik = self.request.params.get('testiliik')
        for rcd in [r for r in self.c.kasutaja.get_reg_sooritajad(testiliik, peitmata=True, kinnitamata=True)]:
            # kustutame kinnitamata registreeringud
            rcd.tyhista()
            rcd.delete()
        model.Session.commit()
        return HTTPFound(location=self.url('nimekirjad_testimiskorrad'))

    def __before__(self):
        id = self.request.matchdict.get('id')
        self.c.kasutaja = model.Kasutaja.get(id)

    def _perm_params(self):
        testiliik = self.request.params.get('testiliik')
        if testiliik:
            return {'testiliik': testiliik, 'koht_id': self.c.user.koht_id}
