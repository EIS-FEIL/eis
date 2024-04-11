from eis.lib.base import *
_ = i18n._
from eis.lib.xtee import ehis
log = logging.getLogger(__name__)

class IsikuvalikController(BaseController):
    _permission = 'regamine'
    def new(self):
        return self.render_to_response('ekk/regamine/avaldus.isikuvalik.mako', self._new_d())

    def _new_d(self):
        return self.response_dict

    def edit(self):
        d = self._edit_d()
        return self.render_to_response('ekk/regamine/avaldus.isikuvalik.mako')
    
    def _edit_d(self):
        c = self.c
        id = self.request.matchdict.get('id')
        c.kasutaja = model.Kasutaja.get(id)
        c.kontroll = self.request.params.get('kontroll')
        if c.kontroll:
            c.sooritajad = list(c.kasutaja.get_reg_sooritajad())            
        return self.response_dict

    def create(self):
        c = self.c
        self.form = Form(self.request, schema=forms.ekk.regamine.IsikuvalikForm)
        if not self.form.validate():
            return Response(self.form.render('ekk/regamine/avaldus.isikuvalik.mako',
                                             extra_info=self._new_d()))
        c.isikukood = self.form.data.get('isikukood')
        c.synnikpv = synnikpv = self.form.data.get('synnikpv')
        c.eesnimi = eesnimi = self.form.data.get('eesnimi')
        c.perenimi = perenimi = self.form.data.get('perenimi')
        kasutaja = None
        # peab sisestama kas isikukoodi või kasutajatunnuse või
        # kui need pole teada, siis synniaja ja nime
        if c.isikukood:
            kasutaja = self._give_kasutaja(c.isikukood)
        else:
            # isikukoodi ei ole
            if not synnikpv or not eesnimi or not perenimi:
                self.error(_("Palun sisestada kas isikukood või sünniaeg ja nimi"))
                return self.new()

            if not self.request.params.get('uus'):
                # kasutajale pole veel samanimeliste seast valida antud
                # kas sama synniaja ja nimega isikuid on juba andmebaasis?
                q = (model.Kasutaja.query
                     .filter_by(synnikpv=synnikpv)
                     .filter(model.Kasutaja.eesnimi.ilike(eesnimi))
                     .filter(model.Kasutaja.perenimi.ilike(perenimi)))
                if q.count():
                    # kuvame samanimelised isikud ja kui kasutaja sealt kellegi ära tunneb,
                    # siis suunatakse edit() lehele
                    c.items = q.all()
                    return self.new()
                
            # loome uue kasutaja kirje
            kasutaja = model.Kasutaja.add_kasutaja(None, eesnimi, perenimi, synnikpv)

        if not kasutaja:
            return self.new()
        else:
            model.Session.commit()
            if self.request.params.get('kontroll'):
                # vajutati nupule "Kontrolli registreeringuid"
                return self._redirect('edit', id=kasutaja.id, kontroll=1)
            return HTTPFound(location=self.url('regamine_avaldus_edit_isikuandmed', id=kasutaja.id, korrad_id=c.korrad_id))

    def update(self):
        id = self.request.matchdict.get('id')
        self.form = Form(self.request, schema=forms.ekk.regamine.IsikuvalikForm)
        if not self.form.validate():
            return Response(self.form.render('ekk/regamine/avaldus.isikuvalik.mako',
                                             extra_info=self._edit_d()))
        userid = self.request.params.get('isikukood')
        if userid:
            kasutaja = self._give_kasutaja(userid)
        else:
            kasutaja = model.Kasutaja.get(id)

        if not kasutaja:
            return Response(self.form.render('ekk/regamine/avaldus.isikuvalik.mako',
                                             extra_info=self._edit_d()))            
        if self.request.params.get('kontroll'):
            # vajutati nupule "Kontrolli registreeringuid"
            return self._redirect('edit', id=kasutaja.id, kontroll=1)
        return HTTPFound(location=self.url('regamine_avaldus_edit_isikuandmed', id=kasutaja.id, korrad_id=self.c.korrad_id))

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
            else:
                model.Session.commit()
                opilane = model.Opilane.get_by_ik(usp.isikukood_ee)
                if not opilane:
                    self.error(_("EHISest ei leitud isikukoodiga {s} õpilast!").format(s=usp.isikukood_ee))
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

    def __before__(self):
        # korraldamisest tulles võib testimiskord olla kaasa antud, et ei peaks uuesti valima
        self.c.korrad_id = self.request.params.get('korrad_id')
