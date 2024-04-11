# -*- coding: utf-8 -*- 

from eis.lib.baseresource import *
_ = i18n._
log = logging.getLogger(__name__)

class HtunnusedController(BaseController):
    _permission = 'lahendamine'
    _authorize = False
    _INDEX_TEMPLATE = 'avalik/htunnused.mako'

    def show(self):
        c = self.c
        aine_kood = self.request.matchdict.get('aine')
        c.klass = self.request.matchdict.get('klass')
        c.aine = model.Klrida.get_by_kood('AINE', aine_kood)
        if c.aine:
            q = (model.SessionR.query(model.Klrida.kood,
                                     model.Klrida.kirjeldus,
                                     model.Klrida.kirjeldus_t)
                 .filter(model.Klrida.klassifikaator_kood==const.KL_HTUNNUS)
                 .filter(model.Klrida.ylem_id==c.aine.id)
                 .filter(model.Klrida.testiklass_kood==c.klass)
                 .order_by(model.Klrida.jrk, model.Klrida.kood)
                 )
            c.htunnused = [r for r in q.all()]

        return self.render_to_response(self._INDEX_TEMPLATE)
