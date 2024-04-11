from eis.lib.baseresource import *
_ = i18n._
log = logging.getLogger(__name__)

class HelifailidController(BaseResourceController):
    """Protokolli helifailid
    """
    _permission = 'toimumisprotokoll'
    # TODO
    #_MODEL = model.Helivastusfail
    _INDEX_TEMPLATE = 'avalik/protokollid/helifailid.mako'
    _EDIT_TEMPLATE = 'avalik/protokollid/helifail.mako'
    _no_paginate = True
    
    def _query(self):
        testikohad_id = [r.id for r in self.c.testikohad]
        q = (model.Helivastusfail.query
             .filter(model.Helivastusfail.helivastused.any(
                 model.Helivastus.sooritus.has(
                     model.Sooritus.testikoht_id.in_(testikohad_id))))
             )
        return q

    def _update(self, item):
        if not self.c.is_edit:
            return

        f = self.request.params.get('filedata') # FieldStorage objekt
        if f != b'':
            item.file_from_form_value(f)
            item.valjast = True # EISi-väliselt salvestatud helifail
            item.kestus = item.audio_duration(item.filedata)
        elif not item.has_file:
            self.error(_('Fail puudub'))
            raise HTTPFound(location=self.url('protokoll_helifailid', toimumisprotokoll_id=self.c.toimumisprotokoll.id))

        sooritused_id = list(map(int, self.request.params.getall('sooritus_id')))
        if len(sooritused_id) == 0:
            self.error(_('Sooritused märkimata'))
            return HTTPFound(location=self.url('protokoll_helifailid', toimumisprotokoll_id=self.c.toimumisprotokoll.id))
        
        for rcd in item.helivastused:
            if rcd.id not in sooritused_id:
                rcd.delete()
        for sooritus_id in sooritused_id:
            rcd = model.Helivastus(sooritus_id=sooritus_id,
                                   helivastusfail=item)

    def _after_update(self, id):
        """Mida teha peale õnnestunud salvestamist
        """
        self.success()
        return self._redirect('index')

    def _after_delete(self, id=None):
        """Mida teha peale õnnestunud salvestamist
        """
        return self._redirect('index')
        
    def __before__(self):
        c = self.c
        mpr_id = self.request.matchdict.get('toimumisprotokoll_id')
        c.toimumisprotokoll = model.Toimumisprotokoll.get(mpr_id)

        c.testikohad = list(c.toimumisprotokoll.testikohad)
        for testikoht in c.testikohad:
            ta = testikoht.toimumisaeg
            if not c.toimumisaeg1:
                c.toimumisaeg1 = ta
            if not ta.on_hindamisprotokollid:
                c.is_edit = False

        if c.toimumisprotokoll.staatus in (const.B_STAATUS_KINNITATUD, const.B_STAATUS_EKK_KINNITATUD):
            c.is_edit = False
        elif not c.user.has_permission('toimumisprotokoll', const.BT_UPDATE, c.toimumisprotokoll):
            c.is_edit = False

    def _perm_params(self): 
        return {'obj': self.c.toimumisprotokoll}

    def _has_permission(self):
        for testikoht in self.c.testikohad:
            if not testikoht.toimumisaeg.on_hindamisprotokollid and self._is_modify():
                return False
        return BaseController._has_permission(self)
