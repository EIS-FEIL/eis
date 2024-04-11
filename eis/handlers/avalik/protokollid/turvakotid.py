from eis.lib.baseresource import *

log = logging.getLogger(__name__)

class TurvakotidController(BaseResourceController):
    """Protokolli turvakotid
    """
    _permission = 'toimumisprotokoll'
    _INDEX_TEMPLATE = 'avalik/protokollid/turvakotid.mako'
    _ITEM_FORM = forms.avalik.admin.ProtokollTurvakotidForm

    _index_after_create = True

    def index(self):
        return self.render_to_response(self._INDEX_TEMPLATE)

    def _create(self):
        """Märgitakse turvakotid tagastamiseks.
        """
        testipaketid_id = [r.id for r in self.c.toimumisprotokoll.testipaketid]
        for rcd in self.form.data.get('tk'):
            turvakott_id = rcd.get('turvakott_id')
            turvakott = model.Turvakott.get(turvakott_id)
            assert turvakott.testipakett_id in testipaketid_id, 'Vale pakett'
            if turvakott.staatus != const.M_STAATUS_TAGASTATUD:
                turvakott.staatus = const.M_STAATUS_TAGASTAMISEL

    def __before__(self):
        c = self.c
        mpr_id = self.request.matchdict.get('toimumisprotokoll_id')
        c.toimumisprotokoll = model.Toimumisprotokoll.get(mpr_id)
        c.testikohad = list(c.toimumisprotokoll.testikohad)
        c.toimumisaeg1 = c.toimumisprotokoll.testikoht.toimumisaeg
        if not c.user.has_permission('toimumisprotokoll', const.BT_UPDATE, c.toimumisprotokoll):
            c.is_edit = False
             
    def _perm_params(self):
        return {'obj': self.c.toimumisprotokoll}

    def _has_permission(self):
        for testikoht in self.c.toimumisprotokoll.testikohad:
            if not testikoht.toimumisaeg.on_hindamisprotokollid and self._is_modify():
                return False
        return BaseController._has_permission(self)
