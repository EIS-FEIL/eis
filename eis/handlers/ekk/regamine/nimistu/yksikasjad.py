# -*- coding: utf-8 -*- 
# $Id: yksikasjad.py 406 2016-03-07 19:18:48Z ahti $

from eis.lib.base import *
_ = i18n._
log = logging.getLogger(__name__)

class YksikasjadController(BaseController):
    """Valitud testide üksikasjade kuvamine
    """
    _permission = 'regamine'
    def edit(self):
        self.c.testiliik = self.request.params.get('testiliik')
        self.c.sessioon = self.request.params.get('sessioon')
        self.c.korrad_id = self.request.matchdict.get('korrad_id')
        korrad_id = self.c.korrad_id.split('-')
        self.c.korrad = [model.Testimiskord.get(kord_id) for kord_id in korrad_id]
        return self.render_to_response('ekk/regamine/nimistu.yksikasjad.mako')

