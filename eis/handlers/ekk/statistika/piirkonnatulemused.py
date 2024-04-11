from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class PiirkonnatulemusedController(BaseResourceController):
    "Piirkondade tulemuste otsing"
    _permission = 'aruanded-prktulemused'
    _MODEL = model.Test
    _SEARCH_FORM = forms.ekk.otsingud.PiirkonnatulemusedForm
    _INDEX_TEMPLATE = 'ekk/statistika/piirkonnatulemused.otsing.mako'
    _LIST_TEMPLATE = 'ekk/statistika/piirkonnatulemused.otsing_list.mako'
    _DEFAULT_SORT = '-alates,-test_id,test_nimi'

    def _search_default(self, q):
        return self._search(q)
    
    def _search(self, q1):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        c = self.c

        q = (model.Session.query(model.Test.id.label('test_id'),
                                 model.Test.nimi.label('test_nimi'),
                                 model.Test.aine_kood,
                                 model.Testikursus.kursus_kood,
                                 model.Testimiskord.id,
                                 model.Testimiskord.tahis,
                                 model.Testimiskord.alates,
                                 model.Testimiskord.kuni)
             .join(model.Test.testimiskorrad)
             .filter(model.Testimiskord.tulemus_kinnitatud==True)              
             .filter(model.Test.testiliik_kood!=const.TESTILIIK_KOOLIPSYH)
             .outerjoin(model.Test.testikursused)
             )

        # kontrollime, et testi on minule lubatud piirkondades sooritatud
        if None not in self.lubatud_piirkonnad_id:
            q = q.filter(model.Testimiskord.sooritajad.any(
                sa.and_(
                    model.Sooritaja.kool_koht.has(
                        model.Koht.piirkond_id.in_(self.lubatud_piirkonnad_id)),
                    model.Sooritaja.staatus==const.S_STAATUS_TEHTUD))
                         )

        q = self._filter(q)
        return q
    
    def _filter(self, q):
        c = self.c
        if c.test_id:
            q = q.filter(model.Test.id==c.test_id)
        if c.alates or c.kuni or c.testsessioon_id:
            f = []
            if c.testsessioon_id:
                f.append(model.Testimiskord.testsessioon_id==c.testsessioon_id)
            if c.alates:
                f.append(model.Testimiskord.alates >= c.alates)
            if c.kuni:
                f.append(model.Testimiskord.kuni <= c.kuni)
            q = q.filter(model.Test.testimiskorrad.any(sa.and_(*f)))
        if c.klass:
            q = q.filter(model.Testimiskord.sooritajad.any(model.Sooritaja.klass==c.klass))

        return q

    def _order(self, q, sort=None):
        return q.order_by(sa.desc(sa.text('alates')))

    def __before__(self):
        self.lubatud_piirkonnad_id = self.c.user.get_kasutaja().get_piirkonnad_id('korraldamine', const.BT_SHOW)
