from eis.lib.base import *
from eis.lib.pangalink import Pangalink
import eis.lib.regpiirang as regpiirang
import eis.lib.xtee.ehis as ehis
from eis.handlers.ekk.otsingud.kohateated import send_regteade
log = logging.getLogger(__name__)
_ = i18n._

class KinnitamineController(BaseController):
    _permission = 'sooritamine'
    _log_params_post = True
    _actions = 'index,create,delete'
    
    def index(self):
        self._index()
        return self.render_to_response('avalik/regamine/avaldus.kinnitamine.mako')
        
    def _index(self):
        c = self.c
        res = c.kasutaja.get_reg_sooritajad(c.testiliik, peitmata=True, regamine=True)
        c.sooritajad = list(res)
        if len(c.sooritajad) == 0:
            self.error('Palun valida testid')
            return HTTPFound(location=self.url('regamine_avaldus_testid', testiliik=c.testiliik))
        if not c.testiliik:
            # testiliik puudub URLis, kasutame esimese regamata testi liiki
            c.testiliik = c.sooritajad[0].test.testiliik_kood
            # ja kysime ainult seda liiki testile regamisi
            res = c.kasutaja.get_reg_sooritajad(c.testiliik, peitmata=True, regamine=True)
            c.sooritajad = list(res)            

        tasumata = 0
        for rcd in c.sooritajad:
            if rcd.tasutud == False:
                tasumata += rcd.tasu or 0
        c.tasumata = tasumata

    def kinnitatud(self):
        c = self.c
        self._index()
        if c.tasumata:
            c.pangad = Pangalink.get_list()

        # kui tullaks pangast, siis ei ole veel teade saadetud ja saadetakse siin
        self._send_regteade(self.c.testiliik, False)
        return self.render_to_response('avalik/regamine/avaldus.kinnitatud.mako')

    def create(self):
        testiliik = self.c.testiliik
        uuesti = self.request.params.get('saadauuesti') or False

        sooritajad = self.c.kasutaja.get_reg_sooritajad(testiliik, peitmata=True, regamine=True)
        regatud = []
        regamata = []
        for r in sooritajad:
            if r.staatus in (const.S_STAATUS_REGATUD, const.S_STAATUS_TASUMATA):
                regatud.append(r)
            else:
                regamata.append(r)

        on_kinnitanud = on_tasumata = False
        if not uuesti and regamata:
            # kinnitame regamata registreeringud
            on_kinnitanud, on_tasumata = self._kinnita(testiliik, regamata)
            
        if uuesti or on_kinnitanud:
            self._send_regteade(testiliik, uuesti)
                
        if regatud or on_kinnitanud or on_tasumata:
            # peale kinnitamist või regatud regamise vaatamist tuleb kinnitamise kontroll
            return HTTPFound(location=self.url_current('kinnitatud', testiliik=testiliik))
        else:
            # kui kinnitatud regamisi pole, siis tagasi otsingusse
            return HTTPFound(location=self.url('regamised'))
            
    def _kinnita(self, testiliik, regamata):
        "Kinnitamine"
        on_kinnitanud = on_tasumata = False
        ained = set()
        kasutaja_id = self.c.kasutaja.id
        regid = [(r, r.testimiskord) for r in regamata]
        # ES-1778 - regamisel ei tohi arvestada juba regatud olekus teste,
        # sest regamise tingimused ei pruugi enam olla täidetud
        tkorrad = [r[1] for r in regid]
        for rcd, tkord in regid:
            test = rcd.test
            err = None
            # kinnitame registreeringu
            if testiliik == const.TESTILIIK_TASE:
                err = regpiirang.reg_te_piirang1(self, kasutaja_id, rcd.id)
                if not err:
                    dt_min, piirang = regpiirang.reg_te_piirang(self, kasutaja_id, rcd.id)            
                    if piirang and dt_min and tkord and tkord.alates < dt_min:
                        err = 'Eksamit ei saa sooritada enne kuupäeva %s (%s)' % (self.h.str_from_date(dt_min), piirang)
            elif testiliik == const.TESTILIIK_SEADUS:
                err = regpiirang.reg_se_piirang1(self, kasutaja_id, rcd.id)
            elif testiliik in (const.TESTILIIK_RIIGIEKSAM, const.TESTILIIK_RV):
                aine = test.aine_kood
                if aine == const.AINE_ET and const.AINE_ET2 in ained or \
                   aine == const.AINE_ET2 and const.AINE_ET in ained:
                    err = 'Korraga ei või registreerida nii eesti keele riigieksamile kui ka eesti keele teise keelena riigieksamile'
                ained.add(aine)
                
                if not err and tkord.cae_eeltest:
                    err = ehis.uuenda_opilased(self, [self.c.kasutaja.isikukood])
                    if not err:
                        # CAE rv ja ingl k riigieksamile korraga ei saa avalikus vaates regada
                        err = regpiirang.reg_rven_cae(self, kasutaja_id, test, tkorrad)
                    if not err:
                        err = regpiirang.reg_rv_cae(self, kasutaja_id, test, tkord)
                
                if not err and test.testiliik_kood == const.TESTILIIK_RIIGIEKSAM:
                    # riigieksami lisaeksamile ei saa regada seda,
                    # kes on samal testsessioonil samas aines põhieksamile registreeritud või tehtud
                    err = regpiirang.reg_r_lisaeksam(self, kasutaja_id, test, tkord)
                    if not err and test.aine_kood == const.AINE_EN:
                        # CAE rv ja ingl k riigieksamile korraga ei saa avalikus vaates regada
                        err = regpiirang.reg_rven_cae(self, kasutaja_id, test, tkorrad)
                if not err and test.testiliik_kood == const.TESTILIIK_RV:
                    err = regpiirang.check_rv(self, rcd, self.c.kasutaja)                    

            if not err and test.aine_kood == const.AINE_ET2:
                err = regpiirang.reg_et2(self, self.c.kasutaja, test, self.c.kasutaja.opilane)
            if err:
                self.error(err)
                return False, False
            if not rcd.reg_aeg:
                rcd.reg_aeg = datetime.now()
            rcd.set_ehis_data()
            rcd.kinnita_reg()
            if rcd.staatus == const.S_STAATUS_REGATUD:
                on_kinnitanud = True
            elif rcd.staatus == const.S_STAATUS_TASUMATA:
                on_tasumata = True
        model.Session.commit()
        return on_kinnitanud, on_tasumata

    def _send_regteade(self, testiliik, uuesti):
        # saadame teate
        if send_regteade(self, self.c.kasutaja, testiliik, False, kordus=uuesti):
            model.Session.commit()
            epost = self.c.kasutaja.epost
            if epost:
                self.notice2(epost)
            # uuendame uute kirjade arvu
            self.c.user.get_new_msg(self.request.session, 0)
            
    def delete(self):
        testiliik = self.c.testiliik
        for rcd in [r for r in self.c.kasutaja.get_reg_sooritajad(testiliik, peitmata=True, kinnitamata=True)]:
            # kustutame kinnitamata registreeringud
            rcd.tyhista()
            rcd.delete()
        model.Session.commit()
        return HTTPFound(location=self.url('regamised'))

    def __before__(self):
        self.c.kasutaja = self.c.user.get_kasutaja()
        self.c.testiliik = self.request.matchdict.get('testiliik')
