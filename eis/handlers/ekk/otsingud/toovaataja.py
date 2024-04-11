from eis.lib.baseresource import *
_ = i18n._

import logging
log = logging.getLogger(__name__)

class ToovaatajaController(BaseResourceController):
    """Testitöö vaataja roll
    """
    _permission = 'korraldamine'
    _MODEL = model.Toovaataja
    _EDIT_TEMPLATE = 'ekk/otsingud/toovaataja.mako'
    _actions = 'index,edit,create,update,delete'
    _INDEX_TEMPLATE = 'ekk/otsingud/toovaataja.otsing.mako'
    _EDIT_TEMPLATE = 'ekk/otsingud/toovaataja.mako'
    _SEARCH_FORM = forms.ekk.hindamine.ToovaatajaOtsiForm
    _ITEM_FORM = forms.ekk.hindamine.ToovaatajaForm
    
    def _query(self):
        return model.Session.query(model.Kasutaja)

    def _search_default(self, q):
        return self._search(q)
    
    def _search(self, q):
        c = self.c
        if not c.isikukood and not c.eesnimi and not c.perenimi:
            return
        if c.isikukood:
            usp = validators.IsikukoodP(self.c.isikukood)
            q = q.filter(usp.filter(model.Kasutaja))
        if c.eesnimi:
            q = q.filter(model.Kasutaja.eesnimi.ilike(c.eesnimi))
        if c.perenimi:
            q = q.filter(model.Kasutaja.perenimi.ilike(c.perenimi))
        return q

    def _show(self, item):
        c = self.c
        c.kasutaja = model.Kasutaja.get(item.kasutaja_id)
        
    def _new(self, item):
        self._show(item)

    def _edit(self, item):
        self._show(item)

    def _create(self):
        sooritaja_id = self.c.sooritaja_id
        kasutaja_id = self.form.data.get('kasutaja_id')
        kehtib_kuni = self.form.data['kehtib_kuni']
        q = (model.Session.query(model.Toovaataja)
             .filter_by(sooritaja_id=sooritaja_id)
             .filter_by(kasutaja_id=kasutaja_id)
             )
        item = q.first()
        if not item:
            item = model.Toovaataja(sooritaja_id=sooritaja_id,
                                    kasutaja_id=kasutaja_id,
                                    kehtib_kuni=kehtib_kuni)
        self._update(item)
        return item

    def _update(self, item):
        kehtib_kuni = self.form.data['kehtib_kuni']
        item.kehtib_kuni = kehtib_kuni

        # uuendame kasutajarolli (vajalik menyy õiguse kontrollimiseks)
        kasutaja_id = item.kasutaja_id
        kr = self._get_kasutajaroll(kasutaja_id)
        if not kr:
            kr = model.Kasutajaroll(kasutaja_id=kasutaja_id,
                                    kasutajagrupp_id=const.GRUPP_TOOVAATAJA,
                                    kehtib_kuni=kehtib_kuni)
        else:
            if kr.kehtib_kuni < kehtib_kuni:
                kr.kehtib_kuni = kehtib_kuni

    def _after_update(self, id):
        c = self.c
        url = self.url('otsing_testisooritus', id=c.sooritaja_id)
        return HTTPFound(location=url)

    def _after_delete(self, parent_id=None):
        return self._after_update(None)
                
    def _get_kasutajaroll(self, kasutaja_id):
        q = (model.Session.query(model.Kasutajaroll)
             .filter_by(kasutaja_id=kasutaja_id)
             .filter_by(kasutajagrupp_id=const.GRUPP_TOOVAATAJA)
             .order_by(model.Kasutajaroll.kehtib_kuni.desc())
             )
        return q.first()

    def __before__(self):
        c = self.c
        c.sooritaja_id = self.request.matchdict.get('sooritaja_id')
        c.sooritaja = model.Sooritaja.get(c.sooritaja_id)
        c.test = c.sooritaja.test

        tkoht1_id = None
        for tos in c.sooritaja.sooritused:
            if tos.testikoht_id:
                tkoht1_id = tos.testikoht_id
                break
        c.testikoht1_id = tkoht1_id
        
    def _perm_params(self):
        c = self.c
        return {'testikoht_id': c.testikoht1_id}

