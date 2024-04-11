from cgi import FieldStorage
import formencode
from eis.forms import validators
from eis.lib.baseresource import *
_ = i18n._
from eis.lib.basegrid import BaseGridController
from eis.lib.xtee import rahvastikuregister, ehis
log = logging.getLogger(__name__)

class KaskkirjadController(BaseResourceController):
    "Käskkirja laadimine"

    _SEARCH_FORM = forms.admin.KaskkirjadForm
    _ITEM_FORM = forms.admin.KaskkirjadForm
    _INDEX_TEMPLATE = '/admin/kaskkirjad.mako'
    _index_after_create = True
            
    _permission = 'kasutajad'

    def _query(self):
        pass
 
    def _create(self, **kw):
        cols = self.request.params.getall('col')
        self.c.aine_kood = self.form.data.get('aine_kood')
        q = model.Klrida.get_q_by_kood('KEELETASE', ylem_kood=self.c.aine_kood)
        lubatud_tasemed = [r[1] for r in q.all()] # koodid
        self.c.keeletase = [r for r in self.form.data.get('keeletase') \
                            if r in lubatud_tasemed]
        self.c.kaskkirikpv = self.form.data.get('kaskkirikpv')
        self.c.kasutajagrupp_id = self.form.data.get('kasutajagrupp_id')
        
        value = self.request.params.get('fail')
        if not isinstance(value, FieldStorage):
            raise ValidationError(self, {'fail': 'Palun sisestada fail'})

        # value on FieldStorage objekt
        value = utils.guess_decode(value.value)
        li_ik = []
        settings = self.request.registry.settings

        # kontrollime faili sisu ning jagame faili read isikute kaupa dictiks
        firstrow = True
        for line in value.splitlines():
            line = line.strip()
            if line and not (firstrow and line.startswith('isikukood')):
                row = self._split_row(line, cols)
                if row:
                    userid = row[0]
                    if not userid:
                        raise ValidationError(self, {'fail': 'Puudub isikukood'})
                    usp = eis.forms.validators.IsikukoodP(userid)
                    if not usp.isikukood:
                        raise ValidationError(self, {'fail': 'Vigane isikukood "%s"' % userid})
                    li_ik.append((usp.isikukood, row))
            firstrow = False
            
        uuendatavad = []
        for ik, row in li_ik:
            if ik:
                kasutaja = model.Kasutaja.get_by_ik(ik)
                uuendada = not kasutaja or kasutaja.ametikoht_uuendada(settings)
                if uuendada:
                    uuendatavad.append(ik)
        if uuendatavad:
            # leidus isikuid, kelle andmeid on vaja uuendada või kelle andmeid polegi EISis
            self._uuenda(uuendatavad)
            model.Session.flush()
            
        cnt = 0
        for ik, row in li_ik:
            kasutaja = model.Kasutaja.get_by_ik(ik)
            if kasutaja:
                cnt += 1
                self._load_isik(kasutaja, row, cols)

        model.Session.commit()
        if cnt:
            msg = _("Failist laaditi {n} isiku käskkirja lisamise andmed. ").format(n=cnt)
            self.notice(msg)
                            
        return self._redirect('index',
                              aine_kood=self.c.aine_kood,
                              kasutajagrupp_id=self.c.kasutajagrupp_id,
                              keeletase=self.c.keeletase,
                              kaskkirikpv=self.c.kaskkirikpv and self.h.str_from_date(self.c.kaskkirikpv))

    def _error_create(self):
        html = self.form.render(self._INDEX_TEMPLATE, extra_info=self.response_dict)
        return Response(html)

    def _split_row(self, line, cols):
        row = [s.strip() for s in line.split(';')]
        cnt = 1 + len(cols)
        if len(row) != cnt:
            self.error(_("Vigane rida {s}. Real peab olema {n} välja.").format(s=line, n=cnt))
            return
        return row

    def _uuenda(self, uuendatavad):
        "Uuendame nende isikute andmed, kelle andmeid EISis ei ole või kelle andmed vajavad uuendamist"
        
        reg = ehis.Ehis(handler=self)
        message, ametikohad = reg.ametikohad(uuendatavad)
        if message:
            self.error(message)
        else:
            di_ametikohad = dict()
            for isikukood in uuendatavad:
                di_ametikohad[isikukood] = list()
                
            for rcd in ametikohad:
                isikukood = str(rcd.isikukood)
                di_ametikohad[isikukood].append(rcd)

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
                else:
                    if kasutaja.update_pedagoogid(di_ametikohad[isikukood]):
                        # kui nimi erineb, siis uuendada isikuandmed
                        xtee.uuenda_rr_pohiandmed(self, kasutaja, showerr=False)
            if puudujad:
                self.error('Rahvastikuregistris pole andmeid isikukoodidega: %s' % ', '.join(puudujad))

    def _load_isik(self, kasutaja, row, cols):
        if not kasutaja.on_labiviija:
            kasutaja.on_labiviija = True
        
        profiil = kasutaja.give_profiil()      
        for ind, col in enumerate(cols):
            if len(row) < ind:
                err = _("Real ei ole piisavalt veerge (isikukood {s})").format(s=kasutaja.isikukood)
                break
            value = row[ind+1]
            if not value:
                continue
            if col == 'epost':
                try:
                    validators.Email(strip=True, max=255).to_python(value)
                except formencode.api.Invalid as ex:
                    self.error(_("Vigane e-posti aadress {s}").format(s=value))
                    return
                else:
                    kasutaja.epost = value
            elif col == 'telefon':
                try:
                    validators.String(max=20).to_python(value)
                except formencode.api.Invalid as ex:
                    self.error(_("Vigane telefon {s}").format(s=value))
                    return
                else:
                    kasutaja.telefon = value

        # Välisvaatleja
        # Hindaja (kirjalik)
        # Hindaja (suuline)
        # Intervjueerija
        # Komisjoni esimees
        # Komisjoni liige
        # Konsultant                 
        if self.c.kasutajagrupp_id == const.GRUPP_VAATLEJA:
            profiil.on_vaatleja = True
            profiil.v_kaskkirikpv = self.c.kaskkirikpv
        else:
            for keeletase_kood in self.c.keeletase or [None]:
                aineprofiil = kasutaja.give_aineprofiil(self.c.aine_kood,
                                                        self.c.kasutajagrupp_id,
                                                        keeletase_kood)
                aineprofiil.kaskkirikpv = self.c.kaskkirikpv

