from simplejson import dumps
from eis.lib.baseresource import *
_ = i18n._
from eis.handlers.avalik.khindamine.hkhindamine import HkhindamineController

log = logging.getLogger(__name__)

class HindajavaadeHkhindamineController(HkhindamineController):
    """Hindaja eelvaade
    """
    _permission = 'hindajamaaramine'    
    _INDEX_TEMPLATE = 'ekk/hindamine/hindajavaade_hkhindamine.mako'
    _get_is_readonly = True
    
    def _redirect_to_index(self, is_json):
        c = self.c
        if c.hindaja:
            # hindaja tööde loetellu
            url = self.url('hindamine_hindajavaade_vastajad',
                           toimumisaeg_id=c.toimumisaeg.id,
                           hindaja_id=c.hindaja_id)
        elif c.action == 'index':
            # EKK hindaja eelvaade ilma hindajata
            url = self.url('hindamine_hindajad', toimumisaeg_id=c.toimumisaeg.id)
        else:
            # eelvaade ilma hindajata
            url = self.url_current('index')
        if is_json:
            return Response(json_body={'redirect': url})
        else:
            return HTTPFound(location=url)

    def index(self):
        c = self.c
        if c.sooritus_id == '0':
            # leiame suvalise töö eelvaates kuvamiseks
            q = (model.Session.query(model.Sooritus)
                 .filter(model.Sooritus.toimumisaeg_id==c.toimumisaeg.id)
                 .filter(model.Sooritus.staatus==const.S_STAATUS_TEHTUD)
                 .join(model.Sooritus.hindamisolekud)
                 .filter(model.Hindamisolek.hindamiskogum_id==c.hindamiskogum.id)
                 .filter(model.Hindamisolek.puudus==False)
                 .filter(model.Hindamisolek.mittekasitsi==False)
                 )
            lang = self.params_lang()
            if lang:
                q = q.join(model.Sooritus.sooritaja).filter_by(lang=lang)
            c.sooritus = q.first()
            if c.sooritus:
                c.sooritus_id = c.sooritus.id
            else:
                self.error(_("Hinnatavaid töid ei leitud"))
                return self._redirect_to_index(True)

        # algupärane osa
        op = self.request.params.get('op')
        ty_id = self._get_next_id(op) or None
        res = self._ty_edit(ty_id)
        if res:
            return res
        if not self.request.params.get('partial'):
            template = self._INDEX_TEMPLATE
        else:
            if ty_id:
                # ylesande vahetamisel: ylesande osa 
                self.c.ainult_yl_vahetub = True
                # muul juhul ylesande osa + kriteeritumite osa
            template = self._EDIT_TEMPLATE
        # hindaja eelvaates muudatusi ei tee!
        model.Session.rollback()
        return self.render_to_response(template)
        
    def _is_next(self, sooritus):
        # kas on veel töid saadaval ja on vaja järgmise töö nuppu
        c = self.c
        if not c.hindaja:
            return False
        return super()._is_next(sooritus)

    def _get_tab_urls(self):
        # vasakul poolel ylesande avamise (GET) või hindamise salvestamise (POST) URL
        c = self.c
        h = self.h
        def f_submit_url(ty_id):
            if ty_id:
                # ylesande hindamine
                return h.url('hindamine_hindajavaade_hkhindamine', sooritus_id=c.sooritus.id, 
                             toimumisaeg_id=c.toimumisaeg.id, hindaja_id=c.hindaja_id, id=ty_id)
            else:
                # hindamiskogumi hindamiskriteeriumite hindamine
                return h.url('hindamine_hindajavaade_hkhindamised', sooritus_id=c.sooritus.id, 
                             toimumisaeg_id=c.toimumisaeg.id, hindaja_id=c.hindaja_id)

        c.f_submit_url = f_submit_url

        get_tab_urls(self, self.c)

    def _update(self, item):
        # ylesande hindamise salvestamine
        c = self.c
        params = self.request.params
        op = params.get('op')
        self.warning(_("Hindaja eelvaates muudatusi ei salvestata"))
        if op == 'lykka':
            #self.success(_("Testitöö hindamine on tagasi lükatud"))
            return self._redirect_to_index(True)

        return self._after_update(op)

    def _update_mcomments(self, id):
        "Tekstis märgitud vigade ja kommentaaride automaatne salvestamine"
        res = {'result':'OK'}
        return Response(json_body=res)

    def _get_hindamiste_arvud(self):
        if not self.c.hindaja:
            return
        super()._get_hindamiste_arvud()
            
    def __before__(self):
        c = self.c
        c.sooritus_id = self.request.matchdict.get('sooritus_id')
        if c.sooritus_id != '0':
            c.sooritus = model.Sooritus.get(c.sooritus_id)

        toimumisaeg_id = self.request.matchdict.get('toimumisaeg_id')
        c.toimumisaeg = model.Toimumisaeg.get(toimumisaeg_id)
        c.testiosa = c.toimumisaeg.testiosa
        c.test = c.testiosa.test
        
        c.hindaja_id = self.request.matchdict.get('hindaja_id')
        if c.hindaja_id.startswith('hk'):
            c.hindamiskogum_id = int(c.hindaja_id[2:])
            c.hindamiskogum = model.Hindamiskogum.get(c.hindamiskogum_id)
        else:
            c.hindaja_id = int(c.hindaja_id)
            c.hindaja = model.Labiviija.get(c.hindaja_id)
            c.hindamiskogum_id = c.hindaja.hindamiskogum_id
            c.hindamiskogum = c.hindaja.hindamiskogum

        c.on_kriteeriumid = c.hindamiskogum.on_kriteeriumid
            
    def _has_permission(self):
        return BaseResourceController._has_permission(self)

    def _perm_params(self):
        return {'obj':self.c.test}
    
def get_tab_urls(handler, c):
    h = handler.h
    
    # paremal poolel ylesandega seotud sakkide andmed
    def f_r_tabs_data(vy, ylesanne, indlg):
        data = []
        indlg = indlg and 1 or None
        if c.r_tab == 'juhend' or ylesanne.on_hindamisjuhend or c.hindamiskogum.on_kriteeriumid:
            url = h.url('hindamine_hindajavaade_juhendid', toimumisaeg_id=c.toimumisaeg.id, vy_id=vy.id, lang=c.lang, indlg=indlg)
            label = _("Hindamisjuhend")
            if ylesanne.hindamisjuhist_muudetud():
                label = label + ' ' + h.mdi_icon('mdi-flag')
            data.append(('juhend', url, label))

        url = h.url('hindamine_hindajavaade_edit_lahendamine', toimumisaeg_id=c.toimumisaeg.id, vy_id=vy.id, id=vy.ylesanne_id, lang=c.lang, correct=1, indlg=indlg)
        data.append(('correct', url, _("Õige vastus")))      

        url = h.url('hindamine_hindajavaade_edit_lahendamine', toimumisaeg_id=c.toimumisaeg.id, vy_id=vy.id, id=vy.ylesanne_id, lang=c.lang, indlg=indlg)
        data.append(('lahendamine', url, _("Lahendaja vaade")))

        url = h.url('hindamine_hindajavaade_hindamiskysimused', toimumisaeg_id=c.toimumisaeg.id, vy_id=vy.id, lang=c.lang, indlg=indlg)
        data.append(('hindamiskysimused', url, _("Küsimused")))

        q = (model.Session.query(sa.func.count(model.Kysimus.id))
             .join(model.Kysimus.sisuplokk)
             .filter(model.Sisuplokk.ylesanne_id==ylesanne.id)
             .filter(model.Kysimus.tekstianalyys==True)
             )
        if q.scalar() > 0:
            url = h.url('hindamine_hindajavaade_tekstianalyys', toimumisaeg_id=c.toimumisaeg.id, vy_id=vy.id, lang=c.lang, indlg=indlg)
            data.append(('tekstianalyys', url, _("Tekstianalüüs")))

        return data
    
    c.f_r_tabs_data = f_r_tabs_data
    if c.vy:
        c.r_tabs_data = f_r_tabs_data(c.vy, c.vy.ylesanne, c.indlg)
