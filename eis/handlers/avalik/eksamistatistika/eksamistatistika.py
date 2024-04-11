import math
import plotly.graph_objects as go
from eis.lib.baseresource import *
_ = i18n._
log = logging.getLogger(__name__)

TESTITYYP_R1 = 'r1' # riigieksamid, mitte-võõrkeeled
TESTITYYP_R2 = 'r2' # riigieksamid, võõrkeeled
TESTITYYP_T3 = 't3' # tasemetöö 3. klass
TESTITYYP_T6 = 't6' # tasemetöö 6. klass

MIN_AASTA = 2015

class EksamistatistikaController(BaseResourceController):
    """Eksamite tulemuste statistika
    """
    _permission = 'lahendamine'
    _INDEX_TEMPLATE = 'avalik/eksamistatistika/otsing.mako'
    _LIST_TEMPLATE = 'avalik/eksamistatistika/otsing_list.mako'
    _DEFAULT_SORT = 'test.nimi,sooritaja.kursus_kood,-testimiskord.aasta,aadresskomponent.nimetus,koolinimi.nimi'
    _ignore_default_params = ['csv']
    _SEARCH_FORM = forms.avalik.eksamistatistika.EksamistatistikaForm
    _authorize = False
    _sort_options = ('kasutaja.sugu',
                     'koht.koolityyp_kood',
                     'koolinimi.nimi',
                     'aadresskomponent.nimetus',
                     'sooritaja.oppekeel',
                     'sooritaja.lang',
                     'sooritaja.keeletase_kood',
                     'sooritaja.oppevorm_kood',
                     'sooritaja.oppevorm_kood',
                     'testimiskord.aasta',
                     'test.nimi',
                     'sooritaja.kursus_kood',
                     'test.id',
                     'test.testiliik_kood',
                     'test.max_pallid',
                     )
    _actions = 'index'
    _no_paginate = True
    # kas testimiskorrad peavad olema avalikus vaates avaldatud
    avalik = True

    def _query(self):
        c = self.c
        c.rv_rows = [] # rv tunnistuste päringu tulemused

        c.opt_aasta = [(year, year) for year in range(date.today().year, MIN_AASTA-1, -1)]
        c.opt_testityyp = [
            (const.TESTILIIK_TASEMETOO, _("Tasemetööd")),
            (const.TESTILIIK_POHIKOOL, _("Põhikooli lõpueksamid")),
            (TESTITYYP_R1, _("Riigieksamid")),
            (TESTITYYP_R2, _("Riigieksamid (võõrkeeled)")),
            ]

        testiliigid = (const.TESTILIIK_RIIGIEKSAM,
                       const.TESTILIIK_RV,
                       const.TESTILIIK_POHIKOOL,
                       const.TESTILIIK_TASEMETOO)

        q = (model.SessionR.query(model.Test.testiliik_kood,
                                 model.Test.aine_kood,
                                 model.Testikursus.kursus_kood,
                                 model.Test.id,
                                 model.Test.nimi,
                                 model.Testimiskord.aasta)
             .distinct()
             .filter(model.Test.testiliik_kood.in_(testiliigid))
             .join(model.Test.testimiskorrad)
             .filter(model.Testimiskord.aasta>=MIN_AASTA)
             .filter(model.Testimiskord.tulemus_kinnitatud==True)
             .outerjoin((model.Testikursus,
                         sa.and_(model.Testikursus.test_id==model.Test.id,
                                 model.Testikursus.kursus_kood!=None)))
             )
        q = q.filter(model.Testimiskord.koondtulemus_avaldet==True)
        if self.avalik:
            q = q.filter(model.Testimiskord.statistika_aval_kpv!=None)
        else:
            q = q.filter(model.Testimiskord.statistika_ekk_kpv!=None)
            
        q = q.order_by(model.Test.testiliik_kood,
                       model.Test.nimi,
                       model.Testimiskord.aasta)
            
        voorkeeled = (const.AINE_EN, const.AINE_FR, const.AINE_DE, const.AINE_RU)
        #model.log_query(q)
        c.opt_data = []
        opt_test = []
        d_testid = {}
        c.testid_et2 = []
        c.testid_pet2 = []

        for tl_kood, aine, kursus, test_id, test_nimi, aasta in q.all():
            if tl_kood in (const.TESTILIIK_RIIGIEKSAM, const.TESTILIIK_RV):
                if aine in voorkeeled:
                    testityyp = TESTITYYP_R2
                else:
                    testityyp = TESTITYYP_R1
            else:
                testityyp = tl_kood

            if kursus:
                kursus_nimi = model.Klrida.get_str('KURSUS', kursus, ylem_kood=aine)
                test_nimi = '%s (%s)' % (test_nimi, kursus_nimi.lower())
                test_id = '%s-%s' % (test_id, kursus)
                
            t_id = d_testid.get(test_nimi)
            if not t_id:
                t_id = d_testid[test_nimi] = test_id
                opt_test.append((t_id, test_nimi))

                if testityyp == TESTITYYP_R1 and aine == const.AINE_ET2:
                    # eesti keel teise keelena riigieksamite ID-d
                    c.testid_et2.append(str(t_id))
                elif testityyp == const.TESTILIIK_POHIKOOL and aine == const.AINE_ET2:
                    # eesti keel teise keelena põhikooli eksamite ID-d
                    c.testid_pet2.append(str(t_id))

            item = (testityyp, aasta, t_id)
            if item not in c.opt_data:
                c.opt_data.append(item)

        c.opt_test = sorted(set(opt_test), key=lambda o: o[1])
        c.opt_kool = []

        c.opt_koolityyp = []
        for tyyp in (const.KOOLITYYP_POHIKOOL, const.KOOLITYYP_KUTSEKOOL):
            c.opt_koolityyp.append((tyyp, model.Klrida.get_str('KOOLITYYP', tyyp)))

        return None

    def _index_koolopt(self):
        c = self.c
        self._copy_search_params()

        # kas on riigieksam 2022 või hilisem avalikus vaates
        # ja ei või koolide kaupa kuvada
        c.is_r2022 = self.is_r2022eis(c.test_id, c.aasta)

        # data on tuple: (opt_mk, opt_kov, opt_kool)
        data = self._get_koolopt()
        opt_mk = []
        for r in data[0]:
            opt_mk.append({'id': r[0],
                           'value': r[1],
                           })
        opt_kov = []
        for r in data[1]:
            opt_kov.append({'id': r[0],
                            'value': r[1],
                            'data-kood1': r[2].get('data-kood1'),
                            })
        opt_kool = []
        for r in data[2]:
            opt_kool.append({'id': r[0],
                             'value': r[1],
                             'data-kood1': r[2].get('data-kood1'),
                             'data-kood2': r[2].get('data-kood2'),
                             })
        return Response(json_body=[opt_mk, opt_kov, opt_kool])

    def _get_koolopt(self):
        "Test ja õppeaasta on antud, leitakse testis osalenud koolid, maakonnad ja KOVid"
        c = self.c
        if not c.test_id or not c.aasta:
            return [], [], []
        aasta = int(c.aasta)
        test_id, kursus = self._split_test_kursus(c.test_id)
        _cache_key = ('EKSAMIKOHT', test_id, kursus, aasta)
        li = model.cache_kood.get(_cache_key)
        if not li:
            Maakond = sa.orm.aliased(model.Aadresskomponent, name='maakond')
            KOV = sa.orm.aliased(model.Aadresskomponent, name='kov')
            q = (model.SessionR.query(model.Koolinimi.id,
                                     model.Koolinimi.nimi,
                                     model.Sooritaja.kool_aadress_kood1,
                                     Maakond.nimetus_liigiga,
                                     model.Sooritaja.kool_aadress_kood2,
                                     KOV.nimetus_liigiga)
                 .distinct()
                 .join(model.Sooritaja.koolinimi)
                 .outerjoin((Maakond, sa.and_(Maakond.kood==model.Sooritaja.kool_aadress_kood1,
                                              Maakond.tase==1)))
                 .outerjoin((KOV, sa.and_(KOV.kood==model.Sooritaja.kool_aadress_kood2,
                                          KOV.tase==2)))
                 .join(model.Sooritaja.testimiskord)
                 .filter(model.Sooritaja.test_id==test_id)
                 .filter(model.Testimiskord.test_id==test_id)
                 .filter(model.Testimiskord.aasta==aasta)
                 )
            if kursus:
                q = q.filter(model.Sooritaja.kursus_kood==kursus)
            q = q.order_by(model.Koolinimi.nimi)
            li = [r for r in q.all()]

            # eraldame kolm valikuhulka (maakonnad, KOVid, koolid)
            opt_kool = []
            di_mk = {}
            di_kov = {}
            cnt_kov = {}
            for (koolinimi_id, koht_nimi, kood1, mk_nimi, kood2, kov_nimi) in li:
                r_mk = (kood1, mk_nimi)
                r_kov = (kood2, kov_nimi, 
                         {'data-kood1': kood1 or '-'})
                r_kool = (koolinimi_id, koht_nimi,
                          {'data-kood1': kood1 or '-',
                           'data-kood2': kood2 or '-'})
                di_mk[kood1] = r_mk
                di_kov[kood2] = r_kov
                opt_kool.append(r_kool)
                # koolide arv KOVis
                cnt_kov[kood2] = (cnt_kov.get(kood2) or 0) + 1

            if c.is_r2022:
                # riigieksam 2022 - ei või kuvada koolide kaupa tulemusi
                # eemaldame KOVid, milles osales vähem kui 2 kooli
                for kood2 in [kood2 for kood2, cnt in cnt_kov.items() if cnt < 2]:
                    di_kov.pop(kood2)
                # koolide valikut kasutajale ei anna
                opt_kool = []

            opt_mk = sorted(list(di_mk.values()), key=lambda r: r[1] or '')
            opt_kov = sorted(list(di_kov.values()), key=lambda r: r[1] or '')
            li = (opt_mk, opt_kov, opt_kool)
            model.cache_kood[_cache_key] = li
        return li

    def is_r2022eis(self, test_id, aasta):
        "Kas on 2022 või hilisem riigieksam, kus ei või näidata vähem kui 2 kooliga KOVide andmeid"
        return False # ES-3280 piirangu eemaldas ES-3315
        test_id, kursus = self._split_test_kursus(test_id)
        if not test_id or not aasta:
            return False
        try:
            aasta = int(aasta)
        except:
            return False
        if self.c.app_eis and aasta >= 2022:
            test = model.Test.getR(test_id)
            if test.testiliik_kood in (const.TESTILIIK_RIIGIEKSAM, const.TESTILIIK_RV):
                return True
        return False
    
    def _search_default(self, q):
        c = self.c
        c.alla = 20
        c.yle = 80
        return None

    def _search(self, q1):
        """Põhiline otsing"""
        c = self.c
        c.koolinimi_id = c.ko # välja nimi on võimalikult lyhike, et URL oleks < 2000
        cnt_mandatory = len([r for r in [c.testityyp, c.aasta, c.test_id] if r])
        if cnt_mandatory < 2:
            self.error('Palun esitada vähemalt kaks parameetrit neist kolmest: eksami tüüp, aasta, testi nimetus')
            return
        c.prepare_row = self._prepare_row

        # kas on riigieksam 2022 või hilisem avalikus vaates
        # ja ei või koolide kaupa kuvada
        c.is_r2022 = self.is_r2022eis(c.test_id, c.aasta)
        if c.is_r2022 and c.koolinimi_id:
            # riigieksam 2022 - ei või kuvada kooli järgi
            c.koolinimi_id = c.ko = ''
            c.warn_kool = True
            
        # kui kuvatakse kooli valik, siis leiame koolid valikusse
        c.opt_mk, c.opt_kov, c.opt_kool = self._get_koolopt()
            
        if not isinstance(c.alla, (int,float)):
            c.alla = 20
        if not isinstance(c.yle, (int,float)):
            c.yle = 80

        li_select = [sa.func.count(model.Sooritaja.id),
                     ]
        li = [model.Test.aine_kood,
              model.Testimiskord.aasta,
              model.Test.id,
              model.Test.nimi,
              model.Sooritaja.kursus_kood,
              model.Test.max_pallid,
              ]
        if not c.testityyp:
            c.n_testiliik = len(li) + len(li_select)
            li.append(model.Test.testiliik_kood)

        Maakond = sa.orm.aliased(model.Aadresskomponent, name='maakond')
        KOV = sa.orm.aliased(model.Aadresskomponent, name='kov')
        
        # võimalikud jaotused
        join_kasutaja = join_koht = join_koolinimi = join_piirkond = join_maakond = join_kov = False
        #join_aadress = False
        c.on_loige = False
        if cnt_mandatory == 3:
            # jaotus on lubatud ainult siis, kui on valitud testi tüüp, aasta ja eksam
            if c.sugu:
                c.n_sugu = len(li) + len(li_select)
                li.append(model.Kasutaja.sugu)
                join_kasutaja = True
                c.on_loige = True
            if c.koolityyp:
                c.n_koolityyp = len(li) + len(li_select)
                li.append(model.Koht.koolityyp_kood)
                join_koht = True
                c.on_loige = True
            if c.oppekeel:
                c.n_oppekeel = len(li) + len(li_select)
                li.append(model.Sooritaja.oppekeel)
                c.on_loige = True
            if c.soorituskeel:
                c.n_soorituskeel = len(li) + len(li_select)
                li.append(model.Sooritaja.lang)
                c.on_loige = True
            if c.maakond:
                c.n_maakond = len(li) + len(li_select)
                li.append(model.Sooritaja.kool_aadress_kood1)
                li.append(Maakond.nimetus)
                join_maakond = True
                c.on_loige = True
            if c.kov:
                c.n_kov = len(li) + len(li_select)
                li.append(model.Sooritaja.kool_aadress_kood2)
                li.append(KOV.nimetus)
                join_kov = True
                c.on_loige = True
            if c.koolinimi_id:
                # koolinimi_id asemel kasutame lyhikest väljanime, kuna kõigi valikute valimisel
                # yletab muidu URLi pikkus IE-s oleva piiri 2083
                c.n_kool = len(li) + len(li_select)
                li.append(model.Sooritaja.koolinimi_id)                
                li.append(model.Koolinimi.nimi)
                join_koolinimi = True
                c.on_loige = True
            if c.keeletase:
                c.n_keeletase = len(li) + len(li_select)
                li.append(model.Sooritaja.keeletase_kood)
                c.on_loige = True
            if c.oppevorm:
                c.n_oppevorm = len(li) + len(li_select)
                li.append(model.Sooritaja.oppevorm_kood)
                c.on_loige = True
        else:
            c.sugu = c.oppekeel = c.soorituskeel = c.maakond = c.kov = c.ko = c.koolinimi_id = c.keeletase = c.oppevorm = c.koolityyp = ''
            
        li_select = li_select + li
        q = model.SessionR.query(*li_select)

        # päringu tingimuste seadmine
        q = (q.join(model.Test.testimiskorrad)
             .filter(model.Testimiskord.tulemus_kinnitatud==True)
             .join(model.Testimiskord.sooritajad)
             .filter(model.Sooritaja.staatus>=const.S_STAATUS_REGATUD)
             )
        q = q.filter(model.Testimiskord.koondtulemus_avaldet==True)
        if self.avalik:
            q = q.filter(model.Testimiskord.statistika_aval_kpv!=None)
        else:
            q = q.filter(model.Testimiskord.statistika_ekk_kpv!=None)
             
        # eksamityyp
        testiliigid = (const.TESTILIIK_RIIGIEKSAM,
                       const.TESTILIIK_RV,
                       const.TESTILIIK_POHIKOOL,
                       const.TESTILIIK_TASEMETOO)
        if c.testityyp:
            voorkeeled = (const.AINE_EN, const.AINE_FR, const.AINE_DE, const.AINE_RU)
            if c.testityyp == TESTITYYP_R1:
                testiliigid = (const.TESTILIIK_RIIGIEKSAM, const.TESTILIIK_RV)
                q = q.filter(~ model.Test.aine_kood.in_(voorkeeled))
            elif c.testityyp == TESTITYYP_R2:
                testiliigid = (const.TESTILIIK_RIIGIEKSAM, const.TESTILIIK_RV)
                q = q.filter(model.Test.aine_kood.in_(voorkeeled))
            elif c.testityyp == TESTITYYP_T3:
                testiliigid = (const.TESTILIIK_TASEMETOO,)
            elif c.testityyp == TESTITYYP_T6:
                testiliigid = (const.TESTILIIK_TASEMETOO,)
            else:
                testiliigid = (c.testityyp,)
        if len(testiliigid) == 1:
            q = q.filter(model.Test.testiliik_kood==testiliigid[0])
        else:
            q = q.filter(model.Test.testiliik_kood.in_(testiliigid))
        
        if join_kasutaja:
            q = q.join(model.Sooritaja.kasutaja)
        if join_koht:
            q = q.outerjoin(model.Sooritaja.kool_koht)
        if join_koolinimi:
            q = q.outerjoin(model.Sooritaja.koolinimi)
        if join_maakond:
            q = q.outerjoin((Maakond,
                             sa.and_(Maakond.kood==model.Sooritaja.kool_aadress_kood1,
                                     Maakond.tase==1)))
        if join_kov:
            q = q.outerjoin((KOV,
                             sa.and_(KOV.kood==model.Sooritaja.kool_aadress_kood2,
                                     KOV.tase==2)))
        if join_piirkond:
            q = q.outerjoin(model.Sooritaja.kool_piirkond)

        test = None
        if c.test_id:
            test_id, kursus = self._split_test_kursus(c.test_id)
            if test_id:
                test = model.Test.getR(test_id)
                if test:
                    q = q.filter(model.Test.nimi==test.nimi)
                    if kursus:
                        q = q.filter(model.Sooritaja.kursus_kood==kursus)

        if c.keeletase_kood:
            q = q.filter(model.Sooritaja.keeletase_kood==c.keeletase_kood)

        if c.aasta:
            q = q.filter(model.Testimiskord.aasta==c.aasta)

        if cnt_mandatory == 3:
            # jaotusega koos antud filtrid
            ALL = 'X'
            if c.sugu and ALL not in c.sugu:
                q = q.filter(model.Kasutaja.sugu.in_(c.sugu))
            if c.koolityyp and ALL not in c.koolityyp:
                q = q.filter(model.Koht.koolityyp_kood.in_(c.koolityyp))
            if c.oppekeel and ALL not in c.oppekeel:
                q = q.filter(model.Sooritaja.oppekeel.in_(c.oppekeel))
            if c.soorituskeel and ALL not in c.soorituskeel:
                q = q.filter(model.Sooritaja.lang.in_(c.soorituskeel))
            if c.maakond and ALL not in c.maakond:
                # leiame ka vanad maakonnad, mis on sama nimega
                maakonnad2 = model.Aadresskomponent.sama_maakonna_koodid(c.maakond)
                q = q.filter(model.Sooritaja.kool_aadress_kood1.in_(maakonnad2))

            all_kov = c.kov and ALL in c.kov
            if all_kov and c.is_r2022:
                # mitte kuvada alla 2 kooliga KOVe
                c.warn_kov2 = True
                all_kov = False
            if c.kov and not all_kov:
                q = q.filter(model.Sooritaja.kool_aadress_kood2.in_(c.kov))

            if c.koolinimi_id and c.is_r2022:
                # mitte kuvada koolide kaupa tulemusi
                c.warn_kool = True
                c.koolinimi_id = [-1]
            if c.koolinimi_id and ALL not in c.koolinimi_id:
                try:
                    values = list(map(int, c.koolinimi_id))
                except ValueError:
                    log.error('vigane koolinimi_id: %s' % c.koolinimi_id)
                else:
                    q = q.filter(model.Sooritaja.koolinimi_id.in_(values))
            if c.oppevorm and ALL not in c.oppevorm:
                q = q.filter(model.Sooritaja.oppevorm_kood.in_(c.oppevorm))

        q = q.group_by(*li)
        self._search_rv(test)
        #model.log_query(q)

        c.is_t22 = c.testityyp == const.TESTILIIK_TASEMETOO and (not c.aasta or int(c.aasta) > 2019)
        c.header = self._prepare_header()
        if c.csv:
            return self._index_csv(q, 'tulemused.csv')
        return q

    def _search_rv(self, test):
        c = self.c
        voorkeeled = (const.AINE_EN, const.AINE_FR, const.AINE_DE, const.AINE_RU)
        if not (c.testityyp == TESTITYYP_R2 or \
                not c.testityyp and \
                test and \
                test.testiliik_kood == const.TESTILIIK_RIIGIEKSAM and \
                test.aine_kood in voorkeeled):
            return
            
        li = [model.Rveksam.aine_kood,
              model.Tunnistus.oppeaasta,
              model.Rvsooritaja.keeletase_kood,
              ]
        li_select = [sa.func.count(model.Rvsooritaja.id),] + li
        q = (model.SessionR.query(*li_select)
             .join(model.Rvsooritaja.rveksam)
             .join(model.Rvsooritaja.tunnistus)
             .filter(model.Rvsooritaja.sooritaja_id==None)
             )
        if test:
            q = q.filter(model.Rveksam.aine_kood==test.aine_kood)

        if c.aasta:
            q = q.filter(model.Tunnistus.oppeaasta==c.aasta)
        else:
            q = q.filter(model.Tunnistus.oppeaasta>=MIN_AASTA)
            
        q = q.group_by(*li)
        q = q.order_by(*li)
        data = []
        prev = None
        for rcd in q.all():
            cnt, aine, aasta, tase = rcd
            key = (aine, aasta)
            if prev == key:
                data[-1][2][tase] = cnt
            else:
                prev = key
                item = [aine, aasta, {tase: cnt}]
                data.append(item)
        c.rv_rows = data
        c.prepare_rv_row = self._prepare_rv_row
        c.prepare_rv_header = self._prepare_rv_header
        
    def _split_test_kursus(self, testkursus_id):
        """Valikväljale on kokku kodeeritud testi id ja kursus.
        Eraldame testi ID (mis määrab testi nime) ja kursuse
        """
        try:
            test_id, kursus = testkursus_id.split('-', 1)
        except ValueError:
            test_id = testkursus_id
            kursus = None
        try:
            return int(test_id), kursus
        except:
            return None, None

    def _add_unique_sort(self, order_list):
        # lisame sorteerimistingimuste lõppu unikaalse ID,
        # sest muidu võib juhtuda, et sorditakse välja järgi, mis on paljudel sama
        # ja siis tulevad tulemused iga kord ise järjekorras
        c = self.c
        values = (('kasutaja.sugu', c.sugu),
                  ('koht.koolityyp_kood', c.koolityyp),
                  ('sooritaja.oppekeel', c.oppekeel),
                  ('sooritaja.lang', c.soorituskeel),
                  ('sooritaja.keeletase_kood', c.keeletase),
                  ('sooritaja.oppevorm_kood', c.oppevorm),
                  ('maakond.nimetus', c.maakond),
                  ('kov.nimetus', c.kov),
                  ('koolinimi.nimi', c.ko),
                  )
        fields = [r[1] for r in order_list]
        for field, inuse in values:
           if inuse:
              if field not in fields:
                 order_list.append((False, field))
    
    def _order_able(self, q, field):
        """Kontrollitakse, kas antud välja järgi on võimalik sortida
        """
        if field not in self._sort_options:
            return False
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
        elif field == 'sooritaja.oppevorm_kood' and not self.c.oppevorm:
            return False
        elif field == 'piirkond.nimi' and not self.c.piirkond:
            return False
        elif field == 'maakond.nimetus' and not self.c.maakond:
            return False
        elif field == 'kov.nimetus' and not self.c.kov:
            return False
        elif field == 'testimiskord.tahis' and not self.c.tkord:
            return False
        elif field == 'koolinimi.nimi' and not self.c.ko:
            return False
        elif field.startswith('aadresskomponent.'):
            # vana versiooni otsing
            return False
        elif field.startswith('alatest.'):
            return self.c.ositi and self.c.alatestinimi and not self.c.testiosanimi
        else:
            return True

    def _prepare_header(self):
        c = self.c        
        c.ind_col_test = 1
        # tabeli päis
        header = [('testimiskord.aasta', _("Aasta")),
                  ('test.nimi sooritaja.kursus_kood', _("Test")),
                  ('test.id', _("Testi ID")),
                  ]
        if c.n_testiliik:
            header.append(('test.testiliik_kood', _("Testi liik")))
        if c.n_sugu:
            header.append(('kasutaja.sugu', _("Sugu")))
        if c.n_koolityyp:
            header.append(('koht.koolityyp_kood', _("Kooli tüüp")))
        if c.n_keeletase:
            header.append(('sooritaja.keeletase_kood', _("Keeleoskuse tase")))
            header.append((None, _("Tasemega sooritajate osa (%)")))
        if c.n_oppekeel:
            header.append(('sooritaja.oppekeel', _("Õppekeel")))
        if c.n_soorituskeel:
            header.append(('sooritaja.lang', _("Soorituskeel")))
        if c.n_maakond:
            header.append(('maakond.nimetus', _("Maakond")))
        if c.n_kov:
            header.append(('kov.nimetus', _("KOV")))            
        if c.n_kool:
            header.append(('koolinimi.nimi', _("Õppeasutus")))
        if c.n_oppevorm:
            header.append(('sooritaja.oppevorm_kood', _("Õppevorm")))                        

        if c.is_t22:
            # ilma pallideta testid
            c.col_eksaminandid = True
            header.append((None, _("Sooritajaid")))
        else:
            if c.col_eksaminandid:
                header.append((None, _("Sooritajaid")))
            if c.col_maxpallid:
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
                
            if c.col_aup:
                header.append((None, _("AUP")))
            if c.col_yup:
                header.append((None, _("ÜUP")))            

        if c.testityyp == const.TESTILIIK_POHIKOOL:
            if c.col_tase_b1:
                header.append((None, "B1 (%)"))
        elif c.testityyp == TESTITYYP_R2:
            if c.col_tase_b1:
                header.append((None, "B1 (%)"))
            if c.col_tase_b2:
                header.append((None, "B2 (%)"))
            if c.col_tase_c1:
                header.append((None, "C1 (%)"))
            if c.col_tase_c2:
                header.append((None, "C2 (%)"))
            if c.col_tasemeta:
                header.append((None, _("Taset mitte saavutanud") + " (%)"))
        elif c.testityyp == TESTITYYP_R1:
            if c.col_tase_b2:
                header.append((None, "B2 (%)"))
            if c.col_tase_c1t:
                header.append((None, _("C1 tasemetunnistuse esitanud")))
            
        return header

    def _prepare_items(self, q):
        "Loetelu ridade andmete väljastamine (CSV jaoks)"
        header = self._prepare_header()
        items = []
        for n, rcd in enumerate(q.all()):
            item = self._prepare_item(rcd, n)
            if item:
                items.append(item)

        if self.c.rv_rows:
            items.append(self._prepare_rv_header())
            for rcd in self.c.rv_rows:
                items.append(self._prepare_rv_row(rcd))
        return header, items

    def _prepare_rv_header(self):
        return ['Aasta',
                'Võõrkeel',
                'Tunnistuse esitajaid',
                'B1 (%)',
                'B2 (%)',
                'C1 (%)',
                'C2 (%)',
                ]

    def _prepare_rv_row(self, rcd):
        aine, aasta, tasemed = rcd
        aine_nimi = model.Klrida.get_str('AINE', aine).replace('(võõrkeel)','')
        total = sum(tasemed.values())
        row = [aasta,
               #u'Tunnistuse esitanud (%s)' % aine_nimi,
               aine_nimi,
               total,
               ]
        for tase in (const.KEELETASE_B1,
                     const.KEELETASE_B2,
                     const.KEELETASE_C1,
                     const.KEELETASE_C2):
            cnt = tasemed.get(tase) or 0
            pr = cnt * 100./total
            row.append(self.h.fstr(pr, 1))
        return row

    def _prepare_item(self, rcd, n):
        "Rea moodustamine CSV jaoks"
        row, d_url, r_url, h_url, d_groups = self._prepare_row(rcd)
        return row
    
    def _prepare_row(self, rcd):        
        "Tabeli ühe rea väljade kokkupanek"
        c = self.c
        h = self.h
        
        regatud = rcd[0]
        aine = rcd[1]
        aasta = rcd[2]
        test_id = rcd[3]          
        test_nimi = rcd[4]
        kursus = rcd[5]
        max_pallid = rcd[6]

        li_d_groups = []
        
        if kursus:
            kursus_nimi = model.Klrida.get_str('KURSUS', kursus, ylem_kood=aine)
            test_nimi = '%s (%s)' % (test_nimi, kursus_nimi)
    
        def n_value(n, nplus=0):
            # kui välja lõikes otsitakse, antakse välja väärtus või -
            # kui välja lõiget ei kasutata, antakse None
            if n:
                return rcd[n + nplus] or Query.NULL

        UNASSIGNED = _("Määramata")
        def ns_value(n, nplus=0):
            # kui välja lõikes otsitakse, antakse välja väärtus või -
            # kui välja lõiget ei kasutata, antakse None
            if n:
                return rcd[n + nplus] or UNASSIGNED
            
        sugu = n_value(c.n_sugu)
        koolityyp = n_value(c.n_koolityyp)
        oppekeel = n_value(c.n_oppekeel)
        soorituskeel = n_value(c.n_soorituskeel)
        maakond_kood = n_value(c.n_maakond)
        maakond_nimi = ns_value(c.n_maakond, 1)
        kov_kood = n_value(c.n_kov)
        kov_nimi = ns_value(c.n_kov, 1)
        koolinimi_id = n_value(c.n_kool)
        kool_nimi = ns_value(c.n_kool, 1)
        keeletase = n_value(c.n_keeletase)
        oppevorm = n_value(c.n_oppevorm)        
        
        qry = Query(self, aasta, test_id, kursus, max_pallid, sugu, koolityyp, oppekeel, soorituskeel,
                    maakond_kood, kov_kood, koolinimi_id, keeletase, oppevorm, avalik=self.avalik)

        total, res_avg, res_stddev, res_min, res_max, res_avg_pr = qry.query_avg()
        if total < 5:
            c.warn_small_result = True
            return None, None, None, None, None
        if c.is_r2022:
            # riigieksam 2022
            if kov_kood and kov_kood not in [r[0] for r in c.opt_kov] or koolinimi_id:
                # kooli kaupa ei tohi tulemusi väljastada
                c.warn_kov2 = True
                return None, None, None, None, None
        
        q_koik, q_koiktasemed = qry._gen_query([sa.func.count(model.Sooritaja.id)])
        q = q_koik.filter(model.Sooritaja.staatus==const.S_STAATUS_TEHTUD)
        
        row = [aasta,
               test_nimi,
               test_id,
               ]
        if c.n_testiliik:
            row.append(model.Klrida.get_str('TESTILIIK', rcd[c.n_testiliik]))
        if c.n_sugu:
            row.append(rcd[c.n_sugu])
            di_sugu = {const.SUGU_N: _("Tüdrukud"), const.SUGU_M: _("Poisid")}
            value = di_sugu.get(row[-1]) or UNASSIGNED
            li_d_groups.append(value.lower())
        if c.n_koolityyp:
            row.append(model.Klrida.get_str('KOOLITYYP', koolityyp) or UNASSIGNED)
            li_d_groups.append(row[-1])
        if c.n_keeletase:
            cnt_koik = q_koiktasemed.filter(model.Sooritaja.staatus==const.S_STAATUS_TEHTUD).scalar()
            cnt_tase = q.scalar()
            if cnt_koik:
                pr_tase = cnt_tase * 100 / cnt_koik
            else:
                pr_tase = None
            row.append(model.Klrida.get_str('KEELETASE', keeletase, ylem_kood=aine) or UNASSIGNED)
            li_d_groups.append(row[-1])            
            row.append(h.fstr(pr_tase,1))
            
        if c.n_oppekeel:
            row.append(const.EHIS_LANG_NIMI.get(oppekeel) or UNASSIGNED)
            value = row[-1]
            if value == 'eesti':
                value = 'eesti õppekeel'
            elif value == 'vene':
                value = 'vene õppekeel'
            li_d_groups.append(value or UNASSIGNED)
        if c.n_soorituskeel:
            row.append(model.Klrida.get_lang_nimi(soorituskeel) or UNASSIGNED)
            value = row[-1].lower()
            li_d_groups.append(value)            
        if c.n_maakond:
            row.append(maakond_nimi)
            li_d_groups.append(row[-1])            
        if c.n_kov:
            row.append(kov_nimi)
            li_d_groups.append(row[-1])            
        if c.n_kool:
            row.append(kool_nimi or UNASSIGNED)
            li_d_groups.append(row[-1])            
        if c.n_oppevorm:
            row.append(model.Klrida.get_str('OPPEVORM', oppevorm) or UNASSIGNED)
            li_d_groups.append(row[-1])            

        if c.col_eksaminandid:
            row.append(total)
        if not c.is_t22:
            if c.col_maxpallid:
                row.append(h.fstr(max_pallid,1))
            if c.col_keskmine:
                row.append(h.fstr(res_avg,1))
            if c.col_keskminepr:
                row.append(h.fstr(res_avg_pr,1))
            if c.col_mediaan:
                mediaan = qry.query_mediaan()
                row.append(h.fstr(mediaan,1))            
            if c.col_halve:
                row.append(h.fstr(res_stddev,1))
                
            if c.col_alla20 or c.col_alla20pr:
                allap, allapr = qry.query_min(q, self.c.alla, total)
                if c.col_alla20:
                    row.append(allap)
                if c.col_alla20pr:
                    row.append(h.fstr(allapr,1))
                    
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
                row.append(h.fstr(res_min,1))
            if c.col_max:
                row.append(h.fstr(res_max,1))

            if c.col_yle80 or c.col_yle80pr:
                ylep, ylepr = qry.query_max(q, self.c.yle, total)
                if c.col_yle80:
                    row.append(ylep)
                if c.col_yle80pr:
                    row.append(h.fstr(ylepr,1))

            if c.col_aup or c.col_yup:
                aup, yup = qry.query_confidence(total, res_stddev, res_avg)
                if c.col_aup:
                    row.append(h.fstr(aup, 1))
                if c.col_yup:
                    row.append(h.fstr(yup, 1))                

        if c.testityyp == const.TESTILIIK_POHIKOOL:
            if c.col_tase_b1:
                row.append(h.fstr(qry.query_tase(q, const.KEELETASE_B1, total),1))

        elif c.testityyp == TESTITYYP_R2:
            if c.col_tase_b1:
                row.append(h.fstr(qry.query_tase(q, const.KEELETASE_B1, total),1))
            if c.col_tase_b2:
                row.append(h.fstr(qry.query_tase(q, const.KEELETASE_B2, total),1))
            if c.col_tase_c1:
                row.append(h.fstr(qry.query_tase(q, const.KEELETASE_C1, total),1))
            if c.col_tase_c2:
                row.append(h.fstr(qry.query_tase(q, const.KEELETASE_C2, total),1))                        
            if c.col_tasemeta:
                row.append(h.fstr(qry.query_tase(q, None, total),1))

        elif c.testityyp == TESTITYYP_R1:
            if c.col_tase_b2:
                row.append(h.fstr(qry.query_tase(q, const.KEELETASE_B2, total),1))
            if c.col_tase_c1t:
                row.append(h.fstr(qry.query_c1_tunnistus(aasta)))

        h_url = d_url = r_url = None
        if max_pallid and total and not c.is_t22:
            params = {'aasta':aasta,
                      'testityyp': c.testityyp,
                      'test_id': test_id,
                      'kursus': kursus,
                      'sugu': sugu,
                      'koolityyp': koolityyp,
                      'oppekeel': oppekeel,
                      'soorituskeel': soorituskeel,
                      'maakond_kood': maakond_kood,
                      'kov_kood': kov_kood,
                      'koolinimi_id': koolinimi_id,
                      'oppevorm': oppevorm,
                      }
            d_url = self.url('eksamistatistika', sub='jaotus', **params)

        test = model.Test.getR(test_id)

        raport = model.Statistikaraport.get_raport(test_id, kursus, aasta, 'html')
        if raport and (raport.avalik or not self.avalik):
            h_url = self.url('eksamistatistika_riikliktagasiside', aasta=aasta, test_id=test_id, kursus=kursus or '')
        raport = model.Statistikaraport.get_raport(test_id, kursus, aasta, 'pdf')
        if raport and (raport.avalik or not self.avalik):
            r_url = self.url('eksamistatistika_riikliktagasiside', aasta=aasta, test_id=test_id, kursus=kursus or '', pdf=1)                

        d_groups = ', '.join([r for r in li_d_groups if r != None])
        return row, d_url, r_url, h_url, d_groups

    def _index_jaotus(self):
        """Jaotuste dialoogiaken"""
        self.form = Form(self.request, schema=self._SEARCH_FORM, method='GET')
        self.form.validate()
        self._copy_search_params(self.form.data)
        c = self.c

        test_id = c.test_id
        kursus = c.kursus
        test = model.Test.getR(test_id)

        if self.is_r2022eis(test_id, c.aasta):
            # ei või kuvada koolide kaupa tulemusi
            if c.koolinimi_id:
                c.koolinimi_id = -1
                c.warn_kool = True
            if c.kov_kood:
                opt_mk, opt_kov, opt_kool = self._get_koolopt()
                if c.kov_kood not in [r[0] for r in opt_kov]:
                    c.kov_kood = '---'
                    c.warn_kov2 = True
                    
        qry = Query(self, c.aasta, test_id, kursus, test.max_pallid,
                    c.sugu, c.koolityyp, c.oppekeel, c.soorituskeel,
                    c.maakond_kood, c.kov_kood, c.koolinimi_id, c.keeletase, c.oppevorm,
                    avalik=self.avalik)

        q = (qry._gen_query1([sa.func.count(model.Sooritaja.pallid)])
             .filter(model.Sooritaja.hindamine_staatus==const.H_STAATUS_HINNATUD)
             .filter(model.Sooritaja.staatus==const.S_STAATUS_TEHTUD)
             )
        max_pallid = test.max_pallid
        field = model.Sooritaja.pallid
        
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
        prot = [self.h.fstr(n*100/total,1) for n in values]
        texts = [f'{values[i]} ({prot[i]}%)' for i in range(x_len)]
        c.items = [(x_labels[i], values[i], prot[i]) for i in range(x_len)]
            
        max_y = max(values)
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
                       hovertemplate=_("Tulemuse vahemik") + ": %{x}p<br>" + _("Sooritajate arv") + ": %{text}"
                       )
                       ]
        fig = go.Figure(data)
        fig.update_layout(xaxis_title=_("Tulemus"),
                          yaxis_title=_("Sooritajate arv"),
                          yaxis={'tickvals': tickvals},
                          margin=dict(l=5, r=5, t=2, b=2))
        c.json_data = fig.to_json()
        html = self.form.render('avalik/eksamistatistika/jaotus.mako',
                                extra_info=self.response_dict)            

        return Response(html)

class Query(object):
    "Päringu objekt, vastab tulemuste loetelu yhele reale, sisaldab reale vastava grupi tingimusi"

    NULL = '-' # kui on välja järgi otsing ja väli on NULL
    tasemeta_lavi = True # PDFis tasemet mitte saanute veerus arvestada ainult 1-p läve yletanuid (va ingl k, ES-2094)
    def __init__(self,
                 handler,
                 aasta,
                 test_id,
                 kursus,
                 max_pallid,
                 sugu=None,
                 koolityyp=None,
                 oppekeel=None,
                 soorituskeel=None,
                 maakond_kood=None,
                 kov_kood=None,
                 koolinimi_id=None,
                 keeletase=None,
                 oppevorm=None,
                 avalik=True):

        self.handler = handler
        self.aasta = aasta
        self.test_id = test_id
        self.kursus = kursus
        self.max_pallid = max_pallid
        self.sugu = sugu
        self.koolityyp = koolityyp
        self.oppekeel = oppekeel
        self.soorituskeel = soorituskeel
        self.maakond_kood = maakond_kood
        self.kov_kood = kov_kood        
        self.koolinimi_id = koolinimi_id
        self.keeletase = keeletase
        self.oppevorm = oppevorm
        self.oppevormid = []
        self.hinnatud = False
        self.avalik = avalik
        
    def _gen_query(self, select_fields, join_koht=False, join_maakond=False, join_kasutaja=False, join_koolinimi=False, testiosa_id=None, alatest_id=None, testiylesanne_id=None, aspekt_kood=None, avaldatud=True):
        "Sooritajate arv ja keskmine tulemus"
        q = model.SessionR.query(*select_fields)

        if self.hinnatud:
            q = (q.filter(model.Sooritaja.staatus==const.S_STAATUS_TEHTUD)
                 .filter(model.Sooritaja.hindamine_staatus==const.H_STAATUS_HINNATUD)
                 )
        if avaldatud:
            q = (q.join(model.Sooritaja.testimiskord)
                 .filter(model.Testimiskord.aasta==self.aasta)
                 .filter(model.Sooritaja.hindamine_staatus!=const.H_STAATUS_TOOPUUDU)
                 .filter(model.Testimiskord.tulemus_kinnitatud==True)
                 .filter(model.Sooritaja.test_id==self.test_id)
                 )
            q = q.filter(model.Testimiskord.koondtulemus_avaldet==True)
            if self.avalik:
                q = q.filter(model.Testimiskord.statistika_aval_kpv!=None)
            else:
                q = q.filter(model.Testimiskord.statistika_ekk_kpv!=None)                
            
        if self.kursus:
            q = q.filter(model.Sooritaja.kursus_kood==self.kursus)
            
        join_aadress = False

        def n_value(value):
            if value == Query.NULL:
                return None
            else:
                return value

        def filter_list(field, values):
            if not isinstance(values, (list, tuple)):
                return field==n_value(values)
            elif len(values) == 1:
                return field==n_value(values[0])
            else:
                return field.in_(values)

        if self.sugu:
            q = q.filter(filter_list(model.Kasutaja.sugu, self.sugu))
            join_kasutaja = True
        if self.koolityyp:
            q = q.filter(filter_list(model.Koht.koolityyp_kood, self.koolityyp))
            join_koht = True
        if self.oppekeel:
            q = q.filter(filter_list(model.Sooritaja.oppekeel, self.oppekeel))
        if self.soorituskeel:
            q = q.filter(filter_list(model.Sooritaja.lang, self.soorituskeel))          
        if self.maakond_kood:
            q = q.filter(filter_list(model.Sooritaja.kool_aadress_kood1, self.maakond_kood))
        if self.kov_kood:
            q = q.filter(filter_list(model.Sooritaja.kool_aadress_kood2, self.kov_kood))
        if self.koolinimi_id:
            join_koolinimi = True
            q = q.filter(filter_list(model.Sooritaja.koolinimi_id, self.koolinimi_id))
        if self.oppevorm:
            q = q.filter(filter_list(model.Sooritaja.oppevorm_kood, self.oppevorm))
        elif self.oppevormid:
            q = q.filter(model.Sooritaja.oppevorm_kood.in_(self.oppevormid))

        if testiosa_id:
            self.field_pallid = model.Sooritus.pallid
            self.field_protsent = model.Sooritus.tulemus_protsent
            q = q.join(model.Sooritaja.sooritused).filter(model.Sooritus.testiosa_id==testiosa_id)
        elif alatest_id:
            self.field_pallid = model.Alatestisooritus.pallid
            self.field_protsent = model.Alatestisooritus.tulemus_protsent            
            q = (q.join(model.Sooritaja.sooritused)
                 .join((model.Alatestisooritus, model.Alatestisooritus.sooritus_id==model.Sooritus.id))
                 .filter(model.Alatestisooritus.alatest_id==alatest_id)
                 )
        elif testiylesanne_id:
            self.field_pallid = model.Ylesandevastus.pallid
            self.field_protsent = None
            q = (q.join(model.Sooritaja.sooritused)
                 .join((model.Ylesandevastus,
                        model.Ylesandevastus.sooritus_id==model.Sooritus.id))
                 .filter(model.Ylesandevastus.testiylesanne_id==testiylesanne_id)
                 )
            if aspekt_kood:
                self.field_pallid = model.Vastusaspekt.pallid
                q = (q.join((model.Vastusaspekt, model.Vastusaspekt.ylesandevastus_id==model.Ylesandevastus.id))
                     .join(model.Vastusaspekt.hindamisaspekt)
                     .filter(model.Hindamisaspekt.aspekt_kood==aspekt_kood)
                     )
        else:
            self.field_pallid = model.Sooritaja.pallid
            self.field_protsent = model.Sooritaja.tulemus_protsent

        if join_koht:
            q = q.outerjoin(model.Sooritaja.kool_koht)
        if join_koolinimi:
            q = q.outerjoin(model.Sooritaja.koolinimi)
        if join_maakond:
            # kui kasutatakse PDFis (vt eksamistatistika_r.py)
            q = q.outerjoin((model.Aadresskomponent,
                             sa.and_(model.Aadresskomponent.kood==model.Sooritaja.kool_aadress_kood1,
                                     model.Aadresskomponent.tase==1)))
        if join_kasutaja:
            q = q.join(model.Sooritaja.kasutaja)
            
        q_koiktasemed = q
        if self.keeletase:
            q = q.filter(model.Sooritaja.keeletase_kood==n_value(self.keeletase))            
        return q, q_koiktasemed

    def _gen_query1(self, select_fields, **kw):
        q, qk = self._gen_query(select_fields, **kw)
        return q
    
    def query_avg(self):
        "Tehtud soorituste arv, keskmine, standardhälve, min ja max pallid"
        field = model.Sooritaja.pallid
        field_pr = model.Sooritaja.tulemus_protsent
        fields = [sa.func.count(field),
                  sa.func.avg(field),
                  sa.func.stddev(field),
                  sa.func.min(field),
                  sa.func.max(field),
                  sa.func.avg(field_pr)]
        q, qk = self._gen_query(fields)
        q = (q.filter(model.Sooritaja.staatus==const.S_STAATUS_TEHTUD)
             .filter(model.Sooritaja.hindamine_staatus==const.H_STAATUS_HINNATUD))
        total = res_min = res_max = 0
        res_avg = res_stddev = None
        #model.log_query(q)
        for rcd in q.all():
            total, res_avg, res_stddev, res_min, res_max, res_avg_pr = rcd
        return total, res_avg, res_stddev, res_min, res_max, res_avg_pr

    def query_confidence(self, total, stddev, avg):
        "Usalduspiiri arvutamine"
        # http://www.wikihow.com/Calculate-Confidence-Interval
        # Veapiir = 1,96 * (standardhälve / ruutjuur valimisuurusest)
        # Alumine usalduspiir = keskmine – veapiir
        # Ülemine usalduspiir = keskmine + veapiir
        if stddev is not None and avg is not None and total:
            #t = 1.96 # usaldus 95 % 
            t = _hills_inv_t(total - 1)
            if t:
                margin = t * stddev / math.sqrt(total) # veapiir
                return avg - margin, avg + margin
        return None, None

    def query_tase(self, q, tase, total):
        "Antud keeleoskuse taseme saanute protsent"
        if total:
            cnt = q.filter(model.Sooritaja.keeletase_kood==tase).scalar()            
            if cnt is not None:
                return cnt * 100./total

    def query_tasemeta(self, q, total):
        "Taseme mittesaavutanud, kuid 1-pallise lävendi yletanud sooritajate protsent"
        if total:
            q1 = q.filter(model.Sooritaja.keeletase_kood==None)
            #if self.tasemeta_lavi:
            #    q1 = q1.filter(model.Sooritaja.pallid>=1)
            cnt = q1.scalar()
            if cnt is not None:
                return cnt * 100./total   

    def query_c1_tunnistus(self, aasta):
        "Tasemetunnistuse esitanute arv (ei pidanud eksamit tegema)"
        # a. kelle periood_kood EISi tabelis „test“ on meid huvitav aasta (nt praegu 2017) JA
        # b. kelle lopetamisaasta EISi „kasutaja“ tabelis on meid huvitav aasta (praegu 2017) JA
        # c. kes ei ole sooritanud eesti keele riigieksamit ega eesti keele teise keelena riigieksamit
        #    meid huvitaval aastal (2017) JA
        # d. kellel on olemas riigikeele tasemeeksamilt C1-tase enne meid huvitavat aastat
        #    (praegu siis enne 01. jaanuari 2017)
        
        f_sooritaja = sa.and_(model.Kasutaja.id==model.Sooritaja.kasutaja_id,
                              model.Sooritaja.test_id==model.Test.id,
                              model.Test.periood_kood==str(aasta)
                              )
        f_eestikeel = sa.and_(model.Kasutaja.id==model.Sooritaja.kasutaja_id,
                              model.Sooritaja.oppeaasta==aasta,
                              model.Sooritaja.staatus==const.S_STAATUS_TEHTUD,
                              model.Sooritaja.test_id==model.Test.id,
                              model.Test.testiliik_kood==const.TESTILIIK_RIIGIEKSAM,
                              model.Test.aine_kood.in_((const.AINE_ET, const.AINE_ET2))
                              )
        f_c1 = sa.and_(model.Kasutaja.id==model.Sooritaja.kasutaja_id,
                       model.Sooritaja.algus<date(aasta,1,1),
                       model.Sooritaja.staatus==const.S_STAATUS_TEHTUD,
                       model.Sooritaja.test_id==model.Test.id,
                       model.Test.testiliik_kood==const.TESTILIIK_TASE,
                       model.Sooritaja.keeletase_kood.in_((const.KEELETASE_C1, const.KEELETASE_C2))
                       )
        
        q = (model.SessionR.query(sa.func.count(model.Kasutaja.id))
             .filter(model.Kasutaja.lopetamisaasta==aasta)
             .filter(~ sa.exists().where(f_eestikeel))
             .filter(sa.exists().where(f_c1))
             )
        
        def n_value(value):
            if value == Query.NULL:
               return None
            else:
               return value
         
        def filter_list(field, values):
           if not isinstance(values, (list, tuple)):
              return field==n_value(values)
           elif len(values) == 1:
              return field==n_value(values[0])
           else:
              return field.in_(values)

        if self.sugu:
            q = q.filter(filter_list(model.Kasutaja.sugu, self.sugu))

        if self.oppevorm:
            f_sooritaja = sa.and_(f_sooritaja, filter_list(model.Sooritaja.oppevorm_kood, self.oppevorm))
        elif self.oppevormid:
            f_sooritaja = sa.and_(f_sooritaja, model.Sooritaja.oppevorm_kood.in_(self.oppevormid))
        if self.oppekeel:
            f_sooritaja = sa.and_(f_sooritaja, filter_list(model.Sooritaja.oppekeel, self.oppekeel))

        f_koht = []
        if self.koolityyp:
            f_koht.append(filter_list(model.Koht.koolityyp_kood, self.koolityyp))
        if self.koolinimi_id:
            f_koht.append(model.Koht.koolinimed.any(filter_list(model.Koolinimi.id, self.koolinimi_id)))
        if f_koht:
            f_koht = sa.and_(*f_koht)
            f_sooritaja = sa.and_(f_sooritaja, model.Sooritaja.kool_koht.has(f_koht))

        if self.maakond_kood:
            f_sooritaja = sa.and_(f_sooritaja,
                                  filter_list(model.Sooritaja.kool_aadress_kood1, self.maakond_kood))
        if self.kov_kood:
            f_sooritaja = sa.and_(f_sooritaja,
                                  filter_list(model.Sooritaja.kool_aadress_kood2, self.kov_kood))
           
        q = q.filter(sa.exists().where(f_sooritaja))
        #model.log_query(q)
        return q.scalar()

    def query_max(self, q, protsent, total):
        "Vähemalt etteantud arvu punkti saanute arv"
        cnt = cntpr = None
        if self.max_pallid is not None:
            diff = 1e-12
            cnt = q.filter(self.field_protsent > protsent - diff).scalar()
            if cnt is not None and total:
                cntpr = cnt * 100./total
        return cnt, cntpr

    def query_min(self, q, protsent, total):
        "Min punktide saajate arv"
        cnt = cntpr = None
        if self.max_pallid is not None:
            diff = 1e-12
            cnt = q.filter(self.field_protsent < protsent + diff).scalar()            
            if cnt is not None and total:
                cntpr = cnt * 100./total
        return cnt, cntpr

    def query_min_p(self, q, pallid, total):
        "Min punktide saajate arv"
        cnt = cntpr = None
        if self.max_pallid is not None:
            diff = 1e-12
            cnt = q.filter(self.field_pallid < pallid).scalar()
            if cnt is not None and total:
                cntpr = cnt * 100./total
        return cnt, cntpr

    def query_mediaan(self, testiosa_id=None, alatest_id=None):
        "Tulemuse mediaan"
        # alates PostgreSQL v9.4 on olemas percentile_cont()
        select_field = self.field_pallid
        q = self._gen_query1([select_field], testiosa_id=testiosa_id, alatest_id=alatest_id)
        q = (q.filter(model.Sooritaja.staatus==const.S_STAATUS_TEHTUD)
             .filter(model.Sooritaja.hindamine_staatus==const.H_STAATUS_HINNATUD))
        sql = "WITH t(value) AS (" + model.str_query(q) + ") SELECT percentile_cont(0.5) WITHIN GROUP (ORDER BY value) FROM t"
        #log.info(sql)
        qm = model.SessionR.execute(sa.text(sql))
        return qm.scalar()

def _norm_z(p):
   # Returns z given a half-middle tail type p.
    a0= 2.5066282
    a1=-18.6150006
    a2= 41.3911977
    a3=-25.4410605
    b1=-8.4735109
    b2= 23.0833674
    b3=-21.0622410
    b4= 3.1308291
    c0=-2.7871893
    c1= -2.2979648
    c2=  4.8501413
    c3=  2.3212128
    d1= 3.5438892
    d2=  1.6370678
 
    r = math.sqrt(0-math.log(0.5-p))
    z=(((c3*r+c2)*r+c1)*r+c0)/((d2*r+d1)*r+1)
    return z

def _hills_inv_t(df):
   # t-distribution table arvutamine
   p = .05 # probability 95%
   values = {1: 12.70620,
             2: 4.30265,
             3: 3.18245,
             4: 2.77645,
             5: 2.57058,
             }
   t = values.get(df)
   if t is None:
      # https://surfstat.anu.edu.au/surfstat-home/tables/t.php
      # Hill's approx. inverse t-dist.: Comm. of A.C.M Vol.13 No.10 1970 pg 620.
      # Calculates t given df and two-tail probability.
      a = 1/(df - 0.5)
      b = 48./(a*a)
      c = ((20700.*a/b - 98.)*a - 16.) * a + 96.36
      d = ((94.5/(b + c) - 3.)/b + 1) * math.sqrt(a * math.pi * .5) * df
      x = d * p
      y = math.pow(x, 2/df)
      if y > 0.05 + a:
         x = _norm_z(.5 * (1 - p))
         y = x * x;
         if (df < 5):
            c = c + 0.3*(df - 4.5)*(x + 0.6)
         c = (((.05 * d * x - 5) * x - 7) * x - 2) * x + b + c
         y = (((((.4 * y + 6.3) * y + 36.)*y + 94.5)/c - y - 3.)/b + 1)*x
         y = a * y * y
         if y > .002:
            y = math.exp(y) - 1
         else:
            y = .5 * y * y + y
         t = math.sqrt(df*y)
      else:
         y = ((1./(((df + 6.)/(df*y) - 0.089*d - 0.822)*(df + 2.)*3.) + 0.5/(df + 4.))*y - 1.)*(df + 1.)/(df + 2.) + 1./y
         t = math.sqrt(df*y)
   return t

