from datetime import datetime, timedelta
import re
from eis.lib.xtee.xroad import *
import logging
log = logging.getLogger(__name__)

import eiscore.const as const

class Rahvastikuregister(XroadClientEIS):
    """Rahvastikuregistri teenuste kasutamine
    """
    producer = 'rr'
    namespace = 'http://rr.x-road.eu/producer'

    def __init__(self, **kw):
        XroadClientEIS.__init__(self, **kw)
        if self.handler and self.handler.is_test:
            # test-RR ei luba kõigil päringuid teha
            self.set_test_user()
            
    def set_test_user(self):
        ## RR testisik, kellel RR lubab päringuid teha
        self.userId = 'EE48212080019'
        
    def rr404_synnikoht(self, isikukood):
        "Sünnikohta väljastav teenus"
        request = E.request(E.valjad('18'), # 18 - synnikoht
                            E.isikukoodid(isikukood),
                            E.eesnimed(''),
                            E.perenimed(''))
        list_path = ['/response/isikud/isik']
        res = self.call('RR404_isik.v4', E.Request(request), list_path, timeout=10)
        response = res['response']
        synnikoht = None
        error = response.faultString
        if not error:
            try:
                synnikoht = response.isikud.isik[0].synnikoht
            except:
                pass
        return error, synnikoht

    def pohiandmed_ik(self, isikukood):
        "Põhiandmete teenus"
        request = E.request(E.Isikukood(isikukood))
        list_path = []
        res = self.call('RR66HMIsikEestk.v3', E.Request(request), list_path, timeout=10)
        return res

    def pohiandmed_ik_data(self, isikukood):
        message = None
        data = None

        isikukoodid, bad = validate_isikukoodid([isikukood])
        if bad:
            err = "Esitati vigane isikukood {s}".format(s=isikukood)
            return err, None
        if not isikukoodid:
            # välismaa isikukood
            err = "Välisriigi isikukoodiga ei saa Rahvastikuregistrist andmeid pärida"
            return err, None
        try:
            res = self.pohiandmed_ik(isikukood)
        except SoapFault as e:
            if e.faultcode == 'V10580':
                # Kasutajal pole kehtivat isikukoodi RR-is või vale masinkonto.
                message = 'Kasutaja isikukood ei ole Rahvastikuregistri andmetel kehtiv'
            else:
                message = 'Rahvastikuregistri päring ebaõnnestus'
            return message, None
        
        try:
            message = res.find('response/veatekst')
            keha = res.response
            if not message and keha and keha.Isikupnimi:
                data = {}
                data['eesnimi'] = keha.Isikuenimi
                data['perenimi'] = keha.Isikupnimi
                data['kodakond_kood'] = keha.KodakondsusKood
                data['ADS_ADR_ID'] = keha.ADS_ADR_ID
            else:
                message = 'Rahvastikuregistris pole isikukoodiga %s isiku andmeid' % (isikukood)

        except Exception as e:
            message = 'Rahvastikuregistri päring ebaõnnestus. '
            if self.handler:
                message = self.handler._error(e, message)

        return message, data

    def set_rr66(self, data, kasutaja, isikukood=None, muuda=False): 
        import eis.model as model
        if kasutaja is None:
            kasutaja = model.Kasutaja.add_kasutaja(isikukood, data['eesnimi'], data['perenimi'])
        else:
            if not kasutaja.is_writable:
                kasutaja = model.Kasutaja.get(kasutaja.id)
        
            kasutaja.isikukood = isikukood
            if not kasutaja.eesnimi or not kasutaja.perenimi or \
              data['eesnimi'].lower() != kasutaja.eesnimi.lower() or \
              data['perenimi'].lower() != kasutaja.perenimi.lower():
                kasutaja.set_kehtiv_nimi(data['eesnimi'], data['perenimi'])
        if not kasutaja.synnikpv or not kasutaja.sugu:
            # määratakse synnikpv ja sugu
            obj = validators.IsikukoodEE(isikukood)
            if obj.parse():
                kasutaja.synnikpv = obj.birthdate
                kasutaja.sugu = obj.sex
        kasutaja.kodakond_kood = data['kodakond_kood']
        if not kasutaja.aadress_id or muuda:
            adr_id = data.get('ADS_ADR_ID')
            if adr_id:
                aadress = model.Aadress.get(adr_id)
                if aadress:
                    kasutaja.aadress_id = adr_id
                    kasutaja.normimata = None
        kasutaja.rr_seisuga = datetime.now()
        return kasutaja
    
def rr_pohiandmed(handler, isikukood):
    
    reg = Rahvastikuregister(handler=handler)
    message, data = reg.pohiandmed_ik_data(isikukood)
    return message, data

def rr_pohiandmed_js(handler, isikukood):
    """AJAXiga käivitatud päring, mille tulemused ei lähe koha andmebaasi,
    vaid ekraanivormile.
    """
    import eis.model as model
    message, data = rr_pohiandmed(handler, isikukood)
    if message:
        res = {'error': message}
    else:
        res = model.Aadresskomponent.get_komp_from_rr(data)
    return res

def set_rr_pohiandmed(handler, kasutaja, isikukood=None, muuda=False, reg=None, showerr=True): 
    """Päritakse kasutaja andmed ja muudetakse kasutaja kirjet.
    Kui kasutaja kirjet veel ei ole, aga andmed tulevad, siis luuakse kirje.
    """
    if not reg:
        reg = Rahvastikuregister(handler=handler)

    isikukood = isikukood or kasutaja and kasutaja.isikukood or None
    if reg.is_pseudo(isikukood) or not is_isikukood_ee(isikukood):
        return kasutaja
    message, data = reg.pohiandmed_ik_data(isikukood)
    if message and showerr:
        handler.error(message)
    elif data:
        return reg.set_rr66(data, kasutaja, isikukood=isikukood, muuda=muuda)
        
def uuenda_rr_pohiandmed(handler, kasutaja, isikukood=None, force=False, showerr=True):
    """Uuendatakse isiku andmed RRis, kui pole hiljuti uuendanud
    is404 - kas on vaja sünnikohta väljastavat päringut (RR404_isik)
    """
    rc = None
    if not handler.request.is_ext() or kasutaja and not kasutaja.isikukood_ee:    
        return
    need_update = force or not kasutaja or not kasutaja.rr_seisuga
    if not need_update:
        settings = handler.request.registry.settings
        cache_hours = float(settings.get('rr.cache.nimi',4380))
        if cache_hours != -1:
            seisuga = datetime.now() - timedelta(hours=cache_hours)
            need_update = kasutaja.rr_seisuga < seisuga
    if need_update:
        # põhiandmed vaja uuendada
        set_rr_pohiandmed(handler, kasutaja, isikukood, muuda=True, showerr=showerr)
        # andmed uuendatud
        return True

def anna_synnikoht(handler, kasutaja):
    if not handler.request.is_ext() or (not kasutaja.isikukood_ee or kasutaja.synnikoht):
        return
    reg = Rahvastikuregister(handler=handler)
    isikukood = kasutaja.isikukood
    if reg.is_pseudo(isikukood):
        return
    error, synnikoht = reg.rr404_synnikoht(kasutaja.isikukood)
    if synnikoht:
        kasutaja.synnikoht = synnikoht
        return True

def vrd_rr_nimi(handler, kasutaja, eesnimi, perenimi):
    """Kui muust allikast tuleb isikule teistsugune nimi kui on EISi andmebaasis,
    siis teeme igaks juhuks päringu RRi, et vajadusel nimi uuendada
    """
    if not handler.request.is_ext() or not kasutaja.isikukood_ee:
        # ei ole Eesti isikukoodi, ei saa andmeid pärida
        return
    need_update = not kasutaja.rr_seisuga
    if not need_update and eesnimi and perenimi:
        # kas nimi erineb?
        k_eesnimi = kasutaja.eesnimi
        k_perenimi = kasutaja.perenimi
        need_update = k_eesnimi.lower() != eesnimi.lower() or k_perenimi.lower() != perenimi.lower()
    return uuenda_rr_pohiandmed(handler, kasutaja, force=need_update, showerr=False)

def is_isikukood_ee(ik):
    return ik and len(ik) == 11 and not re.match(r'[A-Z]{2}', ik)

def _int(node):
    s = str(node)
    if s:
        return int(s)

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG)
    log = logging.getLogger()
    from eis.scripts.scriptuser import *
    ik = 'xxxxxx'
    ik = '49012070019'
    reg = Rahvastikuregister(settings=registry.settings)
    reg.set_test_user()
    try:
        print(reg.rr404_synnikoht(ik))
        #print(reg.pohiandmed_ik_data(ik))
        #print(reg.allowedMethods())
    except SoapFault as e:
        print(e.faultstring)
        raise
