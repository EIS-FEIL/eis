from eis.lib.baseresource import *
from eis.lib.basegrid import BaseGridController
_ = i18n._

log = logging.getLogger(__name__)

class YlesandegrupidController(BaseResourceController):
    """Ylesandegrupid diagnoosivas testis
    """
    _permission = 'ekk-testid'
    _MODEL = model.Ylesandegrupp
    _INDEX_TEMPLATE = 'ekk/testid/ylesandegrupid_list.mako'
    _EDIT_TEMPLATE = 'ekk/testid/ylesandegrupp.new.mako'
    _ITEM_FORM = forms.ekk.testid.YlesandegruppForm 
    _NP_MODIFY_TEMPLATE = 'ekk/testid/ylesandegrupid_modify.mako'
    _index_after_create = True

    def _index_modify(self):
        "normipunktid.mako sees dialoogiakna avamine"
        self.c.lang = self.params_lang()        
        return self.render_to_response(self._NP_MODIFY_TEMPLATE)

    def _create_modify(self):
        "normipunktid.mako seest avatud dialoogiaknas salvestamine"
        lang = self.c.lang = self.params_lang()
        self.form = Form(self.request, schema=forms.ekk.testid.YlesandegrupidModifyForm)
        err = False
        if self.form.validate():
            try:
                ylg = self.form.list_in_posted_order('ylg')
                if not lang:
                    for ind, r in enumerate(ylg):
                        r['seq'] = ind
                BaseGridController(self.c.testiosa.ylesandegrupid,
                                   model.Ylesandegrupp).save(ylg, lang=lang)

                model.Session.flush()
                self.c.test.sum_tahemargid_lang(lang)

            except ValidationError as e:
                self.form.errors = e.errors
                err = True

        if self.form.errors or err:
            model.Session.rollback()
            return self.form.render(self._NP_MODIFY_TEMPLATE, extra_info=self.response_dict)
        else:
            model.Session.commit()
            self.c.is_saved = True
            self.c.is_edit = self.c.is_tr = False
            return self.render_to_response('ekk/testid/ylesandegrupid_modify.mako')

    def _create(self, **kw):
        item = model.Ylesandegrupp(testiosa_id=self.c.testiosa.id)
        item.nimi = self.form.data.get('yg_nimi') or 'Grupp'
        self._update(item)
        return item
    
    def _update(self, item, lang=None):
        "struktuuri vormil yhe grupi ylesannete salvestamine"
        s_vyy_id = self.request.params.get('vyy_id')
        vyy_id = list(map(int, [r for r in s_vyy_id.split(',') if r]))
        rows = [{'valitudylesanne_id': vy_id} for vy_id in vyy_id]
        
        BaseGridController(item.grupiylesanded,
                           model.Grupiylesanne,
                           pkey='valitudylesanne_id').save(rows)
        model.Session.commit()
        return self._redirect('index')

    def _delete(self, item):
        "struktuuri vormilt grupi kustutamine"
        item.delete()
        model.Session.commit()
        return self._redirect('index')
    
    def __before__(self):
        """Väärtustame self.c.test testiga
        """
        testiosa_id = self.request.matchdict.get('testiosa_id')
        self.c.testiosa = model.Testiosa.get(testiosa_id)
        self.c.test = self.c.testiosa.test
        self.c.can_np = True
        #self.c.lang = self.params_lang()
        super(YlesandegrupidController, self).__before__()

    def _perm_params(self):
        return {'obj':self.c.test}

