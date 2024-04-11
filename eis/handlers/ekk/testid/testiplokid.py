# -*- coding: utf-8 -*- 
# $Id: testiplokid.py 546 2016-04-02 07:49:56Z ahti $

from eis.lib.baseresource import *
_ = i18n._
#from eis.lib.basegrid import *
_ = i18n._

log = logging.getLogger(__name__)

class TestiplokidController(BaseResourceController):
    """Testiplokid
    """
    _permission = 'ekk-testid'
    _MODEL = model.Testiplokk
    _EDIT_TEMPLATE = 'ekk/testid/testiplokk.mako'
    _ITEM_FORM = forms.ekk.testid.TestiplokkForm 

    def _create(self, **kw):
        item = BaseResourceController._create(self, **kw)
        
        # kui vahetult alatesti all oli varem ylesandeid, siis tõstame need nüüd testiploki alla
        alatest = item.alatest or model.Alatest.get(item.alatest_id)
        for y in alatest.testiylesanded:
            if y.testiplokk_id is None:
                y.testiplokk = item

        return item

    #def _update(self, item, lang=None):
    #    return BaseResourceController._update(self, item, self.c.lang)

    def _after_update(self, id):
        self.success()
        return HTTPFound(location=self.url('test_struktuur1', 
                              test_id=self.request.matchdict.get('test_id'),
                              id=self.request.matchdict.get('testiosa_id'),
                              lang=self.c.lang))

    def _delete(self, item):
        testiosa = item.alatest.testiosa
        item.delete()
        model.Session.commit()
        testiosa.test.arvuta_pallid()
        model.Session.commit()
        self.success(_("Andmed on kustutatud"))

    def _after_delete(self, parent_id=None):
        return HTTPFound(location=self.url('test_struktuur1', 
                     test_id=self.request.matchdict.get('test_id'),
                     id=self.request.matchdict.get('testiosa_id'),
                     lang=self.c.lang))

    def __before__(self):
        """Väärtustame self.c.test testiga
        """
        #testiosa_id = self.request.matchdict.get('testiosa_id')
        #self.c.testiosa = model.Testiosa.get(testiosa_id)
        #alatest_id = self.request.params.get('alatest_id')
        #self.c.alatest = model.Alatest.get(alatest_id)
        test_id = self.request.matchdict.get('test_id')
        self.c.test = model.Test.get(test_id)
        self.c.lang = self.params_lang()
        super(TestiplokidController, self).__before__()

    def _perm_params(self):
        return {'obj':self.c.test}

