from eis.lib.baseresource import *
from eis.handlers.avalik.klabiviimine.labiviimised import LabiviimisedController
from eis.lib.resultentry import ResultEntry
from eis.lib.resultstat import ResultStat
from .testiosavalik import Testiosavalik
_ = i18n._
log = logging.getLogger(__name__)

class LabiviimineController(LabiviimisedController, Testiosavalik):
    """Oma testide läbiviimine
    """
    _permission = 'testiadmin,omanimekirjad'
    _EDIT_TEMPLATE = 'avalik/testid/labiviimine.mako' 
    _INDEX_TEMPLATE = None
    _actions = 'show,update,edit,delete' # võimalikud tegevused
    
    def _edit_d(self):
        if self.c.test.staatus == const.T_STAATUS_ARHIIV:
            self.error(_("Test on arhiveeritud"))
        self.c.item = self.c.testiruum
        if not self.c.item:
            # nimekirja pole valitud, kuvame tyhja lehe
            return self.render_to_response(self._EDIT_TEMPLATE)
        rc = self._edit(self.c.item)
        if isinstance(rc, (HTTPFound, Response)):
            return rc        
        return self.response_dict

    def _edit(self, item):
        self._redirect_ruum('id')
        LabiviimisedController._edit(self, item)
        self.c.markuskoostajale = self._get_markuskoostajale()

    def _get_sooritused(self):
        q = (model.Sooritus.query
             .filter(model.Sooritus.testiruum_id==self.c.testiruum.id)
             .join(model.Sooritus.sooritaja)
             .order_by(model.Sooritaja.perenimi,model.Sooritaja.eesnimi)
             )
        return q.all()

    def _check_sooritus(self, rcd):
        """Kontrollitakse, kas parameeter on lubatud sooritus.
        """
        rc = rcd.testiruum_id == self.c.testiruum.id 
        return rc

    def _after_update(self):
        return HTTPFound(location=self.url_current('edit'))

    def _get_markuskoostajale(self):
        """Leitakse kasutaja antud märkus sellele testile.
        """
        return (model.Testimarkus.query
                .filter_by(test_id=self.c.test.id)
                .filter_by(kasutaja_id=self.c.user.id)
                .first())

    def _edit_markuskoostajale(self, id):
        """Eeltesti koostajale antav tagasiside.
        """
        return self.render_to_response('avalik/testid/markuskoostajale.mako')

    def _edit_markuskoostajale_id(self, id):
        """Eeltesti koostajale antav tagasiside.
        """
        self.c.markuskoostajale = self._get_markuskoostajale()        
        return self.response_dict

    def _update_markuskoostajale(self, id):
        """Eeltesti koostajale antav tagasiside.
        """
        self.form = Form(self.request, schema=forms.avalik.testid.TestimarkusForm)
        if not self.form.validate():
            self.c.dialog_markuskoostajale = True
            return Response(self.form.render(self._EDIT_TEMPLATE,
                                             extra_info=self._edit_markuskoostajale_id(id)))
        else:
            rcd = self._get_markuskoostajale()
            if rcd is not None:
                rcd.sisu = self.form.data.get('sisu')
                #rcd.teema = self.form.data.get('teema')
            if not rcd:
                rcd = model.Testimarkus(test_id=self.c.test.id,
                         sisu=self.form.data.get('markus'),
                         kasutaja_id=self.c.user.id)

            model.Session.commit()
            self.success('Märkus on salvestatud!')
            return self._after_update()

    def __before__(self):
        c = self.c
        Testiosavalik.set_test_testiosa(self, 'id')
        #log.debug('before osa %s (%s) c.testiruum.id=%s' % (c.testiosa.id, c.testiosa.nimi, c.testiruum.id))
        if c.test and c.test.eeltest_id:
            # kui on eeltest, siis leiame minu korraldajakirje
            c.korraldaja = (model.Testiisik.query
                            .filter_by(test_id=c.test.id)
                            .filter_by(kasutaja_id=c.user.id)
                            .first())

        c.on_kutse = c.test.testiliik_kood == const.TESTILIIK_KUTSE and \
                     c.test.avaldamistase == const.AVALIK_MAARATUD
        LabiviimisedController.__before__(self)

    def _perm_params(self):
        if self.c.test and self.c.test.id != int(self.c.test_id):
            return False
        if self.c.testiruum:
            # testiruum on valitud, kontrollime seda
            nimekiri = self.c.testiruum.nimekiri
            if not nimekiri:
                return False
            if nimekiri.test_id and nimekiri.test_id != self.c.test.id:
                return False
            return {'obj':self.c.testiruum}
        else:
            # igayks võib tulla oma testiruumide loetelu vaatama
            return None

