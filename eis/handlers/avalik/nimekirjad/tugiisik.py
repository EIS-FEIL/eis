from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class TugiisikController(BaseResourceController):
    """Tugiisiku määramine
    """
    _permission = 'nimekirjad'
    _INDEX_TEMPLATE = 'avalik/nimekirjad/tugiisik.mako'
    _get_is_readonly = False
    _actions = 'index,create'
    
    def _index_d(self):
        return self.render_to_response(self._INDEX_TEMPLATE)

    def _index_tik(self):
        isikukood = self.request.params.get('isikukood')
        res = {}
        kasutaja = None
        if not isikukood:
            res['error'] = _("Palun sisestada isikukood")
        else:
            kasutaja = model.Kasutaja.get_by_ik(isikukood)
            if not kasutaja:
                # teeme päringu RRist
                kasutaja = xtee.set_rr_pohiandmed(self, kasutaja, isikukood=isikukood)
                if kasutaja:
                    model.Session.commit()
                
        if kasutaja:
            res['nimi'] = kasutaja.nimi
            res['tkid'] = kasutaja.id
        return Response(json_body=res)

    def _create(self):            
        """Tugiisiku määramine
        """
        self._set_tugik(self.c.sooritus)
        model.Session.commit()

    def _set_tugik(self, sooritus):
        """Tugiisiku määramine testiosas"""
        c = self.c
        params = self.request.params
        key = 'tkid_%s' % sooritus.testiosa_id
        tkid = params.get(key) or None
        if tkid:
            tkid = int(tkid)
            if tkid == c.sooritaja.kasutaja_id:
                self.error(_("Sooritaja ei saa ise enda tugiisik olla"))
                model.Session.rollback()
                return
        sooritus.tugiisik_kasutaja_id = tkid
        sooritus.set_erivajadused(tkid and True or None)
        
    def _after_create(self, none_id):
        if self.has_errors():
            return self._index_d()
        else:
            self.success()
            return HTTPFound(location=self.url('nimekiri_erivajadus', id=self.c.sooritus.id))
    
    def __before__(self):
        c = self.c
        sooritus_id = self.request.matchdict.get('sooritus_id')
        c.sooritus = model.Sooritus.get(sooritus_id)
        c.sooritaja = c.sooritus.sooritaja
        c.test = c.sooritaja.test
        c.testimiskord = c.sooritaja.testimiskord
        assert c.sooritaja.kool_koht_id == c.user.koht_id, 'vale sooritaja'
                
    def _perm_params(self):
        return {'obj':self.c.testimiskord}

