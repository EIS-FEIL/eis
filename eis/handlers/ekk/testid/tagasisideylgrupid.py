from eis.lib.baseresource import *
from eis.lib.basegrid import BaseGridController
from eis.lib.validationerror import neworder
_ = i18n._

log = logging.getLogger(__name__)

class TagasisideylgrupidController(BaseResourceController):
    """Tagasiside ülesandegrupid (d-testis)
    Gruppide loomine toimub struktuuri vormil, siin saab toimetada ja tõlkida.
    """
    _permission = 'ekk-testid'
    _MODEL = model.Ylesandegrupp
    _INDEX_TEMPLATE = 'ekk/testid/tagasiside.ylgrupid.mako'
    _ERROR_TEMPLATE = 'ekk/testid/tagasiside.ylgrupid.mako'
    _EDIT_TEMPLATE = 'ekk/testid/tagasiside.ylgrupp.ylesanded.mako'
    _ITEM_FORM = forms.ekk.testid.TagasisideYlgrupidForm 
    _index_after_create = True
    _create_is_tr = True
    _actions = 'index,create,show,edit,update'
    
    def _index(self):
        return self.render_to_response(self._INDEX_TEMPLATE)

    def _create(self):
        "Loetelu salvestamine"
        ylg = self.form.data['ylg']
        ylg = neworder(self, 'ylg', ylg)
        BaseGridController(self.c.testiosa.ylesandegrupid,
                           model.Ylesandegrupp,
                           parent_controller=self).save(ylg, lang=self.c.lang)        
        model.Session.flush()
        self.c.test.sum_tahemargid_lang(self.c.lang)
        return None

    def _show(self, item):
        "Grupi ülesannete kuvamine"
        self._get_ylesanded(item, True)

    def _edit(self, item):
        "Grupi ülesannete kuvamine"
        self._get_ylesanded(item, False)

    def _update(self, item):
        vyy_id = list(map(int, self.request.params.getall('vy_id')))
        osa_id = self.request.params.get('osa_id')
        if osa_id and vyy_id:
            # jätame alles ainult valitud osa
            q = (model.Session.query(model.Valitudylesanne.id)
                 .filter(model.Valitudylesanne.id.in_(vyy_id))
                 .join(model.Valitudylesanne.testiylesanne)
                 .filter(model.Testiylesanne.testiosa_id==osa_id))
            vyy_id = [vy_id for vy_id, in q.all()]
            
        for gy in list(item.grupiylesanded):
            try:
                vyy_id.remove(gy.valitudylesanne_id)
            except ValueError:
                # ylesanne pole enam grupis
                gy.delete()

        # lisame uued
        for vy_id in vyy_id:
            model.Grupiylesanne(ylesandegrupp=item,
                                valitudylesanne_id=vy_id)
        
    def _get_ylesanded(self, item, show):
        opt_osa = []
        curr_osa_id = None
        data = []
        q0 = (model.Session.query(model.Testiosa.id,
                                 model.Testiosa.nimi)
              .filter(model.Testiosa.test_id==self.c.test.id)
              .order_by(model.Testiosa.seq))
        for osa_id, osa_nimi in q0.all():
            opt_osa.append((osa_id, osa_nimi))
            q = (model.Session.query(model.Komplekt.id,
                                    model.Komplekt.tahis)
                 .join(model.Komplekt.komplektivalik)
                 .filter(model.Komplektivalik.testiosa_id==osa_id)
                 .order_by(model.Komplekt.tahis))
            o_data = []
            for k_id, k_tahis in q.all():
                q1 = (model.Session.query(model.Testiylesanne.tahis,
                                        model.Valitudylesanne.id,
                                        model.Ylesanne.id,
                                        model.Ylesanne.nimi,
                                        model.Grupiylesanne.id)
                    .filter(model.Testiylesanne.testiosa_id==osa_id)
                    .join(model.Testiylesanne.valitudylesanded)
                    .filter(model.Valitudylesanne.komplekt_id==k_id)
                    .join(model.Valitudylesanne.ylesanne)
                    )
                join = (model.Grupiylesanne,
                        sa.and_(model.Grupiylesanne.valitudylesanne_id==model.Valitudylesanne.id,
                                model.Grupiylesanne.ylesandegrupp_id==item.id)
                        )
                if show:
                    q1 = q1.join(join)
                else:
                    q1 = q1.outerjoin(join)
                q1 = q1.order_by(model.Testiylesanne.alatest_seq,
                                model.Testiylesanne.seq)
                li = [r for r in q1.all()]
                if li:
                    o_data.append((k_tahis, li))
                    # kas on see osa, millest on antud grupi ylesanded?
                    if show:
                        curr_osa_id = osa_id
                    else:
                        for r in li:
                            if r[4]:
                                curr_osa_id = osa_id
                                break
                    
            data.append((osa_id, o_data))
        if not curr_osa_id and opt_osa:
            curr_osa_id = opt_osa[0][0]
        self.c.opt_osa = opt_osa
        self.c.gy_data = data
        self.c.curr_osa_id = curr_osa_id
    
    def _after_create(self, id):
        """Mida teha peale gruppide nimekirja salvestamist
        """        
        if not self.has_errors() and not self.has_success():
            self.success()
        return self._redirect('index')
    
    def _after_update(self, id):
        """Mida teha peale grupi ülesandevaliku salvestamist
        """
        q = (model.Session.query(sa.func.count(model.Grupiylesanne.id))
             .filter_by(ylesandegrupp_id=id))
        cnt = q.scalar()
        # muudame suures aknas grupi ylesannete arvu ja suleme dialoogi
        buf = '<script>$("#ylcnt%s").text("%d");close_dialog();</script>' % (id, cnt)
        return Response(buf)
    
    def __before__(self):
        """Väärtustame self.c.test testiga
        """
        testiosa_id = self.request.matchdict.get('testiosa_id')
        self.c.testiosa = model.Testiosa.get(testiosa_id)
        self.c.test = self.c.testiosa.test
        self.c.lang = self.params_lang()
        
    def _perm_params(self):
        return {'obj':self.c.test}
