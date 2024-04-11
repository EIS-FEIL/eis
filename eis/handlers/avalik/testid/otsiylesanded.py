# -*- coding: utf-8 -*- 

from eis.lib.baseresource import *

log = logging.getLogger(__name__)

class OtsiylesandedController(BaseResourceController):

    _permission = 'testid'
    _MODEL = model.Testiylesanne
    #_EDIT_TEMPLATE = 'avalik/testid/otsiylesanded.mako'
    _INDEX_TEMPLATE = 'avalik/testid/otsiylesanded.mako'
    _LIST_TEMPLATE = 'avalik/testid/otsiylesanded_list.mako'
    _SEARCH_FORM = forms.avalik.testid.OtsiylesandedForm
    _ITEM_FORM = forms.avalik.testid.YlesandedForm 
    _DEFAULT_SORT = 'ylesanne.id' # vaikimisi sortimine
    _log_params_never = True # et saaks readonly ylesanded.py transaktsioonist kutsuda
    #_upath = '/tookogumik/ylesandeotsing'
    _actions = 'index' # võimalikud tegevused
    
    def _query(self):
        q = (model.Ylesanne.query
             .filter_by(etest=True)
             .filter_by(adaptiivne=False)
             .filter_by(salastatud=0)
             )
        if self.c.user.on_pedagoog:
            fst = model.Ylesanne.staatus.in_((const.Y_STAATUS_AVALIK, const.Y_STAATUS_PEDAGOOG))
        else:
            fst = model.Ylesanne.staatus == const.Y_STAATUS_AVALIK

        q = q.filter(sa.or_(fst,
                            sa.and_(model.Ylesanne.staatus.in_(const.Y_ST_AV),
                                    model.Ylesanne.ylesandeisikud.any(
                                        sa.and_(model.Ylesandeisik.kasutaja_id==self.c.user.id,
                                                model.Ylesandeisik.kasutajagrupp_id==const.GRUPP_Y_KOOSTAJA))
                                    )
                            ))

        return q

    def _search_default(self, q):
        pass

    def _search(self, q):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        c = self.c
        if c.ylesanne_id:
            q = q.filter_by(id=c.ylesanne_id)

        if c.aine:
            f_aine = model.Ylesandeaine.aine_kood==c.aine
            if c.teema:
                teema = model.Klrida.get_by_kood('TEEMA', kood=c.teema, ylem_kood=c.aine)            
                c.teema_id = teema and teema.id
                if c.alateema:
                    f_teema = (model.Ylesandeaine.ylesandeteemad
                               .any(sa.and_(model.Ylesandeteema.teema_kood==c.teema,
                                            model.Ylesandeteema.alateema_kood==c.alateema)
                                    )
                               )
                else:
                    f_teema = (model.Ylesandeaine.ylesandeteemad
                               .any(model.Ylesandeteema.teema_kood==c.teema))
                f_aine = sa.and_(f_aine, f_teema)
            if self.c.opitulemus_id:
                f_aine = sa.and_(f_aine, model.Ylesandeaine.ylopitulemused.any(
                    model.Ylopitulemus.opitulemus_klrida_id==self.c.opitulemus_id))
            q = q.filter(model.Ylesanne.ylesandeained.any(f_aine))
            
        if c.aste:
            aste_bit = c.opt.aste_bit(c.aste) or 0
            q = q.filter(model.Ylesanne.aste_mask.op('&')(aste_bit) > 0)
            
            
        # if c.testiliik:
        #     q = q.filter(model.Ylesanne.testiliigid
        #                  .any(model.Testiliik.kood==c.testiliik))

        if c.keeletase:
            q = q.filter_by(keeletase_kood=c.keeletase)
        if c.lang:
            q = q.filter(model.Ylesanne.skeeled.like('%' + c.lang + '%'))

        if c.kysimus:
            q = q.filter(model.Ylesanne.sisuplokid\
                             .any(model.Sisuplokk.tyyp==c.kysimus))
        if c.term:
            term = '%' + c.term + '%'
            Aine = sa.orm.aliased(model.Klrida, name='aine')
            Teema = sa.orm.aliased(model.Klrida, name='teema')
            Alateema = sa.orm.aliased(model.Klrida, name='alateema')
            Opitulemus = sa.orm.aliased(model.Klrida, name='opitulemus')
            li = (model.Ylesanne.nimi.ilike(term),
                  model.Ylesanne.markus.ilike(term),
                  model.Ylesanne.marksonad.ilike(term),
                  model.Ylesanne.trans.any(model.T_Ylesanne.marksonad.ilike(term)),
                  model.Ylesanne.ylesandeained.any(
                      sa.or_(model.Ylesandeaine.ylesandeteemad.any(
                          sa.and_(Aine.klassifikaator_kood=='AINE',
                                  Aine.kood==model.Ylesandeaine.aine_kood,
                                  Teema.kood==model.Ylesandeteema.teema_kood,
                                  Teema.klassifikaator_kood=='TEEMA',
                                  Teema.ylem_id==Aine.id,
                                  sa.or_(
                                      Teema.nimi.ilike(term),
                                      sa.exists().where(
                                          sa.and_(Alateema.nimi.ilike(term),
                                                  Alateema.klassifikaator_kood=='ALATEEMA',
                                                  Alateema.ylem_id==Teema.id))
                                      )
                                  )),
                             model.Ylesandeaine.ylopitulemused.any(
                                 sa.and_(
                                     model.Ylopitulemus.opitulemus_klrida_id==Opitulemus.id,
                                     Opitulemus.nimi.ilike(term)
                                 ))
                             )
                      )
                  )
            q = q.filter(sa.or_(*li))

        # kontrollime, et ylesanne juba ei esineks selles komplektis
        komplekt = self.c.test.give_testiosa().give_komplektivalik().give_komplekt()
        if komplekt.id:
            q = q.filter(~ model.Ylesanne.valitudylesanded.any(model.Valitudylesanne.komplekt_id==komplekt.id))

        #model.log_query(q)
        return q

    def _get_current_upath(self):
        # anname upath ette, et leitaks parameetrid ka siis,
        # kui request on tehtud Ylesanded kontrollerile
        return self.h.url_current()
    
    def __before__(self):
        """Väärtustame self.c.test testiga
        """
        self.c.testiruum_id = self.request.matchdict.get('testiruum_id')
        self.c.test_id = self.request.matchdict.get('test_id')
        self.c.komplekt_id = self.request.matchdict.get('komplekt_id')
        self.c.seq = self.request.matchdict.get('id')
        self.c.test = model.Test.get(self.c.test_id)

        BaseResourceController.__before__(self)

    def _perm_params(self):
        return {'obj': self.c.test}

