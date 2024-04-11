# Avalikus vaates saab avaldatud testimiskord peab olema Innove vaate statistikas kasutusel.
# Kui testimiskord ei ole Innove vaates kasutusel, ei saa see olla avalikus vaates avaldatud.
# Testi Innove vaate statistikas kasutatud testimiskordade valiku muutmisel kustutatakse
# kõik antud testis varem genereeritud raportid.
# Testi avalikus vaates avaldatud testimiskordade valiku muutmisel kustutatakse
# antud testis seni avaldatud raportid, kuna need ei vasta enam avaldatud testimiskordade valikule.
# Genereeritud raporteid saab avalikus vaates avaldada siis, kui kõik Innove vaate statistikas kasutusel olevad
# testimiskorrad on ka avalikus vaates avaldatud, sest vastasel juhul ei vasta raport avaldatud testimiskordade valikule
# (kuna raportid genereeritakse Innove vaates kasutatavate testimiskordade põhjal).

from eis.lib.baseresource import *
from eis.lib.feedbackreport import FeedbackReport, report2pdf
from eis.lib.pdf.eksamistatistika import EksamistatistikaDoc
from eis.handlers.avalik.eksamistatistika.eksamistatistika import Query
_ = i18n._
log = logging.getLogger(__name__)

class StatistikaraportidController(BaseResourceController):
    """Statistikaraportite avaldamine
    """
    _permission = 'statistikaraportid'
    _MODEL = model.Testimiskord
    _INDEX_TEMPLATE = 'ekk/muud/statistikaraportid.mako'
    _LIST_TEMPLATE = 'ekk/muud/statistikaraportid_list.mako'
    _DEFAULT_SORT = '-test.id' # vaikimisi sortimine
    _EDIT_TEMPLATE = 'ekk/muud/statistikaraport.avaldamine.mako'

    _index_after_create = True
    
    def _search_default(self, q):
        return self._search(q)

    def _search(self, q1):
        if self.c.sessioon_id:
            self._get_protsessid()
        
        testiliigid = (const.TESTILIIK_RIIGIEKSAM,
                       const.TESTILIIK_RV,
                       const.TESTILIIK_POHIKOOL,
                       const.TESTILIIK_TASEMETOO)
        q = (model.SessionR.query(model.Test, model.Testimiskord.aasta)
             .distinct()
             .filter(model.Test.testityyp==const.TESTITYYP_EKK)
             .join(model.Test.testimiskorrad)
             .filter(model.Test.testiliik_kood.in_(testiliigid))
             .filter(model.Testimiskord.aasta>=2014)
             .filter(model.Testimiskord.tulemus_kinnitatud==True)
             .filter(model.Testimiskord.koondtulemus_avaldet==True)
             )

        self.c.opt_sessioon = self.c.opt.testsessioon
        if not self.c.sessioon_id and len(self.c.opt_sessioon):
            self.c.sessioon_id = self.c.opt_sessioon[0][0]

        if self.c.sessioon_id:
            q = q.filter(model.Testimiskord.testsessioon_id==int(self.c.sessioon_id))
        else:
            q = None
        return q

    def _split_item_id(self, item_id):
        li = item_id.split('-', 2)
        test_id = int(li[0])
        aasta = int(li[1])
        kursus = li[2] or None
        return test_id, aasta, kursus
    
    def _get_korrad(self, korrad_id):
        li = []
        for kord_id in korrad_id:
            kord = model.Testimiskord.get(kord_id)
            li.append(kord)
        return li

    def _new_d(self):
        """Avaldamise muudatuste vormi avamine"""
        korrad_id = list(map(int, self.request.params.getall('kord_id')))
        self.c.korrad = self._get_korrad(korrad_id)
        self.c.list_url = self.request.params.get('list_url')
        self.c.statistika_avaldet = all([k.statistika_aval_kpv != None for k in self.c.korrad])
        self.c.statistika_ekk = all([k.statistika_ekk_kpv != None for k in self.c.korrad])                
        return self.render_to_response(self._EDIT_TEMPLATE)

    def _create(self):
        if self.request.params.get('avaldamine'):
            return self._create_avaldamine()
        elif self.request.params.get('raport'):
            return self._create_raport()        

    def _create_avaldamine(self):
        """Avaldamise muudatuste vormil salvestamine"""

        ekk = self.request.params.get('statistika_ekk')
        avaldet = self.request.params.get('statistika_avaldet')

        if avaldet:
            # avalikus vaates avaldatu peab olema ka Innove vaates
            ekk = True
        if not ekk:
            # kui pole Innove vaates, ei saa olla ka avalikus vaates
            avaldet = False

        korrad_id = list(map(int, self.request.params.getall('kord_id')))
        korrad = self._get_korrad(korrad_id)
        for kord in korrad:
            if bool(kord.statistika_ekk_kpv) != bool(ekk):
                kord.statistika_ekk_kpv = ekk and date.today() or None
                # kustutame kõik raportid
                model.Statistikaraport.remove_raportid(kord.test_id, kord.aasta, None)

            if bool(kord.statistika_aval_kpv) != bool(avaldet):
                kord.statistika_aval_kpv = avaldet and date.today() or None
                # kustutame avalikud raportid
                model.Statistikaraport.remove_raportid(kord.test_id, kord.aasta, True)

        model.Session.commit()
        self.success()
        return self._after_update(None)

    def _create_raport(self):
        sessioon_id = self.request.params.get('sessioon_id')
        debug = self.request.params.get('debug')
        
        # märgime varasemad protsessid lõppenuks (katkestatuks),
        # mis paistavad pooleli olevat
        for rcd in self._query_protsessid(True):
            rcd.lopp = datetime.now()

        params = {'liik': model.Arvutusprotsess.LIIK_STATRAPORT,
                  'kirjeldus': _("Statistikaraporti genereerimine"),
                  'testsessioon_id': sessioon_id,
                  }
        resp = model.Arvutusprotsess.start(self, params, self._gen_raportid)
        if debug:
            return resp
        self.success(_("Raportite genereerimine käivitatud"))
        return self._after_update(None)
    
    def _gen_raportid(self, protsess):
        debug = self.request.params.get('debug')
        items_id = self.request.params.getall('item_id')
        total = len(items_id)
        for ind, item_id in enumerate(items_id):
            
            test_id, aasta, kursus = self._split_item_id(item_id)
            test = model.Test.get(test_id)
            if test:
                # leiame kõik raportifailid
                old_raportid = model.Statistikaraport.get_raportid(test.id, kursus, aasta)
                # loome/asendame vajalikud raportifailid
                raportid = save_statistikaraport(self, test, kursus, aasta, debug)
                # leiame vajalike failide id-le listi
                new_raportid_id = [r.id for r in raportid]
                # kustutame vanad failid, mida ei olnud enam vaja
                for r in old_raportid:
                    if r.id not in new_raportid_id:
                        r.delete()
                if debug:
                    for r in raportid:
                        return r
                if not raportid:
                    raise Exception("Faili genereerimine ebaõnnestus")
            if protsess:
                protsess.edenemisprotsent = (ind + 1) * 100 / total
            model.Session.commit()
            if protsess and protsess.lopp:
                raise ProcessCanceled()
            
    def _update_avalda(self, item_id):
        test_id, aasta, kursus = self._split_item_id(item_id)
        test = model.Test.get(test_id)
        if test:
            for r in model.Statistikaraport.get_raportid(test_id, kursus, aasta):
                r.avalik = True
            model.Session.commit()
            self.success(_("Raport avaldatud"))

        return self._after_update(item_id)
        
    def _after_update(self, id):
        """Peale salvestamist tuuakse ette otsingu sama lehekülg, mis enne oli.
        """
        kw = {}
        list_url = self.request.params.get('list_url')
        if list_url:
            t = self.h.update_params(list_url, _debug=True, **kw)
            kw = t[1]

        kw['kord_id'] = self.request.params.getall('kord_id')
        kw['item_id'] = self.request.params.getall('item_id')        
        return self._redirect('index', **kw)   

    def _search_protsessid(self, q):
        sessioon_id = self.c.sessioon_id or self.request.params.get('sessioon_id')
        q = (q.filter(model.Arvutusprotsess.liik==model.Arvutusprotsess.LIIK_STATRAPORT)
             .filter(model.Arvutusprotsess.testsessioon_id==sessioon_id)
             )
        return q

    def _paginate_protsessid(self, q):
        return q.all()

def save_statistikaraport(handler, test, kursus, aasta, debug=False):
    raportid = []
    filedata = None
    if test.testiliik_kood == const.TESTILIIK_TASEMETOO and aasta > 2019:
        # kasutame tagasisidevormi
        fr = FeedbackReport.init_riiklik(handler, test, const.LANG_ET, kursus)
        q = (model.SessionR.query(model.Testimiskord.id)
             .filter(model.Testimiskord.test_id==test.id)
             .filter(model.Testimiskord.aasta==aasta)
             .filter(model.Testimiskord.tulemus_kinnitatud==True)
             .filter(model.Testimiskord.koondtulemus_avaldet==True)
             .filter(model.Testimiskord.statistika_ekk_kpv!=None)
             )
        testimiskorrad_id = [tk_id for tk_id, in q.all()]
        if fr and testimiskorrad_id:
            # genereerime HTML
            err, data_html = fr.generate(None, testimiskorrad_id=testimiskorrad_id)
            if err:
                handler.error(err)
            else:
                # salvestame HTML raporti
                filename = 'raport%s%s_%s.html' % (test.id, kursus or '', aasta)
                raport = model.Statistikaraport.give_raport(test.id, kursus, aasta, 'html')
                raport.filename = filename
                raport.filedata = data_html.encode('utf-8')
                raport.avalik = False
                raportid.append(raport)
                
            # genereerime PDF
            filedata = fr.generate_pdf(None, testimiskorrad_id=testimiskorrad_id)
    else:
        # kasutame statistikaraportide PDF-malle
        qry = Query(handler, aasta, test.id, kursus, test.max_pallid, avalik=False)
        qry.hinnatud = True
        if test.testiliik_kood in (const.TESTILIIK_RIIGIEKSAM, const.TESTILIIK_RV):
            # riigieksamite korral on raportis ainult stats ja mittestats õppurid,
            # kes õpivad põhikoolis või gümnaasiumis
            qry.oppevormid = (const.OPPEVORM_STATS, const.OPPEVORM_MITTESTATS)
            qry.koolityyp = const.KOOLITYYP_POHIKOOL
        doc = EksamistatistikaDoc(test, qry)
        filedata = doc.generate()
    if filedata:
        if debug:
            return utils.download(filedata, filename)
        filename = 'raport%s%s_%s.pdf' % (test.id, kursus or '', aasta)
        raport = model.Statistikaraport.give_raport(test.id, kursus, aasta, 'pdf')        
        raport.filename = filename
        raport.filedata = filedata
        raport.avalik = False
        raportid.append(raport)
    return raportid
    

