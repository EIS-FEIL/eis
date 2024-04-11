from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class ErisooritusedController(BaseResourceController):
    """Testile registreeritud erivajadusega sooritajad
    """
    _permission = 'ekk-testid'
    _MODEL = model.Erikomplekt
    _INDEX_TEMPLATE = 'ekk/testid/erisooritused.mako'
    _DEFAULT_SORT = '-sooritus.id' # vaikimisi sortimine

    def _query(self):
        testiosa_id = self.c.komplekt.komplektivalik.testiosa_id
        return model.Sooritus.query.\
            join(model.Sooritus.toimumisaeg).\
            filter(model.Toimumisaeg.testiosa_id==testiosa_id).\
            filter(model.Sooritus.on_erivajadused==True)

    def _showlist(self):
        """Otsingu tulemuste kuvamine.
        """
        return self.render_to_response(self._INDEX_TEMPLATE)

    def create(self):
        """Testile registreeritud erivajadustega sooritajate seostamine
        antud komplektiga
        """
        cnt = 0
        for sooritus_id in self.request.params.getall('valik_id'):
            sooritus_id = int(sooritus_id)
            sooritus = model.Sooritus.get(sooritus_id)
            # erikomplekti kirje
            q = (model.Session.query(model.Erikomplekt)
                 .filter_by(komplekt_id=self.c.komplekt.id)
                 .filter_by(sooritus_id=sooritus_id))
            if q.count() > 0:
                self.error(_("Sooritaja {s} on juba lisatud").format(s=sooritus.sooritaja.kasutaja.nimi))
            else:
                model.Erikomplekt(komplekt_id=self.c.komplekt.id,
                                  sooritus=sooritus)
                cnt += 1

            # valitud komplekti kirje
            kv_id = self.c.komplekt.komplektivalik_id
            sk = (model.Session.query(model.Soorituskomplekt)
                  .filter_by(komplektivalik_id=kv_id)
                  .filter_by(sooritus_id=sooritus_id)
                  .first())
            if not sk:
                sk = model.Soorituskomplekt(komplektivalik_id=kv_id,
                                            sooritus_id=sooritus_id,
                                            komplekt_id=self.c.komplekt.id)
            elif sooritus.staatus <= const.S_STAATUS_ALUSTAMATA:
                if sk.komplekt_id != self.c.komplekt.id:
                    sk.komplekt_id = self.c.komplekt.id
            
        if cnt > 0:
            model.Session.commit()
            self.success()
        return HTTPFound(location=self.url('test_erialatest', test_id=self.c.test.id, id=self.c.komplekt.id))

    def _delete(self, item):
        sooritus = item.sooritus
        if sooritus.staatus <= const.S_STAATUS_ALUSTAMATA:
            # kustutame soorituskomplekti, kui pole veel lahendama hakanud
            sooritus_id = item.sooritus_id
            kv_id = self.c.komplekt.komplektivalik_id
            sk = (model.Session.query(model.Soorituskomplekt)
                  .filter_by(komplektivalik_id=kv_id)
                  .filter_by(sooritus_id=sooritus_id)
                  .filter_by(komplekt_id=self.c.komplekt.id)
                  .first())
            if sk:
                sk.delete()
        # erikomplekti kustutamine
        super()._delete(item)
    
    def _after_delete(self, parent_id=None):
        return HTTPFound(location=self.url('test_erialatest', test_id=self.c.test.id, id=self.c.komplekt.id))

    def __before__(self):
        """Väärtustame self.c.test testiga
        """
        test_id = self.request.matchdict.get('test_id')
        self.c.test = model.Test.get(test_id)
        komplekt_id = self.request.matchdict.get('komplekt_id')
        self.c.komplekt = model.Komplekt.get(komplekt_id)

        BaseResourceController.__before__(self)

    def _perm_params(self):
        return {'obj':self.c.test}

