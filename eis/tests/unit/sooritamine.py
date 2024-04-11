import random
from datetime import date, timedelta, datetime
from eis.tests.basetest import *
from eis.handlers.avalik.sooritamine.sooritus import tos_set_komplekt
from eis.lib.resultentry import ResultEntry

kool_koht_id = 1048

class Sooritamine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = main({}, **settings)

    def setUp(self):
        self.app = TestApp(self.app)
        self.config = testing.setUp()

    def test_01(self):
        # leiame täna testikohas tehtava testi alustamata sooritajad
        today = date.today()
        q = (model.Session.query(model.Sooritaja)
             .filter(model.Sooritaja.algus>=today)
             .filter(model.Sooritaja.algus<today+timedelta(days=1))
             .filter(model.Sooritaja.created>=today)
             .join(model.Sooritaja.testimiskord)
             .join(model.Sooritaja.test)
             .filter(model.Test.nimi.ilike('Unit %'))
             .join(model.Sooritaja.sooritused)
             .filter(model.Sooritus.staatus==const.S_STAATUS_ALUSTAMATA)
             .join(model.Sooritus.testikoht)
             .filter(model.Testikoht.koht_id==kool_koht_id)
             )
        print(('%d sooritajat' % q.count()))
        for sooritaja in q.all():
            print('testi %d sooritaja %s' % (sooritaja.test_id, sooritaja.kasutaja.isikukood))
            for tos in sooritaja.sooritused:
                if tos.staatus == const.S_STAATUS_ALUSTAMATA:
                    self._soorita(sooritaja, tos)

        model.Session.commit()
        
    def _soorita(self, sooritaja, tos):
        testiosa = tos.testiosa
        test = testiosa.test
        tos.autentimine = const.AUTH_TYPE_PW
        tos.remote_addr = '127.0.0.1'
        tos.seansi_algus = datetime.now()
        tos_set_komplekt(tos, testiosa, tos.toimumisaeg)
        komplektid = set([ho.komplekt for ho in tos.hindamisolekud])
        for komplekt in komplektid:
            for vy in komplekt.valitudylesanded:
                if vy.seq == 1:
                    yv = tos.give_ylesandevastus(vy.testiylesanne_id, vy.id)
                    q = (model.Session.query(model.Ylesandevastus.id)
                         .join((model.Valitudylesanne,
                                model.Valitudylesanne.id==model.Ylesandevastus.valitudylesanne_id))
                         .filter(model.Valitudylesanne.ylesanne_id==vy.ylesanne_id)
                         .filter(model.Ylesandevastus.vastuseta==False)
                         )
                    cnt = q.count()
                    if cnt:
                        n = int(random.random() * cnt)
                        yv0_id, = q.offset(n).first()
                        yv0 = model.Ylesandevastus.get(yv0_id)
                        #print('ylesanne_id %d copy yv %d' % (vy.ylesanne_id, yv0_id))
                        for kv0 in yv0.kysimusevastused:
                            kv = kv0.copy()
                            yv.kysimusevastused.append(kv)
                            kv0.copy_subrecords(kv, ['kvsisud'])
                    
        for alatest in testiosa.alatestid:
            atos = tos.give_alatestisooritus(alatest.id)
            atos.seansi_algus = datetime.now()
            atos.staatus = const.S_STAATUS_TEHTUD
        tos.set_staatus(const.S_STAATUS_TEHTUD)
        model.Session.flush()
        
        user = TestUser.get_testuser()
        model.usersession.set_user(user)
        handler = user.handler
        tos.give_hindamisolekud()
        #calculate(handler, tos, sooritaja.lang, test, testiosa)
        sooritaja.update_staatus()
        resultentry = ResultEntry(handler, const.SISESTUSVIIS_VASTUS, test, testiosa)
        for holek in tos.hindamisolekud:
            resultentry.update_hindamisolek(sooritaja, tos, holek, is_update_sooritus=False)
        resultentry.update_sooritus(sooritaja, tos)

