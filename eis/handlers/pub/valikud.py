from eis.lib.base import *
_ = i18n._

log = logging.getLogger(__name__)

class ValikudController(BaseController):
    """Select-väljade täitmine klassifikaatoritega,
    mis sõltuvad mingi teise klassifikaatori valikust.
    """
    _authorize = False

    @action(renderer='json')
    def index(self):
        params = self.request.params
        li = []
        kood = self.request.matchdict.get('kood')
        
        byid = params.get('byid')
        ylem_id = params.get('ylem_id')
        if ylem_id:
            ylem_id = int(ylem_id)

        if kood == 'PIIRKONNAKOHT':
            prk = model.Piirkond.get(ylem_id)
            li = prk.get_opt_kohad()

        elif kood == 'PIIRKONNATESTIKOHT':
            ta_id = params.get('ta_id')
            ta = model.Toimumisaeg.get(ta_id)
            li = ta.get_testikohad_opt(ylem_id)            

        elif kood == 'PIIRKOND':
            filtered = params.get('filtered')
            if filtered:
                filtered = list(map(int, filtered.split(',')))
            li = model.Piirkond.get_opt_prk(ylem_id, filtered=filtered)

        elif kood == 'ADRKOMP':
            ylem_tasekood = params.get('ylem_tasekood')
            li = model.Aadresskomponent.get_opt(ylem_tasekood)

        elif kood == 'AADRESS':
            text = params.get('q')
            res = model.Aadress.get_select2_opt(text)
            return res
        
        elif kood == 'KOHT':
            ylem_tasekood = params.get('ylem_tasekood')
            if ylem_tasekood:
                komp = model.Aadresskomponent.get_by_tasekood(ylem_tasekood)
                if komp:
                    li = komp.get_koht_opt()
            else:
                li = model.Koht.get_opt()

        elif kood == 'SOORITUSKOHT':
            ylem_tasekood = params.get('ylem_tasekood')
            if ylem_tasekood:
                komp = model.Aadresskomponent.get_by_tasekood(ylem_tasekood)
                if komp:
                    li = komp.get_soorituskoht_opt()
            else:
                tasekood = params.get('tasekood')
                piirkond_id = params.get('piirkond_id')
                term = params.get('term')
                li = model.Koht.get_opt(on_soorituskoht=True,
                                        tasekood=tasekood,
                                        piirkond_id=piirkond_id,
                                        nimi=term)

        elif kood == 'PLANGIKOHT':
            ylem_tasekood = params.get('ylem_tasekood')
            if ylem_tasekood:
                komp = model.Aadresskomponent.get_by_tasekood(ylem_tasekood)
                if komp:
                    li = komp.get_plangikoht_opt()
            else:
                li = model.Koht.get_plangikoht_opt()
          
        elif kood == 'TOIMUMISAEG':
            testsessioon_id = params.get('sessioon_id')
            testsessioonid_id = [r for r in params.getall('sessioon_id[]') if r]
            if testsessioonid_id:
                testsessioonid_id = list(map(int, testsessioonid_id))
                if len(testsessioonid_id) == 1:
                    testsessioon_id = testsessioonid_id[0]
                    testsessioonid_id = None

            testiliik = params.get('testiliik')
            testiliigid = [r for r in params.getall('testiliik[]') if r]

            test_id = params.get('test_id')
            testimiskord_id = params.get('testimiskord_id')
            keeletase = params.get('keeletase')
            li = model.Toimumisaeg.get_opt(testsessioon_id, 
                                           test_id=test_id,
                                           testimiskord_id=testimiskord_id,
                                           keeletase=keeletase,
                                           testiliik_kood=testiliik,
                                           testiliigid_kood=testiliigid,
                                           testsessioonid_id=testsessioonid_id,
                                           vastvorm_kood=params.get('vastvorm'))                

        elif kood == 'TESTIMISKORD':
            li = model.Testimiskord.get_opt(testsessioon_id=params.get('sessioon_id'), 
                                            testiliik_kood=params.get('testiliik'),
                                            test_id=params.get('test_id'),
                                            testityyp=params.get('testityyp'))                
            
        elif kood == 'TEST':
            testsessioon_id = params.get('sessioon_id')
            testsessioonid_id = [r for r in params.getall('sessioon_id[]') if r]
            if testsessioonid_id:
                testsessioonid_id = list(map(int, testsessioonid_id))
                if len(testsessioonid_id) == 1:
                    testsessioon_id = testsessioonid_id[0]
                    testsessioonid_id = None

            testiliik = params.get('testiliik')
            testiliigid = [r for r in params.getall('testiliik[]') if r]
            li = model.Test.get_opt(testsessioon_id=testsessioon_id,
                                    testsessioonid_id=testsessioonid_id,
                                    testiliik_kood=testiliik,
                                    testiliigid_kood=testiliigid,
                                    test_id=params.get('test_id'),
                                    keeletase=params.get('keeletase'),
                                    testityyp=params.get('testityyp'),
                                    vastvorm=params.get('vastvorm'),
                                    disp_test_id=params.get('disp_test_id'))
        elif kood == 'SESSIOON':
            testiliik = params.get('testiliik') or [r for r in params.getall('testiliik[]') if r]
            li = model.Testsessioon.get_opt(testiliik_kood=testiliik)
            
        elif kood == 'RVEKSAM':
            aine_kood = params.get('aine_kood')
            li = self.c.opt.rveksamid(aine_kood)

        elif kood == 'ASTE':
            #aine = params.get('ylem_kood')
            #li = self.c.opt.astmed(aine)
            li = self.c.opt.astmed()

        elif kood == 'TEEMA2':
            aine = params.get('aine')
            aste = params.get('aste')
            data = self.c.opt.teemad2(aine, aste)
            return data
        elif kood == 'OPITULEMUS2':
            aine = params.get('aine')
            data = self.c.opt.opitulemused(aine, True)
            return data
        elif kood == 'OPITULEMUS':
            aine = params.get('aine')
            li = self.c.opt.opitulemused(aine, False)
        elif kood == 'YLKOGU':
            # ylesandekogude loetelu
            aine = params.get('aine')
            li = self.c.opt.ylkogud(aine)
        elif kood == 'YLKOGUya':
            # ylesandekogude loetelu, milles on avalikke ylesandeid või teste
            aine = params.get('aine')
            li = self.c.opt.ylkogud(aine, avalik_y=True)
        elif kood == 'YLKOGUyp':
            # ylesandekogude loetelu, milles on avalikke või pedagoogile lubatud ylesandeid või teste
            aine = params.get('aine')
            li = self.c.opt.ylkogud(aine, avalik_y=True, pedagoog=True)            
        else:
            # klassifikaatorid
            ylem_kood = params.get('ylem_kood')
            bit = None
            if kood in (const.KL_TEEMA, const.KL_ALATEEMA):
                if kood == const.KL_TEEMA:
                    aine = ylem_kood
                else:
                    aine = params.get('aine_kood')
                astmed = params.get('aste')
                if astmed:
                    bit = 0
                    for aste in astmed.strip(',').split(','):
                        bit += self.c.opt.aste_bit(aste, aine) or 0

            # kui empty oleks True, siis tekiks --Vali-- ridu mitu tükki
            if byid:
                li = self.c.opt.klread_id(kood, ylem_kood=ylem_kood, ylem_id=ylem_id, bit=bit, empty=False)
            else:
                li = self.c.opt.klread_kood(kood, ylem_kood=ylem_kood, ylem_id=ylem_id, bit=bit, empty=False)

        data = [{'id':a[0],'value':a[1], 'name':len(a)>2 and a[2] or ''} for a in li]
        return data

    def kirjeldus(self):
        params = self.request.params
        klassifikaator_kood = self.request.matchdict.get('klassifikaator_kood')
        assert klassifikaator_kood == 'AINE.ASPEKT', 'vale klassifikaator'
        klassifikaator_kood = 'ASPEKT'
        pkood = params.get('kood')
        if pkood:
            ylem_kood, kood = pkood.split('.', 1)
            item = model.Klrida.get_by_kood(klassifikaator_kood, kood, ylem_kood=ylem_kood)
            buf = item and item.ctran.kirjeldus or ''
        else:
            buf = ''
        return Response(buf)
