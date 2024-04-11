from eis.lib.baseresource import *
_ = i18n._
from eis.lib.block import BlockController

log = logging.getLogger(__name__)

class YlesandekogudController(BaseResourceController):
    "Ylesandekogude otsing"
    _permission = 'tookogumikud'

    _MODEL = model.Ylesandekogu
    _INDEX_TEMPLATE = 'avalik/tookogumikud/tookogumik.ylesandekogud.mako'
    _LIST_TEMPLATE = 'avalik/tookogumikud/tookogumik.ylesandekogud_list.mako'
    _SHOW_TEMPLATE = 'avalik/tookogumikud/tookogumik.ylesandekogu.mako'
    _SEARCH_FORM = forms.avalik.tookogumikud.YlesandekoguOtsingForm 
    _DEFAULT_SORT = 'ylesandekogu.nimi' # vaikimisi sortimine
    _upath = '/tookogumik/ylesandekogud'
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
        if c.aine:
            q = q.filter(sa.or_(model.Ylesandekogu.aine_kood==c.aine,
                                model.Ylesandekogu.seotud_ained.any(c.aine)))
        if c.keeletase:
            q = q.filter(model.Ylesandekogu.keeletase_kood==c.keeletase)
        if c.aste:
            aste_bit = c.opt.aste_bit(c.aste, c.aine) or 0
            q = q.filter(model.Ylesandekogu.aste_mask.op('&')(aste_bit) > 0)
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
        #model.log_query(q)
        return q

    def _showlist(self):
        template = self._LIST_TEMPLATE
        return self.render_to_response(template)

    def _show(self, kogu):
        c = self.c
        data = []
        items = []
        q = (model.SessionR.query(model.Ylesanne, model.Koguylesanne.id)
             .join(model.Ylesanne.koguylesanded)
             .filter(model.Koguylesanne.ylesandekogu_id==kogu.id)
             .order_by(model.Ylesanne.nimi))
        for ylesanne, ky_id in q.all():
            if ylesanne.staatus in (const.Y_STAATUS_AVALIK, const.Y_STAATUS_PEDAGOOG) and \
                   c.user.has_permission('lahendamine', const.BT_SHOW, obj=ylesanne):            
                uniqid = f'y{ylesanne.id}'
                item = ('yky-%d' % ky_id, uniqid, ylesanne.id, ylesanne.nimi, ylesanne.staatus_nimi)
                items.append(item)
        if items:
            group_id = 'yky_%d' % kogu.id
            data.append(('Ülesanded', items, group_id))
            
        items = []
        q = (model.SessionR.query(model.Test, model.Kogutest.id)
             .join(model.Test.kogutestid)
             .filter(model.Kogutest.ylesandekogu_id==kogu.id)
             .filter(model.Test.staatus==const.T_STAATUS_KINNITATUD)
             .order_by(model.Test.nimi))
        for test, kt_id in q.all():
            # kiri 2018-09-10 - koostamisel testi ei kuvata
            if c.user.has_permission('testid', const.BT_SHOW, obj=test):
                uniqid = f't{test.id}'
                item = ('ykt-%d' % kt_id, uniqid, test.id, test.nimi, None)
                items.append(item)
        if items:
            group_id = 'ykt_%d' % kogu.id            
            data.append(('Testid', items, group_id))
            
        c.itemdata = data
        c.jrk_args = self.url('tookogumikud', ykyk_id=kogu.id)
        
