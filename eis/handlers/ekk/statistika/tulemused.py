from simplejson import dumps
from collections import defaultdict
import plotly.graph_objects as go
import math
from eis.lib.baseresource import *
_ = i18n._
log = logging.getLogger(__name__)

class TulemusedController(BaseResourceController):
    """Tulemuste statistika
    """
    _permission = 'aruanded-tulemused'
    _INDEX_TEMPLATE = 'ekk/statistika/tulemused.otsing.mako'
    _LIST_TEMPLATE = 'ekk/statistika/tulemused.list.mako'
    _DEFAULT_SORT = 'aine_kl.nimi'
    _ignore_default_params = ['csv']
    _SEARCH_FORM = forms.ekk.otsingud.TulemusedForm

    def _index_d(self):
        res = super()._index_d()
        self._get_protsessid()    
        return res
    
    def _query(self):
        return

    def _search_default(self, q):
        c = self.c
        c.testiliik = const.TESTILIIK_RIIGIEKSAM
        c.alla = 20
        c.yle = 80
        c.tkord = 1
        
        c.col_regatud = 1
        c.col_puudus = 1
        c.col_kais = 1
        c.col_eksaminandid = 1
        c.col_maxpallid = 1
        c.col_keskmine = 1
        c.col_keskminepr = 1
        c.col_halve = 1
        c.col_alla20 = 1
        c.col_alla20pr = 1
        c.col_minsaajad = 1
        c.col_maxsaajad = 1
        c.col_min = 1
        c.col_max = 1
        c.col_yle80 = 1
        c.col_yle80pr = 1
        return None

    def _search(self, q1):
        """Põhiline otsing"""

        self.c.prepare_row = self._prepare_row

        if not isinstance(self.c.alla, (int,float)):
            self.c.alla = 20
        if not isinstance(self.c.yle, (int,float)):
            self.c.yle = 80

        if self.c.ositi:
            li = self.c.osanimi.split('.', 1)
            if len(li) != 2:
                self.c.ositi = False
            else:
                if li[0] == 'a':
                    self.c.alatestinimi = li[1]
                    self.c.testiosanimi = None
                else:
                    self.c.alatestinimi = None
                    self.c.testiosanimi = li[1]
        Aine_kl = sa.orm.aliased(model.Klrida, name='aine_kl')
        
        if self.c.ositi and self.c.testiosanimi:
            li_select = [sa.func.count(model.Sooritus.id),
                         ]
            li = [model.Test.aine_kood,
                  Aine_kl.nimi,
                  model.Testimiskord.aasta,
                  model.Test.id,
                  model.Test.nimi,
                  model.Testiosa.max_pallid,
                  ]
                
        elif self.c.ositi and self.c.alatestinimi:
            li_select = [sa.func.count(model.Alatestisooritus.id),
                         ]
            li = [model.Test.aine_kood,
                  Aine_kl.nimi,
                  model.Testimiskord.aasta,
                  model.Test.id,
                  model.Test.nimi,
                  model.Alatest.max_pallid,
                  ]
        elif not self.c.yhisosa:
            li_select = [sa.func.count(model.Sooritaja.id),
                         ]
            li = [model.Test.aine_kood,
                  Aine_kl.nimi,
                  model.Testimiskord.aasta,
                  model.Test.id,
                  model.Test.nimi,
                  model.Test.max_pallid,
                  ]
        else:
            # ainult yhisosa, grupeerida iga testimiskord eraldi
            li_select = [sa.func.count(model.Sooritaja.id),
                         ]
            li = [model.Test.aine_kood,
                  Aine_kl.nimi,
                  model.Testimiskord.aasta,
                  model.Test.id,
                  model.Test.nimi,
                  model.Test.yhisosa_max_pallid,
                  ]

        Maakond = sa.orm.aliased(model.Aadresskomponent, name='maakond')
        KOV = sa.orm.aliased(model.Aadresskomponent, name='kov')
            
        # võimalikud jaotused
        join_kasutaja = join_koht = join_koolinimi = join_piirkond = join_maakond = join_kov = join_testikoht1 = False
        on_tseis = self.c.testiliik in (const.TESTILIIK_TASE, const.TESTILIIK_SEADUS)
        
        if self.c.sugu:
            self.c.n_sugu = len(li) + len(li_select)
            li.append(model.Kasutaja.sugu)
            join_kasutaja = True
        if self.c.koolityyp:
            self.c.n_koolityyp = len(li) + len(li_select)
            li.append(model.Koht.koolityyp_kood)
            join_testikoht1 = join_koht = True
        if self.c.oppekeel:
            self.c.n_oppekeel = len(li) + len(li_select)
            li.append(model.Sooritaja.oppekeel)
        if self.c.soorituskeel:
            self.c.n_soorituskeel = len(li) + len(li_select)
            li.append(model.Sooritaja.lang)
        if self.c.piirkond:
            self.c.n_piirkond = len(li) + len(li_select)
            if on_tseis:
                join_testikoht1 = True
            li.append(model.Piirkond.id)
            li.append(model.Piirkond.nimi)
            join_piirkond = True
        if self.c.maakond:
            self.c.n_maakond = len(li) + len(li_select)
            if on_tseis:
                join_testikoht1 = True
            li.append(Maakond.kood)
            li.append(Maakond.nimetus)
            join_maakond = True
        if self.c.kov:
            self.c.n_kov = len(li) + len(li_select)
            if on_tseis:
                join_testikoht1 = True
            li.append(KOV.kood)
            li.append(KOV.nimetus)
            join_kov = True
        if self.c.kursus:
            self.c.n_kursus = len(li) + len(li_select)
            li.append(model.Sooritaja.kursus_kood)
        if self.c.keeletase:
            self.c.n_keeletase = len(li) + len(li_select)
            li.append(model.Sooritaja.keeletase_kood)
        if self.c.tvaldkond:
            self.c.n_tvaldkond = len(li) + len(li_select)
            li.append(model.Sooritaja.tvaldkond_kood)
        if self.c.amet:
            self.c.n_amet = len(li) + len(li_select)
            li.append(model.Sooritaja.amet_muu)
        if self.c.haridus:
            self.c.n_haridus = len(li) + len(li_select)
            li.append(model.Sooritaja.haridus_kood)
        if self.c.tkord:
            self.c.n_tkord = len(li) + len(li_select)
            li.append(model.Testimiskord.id)
            li.append(model.Testimiskord.tahis)
        if self.c.kool:
            self.c.n_kool = len(li) + len(li_select)
            if on_tseis:
                join_testikoht1 = True
            li.append(model.Koolinimi.id)
            li.append(model.Koolinimi.nimi)
            join_koolinimi = True
            
        li_select = li_select + li
        q = model.SessionR.query(*li_select)

        # päringu tingimuste seadmine
        q = (q.join(model.Test.testimiskorrad)
             .join(model.Testimiskord.sooritajad)
             .filter(model.Sooritaja.staatus>=const.S_STAATUS_REGATUD)
             .filter(model.Test.testiliik_kood==self.c.testiliik)
             .join((Aine_kl, sa.and_(Aine_kl.klassifikaator_kood=='AINE',
                                     Aine_kl.kood==model.Test.aine_kood)))
             )

        if self.c.ositi and self.c.testiosanimi:
            q = q.join(model.Sooritaja.sooritused).\
                join(model.Sooritus.testiosa).\
                filter(model.Testiosa.nimi==self.c.testiosanimi)
        elif self.c.ositi and self.c.alatestinimi:
            q = (q.join(model.Sooritaja.sooritused)
                 .join((model.Alatestisooritus, model.Alatestisooritus.sooritus_id==model.Sooritus.id))
                 .join((model.Alatest, model.Alatest.id==model.Alatestisooritus.alatest_id))
                 .filter(model.Alatest.nimi==self.c.alatestinimi))
                
        if join_kasutaja:
            q = q.join(model.Sooritaja.kasutaja)
        if join_testikoht1:
            Sooritus1 = sa.orm.aliased(model.Sooritus)
            Testiosa1 = sa.orm.aliased(model.Testiosa)
            q = (q.join((Sooritus1, Sooritus1.sooritaja_id==model.Sooritaja.id))
                 .join((Testiosa1, sa.and_(Testiosa1.id==Sooritus1.testiosa_id,
                                           Testiosa1.seq==1)))
                 .outerjoin(Sooritus1.testikoht)
                 )
        if join_koht:
            if on_tseis:
                q = q.outerjoin(model.Testikoht.koht)
            else:
                q = q.outerjoin(model.Sooritaja.kool_koht)
        if join_koolinimi:
            if on_tseis:
                q = q.outerjoin(model.Testikoht.koolinimi)
            else:
                q = q.outerjoin(model.Sooritaja.koolinimi)
        if join_maakond:
            if on_tseis:
                kood1 = model.Testikoht.koht_aadress_kood1
            else:
                kood1 = model.Sooritaja.kool_aadress_kood1
            q = q.outerjoin((Maakond, sa.and_(Maakond.kood==kood1, Maakond.tase==1)))
        if join_kov:
            if on_tseis:
                kood2 = model.Testikoht.koht_aadress_kood2
            else:
                kood2 = model.Sooritaja.kool_aadress_kood2
            q = q.outerjoin((KOV, sa.and_(KOV.kood==kood2, KOV.tase==2)))
        if join_piirkond:
            if on_tseis:
                q = q.outerjoin(model.Testikoht.koht_piirkond)
            else:
                q = q.outerjoin(model.Sooritaja.kool_piirkond)
        if self.c.test_id:
            q = q.filter(model.Test.id==self.c.test_id)
        if self.c.keeletase_kood:
            q = q.filter(model.Test.testitasemed.any(
                model.Testitase.keeletase_kood==self.c.keeletase_kood))
        if self.c.aine:
            q = q.filter(model.Test.aine_kood==self.c.aine)

        if not self.c.aasta_alates:
            self.c.aasta_alates = self.c.aasta_kuni or date.today().year
        if not self.c.aasta_kuni:
            self.c.aasta_kuni = self.c.aasta_alates
        if self.c.aasta_alates == self.c.aasta_kuni:
            q = q.filter(model.Testimiskord.aasta==self.c.aasta_alates)
        else:
            q = q.filter(model.Testimiskord.aasta >= self.c.aasta_alates).\
                filter(model.Testimiskord.aasta <= self.c.aasta_kuni)

        q = q.group_by(*li)
        
        self.c.header = self._prepare_header()
        if self.c.csv:
            res = self._index_csv(q, 'tulemused.csv')
            if res and isinstance(res, Response):
                return res
            self.success(_("Tulemuste statistika genereerimine on käivitatud"))
            # lehe URLi ei tohi jääda csv=1, muidu satub tsyklisse
            raise HTTPFound(location=self.url_current(getargs=True, csv=None))
        
        self.c.opt_osanimed = self._opt_osanimed()
        return q

    def _order_able(self, q, field):
        """Kontrollitakse, kas antud välja järgi on võimalik sortida
        """
        if field == 'kasutaja.sugu' and not self.c.sugu:
            return False
        elif field == 'koht.koolityyp_kood' and not self.c.koolityyp:
            return False
        elif field == 'sooritaja.oppekeel' and not self.c.oppekeel:
            return False
        elif field == 'sooritaja.lang' and not self.c.soorituskeel:
            return False
        elif field == 'sooritaja.keeletase_kood' and not self.c.keeletase:
            return False                
        elif field == 'sooritaja.kursus_kood' and not self.c.kursus:
            return False                
        elif field == 'piirkond.nimi' and not self.c.piirkond:
            return False
        elif field == 'maakond.nimetus' and not self.c.maakond:
            return False
        elif field == 'kov.nimetus' and not self.c.kov:
            return False
        elif field == 'testimiskord.tahis' and not self.c.tkord:
            return False
        elif field == 'koolinimi.nimi' and not self.c.kool:
            return False
        elif field == 'sooritaja.tvaldkond_kood' and not self.c.tvaldkond:
            return False
        elif field == 'sooritaja.amet_muu' and not self.c.amet:
            return False
        elif field == 'sooritaja.haridus_kood' and not self.c.haridus:
            return False        
        elif field.startswith('alatest.'):
            return self.c.ositi and self.c.alatestinimi and not self.c.testiosanimi
        elif field.startswith('aadresskomponent.'):
            # vana versiooni otsingutingimus
            return False
        else:
            return True

    def _search_protsessid(self, q):
        alates = datetime.now() - timedelta(hours=96)
        q = (q.filter(model.Arvutusprotsess.liik==model.Arvutusprotsess.LIIK_TULEMUSTE_STATISTIKA)
             .filter(model.Arvutusprotsess.kasutaja_id==self.c.user.id)
             .filter(model.Arvutusprotsess.algus>alates)             
             )
        return q

    def _index_csv(self, q, fn='andmed.csv'):
        "Loetelu väljastamine CSV-na"

        def childfunc(protsess):
            q = self.q
            q = self._order(q)
            total = protsess and q.count() or None
            header, items = self._prepare_items(q, protsess, total)
            data = self._csv_data(header, items)
            data = utils.encode_ansi(data)
            if protsess:
                protsess.filename = fn
                protsess.filedata = data
            else:
                return utils.download(data, fn, const.CONTENT_TYPE_CSV)

        self.q = q
        liik = model.Arvutusprotsess.LIIK_TULEMUSTE_STATISTIKA
        params = {'liik': liik,
                  'kirjeldus': _("Tulemuste statistika"),
                  }
        return model.Arvutusprotsess.start(self, params, childfunc)
    
    def _prepare_header(self):
        c = self.c        

        # tabeli päis
        header = [('testimiskord.aasta', _("Aasta")),
                  ('test.nimi', _("Test")),
                  ('aine_kl.nimi', _("Õppeaine")),
                  ('test.id', _("Testi ID")),
                  ]
        if c.n_sugu:
            header.append(('kasutaja.sugu', _("Sugu")))
        if c.n_koolityyp:
            header.append(('koht.koolityyp_kood', _("Kooli tüüp")))
        if c.n_kursus:
            header.append(('sooritaja.kursus_kood', _("Kursus")))
        if c.n_keeletase:
            header.append(('sooritaja.keeletase_kood', _("Keeleoskuse tase")))
            header.append((None, _("Tasemega sooritajate osa (%)")))      
        if c.n_tvaldkond:
            header.append(('sooritaja.tvaldkond_kood', _("Töövaldkond")))
        if c.n_amet:
            #header.append(('kasutaja.amet_kood', _(u"Amet")))
            header.append(('sooritaja.amet_muu', _("Amet")))
        if c.n_haridus:
            header.append(('sooritaja.haridus_kood', _("Haridus")))
        if c.n_oppekeel:
            header.append(('sooritaja.oppekeel', _("Õppekeel")))
        if c.n_soorituskeel:
            header.append(('sooritaja.lang', _("Soorituskeel")))
        if c.n_piirkond:
            header.append(('piirkond.nimi', _("Piirkond")))
        if c.n_maakond:
            header.append(('maakond.nimetus', _("Maakond")))
        if c.n_kov:
            header.append(('kov.nimetus', _("KOV")))            
        if c.n_tkord:
            header.append(('testimiskord.tahis', _("Testimiskord")))
        if c.n_kool:
            header.append(('koolinimi.nimi', _("Õppeasutus")))

        if c.col_regatud:
            header.append((None, _("Registreeritud")))
        if c.col_puudus:
            header.append((None, _("Puudus")))
        if c.col_kais:
            header.append((None, _("Käis")))
        if c.col_eksaminandid:
            header.append((None, _("Eksaminandid")))
        if c.col_maxpallid:
            if c.ositi and c.testiosanimi:
                header.append(('testiosa.max_pallid', _("Max võimalik pallide arv")))
            elif c.ositi and c.alatestinimi:
                header.append(('alatest.max_pallid', _("Max võimalik pallide arv")))
            else:
                header.append(('test.max_pallid', _("Max võimalik pallide arv")))
        if c.col_keskmine:
            header.append((None, _("Keskmine")))
        if c.col_keskminepr:
            header.append((None, _("Keskmine (%)")))
        if c.col_mediaan:
            header.append((None, _("Mediaan")))
        if c.col_halve:
            header.append((None, _("St hälve")))
        if c.col_alla20:
            header.append((None, _("Kuni {p}% pallidest").format(p=c.alla)))
        if c.col_alla20pr:
            header.append((None, _("Kuni {p}% pallidest (%)").format(p=c.alla)))
        if c.col_minsaajad:
            header.append((None, _("Min punktide saajad")))
        if c.col_maxsaajad:
            header.append((None, _("Max punktide saajad")))
        if c.col_min:
            header.append((None, _("Min")))
        if c.col_max:
            header.append((None, _("Max")))
        if c.col_yle80:
            header.append((None, _("Vähemalt {p}% pallidest").format(p=c.yle)))
        if c.col_yle80pr:
            header.append((None, _("Vähemalt {p}% pallidest (%)").format(p=c.yle)))

        if c.col_edukus_pt:
            header.append((None, _("Edukus")))
        if c.col_edukus_pr:
            header.append((None, _("Edukuse %")))

        if c.col_kvaliteet_pt:
            header.append((None, _("Kvaliteet")))
        if c.col_kvaliteet_pr:
            header.append((None, _("Kvaliteedi %")))

        if c.testiliik in (const.TESTILIIK_TASE, const.TESTILIIK_SEADUS) and not c.ositi:
            header.append((None, _("Sooritanute arv")))
            header.append((None, _("Sooritanute %")))

        return header

    def _prepare_items(self, q, protsess, total):
        "Loetelu ridade andmete väljastamine (CSV jaoks)"
        header = self._prepare_header()
        items = []
        for n, rcd in enumerate(q.all()):
            items.append(self._prepare_item(rcd, n))
            if protsess:
                protsent = round(n / total * 98)
                if protsent != protsess.edenemisprotsent:
                    protsess.edenemisprotsent = protsent
                    model.Session.commit()
        return header, items
    
    def _prepare_item(self, rcd, n):
        "Rea moodustamine CSV jaoks"
        row, d_url = self._prepare_row(rcd)
        return row
    
    def _prepare_row(self, rcd):        
        "Tabeli ühe rea väljade kokkupanek"
        c = self.c
        h = self.h
        
        regatud = rcd[0]
        aine = rcd[1]
        aine_nimi = rcd[2]
        aasta = rcd[3]
        test_id = rcd[4]
        test_nimi = rcd[5]
        max_pallid = rcd[6]

        sugu = c.n_sugu and rcd[c.n_sugu]
        koolityyp = c.n_koolityyp and rcd[c.n_koolityyp]
        oppekeel = c.n_oppekeel and rcd[c.n_oppekeel]
        soorituskeel = c.n_soorituskeel and rcd[c.n_soorituskeel]        
        piirkond_id = c.n_piirkond and rcd[c.n_piirkond] or None
        piirkond_nimi = c.n_piirkond and rcd[c.n_piirkond+1]
        maakond_kood = c.n_maakond and rcd[c.n_maakond]
        maakond_nimi = c.n_maakond and rcd[c.n_maakond+1]
        kov_kood = c.n_kov and rcd[c.n_kov]
        kov_nimi = c.n_kov and rcd[c.n_kov+1]        
        tkord_id = c.n_tkord and rcd[c.n_tkord]
        tkord_tahis = c.n_tkord and rcd[c.n_tkord+1]
        koolinimi_id = c.n_kool and rcd[c.n_kool]
        kool_nimi = c.n_kool and rcd[c.n_kool+1]
        kursus = c.n_kursus and rcd[c.n_kursus]
        keeletase = c.n_keeletase and rcd[c.n_keeletase]
        tvaldkond = c.n_tvaldkond and rcd[c.n_tvaldkond]
        amet = c.n_amet and rcd[c.n_amet]
        haridus = c.n_haridus and rcd[c.n_haridus]

        qry = Query(self, aasta, test_id, max_pallid, sugu, koolityyp, oppekeel, soorituskeel,
                    piirkond_id, maakond_kood, kov_kood, tkord_id, koolinimi_id, kursus, keeletase,
                    tvaldkond, amet, haridus)

        total, res_avg, res_stddev, res_min, res_max, res_avg_pr = qry.query_avg()
        q_koik, q_koiktasemed = qry._gen_query([sa.func.count(model.Sooritaja.id)])
        q = q_koik.filter(model.Sooritaja.staatus==const.S_STAATUS_TEHTUD)
        #model.log_query(q_koik)
        
        row = [aasta,
               test_nimi,
               aine_nimi,
               test_id,
               ]
        if c.n_sugu:
            row.append(rcd[c.n_sugu])
        if c.n_koolityyp:
            row.append(model.Klrida.get_str('KOOLITYYP', koolityyp))
        if c.n_kursus:
            row.append(model.Klrida.get_str('KURSUS', kursus, ylem_kood=aine))
        if c.n_keeletase:
            cnt_koik = q_koiktasemed.filter(model.Sooritaja.staatus==const.S_STAATUS_TEHTUD).scalar()
            cnt_tase = q.scalar()
            if cnt_koik:
                pr_tase = cnt_tase * 100 / cnt_koik
            else:
                pr_tase = None
            row.append(model.Klrida.get_str('KEELETASE', keeletase, ylem_kood=aine))            
            row.append(h.fstr(pr_tase,2))
        if c.n_tvaldkond:
            row.append(model.Klrida.get_str('TVALDKOND', tvaldkond))
        if c.n_amet:
            #row.append(model.Klrida.get_str('AMET', amet))
            row.append(amet)
        if c.n_haridus:
            row.append(model.Klrida.get_str('HARIDUS', haridus))
            
        if c.n_oppekeel:
            row.append(const.EHIS_LANG_NIMI.get(oppekeel))
        if c.n_soorituskeel:
            row.append(model.Klrida.get_lang_nimi(soorituskeel))            
        if c.n_piirkond:
            row.append(piirkond_nimi)
        if c.n_maakond:
            row.append(maakond_nimi)
        if c.n_kov:
            row.append(kov_nimi)
        if c.n_tkord:
            row.append(tkord_tahis)
        if c.n_kool:
            row.append(kool_nimi)

        if c.col_regatud:
            row.append(regatud)
        if c.col_puudus:
            puudunud = q_koik.filter(model.Sooritaja.staatus==const.S_STAATUS_PUUDUS).scalar()
            row.append(puudunud)
        if c.col_kais:
            s_kainud = (const.S_STAATUS_TEHTUD,
                        const.S_STAATUS_KATKESTATUD,
                        const.S_STAATUS_KATKESPROT,
                        const.S_STAATUS_EEMALDATUD)
            kainud = q_koik.filter(model.Sooritaja.staatus.in_(s_kainud)).scalar()
            row.append(kainud)

        if c.col_eksaminandid:
            row.append(total)
        if c.col_maxpallid:
            row.append(h.fstr(max_pallid))
        if c.col_keskmine:
            row.append(h.fstr(res_avg))
        if c.col_keskminepr:
            if res_avg_pr is None and max_pallid:
                try:
                    res_avg_pr = res_avg*100./max_pallid
                except:
                    res_avg_pr = None
            row.append(h.fstr(res_avg_pr,2))
        if c.col_mediaan:
            mediaan = qry.query_mediaan()
            row.append(h.fstr(mediaan))            
        if c.col_halve:
            row.append(h.fstr(res_stddev))

        if c.col_alla20 or c.col_alla20pr:
            allap, allapr = qry.query_min(q, self.c.alla, total)
            if c.col_alla20:
                row.append(allap)
            if c.col_alla20pr:
                row.append(h.fstr(allapr,2))

        if c.col_minsaajad:
            diff = 1e-12
            cnt0p = q.filter(qry.field_pallid < diff).scalar()
            row.append(cnt0p)
            
        if c.col_maxsaajad:
            if max_pallid is not None:
                diff = 1e-12
                cnt100p = q.filter(qry.field_pallid > max_pallid - diff).scalar()
                #model.log_query(q.filter(qry.field_pallid > max_pallid - diff))
            else:
                cnt100p = None
            row.append(cnt100p)

        if c.col_min:
            row.append(h.fstr(res_min))
        if c.col_max:
            row.append(h.fstr(res_max))

        if c.col_yle80 or c.col_yle80pr:
            ylep, ylepr = qry.query_max(q, self.c.yle, total)
            if c.col_yle80:
                row.append(ylep)
            if c.col_yle80pr:
                row.append(h.fstr(ylepr,2))

        if c.col_edukus_pt or c.col_edukus_pr:
            ylep, ylepr = qry.query_max(q, 49.995, total)            
            if c.col_edukus_pt:
                row.append(ylep)
            if c.col_edukus_pr:
                row.append(h.fstr(ylepr,2))            

        if c.col_kvaliteet_pt or c.col_kvaliteet_pr:
            ylep, ylepr = qry.query_max(q, 74.995, total)            
            if c.col_kvaliteet_pt:
                row.append(ylep)
            if c.col_kvaliteet_pr:
                row.append(h.fstr(ylepr,2))            

        if self.c.testiliik in (const.TESTILIIK_TASE, const.TESTILIIK_SEADUS) and not self.c.ositi:
            cnt_piisav = q.filter(model.Sooritaja.tulemus_piisav==True).scalar()            
            row.append(cnt_piisav)
            if total:
                cnt_piisav_pr = cnt_piisav * 100./total
            else:
                cnt_piisav_pr = None
            row.append(h.fstr(cnt_piisav_pr,2))

        if max_pallid is None or not total:
            d_url = None
        else:
            d_url = self.url('statistika_tulemused',
                             sub='jaotus', 
                             aasta=aasta,
                             testiliik=c.testiliik,
                             test_id=test_id, 
                             sugu=sugu, 
                             koolityyp=koolityyp, 
                             oppekeel=oppekeel,
                             soorituskeel=soorituskeel,
                             piirkond_id=piirkond_id, 
                             maakond_kood=maakond_kood,
                             kov_kood=kov_kood,
                             kord_id=tkord_id,
                             koolinimi_id=koolinimi_id or c.n_kool and '-',
                             ositi=c.ositi,
                             yhisosa=c.yhisosa,
                             testiosanimi=c.testiosanimi,
                             alatestinimi=c.alatestinimi,
                             kursus=kursus,
                             keeletase=keeletase,
                             tvaldkond=tvaldkond,
                             amet=amet,
                             haridus=haridus)

        return row, d_url

    def _index_jaotus(self):
        """Jaotuste dialoogiaken"""
        self.form = Form(self.request, schema=self._SEARCH_FORM, method='GET')
        self.form.validate()
        self._copy_search_params(self.form.data)
        c = self.c
        
        q = model.SessionR.query(sa.func.count(model.Sooritaja.id))
        q = q.filter(model.Sooritaja.hindamine_staatus!=const.H_STAATUS_TOOPUUDU)

        test = yhisosa = None
        q = q.join(model.Sooritaja.testimiskord).\
            filter(model.Sooritaja.staatus==const.S_STAATUS_TEHTUD).\
            filter(model.Sooritaja.hindamine_staatus==const.H_STAATUS_HINNATUD).\
            filter(model.Testimiskord.aasta==self.c.aasta)

        test = model.Test.get(self.c.test_id)
        q = q.filter(model.Testimiskord.test_id==self.c.test_id)
        if self.c.kord_id:
            q = q.filter(model.Testimiskord.id==self.c.kord_id)

        join_koht = join_koolinimi = join_testikoht1 = join_kasutaja = False
        on_tseis = test.on_tseis
        
        if self.c.sugu:
            q = q.join(model.Sooritaja.kasutaja).\
                filter(model.Kasutaja.sugu==self.c.sugu)
        if self.c.koolityyp:
            q = q.filter(model.Koht.koolityyp_kood==self.c.koolityyp)
            join_koht = True
            if on_tseis:
                join_testikoht1 = True
        if self.c.oppekeel:
            q = q.filter(model.Sooritaja.oppekeel==self.c.oppekeel)
        if self.c.soorituskeel:
            q = q.filter(model.Sooritaja.lang==self.c.soorituskeel)            
        if self.c.kursus:
            q = q.filter(model.Sooritaja.kursus_kood==self.c.kursus)
        if self.c.keeletase:
            q = q.filter(model.Sooritaja.keeletase_kood==self.c.keeletase)
        if self.c.tvaldkond:
            q = q.filter(model.Sooritaja.tvaldkond_kood==self.c.tvaldkond)
        if self.c.amet:
            q = q.filter(model.Sooritaja.amet_kood==self.c.amet)
        if self.c.haridus:
            q = q.filter(model.Sooritaja.haridus_kood==self.c.haridus)            
            
        if self.c.piirkond_id:
            if on_tseis:
                q = q.filter(model.Testikoht.koht_piirkond_id==self.c.piirkond_id)
                join_testikoht1 = True
            else:
                q = q.filter(model.Sooritaja.kool_piirkond_id==self.c.piirkond_id)

        if self.c.maakond_kood:
            if on_tseis:
                q = q.filter(model.Testikoht.koht_aadress_kood1==self.c.maakond_kood)
                join_testikoht1 = True
            else:
                q = q.filter(model.Sooritaja.kool_aadress_kood1==self.c.maakond_kood)
        if self.c.kov_kood:
            if on_tseis:
                q = q.filter(model.Testikoht.koht_aadress_kood2==self.c.kov_kood)
                join_testikoht1 = True
            else:
                q = q.filter(model.Sooritaja.kool_aadress_kood2==self.c.kov_kood)

        if self.c.koht_id:
            if self.c.koht_id == '-':
                self.c.koht_id = None
            q = q.filter(model.Koht.id==self.c.koht_id)
            join_koht = True

        field = model.Sooritaja.pallid
            
        if self.c.ositi and self.c.testiosanimi:
            max_pallid = test.max_pallid
            testiosa = model.Testiosa.query.\
                filter(model.Testiosa.test_id==test.id).\
                filter(model.Testiosa.nimi==self.c.testiosanimi).\
                first()
            if testiosa:
                field = model.Sooritus.pallid
                q = q.join(model.Sooritaja.sooritused).\
                    filter(model.Sooritus.testiosa_id==testiosa.id)
                max_pallid = testiosa.max_pallid

        elif self.c.ositi and self.c.alatestinimi:
            max_pallid = test.max_pallid
            alatest = model.Alatest.query.\
                filter(model.Alatest.nimi==self.c.alatestinimi).\
                join(model.Alatest.testiosa).\
                filter(model.Testiosa.test_id==test.id).\
                first()
            if alatest:
                field = model.Alatestisooritus.pallid
                q = (q.join(model.Sooritaja.sooritused)
                     .join((model.Alatestisooritus, model.Alatestisooritus.sooritus_id==model.Sooritus.id))
                     .filter(model.Alatestisooritus.alatest_id==alatest.id))
                max_pallid = alatest.max_pallid
        elif self.c.yhisosa:
            field = model.Sooritaja.yhisosa_pallid
            max_pallid = test.yhisosa_max_pallid
        else:
            max_pallid = test.max_pallid

        if join_testikoht1:
            Sooritus1 = sa.orm.aliased(model.Sooritus)
            Testiosa1 = sa.orm.aliased(model.Testiosa)
            q = (q.join((Sooritus1, Sooritus1.sooritaja_id==model.Sooritaja.id))
                 .join((Testiosa1, sa.and_(Testiosa1.id==Sooritus1.testiosa_id,
                                           Testiosa1.seq==1)))
                 .outerjoin(Sooritus1.testikoht)
                 )
        if join_koht:
            if on_tseis:
                q = q.outerjoin(model.Testikoht.koht)
            else:
                q = q.outerjoin(model.Sooritaja.kool_koht)
        if join_koolinimi:
            if on_tseis:
                q = q.outerjoin(model.Testikoht.koolinimi)
            else:
                q = q.outerjoin(model.Sooritaja.koolinimi)
        if join_kasutaja:
            q = q.join(model.Sooritaja.kasutaja)

        total = 0
        x_labels = []
        values = []
        diff = .5 + 1e-12
        if max_pallid > 110:
            step = 10
        else:
            step = 5
        range_begin = 0
        while range_begin < max_pallid:
            range_end = range_begin + step
            if range_end + .00001 < max_pallid:
                q1 = q.filter(field <= range_end - diff)
                s_range_end = range_end - 1
            else:
                q1 = q
                s_range_end = max_pallid
            if range_begin > 0:
                q1 = q1.filter(field > range_begin - diff)
            cnt = q1.scalar()
            total += cnt
            range_title = '%s-%s' % (self.h.fstr(range_begin),
                                     self.h.fstr(s_range_end))
            x_labels.append(range_title)
            values.append(cnt)
            range_begin = range_end

        x_len = len(values)
        if total:
            prot = [self.h.fstr(n*100/total,1) for n in values]
            texts = [f'{values[i]} ({prot[i]}%)' for i in range(x_len)]
        else:
            prot = ['' for n in values]
            texts = [f'{values[i]}' for i in range(x_len)]
        c.items = [(x_labels[i], values[i], prot[i]) for i in range(x_len)]

        if values:
            max_y = max(values)
        else:
            # sooritajaid pole, aga kuvame skaalal sooritajate arvu 0-100
            max_y = 100
        dtick = utils.scale_step(max_y)
        y = 0
        tickvals = []
        while y <= max_y:
            tickvals.append(y)
            y += dtick
        
        data = [go.Bar(name='',
                       x=x_labels,
                       y=values,
                       text=texts,
                       hovertemplate="%{x} - %{y}"
                       )
                       ]
        fig = go.Figure(data)
        fig.update_layout(xaxis_title=_("Tulemus"),
                          yaxis_title=_("Sooritajate arv"),
                          yaxis={'tickvals': tickvals},
                          margin=dict(l=5, r=5, t=2, b=2))
        c.json_data = fig.to_json()

        html = self.form.render('ekk/statistika/tulemused.jaotus.mako',
                                extra_info=self.response_dict)            

        return Response(html)

    def _get_pallid_field(self):
        "Milliselt väljalt loetakse tulemuse pallid"
        if self.c.ositi and self.c.testiosanimi:
            field = model.Sooritus.pallid
            field_pr = model.Sooritus.tulemus_protsent
            field_cnt = model.Sooritus.id
        elif self.c.ositi and self.c.alatestinimi:
            field = model.Alatestisooritus.pallid
            field_pr = model.Alatestisooritus.tulemus_protsent
            field_cnt = model.Alatestisooritus.id
        elif self.c.yhisosa:
            field = model.Sooritaja.yhisosa_pallid
            field_pr = None
            field_cnt = model.Sooritaja.id
        else:
            field = model.Sooritaja.pallid
            field_pr = model.Sooritaja.tulemus_protsent
            field_cnt = model.Sooritaja.id
        return field, field_pr, field_cnt
    
    def _index_keskmised(self):
        """Keskmise tulemuse diagramm aastate lõikes"""
        self.form = Form(self.request, schema=self._SEARCH_FORM, method='GET')
        self.form.validate()
        self._copy_search_params(self.form.data)

        li = [model.Testimiskord.aasta,
              model.Test.aine_kood,
              ]

        field, field_pr, field_cnt = self._get_pallid_field()
        li_select = [sa.func.avg(field)] + li

        q = (model.SessionR.query(*li_select)
             .join(model.Sooritaja.testimiskord)
             .join(model.Testimiskord.test)
             .filter(model.Sooritaja.staatus==const.S_STAATUS_TEHTUD)
             .filter(model.Sooritaja.hindamine_staatus==const.H_STAATUS_HINNATUD)
             .filter(model.Test.testiliik_kood==self.c.testiliik))

        if self.c.ositi and self.c.testiosanimi:
            q = (q.join(model.Sooritaja.sooritused)
                 .join(model.Sooritus.testiosa)
                 .filter(model.Testiosa.nimi==self.c.testiosanimi))
        elif self.c.ositi and self.c.alatestinimi:
            q = (q.join(model.Sooritaja.sooritused)
                 .join((model.Alatestisooritus, model.Alatestisooritus.sooritus_id==model.Sooritus.id))
                 .join((model.Alatest, model.Alatest.id==model.Alatestisooritus.alatest_id))
                 .filter(model.Alatest.nimi==self.c.alatestinimi))
    
        if self.c.aine:
            q = q.filter(model.Test.aine_kood==self.c.aine)
        if self.c.aasta_alates:
            q = q.filter(model.Testimiskord.aasta>=self.c.aasta_alates)
        if self.c.aasta_kuni:
            q = q.filter(model.Testimiskord.aasta<=self.c.aasta_kuni)
        if self.c.test_id:
            q = q.filter(model.Test.id==self.c.test_id)
        if self.c.keeletase:
            q = q.filter(model.Sooritaja.keeletase_kood==self.c.keeletase)

        q = q.group_by(*li).\
            order_by(model.Testimiskord.aasta)

        # kogume andmed ainete kaupa
        datasets = defaultdict(dict)
        all_x = []
        for rcd in q.all():
            avg = rcd[0]
            aasta = rcd[1]
            aine = rcd[2]
            datasets[aine][aasta] = avg
            all_x.append(aasta)

        fig = go.Figure()
        if datasets:
            years = list(range(min(all_x), max(all_x) + 2))
            for aine_kood in datasets:
                # igale ainele eraldi joon 
                aine_nimi = model.Klrida.get_str('AINE', aine_kood)
                values = [datasets[aine_kood].get(x) for x in years]
                line = go.Scatter(x=years, y=values, name=aine_nimi)
                fig.add_trace(line)
            fig.update_layout(xaxis_title=_("Aastad"),
                              yaxis_title=_("Keskmine tulemus"),
                              xaxis={'tickvals': years},
                              margin=dict(l=5, r=5, t=2, b=2))
        
        self.c.json_data = fig.to_json()
        html = self.form.render('ekk/statistika/tulemused.keskmised.mako',
                                extra_info=self.response_dict)            

        return Response(html)

    def _opt_osanimed(self):
        if (not self.c.aine or not self.c.testiliik) and not self.c.test_id:
            return []
        q = model.SessionR.query(model.Testiosa.nimi, model.Alatest.nimi).distinct().\
            outerjoin(model.Testiosa.alatestid).\
            join(model.Testiosa.test)
        if self.c.test_id:
            q = q.filter(model.Test.id==self.c.test_id)
        else:
            q = q.filter(model.Test.aine_kood==self.c.aine).\
                filter(model.Test.testiliik_kood==self.c.testiliik)
        if self.c.keeletase:
            q = q.filter(model.Test.testitasemed.any(model.Testitase.keeletase_kood==self.c.keeletase))
        if not self.c.aasta_alates:
            self.c.aasta_alates = self.c.aasta_kuni or date.today().year
        if not self.c.aasta_kuni:
            self.c.aasta_kuni = self.c.aasta_alates
        if self.c.aasta_alates == self.c.aasta_kuni:
            q = q.filter(model.Test.testimiskorrad.any(model.Testimiskord.aasta==self.c.aasta_alates))
        else:
            q = q.filter(model.Test.testimiskorrad.any(\
                        sa.and_(model.Testimiskord.aasta >= self.c.aasta_alates,
                                model.Testimiskord.aasta <= self.c.aasta_kuni)))
        li = []
        for testiosa_nimi, alatest_nimi in q.all():
            if alatest_nimi:
                li.append(('a.%s' % alatest_nimi, '%s (alatest)' % alatest_nimi))
            elif testiosa_nimi:
                li.append(('o.%s' % testiosa_nimi, '%s (testiosa)' % testiosa_nimi))
        li.sort(key=lambda x: x[1])
        return li
            
    def _index_osanimed(self):
        self.form = Form(self.request, schema=self._SEARCH_FORM, method='GET')
        if self.form.validate():
            self._copy_search_params(self.form.data, save=False)
            li = self._opt_osanimed()
        else:
            li = []
        data = [{'id':a[0],'value':a[1]} for a in li]
        return Response(json_body=data)

class Query(object):
    "Päringu objekt, vastab tulemuste loetelu yhele reale, sisaldab reale vastava grupi tingimusi"
    def __init__(self,
                 handler,
                 aasta,
                 test_id,
                 max_pallid,
                 sugu,
                 koolityyp,
                 oppekeel,
                 soorituskeel,
                 piirkond_id,
                 maakond_kood,
                 kov_kood,
                 tkord_id,
                 koolinimi_id,
                 kursus,
                 keeletase,
                 tvaldkond,
                 amet,
                 haridus):
        self.handler = handler
        c = handler.c
        self.aasta = aasta
        self.test_id = test_id
        self.max_pallid = max_pallid
        self.sugu = sugu
        self.koolityyp = koolityyp
        self.oppekeel = oppekeel
        self.soorituskeel = soorituskeel
        self.piirkond_id = piirkond_id
        self.maakond_kood = maakond_kood
        self.kov_kood = kov_kood
        self.tkord_id = tkord_id
        self.koolinimi_id = koolinimi_id
        self.kursus = kursus
        self.keeletase = keeletase
        self.tvaldkond = tvaldkond
        self.amet = amet
        self.haridus = haridus

    def _gen_query(self, select_fields):
        "Sooritajate arv ja keskmine tulemus"
        q = (model.SessionR.query(*select_fields)
             .join(model.Sooritaja.testimiskord)
             .filter(model.Testimiskord.aasta==self.aasta)
             .filter(model.Sooritaja.hindamine_staatus!=const.H_STAATUS_TOOPUUDU)
             .filter(model.Sooritaja.staatus>=const.S_STAATUS_REGATUD)
             )

        join_koht = join_koolinimi = join_kasutaja = join_testikoht1 = False
        
        c = self.handler.c
        on_tseis = c.testiliik in (const.TESTILIIK_TASE, const.TESTILIIK_SEADUS)
        
        q = q.filter(model.Testimiskord.test_id==self.test_id)
        if c.n_sugu:
            q = q.join(model.Sooritaja.kasutaja).\
                filter(model.Kasutaja.sugu==self.sugu)
        if c.n_koolityyp:
            q = q.filter(model.Koht.koolityyp_kood==self.koolityyp)
            join_koht = True
        if c.n_oppekeel:
            q = q.filter(model.Sooritaja.oppekeel==self.oppekeel)
        if c.n_soorituskeel:
            q = q.filter(model.Sooritaja.lang==self.soorituskeel)            
        if c.n_kursus:
            q = q.filter(model.Sooritaja.kursus_kood==self.kursus)
        if c.n_tkord:
            q = q.filter(model.Testimiskord.id==self.tkord_id)
        if c.n_kool:
            join_koolinimi = True
            q = q.filter(model.Koolinimi.id==self.koolinimi_id)
            #join_koht = True
            #q = q.filter(model.Koht.id==self.kool_id)
        if c.n_tvaldkond:
            #join_kasutaja = True
            q = q.filter(model.Sooritaja.tvaldkond_kood==self.tvaldkond)
        if c.n_amet:
            #join_kasutaja = True
            q = q.filter(model.Sooritaja.amet_kood==self.amet)
        if c.n_haridus:
            #join_kasutaja = True
            q = q.filter(model.Sooritaja.haridus_kood==self.haridus)            

        if c.ositi and c.testiosanimi:
            self.field_pallid = model.Sooritus.pallid
            self.field_protsent = model.Sooritus.tulemus_protsent
            q = q.join(model.Sooritaja.sooritused).\
                join(model.Sooritus.testiosa).\
                filter(model.Testiosa.nimi==c.testiosanimi)
        elif c.ositi and c.alatestinimi:
            self.field_pallid = model.Alatestisooritus.pallid
            self.field_protsent = model.Alatestisooritus.tulemus_protsent            
            q = (q.join(model.Sooritaja.sooritused)
                 .join((model.Alatestisooritus, model.Alatestisooritus.sooritus_id==model.Sooritus.id))
                 .join((model.Alatest, model.Alatest.id==model.Alatestisooritus.alatest_id))
                 .filter(model.Alatest.nimi==c.alatestinimi))
        elif c.yhisosa:
            self.field_pallid = model.Sooritaja.yhisosa_pallid
            self.field_protsent = model.Sooritaja.tulemus_protsent                        
        else:
            self.field_pallid = model.Sooritaja.pallid
            self.field_protsent = model.Sooritaja.tulemus_protsent

        if on_tseis and (c.n_piirkond or c.n_maakond or c.n_kov or join_koht or join_koolinimi):
            # join testikoht1
            Sooritus1 = sa.orm.aliased(model.Sooritus)
            Testiosa1 = sa.orm.aliased(model.Testiosa)
            q = (q.join((Sooritus1, Sooritus1.sooritaja_id==model.Sooritaja.id))
                 .join((Testiosa1, sa.and_(Testiosa1.id==Sooritus1.testiosa_id,
                                           Testiosa1.seq==1)))
                 .outerjoin(Sooritus1.testikoht)
                 )
        if c.n_piirkond:
            if on_tseis:
                q = q.filter(model.Testikoht.koht_piirkond_id==self.piirkond_id)
            else:
                q = q.filter(model.Sooritaja.kool_piirkond_id==self.piirkond_id)
        if c.n_maakond:
            if on_tseis:
                q = q.filter(model.Testikoht.koht_aadress_kood1==self.maakond_kood)
            else:
                q = q.filter(model.Sooritaja.kool_aadress_kood1==self.maakond_kood)
        if c.n_kov:
            if on_tseis:
                q = q.filter(model.Testikoht.koht_aadress_kood2==self.kov_kood)
            else:
                q = q.filter(model.Sooritaja.kool_aadress_kood2==self.kov_kood)
        if join_koht:
            if on_tseis:
                q = q.outerjoin(model.Testikoht.koht)
            else:
                q = q.outerjoin(model.Sooritaja.kool_koht)
        if join_koolinimi:
            if on_tseis:
                q = q.outerjoin(model.Testikoht.koolinimi)
            else:
                q = q.outerjoin(model.Sooritaja.koolinimi)
        if join_kasutaja:
            q = q.join(model.Sooritaja.kasutaja)
            
        q_koiktasemed = q
        if c.n_keeletase:
            q = q.filter(model.Sooritaja.keeletase_kood==self.keeletase)            

        return q, q_koiktasemed

    def query_avg(self):
        "Tehtud soorituste arv, keskmine, standardhälve, min ja max pallid"
        field, field_pr, field_cnt = self.handler._get_pallid_field()        
        fields = [sa.func.count(field_cnt),
                  sa.func.avg(field),
                  sa.func.stddev(field),
                  sa.func.min(field),
                  sa.func.max(field),
                  sa.func.avg(field_pr or field)]
        q, qk = self._gen_query(fields)
        q = (q.filter(model.Sooritaja.staatus==const.S_STAATUS_TEHTUD)
             .filter(model.Sooritaja.hindamine_staatus==const.H_STAATUS_HINNATUD))
        total = res_min = res_max = 0
        res_avg = res_stddev = None
        #model.log_query(q)
        for rcd in q.all():
            total, res_avg, res_stddev, res_min, res_max, res_avg_pr = rcd
        if not field_pr:
            res_avg_pr = None
        return total, res_avg, res_stddev, res_min, res_max, res_avg_pr

    def query_max(self, q, protsent, total):
        "Vähemalt etteantud arvu punkti saanute arv"
        cnt = cntpr = None
        if self.max_pallid is not None:
            diff = 1e-12
            #cnt = q.filter(self.field_pallid > self.max_pallid * protsent/100. - diff).scalar()
            cnt = q.filter(self.field_protsent > protsent - diff).scalar()
            if cnt is not None and total:
                cntpr = cnt * 100./total
        return cnt, cntpr

    def query_min(self, q, protsent, total):
        "Min punktide saajate arv"
        cnt = cntpr = None
        if self.max_pallid is not None:
            diff = 1e-12
            #cnt = q.filter(self.field_pallid < self.max_pallid * protsent/100. + diff).scalar()
            cnt = q.filter(self.field_protsent < protsent + diff).scalar()            
            if cnt is not None and total:
                cntpr = cnt * 100./total
        return cnt, cntpr

    def query_mediaan(self):
        "Tulemuse mediaan"
        # alates PostgreSQL v9.4 on olemas percentile_cont()
        select_field = self.field_pallid
        q, qkt = self._gen_query([select_field])
        q = (q.filter(model.Sooritaja.staatus==const.S_STAATUS_TEHTUD)
             .filter(model.Sooritaja.hindamine_staatus==const.H_STAATUS_HINNATUD))            
        sql = "WITH t(value) AS (" + model.str_query(q) + ") SELECT percentile_cont(0.5) WITHIN GROUP (ORDER BY value) FROM t"
        #log.info(sql)
        qm = model.SessionR.execute(sa.text(sql))
        return qm.scalar()
    
