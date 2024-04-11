from cgi import FieldStorage
import formencode
from eis.forms import validators
from eis.lib.baseresource import *
_ = i18n._
from eis.lib.basegrid import BaseGridController
from eis.lib.xtee import rahvastikuregister, ehis
log = logging.getLogger(__name__)

class KoolitusedController(BaseResourceController):
    "Koolituste laadimine"

    #_MODEL = model.Kasutaja
    _SEARCH_FORM = forms.admin.KoolitusedForm
    _ITEM_FORM = forms.admin.KoolitusedForm
    _INDEX_TEMPLATE = '/admin/koolitused.mako'
    _index_after_create = True
            
    _permission = 'kasutajad'

    def _query(self):
        pass
 
    def _create(self, **kw):
        self.c.lang = self.form.data.get('lang')
        self.c.aine_kood = self.form.data.get('aine_kood')
        q = model.Klrida.get_q_by_kood('KEELETASE', ylem_kood=self.c.aine_kood)
        lubatud_tasemed = [r[1] for r in q.all()] # koodid
        self.c.keeletase = [r for r in self.form.data.get('keeletase') \
                            if r in lubatud_tasemed]
        self.c.koolitusaeg = self.form.data.get('koolitusaeg')
        self.c.kasutajagrupp_id = self.form.data.get('kasutajagrupp_id')
        
        if len(self.c.lang) == 0:
            raise ValidationError(self, {'lang':'Palun märkida keeled'})
        skeeled = ' '.join(self.c.lang)
        
        value = self.request.params.get('fail')
        if not isinstance(value, FieldStorage):
            raise ValidationError(self, {'fail': 'Palun sisestada fail'})

        # value on FieldStorage objekt
        value = value.value
        li_ik = []
        settings = self.request.registry.settings

        # kontrollime faili sisu ning jagame faili read isikute kaupa dictiks
        for line in value.splitlines():
            line = utils.guess_decode(line).strip()
            if line:
                row = self._split_row(line)
                if row:
                    userid = row[0]
                    if not userid:
                        raise ValidationError(self, {'fail': 'Puudub isikukood'})
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
                    uuendatavad.append(ik)
                
        if uuendatavad:
            # leidus isikuid, kelle andmeid on vaja uuendada või kelle andmeid polegi EISis
            self._uuenda(uuendatavad)
            model.Session.flush()
            
        cnt = 0
        for ik, row in li_ik:
            if ik:
                kasutaja = model.Kasutaja.get_by_ik(ik)
            if kasutaja:
                cnt += 1
                self._load_isik(kasutaja, row, skeeled)

        model.Session.commit()
        if cnt:
            msg = _("Failist laaditi {n} isiku koolitusandmed. ").format(n=cnt)
            self.notice(msg)
                            
        return self._redirect('index',
                              aine_kood=self.c.aine_kood,
                              kasutajagrupp_id=self.c.kasutajagrupp_id,
                              keeletase=self.c.keeletase,
                              lang=self.c.lang,
                              koolitusaeg=self.c.koolitusaeg and self.h.str_from_date(self.c.koolitusaeg))

    def _error_create(self):
        html = self.form.render(self._INDEX_TEMPLATE, extra_info=self.response_dict)
        return Response(html)

    def _split_row(self, line):
        row = [s.strip() for s in line.strip().split(';')]
        if len(row) < 3 or len(row) > 3 and row[3]:
            self.error(_("Vigane rida {s}. Real peab olema kolm välja (isikukood, e-post, telefon).").format(s=line))
            return
                
        userid, epost, telefon = row[:3]

        try:
            validators.Email(strip=True, max=255).to_python(epost)
        except formencode.api.Invalid as ex:
            self.error(_("Vigane e-posti aadress {s}").format(s=epost))
            return

        try:
            validators.String(max=20).to_python(telefon)
        except formencode.api.Invalid as ex:
            self.error(_("Vigane telefon {s}").format(s=telefon))
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
                        xtee.uuenda_rr_pohiandmed(self, kasutaja, showerr=False)
            if puudujad:
                self.error('Rahvastikuregistris pole andmeid isikukoodidega: %s' % ', '.join(puudujad))

    def _load_isik(self, kasutaja, row, skeeled):
        if not kasutaja.on_labiviija:
            kasutaja.on_labiviija = True
        
        profiil = kasutaja.give_profiil()      

        isikukood, epost, telefon = row[:3]
        if epost:
            kasutaja.epost = epost
        if telefon:
            kasutaja.telefon = telefon

        # Välisvaatleja
        # Hindaja (kirjalik)
        # Hindaja (suuline)
        # Intervjueerija
        # Komisjoni esimees
        # Komisjoni liige
        # Konsultant                 
        if self.c.kasutajagrupp_id == const.GRUPP_VAATLEJA:
            profiil.on_vaatleja = True
            profiil.v_koolitusaeg = self.c.koolitusaeg
            profiil.v_skeeled = skeeled
        else:
            for keeletase_kood in self.c.keeletase or [None]:
                aineprofiil = kasutaja.give_aineprofiil(self.c.aine_kood,
                                                        self.c.kasutajagrupp_id,
                                                        keeletase_kood)
                aineprofiil.koolitusaeg = self.c.koolitusaeg

            if self.c.kasutajagrupp_id in (const.GRUPP_HINDAJA_S, const.GRUPP_INTERVJUU):
                profiil.s_skeeled = skeeled
            elif self.c.kasutajagrupp_id == const.GRUPP_HINDAJA_K:
                profiil.k_skeeled = skeeled
