from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class AvaleheteatelogidController(BaseResourceController):

    _permission = 'olulineinfo'
    _INDEX_TEMPLATE = 'admin/avaleheteatelogid.mako'
    _LIST_TEMPLATE = 'admin/avaleheteated_list.mako'
    _MODEL = model.Avaleheinfologi
    _DEFAULT_SORT = '-avaleheinfologi.id'
    _actions = 'index'
