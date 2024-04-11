from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class TestimiskorradController(BaseResourceController):
    """Registreerimisnimekirjad otsimine.
       Õpetajad saavad vaadata oma kooli registreerimisnimekirju ja kui on registreerimisaeg,
       siis sooritajaid registreerida.
    """
    _permission = 'nimekirjad'
    _MODEL = model.Testimiskord
    _INDEX_TEMPLATE = 'avalik/nimekirjad/testimiskorrad.mako'
    _LIST_TEMPLATE = 'avalik/nimekirjad/testimiskorrad_list.mako'
    _DEFAULT_SORT = 'testimiskord.id' # vaikimisi sortimine
    _SEARCH_FORM = forms.avalik.testid.NimekirjadForm 
    _actions = 'index,show'
    
    def _query(self):
        q = (model.Testimiskord.query
             .filter(model.Testimiskord.osalemise_naitamine==True)
             .join(model.Testimiskord.test)
             )
        return q

    def _search(self, q):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.

        Milliste testide seast otsida?
        Otsitakse testimiskordi testidele, mis on kinnitatud
        ja mille avaldamistasemeks on testimiskorraga test.
        Testimiskorrale peab olema määratud registreerimise ajavahemik.
        """
        c = self.c
        c.get_reg_arv = self._get_reg_arv

        # testile ligipääsuõiguse olemasolu filter
        q = (q.filter(model.Test.staatus==const.T_STAATUS_KINNITATUD)
             .filter(model.Test.avaldamistase==const.AVALIK_EKSAM)
             )

        if c.test_id:
            q_test = q = q.filter(model.Test.id==c.test_id)

        q = self._search_reg(q)

        # kasutaja antud otsinguparameetrid
        if c.nimi:
            like_expr = '%%%s%%' % c.nimi
            q = q.filter(model.Test.nimi.like(like_expr))
        if c.aine:
            q = q.filter(model.Test.aine_kood==c.aine)
        if c.testiliik:
            q = q.filter(model.Test.testiliik_kood==c.testiliik)

        if c.test_id and q.count() == 0:
            # kui testi ID on antud, aga tulemusi pole, siis selgitatakse,
            # miks see test ei vasta tingimustele
            other_result = q_test.count() > 0
            self._explain_test(other_result)
            # kuvatakse tulemused ainult testi ID järgi, muid otsingutingimusi arvestamata
            q = q_test
        return q

    def _search_reg(self, q):
        "Registreerimisviisi ja -vahemiku kontroll"
        c = self.c
        reg_alates = None
        reg_kuni = None

        # kontroll, et registreerimine oleks lubatud
        if c.regviis == const.REGVIIS_KOOL_EIS:
            if c.user.koht_id:
                q = q.filter(sa.or_(
                    model.Testimiskord.reg_kool_eis==True,
                    sa.and_(model.Testimiskord.reg_kool_valitud==True,
                            sa.exists().where(
                                sa.and_(model.Regkoht_kord.testimiskord_id==model.Testimiskord.id,
                                        model.Regkoht_kord.koht_id==c.user.koht_id)
                                )
                            )
                    ))
            else:
                q = q.filter(model.Testimiskord.reg_kool_eis==True)
            reg_alates = model.Testimiskord.reg_kool_alates
            reg_kuni = model.Testimiskord.reg_kool_kuni
        elif c.regviis == const.REGVIIS_EKK:
            q = q.filter(model.Testimiskord.reg_ekk==True)
            # reg aja järgi otsimist ei tehta
        elif c.regviis == const.REGVIIS_SOORITAJA:
            q = q.filter(model.Testimiskord.reg_sooritaja==True)
            reg_alates = model.Testimiskord.reg_sooritaja_alates
            reg_kuni = model.Testimiskord.reg_sooritaja_kuni
        elif c.regviis == const.REGVIIS_XTEE:
            q = q.filter(model.Testimiskord.reg_xtee==True)
            reg_alates = model.Testimiskord.reg_xtee_alates
            reg_kuni = model.Testimiskord.reg_xtee_kuni            

        if c.reg_aeg_alates and reg_kuni:
            q = q.filter(reg_kuni >= c.reg_aeg_alates)
        if c.reg_aeg_kuni and reg_alates:
            q = q.filter(reg_alates <= c.reg_aeg_kuni)            
        if c.aktiiv != 'f' and reg_kuni:
            q = q.filter(reg_kuni >= date.today())
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

        q = model.SessionR.query(model.Test).filter_by(id=c.test_id)
        test = q.first()
        if test:
            # test on olemas, aga ei vasta filtrile
            if test.staatus != const.T_STAATUS_KINNITATUD:
                errors.append(_("Test ei ole Harnos kinnitatud."))
            if test.avaldamistase != const.AVALIK_EKSAM:
                if c.user.has_permission('omanimekirjad', const.BT_SHOW, test=test):
                    url = self.url('test', id=test.id)
                    #url = self.url('test_nimekirjad',test_id=test.id, testiruum_id=0)
                    #url = self.url('tookogumikud', test_id=test.id)
                    errors.append(_('See pole tsentraalselt korraldatud test, aga seda saab kasutada <a href="{url}">töölaua kaudu</a>.').format(url=url))
                else:
                    errors.append(_("See pole tsentraalselt korraldatud test.").format(id=test.id))
            else:
                q1 = q.join(model.Test.testimiskorrad)
                q1 = self._search_reg(q1)
                if q1.count() == 0:
                    errors.append(_("Testile ei saa antud ajal ja/või viisil registreerida."))
            if not errors:
                # test on kättesaadav, aga ei vasta otsingutingimustele
                ferrors = []
                if c.nimi:
                    like_expr = '%%%s%%' % c.nimi
                    q = (model.SessionR.query(model.Test)
                         .filter_by(id=test.id)
                         .filter(model.Test.nimi.like(like_expr)))
                    if q.count() == 0:
                        ferrors.append(_("nimetus"))
                if c.aine:
                    if test.aine_kood != c.aine:
                        ferrors.append(_("õppeaine"))
                if c.testiliik:
                    if test.testiliik_kood != c.testiliik:
                        ferrors.append(_("liik"))
                if ferrors:
                    errors.append(_("Testil on erinev {omadused}.").format(omadused=join_ja(ferrors)))

            if errors:
                if other_result:
                    err = _("Kuvatakse test {id}, aga see ei vasta otsingutingimustele.").format(id=test.id)
                else:
                    err = _("Test {id} ei vasta otsingutingimustele.").format(id=test.id)
                msg = err + ' ' + ' '.join(errors)
                self.warning(msg)
                
    def _search_default(self, q):
        """Otsingu tingimuste seadmine siis, kui otsing toimub 
        kohe otsinguvormi avamisel ja kasutaja pole veel saanud 
        otsingutingimusi valida.
        Kui soovitakse, et sellist vaikimisi otsingut ei tehtaks,
        siis tuleb tagastada None.
        """
        self.c.reg_aeg_alates = self.c.reg_aeg_kuni = date.today()
        self.c.regviis = const.REGVIIS_KOOL_EIS
        return self._search(q)

    def _edit(self, item):
        self.c.is_edit = item._has_permission_reg('nimekirjad', const.BT_UPDATE, self.c.user)

    def show(self):
        # valimi teates koolile antav URL oma õpilaste regamiseks, suuname edasi
        url = self.url('nimekirjad_testimiskord_korrasooritajad',
                       testimiskord_id=self.request.matchdict.get('id'))
        raise HTTPFound(location=url)
        
    def _get_reg_arv(self, tkord_id):
        c = self.c
        q = (model.SessionR.query(sa.func.count(model.Sooritaja.id))
             .filter(model.Sooritaja.testimiskord_id==tkord_id)
             .filter(model.Sooritaja.kool_koht_id==c.user.koht_id)
             .filter(model.Sooritaja.staatus>=const.S_STAATUS_REGATUD)
             )
        return q.scalar()

    def _perm_params(self):
        tkord_id = self.request.matchdict.get('id')
        if tkord_id:
            return {'obj':model.Testimiskord.get(tkord_id)}

