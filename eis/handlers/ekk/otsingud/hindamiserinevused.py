from eis.lib.baseresource import *
_ = i18n._
from eis.lib.pdf.hindamiserinevused import HindamiserinevusedDoc

log = logging.getLogger(__name__)

class HindamiserinevusedController(BaseResourceController):
    """Kolmandat hindamist vajavate testitööde loetelu.
    Kolmandat hindamist on vaja siis, kui on kahekordne hindamine
    ja I ning II hindaja hindavad liiga suure erinevusega.
    """
    _permission = 'aruanded-erinevused'
    _MODEL = model.Hindamisolek
    _INDEX_TEMPLATE = 'ekk/otsingud/hindamiserinevused.otsing.mako'
    _LIST_TEMPLATE = 'ekk/otsingud/hindamiserinevused_list.mako'
    _DEFAULT_SORT = 'sooritus.tahised'
    _ignore_default_params = ['csv', 'tryki']
    
    def _query(self):
        self.c.opt_sessioon = self.c.opt.testsessioon

    def _search_default(self, q):
        return self._search(q)

    def _search(self, q1):
        self.c.prepare_header = self._prepare_header
        self.c.prepare_item = self._prepare_item
        
        if self.c.ta_tahised and (self.c.otsi or self.c.tryki):
            # on antud toimumisaja tähis ja vajutati nupule Otsi
            # (mitte ei valitud loetelust toimumisaega)
            self.c.ta_tahised = self.c.ta_tahised.strip().replace('+','-').upper()
            li_ta = self.c.ta_tahised.split('-')
            if len(li_ta) != 3:
                self.error(_("Sisesta toimumisaja tähis 3-osalisena"))
            else:
                ta = model.Toimumisaeg.query.filter_by(tahised=self.c.ta_tahised).first()
                if not ta:
                    self.error(_("Sellise tähisega toimumisaega ei leitud"))
                else:
                    self.c.toimumisaeg_id = ta.id

        q = ta = None
        if self.c.toimumisaeg_id:
            # toimumisaeg on valitud - kas valikust või tähisega
            self.c.toimumisaeg = ta = model.Toimumisaeg.get(self.c.toimumisaeg_id)
            if ta:
                self.c.sessioon_id = ta.testimiskord.testsessioon_id
                self.c.ta_tahised = ta.tahised
                hkogumid = [hk for hk in ta.testiosa.hindamiskogumid \
                            if hk.staatus and (hk.kahekordne_hindamine or hk.kahekordne_hindamine_valim)]
                self.c.opt_hindamiskogum = [(hk.id, '%s - %s' % (hk.tahis, hk.nimi)) \
                                            for hk in hkogumid]
                if len(hkogumid) == 0:
                    self.error(_("Valitud testiosal ei ole ühtki kahekordse hindamisega hindamiskogumit"))
                else:
                    if not self.c.hindamiskogum_id:
                        self.c.hindamiskogum_id = hkogumid[0].id
                        self.c.hindamiskogum = hkogumid[0]
                    else:
                        self.c.hindamiskogum = model.Hindamiskogum.get(self.c.hindamiskogum_id)
                    q = self._query_erinevused(ta.id, self.c.hindamiskogum_id)
                    self.c.query_ylesandehinded = self._query_ylesandehinded
                    if self.c.tryki:
                        return self._gen_pdf(ta, self.c.hindamiskogum, q, self.c.punktides)
                    if self.c.csv:
                        return self._index_csv(q)

        if self.c.sessioon_id:
            self.c.opt_toimumisaeg = model.Toimumisaeg.get_opt(self.c.sessioon_id) 

        return q
    
    def _query_erinevused(self, ta_id, hindamiskogum_id):
        Hindamine1 = sa.orm.aliased(model.Hindamine, name='hindamine1')
        Hindamine2 = sa.orm.aliased(model.Hindamine, name='hindamine2')
        Kasutaja1 = sa.orm.aliased(model.Kasutaja, name='kasutaja1')
        Kasutaja2 = sa.orm.aliased(model.Kasutaja, name='kasutaja2')

        Hindamine3 = sa.orm.aliased(model.Hindamine, name='hindamine3')

        q = model.SessionR.query(model.Testikoht.tahis,
                                model.Testiprotokoll.tahis,
                                model.Sooritus.tahised,
                                model.Hindamisolek,
                                Hindamine1.id,
                                Hindamine1.pallid,
                                Kasutaja1.nimi,
                                Hindamine2.id,
                                Hindamine2.pallid,
                                Kasutaja2.nimi)
        q = q.filter(model.Sooritus.toimumisaeg_id==ta_id).\
            join(model.Sooritus.hindamisolekud).\
            filter(model.Hindamisolek.hindamiskogum_id==hindamiskogum_id).\
            filter(sa.or_(model.Hindamisolek.hindamistase>=3,
                          sa.and_(model.Hindamisolek.hindamistase==2,
                                  model.Hindamisolek.hindamisprobleem==const.H_PROBLEEM_HINDAMISERINEVUS))).\
            filter(model.Sooritus.staatus==const.S_STAATUS_TEHTUD).\
            join(model.Sooritus.testiprotokoll).\
            join(model.Sooritus.testikoht).\
            join((Hindamine1, sa.and_(Hindamine1.hindamisolek_id==model.Hindamisolek.id,
                                      Hindamine1.sisestus==1,
                                      Hindamine1.tyhistatud==False,
                                      Hindamine1.liik==const.HINDAJA1))).\
            join((Kasutaja1, Kasutaja1.id==Hindamine1.hindaja_kasutaja_id)).\
            join((Hindamine2, sa.and_(Hindamine2.hindamisolek_id==model.Hindamisolek.id,
                                      Hindamine2.sisestus==1,
                                      Hindamine2.tyhistatud==False,
                                      Hindamine2.liik==const.HINDAJA2))).\
            join((Kasutaja2, Kasutaja2.id==Hindamine2.hindaja_kasutaja_id))                                                

        q = q.outerjoin((Hindamine3, sa.and_(Hindamine3.hindamisolek_id==model.Hindamisolek.id,
                                             Hindamine3.liik==const.HINDAJA3,
                                             Hindamine3.sisestus==1,
                                             Hindamine3.tyhistatud==False)))

        if self.c.jagamata:
            # kolmanda hindamise kirjet pole või pole selle hindajat
            q = q.filter(Hindamine3.hindaja_kasutaja_id==None)
        
        return q
 
    def _query_ylesandehinded(self, hindamine_id):
        q = model.SessionR.query(model.Ylesandevastus.testiylesanne_id,
                                model.Ylesandehinne.toorpunktid,
                                model.Ylesandehinne.pallid).\
            filter(model.Ylesandehinne.hindamine_id==hindamine_id).\
            join(model.Ylesandehinne.ylesandevastus)
        d = {}
        for ty_id, toorpunktid, pallid in q.all():
            d[ty_id] = (toorpunktid, pallid)
        return d

    def _gen_pdf(self, ta, hkogum, q, punktides):
        q = q.order_by(model.Sooritus.tahised)
        doc = HindamiserinevusedDoc(ta, hkogum, q, self._query_ylesandehinded, punktides)
        data = doc.generate()
        filename = 'hindamiserinevused.pdf'
        mimetype = const.CONTENT_TYPE_PDF
        return utils.download(data, filename, mimetype)

    def _prepare_header(self):
        c = self.c
        header = [_("Jrk"),
                  ('testiprotokoll.tahised', _("Protokolli tähis")),
                  ('sooritus.tahised', _("Testitöö tähis")),
                  ]
        header.append(('kasutaja1.nimi', _("1. hindaja")))
        for ty in c.hindamiskogum.testiylesanded:
            title = ty.alatest_seq and '%s.%s' % (ty.alatest_seq, ty.seq) or '%s' % ty.seq
            header.append(_("Ül {s}").format(s=title))
        n_kokku1 = len(header)
        header.append(('hindamine1.pallid', _("Kokku")))

        header.append(('kasutaja2.nimi', _("2. hindaja")))
        for ty in c.hindamiskogum.testiylesanded:
            title = ty.alatest_seq and '%s.%s' % (ty.alatest_seq, ty.seq) or '%s' % ty.seq
            header.append(_("Ül {s}").format(s=title))
        n_kokku2 = len(header)
        header.append(('hindamine2.pallid', _("Kokku")))

        header.append(('hindamisolek.hindamiserinevus', _("Vahe")))
        self.c.header_bold = [n_kokku1, n_kokku2]
        return header
    
    def _prepare_item(self, rcd, n):
        c = self.c
        tk_tahis, pr_tahis, s_tahised, holek, h1_id, h1_pallid, h1_nimi, h2_id, h2_pallid, h2_nimi = rcd
        item = [n+1,
                '%s-%s' % (tk_tahis, pr_tahis),
                s_tahised,
                ]

        def _tulemus(punktid, pallid):
            if c.punktides:
                return self.h.fstr(punktid)
            else:
                return '%s (%s)' % (self.h.fstr(pallid), self.h.fstr(punktid))

        d = c.query_ylesandehinded(h1_id)
        punktid1 = 0
        item.append(h1_nimi)
        for ty in c.hindamiskogum.testiylesanded:
            v = d.get(ty.id)
            if v:
                punktid1 += v[0]
                item.append(_tulemus(v[0], v[1]))
            else:
                item.append('')
        item.append(_tulemus(punktid1, h1_pallid))

        d = c.query_ylesandehinded(h2_id)
        punktid2 = 0
        item.append(h2_nimi)
        for ty in c.hindamiskogum.testiylesanded:
            v = d.get(ty.id)
            if v:
                punktid2 += v[0]
                item.append(_tulemus(v[0], v[1]))
            else:
                item.append('')
        item.append(_tulemus(punktid2, h2_pallid))

        if c.punktides:
            item.append(self.h.fstr(abs(punktid2-punktid1)))
        else:
            item.append(self.h.fstr(holek.hindamiserinevus))

        return item
