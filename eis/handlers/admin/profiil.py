from eis.lib.baseresource import *
_ = i18n._
from eis.lib.basegrid import BaseGridController
from eis.lib.xtee import rahvastikuregister
log = logging.getLogger(__name__)

class ProfiilController(BaseController):
    _permission = 'profiil,profiil-vaatleja'
    _get_is_readonly = False
    
    def _show_d(self):
        self.c.profiil = self.c.kasutaja.give_profiil()
        return self.response_dict
    
    def show(self):
        self._show_d()
        return self.render_to_response('/admin/kasutaja.profiil.mako')

    def edit(self):
        return self.show()

    def update(self):
        self.form = Form(self.request, schema=forms.admin.ProfiilForm)
        if self.form.validate():
            try:
                profiil = self.c.kasutaja.give_profiil()      

                if not self.c.can_update_profiil and self.c.can_update_vaatleja:
                    # piirkondlik korraldaja, kes saab muuta ainult vaatlemise profiili
                    profiil.on_vaatleja = self.form.data.get('f_on_vaatleja')
                    profiil.v_skeeled = ' '.join(self.form.data.get('v_skeel'))
                    profiil.v_koolitusaeg = self.form.data.get('f_v_koolitusaeg')
                elif self.c.can_update_profiil:
                    profiil.from_form(self.form.data, 'f_')
                    profiil.v_skeeled = ' '.join(self.form.data.get('v_skeel'))
                    profiil.k_skeeled = ' '.join(self.form.data.get('k_skeel'))
                    profiil.s_skeeled = ' '.join(self.form.data.get('s_skeel'))                    
                    aineprofiilid = self.form.data['a']
                    aineprofiilid = self._check_unique(aineprofiilid)

                    for r in aineprofiilid:
                        r['kasutaja_id'] = self.c.kasutaja.id
                    # piirame read nendega, mille aine kirjeid kasutajal on õigus muuta
                    rows = [r for r in self.c.kasutaja.aineprofiilid \
                            if self.c.user.has_permission('profiil', const.BT_UPDATE, aine=r.aine_kood)]
                    
                    BaseGridController(rows, model.Aineprofiil).save(aineprofiilid)

            except ValidationError as e:
                self.form.errors = e.errors
        if self.form.errors:
            return Response(self.form.render('/admin/kasutaja.profiil.mako',
                                             extra_info=self._show_d()))
        model.Session.commit()
        self.success()
        return self._redirect('edit')

    def _minu_ained(self):
        "Milliseid aineid võib ainespetsialist muuta?"
        q = model.SessionR.query(model.Kasutajaroll.aine_kood,
                                model.Kasutajagrupp_oigus.bitimask)
        q = q.filter_by(kasutaja_id=self.c.user.id).\
            filter(model.Kasutajaroll.kehtib_alates<=datetime.now()).\
            filter(model.Kasutajaroll.kehtib_kuni>=datetime.now()).\
            join((model.Kasutajagrupp_oigus,
                  model.Kasutajagrupp_oigus.kasutajagrupp_id==model.Kasutajaroll.kasutajagrupp_id))
        q = q.filter(model.Kasutajagrupp_oigus.nimi=='profiil')
        return set([r[0] for r in q.all() if r[1] & const.BT_UPDATE == const.BT_UPDATE])

    def _check_unique(self, aineprofiilid):
        li = []
        aineprofiilid2 = []
        for n, a in enumerate(aineprofiilid):
            unique = (a['aine_kood'], a['kasutajagrupp_id'], a['keeletase_kood'])
            if unique in li:
                pass
            else:
                li.append(unique)
                aineprofiilid2.append(a)
        return aineprofiilid2

    def _perm_params(self):
        if not self.c.kasutaja:
            return False
        
    def __before__(self):
        self.c.kasutaja = model.Kasutaja.get(self.request.matchdict.get('id'))
        self.c.can_update_profiil = self.c.user.has_permission('profiil', const.BT_UPDATE)
        self.c.can_update_vaatleja = self.c.can_update_profiil or \
                                     self.c.user.has_permission('profiil-vaatleja', const.BT_UPDATE)        

