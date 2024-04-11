from eis.lib.baseresource import *
from .komplektotsiylesanded import filter_y_st
_ = i18n._

log = logging.getLogger(__name__)

class StruktuurOtsiylesandedController(BaseResourceController):

    _permission = 'ekk-testid'
    _MODEL = model.Testiylesanne
    _EDIT_TEMPLATE = 'ekk/testid/struktuur.otsiylesanded.mako'
    _INDEX_TEMPLATE = 'ekk/testid/struktuur.otsiylesanded.mako'
    _LIST_TEMPLATE = 'ekk/testid/struktuur.otsiylesanded_list.mako'
    _SEARCH_FORM = forms.ekk.testid.StruktuurOtsiylesandedForm 
    _DEFAULT_SORT = 'ylesanne.id' # vaikimisi sortimine

    def _query(self):
        q = model.Ylesanne.query.filter_by(etest=True)
        return q

    def _search_default(self, q):
        c = self.c
        c.aine = c.test.aine_kood
        return self._search(q)

    def _search(self, q):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        c = self.c
        if c.test.testiliik_kood == const.TESTILIIK_DIAG2:
            c.arvutihinnatav = True

        staatused = list()
        if c.st_pedagoog:
            staatused.append(const.Y_STAATUS_PEDAGOOG)
        if c.st_avalik:
            staatused.append(const.Y_STAATUS_AVALIK)
        if staatused:
            if len(staatused) == 1:
                q = q.filter(model.Ylesanne.staatus == staatused[0])
            else:
                q = q.filter(model.Ylesanne.staatus.in_(staatused))
        q = filter_y_st(self, q, c.test, False)

        if c.ylkogu_id:
            q = q.filter(model.Ylesanne.koguylesanded.any(
                model.Koguylesanne.ylesandekogu_id==c.ylkogu_id))

        for lang in c.test.keeled:        
            key = f'lang_{lang}'
            if c.__getattr__(key):
                q = q.filter(model.Ylesanne.skeeled.like('%' + lang + '%'))
                
        # kontrollime, et ylesanne juba ei esineks selles komplektis
        komplektid_id = []
        for kv in c.testiosa.komplektivalikud:
            for k in kv.komplektid:
                komplektid_id.append(k.id)
        q = q.filter(~ model.Ylesanne.valitudylesanded.any(
            model.Valitudylesanne.komplekt_id.in_(komplektid_id)))

        if c.aine:
            f_aine = model.Ylesandeaine.aine_kood == c.aine
            if c.oskus:
                f_aine = sa.and_(f_aine, model.Ylesandeaine.oskus_kood==c.oskus)

            if c.valdkond:
                if c.teema:
                    f_teema = (model.Ylesandeaine.ylesandeteemad
                               .any(sa.and_(model.Ylesandeteema.teema_kood==c.valdkond,
                                            model.Ylesandeteema.alateema_kood==c.teema)
                                    )
                               )
                else:
                    f_teema = (model.Ylesandeaine.ylesandeteemad
                               .any(model.Ylesandeteema.teema_kood==c.valdkond))
                f_aine = sa.and_(f_aine, f_teema)
            q = q.filter(model.Ylesanne.ylesandeained.any(f_aine))

        y_id = None
        if c.id:
            try:
                y_id = int(c.id)
            except:
                y_id = 0
            q = q.filter_by(id=y_id)
                
        if c.nimi:
            q = q.filter(model.Ylesanne.nimi.ilike(c.nimi))
        if c.marksona:
            like_expr = '%%%s%%' % c.marksona
            q = q.filter(sa.or_(model.Ylesanne.marksonad.ilike(like_expr),
                                model.Ylesanne.trans.any(model.T_Ylesanne.marksonad.ilike(like_expr)))
                         )
                         
        if c.mote:
            q = q.filter(model.Ylesanne.motlemistasandid\
                         .any(model.Motlemistasand.kood==c.mote))            
        if c.aste:
            aste_bit = c.opt.aste_bit(c.aste) or 0
            q = q.filter(model.Ylesanne.aste_mask.op('&')(aste_bit) > 0)                                                
        if c.max_pallid:
            q = q.filter_by(max_pallid=c.max_pallid)
        #if c.raskus:
        #    q = q.filter_by(raskus=c.raskus)
        #if c.eristusindeks:
        #    q = q.filter_by(eristusindeks=c.eristusindeks)
        if c.tyyp:
            q = q.filter(model.Ylesanne.sisuplokid\
                             .any(model.Sisuplokk.tyyp==c.tyyp))
        if c.arvutihinnatav:
            q = q.filter_by(arvutihinnatav=True)
        if c.keeletase:
            q = q.filter(model.Ylesanne.keeletase_kood==c.keeletase)
        #model.log_query(q)
        if y_id and not q.count():
            self._explain_noresult(y_id, komplektid_id)
        return q

    def _explain_noresult(self, y_id, komplektid_id):
        "Selgitame, miks y_id ei kuvata loetelus"
        c = self.c
        ylesanne = model.Ylesanne.get(y_id)
        if not ylesanne:
            self.error(_("Ülesannet {id} ei ole olemas").format(id=y_id))
            return
        elif c.test.testiliik_kood == const.TESTILIIK_DIAG2 and not ylesanne.arvutihinnatav:
            self.error(_("Ülesanne {id} pole arvutihinnatav").format(id=y_id))
            return
        else:
            q = (model.Valitudylesanne.query
                 .filter(model.Valitudylesanne.ylesanne_id==y_id)
                 .filter(model.Valitudylesanne.komplekt_id.in_(komplektid_id)))
            if q.count():
                self.error(_("Ülesanne {id} on juba komplekti lisatud").format(id=y_id))
                return
        if c.aine:
            q = (model.Ylesandeaine.query
                 .filter(model.Ylesandeaine.ylesanne_id==y_id)
                 .filter(model.Ylesandeaine.aine_kood==c.aine))
            if not q.count():
                self.error(_("Ülesanne {id} ei kuulu antud õppeainesse").format(id=y_id))                
                return
        keeled = ylesanne.keeled
        for lang in c.test.keeled:        
            key = f'lang_{lang}'
            if c.__getattr__(key) and lang not in keeled:
                self.error(_("Ülesanne {id} ei ole antud keeles").format(id=y_id))                
                return
        self.error(_("Ülesanne {id} ei vasta otsingutingimustele").format(id=y_id))
                
    def _order_join(self, q, tablename):
        return q

    def update(self):
        """Ülesannete lisamine testile.
        id on seq
        """
        params = self.request.params
        testiosa = self.c.testiosa
        kv = testiosa.give_komplektivalik()
        komplekt = kv.give_komplekt()
        if komplekt.skeeled != self.c.test.skeeled:
            komplekt.skeeled = self.c.test.skeeled
        seq = len(testiosa.testiylesanded)
        hkogum = kv.give_default_hindamiskogum()
        on_jatk = params.get('on_jatk') and True or False
        alatest = testiplokk = None
        alatest_id = params.get('alatest_id')
        testiplokk_id = params.get('testiplokk_id')
        if alatest_id:
            alatest = model.Alatest.get(alatest_id)
            assert alatest.testiosa_id == testiosa.id, 'vale alatest'
        if testiplokk_id:
            testiplokk = model.Testiplokk.get(testiplokk_id)
            assert testiplokk.alatest_id == alatest.id, 'vale testiplokk'
        
        for ylesanne_id in params.getall('ylesanne_id'):
            seq += 1
            ylesanne = model.Ylesanne.get(ylesanne_id)
            if ylesanne.max_pallid is None:
                ylesanne.max_pallid = ylesanne.get_max_pallid()
            if ylesanne.salastatud and not ylesanne._has_use_permission(self.c.user.get_kasutaja()):
                self.error(_("Puudub õigus salastatud ülesande testi lisamiseks"))
            else:
                ty = model.Testiylesanne(testiosa=testiosa, 
                                         valikute_arv=1, 
                                         hindamiskogum=hkogum,
                                         seq=seq, 
                                         tahis=str(seq),
                                         naita_max_p=testiosa.naita_max_p,
                                         arvutihinnatav=ylesanne.arvutihinnatav,
                                         max_pallid=ylesanne.get_max_pallid(),
                                         on_jatk=on_jatk)
                testiosa.testiylesanded.append(ty)
                if alatest:
                    ty.alatest = alatest
                if testiplokk:
                    ty.testiplokk = testiplokk
                li_vy = ty.give_valitudylesanded(komplekt)
                li_vy[0].ylesanne_id = ylesanne.id
                li_vy[0].koefitsient = 1.

        model.Session.commit()
        hkogum.arvuta_pallid(testiosa.lotv)
        self.c.test.arvuta_pallid()
        model.Session.commit()
        self.success()       
        return HTTPFound(location=self.url('test_edit_struktuur1', 
                                           test_id=self.c.test.id,
                                           id=self.c.testiosa.id,
                                           lang=self.c.lang))

    def _delete(self, item):
        testiosa = item.testiosa
        hk = item.hindamiskogum
        item.delete()
        model.Session.commit()
        testiosa.test.arvuta_pallid()
        if hk:
            hk.arvuta_pallid(testiosa.lotv)
        model.Session.commit()
        self.success(_("Andmed on kustutatud"))

    def _after_delete(self, parent_id=None):
        return HTTPFound(location=self.url('test_edit_struktuur1', 
                                           test_id=self.c.test.id,
                                           id=self.c.testiosa.id,
                                           lang=self.c.lang))
    
    def __before__(self):
        """Väärtustame self.c.test testiga
        """
        testiosa_id = self.request.matchdict.get('testiosa_id')
        self.c.testiosa = model.Testiosa.get(testiosa_id)
        self.c.test = self.c.testiosa.test
        self.c.lang = self.params_lang()
        super(StruktuurOtsiylesandedController, self).__before__()

    def _perm_params(self):
        return {'obj':self.c.test}

