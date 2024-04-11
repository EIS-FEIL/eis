from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class Hindamised3Controller(BaseResourceController):

    _permission = 'hindamisanalyys'
    _MODEL = model.Hindamisolek
    _INDEX_TEMPLATE = 'ekk/hindamine/analyys.hindamised3.mako'
    _LIST_TEMPLATE = 'ekk/hindamine/analyys.hindamised3_list.mako'
    _DEFAULT_SORT = 'sooritus.id' # vaikimisi sortimine 

    def _search_default(self, q):
        return self._search(q)

    def _search(self, q1):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        if self.c.punktides:
            self.c.punktides = int(self.c.punktides)
            self.c.leia_punktid = lambda hindamine_id: hindamine_id and \
                model.SessionR.query(sa.func.sum(model.Ylesandehinne.toorpunktid)).\
                filter(model.Ylesandehinne.hindamine_id==hindamine_id).\
                scalar()

        Hindamine1 = sa.orm.aliased(model.Hindamine, name='hindamine_1')
        Kasutaja1 = sa.orm.aliased(model.Kasutaja, name='kasutaja_1')

        Hindamine2 = sa.orm.aliased(model.Hindamine, name='hindamine_2')
        Kasutaja2 = sa.orm.aliased(model.Kasutaja, name='kasutaja_2')

        Hindamine3 = sa.orm.aliased(model.Hindamine, name='hindamine_3')

        q = model.SessionR.query(model.Sooritus.id,
                                model.Sooritaja.eesnimi,
                                model.Sooritaja.perenimi,
                                model.Sooritus.tahised,
                                model.Hindamiskogum.id,
                                model.Hindamiskogum.tahis,
                                Kasutaja1.nimi,
                                Hindamine1.id,
                                Hindamine1.pallid,
                                Kasutaja2.nimi,
                                Hindamine2.id,
                                Hindamine2.pallid,
                                Hindamine3.staatus,
                                Hindamine3.id,
                                Hindamine3.pallid)
        q = (q.join(model.Sooritaja.sooritused)
             .filter(model.Sooritus.toimumisaeg_id==self.c.toimumisaeg.id)
             .join(model.Sooritus.hindamisolekud)
             .join(model.Hindamisolek.hindamiskogum))
        q = q.filter(model.Hindamisolek.hindamistase>=3)
        
        if self.c.hindamiskogum_id:
            q = q.filter(model.Hindamisolek.hindamiskogum_id==int(self.c.hindamiskogum_id))
        
        q = q.join((Hindamine1, sa.and_(Hindamine1.hindamisolek_id==model.Hindamisolek.id,
                                        Hindamine1.liik==const.HINDAJA1,
                                        Hindamine1.sisestus==1,
                                        Hindamine1.tyhistatud==False))).\
            join((Kasutaja1, Hindamine1.hindaja_kasutaja_id==Kasutaja1.id))

        q = q.join((Hindamine2, sa.and_(Hindamine2.hindamisolek_id==model.Hindamisolek.id,
                                        Hindamine2.liik==const.HINDAJA2,
                                        Hindamine2.sisestus==1,
                                        Hindamine2.tyhistatud==False))).\
            join((Kasutaja2, Hindamine2.hindaja_kasutaja_id==Kasutaja2.id))

        q = q.outerjoin((Hindamine3, sa.and_(Hindamine3.hindamisolek_id==model.Hindamisolek.id,
                                             Hindamine3.liik==const.HINDAJA3,
                                             Hindamine3.sisestus==1,
                                             Hindamine3.tyhistatud==False)))
        #q = q.outerjoin((Kasutaja3, Hindamine3.hindaja_kasutaja_id==Kasutaja3.id))

        if self.c.csv:
            return self._index_csv(q)
        self.c.header = self._prepare_header()
        self.c.prepare_item = self._prepare_item
        return q

    def _prepare_header(self):
        c = self.c
        header = [('sooritus.tahised', _("Eksamitöö kood")),
                  ('sooritaja.perenimi sooritaja.eesnimi', _("Sooritaja")),
                  ('hindamiskogum.tahis', _("Hindamiskogum")),
                  ('kasutaja_1.perenimi kasutaja_1.eesnimi', _("Esimene hindaja")),
                  c.punktides and (None, _("Toorpunktid")) or ('hindamine_1.pallid', 'Pallid'),
                  ('kasutaja_2.perenimi kasutaja_2.eesnimi', _("Teine hindaja")),
                  c.punktides and (None, _("Toorpunktid")) or ('hindamine_2.pallid', 'Pallid'),
                  (None, _("Vahe")),
                  ('hindamine_3.staatus', _("Kolmas hindamine")),
                  c.punktides and (None, _("Toorpunktid")) or ('hindamine_3.pallid', 'Pallid'),
                  ]
        return header

    def _prepare_items(self, q):
        "Loetelu ridade andmete väljastamine (CSV jaoks)"
        c = self.c
        h = self.h
        header = self._prepare_header()
        items = []
        for n, rcd in enumerate(q.all()):
            item, url_edit = self._prepare_item(rcd, n)
            items.append(item)
        return header, items

    def _prepare_item(self, rcd, n=0):
        c = self.c
        h = self.h
        sooritus_id, eesnimi, perenimi, tahised, hk_id, hk_tahis, \
                     h1_nimi, h1_id, h1_pallid, \
                     h2_nimi, h2_id, h2_pallid, \
                     h3_staatus, h3_id, h3_pallid = rcd 
        if c.punktides:
            tulemus1 = c.leia_punktid(h1_id)
            tulemus2 = c.leia_punktid(h2_id)
            tulemus3 = c.leia_punktid(h3_id)
        else:
            tulemus1 = h1_pallid
            tulemus2 = h2_pallid
            tulemus3 = h3_pallid
        if tulemus1 is not None and tulemus2 is not None:
            vahe = h.fstr(abs(tulemus1-tulemus2))
        else:
            vahe = ''
        url_edit = h.url('hindamine_ekspert_vaatamised', toimumisaeg_id=c.toimumisaeg.id, sooritus_id=sooritus_id, hindamiskogum_id=hk_id)
        item = [tahised,
                '%s %s' % (eesnimi, perenimi),
                hk_tahis or '-',
                h1_nimi,
                h.fstr(tulemus1),
                h2_nimi,
                h.fstr(tulemus2),
                vahe,
                c.opt.H_STAATUS.get(h3_staatus),
                h.fstr(tulemus3),
                ]
        return item, url_edit

    def __before__(self):
        toimumisaeg_id = self.request.matchdict.get('toimumisaeg_id')
        self.c.toimumisaeg = model.Toimumisaeg.get(toimumisaeg_id)
        self.c.test = self.c.toimumisaeg.testiosa.test
        
    def _perm_params(self):
        return {'obj': self.c.test}
