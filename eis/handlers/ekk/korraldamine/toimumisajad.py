from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class ToimumisajadController(BaseResourceController):
    _permission = 'korraldamine'
    _MODEL = model.Toimumisaeg
    _INDEX_TEMPLATE = 'ekk/korraldamine/otsing.mako'
    _LIST_TEMPLATE = 'ekk/korraldamine/otsing_list.mako'
    _DEFAULT_SORT = '-toimumisaeg.alates,toimumisaeg.tahised' # vaikimisi sortimine
    _SEARCH_FORM = forms.ekk.korraldamine.ToimumisajadForm
    
    def _search(self, q):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        c = self.c
        if c.alates:
            q = q.filter(model.Toimumisaeg.alates <= c.alates)
        if c.kuni:
            q = q.filter(model.Toimumisaeg.kuni >= c.kuni)
        if c.ta_tahised:
            q = q.filter(model.Toimumisaeg.tahised.ilike(c.ta_tahised))
        if c.test_id:
            q = q.filter(model.Testimiskord.test_id==c.test_id)
        if c.testsessioon_id:
            q = q.filter(model.Testimiskord.testsessioon_id==c.testsessioon_id)

        if c.testiliik:
            q = q.filter(model.Test.testiliik_kood==c.testiliik)
                         
        if c.periood:
            q = q.filter(model.Test.periood_kood==c.periood)
        if c.aine:
            q = q.filter(model.Test.aine_kood==c.aine)

        if c.vastvorm:
            q = q.filter(model.Testiosa.vastvorm_kood==c.vastvorm)
        if c.s_staatus:
            q = q.filter(model.Toimumisaeg.sooritused.any(
                model.Sooritus.staatus==c.s_staatus))

        q = self._filter_perm(q)

        if not q:
            return
        c.prepare_item = self._prepare_item        
        self.liik_piirkonnad = {}
        if c.test_id and not q.count():
            self._explain_test(c.test_id)
        return q

    def _filter_perm(self, q):
        # milliseid teste on kasutajal lubatud korraldada?
        c = self.c
        lif = []
        if c.user.has_permission('korraldamine', const.BT_INDEX, gtyyp=const.USER_TYPE_AV):
            # võib korraldada oma avaliku vaate teste
            today = date.today()
            fst = sa.and_(model.Test.testityyp==const.TESTITYYP_AVALIK,
                          model.Test.testiisikud.any(sa.and_(
                              model.Testiisik.kasutaja_id==c.user.id,
                              model.Testiisik.kehtib_alates<=today,
                              model.Testiisik.kehtib_kuni>=today))
                          )
            lif.append(fst)

        flt_ekk = [model.Test.testityyp.in_((const.TESTITYYP_EKK, const.TESTITYYP_KONS))]
        liigid = c.user.get_testiliigid(self._permission)
        if None not in liigid:
            flt_ekk.append(model.Test.testiliik_kood.in_(liigid))
        ained = c.user.get_ained(self._permission)
        if None not in ained:
            flt_ekk.append(model.Test.aine_kood.in_(ained))
        if liigid or ained:
            # kasutajal on õigus mingeid EKK teste korraldada
            lif.append(sa.and_(*flt_ekk))

        if not lif:
            return
        elif len(lif) == 1:
            q = q.filter(lif[0])
        else:
            q = q.filter(sa.or_(*lif))
        return q
    
    def _search_default(self, q):
        return self._search(q)

    def _query(self):
        q = (model.Toimumisaeg.query
             .join(model.Toimumisaeg.testimiskord)
             .join(model.Testimiskord.test)
             .join(model.Toimumisaeg.testiosa)
             .filter(model.Test.avaldamistase==const.AVALIK_EKSAM))
        return q

    def _prepare_item(self, rcd, n):
        testiosa = rcd.testiosa
        test = testiosa.test
        testiliik = test.testiliik_kood

        # leiame kasutajale lubatud piirkondade loetelu
        if testiliik in self.liik_piirkonnad:
            piirkonnad_id = self.liik_piirkonnad[testiliik]
        else:
            piirkonnad_id = self.c.user.get_kasutaja().get_piirkonnad_id(
                'korraldamine', const.BT_SHOW, testiliik=testiliik)
            self.liik_piirkonnad[testiliik] = piirkonnad_id
        qcnt = (model.SessionR.query(model.sa.func.count(model.Sooritus.id))
                .filter(model.Sooritus.toimumisaeg_id==rcd.id)
                .filter(model.Sooritus.staatus>const.S_STAATUS_REGAMATA)
                .filter(model.Sooritus.staatus!=const.S_STAATUS_VABASTATUD)
                .filter(model.Sooritus.testikoht_id==None)
                )
        # kas pole õigust kõigi piirkondade korraldamiseks?
        if None not in piirkonnad_id:
            # piirkondlik korraldaja ei või kõiki kohti vaadata, 
            # talle kuvatakse ainult nende piirkondade koolid, mis talle on lubatud
            qcnt = (qcnt.join(model.Sooritus.sooritaja)
                    .filter(model.Sooritaja.piirkond_id.in_(piirkonnad_id))
                    )
        maaramata = qcnt.scalar() or ''

        item = [test.id,
                test.nimi,
                rcd.tahised,
                rcd.millal,
                testiosa.vastvorm_nimi,
                maaramata]
        return item

    def _explain_test(self, test_id):
        "Selgitame, miks test_id ei kuvata loetelus"
        test = model.Test.get(test_id)
        if not test:
            return
        if test.avaldamistase != const.AVALIK_EKSAM:
            self.error(_("Test {id} pole testimiskorraga test").format(id=test_id))

    def _update(self, item):
        self._update_kohad(item)

    def _update_kohad(self, item):
        kohad_id = list(map(int, self.request.params.getall('koht_id')))

        for rcd in item.testikohad:
            if rcd.koht_id in kohad_id:
                kohad_id.remove(rcd.koht_id)
            else:
                rcd.remove()

        for koht_id in kohad_id:
            koht = model.Koht.get(koht_id)
            rcd = model.Testikoht(toimumisaeg=item, koht=koht, staatus=const.B_STAATUS_KEHTIV)
            item.testikohad.append(rcd)        

    def __before__(self):
        id = self.request.matchdict.get('id')
        if id:
            self.c.toimumisaeg = model.Toimumisaeg.get(id)
        
