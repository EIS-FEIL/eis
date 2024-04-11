# -*- coding: utf-8 -*- 

from eis.lib.baseresource import *
from eis.lib.basegrid import *
_ = i18n._
from eis.lib.block import BlockController

log = logging.getLogger(__name__)

class OtsiylesandekogudController(BaseResourceController):
    "Ylesandekogude otsing"
    _permission = 'testid'
    _MODEL = model.Ylesandekogu
    _INDEX_TEMPLATE = 'avalik/testid/otsiylesandekogud.mako'
    _LIST_TEMPLATE = 'avalik/testid/otsiylesandekogud_list.mako'
    _SHOW_TEMPLATE = 'avalik/testid/otsiylesandekogud.ylesandekogu.mako'
    _SEARCH_FORM = forms.avalik.tookogumikud.YlesandekoguOtsingForm 
    _DEFAULT_SORT = 'ylesandekogu.nimi' # vaikimisi sortimine
    _log_params_never = True # et saaks readonly ylesanded.py transaktsioonist kutsuda
    #_upath = '/tookogumik/ylesandekogud'
    _actions = 'index,show'
    
    def _query(self):
        q = (model.SessionR.query(model.Ylesandekogu)
             .filter(model.Ylesandekogu.staatus==const.YK_STAATUS_AVALIK)
             )
        # bugzilla 500 2018-09-11: kuvada ainult neid kogusid,
        # milles leidub mõni avalik ylesanne või test
        q = q.filter(sa.or_(
            model.Ylesandekogu.koguylesanded.any(
                model.Koguylesanne.ylesanne.has(
                    model.Ylesanne.staatus.in_((const.Y_STAATUS_AVALIK, const.Y_STAATUS_PEDAGOOG))
                    )),
            model.Ylesandekogu.kogutestid.any(
                model.Kogutest.test.has(
                    model.Test.staatus==const.T_STAATUS_KINNITATUD))
            ))
        return q
    
    def _search_default(self, q):
        """Otsingu tingimuste seadmine siis, kui otsing toimub 
        kohe otsinguvormi avamisel ja kasutaja pole veel saanud 
        otsingutingimusi valida.
        """
        return self._search(q)

    def _search(self, q):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        c = self.c
        self._get_opt()

        if c.aine:
            #q = q.filter(model.Ylesandekogu.aine_kood==c.aine)
            q = q.filter(sa.or_(model.Ylesandekogu.aine_kood==c.aine,
                                model.Ylesandekogu.seotud_ained.any(c.aine)))
        if c.keeletase:
            q = q.filter(model.Ylesandekogu.keeletase_kood==c.keeletase)
        if c.aste:
            aste_bit = c.opt.aste_bit(c.aste, c.aine) or 0
            q = q.filter(model.Ylesandekogu.aste_mask.op('&')(aste_bit) > 0)
            #q = q.filter(model.Ylesandekogu.peamine_aste_kood==c.aste)
        if c.klass:
            q = q.filter(model.Ylesandekogu.klass==c.klass)
        if c.term:
            term = '%' + c.term + '%'
            Aine = sa.orm.aliased(model.Klrida, name='aine')
            Teema = sa.orm.aliased(model.Klrida, name='teema')
            Alateema = sa.orm.aliased(model.Klrida, name='alateema')
            Opitulemus = sa.orm.aliased(model.Klrida, name='opitulemus')
            li = (model.Ylesandekogu.nimi.ilike(term),
                  model.Ylesandekogu.koguteemad.any(
                      sa.and_(Teema.kood==model.Koguteema.teema_kood,
                              Teema.klassifikaator_kood=='TEEMA',
                              Teema.ylem_id==Aine.id,
                              Aine.klassifikaator_kood=='AINE',
                              Aine.kood==model.Ylesandekogu.aine_kood,
                              sa.or_(
                                  Teema.nimi.ilike(term),
                                  sa.exists().where(
                                      sa.and_(Alateema.nimi.ilike(term),
                                              Alateema.klassifikaator_kood=='ALATEEMA',
                                              Alateema.ylem_id==Teema.id))
                                  )
                              )
                      ),
                  model.Ylesandekogu.koguylesanded.any(
                      sa.and_(model.Koguylesanne.ylesanne_id==model.Ylesandeaine.ylesanne_id,
                              model.Ylesandeaine.id==model.Ylopitulemus.ylesandeaine_id,
                              model.Ylopitulemus.opitulemus_klrida_id==Opitulemus.id,
                              Opitulemus.nimi.ilike(term))
                      ),
                  model.Ylesandekogu.koguylesanded.any(
                      sa.and_(model.Koguylesanne.ylesanne_id==model.Ylesanne.id,
                              sa.or_(model.Ylesanne.nimi.ilike(term),
                                     model.Ylesanne.markus.ilike(term),
                                     model.Ylesanne.marksonad.ilike(term),
                                     model.Ylesanne.trans.any(model.T_Ylesanne.marksonad.ilike(term))
                                     )
                              )
                      ),
                  model.Ylesandekogu.kogutestid.any(
                      sa.and_(model.Kogutest.test_id==model.Test.id,
                              sa.or_(model.Test.nimi.ilike(term),
                                     model.Test.markus.ilike(term))
                              )
                      )
                  )
            q = q.filter(sa.or_(*li))
        return q

    def _get_opt(self):
        "Otsingute valikväljade sisu"
        c = self.c
        q = (model.SessionR.query(model.Ylesandekogu.aine_kood).distinct()
             .filter(model.Ylesandekogu.staatus==const.YK_STAATUS_AVALIK)
             )
        koguained = [kood for kood, in q.all()]
        c.opt_aine_yk = [r for r in c.opt.klread_kood('AINE') if r[0] in koguained]

    def _show(self, kogu):
        c = self.c
        data = []
        items = []
        for ky in kogu.koguylesanded:
            ylesanne = ky.ylesanne
            if c.user.has_permission('lahendamine', const.BT_SHOW, obj=ylesanne):            
                items.append(ylesanne)
        c.itemdata = [('Ülesanded', items)]

    def _get_current_upath(self):
        # anname upath ette, et leitaks parameetrid ka siis,
        # kui request on tehtud Ylesanded kontrollerile
        return self.h.url_current()

    def __before__(self):
        """Väärtustame self.c.test testiga
        """
        self.c.testiruum_id = self.request.matchdict.get('testiruum_id')
        self.c.test_id = self.request.matchdict.get('test_id')
        #self.c.komplekt_id = self.request.matchdict.get('komplekt_id')
        #self.c.seq = self.request.matchdict.get('id')
        self.c.test = model.Test.get(self.c.test_id)
        BaseResourceController.__before__(self)
        
