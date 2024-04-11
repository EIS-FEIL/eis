from simplejson import dumps
from eis.lib.baseresource import *
_ = i18n._
log = logging.getLogger(__name__)

class TellimineController(BaseResourceController):
    """Eksamitööga tutvumise taotluse esitamine
    """
    _permission = 'sooritamine'
    _MODEL = model.Sooritus
    _EDIT_TEMPLATE = 'avalik/tulemused/skann.tellimine.mako'
    _ITEM_FORM = forms.avalik.sooritamine.SkannidTellimineForm
    _actions = 'edit,show,update'
    
    def _update(self, item):
        sooritus = item
        if not sooritus.tutv_esit_aeg:
            sooritus.tutv_esit_aeg = date.today()
        #sooritus.soovib_p = self.form.data.get('soovib_p') and True or False
        sooritus.soovib_skanni = self.form.data.get('soovib_skanni') and True or False
        epost = self.form.data.get('k_epost')
        if epost:
            self.c.user.get_kasutaja().epost = epost

        model.Session.commit()
        self._notify_innove(sooritus)

    def _notify_innove(self, sooritus):
        "Innove üldaadressile ja Maarja-Liisale saadetakse kiri, et on uus taotlus"
        to = self.request.registry.settings.get('smtp.tutvumine')
        if not to:
            return False
        sooritaja = sooritus.sooritaja
        test = sooritaja.test
        kasutaja = sooritaja.kasutaja
        ta = sooritus.toimumisaeg
        body = '%s esitas taotluse testitööga %s tutvumiseks (%s, toimumisaeg %s)' % \
               (kasutaja.nimi,
                sooritus.tahised,
                test.nimi,
                ta and ta.tahised or '-')
        subject = 'Testitööga tutvumise taotlus %s-%s' % (ta and ta.tahised or '', sooritus.tahised)
        log.debug('Saadan kirja aadressile %s' % (to))
        body = Mailer.replace_newline(body)
        if not Mailer(self).send(to, subject, body, out_err=False):
            return True
        else:
            return False

    def _after_update(self, id):
        """Mida teha peale õnnestunud salvestamist
        """        
        self.c.is_saved = True
        self.success(_("Taotlus on esitatud"))
        return self.edit()

    def _has_permission(self):
        id = self.request.matchdict.get('id')
        sooritus = model.Sooritus.get(id)
        if sooritus:
            sooritaja = sooritus.sooritaja
            tk = sooritaja.testimiskord
            dt = date.today()
            if sooritus.staatus == const.S_STAATUS_TEHTUD and tk:
                if self.c.user.get_kasutaja().on_volitatud(sooritaja.kasutaja_id):
                    if (tk.tutv_taotlus_alates and tk.tutv_taotlus_alates <= dt) and \
                           (tk.tutv_taotlus_kuni is None or tk.tutv_taotlus_kuni >= dt):
                        # võib tutvumise taotluse esitada
                        return True
        return False
