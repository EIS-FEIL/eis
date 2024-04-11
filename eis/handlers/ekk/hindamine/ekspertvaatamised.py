from simplejson import dumps
from eis.lib.baseresource import *
_ = i18n._
from eis.lib.block import BlockController
from eis.lib.resultentry import ResultEntry
from eis.handlers.avalik.lahendamine.esitlus import EsitlusController
from .hindajavaade_hkhindamine import get_tab_urls
import logging
log = logging.getLogger(__name__)

class EkspertvaatamisedController(BaseResourceController, EsitlusController):
    """Eksperthindaja hindab või vaatab lahendaja kirjalikku lahendust.
    """
    _permission = 'eksperthindamine'
    _MODEL = model.Testiylesanne
    _INDEX_TEMPLATE = 'ekk/hindamine/ekspert.hindamine.mako'
    _EDIT_TEMPLATE = 'ekk/hindamine/ekspert.hindamine.ylesanne.mako'    
    _ITEM_FORM = forms.avalik.hindamine.KHindamineForm
    _get_is_readonly = False
    _actions = 'index,edit,show,download'
    _actionstask = 'showtask'
    
    def index(self):
        # hindamise lehe avamine või
        # hindamiskriteeriumitega hindamiskogumis teise ylesande avamine
        op = self.request.params.get('op')
        ty_id = self._get_next_id(op) or None
        self._ty_edit(ty_id)

        if not self.request.params.get('partial'):
            template = self._INDEX_TEMPLATE
        else:
            if ty_id:
                # ylesande vahetamisel: ylesande osa 
                self.c.ainult_yl_vahetub = True
                # muul juhul ylesande osa + kriteeritumite osa
            template = self._EDIT_TEMPLATE
        return self.render_to_response(template)

    def _get_ylesanded(self):
        c = self.c
        if not c.komplekt:
            # komplekt pole määratud
            return
        komplektis_ty_id = c.komplekt.get_testiylesanded_id(c.hindamiskogum)
        c.testiylesanded_id = komplektis_ty_id
        
    def _redirect_to_index(self, is_json):
        c = self.c
        url = self.url('hindamine_ekspert_kogum', toimumisaeg_id=c.toimumisaeg.id, id=c.sooritus.id)
        if is_json and c.testiosa.vastvorm_kood in (const.VASTVORM_SH, const.VASTVORM_SP):
            is_json = False
        if is_json:
            return Response(json_body={'redirect': url})
        else:
            return HTTPFound(location=url)

    def _show(self, item):
        return self._edit(item)

    def _edit(self, item):
        return self._ty_edit(item.id)

    def _ty_edit(self, ty_id):
        c = self.c
        # hindamiste vaatamine

        c.show_tulemus = True
        c.eksperdivaade = True
        c.holek = c.sooritus.give_hindamisolek(c.hindamiskogum)
        c.test = c.testiosa.test
        c.komplekt = c.holek.komplekt
        self._get_ylesanded()
        if not ty_id:
            for ty_id in c.testiylesanded_id:
                break
        if not c.komplekt:
            #self.error(_("Ülesandekomplekt pole teada"))
            pass
        elif ty_id:
            # on ylesandeid, mida hinnata
            c.ty = model.Testiylesanne.get(ty_id)
            c.ylesandevastus = c.sooritus.get_ylesandevastus(ty_id)
            if c.ylesandevastus:
                c.vy = c.ylesandevastus.valitudylesanne
            else:
                # vbl d-testi jätkuylesanne
                c.vy = c.komplekt.getq_valitudylesanne(None, c.ty.id)
            c.ylesanne = c.vy.ylesanne
        else:
            # miskipärast ei ole sooritajal yhtki ylesannet vaja hinnata
            c.pole_hinnata = True

        # funktsioonid mako sees kasutamiseks
        c.BlockController = BlockController
        c.lang = c.sooritus.sooritaja.lang

        c.read_only = True
        self._get_tab_urls()

        if c.holek:
            c.hindamised = [rcd for rcd in c.holek.hindamised \
                            if rcd != c.hindamine and rcd.sisestus==1 and \
                            rcd.staatus not in (const.H_STAATUS_LYKATUD, const.H_STAATUS_SUUNATUD)]
            if c.vy:
                c.yhindamised = [(hindamine, hindamine.get_vy_ylesandehinne(c.vy.id)) \
                                 for hindamine in c.hindamised]
            
    def _get_tab_urls(self):
        # vasakul poolel ylesande avamise (GET) või hindamise salvestamise (POST) URL
        c = self.c
        h = self.h
        def f_submit_url(ty_id):
            if ty_id:
                # ylesande hindamine
                return h.url('hindamine_ekspert_vaatamine', sooritus_id=c.sooritus.id, 
                             toimumisaeg_id=c.toimumisaeg.id, hindamiskogum_id=c.hindamiskogum_id, id=ty_id)
            else:
                # hindamiskogumi hindamiskriteeriumite hindamine
                return h.url('hindamine_ekspert_vaatamised', sooritus_id=c.sooritus.id, 
                             toimumisaeg_id=c.toimumisaeg.id, hindamiskogum_id=c.hindaja_id)

        c.f_submit_url = f_submit_url

        get_tab_urls(self, self.c)

    def _get_next_id(self, op):
        if op:
            m = re.match(r'.*\_([0-9]+)', op)
            if m:
                # on antud eelmine, järgmine või sakist valitud ylesanne, kuhu edasi minna
                ty_id = int(m.groups()[0])
                return ty_id

    def _download(self, id, format=None):
        """Laadi helifail alla"""
        item = model.Helivastusfail.get(id)
        if not item:
            raise NotFound('Kirjet %s ei leitud' % id)        
        q = (model.Session.query(model.Helivastus.id)
             .filter_by(helivastusfail_id=item.id)
             .join(model.Helivastus.sooritus)
             .filter(model.Sooritus.toimumisaeg_id==self.c.toimumisaeg.id)
             )
        if not q.count():
            raise NotFound('Puudub ligipääsuõigus')

        mimetype = item.mimetype
        if not mimetype:
            (mimetype, encoding) = mimetypes.guess_type(item.filename)
            
        return utils.download(item.filedata, item.filename, mimetype)

    def showtask(self):
        "Ülesande kuvamine - ei kasutata sooritamisel, aga on kasutusel päritud klassides, kus käib vaatamine"
        c = self.c
        c.read_only = True
        c.ty = ty = self._checkty()

        c.ylesandevastus = self._get_ylesandevastus(ty.id)
        if not c.ylesandevastus:
            self.error(_("Ülesannet pole lahendatud"))
            return self.render_to_response('/avalik/lahendamine/esitlus.message.mako')
        #c.responses = c.ylesandevastus.get_responses()
        c.vy = vy = c.ylesandevastus.valitudylesanne
        c.ylesanne = vy.ylesanne
        c.lang = c.sooritus.sooritaja.lang
        c.responses = {kv.kood: kv for kv in c.ylesandevastus.kysimusevastused}
        c.correct_responses = c.ylesanne.correct_responses(c.ylesandevastus,
                                                           lang=c.lang,
                                                           naide_only=True,
                                                           hindaja=True,
                                                           naidistega=True,
                                                           as_tip=True)
        hindamine = self._give_hindamine()
        return self._gentask(yv=c.ylesandevastus,
                             hindaja=c.hindaja,
                             hindamine_id=hindamine and hindamine.id or None,
                             pcorrect=c.test.oige_naitamine)

    def _give_hindamine(self):
        pass

    def _get_ylesandevastus(self, ty_id, komplekt_id=None):
        return self.c.sooritus.getq_ylesandevastus(ty_id, komplekt_id)

    def _checkty(self):
        ty_id = self.request.matchdict.get('ty_id')
        ty = model.Testiylesanne.get(ty_id)
        assert ty.testiosa.test_id == self.c.test.id, 'vale test'
        return ty

    def __before__(self):
        c = self.c
        sooritus_id = self.request.matchdict.get('sooritus_id')
        c.sooritus = model.Sooritus.get(sooritus_id)

        toimumisaeg_id = self.request.matchdict.get('toimumisaeg_id')
        c.toimumisaeg = model.Toimumisaeg.get(toimumisaeg_id)
        c.testiosa = c.toimumisaeg.testiosa
        c.test = c.testiosa.test

        hindamiskogum_id = self.request.matchdict.get('hindamiskogum_id')
        if hindamiskogum_id:
            # puudub ettepanekhindamise pathis
            c.hindamiskogum_id = int(hindamiskogum_id)
            c.hindamiskogum = model.Hindamiskogum.get(c.hindamiskogum_id)
            c.on_kriteeriumid = c.hindamiskogum.on_kriteeriumid
            assert c.hindamiskogum.testiosa_id == c.testiosa.id, 'vale hk'

        c.eksperdivaade = True

    def _perm_params(self):
        return {'obj': self.c.test}

