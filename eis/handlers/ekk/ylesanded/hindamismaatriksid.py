"Küsimuse hindamismaatriksi kuvamine"
import math
from eis.lib.baseresource import *
_ = i18n._
from eis.lib.block import BlockController
log = logging.getLogger(__name__)

class HindamismaatriksidController(BaseResourceController):
    _permission = 'ylesanded'
    _MODEL = model.Hindamismaatriks
    _INDEX_TEMPLATE = 'sisuplokk/hindamismaatriksid_list.mako'
    _LIST_TEMPLATE = 'sisuplokk/hindamismaatriksid_list.mako'
    _ITEM_FORM = forms.ekk.hindamine.AnalyyskysimusForm
    _default_items_per_page = 50
   
    def _search_default(self, q):
        return self._search(q)
    
    def _search(self, q1):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        c = self.c
        c.block = c.kysimus.sisuplokk
        tulemus = c.kysimus.tulemus
        if tulemus:
            c.baastyyp = tulemus.baastyyp
        self._set_list_url()
       
        q = (model.Session.query(model.Hindamismaatriks)
             .filter_by(maatriks=c.maatriks or 1)
             .join(model.Hindamismaatriks.tulemus)
             .join(model.Tulemus.kysimused)
             .filter(model.Kysimus.id==c.kysimus.id)
             )
        if c.block.tyyp == const.INTER_PUNKT:
            # kuvatakse ainult yhe lynga osa hindamismaatriksist
            kood2 = self.request.params.get('kood2')
            q = q.filter(model.Hindamismaatriks.kood2==kood2)
        return q

    def _order(self, q, sort=None):
        return q.order_by(model.Hindamismaatriks.jrk,
                          model.Hindamismaatriks.id)

    def _paginate(self, q):
        if not self.c.kysimus or not self.c.kysimus.id:
            # uus kysimus
            items = []
        else:
            items = BaseResourceController._paginate(self, q)
            if self.c.page == '0':
                items.page = 0
                items.items = list(q.all())
        self.c.hm_items = items
        #model.log_query(q)
        return items

    def _set_list_url(self):
        c = self.c
        kw = {'ylesanne_id': c.ylesanne.id,
              'sisuplokk_id': c.block.id,
              'kysimus_id': c.kysimus.id,
              'maatriks': c.maatriks,
              'prefix': c.prefix,
              'is_edit': c.is_edit or '',
              'baastyyp': c.baastyyp}
        c.hm_list_url = self.url_current('index', **kw)
        log.debug('LIST URL %s' % c.is_edit)

    def get_items(self):
        q = self._order(self._search(self._query()))
        return self._paginate(q)                
   
    def __before__(self):
        c = self.c
        ylesanne_id = self.request.matchdict.get('ylesanne_id')
        c.ylesanne = model.Ylesanne.get(ylesanne_id)
        block_id = self.request.matchdict.get('sisuplokk_id')
        c.block = model.Sisuplokk.get(block_id)
        kysimus_id = self.request.matchdict.get('kysimus_id')
        c.kysimus = model.Kysimus.get(kysimus_id)
        c.maatriks = self.request.params.get('maatriks') or 1
        c.baastyyp = self.request.params.get('baastyyp')
        c.prefix = self.request.params.get('prefix')
        c.is_edit = self.request.params.get('is_edit')
        
    def _perm_params(self):
        return {'obj':self.c.ylesanne}
