"Testianalüüsi kuvamine hindajale"
from eis.lib.baseresource import *
_ = i18n._
from .hkhindamine import get_tab_urls
from eis.lib.block import _html2txt
log = logging.getLogger(__name__)

class TekstianalyysController(BaseResourceController):
    _permission = 'khindamine'
    _actions = 'index'
    _INDEX_TEMPLATE = 'avalik/khindamine/hindamine_r.tekstianalyys.mako'     

    def _index_d(self):
        self._get_tab_urls()
        self.c.data = self._get_kys()
        return self.response_dict

    def _get_tab_urls(self):
        get_tab_urls(self, self.c)

    def _get_kys(self):
        "Leitakse tekstianalüüsiga küsimused"
        c = self.c
        sooritus_id = self.request.params.get('sooritus_id')

        q = (model.Session.query(model.Kysimus)
             .join(model.Kysimus.sisuplokk)
             .filter(model.Sisuplokk.ylesanne_id==c.ylesanne.id)
             .filter(model.Kysimus.tekstianalyys==True)
             .order_by(model.Sisuplokk.seq, model.Kysimus.seq)
             )
        res = []
        for kysimus in q.all():
            qv = (model.Session.query(model.Kvsisu)
                  .join(model.Kvsisu.kysimusevastus)
                  .filter(model.Kysimusevastus.kysimus_id==kysimus.id)
                  .join(model.Kysimusevastus.ylesandevastus)
                  .filter(model.Ylesandevastus.sooritus_id==sooritus_id)
                  .filter(model.Ylesandevastus.valitudylesanne_id==c.vy.id)
                  .order_by(model.Kvsisu.seq))
            li = []
            for ks in qv.all():
                meta = ks.get_txt_meta()
                if meta:
                    res.append((kysimus.kood, ks.seq, meta))
        return res

    def __before__(self):
        id = self.request.matchdict.get('vy_id')
        c = self.c
        c.vy = model.Valitudylesanne.get(id)
        c.ylesanne = c.vy.ylesanne
        toimumisaeg_id = self.request.matchdict.get('toimumisaeg_id')
        c.toimumisaeg = model.Toimumisaeg.get(toimumisaeg_id)
        c.lang = self.params_lang()
        c.indlg = self.request.params.get('indlg')
        if c.toimumisaeg.testiosa.lotv:
            hk_id = c.vy.hindamiskogum_id
        else:
            hk_id = c.vy.testiylesanne.hindamiskogum_id
        c.hindamiskogum = model.Hindamiskogum.get(hk_id)
        
    def _has_permission(self):
        # suulise hindamise korral on antud c.testiruum
        # kirjaliku hindamise korral on antud c.toimumisaeg
        c = self.c
        hk_id = c.hindamiskogum.id
        c.hindaja = c.toimumisaeg.get_hindaja(c.user.id, hindamiskogum_id=hk_id)
        return self.c.hindaja is not None

