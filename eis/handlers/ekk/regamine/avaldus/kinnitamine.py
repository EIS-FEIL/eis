# -*- coding: utf-8 -*- 

from eis.lib.base import *
_ = i18n._
import eis.handlers.ekk.otsingud.kohateated as kt
import eis.lib.regpiirang as regpiirang
log = logging.getLogger(__name__)

class KinnitamineController(BaseController):
    _permission = 'regamine'
    def edit(self):
        self.c.testiliik = self.request.params.get('testiliik')
        sooritajad = self.c.kasutaja.get_reg_sooritajad(self.c.testiliik)
        if len(sooritajad) == 0:
            self.error(_("Palun valida testid"))
            return HTTPFound(location=self.url('regamine_avaldus_testid', 
                                               id=self.c.kasutaja.id))

        for rcd in sooritajad:
            test = rcd.test
            if test.testiliik_kood == const.TESTILIIK_TASE:
                # mitmele tasemeeksamile ei või korraga regada - hoiatus ES-1078
                piirang = regpiirang.reg_te_piirang1(self, self.c.kasutaja.id, rcd.id, app_ekk=True)
                if piirang:
                    self.notice(piirang)

        self.c.tasu = 0
        self.c.tasutud = True
        for rcd in sooritajad:
            if rcd.tasu and rcd.tasutud == False:
                self.c.tasu += rcd.tasu
                self.c.tasutud = False

        return self.render_to_response('ekk/regamine/avaldus.kinnitamine.mako')

    def update(self):
        katkesta = self.request.params.get('katkesta')
        testiliik = self.request.params.get('testiliik')
        for rcd in self.c.kasutaja.get_reg_sooritajad(testiliik):
            if katkesta and rcd.staatus == const.S_STAATUS_REGAMATA:
                rcd.delete()
            else:
                if rcd.tasu:
                    rcd.tasutud = bool(self.request.params.get('tasutud_%s' % rcd.id))
                else:
                    rcd.tasutud = None

                test = rcd.test
                if test.testiliik_kood == const.TESTILIIK_RIIGIEKSAM:
                    # riigieksami lisaeksamile ei saa regada seda,
                    # kes on samal testsessioonil samas aines põhieksamile registreeritud või tehtud
                    error = regpiirang.reg_r_lisaeksam(self, self.c.kasutaja.id, test, rcd.testimiskord)
                    if error:
                        self.error(error)
                        return self._redirect('edit', testiliik=testiliik)

                if not rcd.reg_aeg:
                    rcd.reg_aeg = datetime.now()
                rcd.set_ehis_data()
                rcd.kinnita_reg()
        model.Session.commit()

        if not katkesta and self.request.is_ext():
            if self.request.params.get('regteade'):
                # saadame registreerimise teate
                if kt.send_regteade(self, self.c.kasutaja, testiliik):
                    self.success(_("Registreerimise teade on saadetud"))

        model.Session.commit()

        kasutaja_id = self.request.matchdict.get('id')
        return HTTPFound(location=self.url('regamised', 
                                           kasutaja_id=kasutaja_id,
                                           testiliik=testiliik,
                                           focus_avaldus=True))

    def __before__(self):
        id = self.request.matchdict.get('id')
        self.c.kasutaja = model.Kasutaja.get(id)
