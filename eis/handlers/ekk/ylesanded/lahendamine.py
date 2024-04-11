from eis.lib.baseresource import *
_ = i18n._
from eis.lib.block import BlockController
from eis.handlers.avalik.lahendamine import lahendamine
log = logging.getLogger(__name__)

class LahendamineController(lahendamine.LahendamineController):

    _permission = 'ylesanded'
    _MODEL = model.Ylesanne
    _EDIT_TEMPLATE = 'ekk/ylesanded/lahendamine.mako' 
    _LIST_TEMPLATE = None
    _SEARCH_TEMPLATE = None
    _authorize = True
    _get_is_readonly = False
    
    def _search(self, q):
        pass

    def _check_status(self, item):
        if not item:
            self.error(_("Vale ülesande ID"))
            return False
        else:
            return True

    def edit(self):
        # esmalt kontrollime ylesande
        c = self.c
        ylesanne_id = c.ylesanne.id
        if self.request.method == 'GET':
            c.ylesanne.check(self)
            model.Session.commit()
            c.ylesanne = model.Ylesanne.get(ylesanne_id)
        return lahendamine.LahendamineController.edit(self)

    def _set_response(self, buf):
        "Antud vastus pannakse c sisse"
        self.c.vastus = buf.replace('\n','<br/>')

    def _set_calculation(self, buf):
        "Arvutuskäik pannakse c sisse"
        self.c.calculation = buf.replace('\n','<br/>\n')
        
    def __before__(self):
        c = self.c
        c.ylesanne = model.Ylesanne.get(self.request.matchdict.get('id'))
        c.lang = self.params_lang()
        
    def _perm_params(self):
        if not self.c.ylesanne:
            return False
        return {'obj':self.c.ylesanne}

    def _get_perm_bit(self):
        "Lahendamine on alati ülesande vaatamine"
        return const.BT_SHOW
