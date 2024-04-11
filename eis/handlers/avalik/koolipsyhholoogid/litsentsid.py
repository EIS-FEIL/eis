from cgi import FieldStorage
import formencode
from eis.forms import validators
from eis.lib.baseresource import *
from eis.lib.xtee import rahvastikuregister, ehis
from .koolipsyhholoogid import anna_roll
log = logging.getLogger(__name__)
_ = i18n._

class LitsentsidController(BaseResourceController):
    "Koolituste laadimine"
    _SEARCH_FORM = forms.avalik.koolipsyhholoogid.LitsentsidForm
    _ITEM_FORM = forms.avalik.koolipsyhholoogid.LitsentsidForm
    _INDEX_TEMPLATE = '/avalik/koolipsyhholoogid/litsentsid.mako'
    _index_after_create = True
            
    _permission = 'pslitsentsid'
    LGROUP = const.GRUPP_A_PSYH
    
    def _query(self):
        pass
 
    def _create(self, **kw):
        value = self.request.params.get('fail')
        if not isinstance(value, FieldStorage):
            raise ValidationError(self, {'fail': _('Palun sisestada fail')})

        # value on FieldStorage objekt
        value = value.value
        uuendatavad = set()

        settings = self.request.registry.settings
        li_ik = []
        # kontrollime faili sisu ning jagame faili read isikute kaupa dictiks
        for line in value.splitlines():
            line = utils.guess_decode(line).strip()
            if line:
                row = self._split_row(line)
                if row:
                    userid = row[0]
                    usp = eis.forms.validators.IsikukoodP(userid)
                    if not usp.isikukood:
                        raise ValidationError(self, {'fail': 'Vigane isikukood "%s"' % userid})
                    li_ik.append((usp.isikukood, row))

        uuendatavad = []
        for ik, row in li_ik:
            if ik:
                kasutaja = model.Kasutaja.get_by_ik(ik)
                uuendada = not kasutaja or kasutaja.ametikoht_uuendada(settings)
                if uuendada:
                    uuendatavad.add(ik)
        if uuendatavad:
            # leidus isikuid, kelle andmeid on vaja uuendada või kelle andmeid polegi EISis
            self._uuenda(uuendatavad)
            model.Session.flush()

        cnt = 0
        for ik, row in li_ik:
            kasutaja = model.Kasutaja.get_by_ik(ik)
            if kasutaja:
                cnt += 1
                self._load_isik(kasutaja, row)

        model.Session.commit()
        if cnt:
            msg = _("Failist laaditi {s} isiku andmed. ").format(s=cnt)
            self.notice(msg)
                            
        return self._redirect('index')

    def _error_create(self):
        html = self.form.render(self._INDEX_TEMPLATE, extra_info=self.response_dict)
        return Response(html)

    def _split_row(self, line):
        row = [s.strip() for s in line.rstrip(';').split(';')]

        # isikukood, epost, telefon = row
        isikukood = row[0]
        try:
            validators.Isikukood().to_python(isikukood)
        except formencode.api.Invalid as ex:
            self.error(_("Vigane isikukood {s}").format(s=isikukood))
            return

        return row

    def _uuenda(self, uuendatavad):
        "Uuendame nende isikute andmed, kelle andmeid EISis ei ole või kelle andmed vajavad uuendamist"
        
        reg = rahvastikuregister.Rahvastikuregister(handler=self)            
        puudujad = []

        for isikukood in uuendatavad:
            kasutaja = model.Kasutaja.get_by_ik(isikukood)
            if not kasutaja:
                # kasutajat pole EISis
                kasutaja = rahvastikuregister.set_rr_pohiandmed(self, kasutaja, isikukood=isikukood, reg=reg)
            if not kasutaja:
                # kasutajat pole RRis
                puudujad.append(isikukood)
                continue
        if puudujad:
            self.error(_('Rahvastikuregistris pole andmeid isikukoodidega {s}').format(s=', '.join(puudujad)))

    def _load_isik(self, kasutaja, row):
        anna_roll(self, kasutaja, True, self.LGROUP)
