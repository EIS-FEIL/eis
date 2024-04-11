from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class ToimumisajadController(BaseResourceController):
    """Otsinguvorm hindamise menüü avamisel
    """
    _permission = 'ekk-hindamine'
    _MODEL = model.Toimumisaeg
    _INDEX_TEMPLATE = 'ekk/hindamine/otsing.mako'
    _LIST_TEMPLATE = 'ekk/hindamine/otsing_list.mako'
    _DEFAULT_SORT = '-toimumisaeg.alates,toimumisaeg.tahised' # vaikimisi sortimine
    _SEARCH_FORM = forms.ekk.hindamine.OtsingForm

    def _query(self):
        q = (model.Toimumisaeg.query
             .join(model.Toimumisaeg.testimiskord)
             .join(model.Testimiskord.test)
             .filter(model.Test.avaldamistase.in_(
                 (const.AVALIK_EKSAM, const.AVALIK_MAARATUD)))
             .join(model.Toimumisaeg.testiosa))
        return q

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
        if c.vastvorm:
            q = (q.join(model.Toimumisaeg.testiosa)
                 .filter(model.Testiosa.vastvorm_kood==c.vastvorm))
        if c.aine:
            q = q.filter(model.Test.aine_kood==c.aine)

        q = self._filter_perm(q)
    
        if c.hinnatud:
            # debug
            # mõni on hinnatud
            q = q.filter(model.Toimumisaeg.sooritused.any(
                sa.and_(model.Sooritus.staatus == const.S_STAATUS_TEHTUD,
                        model.Sooritus.hindamine_staatus==const.H_STAATUS_HINNATUD)
                ))
            
        if c.hindamata:
            # debug
            # mõni on hindamata
            q = q.filter(model.Toimumisaeg.sooritused.any(
                sa.and_(model.Sooritus.staatus == const.S_STAATUS_TEHTUD,
                        model.Sooritus.hindamine_staatus==const.H_STAATUS_HINDAMATA)
                ))
        if c.hindajad:
            q = q.filter(model.Toimumisaeg.labiviijad.any(
                model.Labiviija.kasutajagrupp_id==const.GRUPP_HINDAJA_K))

        if c.valimis:
            # debug
            q = q.filter(model.Testimiskord.sisaldab_valimit==True)
        return q

    def _filter_perm(self, q):
        # milliseid teste on kasutajal lubatud näha?
        c = self.c

        # testityybi kontrolli on vaja ainult siis, kui
        # mõlemad tyybid pole lubatud
        if not c.user.has_permission('ekk-hindamine', const.BT_INDEX, gtyyp=const.USER_TYPE_AV):
            q = q.filter(model.Test.testityyp==const.TESTITYYP_EKK)
        if not c.user.has_permission('ekk-hindamine', const.BT_INDEX, gtyyp=const.USER_TYPE_EKK):
            q = q.filter(model.Test.testityyp==const.TESTITYYP_AVALIK)

        # oma testi vaatamine (EKK või avalik)
        today = date.today()
        f_isik = model.Test.testiisikud.any(sa.and_(
            model.Testiisik.kasutaja_id==c.user.id,
            model.Testiisik.kasutajagrupp_id.in_(
                (const.GRUPP_T_VAATAJA, const.GRUPP_T_KOOSTAJA)),
            model.Testiisik.kehtib_alates<=today,
            model.Testiisik.kehtib_kuni>=today))

        lif = [f_isik]
        
        if c.user.has_permission('ekk-hindamine', const.BT_INDEX, gtyyp=const.USER_TYPE_EKK):
            # võib EKK vaate teste näha
            flt_ekk = [model.Test.testityyp==const.TESTITYYP_EKK]
            ained = c.user.get_ained(self._permission)
            if None not in ained:
                # kõik ained ei ole lubatud
                # lubatud on individuaalse õigusega või aine järgi
                if ained:
                    flt = model.sa.or_(f_isik, model.Test.aine_kood.in_(ained))
                    flt_ekk.append(flt)

            liigid = c.user.get_testiliigid(self._permission)
            if None not in liigid:
                # kõik testid ei ole lubatud
                # lubatud on individuaalse õigusega või testiliigi järgi
                if liigid:
                    flt = model.sa.or_(f_isik, model.Test.testiliik_kood.in_(liigid))
                    flt_ekk.append(flt)
            lif.append(sa.and_(*flt_ekk))
        q = q.filter(sa.or_(*lif))
        return q
    
    def _search_default(self, q):
        return self._search(q)
    
    def __before__(self):
        id = self.request.matchdict.get('id')
        if id:
            self.c.toimumisaeg = model.Toimumisaeg.get(id)
        
