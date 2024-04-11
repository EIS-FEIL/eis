from eis.lib.baseresource import *
from eis.lib.xtee import ehis

log = logging.getLogger(__name__)
_ = i18n._
class OtsisooritajadController(BaseResourceController):
    """Sooritajate otsimine dialoogiaknas.
    Testimiskord on varem leitud.
    Hiljem salvestatakse sooritajad teises kontrolleris (Sooritajad)
    """
    _permission = 'omanimekirjad'
    _MODEL = model.Kasutaja
    _INDEX_TEMPLATE = '/avalik/testid/otsisooritajad.ik.mako'
    _get_is_readonly = False
    _actions = 'index' # võimalikud tegevused
    
    def _index_ik(self):
        "Otsing EHISest"
        rc = True
        self.c.isikukood = self.request.params.get('isikukood')
        if self.c.isikukood:
            usp = eis.forms.validators.IsikukoodP(self.c.isikukood)
            kasutaja = usp.get(model.Kasutaja)
            if not usp.isikukood:
                self.error(_("Sisestatud isikukood on vigases formaadis"))
            elif usp.isikukood_ee and self.request.is_ext():
                # vajadusel uuendame EHISest andmeid
                err = ehis.uuenda_opilased(self, [usp.isikukood_ee])
                if err:
                    self.error(err)
                    rc = False
                else:
                    model.Session.commit()
                    opilane = model.Opilane.get_by_ik(usp.isikukood)
                    if opilane and not kasutaja:
                        kasutaja = opilane.give_kasutaja()
            
                # kui EHISes ei ole andmeid ja EISis ka pole, siis küsime RRist
                if not kasutaja:
                    kasutaja = xtee.set_rr_pohiandmed(self, None, usp.isikukood_ee)
                # salvestame leitud isiku
                model.Session.commit()

            if kasutaja:
                self.c.items = [kasutaja]
        else:
            if 'isikukood' in self.request.params:
                self.error(_("Palun sisestada isikukood"))
        return self.render_to_response('avalik/testid/otsisooritajad.ik.mako')

    def _index_ehis(self):
        "Otsing EHISest"
        # kasutaja õppeasutus
        c = self.c
        if 'klass' in self.request.params:
            c.klass = self.request.params.get('klass')
            c.paralleel = self.request.params.get('paralleel')
            if c.paralleel:
                c.paralleel = c.paralleel.upper()
            if not c.klass:
                self.error(_('Palun sisesta klass, mille õpilasi pärid'))
            else:
                klass, ryhm_id = model.Klass.klass_ryhm(c.klass)
                kool_id = c.user.koht.kool_id
                c.user.uuenda_klass(kool_id, klass, c.paralleel)

                q = model.Opilane.query.filter_by(kool_id=kool_id)
                if klass:
                    q = q.filter_by(klass=klass)
                    if c.paralleel:
                        q = q.filter_by(paralleel=c.paralleel)
                elif ryhm_id:
                    q = q.filter_by(ryhm_id=ryhm_id)
                c.items = q.order_by(model.Opilane.perenimi,
                                     model.Opilane.eesnimi).all()

                if not len(c.items) and not self.has_errors():
                    self.error('Õpilasi ei leitud!')
        return self.render_to_response('avalik/testid/otsisooritajad.ehis.mako')

    def _index_ryhm(self):
        "Otsing õpilaste ryhmast"
        # kasutaja õppeasutus
        c = self.c
        self._sub_params_into_c('ryhm')
        q = (model.SessionR.query(model.Opperyhm.id, model.Opperyhm.nimi)
             .filter(model.Opperyhm.kasutaja_id==c.user.id)
             .filter(model.Opperyhm.koht_id==c.user.koht_id)
             .filter(model.Opperyhm.opperyhmaliikmed.any())
             .order_by(model.Opperyhm.nimi)
             )
        c.opt_ryhmad = tmp = [r for r in q.all()]
        if len(c.opt_ryhmad) == 1:
            c.ryhm_id = c.opt_ryhmad[0][0]
        if c.ryhm_id:
            try:
                ryhm_id = int(c.ryhm_id)
            except:
                ryhm_id = None
            if ryhm_id in [r[0] for r in c.opt_ryhmad]:
                q = (model.SessionR.query(model.Kasutaja.id,
                                         model.Kasutaja.nimi,
                                         model.Kasutaja.isikukood,
                                         model.Opilane.lang,
                                         model.Opilane.klass,
                                         model.Opilane.paralleel)
                     .join(model.Kasutaja.opperyhmaliikmed)
                     .filter(model.Opperyhmaliige.opperyhm_id==ryhm_id)
                     .outerjoin((model.Opilane,
                                 sa.and_(model.Opilane.kasutaja_id==model.Kasutaja.id,
                                         model.Opilane.on_lopetanud==False)))
                     .order_by(model.Kasutaja.nimi)
                     )
                c.items = [r for r in q.all()]
        return self.render_to_response('avalik/testid/otsisooritajad.ryhm.mako')

    def _index_fail(self):
        return self.render_to_response('avalik/testid/otsisooritajad.fail.mako')

    def __before__(self):
        c = self.c
        c.test_id = self.request.matchdict.get('test_id')
        c.testiruum_id = self.request.matchdict.get('testiruum_id')           
    
    def _perm_params(self):
        c = self.c
        c.nimekiri_id = int(self.request.matchdict.get('nimekiri_id'))
        if c.nimekiri_id == 0:
            # nimekirja pole veel loodud
            c.test = model.Test.get(c.test_id)
            return {'obj': c.test}
            
        c.nimekiri = model.Nimekiri.get(c.nimekiri_id)
        if not c.nimekiri:
            return False
        c.testimiskord = c.nimekiri.testimiskord
        c.test = c.nimekiri.test
        return {'obj': c.nimekiri}
