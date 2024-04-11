from eis.lib.baseresource import *
from .testiosavalik import Testiosavalik
log = logging.getLogger(__name__)

class StruktuurController(BaseResourceController, Testiosavalik):

    _permission = 'testid'
    _MODEL = model.Test
    _EDIT_TEMPLATE = 'avalik/testid/struktuur.mako'
    _INDEX_TEMPLATE = 'avalik/testid/struktuur.mako'
    _ITEM_FORM = forms.avalik.testid.StruktuurForm 
    _actions = 'show,update,edit' # võimalikud tegevused

    def _update(self, item):
        c = self.c
        testiosa = item.give_testiosa()
        testiosa.from_form(self.form.data, 'f_')

        order = self.request.params.get('order')
        if order:
            # order on selline: ylesanne_13,ylesanne_21,ylesanne_2
            seq_testiylesanne = 0
            for name in order.split(','):
                row_type, id = name.split('_')
                testiylesanne = model.Testiylesanne.get(id)
                assert testiylesanne.testiosa_id == testiosa.id, 'vale testiosa'
                seq_testiylesanne += 1
                testiylesanne.seq = seq_testiylesanne
                testiylesanne.tahis = str(seq_testiylesanne)

        # hindepallide määramine
        for ty_rcd in self.form.data.get('ty'):
            ty = model.Testiylesanne.get(ty_rcd['id'])
            assert ty.testiosa_id == testiosa.id, 'Vale testiosa'
            max_pallid = ty_rcd.get('max_pallid')
            if max_pallid:
                ty.max_pallid = max_pallid
                for vy in ty.valitudylesanded:
                    if vy.ylesanne.max_pallid:
                        vy.koefitsient = max_pallid / vy.ylesanne.max_pallid
                    else:
                        vy.koefitsient = 0

        kv = testiosa.give_komplektivalik()
        hkogum = kv.give_default_hindamiskogum()
        hkogum.arvuta_pallid(testiosa.lotv)
        item.arvuta_pallid()
        return item
    
    def _after_update(self, id):
        """Mida teha peale õnnestunud salvestamist
        """        
        if not self.has_errors():
            self.success()
        return self._redirect('edit', id,
                              testiruum_id=self.c.testiruum_id,
                              lisatkst=self.request.params.get('lisatkst') and 1 or None)

    def _show(self, item):
        if self.c.test.testiliik_kood == const.TESTILIIK_KOOLIPSYH:
            # koolipsyhholoogi testil ei kuvata struktuuri vormi
            raise HTTPFound(location=self.url('test', id=item.id))
        return super()._show(item)
                            
    def _edit(self, item):
        self._redirect_ruum()
            
    def __before__(self):
        """Väärtustame self.c.test testiga
        """
        c = self.c
        Testiosavalik.set_test_testiosa(self, 'testiruum_id','id')        
        super(StruktuurController, self).__before__()

    def _perm_params(self):
        return {'obj':self.c.test}
        
    def _no_permission_url(self, action):
        "Kui test pole enam ligipääsetav, siis võib olla ligipääsetav tulemuste vorm"
        c = self.c
        if c.user.has_permission('omanimekirjad', const.BT_CREATE, c.test) or \
               c.user.has_permission('omanimekirjad', const.BT_VIEW, testiruum_id=c.testiruum_id):
            url = self.h.url('test_nimekirjad',test_id=c.test_id, testiruum_id=c.testiruum_id)
            return url

