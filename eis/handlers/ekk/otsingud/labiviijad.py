from itertools import groupby
import urllib.parse

from eis.lib.baseresource import *
_ = i18n._
from eis.lib.pdf.labiviijad import LabiviijadDoc
from eis.lib.pdf.labiviijaakt import LabiviijaaktDoc
from eis.lib.pdf.labiviijakiri import LabiviijakiriDoc

log = logging.getLogger(__name__)

class LabiviijadController(BaseResourceController):
    """Läbiviijate aruanded
    """
    _permission = 'aruanded-labiviijad'
    _INDEX_TEMPLATE = 'ekk/otsingud/labiviijad.mako'
    _LIST_TEMPLATE = 'ekk/otsingud/labiviijad_list.mako'
    _DEFAULT_SORT = 'kasutaja.perenimi,kasutaja.eesnimi'
    _ignore_default_params = ['pdf', 'csv', 'csv2', 'akt', 'mail', 'tcsv', 'format', 'list_url']
    _SEARCH_FORM = forms.ekk.otsingud.LabiviijadForm # valideerimisvorm otsinguvormile
    _get_is_readonly = False
    
    # kõigile päringutele ühised väljad
    _select_fields = [model.Kasutaja.id,
                      model.Kasutaja.epost,
                      model.Kasutaja.eesnimi,
                      model.Kasutaja.perenimi,
                      model.Kasutaja.isikukood,
                      model.Test.aine_kood,
                      model.Test.testiliik_kood,
                      model.Test.nimi,
                      model.Toimumisaeg.tahised,
                      model.Toimumisaeg.alates,
                      model.Profiil.arveldusarve,
                      ]
    
    def _query(self):
        # otsingu valikväljade valikute koostamine
        return None

    def _search_default(self, q):
        return None

    def _search(self, q1):
        c = self.c

        # TE, SE saab ainult eraldi valida
        if const.TESTILIIK_TASE in c.testiliik:
            c.testiliik = [const.TESTILIIK_TASE]
        elif const.TESTILIIK_SEADUS in c.testiliik:
            c.testiliik = [const.TESTILIIK_SEADUS]
        
        if not c.sessioon_id:
            log.debug('Puudub sessioon_id')
            return None

        if len(c.grupp_id) == 0:
            # läbiviija aruande jaoks on vaja ette anda läbiviija roll, mille aruannet tehakse
            self.error(_("Palun vali läbiviijate roll(id)"))
            log.debug('Puudub grupp_id')
            return

        format = self._getformat()

        # väljastatavad andmed sõltuvad sellest, millise rolli aruanne on
        set_grupp_id = set(c.grupp_id)
        s = set([const.GRUPP_KOMISJON,
                 const.GRUPP_INTERVJUU,
                 const.GRUPP_HINDAJA_S,
                 const.GRUPP_HINDAJA_S2,                 
                 const.GRUPP_VAATLEJA,
                 const.GRUPP_KONSULTANT,
                 const.GRUPP_T_ADMIN])
        on_kohtaeg = set_grupp_id.intersection(s)
        on_shindaja = const.GRUPP_HINDAJA_S in set_grupp_id        
        on_khindaja = const.GRUPP_HINDAJA_K in set_grupp_id
        on_s2hindaja = const.GRUPP_HINDAJA_S2 in set_grupp_id        
        on_intervjuu = const.GRUPP_INTERVJUU in set_grupp_id
        on_vaidehindaja = const.GRUPP_HINDAMISEKSPERT in set_grupp_id

        #log.debug('GRUPID: %s' % str(set_grupp_id))
        c.rep_title, c.aktimall = self._vali_mallid(c.testiliik, set_grupp_id, c.sessioon_id, c.test_id) 

        # komisjoniliikmete aruanne peab sisaldama ka komisjoniesimehi
        if const.GRUPP_KOMISJON in set_grupp_id:
            set_grupp_id.add(const.GRUPP_KOMISJON_ESIMEES)

        # kui otsitakse suulist I hindajat või intervjueerijat, siis tuleb kuvada ka hindaja-intervjueerija
        if on_shindaja or on_intervjuu:
            set_grupp_id.add(const.GRUPP_HIND_INT)

        # suuline II, III hindaja on läbiviijate tabelis suulise hindajana
        if on_s2hindaja:
            set_grupp_id.add(const.GRUPP_HINDAJA_S)

        # päringu väljundväljad
        li_select = self._select_fields + \
                    [model.Labiviija,
                     ]
        if on_kohtaeg:
            li_select += [model.Koht.nimi,
                          model.Testiruum.algus,
                          model.Testikoht.alates,
                          ]
        if on_khindaja or on_s2hindaja:
            li_select += [model.Hindamiskogum.tahis or '-',
                          ]

        join_leping = format == 'csv' or format == 'csv2'

        if join_leping:
            li_select += [model.Labiviijaleping.id,
                          model.Leping.nimetus]

        # päringu koostamine
        q = model.Session.query(*li_select).\
            join(model.Labiviija.kasutaja).\
            filter(model.Labiviija.kasutajagrupp_id.in_(set_grupp_id)).\
            join(model.Labiviija.toimumisaeg).\
            join(model.Toimumisaeg.testimiskord).\
            join(model.Testimiskord.test).\
            outerjoin(model.Kasutaja.profiil)

        if join_leping:
            q = (q.outerjoin((model.Testileping,
                              sa.and_(model.Testimiskord.id==model.Testileping.testimiskord_id,
                                      model.Testileping.kasutajagrupp_id==model.Labiviija.kasutajagrupp_id,
                                      model.Testileping.leping.has(model.Leping.yldleping==False))))
                 .outerjoin(model.Testileping.leping)
                 .outerjoin((model.Labiviijaleping,
                             sa.and_(model.Labiviijaleping.kasutaja_id==model.Kasutaja.id,
                                     sa.or_(
                                         model.Labiviijaleping.testsessioon_id==model.Testimiskord.testsessioon_id,
                                         sa.and_(model.Leping.sessioonita==True,
                                                 model.Leping.aasta_alates<=model.Testimiskord.aasta,
                                                 model.Leping.aasta_kuni>=sa.func.coalesce(model.Testimiskord.aasta, model.Leping.aasta_kuni))
                                         ),
                                     model.Labiviijaleping.leping_id==model.Testileping.leping_id)))
                 .outerjoin(model.Testileping.leping)
                 )

        if on_shindaja and not on_s2hindaja:
            # ainult I hindaja
            q = q.filter(sa.or_(model.Labiviija.kasutajagrupp_id!=const.GRUPP_HINDAJA_S,
                                model.Labiviija.liik==const.HINDAJA1))
        elif not on_shindaja and on_s2hindaja:
            # ainult II-III hindaja
            q = q.filter(sa.or_(model.Labiviija.kasutajagrupp_id!=const.GRUPP_HINDAJA_S,
                                model.Labiviija.liik>const.HINDAJA1))

        if on_kohtaeg:
            q = q.outerjoin(model.Labiviija.testikoht).\
                outerjoin(model.Testikoht.koht).\
                outerjoin(model.Labiviija.testiruum)

        if on_khindaja or on_s2hindaja:
            q = q.outerjoin(model.Labiviija.hindamiskogum)
           
        # kui on komisjoniliige või intervjueerija? või shindaja või admin,
        # siis peab olema toimumise protokollil märgitud osalenuks
        s_toimprot = set([const.GRUPP_KOMISJON,
                          const.GRUPP_KOMISJON_ESIMEES,
                          const.GRUPP_INTERVJUU,
                          const.GRUPP_HIND_INT,
                          const.GRUPP_T_ADMIN])
        if set_grupp_id.intersection(s_toimprot):
            if set_grupp_id - s_toimprot:
                # on ka muid gruppe
                q = q.filter(sa.or_(~ model.Labiviija.kasutajagrupp_id.in_(s_toimprot),
                                    model.Labiviija.staatus==const.L_STAATUS_OSALENUD))
            else:
                q = q.filter(model.Labiviija.staatus==const.L_STAATUS_OSALENUD)

        # kui on kirjalik või suuline hindaja, siis peab olema hinnatud tööde arv > 0
        if on_khindaja or on_shindaja or on_s2hindaja or on_intervjuu or on_vaidehindaja:
            s_hindajad = set([const.GRUPP_HINDAJA_K, 
                              const.GRUPP_HINDAJA_S, 
                              const.GRUPP_HINDAJA_S2, 
                              const.GRUPP_INTERVJUU,
                              const.GRUPP_HIND_INT,
                              const.GRUPP_HINDAMISEKSPERT])
            if set_grupp_id - s_hindajad:
                # on ka muid gruppe
                q = q.filter(sa.or_(~ model.Labiviija.kasutajagrupp_id.in_(s_hindajad),
                                    model.Labiviija.tasu_toode_arv>0))
            else:
                q = q.filter(model.Labiviija.tasu_toode_arv>0)

        if c.toimumisaeg_id:
            q = q.filter(model.Labiviija.toimumisaeg_id==int(c.toimumisaeg_id))
        if c.alates:
            q = q.filter(model.Toimumisaeg.kuni>=c.alates)
        if c.kuni:
            q = q.filter(model.Toimumisaeg.alates<c.kuni+timedelta(1))
            
        q = self._search_filter(q)
        #model.log_query(q)
        return q

    def _search_filter(self, q):
        """Päringufiltrid, mis ei sõltu rollist ja on kõigile rollidele ühised"""
        c = self.c
        if c.testiliik:
            q = q.filter(model.Test.testiliik_kood.in_(c.testiliik))
        if c.sessioon_id:
            q = q.filter(model.Testimiskord.testsessioon_id.in_(c.sessioon_id))
        if c.test_id:
            q = q.filter(model.Testimiskord.test_id==c.test_id)
        if c.isikukood:
            usp = validators.IsikukoodP(self.c.isikukood)
            q = q.filter(usp.filter(model.Kasutaja))

        if c.eesnimi:
            q = q.filter(model.Kasutaja.eesnimi.ilike(c.eesnimi))
        if c.perenimi:
            q = q.filter(model.Kasutaja.perenimi.ilike(c.perenimi))
        if c.aine:
            q = q.filter(model.Test.aine_kood==c.aine)

        return q

    def _prepare_items(self, c_items=None, is_csv=False):
        """Päringutulemuste paigutamine väljastamiseks sobivale kujule"""
        set_grupp_id = set(self.c.grupp_id)
        s = set([const.GRUPP_HINDAJA_S,
                 const.GRUPP_HINDAJA_S2,
                 const.GRUPP_INTERVJUU,
                 const.GRUPP_VAATLEJA,
                 const.GRUPP_KOMISJON,
                 const.GRUPP_KONSULTANT,
                 const.GRUPP_T_ADMIN])
        on_kohtaeg = set_grupp_id.intersection(s)
        on_khindaja = const.GRUPP_HINDAJA_K in set_grupp_id
        on_shindaja = const.GRUPP_HINDAJA_S in set_grupp_id        
        on_s2hindaja = const.GRUPP_HINDAJA_S2 in set_grupp_id
        on_intervjuu = const.GRUPP_INTERVJUU in set_grupp_id
        on_vaidehindaja = const.GRUPP_HINDAMISEKSPERT in set_grupp_id
        
        on_miturolli = len(set_grupp_id) > 1 or on_shindaja or on_intervjuu
        # suulise I hindaja või intervjueerija korral kuvatakse ka hindaja-intervjueerija,
        # seetõttu on mitu rolli
        
        header = [('kasutaja.isikukood', _("Isikukood")),
                  ('kasutaja.eesnimi', _("Eesnimi")),
                  ('kasutaja.perenimi', _("Perekonnanimi")),
                  ]
        header += [('test.nimi', _("Test")),
                   ('toimumisaeg.tahised', _("Toimumisaja tähised")),
                   ('toimumisaeg.alates', _("Aeg")),
                   ]
        
        if not is_csv and on_miturolli:
            header += [('labiviija.kasutajagrupp_id', _("Roll")),
                       ]
            
        if on_khindaja or on_s2hindaja:
            header += [('hindamiskogum.tahis', _("Hindamiskogum")),
                       ]

        if const.TESTILIIK_RIIGIEKSAM in self.c.testiliik \
          or const.TESTILIIK_POHIKOOL in self.c.testiliik:
            if on_shindaja or on_khindaja or on_s2hindaja:
                header += [('labiviija.liik', _("Liik")),
                           ('labiviija.lang', _("Keel")),
                               ]
        else:
            if on_khindaja or on_s2hindaja:
                header += [('labiviija.liik', _("Liik")),
                               ]
        if on_shindaja or on_khindaja or on_s2hindaja or on_intervjuu or on_vaidehindaja:
            header += [('labiviija.tasu_toode_arv', _("Tööde arv")),
                       ]
            
        if on_kohtaeg:
            header += [('koht.nimi', _("Soorituskoht")),
                       ]
            
        header += [(None, _("Maksumus")),
                   ('kasutaja.epost', _("E-post")),
                   ]

        if is_csv:
            header = [('labiviijaleping.id', _("Lepingu ID")),
                      ('leping.nimetus', _("Lepingu liik")),
                      ('labiviija.id', _("Läbiviija ID")),
                      ] + header + \
                      [('profiil.arveldusarve', _("Arveldusarve")),
                       ]

        items = []
        n_labiviija = 11
        n_koht = 12
        n_hk = on_kohtaeg and 15 or 12
        format = self._getformat()
        for rcd in c_items or self.c.items:
            k_id, k_epost, k_eesnimi, k_perenimi, k_ik, aine, testiliik, test_nimi, ta_tahised, alates, arvenr, lv = \
                rcd[:n_labiviija+1]

            item = [k_ik,
                    k_eesnimi,
                    k_perenimi,
                    test_nimi,
                    ta_tahised,
                    ]
            if is_csv:
                lleping_id, leping_liik = rcd[-2:]
                item = [lleping_id, leping_liik, lv.id] + item

            if not format:
                # kuvatakse veebis koos märkeruuduga
                item.insert(0, lv.id)
            if on_kohtaeg:
                koht_nimi, tr_algus, tk_algus = rcd[n_koht:n_koht+3]
                alates = tr_algus or tk_algus or alates  
           
            item.append(self.h.str_from_date(alates))
            if not is_csv and on_miturolli:
                roll = lv.kasutajagrupp_nimi
                item.append(roll)              
           
            # kui toimumisaeg.on_ruumiprotokoll, siis on aeg väljal tr_algus, muidu tk_algus
            if on_khindaja or on_s2hindaja:
                hk_tahis = rcd[n_hk]
                item += [hk_tahis or '-',
                         ]

            if const.TESTILIIK_RIIGIEKSAM in self.c.testiliik \
              or const.TESTILIIK_POHIKOOL in self.c.testiliik:
                if on_shindaja or on_khindaja or on_s2hindaja:
                    item += [lv.liik_nimi,
                             lv.lang_nimi,
                             ]
            else:
                if on_khindaja or on_s2hindaja:
                    item += [lv.liik_nimi,
                             ]
            if on_shindaja or on_khindaja or on_s2hindaja or on_intervjuu or on_vaidehindaja:
                item += [lv.tasu_toode_arv,
                         ]
                
            if on_kohtaeg:
                item += [koht_nimi,
                         ]

            tasu = lv.get_tasu()
            if is_csv:
                # Excel ei kuva euro märki
                tasu = self.h.fstr(tasu, 2)
            else:
                tasu = self.h.mstr(tasu)

            item += [tasu,
                     k_epost]

            if is_csv:
                item.append(arvenr)

            items.append(item)

        return header, items

    def _prepare_items_csv2(self, c_items=None):
        """Päringutulemuste paigutamine väljastamiseks sobivale kujule"""
        set_grupp_id = set(self.c.grupp_id)
        s = set([const.GRUPP_HINDAJA_S,
                 const.GRUPP_HINDAJA_S2,
                 const.GRUPP_INTERVJUU,
                 #const.GRUPP_HIND_INT,
                 const.GRUPP_VAATLEJA,
                 const.GRUPP_KOMISJON,
                 const.GRUPP_KONSULTANT,
                 const.GRUPP_T_ADMIN])
        on_kohtaeg = set_grupp_id.intersection(s)
        on_khindaja = const.GRUPP_HINDAJA_K in set_grupp_id
        on_shindaja = const.GRUPP_HINDAJA_S in set_grupp_id        
        on_s2hindaja = const.GRUPP_HINDAJA_S2 in set_grupp_id
        on_intervjuu = const.GRUPP_INTERVJUU in set_grupp_id
        on_vaidehindaja = const.GRUPP_HINDAMISEKSPERT in set_grupp_id
        
        on_miturolli = len(set_grupp_id) > 1 or on_shindaja or on_intervjuu
        # suulise I hindaja või intervjueerija korral kuvatakse ka hindaja-intervjueerija,
        # seetõttu on mitu rolli

        header = [('labiviijaleping.id', _("Lepingu ID")),
                  ('leping.nimetus', _("Lepingu liik")),
                  ('kasutaja.isikukood', _("Isikukood")),
                  ('kasutaja.eesnimi', _("Eesnimi")),
                  ('kasutaja.perenimi', _("Perekonnanimi")),
                  (None, _("Maksumus")),
                  ('kasutaja.epost', _("E-post")),
                  ('profiil.arveldusarve', _("Arveldusarve")),
                  ]

        items = []
        itempos = dict()
        n_labiviija = 11
        n_koht = 12
        n_hk = on_kohtaeg and 15 or 12

        c_tasu = 5 # maksumuse veeru indeks CSV-s
        
        for rcd in c_items or self.c.items:
            k_id, k_epost, k_eesnimi, k_perenimi, k_ik, aine, testiliik, test_nimi, ta_tahised, alates, arvenr, lv = \
                rcd[:n_labiviija+1]
            lleping_id, leping_liik = rcd[-2:]

            tasu = lv.get_tasu()

            itemkey = k_id, lleping_id
            k_ind = itempos.get(itemkey)
            if k_ind is not None:
                # isik on juba tulemuste seas
                if tasu is not None:
                    if items[k_ind][c_tasu]:
                        items[k_ind][c_tasu] += tasu
                    else:
                        items[k_ind][c_tasu] = tasu
            else:
                # uus isik tulemustesse
                item = [lleping_id,
                        leping_liik,
                        k_ik,
                        k_eesnimi,
                        k_perenimi,
                        tasu,
                        k_epost,
                        arvenr,
                        ]
                itempos[itemkey] = len(items)
                items.append(item)

        # teeme raha stringiks
        for item in items:
            item[c_tasu] = self.h.fstr(item[c_tasu], 2)

        return header, items

    def create(self):
        format = self._getformat()
        if format:
            self._copy_list_url_params()
            q = self._search(self._query())
            if q:
                q = self._search_format(q)
                if isinstance(q, (HTTPFound, Response)):
                    # q pole päring, vaid ümbersuunamine
                    return q
                else:
                    q = self._order(q)
                    model.log_query(q)
                    self.c.items = q.all()
                
                    if format == 'csv':
                        data, filename = self._render_csv()
                        mimetype = const.CONTENT_TYPE_CSV
                        return utils.download(data, filename, mimetype)

                    elif format == 'csv2':
                        data, filename = self._render_csv2()
                        mimetype = const.CONTENT_TYPE_CSV
                        return utils.download(data, filename, mimetype)                                

                    elif format == 'pdf':
                        data, filename = self._render_pdf()
                        mimetype = const.CONTENT_TYPE_PDF
                        return utils.download(data, filename, mimetype)            

                    elif format == 'tcsv':
                        # sisestused tunnis, vt sisestajad.py
                        data, filename = self._render_tcsv(q)
                        mimetype = const.CONTENT_TYPE_CSV
                        return utils.download(data, filename, mimetype)            

        return self._redirect('index', getargs=True)

    def _filter_checked(self, q):
        "Päringut kitsendatakse, et see annaks välja ainult need read, mis on linnutatud"
        labiviijad_id = list(map(int, self.request.params.getall('lv_id')))
        q = q.filter(model.Labiviija.id.in_(labiviijad_id))
        return q
    
    def _search_format(self, q):
        format = self._getformat()
        if format and not self.request.params.get('valikoik'):
            # vaatame ainult neid ridu, mis on märkeruuduga valitud
            q = self._filter_checked(q)
        #model.log_query(q)

        if format == 'akt':
            if not self.c.aktimall:
                self.error(_("Akti malli ei õnnestu määrata"))
            else:
                sort = self._sort_by_kasutaja()
                q = self._order(q, sort)
                data, filename = self._render_akt(q)
                mimetype = const.CONTENT_TYPE_PDF
                return utils.download(data, filename, mimetype)            

        elif format == 'mail':
            if not self.c.aktimall:
                self.error(_("Akti malli ei õnnestu määrata"))
            else:
                self._send_mail(q)
            return self._redirect('index', getargs=True, mail=None)

        return q

    def _vali_mallid(self, testiliik, grupid_id, sessioon_id, test_id):
        "Aruande pealkirja ja akti genereerimiseks kasutatava malli määramine"
        title = _("Läbiviijate aruanne")
        aktimall = None

        if const.TESTILIIK_TASE in testiliik:
            # kui on tasemeeksami sessioon, siis on tasemeeksami mall
            if len(grupid_id - set([const.GRUPP_HINDAJA_K, const.GRUPP_HINDAJA_S2, const.GRUPP_HINDAMISEKSPERT])) == 0:
                aktimall = 'tehindaja'
            else:
                aktimall = 'tasemeeksam'

        elif const.TESTILIIK_SEADUS in testiliik:
            # kui on tasemeeksami sessioon, siis on tasemeeksami mall
            if len(grupid_id - set([const.GRUPP_HINDAJA_K, const.GRUPP_HINDAJA_S2, const.GRUPP_HINDAMISEKSPERT])) == 0:
                aktimall = 'sehindaja'
            else:
                aktimall = 'seadus'

        else:
            if len(grupid_id - set([const.GRUPP_VAATLEJA])) == 0:
                aktimall = 'vaatleja' 
            else:
                aktimall = 'riigieksam'
                # varasemad mallid: rv,riigieksam,pohikool

            if len(grupid_id) == 1:
                if const.GRUPP_KOMISJON in grupid_id:
                    title = _("Komisjoniliikmete aruanne")
                elif const.GRUPP_INTERVJUU in grupid_id:
                    title = _("Intervjueerijate aruanne")
                elif const.GRUPP_VAATLEJA in grupid_id:
                    title = _("Vaatlejate aruanne")
                    aktimall = 'vaatleja'                    
                elif const.GRUPP_KONSULTANT in grupid_id:
                    title = _("Konsultantide aruanne")
                elif const.GRUPP_HINDAJA_S in grupid_id:
                    title = _("Suuliste hindajate aruanne")
                elif const.GRUPP_HINDAJA_S2 in grupid_id:
                    title = _("Suuliste hindajate aruanne")
                elif const.GRUPP_HINDAJA_K in grupid_id:
                    title = _("Kirjalike hindajate aruanne")
                elif const.GRUPP_HINDAMISEKSPERT in grupid_id:
                    title = _("Vaidehindajate aruanne")
                elif const.GRUPP_T_ADMIN in grupid_id:
                    title = _("Testi administraatorite aruanne")
        return title, aktimall

    def _sort_by_kasutaja(self):
        """Aktide koostamisel peavad sortimistingimused olema sellised, et kasutaja kirje on koos.
        Selleks lisame enne esimest mitte-kasutaja tabeli tingimust tingimuse kasutaja.id.
        """
        sort = self.c.sort or self._DEFAULT_SORT
        li = sort.split(',')
        n = 0
        for n in range(len(li)):
            s = li[n]
            if not s.startswith('kasutaja.') and not s.startswith('-kasutaja.'):
                break
        li[n:n] = ['kasutaja.id']
        if 'kasutaja.eesnimi' not in li:
            li[n:n] = ['kasutaja.eesnimi']                
        if 'kasutaja.perenimi' not in li:
            li[n:n] = ['kasutaja.perenimi']
        sort = ','.join(li)
        return sort

    def _txt_eksamitel(self, testiliigid):
        "Testiliigi sõnastamine"

        map_liik = {const.TESTILIIK_POHIKOOL: 'põhikooli lõpueksamitel',
                    const.TESTILIIK_RIIGIEKSAM: 'riigieksamitel',
                    const.TESTILIIK_RV: 'rahvusvahelistel võõrkeeleeksamitel',
                    }
        li = [map_liik.get(liik) for liik in testiliigid]
        eksamitel = 'eksamitel'
        if None not in li:
            # komadega ühendamine, lõpus "ja"
            eksamitel = utils.joinand(li)
        return eksamitel
    
    def _send_mail(self, q):
        
        aktimall = self.c.aktimall
        sort = self._sort_by_kasutaja()
        q = q.filter(model.Kasutaja.epost!=None)
        q = self._order(q, sort)
        mako = 'mail/labiviijatasu.%s.mako' % aktimall
        taiendavinfo = self.request.params.get('taiendavinfo')
        cnt = 0 # saadetud kirjade arv

        n_labiviija = 11 # läbiviija asukoht päringutulemuste kirjes

        for (kasutaja_id), group_rows in groupby(list(q.all()), lambda r: r[0]):
            # yhele kasutajale kirja saatmine
            rows = [r for r in group_rows]
            testiliigid = set([r[6] for r in rows])
            eksamitel = self._txt_eksamitel(testiliigid)
        
            doc = LabiviijakiriDoc(rows, aktimall, grupeeritud=True, testiliik=testiliigid,
                                   taiendavinfo=taiendavinfo)
            filedata = doc.generate()
            filename = '%s.pdf' % aktimall
            attachments = [(filename, filedata)]
            isik_nimi = '%s %s' % (rows[0][2], rows[0][3])

            epost = rows[0][1]
            data = {'isik_nimi': isik_nimi,
                    'user_nimi': self.c.user.fullname,
                    'eksamitel': eksamitel,
                    }
            subject, body = self.render_mail(mako, data)
            body = Mailer.replace_newline(body)
            if Mailer(self).send(epost, subject, body, attachments):
                # viga, mis takistab edasist tööd
                break
            else:
                # kiri saadetud
                cnt += 1
                kiri = model.Kiri(saatja_kasutaja_id=self.c.user.id,
                                  tyyp=model.Kiri.TYYP_LABIVIIJA_TASU,
                                  sisu=body,
                                  teema=subject,
                                  filename=filename,
                                  filedata=filedata,
                                  teatekanal=const.TEATEKANAL_EPOST)
                for row in rows:
                    lv = row[n_labiviija]
                    if isinstance(lv, model.Labiviija):
                        # kui ei ole sisestajate päring
                        model.Labiviijakiri(labiviija=lv, kiri=kiri)
                model.Kirjasaaja(kiri=kiri, kasutaja_id=kasutaja_id, epost=epost)
                model.Session.commit()
                
        if cnt > 1:
            self.success(_("Saadetud {n} kirja").format(n=cnt))
        elif cnt == 1:
            self.success(_("Saadetud {n} kiri").format(n=cnt))
        else:
            self.notice(_("Ei saadetud ühtki kirja"))

    def _paginate(self, q):
        # et failina laadimisel ei pagineeriks
        format = self._getformat()
        if format:
            return q.all()
        else:
            return BaseResourceController._paginate(self, q)

    def _getformat(self):
        for key in ('csv', 'csv2', 'tcsv', 'pdf'):
            if self.request.params.get(key):
                return key
        # akt,mail tulevad op väärtusena
        return self.request.params.get('op')

    def _showlist(self):
        """Otsingu tulemuste kuvamine.
        """
        self.c.prepare_items = self._prepare_items
        if self.request.params.get('partial'):
            return self.render_to_response(self._LIST_TEMPLATE)
        else:
            return self.render_to_response(self._INDEX_TEMPLATE)

    def _render_csv(self):
        header, items = self._prepare_items(is_csv=True)
        data = ';'.join([r[1] for r in header]) + '\n'
        for item in items:
            item = [s and str(s) or '' for s in item]
            data += ';'.join(item) + '\n'

        data = utils.encode_ansi(data)
        filename = 'labiviijad.csv'
        return data, filename

    def _render_csv2(self):
        header, items = self._prepare_items_csv2()
        data = ';'.join([r[1] for r in header]) + '\n'
        for item in items:
            item = [s and str(s) or '' for s in item]
            data += ';'.join(item) + '\n'

        data = utils.encode_ansi(data)
        filename = 'labiviijad_lepingud.csv'
        return data, filename

    def _render_pdf(self):
        header, items = self._prepare_items()
        header = [r[1] for r in header]
        items = [[s and str(s) or '' for s in item] for item in items]

        doc = LabiviijadDoc(header, items, self.c.rep_title)
        data = doc.generate()
        filename = 'labiviijad.pdf'
        return data, filename

    def _render_akt(self, q):
        """Kõigi läbiviijate aktide dokumendi genereerimine
        """
        doc = LabiviijaaktDoc(q.all(),
                              self.c.aktimall,
                              grupid_id=set(self.c.grupp_id),
                              testiliik=self.c.testiliik,
                              taiendavinfo=self.request.params.get('taiendavinfo'))
        data = doc.generate()
        filename = '%s_akt.pdf' % self.c.aktimall
        return data, filename

    def _copy_list_url_params(self):
        list_url = self.request.params.get('list_url')
        if list_url:
            # kui kasutaja vajutas formati nuppudele,
            # siis otingutingimused võetakse list_url väljalt

            # eemaldame raja, et jääks ainult parameetrid
            list_url = list_url.split('?', 1)[-1]

            res = urllib.parse.parse_qs(list_url)
            params = dict()
            for key in res:
                if key in ('grupp_id','testiliik','sessioon_id'):
                    # listina antavad parameetrid
                    params[key] = res[key]
                else:
                    # yhekordsed parameetrid
                    params[key] = res[key][0]

            data = self._SEARCH_FORM.to_python(params)
            for key in data:
                self.c.__setattr__(key, data[key])
