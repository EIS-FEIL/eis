from eis.lib.base import *
_ = i18n._
log = logging.getLogger(__name__)

class IsikuandmedController(BaseController):
    _permission = 'regamine'
    _get_is_readonly = False
    
    def edit(self):
        sub = self.request.params.get('sub')
        if sub == 'rr':
            return self._show_rr(self.c.kasutaja.id)
        d = self._edit_d()
        return self.render_to_response('ekk/regamine/avaldus.isikuandmed.mako')

    def _edit_d(self):
        return self.response_dict

    def _error_update(self):
        html = self.form.render('/ekk/regamine/avaldus.isikuandmed.mako',
                                extra_info=self._edit_d())            
        return Response(html)
    
    def update(self):

        self.form = Form(self.request, schema=forms.ekk.regamine.IsikuandmedForm)
        if not self.form.validate():
            return self._error_update()

        kasutaja = self.c.kasutaja
        # isikuandmed
        kasutaja.from_form(self.form.data, 'k_')
        # õppimisandmed
        kasutaja.from_form(self.form.data, 'ko_')
        if not kasutaja.isikukood:
            kasutaja.kodakond_kood = self.form.data.get('kodakond_kood')
        model.Aadress.adr_from_form(kasutaja, self.form.data, 'a_')

        model.Session.commit()
        return HTTPFound(location=self.url('regamine_avaldus_testid', 
                                           id=kasutaja.id,
                                           korrad_id=self.c.korrad_id))

    def _show_rr(self, id):
        "Isiku päring Rahvastikuregistrist"
        res = xtee.rr_pohiandmed_js(self, self.c.kasutaja.isikukood)
        rc = False
        kodakond = res.get('kodakond_kood')
        if kodakond and kodakond != self.c.kasutaja.kodakond_kood:
            self.c.kasutaja.kodakond_kood = kodakond
            res['kodakond_nimi'] = model.Klrida.get_str('KODAKOND', kodakond) or kodakond
            rc = True
        if self.c.kasutaja.set_kehtiv_nimi(res.get('eesnimi'), res.get('perenimi')):
            rc = True
        if rc:
            model.Session.commit()

        return Response(json_body=res)

    def __before__(self):
        id = self.request.matchdict.get('id')
        self.c.kasutaja = model.Kasutaja.get(id)
        # korraldamisest tulles võib testimiskord olla kaasa antud, et ei peaks uuesti valima
        self.c.korrad_id = self.request.params.get('korrad_id')
