from eis.lib.baseresource import *
_ = i18n._
from eis.lib.pdf.testikohamarkused import TestikohamarkusedDoc
log = logging.getLogger(__name__)

class MarkusedController(BaseResourceController):
    _permission = 'korraldamine'
    _MODEL = model.Testikoht
    _INDEX_TEMPLATE = '/ekk/korraldamine/markused.mako' 
    _LIST_TEMPLATE = '/ekk/korraldamine/markused_list.mako'
    _DEFAULT_SORT = 'koht.nimi'
    _ignore_default_params = ['pdf']
    
    def _query(self):
        q = model.SessionR.query(model.Koht.nimi,
                                model.Testikoht.markus).\
            join(model.Koht.testikohad).\
            filter(model.Testikoht.toimumisaeg_id==self.c.toimumisaeg.id).\
            filter(model.Testikoht.markus!=None)
        return q

    def _search(self, q):
        if self.c.piirkond_id:
            f = []
            self.c.piirkond = prk = model.Piirkond.get(self.c.piirkond_id)
            for prk_id in prk.get_alamad_id():
                f.append(model.Koht.piirkond_id==prk_id)
            q = q.filter(sa.or_(*f))
        return q

    def _showlist(self):
        """Otsingu tulemuste kuvamine.
        """
        if self.request.params.get('pdf'):
            data, filename = self._render_pdf()
            mimetype = const.CONTENT_TYPE_PDF
            return utils.download(data, filename, mimetype)            

        if self.request.params.get('partial'):
            return self.render_to_response(self._LIST_TEMPLATE)
        else:
            return self.render_to_response(self._INDEX_TEMPLATE)

    def _render_pdf(self):
        doc = TestikohamarkusedDoc(self.c.toimumisaeg, self.c.items)
        data = doc.generate()
        filename = 'markused_%s.pdf' % self.c.toimumisaeg.tahised
        return data, filename
    
    def __before__(self):
        self.c.toimumisaeg = model.Toimumisaeg.get(self.request.matchdict.get('toimumisaeg_id'))
        self.c.testiosa = self.c.toimumisaeg.testiosa
        self.c.test = self.c.testiosa.test
        
