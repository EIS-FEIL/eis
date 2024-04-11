from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class TestiotsingController(BaseResourceController):
    "Testide otsing"
    _permission = 'tookogumikud'

    _MODEL = model.Test
    _INDEX_TEMPLATE = 'avalik/tookogumikud/tookogumik.testiotsing.mako'
    _LIST_TEMPLATE = 'avalik/tookogumikud/tookogumik.testiotsing_list.mako'
    _SEARCH_FORM = forms.avalik.tookogumikud.TestiOtsingForm 
    _DEFAULT_SORT = 'test.nimi' # vaikimisi sortimine
    _upath = '/tookogumik/testiotsing'
    _actions = 'index'
    
    def _query(self):
        q = model.Test.query.filter_by(staatus=const.T_STAATUS_KINNITATUD)
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
        q = self._filter_perm(q)

        if c.test_id:
            q = q.filter(model.Test.id==c.test_id)
            q_test = q
        if c.testiliik:
            if c.testiliik == const.TESTILIIK_AVALIK:
                q = q.filter(model.Test.testiliik_kood==None)
            else:
                q = q.filter(model.Test.testiliik_kood==c.testiliik)

        if c.aine:
            q = q.filter(model.Test.aine_kood==c.aine)
            
        if c.aste:
            aste_bit = c.opt.aste_bit(c.aste) or 0
            q = q.filter(model.Test.aste_mask.op('&')(aste_bit) > 0)

        if c.test_id and not q.count():
            # kui testi ID on antud, aga tulemusi pole, siis selgitatakse,
            # miks see test ei vasta tingimustele
            other_result = q_test.count() > 0
            self._explain_test(other_result)
            q = q_test
        return q

    def _filter_perm(self, q):
        "Kontrollitakse testile ligipääsu õigust"
        
        def _filter_avalik_omanik():
            # avalikud testid, kus kasutaja on omanik või töövaataja
            return model.Test.testiisikud.any(model.Testiisik.kasutaja_id==self.c.user.id)
        
        def _filter_ekk_maaratud():
            # Innove testid, mis on kasutajale määratud
            dt = date.today()                    
            f = sa.and_(model.Test.avaldamistase==const.AVALIK_MAARATUD,
                        sa.or_(model.Test.avalik_alates <= dt, 
                               model.Test.avalik_alates == None),
                        sa.or_(model.Test.avalik_kuni >= dt,
                               model.Test.avalik_kuni == None),
                        model.Test.testiisikud.any(model.Testiisik.kasutaja_id==self.c.user.id)
                        )
            return f

        def _filter_ekk_pedagoog():
            # Innove testid, mis on pedagoogidele määratud
            dt = date.today()
            return  sa.and_(model.Test.avaldamistase==const.AVALIK_OPETAJAD,
                            sa.or_(model.Test.avalik_alates <= dt, 
                                   model.Test.avalik_alates == None),
                            sa.or_(model.Test.avalik_kuni >= dt,
                                   model.Test.avalik_kuni == None))

        def _filter_ekk_maaratud_pedagoog():
            # Innove testid, mis on kasutajale määratud või kõigile pedagoogidele
            dt = date.today()                    
            f = sa.and_(model.Test.avaldamistase.in_((const.AVALIK_MAARATUD, const.AVALIK_OPETAJAD)),
                        sa.or_(model.Test.avalik_alates <= dt, 
                               model.Test.avalik_alates == None),
                        sa.or_(model.Test.avalik_kuni >= dt,
                               model.Test.avalik_kuni == None),
                        sa.or_(model.Test.avaldamistase==const.AVALIK_OPETAJAD,
                               model.Test.testiisikud.any(model.Testiisik.kasutaja_id==self.c.user.id))
                        )
            return f
          
        def _filter_ekk_koigile():
            # Innove testid, mis on kõigile vabaks kasutamiseks 
            dt = date.today()
            return sa.and_(model.Test.avaldamistase==const.AVALIK_SOORITAJAD,
                           sa.or_(model.Test.avalik_alates <= dt, 
                                  model.Test.avalik_alates == None),
                           sa.or_(model.Test.avalik_kuni >= dt,
                                  model.Test.avalik_kuni == None))

        def _filter_ekk_psyh():
            return sa.and_(model.Test.avaldamistase==const.AVALIK_LITSENTS,
                           model.Test.testiliik_kood==const.TESTILIIK_KOOLIPSYH)

        def _filter_ekk_logopeed():
            return sa.and_(model.Test.avaldamistase==const.AVALIK_LITSENTS,
                           model.Test.testiliik_kood==const.TESTILIIK_LOGOPEED)

        f_avalik = _filter_avalik_omanik()
        f_ekk = None

        # oma teste näen alati
        if not self.c.minu:
            if self.c.user.on_pedagoog:
                f_ekk = sa.or_(_filter_ekk_koigile(),
                               _filter_ekk_maaratud_pedagoog())
            else:
                f_ekk = sa.or_(_filter_ekk_koigile(),
                               _filter_ekk_maaratud())
            if self.c.user.on_koolipsyh:
                f_ekk = sa.or_(f_ekk, _filter_ekk_psyh())
            if self.c.user.on_logopeed:
                f_ekk = sa.or_(f_ekk, _filter_ekk_logopeed())                

        if f_avalik is not None:
            f_avalik = sa.and_(f_avalik, model.Test.testityyp.in_((const.TESTITYYP_AVALIK, const.TESTITYYP_TOO)))
        if f_ekk is not None:
            f_ekk = sa.and_(f_ekk, model.Test.testityyp==const.TESTITYYP_EKK)

        if f_avalik is not None and f_ekk is not None:
            q = q.filter(sa.or_(f_avalik, f_ekk))
        elif f_avalik is not None:
            q = q.filter(f_avalik)
        elif f_ekk is not None:
            q = q.filter(f_ekk)
        else:
            return
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

        q = model.Session.query(model.Test).filter_by(id=c.test_id)
        test = q.first()
        if test:
            # test on olemas, aga ei vasta filtrile
            if test.staatus != const.T_STAATUS_KINNITATUD:
                if test.staatus == const.T_STAATUS_ARHIIV:
                    errors.append(_("Test on arhiveeritud."))
                else:
                    errors.append(_("Test ei ole kinnitatud."))
            elif test.avaldamistase == const.AVALIK_EKSAM:
                url = self.url('nimekirjad_testimiskorrad', test_id=test.id)
                errors.append(_('See on <a href="{url}">tsentraalselt korraldatud test</a>.').format(url=url))
            else:
                q1 = self._filter_perm(q)
                if q1.count() == 0:
                    errors.append(_("Sellele testile ei ole ligipääsuõigust."))

            if errors:
                err0 = _("Test {id} ei ole töölaua kaudu kasutamiseks.").format(id=test.id)
            else:
                ferrors = []
                if c.testiliik == const.TESTILIIK_AVALIK and test.testiliik_kood:
                    ferrors.append("liik")
                elif c.testiliik and c.testiliik != test.testiliik_kood:
                    ferrors.append("liik")
                if c.aine and c.aine != test.aine_kood:
                    ferrors.append(_("õppeaine"))
                if c.aste:
                    aste_bit = c.opt.aste_bit(c.aste) or 0
                    if (test.aste_mask or 0) & aste_bit == 0:
                        ferrors.append("kooliaste")
                if ferrors:
                    errors.append(_("Testil on erinev {omadused}.").format(omadused=join_ja(ferrors)))
                if other_result:
                    err0 = _("Kuvatakse test {id}, aga see ei vasta otsingutingimustele.").format(id=test.id)
                else:
                    err0 = _("Test {id} ei vasta otsingutingimustele.").format(id=test.id)
            if errors:
                msg = err0 + ' ' + ' '.join(errors)
                self.warning(msg)
            
    def _showlist(self):
        template = self._LIST_TEMPLATE
        return self.render_to_response(template)

