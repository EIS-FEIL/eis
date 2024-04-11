from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class ParoolidController(BaseResourceController):

    _permission = 'kparoolid'
    _MODEL = model.Kasutajaajalugu
    _SEARCH_FORM = forms.admin.ParoolidForm
    _INDEX_TEMPLATE = 'admin/parool.mako' # otsinguvormi mall
    _LIST_TEMPLATE = 'admin/parool.ajalugu.mako'
    _DEFAULT_SORT = '-kasutajaajalugu.id'
    _ignore_default_params = ['sort','jatka','id']
    _get_is_readonly = False
    
    def _search_default(self, q):
        return None

    def _search(self, q):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        c = self.c
        kasutaja_id = self.form.data.get('id')
        if kasutaja_id:
            kasutaja = model.Kasutaja.get(kasutaja_id)
        else:
            c.isikukood = self.form.data.get('isikukood')
            usp = eis.forms.validators.IsikukoodP(c.isikukood)
            kasutaja = usp.valid and usp.get(model.Kasutaja)
            if usp.isikukood_ee and not kasutaja:
                # pole veel kasutaja, aga kas on õpilane
                opilane = model.Opilane.query.filter_by(isikukood=usp.isikukood_ee).first()
                if opilane:
                    kasutaja = opilane.give_kasutaja()

                else:
                    if self.request.is_ext() and usp.isikukood_ee:
                        # otsime RRist
                        kasutaja = xtee.set_rr_pohiandmed(self, None, usp.isikukood_ee)
                if kasutaja:
                    # salvestame lisatud kasutaja
                    model.Session.commit()

        if kasutaja:
            rc, err = self._can_set_pwd(kasutaja)
            if not rc:
                self.error(err)
            else:
                c.kasutaja = kasutaja
                q = q.filter_by(kasutaja_id=kasutaja.id)
                return q
        elif c.jatka:
            if not c.isikukood:
                self.error(_("Palun sisestada isikukood"))        
            else:
                self.error(_("Kasutajat ei leitud"))

    def create(self):
        """POST /admin_ITEMS: Create a new item"""
        self.form = Form(self.request, schema=self._ITEM_FORM)
        if self.form.validate():
            try:
                item = self._create()
            except ValidationError as e:
                self.form.errors = e.errors
        if self.form.errors or self.has_errors():
            return Response(self.form.render(self._EDIT_TEMPLATE,
                                             extra_info=self._new_d()))
        model.Session.commit()
        return self._redirect(action='index', id=item and item.id)

    def _create(self):
        "Parooli andmine"
        c = self.c
        kasutaja_id = self.form.data.get('id')
        c.kasutaja = model.Kasutaja.get(kasutaja_id)
        if c.kasutaja:
            # kontrollime, et pole kõva kasutaja
            rc, err = self._can_set_pwd(c.kasutaja)
            if not rc:
                self.error(err)
                return

            c.pwd = User.gen_pwd()
            c.kasutaja.set_password(c.pwd, True)       
            self.notice(_("Uus parool on: {s}").format(s=c.pwd))
        return self.c.kasutaja

    def _can_set_pwd(self, kasutaja):
        # kparoolid UPDATE - annab õiguse muuta parooli kasutajal, kes pole eksamikeskuse kasutaja
        # kparoolid-ekk UPDATE - annab õiguse muuta kõigi isikute paroole

        # olemasoleval kasuajal saab parooli muuta
        rc = False
        if self.c.user.has_permission('admin', const.BT_UPDATE):
            # admin saab kõigi kasutajate paroole muuta
            rc = True
        elif self.c.user.has_permission('kparoolid', const.BT_UPDATE):
            # ei saa muuta eksamikeskuse kasutajate paroole
            rc = not kasutaja.on_kehtiv_ametnik
        if rc:
            return True, None
        else:
            return False, _("Selle kasutaja parooli muutmiseks on eriõiguseid vaja")

