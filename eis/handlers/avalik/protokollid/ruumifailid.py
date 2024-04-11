from eis.lib.baseresource import *
_ = i18n._
log = logging.getLogger(__name__)

class RuumifailidController(BaseResourceController):
    """Ruumide istumisplaanid jm failid
    """
    _permission = 'toimumisprotokoll,tprotsisestus'
    _MODEL = model.Ruumifail
    _INDEX_TEMPLATE = 'avalik/protokollid/ruumifailid.mako'
    _EDIT_TEMPLATE = 'avalik/protokollid/ruumifail.mako'
    _DEFAULT_SORT = 'ruumifail.id'
    _no_paginate = True
    
    def _query(self):
        testikohad_id = [r.id for r in self.c.testikohad]
        q = (model.Ruumifail.query
             .filter(model.Ruumifail.toimumisprotokoll_id==self.c.toimumisprotokoll.id)
             )
        return q

    def _edit(self, item):
        testikohad_id = [r.id for r in self.c.testikohad]
        q = (model.Session.query(model.Testiruum.id,
                                 model.Testiruum.tahis,
                                 model.Ruum.tahis)
             .filter(model.Testiruum.testikoht_id.in_(testikohad_id))
             .outerjoin(model.Testiruum.ruum)
             .order_by(model.Testiruum.tahis))
        self.c.opt_testiruumid = [(tr_id, '%s (%s)' % (tr_tahis, r_tahis or _("määramata"))) \
                                  for (tr_id, tr_tahis, r_tahis) in q.all()]
        
    def _update(self, item):
        if not self.c.is_edit:
            return

        f = self.request.params.get('filedata') # FieldStorage objekt
        if f != b'':
            item.file_from_form_value(f)
        elif item.filedata is None:
            self.error(_('Fail puudub'))
            raise HTTPFound(location=self.url('protokoll_ruumifailid', toimumisprotokoll_id=self.c.toimumisprotokoll.id))

        item.testiruum_id = self.request.params.get('testiruum_id')
        if not item.testiruum_id:
            self.error(_('Palun valida ruum'))
            return HTTPFound(location=self.url('protokoll_ruumifailid', toimumisprotokoll_id=self.c.toimumisprotokoll.id))

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

        if c.toimumisprotokoll.staatus in (const.B_STAATUS_KINNITATUD, const.B_STAATUS_EKK_KINNITATUD):
            c.is_edit = False

        c.testikohad = list(c.toimumisprotokoll.testikohad)
        for testikoht in c.testikohad:
            ta = testikoht.toimumisaeg
            if not c.toimumisaeg1:
                c.toimumisaeg1 = ta
            if not ta.on_hindamisprotokollid:
                c.is_edit = False
            
    def _perm_params(self): 
        return {'obj': self.c.toimumisprotokoll}

