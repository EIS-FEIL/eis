from eis.lib.baseresource import *
log = logging.getLogger(__name__)
_ = i18n._

class TaotlemineController(BaseResourceController):
    """Valitakse testsessioonid
    """
    _permission = 'skannid'
    _MODEL = model.Testimiskord    
    _INDEX_TEMPLATE = 'ekk/muud/skannid.taotlemised.mako'
    _LIST_TEMPLATE = 'ekk/muud/skannid.taotlemised_list.mako'
    _DEFAULT_SORT = '-testimiskord.id' # vaikimisi sortimine
    _EDIT_TEMPLATE = 'ekk/muud/skannid.taotlemine.mako'
    _ITEM_FORM = forms.ekk.muud.SkannidTaotlemineForm
    
    def _search_default(self, q):
        return self._search(q)

    def _search(self, q):
        q = (q.join(model.Testimiskord.test)
             .filter(model.Test.testityyp==const.TESTITYYP_EKK)
             .filter(model.Test.testiosad.any(
                 model.Testiosa.vastvorm_kood==const.VASTVORM_KP))
             )
        self.c.opt_sessioon = self.c.opt.testsessioon
        if not self.c.sessioon_id and len(self.c.opt_sessioon):
            self.c.sessioon_id = self.c.opt_sessioon[0][0]
        if self.c.sessioon_id:
            q = q.filter(model.Testimiskord.testsessioon_id==int(self.c.sessioon_id))
        else:
            q = None
        return q

    def _get_korrad(self, korrad_id):
        li = []
        for kord_id in korrad_id:
            kord = model.Testimiskord.get(kord_id)
            li.append(kord)
        return li

    def _new_d(self):
        """Avaldamise muudatuste vormi avamine"""
        korrad_id = list(map(int, self.request.params.getall('kord_id')))
        self.c.korrad = self._get_korrad(korrad_id)
        self.c.list_url = self.request.params.get('list_url')
        self.c.tutv_taotlus_alates = max([k.tutv_taotlus_alates for k in self.c.korrad if k.tutv_taotlus_alates] or [None])        
        self.c.tutv_taotlus_kuni = min([k.tutv_taotlus_kuni for k in self.c.korrad if k.tutv_taotlus_kuni] or [None])
        urlid = set([k.tutv_hindamisjuhend_url for k in self.c.korrad if k.tutv_hindamisjuhend_url])
        if len(urlid) > 1:
            self.c.tutv_hindamisjuhend_url = 'hindamisjuhendid erinevad'
        elif len(urlid) == 1:
            self.c.tutv_hindamisjuhend_url = list(urlid)[0]
        return self.response_dict

    def _create(self):
        """Avaldamise muudatuste vormil salvestamine"""
        params = self.request.params
        korrad_id = list(map(int, params.getall('kord_id')))
        korrad = self._get_korrad(korrad_id)
        data = self.form.data
        for kord in korrad:
            kord.tutv_taotlus_alates = data.get('tutv_taotlus_alates')
            kord.tutv_taotlus_kuni = data.get('tutv_taotlus_kuni')            
            kord.tutv_hindamisjuhend_url = data.get('tutv_hindamisjuhend_url')

    def _after_update(self, id):
        """Peale salvestamist tuuakse ette otsingu sama lehekülg, mis enne oli.
        """
        kw = {}
        list_url = self.request.params.get('list_url')
        if list_url:
            t = self.h.update_params(list_url, _debug=True, **kw)
            kw = t[1]

        kw['kord_id'] = self.request.params.getall('kord_id')
        return self._redirect('index', **kw)   
