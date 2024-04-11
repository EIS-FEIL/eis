from eis.lib.baseresource import *
from . import suulised

log = logging.getLogger(__name__)

class KirjalikudController(suulised.SuulisedController):
    """Kirjaliku testi hindamisprotokollide otsimine sisestamiseks
    """
    _INDEX_TEMPLATE = 'ekk/sisestamine/kirjalikud.otsing.mako'
    _LIST_TEMPLATE = 'ekk/sisestamine/kirjalikud.otsing_list.mako'
    _vastvorm_kood = const.VASTVORM_KP

    def _query(self):
        # kirjaliku testi puhul sisestatakse protokoll ainult neile hindamiskogumitele,
        # mida ei sisestata vastuste sisestamise teel
        return suulised.SuulisedController._query(self).\
            filter(model.Sisestuskogum.on_hindamisprotokoll==True)

    def _url_sisestama(self, hpr, sisestus):
        return HTTPFound(location=self.h.url('sisestamine_kirjalikud_hindamised',
                                             hindamisprotokoll_id=hpr.id, 
                                             sisestus=sisestus))
