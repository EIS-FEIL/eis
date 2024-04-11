from eis.lib.baseresource import *
_ = i18n._
log = logging.getLogger(__name__)

class HelifailidController(BaseResourceController):
    """Protokolli helifailid
    """
    _permission = 'sisestamine'
    _MODEL = model.Helivastusfail
    _INDEX_TEMPLATE = 'ekk/sisestamine/protokoll.helifailid.mako'
    _EDIT_TEMPLATE = 'avalik/protokollid/helifail.mako'

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
            item.kestus = item.audio_duration(item.filedata)
            item.valjast = True
        elif not item.has_file:
            self.error('Fail puudub')
            raise HTTPFound(location=self.url('sisestamine_protokoll_helifailid', toimumisprotokoll_id=self.c.toimumisprotokoll.id))

        sooritused_id = list(map(int, self.request.params.getall('sooritus_id')))
        if len(sooritused_id) == 0:
            self.error(_('Sooritused märkimata'))
            return HTTPFound(location=self.url('sisestamine_protokoll_helifailid', toimumisprotokoll_id=self.c.toimumisprotokoll.id))
        
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
        self.c.toimumisprotokoll = model.Toimumisprotokoll.get(self.request.matchdict.get('toimumisprotokoll_id'))
        self.c.testikohad = list(self.c.toimumisprotokoll.testikohad)
        self.c.testikoht = self.c.toimumisprotokoll.testikoht
        self.c.toimumisaeg = self.c.testikoht.toimumisaeg

    def _has_permission(self):
        if not self.c.toimumisaeg.on_hindamisprotokollid and self._is_modify():
            return False
        return BaseController._has_permission(self)
