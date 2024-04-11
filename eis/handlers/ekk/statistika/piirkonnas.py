from eis.lib.baseresource import *
from eis.lib.feedbackreport import FeedbackReport
_ = i18n._
log = logging.getLogger(__name__)

class Query(object):
    "Päringu objekt, vastab tulemuste loetelu yhele reale, sisaldab reale vastava grupi tingimusi"
    debug = False
    
    def __init__(self,
                 handler,
                 kool_id=None,
                 paralleel=None,
                 maakond_kood=None,
                 linn_kood=None,
                 lang=None,
                 sugu=None,
                 piirkond_id=None,
                 kursus=None):
        self.handler = handler
        c = handler.c
        self.test_id = c.test.id
        self.aine = c.test.aine_kood
        self.max_pallid = c.test.max_pallid
        self.testimiskord_id = c.testimiskord_id
        self.kool_id = kool_id
        self.kursus = kursus
        self.maakond_kood = maakond_kood
        self.linn_kood = linn_kood
        self.lang = lang
        self.sugu = sugu
        self.piirkond_id = piirkond_id
        self.ajakulu = c.ajakulu
        self.debug = False

    def query_cnt(self, valimid_tk_id=None):
        "Sooritajate arv ja keskmine tulemus"
        select_fields = [sa.func.count(model.Sooritaja.id),
                         sa.func.avg(model.Sooritaja.pallid),
                         sa.func.avg(model.Sooritaja.tulemus_protsent)
                         ]
        if self.ajakulu:
            select_fields.append(sa.func.avg(model.Sooritaja.ajakulu))
        else:
            # et oleks sama arv tulemuses
            select_fields.append(sa.func.count(model.Sooritaja.id))

        q = self._gen_query(select_fields, valimid_tk_id=valimid_tk_id)
        if self.debug:
            model.log_query(q)
        cnt, avg_p, avg_pr, ajakulu = q.first()
        try:
            # arvutame keskmise protsendi pallide järgi,
            # kuna andmebaasi protsendiveerg võib olla ümardatud
            avg_pr = avg_p * 100. / self.max_pallid
        except:
            pass
        return cnt, avg_p, avg_pr, ajakulu

    def query_max(self, protsent, total):
        "Vähemalt etteantud protsendi saanute arv"
        diff = 1e-12
        select_fields = [sa.func.count(model.Sooritaja.id)]
        q = (self._gen_query(select_fields)
             .filter(model.Sooritaja.tulemus_protsent > protsent - diff)
             )
        cnt = q.scalar()
        cntpr = None
        if cnt is not None and total:
            cntpr = cnt * 100./total        
        return cnt, cntpr

    def query_min(self, protsent, total):
        "Kuni etteantud protsendi saanute arv"
        diff = 1e-12
        select_fields = [sa.func.count(model.Sooritaja.id)]
        q = (self._gen_query(select_fields)
             .filter(model.Sooritaja.tulemus_protsent < protsent + diff)
             )
        cnt = q.scalar()
        cntpr = None
        if cnt is not None and total:
            cntpr = cnt * 100./total        
        return cnt, cntpr

    def query_max_pall(self, protsent):
        "Vähemalt etteantud arvu punkti saanute arv"
        diff = 1e-12
        select_fields = [sa.func.count(model.Sooritaja.id)]
        q = (self._gen_query(select_fields)
             .filter(model.Sooritaja.pallid > self.max_pallid * protsent/100. - diff)
             )
        #model.log_query(q)
        return q.scalar()
            
    def query_min_pall(self):
        "Min punktide saajate arv"
        diff = 1e-12
        select_fields = [sa.func.count(model.Sooritaja.id)]        
        q = (self._gen_query(select_fields)
             .filter(model.Sooritaja.pallid < diff)
             )
        return q.scalar()       

    def query_mediaan(self):
        "Tulemuse mediaan"
        # alates PostgreSQL v9.4 on olemas percentile_cont()
        select_fields = [model.Sooritaja.pallid]        
        q = self._gen_query(select_fields)
        sql = "WITH t(value) AS (" + model.str_query(q) + ") SELECT percentile_cont(0.5) WITHIN GROUP (ORDER BY value) FROM t"
        #log.info(sql)
        qm = model.SessionR.execute(sa.text(sql))
        return qm.scalar()
        
    def list_kool(self):
        groups = [sa.distinct(model.Sooritaja.kool_koht_id)]
        q = self._gen_query(groups, filter_groups=False)
        koolid_id = [r for r, in q.all() if r]
        #model.log_query(q)
        if koolid_id:
            q = (model.SessionR.query(model.Koht.id, model.Koht.nimi)
                 .filter(model.Koht.id.in_(koolid_id))
                 .order_by(model.Koht.nimi))
            return q.all()
        else:
            return []
    
    def list_maakond(self):
        groups = [sa.distinct(model.Aadress.kood1)]
        q = self._gen_query(groups, filter_groups=False)
        q = (q.join(model.Sooritaja.kool_koht)
             .join(model.Koht.aadress))
        koodid = [r for r, in q.all() if r]
        if koodid:
            q = (model.SessionR.query(model.Aadresskomponent.kood,
                                     model.Aadresskomponent.nimetus_liigiga)
                 .filter(model.Aadresskomponent.tase==1)
                 .filter(model.Aadresskomponent.kood.in_(koodid))
                 .order_by(model.Aadresskomponent.nimetus_liigiga))
            return q.all()
        else:
            return []

    def list_piirkond(self):
        groups = [sa.distinct(model.Koht.piirkond_id)]
        q = self._gen_query(groups, filter_groups=False)
        q = q.join(model.Sooritaja.kool_koht)
        piirkonnad_id = [r for r, in q.all() if r]
        #model.log_query(q)
        #log.info('PIIRKONNAD: %s' % piirkonnad_id)
        if piirkonnad_id:
            q = (model.SessionR.query(model.Piirkond.id, model.Piirkond.nimi)
                 .filter(model.Piirkond.id.in_(piirkonnad_id))
                 .order_by(model.Piirkond.nimi))
            return q.all()
        else:
            return []
        
    def _gen_query(self, select_fields, filter_groups=True, valimid_tk_id=None):
        c = self.handler.c
        q = (model.SessionR.query(*select_fields)
             .filter(sa.and_(model.Sooritaja.staatus==const.S_STAATUS_TEHTUD,
                             model.Sooritaja.hindamine_staatus==const.H_STAATUS_HINNATUD,
                             model.Sooritaja.test_id==self.test_id))
             )
        if self.maakond_kood:
            q = (q.join(model.Sooritaja.kool_koht)
                 .join(model.Koht.aadress)
                 .filter(model.Aadress.kood1==self.maakond_kood))
        elif self.linn_kood:
            q = (q.join(model.Sooritaja.kool_koht)
                 .join(model.Koht.aadress)
                 .filter(model.Aadress.kood2==self.linn_kood))
        elif self.piirkond_id:
            q = (q.join(model.Sooritaja.kool_koht)
                 .filter(model.Koht.piirkond_id==self.piirkond_id))
        if self.kursus:
            q = q.filter(model.Sooritaja.kursus_kood==self.kursus)
        if c.sugu:
            q = q.join(model.Sooritaja.kasutaja)
        if filter_groups:
            if c.lang:
                q = q.filter(model.Sooritaja.lang==self.lang)
            if c.sugu:
                q = q.filter(model.Kasutaja.sugu==self.sugu)
        if valimid_tk_id and len(valimid_tk_id) == 1:
            q = (q.filter(model.Sooritaja.testimiskord_id==valimid_tk_id[0])
                 .filter(model.Sooritaja.valimis==True))
        elif valimid_tk_id:
            q = (q.filter(model.Sooritaja.testimiskord_id.in_(valimid_tk_id))
                 .filter(model.Sooritaja.valimis==True))
        else:
            q = q.filter(model.Sooritaja.testimiskord_id==self.testimiskord_id)
        return q

    def get_rows_grouped(self):
        # leiame grupid (keele ja soo kaupa)
        groups = []
        orders = []
        c = self.handler.c
        if c.lang:
            groups.append(model.Sooritaja.lang)
            #orders.append('lang_sort(sooritaja.lang)')
            orders.append('sooritaja.lang')
        if c.sugu:
            groups.append(model.Kasutaja.sugu)
            orders.append('kasutaja.sugu desc')
        if groups:
            groups[0] = sa.distinct(groups[0])
            q = (self._gen_query(groups, filter_groups=False)
                 .order_by(sa.text(','.join(orders)))
                 )
            grupid = list(q.all())
            if c.lang:
                langorder = ['et','ru','en','de','fr']
                grupid = sorted(grupid, key=lambda row: row[0] in langorder and langorder.index(row[0]) or 9)
        else:
            grupid = None

        # teema iga grupi kohta eraldi päringud ja saama eraldi rea tulemustesse
        rows = list()
        on_pdf = False
        for grupid1 in grupid or [None]:
            if grupid1 is not None:
                ind = 0
                if c.lang:
                    self.lang = grupid1[ind]
                    ind += 1
                if c.sugu:
                    self.sugu = grupid1[ind]
                    ind += 1
            rows.append((self._prepare_row(), '', ''))
        return rows

    def _prepare_row(self):
        c = self.handler.c
        h = self.handler.h
        total, pallid, protsent, ajakulu = self.query_cnt()
        max_pallid = c.test.max_pallid
        row = []
        if c.lang:
            row.append(self.lang and model.Klrida.get_lang_nimi(self.lang).lower() or '')
        if c.sugu:
            row.append(self.sugu)
        if c.cnt:
            row.append(h.fstr(total, 1))
        if c.ajakulu != '':
            row.append(h.str_from_time(ajakulu))
        if c.avg_pt != '':
            row.append(h.fstr(pallid,1))
        if c.avg_pr != '':
            row.append(h.fstr(protsent,1))

        if self.handler.valimid_tk_id:
            v_cnt, v_pallid, v_protsent, v_ajakulu = self.query_cnt(valimid_tk_id=c.valimid_tk_id)
            if c.avg_pt:
                row.append(h.fstr(v_pallid, 1))
            if c.avg_pr:
                row.append(h.fstr(v_protsent, 1))
        if c.mediaan:
            row.append(h.fstr(self.query_mediaan(), 1))
        if c.min:
            row.append(h.fstr(self.query_min_pall(), 1))            
        if c.max:
            row.append(h.fstr(self.query_max_pall(100), 1))

        if c.edukus_pt or c.edukus_pr:
            edukus, edukus_pr = self.query_max(49.95, total)
            if c.edukus_pt != '':
                row.append(h.fstr(edukus, 1))
            if c.edukus_pr != '':
                row.append(h.fstr(edukus_pr, 1))

        if c.kvaliteet_pt or c.kvaliteet_pr:
            kvaliteet, kvaliteet_pr = self.query_max(74.95, total)
            if c.kvaliteet_pt != '':
                row.append(h.fstr(kvaliteet, 1))
            if c.kvaliteet_pr != '':
                row.append(h.fstr(kvaliteet_pr, 1))

        if c.alla20 or c.alla20pr:
            if not c.alla and c.alla != 0:
                c.alla = 20
            allap, allapr = self.query_min(c.alla, total)
            if c.alla20:
                row.append(allap)
            if c.alla20pr:
                row.append(h.fstr(allapr,1))

        if c.yle80 or c.yle80pr:
            if not c.yle and c.yle != 0:
                c.yle = 80
            ylep, ylepr = self.query_max(c.yle, total)
            if c.yle80:
                row.append(ylep)
            if c.yle80pr:
                row.append(h.fstr(ylepr,1))
        return row
        

class PiirkonnasController(BaseResourceController):
    "Piirkonna tulemused"
    _permission = 'korraldamine'
    _INDEX_TEMPLATE = 'ekk/statistika/piirkonnas.mako'
    _LIST_TEMPLATE = 'ekk/statistika/piirkonnas_list.tbody.mako'
    _SEARCH_FORM = forms.ekk.otsingud.PiirkonnatulemusedForm
    _actions = 'show'
    _DEFAULT_SORT = ''
    _ignore_default_params = ['csv', 'pdf', 'fpdf']

    def show(self):
        return self.index()

    def _query(self):
        return True

    def _search_default(self, q):
        c = self.c
        c.cnt = 1
        c.avg_pt = 1
        c.avg_pr = 1
        c.alla = 20
        c.yle = 80
        return self._search(q)

    def _prepare_header(self):
        c = self.c
        c.mitu_testiosa = len(c.test.testiosad) > 1
        header = ['']

        if c.lang:
            header.append(_("Keel"))
        if c.sugu:
            header.append(_("Sugu"))
        if c.cnt:
            header.append(_("Sooritajate arv"))
        if c.ajakulu:
            if c.mitu_testiosa:
                #self.error(_("Kasutatud aja filtrit ei saa mitme testiosaga testi korral kasutada"))
                c.ajakulu = ''
            else:
                header.append(_("Kasutatud aeg"))
        if c.avg_pt:
            header.append(_("Keskmine (punktid)"))
        if c.avg_pr:
            header.append(_("Keskmine (%)"))
        if self.valimid_tk_id:
            if c.avg_pt:
                header.append(_("Valimi keskmine (punktid)"))
            if c.avg_pr:
                header.append(_("Valimi keskmine (%)"))
        if c.mediaan:
            header.append(_("Mediaan"))
        if c.min:
            header.append(_("Min punktide saajad"))
        if c.max:
            header.append(_("Max punktide saajad"))
        if c.edukus_pt:
            header.append(_("Edukus"))
        if c.edukus_pr:
            header.append(_("Edukuse %"))
        if c.kvaliteet_pt:
            header.append(_("Kvaliteet"))
        if c.kvaliteet_pr:
            header.append(_("Kvaliteedi %"))
        if not c.alla and c.alla != 0:
            c.alla = 20
        if not c.yle and c.yle != 0:
            c.yle = 80
        if c.alla20:
            header.append(_("Kuni {p}% pallidest").format(p=c.alla))
        if c.alla20pr:
            header.append(_("Kuni {p}% pallidest (%)").format(p=c.alla))
        if c.yle80:
            header.append(_("Vähemalt {p}% pallidest").format(p=c.yle))
        if c.yle80pr:
            header.append(_("Vähemalt {p}% pallidest (%)").format(p=c.yle))

        return header
    
    def _search(self, q):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        c = self.c
        if not c.user.koht_id:
            return

        sis_valim_tk_id, valimid_tk_id, v_avaldet = \
            FeedbackReport.leia_valimi_testimiskord(c.test.id, c.testimiskord_id)        
        self.valimid_tk_id = sis_valim_tk_id and [c.testimiskord_id] or valimid_tk_id
        
        c.items1 = []
        c.items2 = []        
        c.items3 = []

        if c.piirkond_id:
            # kasutaja klikkis piirkonnal, kuvame piirkonnas olevate koolide tulemuste loetelu
            if None in self.lubatud_piirkonnad_id or int(c.piirkond_id) in self.lubatud_piirkonnad_id:
                # oma piirkonna koolide tulemused
                qry = Query(self,
                            piirkond_id=c.piirkond_id,
                            kursus=c.kursus)
                for kool_id, kool_nimi in qry.list_kool():
                    qry.kool_id = kool_id
                    c.items2.append((kool_nimi, 'kool', None, qry.get_rows_grouped()))
            return
        
        c.header = self._prepare_header()
        
        curr_params = self._get_curr_params()

        # piirkonnad
        qry = Query(self, kursus=c.kursus)
        for piirkond_id, piirkond_nimi in qry.list_piirkond():
            qry.piirkond_id = piirkond_id
            on_oma = None in self.lubatud_piirkonnad_id or piirkond_id in self.lubatud_piirkonnad_id
            if on_oma:
                k_url = self.url_current('show', piirkond_id=piirkond_id, partial=1, **curr_params)
            else:
                k_url = ''
            c.items1.append((piirkond_nimi, 'piirkond', k_url, qry.get_rows_grouped()))

            if on_oma and (self.c.csv or self.c.pdf):
                # CSV või PDF korral kuvame kohe koolide andmed ka
                qry2 = Query(self,
                            piirkond_id=piirkond_id)
                for kool_id, kool_nimi in qry2.list_kool():
                    qry2.kool_id = kool_id
                    c.items1.append((kool_nimi, 'kool', None, qry2.get_rows_grouped()))

                
        # Eesti keskmine
        # kui testil on valimi testimiskord (või -korrad), siis arvutatakse nende põhjal
        # kui ei ole valimi testimiskorda, siis arvutatakse üle Eesti 
        qry = Query(self, kursus=c.kursus)
        c.items1.append((_("Eesti keskmine"), 'valim', None, qry.get_rows_grouped()))

        if self.c.csv:
            return self._index_csv()
        elif self.c.pdf:
            return self._index_pdf()

    def _index_csv(self):
        c = self.c

        # tabeli sisu
        items = [c.header]
        for title, k_class, k_url, rows in c.items1 + c.items2 + c.items3:
            for row, d_url, d_title in rows:
                items.append([title] + row)
        buf = ''
        for r in items:
            buf += ';'.join([v is not None and str(v) or '' for v in r]) + '\n'

        buf = utils.encode_ansi(buf)
        response = Response(buf) 
        response.content_type = 'text/csv'
        response.content_disposition = 'attachment;filename=piirkonnatulemused.csv'
        return response

    def _get_curr_params(self):
        "Leiame kehtivad parameetrid (ei pruugi olla URLis sees, kui on vaikimisi eelmisest korrast)"
        params = {}
        keys = ('lang', 'sugu', 'cnt', 'ajakulu', 'avg_pt', 'avg_pr', 'mediaan', 'max', 'min', 'edukus_pt', 'edukus_pr', 'kvaliteet_pt', 'kvaliteet_pr','kursus')
        for key in keys:
            try:
                value = self.c.__getattribute__(key)
            except AttributeError:
                pass
            else:
                if value:
                    params[key] = value
        return params

    def _copy_search_params(self, form_data=None, save=False, upath=None):
        "Soovime, et piirkonna sisu näitamisel parameetreid ei salvestataks"
        if self.request.params.get('piirkond_id'):
            save = False
        return BaseResourceController._copy_search_params(self, form_data, save, upath)
        
    def __before__(self):
        test_id = self.request.matchdict.get('test_id')
        self.c.test = model.Test.get(test_id)
        self.c.testimiskord_id = self.request.matchdict.get('testimiskord_id')
        self.c.testimiskord = model.Testimiskord.get(self.c.testimiskord_id)
        self.c.kursus = self.request.matchdict.get('kursus')
        self.lubatud_piirkonnad_id = self.c.user.get_kasutaja().get_piirkonnad_id('korraldamine', const.BT_SHOW)
