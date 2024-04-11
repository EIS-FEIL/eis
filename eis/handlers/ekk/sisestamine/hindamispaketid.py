# -*- coding: utf-8 -*- 
# $Id: hindamispaketid.py 466 2016-03-14 13:55:14Z ahti $

from eis.lib.baseresource import *
from eis.lib.basegrid import *
from eis.lib.pdf.hindajakleeps import HindajakleepsDoc
_ = i18n._

log = logging.getLogger(__name__)

class HindamispaketidController(BaseResourceController):
    """Kirjaliku testi hindajatele testitöödega ümbrike hindamiseks väljastamine
    """
    _permission = 'sisestamine'
    _MODEL = model.Labiviija
    _INDEX_TEMPLATE = 'ekk/sisestamine/hindamispaketid.mako'
    _LIST_TEMPLATE = 'ekk/sisestamine/hindamispaketid_list.mako'    
    _DEFAULT_SORT = 'hindamiskogum.id' # vaikimisi sortimine
    _SEARCH_FORM = forms.ekk.sisestamine.HindamispaketidForm 
    _UNIQUE_SORT = 'labiviija_1.id'
    
    def _query(self):
        testiosa = self.c.toimumisaeg.testiosa
        self.c.hindamiskogumid_opt = [(r.id, r.tahis) \
                                          for r in testiosa.hindamiskogumid \
                                          if r.staatus]
        self.c.hindajad_opt = self._get_hindajad_opt()

        self.Labiviija1 = sa.orm.aliased(model.Labiviija, name='labiviija_1')
        # kui kasutada ..table.alias(), siis filtri sees hindaja1.c.id=...
        # ja tulemuses on üksikud väljad, mitte objekt
        #self.Labiviija1 = model.Labiviija.table.alias('hindaja1')
        #if self.c.kaks_hindajat:
        self.Labiviija2 = sa.orm.aliased(model.Labiviija, name='labiviija_2')
        q = model.SessionR.query(model.Hindamiskogum, self.Labiviija1, self.Labiviija2).\
            join((self.Labiviija1, model.Hindamiskogum.id==self.Labiviija1.hindamiskogum_id)).\
            filter(self.Labiviija1.liik==const.HINDAJA1).\
            filter(self.Labiviija1.toimumisaeg_id==self.c.toimumisaeg.id).\
            outerjoin((self.Labiviija2, 
                       sa.and_(self.Labiviija1.id==self.Labiviija2.hindaja1_id,
                               self.Labiviija2.liik==const.HINDAJA2,
                               self.Labiviija2.toimumisaeg_id==self.c.toimumisaeg.id)))
        self.Kasutaja1 = None
        self.Kasutaja2 = None
        return q

    def _search(self, q):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        if self.c.hindamiskogum_id:
            hindamiskogum_id = int(self.c.hindamiskogum_id)
            q = q.filter(model.Hindamiskogum.id==hindamiskogum_id)

        if self.c.hindaja_id:
            hindaja_id = int(self.c.hindaja_id)
            q = q.filter(sa.or_(self.Labiviija1.kasutaja_id==hindaja_id,
                                self.Labiviija2.kasutaja_id==hindaja_id))

        if self.request.params.get('kleeps'):
            return self._gen_kleeps(q, False)
        elif self.request.params.get('kleeps1'):
            return self._gen_kleeps(q, True)        
        return q

    def _gen_kleeps(self, q, yhekaupa):
        q = self._order(q)        
        doc = HindajakleepsDoc(q, self.c.toimumisaeg, yhekaupa)
        data = doc.generate()
        filename = 'kleebis.pdf'
        mimetype = const.CONTENT_TYPE_PDF
        return utils.download(data, filename, mimetype)

    def _order_join(self, q, tablename):
        """Otsingupäringu sortimisel lisatakse päringule join 
        tabeliga, mille välja järgi tuleb sortida
        """
        if tablename == 'kasutaja_1':
            if not self.Kasutaja1:
                self.Kasutaja1 = sa.orm.aliased(model.Kasutaja, name='kasutaja_1')
                q = q.join((self.Kasutaja1, self.Kasutaja1.id==self.Labiviija1.kasutaja_id))
        if tablename == 'kasutaja_2':
            if not self.Kasutaja2:
                self.Kasutaja2 = sa.orm.aliased(model.Kasutaja, name='kasutaja_2')
                q = q.outerjoin((self.Kasutaja2, self.Kasutaja2.id==self.Labiviija2.kasutaja_id))
        return q

    def _get_hindajad_opt(self):
        qh = model.SessionR.query(model.Kasutaja.id, model.Kasutaja.nimi).\
            join((model.Labiviija, model.Kasutaja.id==model.Labiviija.kasutaja_id)).\
            filter(model.Labiviija.toimumisaeg_id==self.c.toimumisaeg.id).\
            filter(model.Labiviija.liik.in_((const.HINDAJA1, const.HINDAJA2))).\
            order_by(model.Kasutaja.nimi)
        return [(k[0],k[1]) for k in qh.all()] 

    def _show_kleeps(self, id):
        "Kleebise trükkimine"

    def __before__(self):
        toimumisaeg_id = self.request.matchdict.get('toimumisaeg_id')
        self.c.toimumisaeg = model.Toimumisaeg.get(toimumisaeg_id)
        #self.c.kaks_hindajat = self.c.toimumisaeg.kahekordne_hindamine

