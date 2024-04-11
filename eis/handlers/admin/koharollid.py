from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class KoharollidController(BaseResourceController):
    _permission = 'admin'
    _MODEL = model.Kasutajaroll
    _INDEX_TEMPLATE = 'admin/isikud.mako' # otsinguvormi mall
    _EDIT_TEMPLATE = 'admin/koht.roll.mako' # muutmisvormi mall
    _ITEM_FORM = forms.admin.KoharollForm

    def create(self):
        self.form = Form(self.request, schema=self._ITEM_FORM)
        if self.form.validate():
            try:
                self._create()
            except ValidationError as e:
                self.form.errors = e.errors
                
        if self.form.errors:
            self.c.dialog = True
            return Response(self.form.render(self._EDIT_TEMPLATE,
                                             extra_info=self._new_d()))
        model.Session.commit()
        return self._after_update()

    def _after_update(self, id=None):
        return HTTPFound(location=self.url('admin_koht_rollid', koht_id=self.c.koht.id))

    def _create(self):
        """Kasutajarolli(de) lisamine
        """
        grupp = model.Kasutajagrupp.get(self.form.data['kasutajagrupp_id'])
        assert grupp.tyyp == const.USER_TYPE_KOOL, _("Vale grupp")

        kehtib_kuni = self.form.data.get('kehtib_kuni') or const.MAX_DATE
        for isikukood in self.request.params.getall('oigus'):
            kasutaja = model.Kasutaja.get_by_ik(isikukood)
            if kasutaja:
                if model.Kasutajaroll.query.\
                        filter_by(kasutaja_id=kasutaja.id).\
                        filter_by(koht_id=self.c.koht.id).\
                        filter_by(kasutajagrupp_id=grupp.id).\
                        count() > 0:
                    self.error(_("Kasutaja {s} juba on antud rollis").format(s=kasutaja.nimi))
                    continue

            if not kasutaja:
                continue
            item = model.Kasutajaroll(kasutajagrupp_id=grupp.id,
                                      kasutaja_id=kasutaja.id,
                                      koht_id=self.c.koht.id,
                                      kehtib_alates=date.today(),
                                      kehtib_kuni=kehtib_kuni)
            self._log_roll(item, False)

    def _update(self, item):
        rc = True
        grupp = model.Kasutajagrupp.get(self.form.data['kasutajagrupp_id'])
        assert grupp.tyyp == const.USER_TYPE_KOOL, _("Vale grupp")
        kehtib_kuni = self.form.data.get('kehtib_kuni') or const.MAX_DATE
        if model.Kasutajaroll.query.\
                filter_by(kasutaja_id=item.kasutaja.id).\
                filter_by(koht_id=self.c.koht.id).\
                filter_by(kasutajagrupp_id=grupp.id).\
                filter(model.Kasutajaroll.id != item.id).\
                count() > 0:
            self.error(_("Kasutaja juba on antud rollis"))
            rc = False

        if rc:
            item.kasutajagrupp_id = grupp.id
            item.kehtib_kuni = kehtib_kuni
            model.Session.commit()
            self.success()
        return self._after_update()
            
    def _log_roll(self, roll, is_delete):
        grupp_id = roll.kasutajagrupp_id
        if is_delete:
            sisu = 'Eemaldamine\n' + roll.get_str()
        else:
            old_values, new_values = roll._get_changed_values()
            if not new_values:
                return
            sisu = roll.get_str()
        krl = model.Kasutajarollilogi(kasutaja_id=roll.kasutaja_id,
                                      muutja_kasutaja_id=self.c.user.id,
                                      aeg=datetime.now(),
                                      sisu=sisu,
                                      kasutajagrupp_id=grupp_id,
                                      kasutajaroll=not is_delete and roll or None,
                                      tyyp=const.USER_TYPE_KOOL)

    def __before__(self):
        self.c.koht = model.Koht.get(self.request.matchdict.get('koht_id'))
