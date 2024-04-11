from eis.lib.baseresource import *
from eis.lib.basegrid import BaseGridController
_ = i18n._

log = logging.getLogger(__name__)

class ErivajadusedController(BaseResourceController):
    """Soorituse erivajadused
    """
    _permission = 'erivajadused'
    _MODEL = model.Sooritus
    _EDIT_TEMPLATE = 'ekk/regamine/erivajadus.mako'
    _ITEM_FORM = forms.ekk.regamine.ErivajadusedForm

    def _update(self, item):
        collection = []
        vabastatud_alatestid_id = self.form.data.get('vaba_alatest_id')
        oli_vabastatud = item.staatus == const.S_STAATUS_VABASTATUD
        
        # testiosa vabastus
        if self.form.data.get('vaba_osa'):
            # kogu testiosast vabastatud
            item.staatus = const.S_STAATUS_VABASTATUD
            for alatest in item.alatestid:
                atos = item.give_alatestisooritus(alatest.id)
                atos.staatus = const.S_STAATUS_VABASTATUD
        else:          
            # alatestide vabastus
            for alatest in item.alatestid:
                on_vabastatud = alatest.id in vabastatud_alatestid_id
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

            for rcd in self.form.data.get('ev'):
                if not rcd.get('erivajadus_kood'):
                    # üldine märkuste kirje
                    rcd['erivajadus_kood'] = None
                    rcd['taotlus'] = bool(rcd.get('taotlus_markus'))
                    rcd['kinnitus'] = bool(rcd.get('kinnitus_markus'))
                if rcd.get('taotlus') or rcd.get('kinnitus'):
                    collection.append(rcd)

            BaseGridController(item.erivajadused, model.Erivajadus).save(collection)

        item.sooritaja.from_form(self.form.data, 'r_')
        model.Session.flush()
        item.set_erivajadused(None)

        if self.form.data.get('on_erivajadused_vaadatud'):
            item.on_erivajadused_vaadatud = True
        else:
            item.on_erivajadused_kinnitatud = True

        if oli_vabastatud != item.staatus == const.S_STAATUS_VABASTATUD:
            testiruum = item.testiruum
            if testiruum:
                testiruum.set_sooritajate_arv()
