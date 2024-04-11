# -*- coding: utf-8 -*- 

from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class FailidController(BaseResourceController):
    """Testile lisatud failid
    """
    _permission = 'ekk-testid-failid'

    _MODEL = model.Testifail
    _INDEX_TEMPLATE = 'ekk/testid/failid.mako'
    _EDIT_TEMPLATE = 'ekk/testid/failid.mako'
    _LIST_TEMPLATE = 'ekk/testid/failid_list.mako'
    _DEFAULT_SORT = 'testifail.id' # vaikimisi sortimine

    def _search(self, q):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        if self.c.komplekt_id:
            q = q.filter_by(komplekt_id=self.c.komplekt_id)
        elif self.c.testiosa_id:
            q = q.join(model.Testifail.komplekt).\
                join(model.Komplekt.komplektivalik).\
                filter(model.Komplektivalik.testiosa_id==self.c.testiosa_id)
        return q
        #return None

    def _order_join(self, q, tablename):
        """Otsingu sorteerimine.
        """
        if tablename == 'komplekt':
            if self.c.komplekt_id:
                q = q.join(model.Testifail.komplekt)
                    
        return q

    def _create(self, **kw):
        self.c.komplekt_id = int(self.request.params.get('komplekt_id'))
        if self.request.params.get('f_filedata') != b'':
            item = model.Testifail(komplekt_id=self.c.komplekt_id)
            self._update(item)
            return item
        else:
            errors = {'f_filedata': 'Fail puudub'}
            raise ValidationError(self, errors)

    def _after_update(self, id):
        """Mida teha peale õnnestunud salvestamist
        """
        self.success()
        komplekt = model.Komplekt.get(self.c.komplekt_id)
        komplektivalik = komplekt.komplektivalik
        testiosa_id = komplektivalik.testiosa_id
        return HTTPFound(location=self.url('test_failid', test_id=self.c.test.id, komplekt_id=self.c.komplekt_id, komplektivalik_id=komplektivalik.id, testiosa_id=testiosa_id))

    def _after_delete(self, parent_id=None):
        komplekt = model.Komplekt.get(parent_id)
        komplektivalik = komplekt.komplektivalik
        testiosa_id = komplektivalik.testiosa_id
        return HTTPFound(location=self.url('test_failid', test_id=self.c.test.id, komplekt_id=parent_id, testiosa_id=testiosa_id, komplektivalik_id=komplektivalik.id))

    def _edit_markus(self, id):
        """Märkuse lisamise vormi avamine
        """
        ylem_id = self.request.params.get('ylem_id')
        if ylem_id:
            self.c.ylem = model.Testifailimarkus.get(ylem_id)
            assert self.c.ylem.testifail_id == self.c.item.id, _("Vale fail")
        return self.render_to_response('ekk/testid/testifailimarkus.mako')

    def _show_markus(self, id):
        """Märkuste vaatamine
        """
        return self.render_to_response('ekk/testid/testifailimarkused.mako')

    def _update_markus(self, id):
        """Märkuse salvestamine
        """
        self.form = Form(self.request, schema=forms.ekk.testid.TestifailimarkusForm)
        if not self.form.validate():
            self.c.dialog_markus = True
            return Response(self.form.render(self._EDIT_TEMPLATE,
                                             extra_info=self.response_dict))

        else:
            self.c.dialog_markus = False
            model.Testifailimarkus(testifail_id=self.c.item.id,
                         sisu=self.form.data.get('sisu'),
                         teema=self.form.data.get('teema'),
                         ylem_id=self.form.data.get('ylem_id'),
                         kasutaja_id=self.c.user.id)

            model.Session.commit()
            self.success(_("Märkus on lisatud!"))
            return HTTPFound(location=self.url('test_failid', test_id=self.c.test.id, komplekt_id=self.c.komplekt.id))

    def __before__(self):
        """Väärtustame self.c.test testiga
        """
        test_id = self.request.matchdict.get('test_id')
        self.c.test = model.Test.get(test_id)
        self.c.testiosa_id = self.request.params.get('testiosa_id')
        self.c.komplekt_id = self.request.params.get('komplekt_id')
        self.c.komplektivalik_id = self.request.params.get('komplektivalik_id')        
        testifail_id = self.request.matchdict.get('id')
        if testifail_id:
            self.c.item = model.Testifail.get(testifail_id)
            self.c.komplekt_id = self.c.item.komplekt_id
        if self.c.komplekt_id:
            self.c.komplekt = model.Komplekt.get(self.c.komplekt_id)
            self.c.komplektivalik_id = self.c.komplekt.komplektivalik_id
        if self.c.komplektivalik_id:
            self.c.komplektivalik = model.Komplektivalik.get(self.c.komplektivalik_id)
            self.c.testiosa_id = self.c.komplektivalik.testiosa_id
        if self.c.testiosa_id:
            self.c.testiosa = model.Testiosa.get(self.c.testiosa_id)
            assert self.c.test == self.c.testiosa.test, _("Vale test")
        elif len(self.c.test.testiosad):
            self.c.testiosa = self.c.test.testiosad[0]
            self.c.testiosa_id = self.c.testiosa.id
        BaseResourceController.__before__(self)

    def _perm_params(self):
        return {'obj':self.c.test}
