# /srv/eis/bin/python -m unittest -q eis.tests.unit.test.TestTests
# python setup.py test -s eis.tests.unit.test.TestTests

from datetime import date, timedelta, datetime
from eis.tests.basetest import *
import eis.handlers.ekk.korraldamine.valjastus as valjastus
# ylesanded.py test_50 loodud ylesanded
ylesanded_id = (2624,424,425,426,427,428,429,430,431)
k_ylesanded_id = (181,1712,1713,1710,1711,1717,1718,1715,1716)
ylesanded_id = (12942,10,12,15,20,1014,1015,1016,1017,1018,1019,1020,1021,72,2624,1802,1023,3022,3023,3024,3025,3026,3027,3028)
k_ylesanded2_id = (1711,1717,1718,1715,1716)
ylesanded2_id = (2624,1802,1023,3022,3023,3024,3025,3026,3027,3028)
opilased_ik = ('48101110215',
               '48011228870',
               '48010109918',
               '48001228877',
               '31511173826',
               '31511222637',
               '31511278251',
               '31512037818',
               '31512102198',
               '31512119042',
               '31512161579',
               '31512172638',
               '31512193976',
               '31512201446',
               '31512218650',
               '31601198628',
               '31601206724',
               '31601222658',
               '31601289178',
               '31602176004',
               '31602233765',
               '31602269354',
               '31602274757',
               '31603029190',
               '33008163425',
               '33008207552',
               '33008212846',
               '33008255789',
               '33008276102',
               '33009054937',
               '33009103639',
               '33009116408',
               '33009260293',
               '33009261987',
               '33010037830',
               '33010097207',
               '33010101256',
               '33010161657',
               '33010198472',
               '33010209598',
               '33010228157',
               '33010262769',
               '33010274432',
               '33011050325',
               )
kool_koht_id = 1048

class TestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = main({}, **settings)

    def setUp(self):
        self.app = TestApp(self.app)
        self.config = testing.setUp()
        model.usersession.set_user(TestUser.get_testuser())
        
    def test_01(self):
        test = self._create_test()
        if test:
            tk = self._create_testimiskord(test)
            if tk:
                self._create_sooritajad(test, tk)
                self._create_testikohad(test, tk)
                self._create_labiviijad(test, tk)
                self._create_hindajad(test, tk)
                self._valjasta(test, tk)
        model.Session.commit()
        
    def _create_test(self):
        test = model.Test(nimi='Unit Test',
                          testityyp=const.TESTITYYP_EKK,
                          avaldamistase=const.AVALIK_EKSAM,
                          aine_kood='B',
                          testiliik_kood=const.TESTILIIK_POHIKOOL,
                          max_pallid=30,
                          lang=const.LANG_ET,
                          skeeled=const.LANG_ET)
        self._create_testiosa(test, 1, ylesanded_id, k_ylesanded_id)
        self._create_testiosa(test, 2, ylesanded2_id, k_ylesanded2_id)

        test.arvuta_pallid()
        model.Session.flush()
        test.staatus = const.T_STAATUS_KINNITATUD
        test.nimi = 'Unit Test %s %s' % (test.id, date.today().isoformat())
        print('Loodud test %d' % test.id)
        return test

    def _create_testiosa(self, test, seq, ylesanded_id, k_ylesanded_id):
        osa1 = model.Testiosa(max_pallid=100,
                              seq=seq,
                              tahis=f'{seq}',
                              nimi=f'osa {seq}',
                              vastvorm_kood=const.VASTVORM_KE,
                              test=test)
        test.testiosad.append(osa1)
        osa1.max_pallid = 100
        #osa1.skoorivalem = '50 + 16 * (SKOOR-0)/4.52'
        
        for i in range(8):
            arvutihinnatav = i<4
            arvutihinnatav = True
            ty = model.Testiylesanne(seq=i+1,
                                     nimi='Ülesanne %d' % (i+1),
                                     tahis=str(i+1),
                                     hindamine_kood=const.HINDAMINE_OBJ,
                                     arvutihinnatav=arvutihinnatav,
                                     max_pallid=10,
                                     testiosa=osa1)
            #osa1.testiylesanded.append(ty)

        kv = osa1.give_komplektivalik()
        y_ind = 0
        for i in range(2):
            k = model.Komplekt(staatus=const.K_STAATUS_KINNITATUD,
                               lukus=const.LUKUS_KINNITATUD,
                               tahis='%s' % (i+1),
                               skeeled='et')
            kv.komplektid.append(k)
            for ty in osa1.testiylesanded:
                if y_ind >= len(ylesanded_id) or y_ind >= len(k_ylesanded_id):
                    y_ind = 0
                vy = ty.give_valitudylesanne(k)
                if ty.arvutihinnatav:
                    vy.ylesanne_id = ylesanded_id[y_ind]
                else:
                    vy.ylesanne_id = k_ylesanded_id[y_ind]
                print(('Komplekt %s ty %s y %s' % (k.tahis, ty.tahis, vy.ylesanne_id)))
                y_ind += 1
        
        valemid = {
            0:'(OIGED+0.83)*4.39',
            1:'(OIGED+1.01)*4.58',
            }
        for i in range(2):
            alatest = model.Alatest(seq=i+1,
                                    nimi='Alatest %d' % (i+1),
                                    max_pallid=25,
                                    #skoorivalem=valemid.get(i),
                                    vastvorm_kood=const.VASTVORM_KE,
                                    komplektivalik=kv)
            osa1.alatestid.append(alatest)

        kv.alatestideta = None    
        for ty in osa1.testiylesanded:
            ty.alatest = ty.seq <= 2 and osa1.alatestid[0] or osa1.alatestid[1]

        hkogumid = []
        for n_hk in range(1,3):
            hk = model.Hindamiskogum(testiosa=osa1,
                                     tahis='HK%d' % n_hk,
                                     nimi='Hindamiskogum %d' % n_hk,
                                     hindamine_kood=const.HINDAMINE_OBJ,
                                     arvutihinnatav=n_hk<=1,
                                     tasu=5,
                                     komplektivalik=kv)
            #osa1.hindamiskogumid.append(hk)
            hkogumid.append(hk)

            for ty in osa1.testiylesanded:
                if ty.arvutihinnatav == hk.arvutihinnatav:
                    hk.testiylesanded.append(ty)

        model.Session.flush()
        for ty in osa1.testiylesanded:
            ty.update_koefitsient()            

        hk.arvuta_pallid(osa1.lotv)
    
    def _create_testimiskord(self, test):
        assert test and test.id, 'Test puudub'

        tk = model.Testimiskord(test=test,
                                tahis='TK1',
                                aasta=2022,
                                reg_sooritaja=True,
                                reg_sooritaja_alates=date.today(),
                                reg_sooritaja_kuni=date.today() + timedelta(days=30),
                                skeeled='et')

        opt_sessioon = model.Testsessioon.get_opt(test.testiliik_kood)
        if opt_sessioon:
            tk.testsessioon_id = opt_sessioon[0][0]
        
        tk.give_toimumisajad()
        model.Session.flush()
        for ta in tk.toimumisajad:
            print('Loodud toimumisaeg %s' % ta.id)
            for kv in ta.testiosa.komplektivalikud:
                for k in kv.komplektid:
                    ta.komplektid.append(k)
            tpaev = model.Toimumispaev(aeg=datetime.now(),
                                       toimumisaeg=ta)
            #ta.toimumispaevad.append(tpaev)
            ta.komplekt_valitav = True
            ta.admin_maaraja = True
            ta.reg_labiviijaks = True
            ta.on_arvuti_reg = False
            ta.protok_ryhma_suurus = 10
            ta.jatk_voimalik = True
            ta.tagastuskoti_maht = 6
            ta.valjastuskoti_maht = 7
            ta.vaatleja_tasu = 2.55
            ta.vaatleja_lisatasu = 3.19
            ta.komisjoniliige_tasu = 4.29
            ta.esimees_tasu = 11.97
            ta.admin_tasu = 8.87
            ta.ruumide_jaotus = True
            ta.labiviijate_jaotus = True
            ta.kohad_avalikud = True
        model.Session.flush()
        return tk
    
    def _create_sooritajad(self, test, tk):
        assert tk and tk.id, 'Testimiskord puudub'
        for ik in opilased_ik:
            print('sooritaja %s' % ik)
            k = model.Kasutaja.get_by_ik(ik)
            added, sooritaja = model.Sooritaja.registreeri(k,
                                                           test.id,
                                                           tk,
                                                           const.LANG_ET,
                                                           None,
                                                           const.REGVIIS_SOORITAJA,
                                                           k.id,
                                                           None)
            sooritaja.kinnita_reg()
        model.Session.flush()

    def _create_testikohad(self, test, tk):
        assert tk and tk.id, 'Testimiskord puudub'
        koht = model.Koht.get(kool_koht_id)
        for ta in tk.toimumisajad:
            tkoht = model.Testikoht.give_testikoht(koht.id,
                                                   ta.testiosa_id,
                                                   ta.id)
            tkoht.gen_tahis()
            tkoht.set_tahised()
            ta.testikohad.append(tkoht)
            pakett = tkoht.give_testipakett(const.LANG_ET)
            truum = tkoht.give_testiruum()
            for tpaev in ta.toimumispaevad:
                truum.toimumispaev = tpaev
                break
            cnt = 0
            for sooritus in ta.sooritused:
                sooritus.suuna(tkoht, truum)
                cnt += 1
            print('Lisatud testikoht, suunatud %s sooritajat' % (cnt))
        model.Session.flush()

    def _create_labiviijad(self, test, tk):
        kasutajad_id = list()
        for ta in tk.toimumisajad:
            for tkoht in ta.testikohad:
                for truum in tkoht.testiruumid:
                    truum.give_labiviijad(tkoht)
                    grupp_id = const.GRUPP_T_ADMIN
                    lv = truum.give_labiviija(grupp_id, True)
                    #print 'truum %s... lv %s...' % (truum, lv)
                    kasutaja_id = None
                    for unused, q in ((True, tkoht.get_valik_q(grupp_id, on_piirkond=True)),
                                      (True, tkoht.get_valik_q(grupp_id, on_piirkond=False)),
                                      (False, tkoht.get_valik_q(grupp_id, on_piirkond=False))):
                        for k in q.all():
                            if unused and k.id in kasutajad_id:
                                continue
                            else:
                                kasutajad_id.append(k.id)
                                kasutaja_id = k.id
                                print('testi admin: %s %s' % (k.isikukood, k.nimi))
                                break

                        if kasutaja_id:
                            lv.set_kasutaja(kasutaja_id)
                            break
        print('määratud kasutajad %s' % kasutajad_id)
        model.Session.flush()

    def _create_hindajad(self, test, tk):
        lang = test.lang
        for ta in tk.toimumisajad:
            kasutajad_id = list()
            grupp_id = const.GRUPP_HINDAJA_K
            q = ta.get_valik_q(grupp_id, lang=lang)
            kasutaja = q.first()
            for lang in tk.keeled:
                for hk in ta.testiosa.hindamiskogumid:
                    if not hk.arvutihinnatav:
                        if not hk.kahekordne_hindamine:
                            lv = model.Labiviija(toimumisaeg=ta,
                                                 hindamiskogum=hk,
                                                 lang=lang,
                                                 liik=const.HINDAJA1,
                                                 on_paaris=False,
                                                 kasutajagrupp_id=grupp_id)
                            if kasutaja:
                                lv.set_kasutaja(kasutaja.id)
            if kasutaja:
                print('määratud hindaja %s' % kasutaja.isikukood)
        model.Session.flush()

    def _valjasta(self, test, tk):
        handler = None
        for ta in tk.toimumisajad:
            sailitakoodid = True
            err = valjastus.create_kogused(handler, ta, sailitakoodid)
            if not err:
                err = valjastus.create_hindamisprotokollid(handler, ta)
                #if not err:
                #    err = valjastus.create_ymbrikud(handler, ta)
            if err:
                raise Exception(err)

            # lubame alustada
            for sooritus in ta.sooritused:
                sooritus.staatus = const.S_STAATUS_ALUSTAMATA
                sooritus.sooritaja.update_staatus()
