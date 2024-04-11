from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class ErialatestidController(BaseResourceController):

    _permission = 'ekk-testid'
    _MODEL = model.Komplekt
    _EDIT_TEMPLATE = 'ekk/testid/erialatestid.mako'
    _ITEM_FORM = forms.ekk.testid.ErialatestidForm 
    _get_is_readonly = False
    
    def _update(self, item):
        if len(self.c.komplekt.komplektivalik.testiosa.alatestid):
            self._update_erialatestid()
        else:
            self._update_komplekt()

    def _update_erialatestid(self):
        testiosa_lisaaeg = 0
        testiosa_dif_hindamine = 0
        for rcd in self.form.data.get('ek'):
            alatest_id = rcd.get('alatest_id')
            lisaaeg = rcd.get('lisaaeg')
            dif_hindamine = rcd.get('dif_hindamine')
            if dif_hindamine or lisaaeg:
                k = self.c.komplekt.give_erialatest(alatest_id)
                k.dif_hindamine = dif_hindamine and True or False
                k.lisaaeg = lisaaeg
                testiosa_lisaaeg += lisaaeg or 0
                testiosa_dif_hindamine |= dif_hindamine or 0
            else:
                k = self.c.komplekt.get_erialatest(alatest_id)
                if k is not None:
                    k.delete()
        self.c.komplekt.lisaaeg = testiosa_lisaaeg
        self.c.komplekt.dif_hindamine = testiosa_dif_hindamine and True or False

    def _update_komplekt(self):
        for rcd in self.form.data.get('ek'):
            self.c.komplekt.lisaaeg = rcd.get('lisaaeg')
            self.c.komplekt.dif_hindamine = rcd.get('dif_hindamine') and True or False
            break

    def __before__(self):
        """Väärtustame self.c.test testiga
        """
        test_id = self.request.matchdict.get('test_id')
        self.c.test = model.Test.get(test_id)
        self.c.komplekt_id = self.request.matchdict.get('id')
        self.c.komplekt = model.Komplekt.get(self.c.komplekt_id)
        self.c.komplektivalik = self.c.komplekt.komplektivalik
        self.c.komplektivalik_id = self.c.komplektivalik.id
        self.c.testiosa = self.c.komplektivalik.testiosa
        BaseResourceController.__before__(self)

    def _perm_params(self):
        return {'obj':self.c.test}
