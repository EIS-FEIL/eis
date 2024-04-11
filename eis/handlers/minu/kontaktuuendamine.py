from eis.lib.baseresource import *
log = logging.getLogger(__name__)
_ = i18n._

class KontaktuuendamineController(BaseResourceController):
    _permission = 'minu'
    _get_is_readonly = False
    _actions = 'create,index'
    _EDIT_TEMPLATE = 'minu/kontaktuuendamine.mako'
    _ITEM_FORM = forms.minu.KontaktuuendamineForm
    
    def index(self):
        return self.render_to_response(self._EDIT_TEMPLATE)

    def create(self):
        item = self.c.user.get_kasutaja(write=True)
        if self.request.params.get('op') != 'cancel':
            self.form = Form(self.request, schema=self._ITEM_FORM)
            if not self.form.validate():
                return self._error_create()
            item.epost = self.form.data.get('chk_epost')
            item.epost_seisuga = datetime.now()
            model.Session.commit()

        if 'chk.email' in self.request.session:
            del self.request.session['chk.email']
            self.request.session.changed()
        self.c.do_close = True
        return self.index()

    def _error_create(self):
        html = self.form.render(self._EDIT_TEMPLATE,
                                extra_info=self.response_dict)
        return Response(html)
