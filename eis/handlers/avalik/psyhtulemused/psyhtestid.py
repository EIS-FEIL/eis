from eis.lib.baseresource import *
_ = i18n._
log = logging.getLogger(__name__)

class PsyhtestidController(BaseResourceController):

    _permission = 'koolipsyh'
    _MODEL = model.Test
    _INDEX_TEMPLATE = 'avalik/psyhtulemused/psyhtestid.mako'
    _LIST_TEMPLATE = 'avalik/psyhtulemused/psyhtestid_list.mako'
    _SEARCH_FORM = forms.avalik.testid.OtsingForm 
    _actions = 'index' # võimalikud tegevused
    
    def _query(self):
        q = (model.Session.query(model.Test)
             .filter_by(staatus=const.T_STAATUS_KINNITATUD)
             .filter(model.Test.avaldamistase==const.AVALIK_LITSENTS)
             .filter(model.Test.testiliik_kood==const.TESTILIIK_KOOLIPSYH)
             )
        return q

    def _search_default(self, q):
        c = self.c
        return self._search(q)
    
    def _search(self, q):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        c = self.c
        if c.id:
            q_test = q = q.filter_by(id=c.id)
        if c.nimi:
            like_expr = '%%%s%%' % c.nimi
            q = q.filter(model.Test.nimi.like(like_expr))

        if c.id and q.count() == 0:
            other_result = q_test.count() > 0
            self._explain_test(other_result, q_test)
            q = q_test
        return q

    def _explain_test(self, other_result, q_test):
        "Selgitatakse, miks antud testi ID ei anna otsingutulemusi"
        c = self.c
        errors = []
        q = model.Session.query(model.Test).filter_by(id=c.id)
        test = q.first()
        if test:
            if other_result:
                like_expr = '%%%s%%' % c.nimi
                q = q.filter(model.Test.nimi.like(like_expr))
                if q.count() == 0:
                    errors.append(_("Testi nimetus erineb."))
            else:
                if test.staatus != const.T_STAATUS_KINNITATUD:
                    errors.append(_("Test ei ole Harnos kinnitatud."))
                if test.avaldamistase != const.AVALIK_LITSENTS:
                    errors.append(_("Test ei ole avaldatud litsentseeritud kasutajatele."))
                if test.testiliik_kood != const.TESTILIIK_KOOLIPSYH:
                    errors.append(_("Test ei ole koolipsühholoogi test."))

                if test.avaldamistase != const.AVALIK_EKSAM:
                    if c.user.has_permission('omanimekirjad', const.BT_SHOW, test=test):
                        url = self.url('test_nimekirjad',test_id=test.id, testiruum_id=0)
                        errors.append(_('Kuid seda testi võib saada kasutada <a href="{url}">töölaua kaudu</a>.').format(url=url))
                
            if errors:
                if other_result:
                    err = _("Kuvatakse test {id}, aga see ei vasta otsingutingimustele.").format(id=test.id)
                else:
                    err = _("Test {id} ei vasta otsingutingimustele.").format(id=test.id)
                msg = err + ' ' + ' '.join(errors)
                self.warning(msg)
            
