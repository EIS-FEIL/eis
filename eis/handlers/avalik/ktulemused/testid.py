from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class TestidController(BaseResourceController):
    "Testide loetelu"
    _permission = 'avalikadmin,testiadmin,aineopetaja'
    _MODEL = model.Test
    _SEARCH_FORM = forms.avalik.admin.TestitulemusedForm
    _INDEX_TEMPLATE = 'avalik/ktulemused/otsing.mako'
    _LIST_TEMPLATE = 'avalik/ktulemused/otsing_list.mako'
    _DEFAULT_SORT = '-alates,-test_id,test_nimi'    
    _actions = 'index,show'
    
    def _search_default(self, q):
        return self._search(q)
    
    def _search(self, q1):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        c = self.c
        if not c.user.koht_id:
            return None

        f_t = f_a = None
        if c.user.on_testiadmin:
            # kasutaja peab olema olnud sama testi administraator samas koolis
            # ja tulemused peavad olema testiadminile lubatud
            Toimumisaeg2 = sa.orm.aliased(model.Toimumisaeg)
            f_t = sa.and_(model.Testimiskord.tulemus_admin==True,
                          sa.exists().where(sa.and_(model.Labiviija.kasutaja_id==c.user.id,
                                                    model.Labiviija.kasutajagrupp_id==const.GRUPP_T_ADMIN,
                                                    model.Labiviija.testikoht_id==model.Testikoht.id,
                                                    model.Testikoht.koht_id==c.user.koht_id,
                                                    model.Labiviija.toimumisaeg_id==Toimumisaeg2.id,
                                                    Toimumisaeg2.testimiskord_id==model.Testimiskord.id)))
        if c.user.on_avalikadmin:
            # või on kasutaja selle kooli soorituskoha administraator
            # ja tulemused on soorituskoha administraatorile lubatud
            f_a =  model.Testimiskord.tulemus_koolile==True
        else:
            # või on kasutaja mõne sooritaja aineõpetaja
            # ja tulemused on koolile lubatud            
            f_a = sa.and_(model.Testimiskord.tulemus_koolile==True,
                          model.Test.testiliik_kood!=const.TESTILIIK_SISSE,
                          model.Testimiskord.sooritajad.any(
                              sa.and_(model.Sooritaja.kool_koht_id==c.user.koht_id,
                                      model.Sooritaja.testiopetajad.any(
                                          model.Testiopetaja.opetaja_kasutaja_id==c.user.id)))
                          )


        # testi kaupa
        q = model.Session.query(model.Test.id.label('test_id'),
                                model.Test.nimi.label('test_nimi'),
                                model.Test.aine_kood,
                                model.Testikursus.kursus_kood,
                                model.Testimiskord.id,
                                model.Testimiskord.tahis,
                                model.Testimiskord.alates,
                                model.Testimiskord.kuni)

        q2 = (q.join(model.Test.testimiskorrad)
              .filter(model.Testimiskord.osalemise_naitamine==True)
              .filter(model.Testimiskord.koondtulemus_avaldet==True)              
              .filter(model.Test.testiliik_kood!=const.TESTILIIK_KOOLIPSYH)
              .outerjoin(model.Test.testikursused)
              )

        if f_t is not None and f_a is not None:
            q2 = q2.filter(sa.or_(f_t, f_a))
        elif f_t is not None:
            q2 = q2.filter(f_t)
        elif f_a is not None:
            q2 = q2.filter(f_a)            

        q = self._filter(q2)
        #model.log_query(q)
        return q
    
    def _filter(self, q):
        c = self.c
        if c.test_id:
            q_test = q = q.filter(model.Test.id==c.test_id)

        # oma kooli õpilane või on antud kooli sisseastumistest 
        fkool = sa.or_(sa.and_(model.Test.testiliik_kood!=const.TESTILIIK_SISSE,
                               model.Sooritaja.kool_koht_id==c.user.koht_id),
                       sa.and_(model.Test.testiliik_kood==const.TESTILIIK_SISSE,
                               model.Sooritaja.kandideerimiskohad.any(
                                   model.Kandideerimiskoht.koht_id==c.user.koht_id))
                       )
        if c.klass:
            q = q.filter(model.Testimiskord.sooritajad.any(
                sa.and_(fkool, model.Sooritaja.klass==c.klass)))
        else:
            q = q.filter(model.Testimiskord.sooritajad.any(fkool))

        if c.testsessioon_id:
            q = q.filter(model.Testimiskord.testsessioon_id==c.testsessioon_id)
        if c.alates:
            q = q.filter(model.Testimiskord.kuni >= c.alates)
        if c.kuni:
            q = q.filter(model.Testimiskord.alates <= c.kuni)

        if c.test_id and q.count() == 0:
            # kui testi ID on antud, aga tulemusi pole, siis selgitatakse,
            # miks see test ei vasta tingimustele
            other_result = q_test.count() > 0
            self._explain_test(other_result)
            # kuvatakse tulemused ainult testi ID järgi, muid otsingutingimusi arvestamata
            q = q_test
        return q

    def _explain_test(self, other_result):
        c = self.c
        errors = []

        def join_ja(li):
            if len(li) > 1:
                return ', '.join(li[:-1]) + _(" ja ") + li[-1]
            elif len(li) == 1:
                return li[-1]
            else:
                return ''

        def oma_testiruum(test):
            # kas leidub testimiskorrata nimekirju, mida võin vaadata
            q = (model.Session.query(model.Testiruum.id)
                 .join(model.Testiruum.nimekiri)
                 .filter(model.Nimekiri.test_id==test.id)
                 .filter(model.Nimekiri.testimiskord_id==None))
            if c.user.on_pedagoog:
                q = q.filter(model.Nimekiri.esitaja_koht_id==c.user.koht_id)
            if test.testiliik_kood == const.TESTILIIK_KOOLIPSYH:
                # koolipsühholoogi testi kasutaja peab olema nimekirja omanik
                q = q.filter_by(esitaja_kasutaja_id=c.user.id)
            elif c.user.koht_id and c.user.has_permission('klass', const.BT_SHOW, obj=c.user.koht):
                # muidu, kui kasutaja on pedagoog, siis võib ta kõiki oma kooli nimekirju näha, mis on pedag nähtavad
                q = (q.filter(model.sa.or_(model.Nimekiri.esitaja_kasutaja_id==c.user.id,
                                           model.sa.and_(model.Nimekiri.esitaja_koht_id==c.user.koht_id,
                                                         model.Nimekiri.pedag_nahtav==True))
                              ))
            else:
                # muidu peab olema nimekirja omanik
                q = q.filter_by(esitaja_kasutaja_id=c.user.id)
            q = q.order_by(sa.desc(model.Testiruum.id))
            r = q.first()
            if r:
                return r[0]

        def check_filter(q):
            # otsingutingimuste kontroll
            ferrors = []
            if c.testsessioon_id:
                q1 = q.filter(model.Testimiskord.testsessioon_id==c.testsessioon_id)
                if q1.count() == 0:
                    ferrors.append(_("testsessioon"))

            if c.alates or c.kuni:
                q1 = q
                if c.alates:
                    q1 = q1.filter(model.Testimiskord.kuni >= c.alates)
                if c.kuni:
                    q1 = q1.filter(model.Testimiskord.alates <= c.kuni)
                if q1.count() == 0:
                    ferrors.append(_("toimumise algusaeg"))

            if c.klass:
                # oma kooli õpilane või on antud kooli sisseastumistest 
                fkool = sa.or_(sa.and_(model.Test.testiliik_kood!=const.TESTILIIK_SISSE,
                                       model.Sooritaja.kool_koht_id==c.user.koht_id),
                               sa.and_(model.Test.testiliik_kood==const.TESTILIIK_SISSE,
                                       model.Sooritaja.kandideerimiskohad.any(
                                         model.Kandideerimiskoht.koht_id==c.user.koht_id))
                        )
                q1 = q.filter(model.Testimiskord.sooritajad.any(
                    sa.and_(fkool, model.Sooritaja.klass==c.klass)
                ))
                if q1.count() == 0:
                    ferrors.append(_("klass"))
            if ferrors:
                return _("Testil on erinev {omadused}.").format(omadused=join_ja(ferrors))
            
        q = model.Session.query(model.Test).filter_by(id=c.test_id)
        test = q.first()
        if test:
            # test on olemas
            q = q.join(model.Test.testimiskorrad)
            if q.count() == 0:
                errors.append(_("Testi ei ole tsentraalselt korraldatud."))
            else:
                q = (q.filter(model.Testimiskord.osalemise_naitamine==True)
                     .filter(model.Testimiskord.koondtulemus_avaldet==True)
                     .filter(model.Test.testiliik_kood!=const.TESTILIIK_KOOLIPSYH))
                if q.count() == 0:
                    errors.append(_("Testi tulemusi pole avaldatud."))
            if not errors:
                q = q.filter(model.Testimiskord.sooritajad.any(
                     model.Sooritaja.kool_koht_id==c.user.koht_id))
                if q.count() == 0:
                    errors.append(_("Testimiskorral ei ole meie kooli õpilasi osalenud."))
                elif other_result:
                    # test on kättesaadav, aga ei vasta otsingutingimustele
                    err = check_filter(q)
                    if err:
                        errors.append(err)
                else:
                    errors.append(_("Testimiskorra tulemused pole avalikud."))
                    
            if test.avaldamistase != const.AVALIK_EKSAM:
                testiruum_id = oma_testiruum(test)
                if testiruum_id:
                    url = self.url('test_nimekirjad',test_id=test.id, testiruum_id=testiruum_id)
                    errors.append(_('Ise korraldatud testimise tulemusi saab vaadata <a href="{url}">töölaua kaudu</a>.').format(url=url))
                    
            if errors:
                if other_result:
                    err = _("Kuvatakse test {id}, aga see ei vasta otsingutingimustele.").format(id=test.id)
                else:
                    err = _("Test {id} ei vasta otsingutingimustele.").format(id=test.id)
                msg = err + ' ' + ' '.join(errors)
                self.warning(msg)

    def show(self):
        """Koolile saadetud teade testimiskorra tulemuste
        avaldamise kohta sisaldab linki testi ID-ga,
        mille avamisel suunatakse kasutaja otsinguvormile
        """
        test_id = self.request.matchdict.get('id')
        return self._redirect('index', test_id=test_id)
    
