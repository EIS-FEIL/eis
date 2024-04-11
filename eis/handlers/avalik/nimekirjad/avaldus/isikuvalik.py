from eis.lib.base import *
_ = i18n._
from eis.lib.xtee import ehis
log = logging.getLogger(__name__)

class IsikuvalikController(BaseController):
    _permission = 'nimekirjad'
    def new(self):
        self._new_d()
        return self.render_to_response('avalik/nimekirjad/avaldus.isikuvalik.mako')

    def _new_d(self):
        return self.response_dict

    def edit(self):
        d = self._edit_d()
        return self.render_to_response('avalik/nimekirjad/avaldus.isikuvalik.mako')
    
    def _edit_d(self):
        id = self.request.matchdict.get('id')
        self.c.kasutaja = model.Kasutaja.get(id)
        self.c.testiliik = self.request.params.get('testiliik')
        return self.response_dict

    def create(self):
        c = self.c
        self.form = Form(self.request, schema=forms.ekk.regamine.IsikuvalikForm)
        if not self.form.validate():
            return Response(self.form.render('avalik/nimekirjad/avaldus.isikuvalik.mako',
                                             extra_info=self._new_d()))
        kasutaja = None
        userid = self.form.data.get('isikukood')
        if userid:
            kasutaja = self._give_kasutaja(userid)
        else:
            self.error(_("Palun sisestada isikukood"))

        if kasutaja:
            model.Session.commit()
            return HTTPFound(location=self.url('nimekirjad_avaldus_isikuandmed', id=kasutaja.id))
        else:
            return self.new()

    def update(self):
        id = self.request.matchdict.get('id')
        self.form = Form(self.request, schema=forms.ekk.regamine.IsikuvalikForm)
        if not self.form.validate():
            return Response(self.form.render('avalik/nimekirjad/avaldus.isikuvalik.mako',
                                             extra_info=self._edit_d()))
        userid = self.request.params.get('isikukood')
        if userid:
            kasutaja = self._give_kasutaja(userid)
        else:
            kasutaja = model.Kasutaja.get(id)
            
        if not kasutaja:
            return Response(self.form.render('avalik/nimekirjad/avaldus.isikuvalik.mako',
                                             extra_info=self._edit_d()))            
        model.Session.commit()
        return HTTPFound(location=self.url('nimekirjad_avaldus_isikuandmed', id=kasutaja.id))

    def _give_kasutaja(self, userid):
        """Otsitakse isikut isikukoodi järgi.
        Kui leitakse kuskilt, siis suunatakse isikuandmete lehele.
        """
        usp = eis.forms.validators.IsikukoodP(userid)
        kasutaja = usp.get(model.Kasutaja)
        if usp.isikukood_ee:
            err = ehis.uuenda_opilased(self, [usp.isikukood_ee])
            if err:
                self.error(err)
                return
            model.Session.commit()
            # get_by_ik leiab isiku kõrgeima prioriteediga õpilaskirje
            opilane = model.Opilane.get_by_ik(usp.isikukood_ee)
            if not opilane:
                self.error(_("EHISest ei leitud isikukoodiga {s} õpilast!").format(s=usp.isikukood))
            else:
                if not kasutaja:
                    kasutaja = opilane.give_kasutaja()
                else:
                    kasutaja.from_opilane(opilane)

            if self.request.is_ext():
                # teeme päringu RRist
                if not kasutaja:
                    kasutaja = xtee.set_rr_pohiandmed(self, kasutaja, usp.isikukood_ee)
                else:
                    xtee.uuenda_rr_pohiandmed(self, kasutaja)
        return kasutaja
