from eis.lib.baseresource import *
from eis.lib.basegrid import BaseGridController
_ = i18n._

log = logging.getLogger(__name__)

class ErivajadusedController(BaseResourceController):
    """Soorituse erivajadused
    """
    _permission = 'erivmark,erivmark_p'
    _MODEL = model.Sooritus
    _EDIT_TEMPLATE = 'avalik/nimekirjad/erivajadus.mako'
    _ITEM_FORM = forms.avalik.regamine.ErivajadusedForm

    def _update(self, item):
        if self.c.is_edit_p:
            # salvestatakse ainult neid eritingimusi, mida Innove ei kinnita
            self._update_p(item)
            return
        errors = {}
        collection = []

        if item.on_erivajadused_kinnitatud:
            return

        on_erivajadused = False
        vabastatud_alatestid_id = self.form.data.get('vaba_alatest_id')

        # testiosa vabastus
        if self.form.data.get('vaba_osa'):
            # kogu testiosast vabastatud
            item.staatus = const.S_STAATUS_VABASTATUD
            on_erivajadused = True
            for alatest in item.alatestid:
                atos = item.give_alatestisooritus(alatest.id)
                atos.staatus = const.S_STAATUS_VABASTATUD
        else:          
            # alatestide vabastus
            for alatest in item.alatestid:
                on_vabastatud = alatest.id in vabastatud_alatestid_id
                if on_vabastatud:
                    on_erivajadused = True
                atos = item.get_alatestisooritus(alatest.id)
                if atos and atos.staatus == const.S_STAATUS_VABASTATUD and not on_vabastatud:
                    # eemaldame vabastuse
                    atos.staatus = item.staatus
                elif on_vabastatud:
                    if not atos:
                        atos = item.give_alatestisooritus(alatest.id)
                    if atos.staatus != const.S_STAATUS_VABASTATUD:
                        atos.staatus = const.S_STAATUS_VABASTATUD

            if item.staatus == const.S_STAATUS_VABASTATUD:
                # võtame testiosa vabastuse maha
                item.staatus = item.sooritaja.staatus

            for ind, rcd in enumerate(self.form.data.get('ev')):
                if not rcd.get('erivajadus_kood'):
                    # üldine märkuste kirje
                    rcd['erivajadus_kood'] = None
                    rcd['taotlus'] = bool(rcd.get('taotlus_markus'))
                if rcd.get('taotlus'):
                    if rcd.get('erivajadus_kood'):
                        on_erivajadused = True
                    if not rcd['taotlus_markus']:
                        errors['ev-%d.taotlus_markus' % ind] = _("puudub")
                    collection.append(rcd)

        item.on_erivajadused_vaadatud = False
        if errors:
            raise ValidationError(self, errors)
        
        BaseGridController(item.erivajadused, model.Erivajadus).save(collection)
        item.sooritaja.from_form(self.form.data, 'r_')
        model.Session.flush()
        item.set_erivajadused(None)
        if not item.on_erivajadused:
            self.notice(_("Ühtki eritingimust pole valitud"))
            
    def _update_p(self, item):
        # salvestatakse ainult neid eritingimusi, mida Innove ei pea kinnitama
        errors = {}
        on_erivajadused = False
        collection = []
        for ind, rcd in enumerate(self.form.data.get('ev')):
            if not rcd.get('erivajadus_kood'):
                # üldine märkuste kirje
                rcd['erivajadus_kood'] = None
                rcd['taotlus'] = bool(rcd.get('taotlus_markus'))
            if rcd.get('taotlus'):
                if rcd.get('erivajadus_kood'):
                    on_erivajadused = True
                if not rcd['taotlus_markus']:
                    errors['ev-%d.taotlus_markus' % ind] = _("puudub")
                collection.append(rcd)

        if errors:
            raise ValidationError(self, errors)
        erivajadused = [r for r in item.erivajadused if r.ei_vaja_kinnitust(self.c.test)]
        BaseGridController(erivajadused, model.Erivajadus, supercollection=item.erivajadused).save(collection)
        item.sooritaja.from_form(self.form.data, 'r_')
        model.Session.flush()
        item.set_erivajadused(None)
        if not item.on_erivajadused:
            self.notice(_('Ühtki eritingimust pole valitud'))

    def _delete(self, item):
        for r in list(item.erivajadused):
            if not self.c.is_edit_p or r.ei_vaja_kinnitust(self.c.test):
                r.delete()
        item.tugiisik_kasutaja_id = None
        model.Session.flush()
        item.set_erivajadused(None)
        model.Session.commit()
        self.success(_("Eritingimused on tühistatud"))

    def _after_delete(self, parent_id=None):
        c = self.c
        return HTTPFound(location=self.url('nimekiri_kanne', testimiskord_id=c.testimiskord_id, id=parent_id))

    def __before__(self):
        c = self.c
        c.sooritus = model.Sooritus.get(self.request.matchdict.get('id'))
        c.sooritaja = c.sooritus.sooritaja

        # ekk test
        c.testimiskord_id = c.sooritaja.testimiskord_id
        c.testimiskord = c.sooritaja.testimiskord
        # avalik test
        c.nimekiri_id = c.sooritaja.nimekiri_id
        c.nimekiri = c.sooritaja.nimekiri

        c.test = c.sooritaja.test

    def _has_permission(self):
        rc = super()._has_permission()
        if rc:
            # lisaks testimiskorra õigusele kontrollime, et on oma kooli õpilane
            perm_bit = self._get_perm_bit()            
            rc = self.c.user.has_permission('regikuitk', perm_bit, self.c.sooritaja)
        return rc
        
    def _perm_params(self):
        c = self.c
        if (c.is_edit or c.action=='delete') and c.sooritus:
            if c.sooritus.on_erivajadused_kinnitatud or \
               c.testimiskord and not c.user.has_permission('erivmark', const.BT_UPDATE, obj=c.testimiskord):
                # erivajaduste periood on läbi
                if c.testimiskord and c.user.has_permission('erivmark_p', const.BT_UPDATE, obj=c.testimiskord):
                    # võib muuta ainult neid tingimusi, mida Innove ei pea kinnitama
                    c.is_edit_p = True
                else:
                    # ei saa midagi muuta
                    return False
        if c.testimiskord:
            return {'obj':c.testimiskord}
        else:
            return {'obj':c.nimekiri}
