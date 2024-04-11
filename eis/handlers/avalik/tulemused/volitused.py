from eis.lib.baseresource import *
_ = i18n._
from eis.lib.xtee import set_rr_pohiandmed
from .tulemused import TulemusedController
log = logging.getLogger(__name__)

# päritud tulemuste kontrollerist, et vea korral index() võtta oleks
class VolitusedController(TulemusedController):
    """Õiguste andmine ja võtmine kasutaja tulemuste vaatamiseks
    """
    _permission = 'sooritamine'
    _MODEL = model.Kasutaja
    _actions = 'index,create,new,download,show,delete,edit'

    def create(self):
        self.form = Form(self.request, schema=forms.avalik.regamine.VolitusForm)
        if not self.form.validate():
            return Response(self.form.render(self._INDEX_TEMPLATE,
                                             extra_info=self._index_d()))
        userid = self.form.data.get('isikukood')
        usp = eis.forms.validators.IsikukoodP(userid)
        kasutaja = usp.get(model.Kasutaja)
        if not usp.valid:
            self.error(_("Vigane isikukood"))
            kasutaja = None
        elif not kasutaja:
            kasutaja = set_rr_pohiandmed(self, None, userid)
            if kasutaja:
                model.Session.flush()
                
        if kasutaja and kasutaja.id == self.c.user.id:
            self.error(_("Kasutajale endale pole enda andmete vaatamiseks vaja volitust anda"))
        elif kasutaja:
            rc = True
            q = (model.Volitus.query
                 .filter(model.Volitus.volitatu_kasutaja_id==kasutaja.id)
                 .filter(model.Volitus.opilane_kasutaja_id==self.c.user.id)
                 .filter(model.Volitus.tyhistatud==None)
                 .filter(model.Volitus.kehtib_kuni >= datetime.now())
                 )
            if kasutaja.id and q.count() > 0:
                self.error(_("Volitus juba kehtib"))
                rc = False
            
            if rc:
                model.Volitus(volitatu_kasutaja_id=kasutaja.id,
                              opilane_kasutaja_id=self.c.user.id,
                              andja_kasutaja_id=self.c.user.id,
                              kehtib_alates=datetime.now(),
                              kehtib_kuni=const.MAX_DATETIME)
                model.Session.commit()
                self.success()

        return HTTPFound(location=self.url('tulemused'))

    def delete(self):
        id = self.request.matchdict.get('id')
        q = (model.Session.query(model.Volitus)
             .filter_by(opilane_kasutaja_id=self.c.user.id)
             .filter_by(volitatu_kasutaja_id=id))
        for rcd in q.all():
            rcd.tyhistatud = datetime.now()
            rcd.tyhistaja_kasutaja_id = self.c.user.id
        model.Session.commit()
        return HTTPFound(location=self.url('tulemused'))

    def _has_permission(self):
        return True
