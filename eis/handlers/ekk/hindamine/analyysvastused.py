from io import StringIO
from html.parser import HTMLParser

from eis.lib.baseresource import *
_ = i18n._
from eis.lib.blockview import BlockView
from eis.lib.pdf.vastustestatistika import VastustestatistikaDoc

log = logging.getLogger(__name__)

class AnalyysvastusedController(BaseResourceController):
    _permission = 'vastusteanalyys'

    _MODEL = model.Valitudylesanne
    _INDEX_TEMPLATE = 'ekk/hindamine/analyys.vastused.mako'
    _no_paginate = True
    _ignore_default_params = ['csv_y', 'csv_k', 'csv_v', 'pdf', 'vy_id']

    @property
    def _EDIT_TEMPLATE(self):
        if self.request.params.get('partial'):
            return 'ekk/hindamine/analyys.vastus.mako'
        else:
            return 'ekk/hindamine/analyys.vastused.mako'

    def _query(self):
        q = model.SessionR.query(model.Ylesanne, 
                                model.Valitudylesanne,
                                model.Testiylesanne,
                                model.Ylesandestatistika)

        f_yst = sa.and_(model.Ylesandestatistika.testikoht_id==None,
                        model.Ylesandestatistika.kool_koht_id==None,
                        model.Ylesandestatistika.testiruum_id==None)
        komplektis = self.request.params.get('komplektis') == '1' and 1 or None
        if komplektis:
            f_yst = sa.and_(f_yst,
                            model.Ylesandestatistika.valitudylesanne_id==model.Valitudylesanne.id)
        else:
            f_yst = sa.and_(f_yst,
                            model.Ylesandestatistika.valitudylesanne_id==None,
                            model.Ylesandestatistika.ylesanne_id==model.Valitudylesanne.ylesanne_id)
        
        if self.c.testimiskord and self.c.testimiskord.analyys_eraldi:
            qta = (model.SessionR.query(model.Toimumisaeg.id)
                   .filter_by(testimiskord_id=self.c.testimiskord.id))
            toimumisajad_id = [ta_id for ta_id, in qta.all()]
            if len(toimumisajad_id) == 1:
                f_yst = sa.and_(f_yst, 
                                model.Ylesandestatistika.toimumisaeg_id==self.c.toimumisaeg.id)
            else:
                f_yst = sa.and_(f_yst, 
                                model.Ylesandestatistika.toimumisaeg_id.in_(toimumisajad_id))
        else:
            f_yst = sa.and_(f_yst,
                            model.Ylesandestatistika.toimumisaeg_id==None,
                            model.Ylesandestatistika.tkorraga==True)

        q = (q.join(model.Testiylesanne.valitudylesanded)
             .filter(model.Testiylesanne.liik.in_((const.TY_LIIK_Y, const.TY_LIIK_K)))
             .filter(model.Valitudylesanne.test_id==self.c.test.id)
             .join(model.Valitudylesanne.ylesanne)
             .outerjoin((model.Ylesandestatistika, f_yst))
             )

        return q
    
    def _search_default(self, q):
        # vaikimisi otsitakse jooksvast testiosast
        self.c.testiosa_id = self.c.toimumisaeg.testiosa_id
        return self._search(q)
        
    def _search(self, q):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        self._get_protsessid()    

        c = self.c
        c.komplektis = c.komplektis == '1' or c.komplektis == 1 or None
        if c.csv_v:
            testimiskord_id = c.testimiskord and c.testimiskord.id or None
            return self._download_vastused(c.test.id, c.testiosa_id, c.alatest_id, c.komplekt_id, testimiskord_id)
        if c.testiosa_id and c.toimumisaeg and int(c.testiosa_id) != c.toimumisaeg.testiosa_id:
            # kui valiti muu testiosa, siis suuname kasutaja selle toimumisajale
            q1 = (model.SessionR.query(model.Toimumisaeg.id)
                  .filter_by(testiosa_id=c.testiosa_id)
                  .filter_by(testimiskord_id=c.testimiskord.id))
            for ta_id, in q1.all():
                return self._redirect('index', toimumisaeg_id=ta_id, getargs=True)
        
        c.opt_testiosad = c.test.opt_testiosad
        if len(c.opt_testiosad) == 1:
            c.testiosa_id = c.opt_testiosad[0][0]
        if not c.testiosa_id:
            c.komplekt_id = c.komplektivalik = c.kursus = None
        else:
            testiosa = model.Testiosa.get(c.testiosa_id)
            if c.komplektivalik_id:
                c.komplektivalik = model.Komplektivalik.get(c.komplektivalik_id)

            c.opt_kv = testiosa.get_opt_komplektivalikud(kursus=c.kursus)
            valikud_id = [r[0] for r in c.opt_kv]
            if not c.komplektivalik or c.komplektivalik.id not in valikud_id:
                c.komplektivalik = None
                if len(valikud_id):
                    c.komplektivalik = model.Komplektivalik.get(valikud_id[0])

            if c.komplektivalik:
                c.kursus = c.komplektivalik.kursus_kood
                ta = c.testimiskord and c.testimiskord.get_toimumisaeg(testiosa) or None
                c.opt_komplekt = c.komplektivalik.get_opt_komplektid(ta)
            else:
                c.opt_komplekt = []
            if c.komplekt_id:
                komplekt = model.Komplekt.get(c.komplekt_id)
                if komplekt.komplektivalik != c.komplektivalik:
                    c.komplekt_id = None

            if c.komplekt_id and not c.pdf:
                # PDFis on kõik komplektid koos
                q = q.filter(model.Valitudylesanne.komplekt_id==int(c.komplekt_id))
            elif c.testiosa_id:
                q = q.filter(model.Testiylesanne.testiosa_id==c.testiosa_id)
            if c.alatest_id:
                q = q.filter(model.Testiylesanne.alatest_id==int(c.alatest_id))

            if (not c.komplekt_id or c.pdf) and c.testimiskord:
                # komplekt peab olema testimiskorral kasutusel
                qk = (model.SessionR.query(model.Toimumisaeg_komplekt.komplekt_id)
                      .join((model.Toimumisaeg,
                             model.Toimumisaeg.id==model.Toimumisaeg_komplekt.toimumisaeg_id))
                      .filter(model.Toimumisaeg.testimiskord_id==c.testimiskord.id)
                      )
                if c.testiosa_id:
                    qk = qk.filter(model.Toimumisaeg.testiosa_id==c.testiosa_id)
                tk_komplektid_id = [k_id for k_id, in qk.all()]
                q = q.filter(model.Valitudylesanne.komplekt_id.in_(tk_komplektid_id))
                        
        cnt_yst = q.filter(model.Ylesandestatistika.id!=None).count()
        if cnt_yst == 0:
            self.notice(_("Statistika arvutamata"))            

        self._get_data(q)

        if c.csv_y:
            return self._index_xls(q, 'ylesanded.xlsx')
        if c.csv_k:
            return self._index_xls(q, 'kysimused.xlsx')                
        if c.pdf:
            return self._index_pdf(q, 'statistika.pdf')

        c.header = self._prepare_header_y()
        c.prepare_item_y = self._prepare_item_y
        
        if c.vy_id and not isinstance(c.vy_id, list):
            # isinstance kontrollib, et ei tuldud loetelu lehelt
            # valitud ylesandega lehel muudeti nt ylesandekomplekti valikut või järjestust
            item = model.Valitudylesanne.get(c.vy_id)
            if not c.komplekt_id or int(c.komplekt_id) == item.komplekt_id:
                c.item = item
                self._edit(item)

    def _order(self, q):
        q = q.order_by(model.Testiylesanne.testiosa_id,
                       model.Valitudylesanne.komplekt_id,
                       model.Testiylesanne.alatest_seq,
                       model.Testiylesanne.seq,
                       model.Valitudylesanne.seq)
        return q

    def _get_data(self, q):
        # leiame andmed komplektide kaupa
        c = self.c
        q = self._order(q)
        c.osad = {}
        c.komplektid = {}
        c.data = {}
        for row in q.all():
            ylesanne, vy, ty, yst = row            
            komplekt_id = vy.komplekt_id
            osa_id = ty.testiosa_id
            if osa_id not in c.osad:
                osa = model.Testiosa.get(osa_id)
                c.osad[osa_id] = osa.tahis
            if komplekt_id not in c.komplektid:
                komplekt = model.Komplekt.get(komplekt_id)
                c.komplektid[komplekt_id] = komplekt.tahis
                c.data[komplekt_id] = [[], osa_id, komplekt_id]
            c.data[komplekt_id][0].append(row)

    def _edit(self, item):
        # ainult oma testiosa ylesande kohta
        c = self.c
        c.komplekt_id = item.komplekt_id
        c.komplektivalik = item.komplekt.komplektivalik
        c.komplektivalik_id = c.komplektivalik.id
        c.komplektis = self.request.params.get('komplektis') == '1' and 1 or None
        self._index_d()
        c.lang = self.params_lang()
        c.valitudylesanne_id = item.id # vajalik analysis.kysimus.mako sees

        c.toimumisaeg_id = c.toimumisaeg.id

        kvst_order = self.request.params.get('kvst_order')
        if kvst_order:
            self._set_default_params({'kvst_order': kvst_order})
            c.kvst_order = kvst_order
        else:
            p = self._get_default_params()
            c.kvst_order = p and p.get('kvst_order')
        
        ylesanne = item.ylesanne
        if ylesanne:
            c.testiosa = c.toimumisaeg.testiosa
            ta_id = c.testimiskord.analyys_eraldi and c.toimumisaeg.id or None
            if c.komplektis:
                c.ylesandestatistika = model.Ylesandestatistika.get_by_keys(item.id, item.ylesanne_id, True, ta_id)
            else:
                c.ylesandestatistika = model.Ylesandestatistika.get_by_keys(None, item.ylesanne_id, True, ta_id)
            c.item_html = BlockView(self, item.ylesanne, c.lang).assessment_analysis()

    def _prepare_items(self, q):
        "Loetelu ridade andmete väljastamine (CSV jaoks)"
        if self.c.csv_y:
            return self._prepare_items_y(q)
        else:
            return self._prepare_items_k(q)

    def _prepare_items_y(self, q, is_pdf=False):
        "Loetelu ridade andmete väljastamine (CSV jaoks)"
        c = self.c
        h = self.h
        header = self._prepare_header_y()
        items = []
        total_mean = total_max = 0
        for n, rcd in enumerate(q.all()):
            item, keskmine_p, max_p, vy_id, url_y = self._prepare_item_y(rcd, is_pdf)
            items.append(item)
            
            if keskmine_p is not None:
                total_mean += keskmine_p
            total_max += max_p

        item = [_("Kokku"),
                '',
                '',
                total_max and '%s (%s%%)' % (h.fstr(total_mean), h.fstr(total_mean*100./total_max)),
                h.fstr(total_max),
                ]
        return header, items

    def _prepare_header_y(self):
        c = self.c
        header = []
        header.extend([(None, _("Jrk")),
                       (None, _("Toorpunktid, keskmine")),
                       (None, _("Toorpunktid, max")),
                       (None, _("Hindepallid, keskmine")),
                       (None, _("Hindepallid, max")),
                       (None, _("Keskmine lahendusprotsent")),
                       (None, _("Rit")),
                       (None, _("Rir")),
                       ])
        if c.test.testiliik_kood == const.TESTILIIK_KOOLIPSYH:
            header.extend([(None, _("Keskmine aeg")),
                           (None, _("Min aeg")),
                           (None, _("Max aeg")),
                           ])
        header.append((None, _("Ülesande nimetus")))
        return header

    def _prepare_item_y(self, row, is_pdf=False):
        "Loetelu ridade andmete väljastamine"
        c = self.c
        h = self.h
        
        ylesanne, vy, ty, yst = row
        if yst:
            keskmine_p = yst.keskmine and yst.keskmine * vy.koefitsient or 0
        else:
            keskmine_p = None                
        if ty.max_pallid is None:
            max_p = ylesanne.max_pallid or 0
        else:
            max_p = ty.max_pallid

        if yst and yst.lahendatavus is not None:
            lahendatavus = '%s%%' % (h.fstr(yst.lahendatavus))
        else:
            lahendatavus = ''

        item = []
        item.extend([ty.tahis,
                     h.fstr(yst and yst.keskmine),
                     h.fstr(ylesanne.max_pallid),
                     h.fstr(keskmine_p),
                     h.fstr(ty.max_pallid),
                     lahendatavus,
                     h.fstr(yst and yst.rit, 2),
                     h.fstr(yst and yst.rir, 2),
                     ])
        if c.test.testiliik_kood == const.TESTILIIK_KOOLIPSYH:
            item.extend([h.str_from_time_sec(yst and yst.aeg_avg),
                         h.str_from_time_sec(yst and yst.aeg_min),
                         h.str_from_time_sec(yst and yst.aeg_max),
                         ])
        item.append(ylesanne.nimi)
        url_y = h.url_current('show', id=vy.id, komplekt_id=vy.komplekt_id, komplektis=c.komplektis)
        return item, keskmine_p, max_p, vy.id, url_y

    def _prepare_items_k(self, q, is_pdf=False):
        "Loetelu ridade andmete väljastamine (CSV jaoks)"
        c = self.c
        h = self.h
        header = [_("Ülesanne"),
                  _("Küsimus"),
                  _("Keskmine lahendusprotsent"),
                  _("Rit"),
                  _("Rir"),
                  ]
        
        tkorraga = bool(c.testimiskord)
        analyys_eraldi = c.testimiskord and c.testimiskord.analyys_eraldi
        if c.testimiskord:
            toimumisajad = {ta.testiosa_id: ta for ta in c.testimiskord.toimumisajad}
        else:
            toimumisajad = {}
        items = []
        for n, rcd in enumerate(q.all()):
            ylesanne, vy, ty, yst = rcd
            vy_id = c.komplektis and vy.id or None
            if c.testimiskord and analyys_eraldi:
                ta = toimumisajad[ty.testiosa_id]
            else:
                ta = None
            for sp in ylesanne.sisuplokid:
                if sp.is_interaction:
                    for kysimus in sp.kysimused:
                        if kysimus.tulemus_id or (sp.tyyp != const.INTER_MATCH2 and sp.tyyp != const.INTER_MATCH3):
                            if ta:
                                kst = ta.get_kysimusestatistika(kysimus.id, vy_id)
                            else:
                                kst = ty.testiosa.get_kysimusestatistika(kysimus.id, vy_id, tkorraga)
                            if kst:
                                item = [ty.tahis,
                                        kysimus.kood,
                                        h.fstr(kst.klahendusprotsent),
                                        h.fstr(kst.rit),
                                        h.fstr(kst.rir),
                                        ]
                                items.append(item)
        return header, items

    def _index_pdf(self, q, fn):
        c = self.c
        q = self._order(q)
        test = c.test
        testiosa = c.testiosa_id and model.Testiosa.get(c.testiosa_id) or None
        doc = VastustestatistikaDoc([test,
                                     testiosa,
                                     c.testimiskord,
                                     q,
                                     self._prepare_items_y,
                                     self._prepare_items_k,
                                     self._is_y_perm,
                                     c.opt])
        data = doc.generate()
        if doc.error:
            self.error(doc.error)
            return self._redirect('index')
        eeltest_id = test.eeltest_id
        if eeltest_id:
            # salvestame eeltesti statistika failina
            # peale seda võib eeltesti kustutada
            model.Session.rollback()
            eeltest = model.Eeltest.get(eeltest_id)
            eeltest.stat_filedata = data
            eeltest.stat_ts = datetime.now()
            model.Session.commit()
        return utils.download(data, fn, const.CONTENT_TYPE_PDF)

    def _search_protsessid(self, q):
        q = (q.filter(model.Arvutusprotsess.liik==model.Arvutusprotsess.LIIK_VASTUSED)
             .filter(model.Arvutusprotsess.kasutaja_id==self.c.user.id)
             .filter(model.Arvutusprotsess.toimumisaeg_id==self.c.toimumisaeg.id)
             )
        return q

    def _is_y_perm(self, ylesanne):
        c = self.c
        if not ylesanne or \
               c.user.has_permission('ylesanded', const.BT_SHOW, obj=ylesanne) \
               or c.app_eis and c.user.has_permission('avylesanded', const.BT_SHOW, obj=ylesanne) \
               or c.app_eis and c.user.has_permission('lahendamine', const.BT_SHOW, obj=ylesanne):
            return True
        else:
            return False
    
    def _perm_params(self):
        id = self.request.matchdict.get('id')
        if id:
            c = self.c
            item = model.Valitudylesanne.get(id)
            if not self._is_y_perm(item.ylesanne):
                self.error(_("Puudub õigus ülesande vaatamiseks"))
                raise HTTPFound(location=self.url_current('index'))
        return {'test_id': self.c.test.id}
    
    def __before__(self):
        c = self.c
        toimumisaeg_id = self.request.matchdict.get('toimumisaeg_id')
        c.toimumisaeg = model.Toimumisaeg.get(toimumisaeg_id)
        c.testimiskord = c.toimumisaeg.testimiskord
        c.testiosa = c.toimumisaeg.testiosa
        c.test = c.testimiskord.test
        
    def _gen_vastused(self, protsess, test_id, testiosa_id, alatest_id, komplekt_id, testimiskord_id):        
        "Vastuste ja tulemuste väljavõtte allalaadimine Exceli failina"
        max_protsent = 0

        def set_protsent(prot=None):
            if prot is None:
                prot = max_protsent
            prot = round(prot)
            if protsess and protsess.edenemisprotsent < prot:
                protsess.edenemisprotsent = prot
                model.Session.commit()
            if protsess.lopp:
                raise Exception("protsess katkestati")
        
        def _get_ylesanded(test_id, testiosa_id, alatest_id, komplekt_id, vyy_id):
            "Leitakse ylesanded, mille andmeid väljastada"
            q = (model.SessionR.query(model.Valitudylesanne.ylesanne_id,
                                     model.Valitudylesanne.id,
                                     model.Testiylesanne.testiosa_id,
                                     model.Testiylesanne.alatest_seq,
                                     model.Testiylesanne.seq,
                                     model.Testiylesanne.tahis,
                                     model.Testiylesanne.valikute_arv,
                                     model.Valitudylesanne.seq,
                                     model.Ylesanne.nimi,
                                     model.Komplekt.tahis)
                 .join(model.Valitudylesanne.testiylesanne)
                 .join(model.Valitudylesanne.ylesanne)
                 .filter(model.Valitudylesanne.id.in_(vyy_id))
                 .filter(model.Testiylesanne.liik.in_(
                     (const.TY_LIIK_Y, const.TY_LIIK_K)))
                 .filter(model.Valitudylesanne.test_id==test_id)
                 .join(model.Valitudylesanne.komplekt)
                 )
            if komplekt_id:
                q = q.filter(model.Valitudylesanne.komplekt_id==komplekt_id)
            elif alatest_id:
                q = q.filter(model.Testiylesanne.alatest_id==alatest_id)
            elif testiosa_id:
                q = q.filter(model.Testiylesanne.testiosa_id==testiosa_id)
            q = q.order_by(model.Testiylesanne.testiosa_id,
                           model.Testiylesanne.alatest_seq,
                           model.Komplekt.komplektivalik_id,
                           model.Komplekt.tahis,
                           model.Testiylesanne.seq,
                           model.Valitudylesanne.seq)
                 
            class Ydata:
                def __init__(self, y_id, vy_id, testiosa_id, alatest_seq, ty_seq, ty_tahis, valikute_arv, vy_seq, k_tahis):
                    self.ylesanne_id = y_id
                    self.vy_id = vy_id
                    self.testiosa_id = testiosa_id
                    self.alatest_seq = alatest_seq
                    self.ty_seq = ty_seq
                    self.ty_tahis = ty_tahis
                    self.on_valikylesanne = valikute_arv > 1
                    self.vy_seq = vy_seq
                    self.k_tahis = k_tahis
                    self.kysimused = []
                    self.aspektid = []
                    
            ylesanded = {}
            for r in q.all():
                y_id, vy_id, testiosa_id, alatest_seq, ty_seq, ty_tahis, valikute_arv, vy_seq, y_nimi, k_tahis = r
                ydata = Ydata(y_id, vy_id, testiosa_id, alatest_seq, ty_seq, ty_tahis, valikute_arv, vy_seq, k_tahis)
                ydata.nimi = y_nimi
                ylesanded[vy_id] = ydata
            set_protsent()
            return ylesanded

        def _get_testiosad(ylesanded, testimiskord_id):
            "Leitakse testiosad ja toimumisajad, mille ülesandeid on vaja väljastada"
            testiosad_id = set()
            for ydata in ylesanded.values():
                testiosad_id.add(ydata.testiosa_id)

            class Odata:
                def __init__(self, testiosa, toimumisaeg_id):
                    self.testiosa = testiosa
                    self.testiosa_id = testiosa.id
                    self.toimumisaeg_id = toimumisaeg_id
                    self.normipunktid = []

                    # vastavus alatestide ja komplektivalikute vahel
                    if testiosa.on_alatestid:
                        alatest_kv = {a.seq: a.komplektivalik_id for a in testiosa.alatestid}
                    else:
                        alatest_kv = {None: kv.id for kv in testiosa.komplektivalikud}
                    self.map_alatest_kv = alatest_kv

                    # vastavus komplekti id ja tähise vahel
                    map_k = {}
                    for kv in testiosa.komplektivalikud:
                        for k in kv.komplektid:
                            map_k[k.id] = k.tahis
                    self.map_k = map_k
                    
                    # kas komplektivalik kehtib osade alatestide või kogu testiosa kohta
                    self.on_alatest_komplekt = len(alatest_kv) > 1
                    self.on_testiosa_komplekt = not self.on_alatest_komplekt
                    
            if testimiskord_id:
                q = (model.SessionR.query(model.Testiosa, model.Toimumisaeg.id)
                     .filter(model.Testiosa.id.in_(testiosad_id))
                     .join(model.Toimumisaeg.testiosa)
                     .filter(model.Toimumisaeg.testimiskord_id==testimiskord_id)
                     .order_by(model.Testiosa.seq))
                testiosad = [Odata(osa, ta_id) for (osa, ta_id) in q.all()]
            else:
                q = (model.SessionR.query(model.Testiosa)
                     .filter(model.Testiosa.id.in_(testiosad_id))
                     .order_by(model.Testiosa.seq))
                testiosad = [Odata(osa, None) for osa in q.all()]
            set_protsent()
            return testiosad
        
        def _get_kysimused(vyy_id, ylesanded):
            "Leitakse kysimused, mille andmed väljastada"
            sql = """SELECT vy.id,
                kysimus.sisuplokk_id,
                kysimus.kood,
                vk.kood,
                sp.seq sp_seq,
                sp.tyyp sp_tyyp,
                kysimus.seq AS kysimus_seq,
                kysimus.id kysimus_id,
                tulemus.kardinaalsus,
                tulemus.arvutihinnatav,
                tulemus.hybriidhinnatav,
             	COALESCE(vk.max_vastus, kysimus.max_vastus, kysimus.max_vastus_arv) max_vastus,
                CASE WHEN vk.id IS NULL THEN COALESCE(tulemus.max_pallid, tulemus.max_pallid_arv)
                     ELSE vk.max_pallid
                END AS max_punktid,
                vv.sisujarjestus,
                vv.mittevastus,
                vv.analyys1,
                CASE WHEN vk.id IS NULL THEN kysimus.selgitus
                     ELSE vk.selgitus
                END AS k_selgitus,
                kysimus.rtf
            FROM kysimus
                 JOIN sisuplokk sp ON sp.id=kysimus.sisuplokk_id
                 JOIN tulemus ON tulemus.id = kysimus.tulemus_id
                 JOIN valitudylesanne vy ON vy.ylesanne_id=tulemus.ylesanne_id
                 JOIN testiylesanne ty ON ty.id=vy.testiylesanne_id
                 LEFT JOIN valikvastus vv ON vv.tulemus_id = tulemus.id AND
                      (vv.maatriks=1 OR sp.tyyp='5' /* imatch3 */)
                 LEFT JOIN valik vk ON vv.paarina = false AND
                      (vv.vahetada = true AND vk.kysimus_id=vv.valik2_kysimus_id OR
                       vv.vahetada = false AND vk.kysimus_id=vv.valik1_kysimus_id)
                 WHERE (vv.statvastuses=true OR vv.id IS NULL)
                 AND vy.id=ANY(:vyy_id)
                 """
            params = {'vyy_id': vyy_id}
            sql += " ORDER BY vy.id, sp.seq, kysimus.seq, vk.seq "
            #log.debug(sql + str(params))

            for r in model.SessionR.execute(sa.text(sql), params):
                vy_id, sp_id, k_kood, vk_kood, sp_seq, sp_tyyp, k_seq, k_id, kardinaalsus,\
                       arvutihinnatav, hybriidhinnatav, max_v, max_p, \
                       sisujarjestus, mittevastus, analyys1, k_selgitus, k_rtf = r
                if sisujarjestus or not max_v or analyys1:
                    max_v = 1
                if vk_kood:
                    kood1 = f'{k_kood}:{vk_kood}'
                else:
                    kood1 = k_kood
                hinnatav = sp_tyyp != const.BLOCK_RANDOM
                rcd = (sp_seq, kood1, k_id, max_v, sp_id, arvutihinnatav, max_p, hinnatav, mittevastus, vk_kood, k_selgitus, k_rtf)
                ylesanded[vy_id].kysimused.append(rcd)
            set_protsent()
            
        def _get_aspektid(vyy_id, ylesanded):
            "Leitakse hindamisaspektid"
            q = (model.SessionR.query(model.Valitudylesanne.id,
                                     model.Hindamisaspekt.id,
                                     model.Hindamisaspekt.aspekt_kood,
                                     model.Hindamisaspekt.seq,
                                     model.Hindamisaspekt.aine_kood)
                 .join((model.Hindamisaspekt,
                        model.Hindamisaspekt.ylesanne_id==model.Valitudylesanne.ylesanne_id))
                 .join(model.Valitudylesanne.testiylesanne)
                 .filter(model.Valitudylesanne.id.in_(vyy_id))
                 .order_by(model.Valitudylesanne.id,
                           model.Hindamisaspekt.seq)
                 )
            aspektid = {}
            for r in q.all():
                vy_id, ha_id, ha_kood, ha_seq, aine = r
                a_nimi = model.Klrida.get_str('ASPEKT', ha_kood, ylem_kood=aine)
                rcd = (ha_id, ha_kood, ha_seq, a_nimi)
                ylesanded[vy_id].aspektid.append(rcd)
            set_protsent()
            
        def _get_header(ylesanded, testiosad, normipunktid, ajakulu, ylp, kysv, kysp, oige, on_avalik):
            "Väljavõtte tabeli päise andmete kogumine"
            # andmete väljavõtte tabeli päis
            header = ["sooritaja_id",
                      _("Sugu"),
                      _("Õppimiskoha ehis_id"),
                      _("Õppimiskoht"),
                      _("Soorituskeel"),
                      _("Testi tulemus"),
                      ]
            if on_avalik:
                header[1:1] = [_("Isikukood"), _("Nimi")]
                
            # andmete väljavõtte tabeli veergude selgitused, kuvatakse Exceli teisel lehel
            legend = []
            mitu_osa = len(testiosad) > 1
            for odata in testiosad:
                testiosa = odata.testiosa
                toimumisaeg_id = odata.toimumisaeg_id
                osa_ylesanded = [ydata for ydata in ylesanded.values() if ydata.testiosa_id == testiosa.id]
                odata.mitu_komplekti = len(set([ydata.k_tahis for ydata in osa_ylesanded])) > 1
                if mitu_osa:
                    osa_prefix = testiosa.tahis + '_'
                    header.append(osa_prefix + _("Testiosa tulemus"))
                    header.append(osa_prefix + _("Kuupäev"))
                else:
                    osa_prefix = ''
                    header.append(osa_prefix + _("Kuupäev"))

                if odata.on_testiosa_komplekt:
                    header.append(osa_prefix + _("Komplekt"))
                    
                if ajakulu and testiosa.vastvorm_kood in (const.VASTVORM_KE, const.VASTVORM_SE):
                    header.append(osa_prefix + _("Testiosa ajakulu (minutid)"))

                prev_alatest_seq = None
                for ydata in osa_ylesanded:
                    if odata.mitu_komplekti:
                        k_prefix = osa_prefix + ydata.k_tahis + '_'
                    else:
                        k_prefix = osa_prefix

                    if odata.on_alatest_komplekt and ydata.alatest_seq != prev_alatest_seq:
                        # uus alatest algas
                        prev_alatest_seq = ydata.alatest_seq
                        header.append(k_prefix + _("Komplekt"))
                        
                    y_header, y_legend = _get_y_header(k_prefix, ydata, ajakulu, ylp, kysv, kysp, oige)
                    header.extend(y_header)
                    legend.extend(y_legend)

            if c.tsopil or c.tsopet:
                # tunnuste tagasiside
                np_header, np_legend = _get_np_header(normipunktid, c.tsopil, c.tsopet)
                header.extend(np_header)
                legend.extend(np_legend)
            set_protsent()
            return header, legend
        
        def _get_y_header(k_prefix, ydata, ajakulu, ylp, kysv, kysp, oige):
            "Ühe ülesandega seotud päis"
            header = []
            legend = []
            y_prefix = k_prefix + (ydata.ty_tahis or '')
            if ydata.on_valikylesanne:
                y_prefix += f'_v{ydata.vy_seq}'
            if ylp:
                header.append(f'{y_prefix}_YlPunktid')
            if ajakulu:
                header.append(f'{y_prefix}_Ajakulu')

            on_aspektid = bool(ydata.aspektid)

            for r in ydata.kysimused:
                sp_seq, kood1, k_id, max_v, sp_id, arvutihinnatav, max_p, hinnatav, mittevastus, vk_kood, k_selgitus, rtf = r
                k_prefix = f'{y_prefix}_{sp_seq}_{kood1}'                
                if not mittevastus:
                    for n_seq in range(max_v):
                        if max_v == 1:
                            ks_prefix = k_prefix
                        else:
                            ks_prefix = f'{k_prefix}_{n_seq}'
                        if kysv:
                            header.append(f'{ks_prefix}_Vastus')
                            if vk_kood or arvutihinnatav:
                                # kui on valikvastus või arvutihinnatav
                                header.append(f'{ks_prefix}_Selgitus')
                        if oige and arvutihinnatav and hinnatav and not on_aspektid:
                            # arvutihinnatava vastuse õigsus on teada iga vastuse kohta
                            header.append(f'{ks_prefix}_Oige')
                if hinnatav and not on_aspektid:
                    if oige and not arvutihinnatav and not mittevastus:
                        # käsitsihinnatavaid kysimusi hinnatakse kõik vastused koos
                        header.append(f'{k_prefix}_Oige')
                    if kysp:
                        header.append(f'{k_prefix}_Punktid')
                # kui kysimuse kohta on mõni veerg, siis lisame legendi
                if header and header[-1].startswith(k_prefix):
                    legend.append((k_prefix, k_selgitus or ''))
                        
            for r in ydata.aspektid:
                ha_id, ha_kood, ha_seq, a_nimi = r
                ha_prefix = f'{y_prefix}_{ha_kood}'
                if kysp:
                    header.append(f'{ha_prefix}_Punktid')
                    legend.append((ha_prefix, a_nimi or ''))

            # kui ylesande kohta on mõni veerg, siis lisame legendi
            if ydata.nimi and header and header[-1].startswith(y_prefix):
                label = '%s %s: %s' % (_("Ülesanne"), ydata.ylesanne_id, ydata.nimi)
                legend.insert(0, (y_prefix, label))
            return header, legend

        def get_sts_id(testiosa_id, toimumisaeg_id):
            "Leitakse viimane andmete väljavõtte jaoks andmestiku genereerimise protsessi ID"
            q = (model.SessionR.query(sa.func.max(model.Statvastus_t_seis.id))
                 .filter_by(testiosa_id=testiosa_id)
                 .filter_by(toimumisaeg_id=toimumisaeg_id))
            return q.scalar()

        def _get_vastused(testiosad, vyy_id):
            "Leitakse sooritajate vastused"
            data = {}
            for odata in testiosad:
                testiosa_id = odata.testiosa_id
                toimumisaeg_id = odata.toimumisaeg_id
                sts_id = get_sts_id(testiosa_id, toimumisaeg_id)
                q = (model.SessionR.query(model.Statvastus_t.sooritus_id,
                                         model.Statvastus_t.valitudylesanne_id,
                                         model.Statvastus_t.kysimus_id,
                                         model.Statvastus_t.kood1,
                                         model.Statvastus_t.kvsisu_seq,
                                         model.Statvastus_t.vastus,
                                         model.Statvastus_t.selgitus,
                                         model.Statvastus_t.ks_punktid,
                                         model.Statvastus_t.oige,
                                         model.Statvastus_t.kv_punktid)
                     .filter(model.Statvastus_t.valitudylesanne_id.in_(vyy_id))
                     .filter(model.Statvastus_t.staatus==const.S_STAATUS_TEHTUD)
                     .filter(model.Statvastus_t.statvastus_t_seis_id==sts_id)
                     .filter(model.Statvastus_t.toimumisaeg_id==toimumisaeg_id)
                    )
                for r in q.all():
                    s_id, vy_id, k_id, kood1, kvs_seq, vastus, selgitus, ks_p, oige, kv_p = r
                    key = (s_id, vy_id, k_id, kood1)
                    # Microsoft Excel has a character limit of 32,767 characters in each cell
                    MAX_LENGTH = 32767
                    if vastus and len(vastus) > MAX_LENGTH:
                        vastus = vastus[:MAX_LENGTH]
                    value = (kvs_seq, vastus, selgitus, ks_p, oige, kv_p)
                    if key not in data:
                        data[key] = [value]
                    else:
                        data[key].append(value)
            
            # järjestame vastused kvs_seq järjekorras
            # (paaridega vastuse korral ei ole kvs.seq sama, mis kood1 jrk nr,
            # nt seostamine k_id=179307 vy_id=58353 s_id=4059924)
            for key, values in data.items():
                values.sort(key=lambda x: x[0])
            set_protsent()
            return data

        def _get_aspektipunktid(testiosad, vyy_id):
            "Leitakse sooritajate aspektide tulemused"
            data = {}
            for odata in testiosad:
                testiosa_id = odata.testiosa_id
                toimumisaeg_id = odata.toimumisaeg_id
                q = (model.SessionR.query(model.Ylesandevastus.sooritus_id,
                                        model.Ylesandevastus.valitudylesanne_id,
                                        model.Vastusaspekt.hindamisaspekt_id,
                                        model.Vastusaspekt.toorpunktid)
                     .filter(model.Ylesandevastus.valitudylesanne_id.in_(vyy_id))
                     .join((model.Sooritus, model.Sooritus.id==model.Ylesandevastus.sooritus_id))
                     .join((model.Vastusaspekt,
                            model.Ylesandevastus.id==model.Vastusaspekt.ylesandevastus_id))
                     .filter(model.Sooritus.staatus==const.S_STAATUS_TEHTUD)
                     .filter(model.Sooritus.testiosa_id==testiosa_id)
                     )
                if toimumisaeg_id:
                    q = q.filter(model.Sooritus.toimumisaeg_id==toimumisaeg_id)
                else:
                    q = q.filter(model.Sooritus.toimumisaeg_id==None)
                for s_id, vy_id, ha_id, ha_p in q.all():
                    data[(s_id, vy_id, ha_id)] = ha_p
            set_protsent()
            return data

        def _get_ylesandepallid(testiosad, vyy_id):
            "Leitakse sooritajate ylesandetulemused"
            data = {}
            for odata in testiosad:
                testiosa_id = odata.testiosa_id
                toimumisaeg_id = odata.toimumisaeg_id
                q = (model.SessionR.query(model.Ylesandevastus.sooritus_id,
                                        model.Ylesandevastus.valitudylesanne_id,
                                        model.Ylesandevastus.pallid,
                                        model.Ylesandevastus.ajakulu)
                    .filter(model.Ylesandevastus.valitudylesanne_id.in_(vyy_id))
                    .join((model.Sooritus, model.Sooritus.id==model.Ylesandevastus.sooritus_id))
                    .filter(model.Sooritus.testiosa_id==testiosa_id)
                    .filter(model.Sooritus.toimumisaeg_id==toimumisaeg_id)
                    .filter(model.Sooritus.staatus==const.S_STAATUS_TEHTUD)
                    )
                for s_id, vy_id, y_p, ajakulu in q.all():
                    data[(s_id, vy_id)] = (y_p, ajakulu)
            set_protsent()
            return data

        def _get_np(test_id):
            "Tagasiside tunnused"
            normipunktid = []
            q1 = (model.SessionR.query(model.Testiosa.id)
                  .filter(model.Testiosa.test_id==test_id)
                  .order_by(model.Testiosa.seq))
            for testiosa_id, in q1.all():
                q = (model.SessionR.query(model.Normipunkt.id,
                                         model.Normipunkt.kood,
                                         model.Normipunkt.nimi,
                                         model.Normipunkt.seq,
                                         model.Alatest.seq,
                                         model.Testiylesanne.alatest_seq,
                                         model.Testiylesanne.seq,
                                         model.Testiylesanne.tahis)
                     .outerjoin(model.Normipunkt.alatest)
                     .outerjoin(model.Normipunkt.testiylesanne)
                     .filter(sa.or_(model.Normipunkt.testiosa_id==testiosa_id,
                               model.Alatest.testiosa_id==testiosa_id,
                               model.Testiylesanne.testiosa_id==testiosa_id))
                     .filter(model.Testiosa.test_id==test_id)
                     .filter(model.Normipunkt.nptagasisided.any(
                         sa.or_(model.Nptagasiside.tagasiside!=None,
                                model.Nptagasiside.op_tagasiside!=None)))
                     .order_by(model.Alatest.seq,
                            model.Testiylesanne.alatest_seq,
                            model.Testiylesanne.seq,
                            model.Normipunkt.seq)
                    )
                for r in q.all():
                    np_id, np_kood, np_nimi, np_seq, a_seq, tya_seq, ty_seq, ty_tahis = r
                    if not np_kood:
                        np_kood = ''
                    if ty_tahis:
                        np_prefix = f'{ty_tahis}_{np_kood}'
                    else:
                        np_prefix = f'{np_seq}_{np_kood}'                    
                    normipunktid.append((np_id, np_prefix, np_nimi))
                    
            return normipunktid

        def _get_np_header(normipunktid, tsopil, tsopet):
            "Tagasiside väljade päis"
            header = []
            legend = []
            for np_id, np_prefix, np_nimi in normipunktid:
                if tsopil:
                    header.append(f'{np_prefix}_õpilane')
                if tsopet:
                    header.append(f'{np_prefix}_õpetaja')
                if np_nimi:
                    legend.append((np_prefix, np_nimi))
            return header, legend

        def _get_tagasiside(test_id, testimiskord_id):
            "Tunnuste tagasiside kogumine"
            data = {}
            q = (model.SessionR.query(model.Sooritaja.id,
                                     model.Npvastus.normipunkt_id,
                                     model.Nptagasiside.tagasiside,
                                     model.Nptagasiside.op_tagasiside)
                 .join((model.Nptagasiside,
                        model.Nptagasiside.id==model.Npvastus.nptagasiside_id))
                 .join((model.Sooritus, model.Sooritus.id==model.Npvastus.sooritus_id))
                 .join(model.Sooritus.sooritaja)
                 .filter(model.Sooritaja.test_id==test_id)
                 .filter(model.Sooritaja.testimiskord_id==testimiskord_id)
                 )
            for j_id, np_id, tagasiside, op_tagasiside in q.all():
                data[(j_id, np_id)] = (tagasiside, op_tagasiside)
            set_protsent()
            return data

        def out_kysimus(s_id, vy_id, r, data, on_aspektid):
            "Kysimuse veergude väljastamine"
            sp_seq, kood1, k_id, max_v, sp_id, arvutihinnatav, max_p, hinnatav, mittevastus, vk_kood, k_selgitus, rtf = r
            # kas on andmeid
            any_data = False
            # kysimuse veerud
            item = []
            key = (s_id, vy_id, k_id, kood1)
            values = data.get(key)
            # selgitus on siis, kui on valikvastus või arvutihinnatav
            on_selgitus = vk_kood or arvutihinnatav
            ks_p_sum = kv_p = None
            for kvs_seq in range(max_v or 1):
                value = values and len(values) > kvs_seq and values[kvs_seq]
                if value:
                    any_data = True
                    seq, vastus, selgitus, ks_p, oige, kv_p = value
                    if ks_p is not None:
                        ks_p_sum = (ks_p_sum or 0) + ks_p
                    if c.kysv and not mittevastus:
                        if rtf:
                            vastus = html2plain(vastus)
                        item.append(vastus)
                        if on_selgitus:
                            item.append(selgitus)
                    if c.oige and arvutihinnatav and hinnatav and not on_aspektid and not mittevastus:
                        item.append(oige)
                else:
                    if c.kysv and not mittevastus:
                        item.append('')
                        if on_selgitus:
                            item.append('')
                    if c.oige and arvutihinnatav and hinnatav and not on_aspektid and not mittevastus:
                        item.append('')
            if ks_p_sum is not None and kv_p is not None and ks_p_sum > kv_p:
                ks_p_sum = kv_p
            elif ks_p_sum is None and kv_p is not None:
                ks_p_sum = kv_p
            elif ks_p_sum == 0 and kv_p is not None and kv_p > 0:
                # p-test, kus kvsisu kirjed puuduvad
                ks_p_sum = kv_p
            if hinnatav and not on_aspektid:
                if c.oige and not arvutihinnatav and not mittevastus:
                    # leiame kysimuse taseme õigsuse
                    if ks_p_sum is None or max_p is None:
                        oige = ''
                    elif ks_p_sum >= max_p - .00001:
                        oige = 1
                    elif ks_p_sum > 0:
                        oige = 0.5
                    else:
                        oige = 0
                    item.append(oige)
                if c.kysp:
                    item.append(ks_p_sum)
            return item, any_data

        def out_ylesanne(s_id, vy_id, ydata, data, data_y, data_ha):
            "Ylesande veergude väljastamine"
            any_data = False
            item = []
            on_aspektid = bool(ydata.aspektid)
            # ylesande punktid ja ajakulu
            key = (s_id, vy_id)
            r = data_y.get(key)
            if r:
                any_data = True
                y_p, ajakulu = r
            else:
                y_p = ajakulu = None
            if c.ylp:
                item.append(y_p)
            if c.ajakulu:
                item.append(ajakulu)

            # kysimused
            for r in ydata.kysimused:
                k_item, k_any_data = out_kysimus(s_id, vy_id, r, data, on_aspektid)
                item.extend(k_item)
                any_data |= k_any_data
                
            # hindamisaspektid
            for r in ydata.aspektid:
                ha_id, ha_kood, ha_seq, a_nimi = r
                key = (s_id, vy_id, ha_id)
                ha_p = data_ha.get(key)
                if ha_p is not None:
                    any_data = True
                elif y_p == 0:
                    ha_p = 0
                if c.kysp:
                    item.append(ha_p)

            return item, any_data

        def out_ts(j_id, np_id, data_ts):
            "Tagasiside veergude väljastamine"
            any_data = False
            item = []
            r = data_ts.get((j_id, np_id))
            if r:
                tagasiside, op_tagasiside = r
            else:
                tagasiside = op_tagasiside = ''
            if c.tsopil:
                value = ''
                if tagasiside:
                    value = html2plain(tagasiside)
                    any_data = True
                item.append(value)
            if c.tsopet:
                value = ''
                if op_tagasiside:
                    value = html2plain(op_tagasiside)
                    any_data = True
                item.append(value)
            return item, any_data

        def q_sooritajad(testiosad, testiosa_id, komplekt_id, testimiskord_id):
            # sooritajate päring
            testiosad_id = [odata.testiosa_id for odata in testiosad]
            q = (model.SessionR.query(model.Sooritaja.id,
                                    model.Sooritaja.eesnimi,
                                    model.Sooritaja.perenimi,
                                    model.Kasutaja.id,
                                    model.Kasutaja.isikukood,
                                    model.Sooritaja.pallid,
                                    model.Kasutaja.sugu,
                                    model.Koht.kool_id,
                                    model.Koolinimi.nimi,
                                    model.Sooritaja.lang)
                .filter(model.Sooritaja.testimiskord_id==testimiskord_id)
                .filter(model.Sooritaja.test_id==test_id)
                .join(model.Sooritaja.kasutaja)
                .outerjoin(model.Sooritaja.kool_koht)
                .outerjoin(model.Sooritaja.koolinimi)
                )
            if testiosa_id:
                # etteantud testiosa peab olema tehtud
                q = (q.join(model.Sooritaja.sooritused)
                    .filter(model.Sooritus.testiosa_id==testiosa_id)
                    .filter(model.Sooritus.staatus==const.S_STAATUS_TEHTUD)
                    )
                if komplekt_id:
                    q = (q.join((model.Soorituskomplekt,
                                 model.Sooritus.id==model.Soorituskomplekt.sooritus_id))
                        .filter(model.Soorituskomplekt.komplekt_id==komplekt_id)
                        )
            else:
                # kõik sooritajad, millel mõni meid huvitav testiosa on tehtud
                q = (q.filter(model.Sooritaja.sooritused.any(
                    sa.and_(model.Sooritus.testiosa_id.in_(testiosad_id),
                            model.Sooritus.staatus==const.S_STAATUS_TEHTUD)))
                    )
            q = q.order_by(model.Sooritaja.eesnimi, model.Sooritaja.perenimi)
            set_protsent()
            return q
        
        def out_sooritaja(r, testiosad, ylesanded, normipunktid, data, data_y, data_ha, data_ts, on_avalik):
            "Sooritaja rea väljastamine"
            j_id, j_eesnimi, j_perenimi, k_id, k_ik, j_pallid, sugu, kool_id, k_nimi, j_lang = r
            item = [j_id,
                    sugu,
                    kool_id,
                    k_nimi,
                    j_lang,
                    j_pallid
                    ]
            if on_avalik:
                item[1:1] = [k_ik, f'{j_eesnimi} {j_perenimi}']
            any_data = False
            mitu_osa = len(testiosad) > 1
            for odata in testiosad:
                testiosa = odata.testiosa
                testiosa_id = odata.testiosa_id
                q = (model.SessionR.query(model.Sooritus.id,
                                         model.Sooritus.algus,
                                         model.Sooritus.lopp,
                                         model.Sooritus.ajakulu,
                                         model.Sooritus.pallid)
                     .filter(model.Sooritus.sooritaja_id==j_id)
                     .filter(model.Sooritus.staatus==const.S_STAATUS_TEHTUD)
                     .filter(model.Sooritus.testiosa_id==testiosa_id)
                     )
                r2 = q.first()
                if r2:
                    s_id, algus, lopp, ajakulu, pallid = r2
                else:
                    s_id = -1
                    algus = lopp = ajakulu = pallid = None
                if mitu_osa:
                    item.append(pallid)
                item.append(self.h.str_from_date(algus))

                # komplekt
                q = (model.SessionR.query(model.Soorituskomplekt.komplektivalik_id,
                                         model.Soorituskomplekt.komplekt_id)
                     .filter(model.Soorituskomplekt.sooritus_id==s_id)
                     )
                map_kv_k = {kv_id: k_id for (kv_id, k_id) in q.all()}
                if odata.on_testiosa_komplekt:
                    # sama komplekt kogu testiosas
                    k_tahis = ''
                    for k_id in map_kv_k.values():
                        k_tahis = odata.map_k.get(k_id)
                        break
                    item.append(k_tahis)
                    
                if c.ajakulu and testiosa.vastvorm_kood in (const.VASTVORM_KE, const.VASTVORM_SE):                    
                    ajakulu_min = ajakulu and round(ajakulu/60) or None
                    item.append(ajakulu_min)

                prev_alatest_seq = None
                for vy_id, ydata in ylesanded.items():
                    if ydata.testiosa_id == testiosa_id:
                        if odata.on_alatest_komplekt and prev_alatest_seq != ydata.alatest_seq:
                            # algab uus alatest
                            prev_alatest_seq = ydata.alatest_seq
                            kv_id = odata.map_alatest_kv.get(ydata.alatest_seq)
                            k_id = map_kv_k.get(kv_id)
                            k_tahis = odata.map_k.get(k_id)
                            item.append(k_tahis)
                            
                        y_item, y_any_data = out_ylesanne(s_id, vy_id, ydata, data, data_y, data_ha)
                        any_data |= y_any_data
                        item.extend(y_item)

            for np_id, np_prefix, np_nimi in normipunktid:
                ts_item, ts_any_data = out_ts(j_id, np_id, data_ts)
                any_data |= ts_any_data
                item.extend(ts_item)

            if any_data:
                return item

        c = self.c
        self.prf()

        vyy_id = list(map(int, self.request.params.getall('vy_id')))
        max_protsent = 5
        ylesanded = _get_ylesanded(test_id, testiosa_id, alatest_id, komplekt_id, vyy_id)
        vyy_id = list(ylesanded.keys())
        self.prf('ylesanded')
        max_protsent = 10
        # kas on mitme testiosa ylesanded?
        testiosad = _get_testiosad(ylesanded, testimiskord_id)

        if c.tsopil or c.tsopet:                
            normipunktid = _get_np(c.test.id)
        else:
            normipunktid = []

        max_protsent = 15      
        _get_kysimused(vyy_id, ylesanded)
        self.prf('kysimused')
        max_protsent = 20
        _get_aspektid(vyy_id, ylesanded)
        self.prf('aspektid')

        max_protsent = 25
        on_avalik = c.test.testiliik_kood == const.TESTILIIK_AVALIK
        header, legend = _get_header(ylesanded, testiosad, normipunktid, c.ajakulu, c.ylp, c.kysv, c.kysp, c.oige, on_avalik)
        self.prf('header')
        max_protsent = 65
        data = _get_vastused(testiosad, vyy_id)
        self.prf('vastused')
        max_protsent = 70
        if c.ajakulu or c.ylp:
            data_y = _get_ylesandepallid(testiosad, vyy_id)
            self.prf('ylesandepallid')
        else:
            data_y = {}

        max_protsent = 75
        if c.kysp:
            data_ha = _get_aspektipunktid(testiosad, vyy_id)
            self.prf('aspektipunktid')
        else:
            data_ha = {}

        max_protsent = 80
        if c.tsopil or c.tsopet:
            # tunnuste tagasiside
            data_ts = _get_tagasiside(c.test.id, testimiskord_id)
        else:
            normipunktid = []
            data_ts = {}

        max_protsent = 85
        self.prf('q sooritajad')
        # tabeli read
        q = q_sooritajad(testiosad, testiosa_id, komplekt_id, testimiskord_id)
        total = q.count()
        items = []
        for ind, r in enumerate(q.all()):
            item = out_sooritaja(r, testiosad, ylesanded, normipunktid, data, data_y, data_ha, data_ts, on_avalik)
            if item:
                items.append(item)
            if protsess:
                protsent = max_protsent + round(ind/total * 6)
                if protsent != protsess.edenemisprotsent:
                    protsess.edenemisprotsent = protsent
                    model.Session.commit()
                    
        self.prf('tehtud')

        legend_header = (_("Veerg"), _("Selgitus"))

        # kahe lehega Exceli fail, esimeses andmed ja teises veergude selgitused
        sheets = [(header, items, _("Andmed")),
                  (legend_header, legend, _("Legend"))]
        if testiosa_id:
            testiosa = model.Testiosa.get(testiosa_id)
            if komplekt_id:
                komplekt = model.Komplekt.get(komplekt_id)
                fn = 'vastused_%s_%s_%s.xlsx' % (test_id, testiosa.seq, komplekt.tahis)
            else:
                fn = 'vastused_%s_%s.xlsx' % (test_id, testiosa.seq)                
        else:
            fn = 'vastused_%s.xlsx' % (test_id)
        setwidth = self.c.is_devel or self.c.is_debug and 1 or 0
        filedata = utils.xls_multisheet_data(sheets, setwidth)
        return filedata, fn

    def _download_vastused(self, test_id, testiosa_id, alatest_id, komplekt_id, testimiskord_id):
        debug = self.request.params.get('debug')

        def childfunc(protsess):
            filedata, fn = self._gen_vastused(protsess, test_id, testiosa_id, alatest_id, komplekt_id, testimiskord_id)
            if protsess:
                protsess.filename = fn
                protsess.filedata = filedata
            else:
                return utils.download(filedata, fn)

        c = self.c
        if c.user.has_permission('vastustevaljavote', const.BT_SHOW, obj=c.test):
            # lõpetame vanad
            for rcd in self._query_protsessid(True):
                rcd.lopp = datetime.now()
                model.Session.commit()

            liik = model.Arvutusprotsess.LIIK_VASTUSED
            params = {'liik': liik,
                      'test_id': c.test.id,
                      }
            if c.testimiskord and c.toimumisaeg:
                params['testimiskord_id'] = c.testimiskord.id
                params['toimumisaeg_id'] = c.toimumisaeg.id
                tahised = c.toimumisaeg.tahised
                params['kirjeldus'] = _("Vastuste väljavõte") + f' ({tahised})'
            else:
                params['kirjeldus'] = _("Vastuste väljavõte") + f' ({c.test.id})'
            resp = model.Arvutusprotsess.start(self, params, childfunc)
            if debug:
                return resp
        self.success(_("Vastuste väljavõtte genereerimine on käivitatud"))
        raise self._redirect('index')


class MLStripper(HTMLParser):
    "HTMLi tagide eemaldamine"
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.text = StringIO()

    def handle_data(self, d):
        self.text.write(d)

    def get_data(self):
        return self.text.getvalue()

def html2plain(html):
    # toores alternatiiv: return re.sub(r'<[^>]+>', '', html)
    
    s = MLStripper()
    s.feed(html)
    return s.get_data()
