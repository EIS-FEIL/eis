from eis.lib.baseresource import *
from eis.lib.basegrid import BaseGridController
log = logging.getLogger(__name__)

class ProfiilController(BaseResourceController):
    _permission = 'nousolekud'
    _MODEL = model.Labiviija
    _INDEX_TEMPLATE = '/avalik/nousolekud/profiil.mako' 
    _get_is_readonly = False
    
    def index(self):
        self.c.profiil = self.c.kasutaja.give_profiil()
        return self.render_to_response('/avalik/nousolekud/profiil.mako')

    def create(self):
        self.form = Form(self.request, schema=forms.avalik.admin.ProfiilForm)
        if self.form.validate():
            try:
                profiil = self.c.kasutaja.give_profiil()      
                profiil.from_form(self.form.data, 'f_')
                aineprofiilid = self.form.data['a']
                BaseGridController(self.c.kasutaja.aineprofiilid, model.Aineprofiil).save(aineprofiilid)
            except ValidationError as e:
                self.form.errors = e.errors

        if self.form.errors:
            return Response(self.form.render(self._ITEM_TEMPLATE,
                                             extra_info=self.response_dict))
        model.Session.commit()
        self.success()
        return self._redirect('index')

    def _after_delete(self, parent_id=None):
        """Kuhu peale läbiviija kirje kustutamist minna
        """
        return self._redirect('index')

    def _after_update(self, id):
        """Mida teha peale õnnestunud salvestamist
        """
        self.success()
        return self._redirect('index')

    def __before__(self):
        self.c.kasutaja = self.c.user.get_kasutaja(write=True)
        self.c.is_edit = False
