from eis.lib.baseresource import *
_ = i18n._
log = logging.getLogger(__name__)

class IsikuandmedController(BaseResourceController):
    _permission = 'nimekirjad'
    _get_is_readonly = False
    _MODEL = model.Kasutaja
    _EDIT_TEMPLATE = 'avalik/nimekirjad/avaldus.isikuandmed.mako'
    
    def edit(self):
        self.c.testiliik = self.request.params.get('testiliik')
        sub = self.request.params.get('sub')
        if sub == 'rr':
            return self._show_rr(self.c.kasutaja.id)
        d = self._show_d()
        return self.render_to_response(self._EDIT_TEMPLATE)

    def _show_d(self):
        self.c.opilane = self.c.kasutaja.any_opilane
        return self.response_dict

    def _show_rr(self, id):
        "Isiku päring Rahvastikuregistrist"
        res = xtee.rr_pohiandmed_js(self, self.c.kasutaja.isikukood)

        if self.c.kasutaja.set_kehtiv_nimi(res.get('eesnimi'), res.get('perenimi')):
            model.Session.commit()

        return Response(json_body=res)

    def _update(self, item):
        # siia ei tulda
        errors = {}
        
    def _after_update(self, id):
        params = self.request.params
        testiliik = params.get('testiliik')
        if params.get('jatka'):
            url = self.url('nimekirjad_avaldus_testid', id=id, testiliik=testiliik)
        else:
            url = self.url('nimekirjad_edit_avaldus', id=id, testiliik=testiliik)
        return HTTPFound(location=url)
    
    def __before__(self):
        id = self.request.matchdict.get('id')
        self.c.kasutaja = model.Kasutaja.get(id)
