"Kasutaja saab vaadata ja muuta oma isikuandmeid"
from eis.lib.base import *
from eis.lib.xtee import rahvastikuregister
log = logging.getLogger(__name__)
_ = i18n._
class MinuandmedController(BaseController):
    _permission = 'minu'
    _get_is_readonly = False
    _actions = 'index,edit,create'
    
    @action(renderer='minu/minuandmed.mako')
    def index(self):
        c = self.c
        c.item = c.kasutaja = model.Kasutaja.get(c.user.id)
        return self.response_dict

    @action(renderer='minu/minuandmed.mako')
    def edit(self):
        """Rahvastikuregistrist andmete pärimine, id="rr"
        """
        id = self.request.matchdict.get('id')
        c = self.c
        c.item = c.kasutaja = model.Kasutaja.get(c.user.id)        
        xtee.set_rr_pohiandmed(self, c.kasutaja, muuda=True)
        if not self.has_errors():
            self.success(_("Andmed uuendati!"))
        return self.response_dict

    def create(self):
        self.form = Form(self.request, schema=forms.minu.IsikuandmedForm)
        if not self.form.validate():
            return self._error_create()

        item = model.Kasutaja.get(self.c.user.id)
        item.from_form(self.form.data, 'k_')
        model.Aadress.adr_from_form(item, self.form.data, 'a_')

        model.Session.commit()
        self.success()
        if not item.epost:
            self.warning(_("Soovitame lisada e-posti aadressi, et saaksime vajadusel saata eksamiteavitusi"))
        return self._redirect('index')

    def _error_create(self):
        html = self.form.render('minu/minuandmed.mako',
                                extra_info=self.index())
        return Response(html)
