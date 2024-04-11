from eis.lib.baseresource import *
_ = i18n._
from eis.lib.basegrid import BaseGridController
from eis.handlers.admin.kasutajad import KasutajadController
log = logging.getLogger(__name__)

class KoolipsyhholoogidController(KasutajadController):
    "Koolipsyhholoogid"

    _MODEL = model.Kasutaja
    _SEARCH_FORM = forms.avalik.koolipsyhholoogid.KoolipsyhholoogidForm
    _ITEM_FORM = forms.avalik.koolipsyhholoogid.KoolipsyhholoogForm
    _INDEX_TEMPLATE = '/avalik/koolipsyhholoogid/koolipsyhholoogid.mako' # otsinguvormi mall
    _EDIT_TEMPLATE = '/avalik/koolipsyhholoogid/koolipsyhholoog.mako' # muutmisvormi mall
    _LIST_TEMPLATE = '/avalik/koolipsyhholoogid/koolipsyhholoogid_list.mako'
    _DEFAULT_SORT = 'perenimi'

    _permission = 'pslitsentsid'
    LGROUP = const.GRUPP_A_PSYH

    def _search(self, q):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        if self.c.isikukood:
            q = q.filter(eis.forms.validators.IsikukoodP(self.c.isikukood)
                         .filter(model.Kasutaja))
            item = q.first()
            if item:
                if not item.on_kehtiv_roll(self.LGROUP):
                    self.error(self._err_no_group())
        else:
            stmt = sa.sql.exists()\
                .where(model.Kasutajaroll.kasutaja_id==model.Kasutaja.id)
            stmt = stmt.where(model.Kasutajaroll.kasutajagrupp_id==self.LGROUP)
            if self.c.kehtib:
                stmt = stmt.where(model.Kasutajaroll.kehtib_kuni>=date.today())
            q = q.filter(stmt)

        if self.c.eesnimi:
            q = q.filter(model.Kasutaja.eesnimi.ilike(self.c.eesnimi))
        if self.c.perenimi:
            q = q.filter(model.Kasutaja.perenimi.ilike(self.c.perenimi))

        return q

    def _edit(self, item):
        self.c.kasutaja = item
        if item.id and not item.on_kehtiv_roll(self.LGROUP):
            self.error(self._err_no_group())

    def _update(self, item):      
        is_new = not item.id
        item.from_form(self.form.data, 'k_')
        self._save_ik(item)        
        model.Session.flush()
        model.Aadress.adr_from_form(item, self.form.data, 'a_')
        anna_roll(self, item, self.request.params.get('on_roll'), self.LGROUP)

    def _err_no_group(self):
        return _("Isikul ei ole koolipsühholoogi litsentsi")
            
def anna_roll(handler, kasutaja, on_roll, grupp):
    "Roll antakse või võetakse"
    roll =  None
    for r in kasutaja.kasutajarollid:
        if r.kasutajagrupp_id==grupp:
            roll = r
            break

    if on_roll:
        if roll:
            if not roll.kehtiv:
                roll.kehtib_kuni = const.MAX_DATE
        else:
            roll = model.Kasutajaroll(kasutaja_id=kasutaja.id,
                                      kasutajagrupp_id=grupp,
                                      kehtib_alates=date.today(),
                                      kehtib_kuni=const.MAX_DATE)
            kasutaja.kasutajarollid.append(roll)
            _log_roll(handler, roll, False)
    else:
        if roll:
            _log_roll(handler, roll, False)
            roll.delete()       

def _log_roll(handler, roll, is_delete):
    grupp_id = roll.kasutajagrupp_id
    if is_delete:
        sisu = 'Eemaldamine\n' + roll.get_str()
    else:
        old_values, new_values = roll._get_changed_values()
        if not new_values:
            return
        sisu = roll.get_str()
    krl = model.Kasutajarollilogi(kasutaja_id=roll.kasutaja_id,
                                  muutja_kasutaja_id=handler.c.user.id,
                                  aeg=datetime.now(),
                                  sisu=sisu,
                                  kasutajagrupp_id=grupp_id,
                                  tyyp=const.USER_TYPE_KOOL)
    roll.kasutajarollilogid.append(krl)
