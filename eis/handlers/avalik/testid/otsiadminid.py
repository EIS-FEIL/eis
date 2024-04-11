# -*- coding: utf-8 -*- 

from eis.lib.baseresource import *

log = logging.getLogger(__name__)
_ = i18n._
class OtsiadminidController(BaseResourceController):
    """Korraldajad
    """
    _permission = 'testid'
    _MODEL = model.Labiviija
    _INDEX_TEMPLATE = 'avalik/testid/nimekiri.otsiadminid.mako'
    _actions = 'index,create,delete' # võimalikud tegevused
    
    def _index_d(self):
        self.c.test_id = self.c.test.id
        self.c.grupp_id = const.GRUPP_T_ADMIN
        if 'isikukood' in self.request.params:
            # kasutaja on vajutanud nupule Otsi
            # (akna avamisel automaatselt ei otsita)
            q = self._query()
            if not self.form:
                if self.request.params:
                    self.form = Form(self.request, schema=self._SEARCH_FORM)
                    if not self.form.validate():
                        return Response(self.form.render(self._INDEX_TEMPLATE, extra_info=self.response_dict))

                    self._copy_search_params(self.form.data)
                    q = self._search(q)

            if q:
                q = self._order(q)
                if q.count() == 0 and self.c.isikukood:
                    # otsime lisaks RRist
                    error, data = xtee.rr_pohiandmed(self, self.c.isikukood)
                    if error:
                        self.error(error)
                    if data:
                        self.c.items = [NewItem(eesnimi=data['eesnimi'], 
                                                perenimi=data['perenimi'], 
                                                isikukood=self.c.isikukood)]
                else:
                    self.c.items = self._paginate(q)

        return self.response_dict

    def _query(self):
        return model.Kasutaja.query

    def _search(self, q):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        if self.c.isikukood:
            q = q.filter_by(isikukood=self.c.isikukood)
        if self.c.eesnimi:
            #like_expr = '%%%s%%' % self.c.eesnimi
            like_expr = self.c.eesnimi
            q = q.filter(model.Kasutaja.eesnimi.ilike(like_expr))
        if self.c.perenimi:
            #like_expr = '%%%s%%' % self.c.perenimi
            like_expr = self.c.perenimi
            q = q.filter(model.Kasutaja.perenimi.ilike(like_expr))

        if not self.c.isikukood and not self.c.perenimi:
            self.error(_('Isikukood või perekonnanimi on vaja ette anda'))
            return None
        return q

    def _create(self):            
        """Isiku lisamine ülesandega seotuks
        """
        c = self.c
        grupp_id = const.GRUPP_T_ADMIN

        isikukoodid = self.request.params.getall('oigus')
        not_added = []
        added = False
        kasutajad_id = [r.kasutaja_id for r in c.testiruum.labiviijad if r.kasutajagrupp_id == grupp_id]

        for ik in isikukoodid:
            if ik[0] == 'K':
                # olemasolev kasutaja
                kasutaja_id = ik[1:]
                kasutaja = model.Kasutaja.get(kasutaja_id)
                if not kasutaja:
                    # keegi teeb lolli nalja
                    continue
            else:
                # RRist küsitud andmed
                kasutaja = model.Kasutaja.get_by_ik(ik)
                if not kasutaja:
                    eesnimi = self.request.params.get('i%s_eesnimi' % ik)
                    perenimi = self.request.params.get('i%s_perenimi' % ik)
                    kasutaja = model.Kasutaja.add_kasutaja(ik, eesnimi, perenimi)
                    model.Session.flush()
                    
            if kasutaja.id in kasutajad_id:
                not_added.append(kasutaja.nimi)
            else:
                added = True
                isik = model.Labiviija(kasutaja=kasutaja,
                                       testikoht_id=c.testiruum.testikoht_id,
                                       testiruum_id=c.testiruum.id,
                                       kasutajagrupp_id=grupp_id)
                    
        if not_added:
            if len(not_added) == 1:
               buf = _('Kasutaja {s2} on juba lisatud').format(s2=', '.join(not_added))
            else:
               buf = _('Kasutajad {s2} on juba lisatud').format(s2=', '.join(not_added))
            self.error(buf)
        if added:
            model.Session.commit()
            self.success()

        return HTTPFound(location=self.h.url('test_nimekirjad', test_id=c.test.id, testiruum_id=c.testiruum.id))

    def _after_delete(self, parent_id=None):
        c = self.c
        return HTTPFound(location=self.h.url('test_nimekirjad', test_id=c.test.id, testiruum_id=c.testiruum.id))

    def __before__(self):
        """Väärtustame self.c.test testiga
        """
        self.c.test_id = self.request.matchdict.get('test_id')
        self.c.test = model.Test.get(self.c.test_id)
        testiruum_id = self.request.matchdict.get('testiruum_id')
        self.c.testiruum = model.Testiruum.get(testiruum_id)
        nimekiri_id = self.request.matchdict.get('nimekiri_id')
        self.c.nimekiri = model.Nimekiri.get(nimekiri_id)
        assert self.c.testiruum.nimekiri_id == self.c.nimekiri.id, 'vale nimekiri'
        assert self.c.nimekiri.test_id == self.c.test.id, 'vale test'
        BaseResourceController.__before__(self)

    def _perm_params(self):
        return {'obj':self.c.nimekiri}

        
