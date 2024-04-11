import formencode
from eis.forms import validators
from eis.lib.baseresource import *
_ = i18n._
from eis.lib.xtee import ehis
import eis.handlers.ekk.otsingud.kohateated as kt
import eis.lib.regpiirang as regpiirang
from cgi import FieldStorage
log = logging.getLogger(__name__)

class SooritajadController(BaseResourceController):
    _EDIT_TEMPLATE = 'ekk/regamine/nimistu.sooritajad.mako'
    _ITEM_FORM = forms.ekk.regamine.NimistusooritajadForm
    
    _permission = 'regamine'

    def _index_d(self):
        return self.edit()

    def _search_protsessid(self, q):
        alates = datetime.now() - timedelta(hours=24)
        q = (q.filter(model.Arvutusprotsess.liik==model.Arvutusprotsess.LIIK_REG)
             .filter(model.Arvutusprotsess.kasutaja_id==self.c.user.id)
             .filter(model.Arvutusprotsess.param==self.c.korrad_id)
             .filter(model.Arvutusprotsess.algus>alates)
             )
        return q

    def edit(self):
        self.c.testiliik = self.request.params.get('testiliik')
        self.c.debug = self.request.params.get('debug') or ''
        self._get_protsessid()
        return self.render_to_response(self._EDIT_TEMPLATE)
  
    def _create(self):
        params = self.request.params
        self.c.testiliik = params.get('testiliik')
        cols = params.getall('col')

        # kas kool tohib registreeringut muuta
        if params.get('muutmatu'):
            muutmatu = 2
        elif params.get('tyhistamatu'):
            muutmatu = 1
        else:
            muutmatu = None

        # testimiskorrad, millele regatakse
        korrad_id = list(map(int, self.c.korrad_id.split('-')))
        korrad = self.c.korrad

        # kas määrata kõik laaditavad sooritajad testimiskorrasisesesse valimisse
        valimis = params.get('valimis') and True or False
            
        lang = None
        tadata = {}
        for r in self.form.data['tadata']:
            ta_id = r['ta_id']
            tk_id = r['testikoht_id']
            r['testikoht'] = tk_id and model.Testikoht.get(tk_id) or None
            tadata[ta_id] = r
            
        errors = {}
        tyhistada = params.get('tyhistada')
        if tyhistada:
            pohjus = params.get('pohjus')
            if not pohjus:
                errors['pohjus'] = _("Palun sisestada põhjus")
        
        value = params.get('ik_fail')
        if not isinstance(value, FieldStorage):
            errors['ik_fail'] = _("Faili ei leitud")
        else:
            # value on FieldStorage objekt
            filename = value.filename
            value = value.value
            li_ik, errors = self._split_to_lines(filename, value, errors)

        if errors:
            raise ValidationError(self, errors)
            
        if not errors and tyhistada:
            # tyhistada registreeringud
            return self._tyhista(li_ik, korrad_id, korrad, pohjus)
                
        if not errors and not tyhistada:
            # lisada registreeringud
            if valimis:
                # märgime, et testimiskordadel on testimiskorrasisene valim
                for kord in korrad:
                    if not kord.sisaldab_valimit:
                        kord.sisaldab_valimit = True
                model.Session.commit()
            # sooritajate regamine
            self._regfile(li_ik, korrad_id, korrad, value, tadata, muutmatu, valimis, cols)
        return self._redirect('edit')

    def _regfile(self, li_ik, korrad_id, korrad, filedata, tadata, muutmatu, valimis, cols):
        settings = self.request.registry.settings
        
        def childfunc(protsess):
            # EHISe päring
            uuendada_isikukoodid = set([r[0] for r in li_ik if r[0]])
            err = ehis.uuenda_opilased(self,
                                       uuendada_isikukoodid,
                                       protsess=protsess,
                                       progress_end=80)
            if err:
                self.error(err)

            puuduvad_isikukoodid = set()
            for isikukood, line in li_ik:
                opilane = model.Opilane.get_by_ik(isikukood)
                if opilane:
                    opilane.give_kasutaja()
                else:
                    puuduvad_isikukoodid.add(isikukood)

            # teatame isikukoodidest, millele vastavaid õpilasi ei leitud
            if len(puuduvad_isikukoodid) and self.request.is_ext():
                total = len(puuduvad_isikukoodid)
                if protsess:
                    progress_start = protsess.edenemisprotsent
                    progress_end = 90
                for cnt, isikukood in enumerate(puuduvad_isikukoodid):
                    # EHISes ei olnud, kas on EISis?
                    kasutaja = model.Kasutaja.get_by_ik(isikukood)
                    # teeme päringu RRist
                    kasutaja = xtee.set_rr_pohiandmed(self, kasutaja, isikukood)
                    if protsess:
                        prot = progress_start + (progress_end - progress_start) * cnt / total
                        protsess.edenemisprotsent = prot
                        model.Session.commit()

            model.Session.flush()

            # võimalikud testi ID väärtused
            testid_id = [tk.test_id for tk in korrad]
            
            # registreerime õpilase testile
            if protsess:
                progress_start = protsess.edenemisprotsent
                progress_end = 99
            total = 0
            cnt_total = len(li_ik)
            cnt_exists = cnt_err = 0 # mitu registreeringut oli juba varem olemas
            for ikline in li_ik:
                row, is_exists, is_err = self._isikuregamine(ikline, cols, korrad, testid_id, tadata, muutmatu, valimis, protsess)
                total += 1
                if is_exists:
                    cnt_exists += 1
                if is_err:
                    cnt_err += 1
                if protsess:
                    prot = round(progress_start + (progress_end - progress_start) * total / cnt_total)
                    if prot > protsess.edenemisprotsent:
                        protsess.edenemisprotsent = prot
                        model.Session.commit()                    

            model.Session.commit()
            if total:
                msg = _("Failist laaditi {n} sooritaja andmed. ").format(n=total)
                if cnt_exists:
                    msg += _("{n} registreeringut oli juba varem olemas. ").format(n=cnt_exists)
                if cnt_err:
                    msg += _("{n} sooritajat ei saanud registreerida, sest on samale testile juba registreeritud. ").format(n=cnt_err)
                if puuduvad_isikukoodid:
                    buf = ', '.join(puuduvad_isikukoodid)
                    cnt_p = len(puuduvad_isikukoodid)
                    msg += _("EHISest ei leitud {n} õpilast ({s}). ").format(n=cnt_p, s=buf)

                if protsess:
                    protsess.set_viga(msg)
                else:
                    self.notice(msg)

        liik = model.Arvutusprotsess.LIIK_REG
        tahised = [tk.tahised for tk in korrad]
        kirjeldus = 'Sooritajate registreerimine (%s)' % (', '.join(tahised))
        params = {'liik': liik,
                  'kirjeldus': kirjeldus,
                  'param': self.c.korrad_id}

        if len(korrad) == 1:
            tkord = korrad[0]
            params['testimiskord'] = tkord
            params['test'] = tkord.test
        model.Arvutusprotsess.start(self, params, childfunc, debug_p=True)
        self.success(_("Käivitatud on registreerimise protsess, mille käigus uuendatakse õppurite andmed EHISest"))
        

    def _split_to_lines(self, filename, value, errors):
        # faili sisu võimalused:
        # isikukood; epost; aadress; test_id; lang

        li_ik = []
        line_no = 0
        for line in value.splitlines():
            line_no += 1
            line = line.strip()
            if line:
                line = utils.guess_decode(line)
                li = [s.strip() for s in line.split(';')]
                ik = li[0]
                if not ik:
                    err = _("Isikukood puudub (rida {n})").format(n=line_no)
                    errors['ik_fail'] = err
                    break
                usp = eis.forms.validators.IsikukoodP(ik)
                if not usp.isikukood:
                    if filename.rsplit('.',1)[-1] in ('xlsx','xls'):
                        err = _("Palun kasutada CSV formaadis faili")
                    else:
                        err = _("Vigane isikukood (rida {n})").format(n=line_no)
                    errors['ik_fail'] = err
                    break
                li_ik.append((usp.isikukood, li))
        return li_ik, errors

    def _set_isikuandmed(self, kasutaja, muu, cols, testid_id):
        err = None
        test_id = lang = None
        for ind, col in enumerate(cols):
            if len(muu) <= ind:
                err = _("Real ei ole piisavalt veerge (isikukood {s})").format(s=kasutaja.isikukood)
                break
            value = muu[ind].strip()
            if not value:
                continue
            if col == 'epost':
                try:
                    validators.Email(strip=True, max=255).to_python(value)
                except formencode.api.Invalid as ex:
                    err = _("Vigane e-posti aadress {s}").format(s=value)
                    break
                else:
                    kasutaja.epost = value
            elif col == 'aadress':
                q = (model.Session.query(model.Aadress.id)
                     .filter(sa.func.to_tsvector('simple', model.Aadress.tais_aadress)
                             .op('@@')(sa.func.plainto_tsquery(value)))
                     .filter(model.Aadress.staatus==const.B_STAATUS_KEHTIV)
                     )
                aadress_id = None
                for a_id, in q.all():
                    if aadress_id:
                        err = _("Aadress pole täpne: {s}").format(s=value)
                        break
                    aadress_id = a_id
                if not aadress_id:
                    err = _("Aadressi ei leitud: {s}").format(s=value)
                    break
                kasutaja.aadress_id = aadress_id
            elif col == 'test_id':
                if not value:
                    err = _("Testi ID puudub")
                else:
                    try:
                        test_id = int(value)
                    except:
                        err = _("Vigane testi ID {s}").format(s=value)
                    else:
                        if test_id not in testid_id:
                            err = _("Failis on testi ID {test_id}, mille testimiskorda pole valitud").format(test_id=test_id)
            elif col == 'lang':
                keeled = [r[0] for r in self.c.opt.klread_kood('SOORKEEL')]
                if value in keeled:
                    lang = value
                else:
                    err = _("Soorituskeelte klassifikaatoris ei ole keelt {lang}").format(lang=value)
        if err:
            raise ValidationError(self, {}, err)                            
        return test_id, lang
    
    def _isikuregamine(self, ikline, cols, korrad, testid_id, tadata, muutmatu, valimis, protsess):
        isikukood, line = ikline
        muu = line[1:]
        cnt_exists = cnt_err = False
        kasutaja = model.Kasutaja.get_by_ik(isikukood)
        opilane = model.Opilane.get_by_ik(isikukood)
        if not kasutaja and opilane:
            kasutaja = opilane.give_kasutaja()
        if not kasutaja:
            return None, cnt_exists, cnt_err
        test_id, lang = self._set_isikuandmed(kasutaja, muu, cols, testid_id)
        # kui keel pole failis, siis kasutatakse vaikimisi õppekeelt
        if not lang and opilane:
            lang = opilane.lang
            
        if protsess:
            model.Kasutajaprotsess(kasutaja_id=kasutaja.id,
                                   arvutusprotsess_id=protsess.id)
        kasutaja_sooritajad = [] # tabeli ühe rea regamised
        for kord in korrad:
            if test_id and test_id != kord.test_id:
                # faili rida käib teise testi kohta
                continue
                
            klang = lang
            keeled = kord.get_keeled()
            if klang not in keeled:
                klang = keeled[0]

            err = sooritaja = None
            test = kord.test
            if test.testiliik_kood == const.TESTILIIK_RIIGIEKSAM:
                err = regpiirang.reg_r_lisaeksam(self, kasutaja.id, test, kord)
                if err:
                    self.error(err)

            if test.aine_kood == const.AINE_ET2:
                warn = regpiirang.reg_et2(self, kasutaja, test, opilane)
                if warn:
                    self.notice(warn)

            sooritaja = None
            if not err:
                # ei ole piiranguid
                added, sooritaja = self._append_sooritaja(kasutaja, klang, kord)
                if sooritaja:
                    if not added and sooritaja.staatus > const.S_STAATUS_REGAMATA:
                        # ei lisatud, sest oli varem olemas ja ei olnud tyhistatud
                        cnt_exists = True
                    sooritaja.muutmatu = muutmatu
                    sooritaja.valimis = valimis
                    for tos in sooritaja.sooritused:
                        ta_id = tos.toimumisaeg.id
                        _tadata = tadata[ta_id]
                        tos.reg_toimumispaev_id = _tadata['toimumispaev_id']
                        testikoht = _tadata['testikoht']
                        kell = _tadata['kell']
                        if testikoht:
                            testiruum = testikoht.give_testiruum(toimumispaev_id=tos.reg_toimumispaev_id)
                            if kell:
                                algus = datetime.combine(testiruum.algus, time(kell[0], kell[1]))
                            else:
                                algus = None
                            tos.suuna(testikoht, testiruum, algus=algus)
                else:
                    cnt_err = True
            kasutaja_sooritajad.append(sooritaja)
        return (kasutaja, kasutaja_sooritajad), cnt_exists, cnt_err

    def _append_sooritaja(self, kasutaja, lang, kord):
        """Lisatakse sooritaja või muudetakse olemasolevat.
        """
        test_id = kord.test_id
        piirkond_id = None
        esitaja_kasutaja_id=self.c.user.id
        esitaja_koht_id = const.KOHT_EKK

        return model.Sooritaja.registreeri(kasutaja, 
                                           test_id, 
                                           kord, 
                                           lang, 
                                           piirkond_id, 
                                           const.REGVIIS_EKK,
                                           esitaja_kasutaja_id, 
                                           esitaja_koht_id)

    def _get_kasutaja_rr(self, isikukood):
        """Küsitakse RR-ist nende isikute andmeid, keda EHISes ei olnud.
        Lisatakse kasutajateks ja tagastatakse kasutajate list.
        """

    def _tyhista(self, li_ik, korrad_id, korrad, pohjus):
        cnt = 0
        rows = []
        for isikukood, line in li_ik:
            kasutaja = model.Kasutaja.get_by_ik(isikukood)
            if kasutaja:
                kasutaja_sooritajad = [] # tabeli ühe rea regamised
                for kord_id in korrad_id:
                    q = (model.Sooritaja.query
                         .filter(model.Sooritaja.kasutaja_id==kasutaja.id)
                         .filter(model.Sooritaja.testimiskord_id==kord_id))
                    sooritaja = q.first()
                    if sooritaja:
                        if sooritaja.staatus in (const.S_STAATUS_REGAMATA,
                                                 const.S_STAATUS_TASUMATA,
                                                 const.S_STAATUS_REGATUD,
                                                 const.S_STAATUS_ALUSTAMATA):
                            sooritaja.logi_pohjus = pohjus
                            kt.send_tyhteade(self, kasutaja, sooritaja)
                            sooritaja.tyhista()
                            cnt += 1
                    kasutaja_sooritajad.append(sooritaja)                        
                rows.append((kasutaja, kasutaja_sooritajad))

        model.Session.commit()
        if not cnt:
            raise ValidationError(self, {}, _("Ei leitud ühtki registreeringut"))
        else:
            msg = _("Tühistatud {n} registreeringut").format(n=cnt)
            self.notice(msg)
            self.c.rows = rows
            self.c.korrad = korrad
            self.c.tyhistatud = True
            return self.render_to_response('ekk/regamine/nimistu.lisavalikud.mako')   

    def _error_create(self):
        html = self.form.render(self._EDIT_TEMPLATE, extra_info=self.response_dict)
        return Response(html)

    def __before__(self):
        self.c.korrad_id = self.request.matchdict.get('korrad_id')
        korrad_id = self.c.korrad_id.split('-')        
        self.c.korrad = [model.Testimiskord.get(kord_id) for kord_id in korrad_id]        
        
