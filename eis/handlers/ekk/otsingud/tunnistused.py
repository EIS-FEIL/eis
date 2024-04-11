# -*- coding: utf-8 -*- 
# $Id: tunnistused.py 544 2016-04-01 09:07:15Z ahti $

from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class TunnistusedController(BaseResourceController):
    """Tunnistuste otsimine
    """
    _permission = 'aruanded-tunnistused'
    _MODEL = model.Tunnistus
    _INDEX_TEMPLATE = 'ekk/otsingud/tunnistused.otsing.mako'
    _LIST_TEMPLATE = 'ekk/otsingud/tunnistused.otsing_list.mako'
    _DEFAULT_SORT = 'tunnistus.id'

    def _query(self):
        q = (model.Session.query(model.Tunnistus,
                                 model.Kasutaja,
                                 model.Rveksam.nimi,
                                 model.Tunnistusekontroll)
             .join(model.Tunnistus.kasutaja)
             .outerjoin(model.Tunnistus.rvsooritaja)
             .outerjoin(model.Rvsooritaja.rveksam)
             .outerjoin(model.Tunnistus.tunnistusekontroll)
             )
        return q

    def _search_default(self, q):
        return None

    def _search(self, q):
        if not self.c.isikukood and not self.c.tunnistusenr:
            self.error(_("Palun esita otsinguparameetrid"))
            return
        
        if self.c.isikukood:
            usp = validators.IsikukoodP(self.c.isikukood)
            q = q.filter(usp.filter(model.Kasutaja))
        if self.c.tunnistusenr:
            q = q.filter(model.Tunnistus.tunnistusenr==self.c.tunnistusenr)
            
        return q

    def _download(self, id, format):
        """Näita faili"""
        item = self._MODEL.get(id)
        
        if not item:
            raise NotFound('Ei leitud')
        filename = item.filename
        filedata = item.filedata
        mimetype = item.mimetype
        if not filedata:
            raise NotFound('Dokumenti ei leitud')

        return utils.download(filedata, filename, mimetype)
