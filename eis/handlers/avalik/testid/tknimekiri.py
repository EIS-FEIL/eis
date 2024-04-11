from eis.lib.baseresource import *
from eis.handlers.avalik.testid.testinimekirjad import send_nimekirjateade
_ = i18n._
log = logging.getLogger(__name__)

class TknimekiriController(BaseResourceController):
    "Töölaualt uue jagamise alustamine"
    _permission = 'omanimekirjad'
    _MODEL = model.Nimekiri
    _actions = 'create,show,update,edit' # võimalikud tegevused
    
    def create(self, **kw):
        "Testi loomine töökogumikust tulles"        
        nimekiri = self._create()
        return self._after_create(nimekiri and nimekiri.id or None)

    def _create(self, **kw):
        c = self.c
        params = self.request.params
        op = params.get('op')
        s_ids = params.get('ids')
        ids = [int(uniqid[1:]) for uniqid in s_ids.split(',') if uniqid]
        if op == 'usetest':
            # valitud testi kasutamine
            if not ids:
                self.error(_("Test on valimata"))
                return
            test = model.Test.get(ids[0])
            if not test or not c.user.has_permission('omanimekirjad', const.BT_UPDATE, obj=test):
                self.error(_("Valitud test ei ole ligipääsetav"))
                return
        else:
            # lisatest,lisatoo - valitud ylesannetest uue testi/töö loomine
            if not ids:
                self.error(_("Ülesanded on valimata"))
                return
            ylesanded = self._check_ylesanded(ids)
            if not ylesanded:
                # veateade juba anti
                return
            
            test = self._lisa_test(op, ylesanded)
            
        nimekiri = model.Nimekiri.lisa_nimekiri(c.user, const.REGVIIS_KOOL_EIS, test)
        testiruum = None
        for osa in reversed(test.testiosad):
            koht_id = c.user.koht_id or const.KOHT_EKK
            testikoht = model.Testikoht.give_testikoht(koht_id, osa.id, None)
            testiruum = nimekiri.give_avalik_testiruum(testikoht)
        if test.testiliik_kood == const.TESTILIIK_TKY:
            # taustakysitluse õpetaja osa suunata õpetajale
            kasutaja = c.user.get_kasutaja()
            model.Sooritaja.reg_tky_opetaja(kasutaja, test, nimekiri)

        model.Session.commit()
        send_nimekirjateade(self, nimekiri, test)
        c.testiruum_id = testiruum.id
        c.nimekiri_id = nimekiri.id
        c.test_id = test.id
        return nimekiri

    def _check_ylesanded(self, ylesanded_id):
        # eemaldame korduvad
        ylesanded2_id = []
        for y_id in ylesanded_id:
            if y_id not in ylesanded2_id:
                ylesanded2_id.append(y_id)

        # kontrollime õigust
        lubatud = []
        no_perm = 0
        for ylesanne_id in ylesanded2_id:
            ylesanne = model.Ylesanne.get(ylesanne_id)
            if ylesanne and self.c.user.has_permission('suunamine', const.BT_SHOW, obj=ylesanne):
                lubatud.append(ylesanne)
            else:
                no_perm += 1
        if no_perm:
            self.error(_("{n} ülesande kasutamiseks polnud enam luba").format(n=no_perm))
        return lubatud
    
    def _lisa_test(self, op, ylesanded):
        "Uue testi/töö loomine"
        c = self.c

        aine_kood = None
        if op == 'lisatest':
            # jagatakse testina
            test_nimi = 'Test'
            testityyp = const.TESTITYYP_AVALIK
        else:
            # jagatakse ülesannetena
            test_nimi = 'Iseseisev töö'
            testityyp = const.TESTITYYP_TOO
        test_id = model.Test.gen_avalik_id()
        test = model.Test(id=test_id,
                          testityyp=testityyp,
                          staatus=const.T_STAATUS_KINNITATUD,
                          nimi=test_nimi,
                          aine_kood=aine_kood,
                          lang=const.LANG_ET,
                          avaldamistase=const.AVALIK_MAARATUD,
                          ymardamine=False,
                          arvutihinde_naitamine=True)

        test.logi('Loomine', None, None, const.LOG_LEVEL_GRANT)

        osa = test.give_testiosa()
        osa.vastvorm_kood = const.VASTVORM_KE
        kv = osa.give_komplektivalik()
        komplekt = kv.give_komplekt()
        komplekt.gen_tahis()
        komplekt.staatus = const.K_STAATUS_KINNITATUD
        komplekt.copy_lang(test)

        # testi looja saab kohe testiga seotud isikuks koostaja rollis
        test.add_testiisik(const.GRUPP_T_OMANIK)

        hkogum = kv.give_default_hindamiskogum()
        aine = test.aine_kood

        # lisame ylesanded
        seq = 0
        for ylesanne in ylesanded:
            seq += 1
            if not aine:
                for ya in ylesanne.ylesandeained:
                    aine = ya.aine_kood
                    break
            ty = model.Testiylesanne(hindamiskogum=hkogum,
                                     seq=seq,
                                     valikute_arv=1,
                                     tahis=str(seq),
                                     arvutihinnatav=ylesanne.arvutihinnatav,
                                     max_pallid=ylesanne.max_pallid,
                                     testiosa=osa)
            vy = ty.give_valitudylesanne(komplekt, ylesanne_id=ylesanne.id)
            vy.koefitsient = 1.

        if not test.aine_kood and aine:
            test.aine_kood = aine

        model.Session.flush()
        model.Session.refresh(hkogum)
        hkogum.arvuta_pallid(osa.lotv)
        test.arvuta_pallid()
        model.Session.flush()
        test.update_lang_by_y()
        komplekt.copy_lang(test)
        return test
    
    def _after_create(self, id):
        """Mida teha peale uue töö loomist
        """
        c = self.c
        if not id:
            # ei saanud uut testi luua, mingi viga oli
            url = self.url('tookogumikud')
        else:
            if not self.has_errors():
                self.success()
            op = self.request.params.get('op')
            if op == 'usetest':
                # suunamiseks jagati terve test, testi ei saa muuta
                url = self.url('test_nimekirjad', test_id=c.test_id, testiruum_id=c.testiruum_id)
            else:
                # suunamiseks jagati ylesanded (testina või ylesannetena)
                url = self.url('testid_edit_yldandmed', id=c.test_id, testiruum_id=c.testiruum_id)

        return HTTPFound(location=url)
