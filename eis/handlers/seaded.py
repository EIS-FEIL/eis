from eis.lib.base import *
_ = i18n._

log = logging.getLogger(__name__)

class SeadedController(BaseController):
    """Kasutajaliidese seadistamine,
    et test- ja live-keskkonnas oleks erinevad värvid,
    aga vajadusel oleks võimalik juhendite koostamiseks sama värv panna
    """
    _INDEX_TEMPLATE = '/seaded.mako'
    _actions = 'index,create'
    _authorize = False
    
    def index(self):
        c = self.c
        return self.render_to_response(self._INDEX_TEMPLATE)

    def create(self):
        sub = self.request.params.get('sub')
        if sub == 'forget':
            self._create_forget()
        elif sub == 'rmc':
            return self._create_rmc()
        else:
            self._create_inst()
        return self._redirect('index')

    def _create_inst(self):
        c = self.c
        params = self.request.params
        c.my_inst_name = params['inst']
        app_name = self.c.app_name
        inst_name = self.c.inst_name

        session = self.request.session
        if inst_name == c.my_inst_name or \
           c.my_inst_name not in ('test','prelive','live','clone'):
            if not (c.is_test and c.my_inst_name == 'test'):
                c.my_inst_name = None
        session['my_inst_name'] = c.my_inst_name
        session.changed()

    def _create_forget(self):
        "Unustada otsinguparameetrid"
        self.request.session['default_params'] = {}
        self.request.session.changed()
        self.success(_("Otsinguparameetrid unustatud!"))

    def _has_permission(self):
        #return self.is_test
        return True
