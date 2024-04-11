from eis.lib.baseresource import *
_ = i18n._
from .labiviijad import LabiviijadController

log = logging.getLogger(__name__)

class SisestajadController(LabiviijadController):
    """Läbiviijate aruanded
    """
    _LIST_TEMPLATE = 'ekk/otsingud/labiviijad_list.mako'
    _DEFAULT_SORT = 'kasutaja.perenimi,kasutaja.eesnimi'
    
    def _search(self, q1):
        # otsitakse kasutajad, kes on olnud esimene või teine sisestaja
        c = self.c
        c.rep_title = _("Sisestajate aruanne")

        # TE, SE saab ainult eraldi valida
        if const.TESTILIIK_TASE in c.testiliik:
            c.testiliik = [const.TESTILIIK_TASE]
            c.aktimall = 'tesisestaja'
        elif const.TESTILIIK_SEADUS in c.testiliik:
            c.testiliik = [const.TESTILIIK_SEADUS]
            c.aktimall = 'sesisestaja'
        else:
            c.aktimall = 'sisestaja'
        
        li_select = self._select_fields + \
                    [model.Sisestuskogum.tahis,
                     model.Sisestuskogum.nimi,                     
                     model.Sisestuskogum.tasu,
                     model.Toimumisaeg.id,
                     model.Sisestuskogum.id,
                     ]

        format = self._getformat()
        if format == 'tcsv':
            # sisestused tunnis
            expr_algus = sa.sql.expression.case([(model.Sisestusolek.sisestaja1_kasutaja_id==model.Kasutaja.id,
                                                  model.Sisestusolek.sisestaja1_algus)],
                                                else_=model.Sisestusolek.sisestaja2_algus)
            li_select.append(sa.func.date_trunc('hour', expr_algus))

        li_params = li_select + [sa.func.count(model.Sisestusolek.id)]

        q = model.Session.query(*li_params)
        q = (q.join(model.Toimumisaeg.sooritused)
             .join(model.Sooritus.sisestusolekud)
             .join((model.Sisestuskogum,
                    model.Sisestuskogum.id==model.Sisestusolek.sisestuskogum_id))
             )

        f1 = sa.and_(model.Sisestusolek.sisestaja1_kasutaja_id==model.Kasutaja.id,
                     model.Sisestusolek.staatus1==const.H_STAATUS_HINNATUD)
        f2 = sa.and_(model.Sisestusolek.sisestaja2_kasutaja_id==model.Kasutaja.id,
                     model.Sisestusolek.staatus2==const.H_STAATUS_HINNATUD)
        if c.alates:
            f1 = sa.and_(f1,
                         model.Sisestusolek.sisestaja1_algus>=c.alates)
            f2 = sa.and_(f2,
                         model.Sisestusolek.sisestaja2_algus>=c.alates)
        if c.kuni:
            f1 = sa.and_(f1,
                         model.Sisestusolek.sisestaja1_algus<c.kuni+timedelta(1))
            f2 = sa.and_(f2,
                         model.Sisestusolek.sisestaja2_algus<c.kuni+timedelta(1))                         
        q = q.filter(sa.or_(f1, f2))

        q = (q.join(model.Toimumisaeg.testimiskord)
             .join(model.Testimiskord.test)
             .outerjoin(model.Kasutaja.profiil))

        if c.toimumisaeg_id:
            q = q.filter(model.Sooritus.toimumisaeg_id==int(c.toimumisaeg_id))
        elif c.sessioon_id:
            sessioonid_id = list(map(int, c.sessioon_id))
            if len(c.sessioon_id) == 1:
                q = q.filter(model.Testimiskord.testsessioon_id==sessioonid_id[0])
            else:
                q = q.filter(model.Testimiskord.testsessioon_id.in_(sessioonid_id))

        q = self._search_filter(q)
        q = q.group_by(*li_select)

        return q

    def _prepare_items(self, c_items=None, is_csv=False):
        format = self._getformat()
        header = [('kasutaja.isikukood', _("Isikukood")),
                  ('kasutaja.eesnimi', _("Eesnimi")),
                  ('kasutaja.perenimi', _("Perekonnanimi")),
                  ('test.nimi', _("Test")),
                  ('toimumisaeg.tahised', _("Toimumisaja tähised")),
                  ('sisestuskogum.tahis', _("Sisestuskogum")),
                  (None, _("Arv")),
                  (None, _("Maksumus")),
                  ('kasutaja.epost', _("E-post")),                  
                  ]
        if is_csv:
            header += [('profiil.arveldusarve', _("Arveldusarve")),
                       ]

        items = []
        for rcd in c_items or self.c.items:
            k_id, k_epost, k_eesnimi, k_perenimi, k_ik, aine, testiliik, test_nimi, ta_tahised, alates, arvenr, sk_tahis, sk_nimi, sk_tasu, ta_id, sk_id, cnt = rcd

            tasu = cnt * (sk_tasu or 0)
            if is_csv:
                # Excel ei kuva euro märki
                tasu = self.h.fstr(tasu, 2)
            else:
                tasu = self.h.mstr(tasu)

            item = [k_ik,
                    k_eesnimi,
                    k_perenimi,
                    test_nimi,
                    ta_tahised,
                    sk_tahis,
                    cnt,
                    tasu,
                    k_epost]
            if not format:
                # kuvatakse veebis koos märkeruuduga
                item.insert(0, '%s/%s/%s' % (k_id, ta_id, sk_id))
            if is_csv:
                item.append(arvenr)
            items.append(item)

        return header, items

    def _filter_checked(self, q):
        "Päringut kitsendatakse, et see annaks välja ainult need read, mis on linnutatud"
        labiviijad_id = self.request.params.getall('lv_id')
        f = []
        for lv_id in labiviijad_id:
            k_id, ta_id, sk_id = list(map(int, lv_id.split('/')))
            crit = sa.and_(model.Kasutaja.id==k_id,
                           model.Toimumisaeg.id==ta_id,
                           model.Sisestuskogum.id==sk_id)
            f.append(crit)
        q = q.filter(sa.or_(*f))
        return q
    
    def _render_tcsv(self, q):
        "Sisestused tunnis, CSV"
        header, items = self._prepare_items_tunnis(q)
        #header = [r[1] for r in header]
        data = ';'.join(header) + '\n'
        for item in items:
            item = [s and str(s) or '' for s in item]
            data += ';'.join(item) + '\n'

        data = utils.encode_ansi(data)
        filename = 'sisestused_tunnis.csv'
        return data, filename

    def _prepare_items_tunnis(self, q):
        header = [_("Testi nimetus"),
                  _("Toimumisaja tähis"),
                  _("Sisestuskogum"),
                  _("Sisestaja eesnimi"),
                  _("Sisestaja perekonnanimi"),
                  _("Kuupäev"),
                  _("Tund"),
                  _("Sisestuste arv tunnis"),
                  ]
        items = []
        for rcd in q.all():
            k_id, epost, k_eesnimi, k_perenimi, k_ik, aine, testiliik, test_nimi, ta_tahised, alates, arvenr, sk_tahis, sk_nimi, sk_tasu, ta_id, sk_id, paevtund, cnt = rcd
            kpv = paevtund and self.h.str_from_date(paevtund) or ''
            tund = paevtund and str(paevtund.hour) or ''
            item = [test_nimi,
                    ta_tahised,
                    sk_tahis,
                    k_eesnimi,
                    k_perenimi,
                    kpv,
                    tund,
                    cnt,
                    ]
            items.append(item)
        return header, items

