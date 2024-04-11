# -*- coding: utf-8 -*- 

from eis.lib.baseresource import *
from eis.lib.basegrid import *
from eis.lib.block import BlockController
_ = i18n._

log = logging.getLogger(__name__)

class KonsultatsioonidController(BaseResourceController):
    """Konsultatsioonide otsing ning üldandmed
    """
    _permission = 'konsultatsioonid'
    _MODEL = model.Test
    _INDEX_TEMPLATE = 'ekk/konsultatsioonid/otsing.mako'
    _EDIT_TEMPLATE = 'ekk/konsultatsioonid/yldandmed.mako' 
    _LIST_TEMPLATE = 'ekk/konsultatsioonid/otsing_list.mako'
    _SEARCH_FORM = forms.ekk.konsultatsioonid.OtsingForm 
    _ITEM_FORM = forms.ekk.konsultatsioonid.YldandmedForm
    _DEFAULT_SORT = '-test.id' # vaikimisi sortimine
    
    def _search(self, q):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        if self.c.id:
            q = q.filter_by(id=self.c.id)
        if self.c.nimi:
            like_expr = '%%%s%%' % self.c.nimi            
            q = q.filter(model.Test.nimi.ilike(like_expr))
        if self.c.testiliik:
            q = q.filter_by(testiliik_kood=self.c.testiliik)
        else:
            liigid = self.c.user.get_testiliigid(self._permission)
            if None not in liigid:
                q = q.filter(model.Test.testiliik_kood.in_(liigid))            
        if self.c.periood:
            q = q.filter_by(periood_kood=self.c.periood)
        if self.c.aine:
            q = q.filter_by(aine_kood=self.c.aine)
        else:
            ained = self.c.user.get_ained(self._permission)
            if None not in ained:
                q = q.filter(model.Test.aine_kood.in_(ained))

        if self.c.koostaja:
            like_expr = '%%%s%%' % self.c.koostaja
            q = q.join((model.Kasutaja, 
                        model.Kasutaja.isikukood==model.Test.creator)).\
                filter(model.Kasutaja.nimi.ilike(like_expr))

        return q

    def _query(self):
        return model.Test.query.filter_by(testityyp=const.TESTITYYP_KONS)

    def _search_default(self, q):
        """Otsingu tingimuste seadmine siis, kui otsing toimub 
        kohe otsinguvormi avamisel ja kasutaja pole veel saanud 
        otsingutingimusi valida.
        """
        return None

    def _create(self, **kw):
        item = BaseResourceController._create(self, testityyp=const.TESTITYYP_KONS)
        item.avaldamistase = const.AVALIK_EKSAM
        item.logi('Loomine', None, None, const.LOG_LEVEL_GRANT)

        # testi looja saab kohe testiga seotud isikuks koostaja rollis
        item.add_testiisik(const.GRUPP_T_KOOSTAJA)

        return item

    def _update(self, item, lang=None):
        BaseResourceController._update(self, item, lang)

        # salvestame keeleoskuse taseme
        keeletase_kood = self.form.data.get('keeletase_kood')
        if keeletase_kood:
            testitase = item.give_testitase(1)
            testitase.pallid = None
            testitase.aine_kood = item.aine_kood
            testitase.keeletase_kood = keeletase_kood
        else:
            for r in item.testitasemed:
                r.delete()
        
    def _update_kopeeri(self, id):            
        """Testi kopeerimine
        """
        item = model.Test.get(id)
        cp = item.copy()
        cp.staatus = const.T_STAATUS_KINNITATUD

        cp.logi('Loomine koopiana', None, None, const.LOG_LEVEL_GRANT)
        # testi looja saab kohe testiga seotud isikuks koostaja rollis
        cp.add_testiisik(const.GRUPP_T_OMANIK)
        model.Session.commit()
        self.success(_('Testist on tehtud koopia'))
        return HTTPFound(location=self.url('konsultatsioon', id=cp.id))

    def _delete(self, item):
        if item:
            rc = True
            for tk in item.testimiskorrad:
                self.error(_('Konsultatsiooni ei saa kustutada, sest sellel on olemas toimumiskordi'))              
                rc = False
                break
            if not rc:
                return self._redirect('show', item.id)

            item.delete()
            model.Session.commit()
            self.success(_('Andmed on kustutatud!'))

    def _perm_params(self):
        test_id = self.request.matchdict.get('id')
        if test_id:
            return {'obj':model.Test.get(test_id)}

