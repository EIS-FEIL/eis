from eis.lib.baseresource import *
from eis.lib.xtee import ehis
_ = i18n._
log = logging.getLogger(__name__)

class KlassiparoolidController(BaseResourceController):
    _permission = 'paroolid'
    _SEARCH_FORM = forms.admin.KlassiparoolidForm
    _INDEX_TEMPLATE = 'admin/klassiparoolid.mako'
    _LIST_TEMPLATE = 'admin/klassiparoolid_list.mako'
    _no_paginate = True
    _get_is_readonly = False
    
    def _query(self):
        return None

    def _search_default(self, q):
        return self._search(q)
    
    def _search(self, q):
        c = self.c
        koht = c.user.koht
        c.opt_klassid_ryhmad = c.opt.opt_klassid_ryhmad(koht)
        if c.klass:
            klass, ryhm_id = model.Klass.klass_ryhm(c.klass)
            koht_id = koht.id
            kool_id = koht.kool_id
            paralleel = c.paralleel
            c.user.uuenda_klass(kool_id, klass, paralleel)

            q = (model.Session.query(model.Opilane)
                 .filter_by(koht_id=koht_id))
            if klass:
                q = q.filter_by(klass=klass)
                if paralleel:
                    q = q.filter_by(paralleel=paralleel)
            elif ryhm_id:
                q = q.filter_by(ryhm_id=ryhm_id)
            return q
    
    def create(self):
        c = self.c
        c.items = []
        c.isikukoodid = self.request.params.getall('isikukood')
        c.klass = self.request.params.get('klass')
        c.paralleel = self.request.params.get('paralleel') or ''
        c.data = {}
        npwd = 0
        for ik in c.isikukoodid:
            r = self._create_pwd(ik)
            if r:
                opilane_id, pwd, err = r
                c.data[opilane_id] = (pwd, err)
                if pwd:
                    npwd += 1
        c.npwd = npwd
        model.Session.commit()

        q = self._search(None)
        q = self._order(q)
        c.items = self._paginate(q)
        
        return self.render_to_response('/admin/klassiparoolid_list.mako')
    
    def _create_pwd(self, ik):
        err = None
        opilane = model.Opilane.get_by_ik(ik)
        if opilane:
            kasutaja = opilane.kasutaja
            if kasutaja:
                # kontrollime, et pole kõva kasutaja
                if not self._can_set_pwd(kasutaja):
                    err = _("Selle kasutaja parooli muutmiseks on eriõiguseid vaja")
                    return opilane.id, None, err
            else:
                kasutaja = opilane.give_kasutaja()

            pwd = User.gen_pwd()
            kasutaja.set_password(pwd, True)
            return opilane.id, pwd, None

    def _can_set_pwd(self, kasutaja):
        "Parooli saab muuta tavalisel kasutajal, kellel pole õiguseid"
        if kasutaja:
            if kasutaja.on_labiviija:
                return False
            for r in kasutaja.kasutajarollid:
                # sh kontrollitakse, kas on ametnik
                if r.kehtiv:
                    return False

        return True

    def _perm_params(self):
        if not self.c.user.koht_id:
            return False
