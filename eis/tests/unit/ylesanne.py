# python setup.py test -s eis.tests.unit.ylesanne.Ylesanne

from datetime import date, timedelta
from eis.tests.basetest import *

class Ylesanne(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = main({}, **settings)

    def setUp(self):
        self.app = TestApp(self.app)
        self.config = testing.setUp()
        model.usersession.set_user(TestUser.get_testuser())
        
    def test_02_sp19(self):
        # avatud vastus
        y = model.Ylesanne(nimi='Avatud vastus',
                           staatus=const.Y_STAATUS_VALMIS,
                           max_pallid=1,
                           vastvorm_kood=const.VASTVORM_KE,
                           hindamine_kood=const.HINDAMINE_OBJ,
                           arvutihinnatav=True,
                           adaptiivne=False,
                           ptest=True,
                           etest=True,
                           lang=const.LANG_ET,
                           kasutusmaar=0,
                           ymardamine=False,
                           pallemaara=False,
                           skeeled='et')
        ya = model.Ylesandeaine(aine_kood='B',
                                ylesanne=y,
                                seq=0)

        #y.logging = False
        sp = model.Sisuplokk(ylesanne=y,
                             seq=1,
                             staatus=const.B_STAATUS_KEHTIV,
                             naide=False,
                             ymardamine=False,
                             tyyp=const.INTER_EXT_TEXT,
                             nimi='Kui palju on 2x3?')
        sp.logging = False
        kysimus = model.Kysimus(kood='K01',
                                seq=1,
                                segamini=False,
                                max_vastus=1,
                                sisuplokk=sp,
                                sonadearv=False,
                                pseudo=False)
        tulemus = model.Tulemus(kood=kysimus.kood,
                                baastyyp=const.BASETYPE_INTEGER,
                                kardinaalsus=const.CARDINALITY_SINGLE,
                                min_pallid=0,
                                vaikimisi_pallid=0,
                                ylesanne=y,
                                arvutihinnatav=True)
        kysimus.tulemus = tulemus
        hm = model.Hindamismaatriks(kood1='6',
                                    oige=True,
                                    pallid=1,
                                    maatriks=1,
                                    tulemus=tulemus)
        y.check(None)
        model.Session.commit()
        print('Loodud ülesanne %s' % y.id)

    def test_04_sp12(self):
        # valikvastusega kysimus
        y = model.Ylesanne(nimi='Valikvastus',
                           staatus=const.Y_STAATUS_VALMIS,
                           max_pallid=1,
                           vastvorm_kood=const.VASTVORM_KE,
                           hindamine_kood=const.HINDAMINE_OBJ,
                           arvutihinnatav=True,
                           adaptiivne=False,
                           ptest=True,
                           etest=True,
                           lang=const.LANG_ET,
                           kasutusmaar=0,
                           ymardamine=False,
                           pallemaara=False,
                           skeeled='et')
        ya = model.Ylesandeaine(aine_kood='B',
                                ylesanne=y,
                                seq=0)

        #y.logging = False
        sp = model.Sisuplokk(ylesanne=y,
                             seq=1,
                             staatus=const.B_STAATUS_KEHTIV,
                             naide=False,
                             ymardamine=False,
                             tyyp=const.INTER_CHOICE,
                             nimi='Kui palju on 2+3?')
        sp.logging = False
        kysimus = model.Kysimus(kood='K1',
                                seq=1,
                                segamini=False,
                                max_vastus=1,
                                sisuplokk=sp,
                                sonadearv=False,
                                pseudo=False)
        for seq, row in enumerate((('A', 'neli'), ('B','viis'), ('C', 'kuus'))):
            v = model.Valik(seq=seq+1,
                            kood=row[0],
                            nimi=row[1],
                            kysimus=kysimus)

        tulemus = model.Tulemus(kood=kysimus.kood,
                                baastyyp=const.BASETYPE_IDENTIFIER,
                                kardinaalsus=const.CARDINALITY_MULTIPLE,
                                min_pallid=0,
                                vaikimisi_pallid=0,
                                ylesanne=y,
                                arvutihinnatav=True)
        kysimus.tulemus = tulemus
        hm = model.Hindamismaatriks(kood1='B',
                                    oige=True,
                                    pallid=1,
                                    maatriks=1,
                                    tulemus=tulemus)
        y.check(None)
        model.Session.commit()
        print('Loodud ülesanne %s' % y.id)
