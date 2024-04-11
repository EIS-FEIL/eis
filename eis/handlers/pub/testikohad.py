# -*- coding: utf-8 -*- 

"Toimumisaja testikohtade valiku uuendamine piirkonna järgi"

from eis.lib.base import *
_ = i18n._

log = logging.getLogger(__name__)

class TestikohadController(BaseController):
    _authorize = False

    @action(renderer='json')
    def index(self):
        toimumisaeg_id = self.request.matchdict.get('toimumisaeg_id')
        toimumisaeg = model.Toimumisaeg.get(toimumisaeg_id)
        piirkond_id = self.request.params.get('piirkond_id')
        if piirkond_id:
            piirkond_id = int(piirkond_id)

        li = [('', _("-- Vali --"))] + toimumisaeg.get_testikohad_opt(piirkond_id)
        data = [{'id':a[0],'value':a[1]} for a in li]
        return data
