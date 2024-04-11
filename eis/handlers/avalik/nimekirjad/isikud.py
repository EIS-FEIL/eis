from eis.lib.baseresource import *
_ = i18n._
from eis.lib.xtee import ehis

log = logging.getLogger(__name__)

class IsikudController(BaseResourceController):
    """Sooritajate otsimine dialoogiaknas.
    Testimiskord on varem leitud.
    Hiljem salvestatakse sooritajad teises kontrolleris (Sooritajad)
    """
    _permission = 'nimekirjad'
    _MODEL = model.Kasutaja
    _INDEX_TEMPLATE = 'avalik/nimekirjad/isikud.ik.mako'
    _get_is_readonly = False
    
    def index(self):
        sub = self.request.params.get('sub')
        if sub == 'fail':
            return self._index_fail()
        elif sub == 'ehis':
            return self._index_ehis()
        else: # 'ik'
            return self._index_ik()

    def _index_ik(self):
        "Otsing EHISest"
        c = self.c
        rc = True
        c.isikukood = self.request.params.get('isikukood')
        usp = eis.forms.validators.IsikukoodP(c.isikukood)
        kasutaja = opilane = None
        kasutaja = usp.get(model.Kasutaja)
        if usp.isikukood_ee and self.request.is_ext():
            # vajadusel uuendame EHISest andmeid
            err = ehis.uuenda_opilased(self, [usp.isikukood_ee])
            if err:
                self.error(err)
                rc = False
            model.Session.commit()
            if not kasutaja:
                opilane = model.Opilane.get_by_ik(usp.isikukood_ee)
                if opilane:
                    kasutaja = opilane.give_kasutaja()
                    model.Session.commit()
            if not opilane and not kasutaja and self.request.is_ext():
                # teeme päringu RRist
                kasutaja = xtee.set_rr_pohiandmed(self, None, usp.isikukood_ee)
                if kasutaja:
                    # salvestame leitud isiku
                    model.Session.commit()
        if not kasutaja and c.isikukood:
            self.error(_("Sellise isikukoodiga isikut ei leitud!"))
        if kasutaja:
            if self.c.test.testiliik_kood == const.TESTILIIK_RIIGIEKSAM:
                if opilane and opilane.klass in ('7','8','9'):
                    err = _("{s}. klassi õpilasi ei või riigieksamile registreerida").format(s=opilane.klass)
                    self.error(err)
                    rc = False
            if rc:
                # kui EHISe päring ei andnud vigu või kui EHISe päringut polnud vaja teha
                self.c.items = [kasutaja]                    

        return self.render_to_response('avalik/nimekirjad/isikud.ik.mako')

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
                self.error(_("Palun sisesta klass, mille õpilasi pärid"))
            else:
                klass, ryhm_id = model.Klass.klass_ryhm(c.klass)
                kool_id = c.user.koht.kool_id
                c.user.uuenda_klass(kool_id, klass, c.paralleel)

                q = model.Opilane.query
                if self.request.is_ext() and kool_id:
                    q = q.filter_by(kool_id=kool_id)
                else:
                    q = q.filter_by(koht_id=c.user.koht.id)
                if klass:
                    q = q.filter_by(klass=klass)
                    if c.paralleel:
                        q = q.filter_by(paralleel=c.paralleel)
                elif ryhm_id:
                    q = q.filter_by(ryhm_id=ryhm_id)
                c.items = q.order_by(model.Opilane.perenimi,
                                     model.Opilane.eesnimi).all()
                log.debug(str(q))
                log.debug('OPILASI:%d' % len(c.items))

                if not len(c.items) and not self.has_errors():
                    self.error(_("Õpilasi ei leitud!"))
        return self.render_to_response('avalik/nimekirjad/isikud.ehis.mako')

    def _index_fail(self):
        return self.render_to_response('avalik/nimekirjad/isikud.fail.mako')
    
    def __before__(self):
        c = self.c
        c.testimiskord_id = int(self.request.matchdict.get('testimiskord_id'))
        c.testimiskord = model.Testimiskord.get(c.testimiskord_id)
        c.test = c.testimiskord.test

    def _perm_params(self):
        return {'obj':self.c.testimiskord}
