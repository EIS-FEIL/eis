"""
EHISe X-tee teenused
EHISe WSDL vt https://x-tee.ee/catalogue-data/ee-test/ee-test/GOV/70000740/ehis/59.wsdl
"""

import requests
from datetime import datetime, timedelta
from eis.lib.xtee.xroad import *
import eis.model as model
import sqlalchemy as sa
import json
import logging
log = logging.getLogger(__name__)

class Ehis(XroadClientEIS):
    producer = 'ehis'
    namespace = 'http://producers.ehis.xtee.riik.ee/producer/ehis'

    def on_fault(self, e, service_name):
        if isinstance(e, SoapFault):
            msg = e.faultstring
            if service_name == 'oppurid':
                # EHISe õppurite päring väljatab tehnilise veateate, kui klass ei sobi
                # seda ei peaks kohtlema tehnilise veana
                if msg and msg.startswith('Kutsekoolil puudub klass'):
                    raise SoapFault(None, msg)
            elif service_name == 'eeIsikukaart':
                # isiku puudumist ei peaks kohtlema tehnilise veana
                if msg == 'Isiku kohta andmeid ei leitud.':
                    raise SoapFault(None, msg)
            elif service_name == 'pedagoogAmetikohtV2':
                # EHISe õppeaine klassifikaatori avaandmed ja tegelikkus pole kooskõlas
                if msg.startswith('Classification with such code does not exist!'):
                    raise SoapFault(None, msg)
                
        try:
            XroadClientEIS.on_fault(self, e, service_name)
        except SoapFault:
            err = 'Meil ei õnnestu hetkel EHISest andmeid pärida.'
            try:
                if e.faultcode.startswith('Server.ServerProxy'):
                    err = 'EHIS ei ole hetkel töökorras ja meil ei õnnestu EHISest andmeid pärida.'
            except:
                pass
            raise SoapFault(None, err)

    def oppeasutused(self):
        list_path = ['/oppeasutused/oppeasutus',
                     '/oppeasutused/oppeasutus/oppetasemed/oppetase',
                     '/oppeasutused/oppeasutus/oppekeeled/oppekeel'
                     ]
        try:
            res = self.call('eisOppeasutused', E.Request(''), list_path)
            if res:
                li = res.find('oppeasutused/oppeasutus')
                return None, li
        except SoapFault as e:
            #return u'EHISe õppeasutuste päring ei toimi', []
            return e.faultstring, []
        return None, []

    def ametikohad(self, isikukoodid):
        return self.pedagoogAmetikoht(isikukoodid, None, None, None)
    
    def pedagoogAmetikoht(self, isikukoodid, koolId, kooliaste, oppeaine):
        request = E.Request()
        if isikukoodid:
            check_digit = self.settings.get('%s.check_digit' % self.producer, 'true') == 'true'
            isikukoodid, bad = validate_isikukoodid(isikukoodid, check_digit)
            if bad:
                err = "Esitati vigane isikukood: {s}".format(s=', '.join(bad))
                return err, None
            if not isikukoodid:
                # kõik olid välismaa isikukoodid
                return None, []
            param = E.isikukoodid()
            for isikukood in isikukoodid:
                param.append(E.isikukood(isikukood))
            request.append(param)
        if koolId:
            request.append(E.koolId(koolId))
        if kooliaste:
            request.append(E.kooliaste(kooliaste))
        if oppeaine:
            request.append(E.oppeaine(oppeaine))
        list_path = ['/ametikohad/ametikoht',
                     '/ametikohad/ametikoht/oppeained/oppeaine',
                     '/ametikohad/ametikoht/oppeained/oppeaine/kooliaste']
        try:
            res = self.call('pedagoogAmetikohtV2', request, list_path=list_path)
        except SoapFault as e:
            return e.faultstring, []
        else:
            if res:
                li = res.find('ametikohad/ametikoht') or []
                # isikukood
                # eesnimi
                # perenimi
                # koolId
                # koolijuht
                # oppeained/oppeaine/kood
                # oppeained/oppeaine/kooliaste
                return None, li
        return None, []

    def oppurid_ik(self, isikukoodid):
        check_digit = self.settings.get('%s.check_digit' % self.producer, 'true') == 'true'
        isikukoodid, bad = validate_isikukoodid(isikukoodid, check_digit)
        if bad:
            err = "Esitati vigane isikukood: {s}".format(s=', '.join(bad))
            return err, None
        if not isikukoodid:
            # kõik olid välismaa isikukoodid
            return None, []
        return self._oppurid(isikukoodid=isikukoodid)

    def oppurid_kool(self, kool_id, klass, paralleel=None):
        if not kool_id:
            return 'Kool puudub', None
        return self._oppurid(kool_id=kool_id, klass=klass, paralleel=paralleel)
    
    def _oppurid(self, isikukoodid=None, kool_id=None, klass=None, paralleel=None):
        is_ES2739 = self.handler and not self.handler.is_live
        oppurid = E.oppurid()
        if isikukoodid:
            for isikukood in isikukoodid:
                oppurid.append(E.isikukood(isikukood))
        else:
            elem = E.oppeasutus(E.koolId(kool_id))
            elem.append(E.klassKursus(klass or ''))
            if paralleel:
                elem.append(E.paralleeliTunnus(paralleel.upper()))
            oppurid.append(elem)
            if is_ES2739:
                oppurid.append(E.onLopetanud(False)) # ES-2739

        list_path = ['/oppimised/oppimine']
        try:
            # ES-2739
            if is_ES2739:
                res = self.call('oppuridV2', E.Request(oppurid), list_path=list_path, service_version='v2')
            else:
                res = self.call('oppurid', E.Request(oppurid), list_path=list_path)
        except SoapFault as e:
            msg = e.faultstring
            if msg.startswith('Kutsekoolil puudub klass'):
                # pole tegelikult tehniline viga
                return None, []
            return msg, []
        else:
            if res:
                li = res.find('oppimised/oppimine') or []
                # str(rcd.isikukood)
                # bool(rcd.on_lopetanud) onLopetanud
                # unicode(rcd.eesnimi)
                # unicode(rcd.perenimi)
                # int(rcd.kool_id) koolId
                # unicode(rcd.klass_kursus) klassKursus
                # unicode(rcd.paralleeli_tunnus) paralleeliTunnus
                # unicode(rcd.oppekeel)
                # str(rcd.lopet_aasta) - int none lopetAasta
                # unicode(rcd.tunnistus_nr) tunnistusNr
                # date(rcd.tunnistus_kp) tunnistusKp
                return None, li
        return None, []

    def klassifikaatorid(self, ehis_kl_kood):
        # http://enda.ehis.ee/avaandmed/rest/klassifikaatorid/OPPEAINE/1/JSON
        # 1 - ainult kehtivad
        url = f'http://enda.ehis.ee/avaandmed/rest/klassifikaatorid/{ehis_kl_kood}/1/JSON'
        log.debug(f'GET {url}')
        http_proxy = self.settings.get('http_proxy')
        try:
            if http_proxy:
                resp = requests.get(url=url, proxies={'http': http_proxy})
            else:
                resp = requests.get(url=url)
            data = resp.json()
            kl = data['body']['klassifikaatorid']['klassifikaator']
            elemendid = kl[0]['elemendid']['element']
            # nimetus, kood, kehtiv
            return elemendid, None
        except Exception as ex:
            err = 'EHISest avaandmete saamise viga'
            if self.handler:
                self.handler._error(ex)
            return None, err

    def upd_klassifikaator(self, kl_kood):
        "EHISe klassifikaatori puhvri uuendamine"
        cache_hours = int(self.settings.get('ehis.cache.klass',10))        
        now = datetime.now()
        seisuga = now - timedelta(hours=cache_hours)
        ehis_koodid = {'EHIS_AINE': 'OPPEAINE',
                       'EHIS_ASTE': 'klassi_aste',
                       }
        kl = model.Klassifikaator.get(kl_kood)
        if not kl.seisuga or kl.seisuga < seisuga:
            ehis_kl_kood = ehis_koodid[kl_kood]
            elemendid, err = self.klassifikaatorid(ehis_kl_kood)
            if err:
                return err
            elif elemendid:
                items = {r.kood: r for r in kl.read}
                for elem in elemendid:
                    kood = elem['kood']
                    nimi = elem['nimetus']
                    try:
                        # kas on juba olemas
                        item = items.pop(kood)
                    except KeyError:
                        # uue väärtuse lisamine
                        item = model.Klrida(kood=kood,
                                            nimi=nimi,
                                            kehtib=True,
                                            alates=now)
                        kl.read.append(item)
                    else:
                        # olemasoleva väärtuse uuendamine
                        item.nimi = nimi
                        item.kehtib = True
                # kadunud väärtuste tühistamine
                for item in items.values():
                    item.kuni = now
                    item.kehtib = False
                kl.seisuga = now
                model.Session.flush()

    def isikukaart(self, isikukood):
        "Isikukaardi päring töötamise andmete saamiseks"
        # https://projektid.edu.ee/pages/viewpage.action?pageId=118489668
        list_path = ['/isikukaart/gdprlog',
                     '/isikukaart/oping',
                     '/isikukaart/tootamine',
                     '/isikukaart/taiendkoolitus',
                     '/isikukaart/tasemeharidus',
                     '/isikukaart/kvalifikatsioon',
                     '/isikukaart/valiskvalifikatsioon',
                     '/isikukaart/tootamine/oppekava',
                     '/isikukaart/tootamine/oppeaine',
                     ]
        try:
            request = E.Request(E.isikukood(isikukood),
                                E.format('xml'),
                                E.andmeplokk('TOOTAMINE_HUVI_KEHTIV'),
                                E.andmeplokk('TOOTAMINE_ALUS_KEHTIV'),
                                E.andmeplokk('TOOTAMINE_POHI_KEHTIV'),
                                E.andmeplokk('TOOTAMINE_KUTSE_KEHTIV'),
                                E.andmeplokk('TOOTAMINE_KORG_KEHTIV'))
            res = self.call('eeIsikukaart', request, list_path)
            if res:
                #li = res.find('isikukaart')
                return None, res
        except SoapFault as e:
            msg = e.faultstring
            if msg != 'Isiku kohta andmeid ei leitud.':
                # on päris viga
                return msg, None
        return None, None
                
def uuenda_opilased(handler, koik_isikukoodid, protsess=None, progress_end=None, force=False):
    """Uuendatakse nende õpilaste kirjed EHISest, kelle andmed pole värsked
       Tagastab veateate, kui EHISe päring ebaõnnestub
    """
    def _uuenda(reg, isikukoodid):
        # teeme EHISe päringu
        message, oppimised = reg.oppurid_ik(isikukoodid)
        if message:
            return message
        else:
            model.Opilane.update_opilased(oppimised, isikukoodid)

    if not handler.request.is_ext():
        return
    reg = Ehis(handler=handler)
    cache_hours = float(handler.request.registry.settings.get('ehis.cache.opilane',1))
    if force or cache_hours != -1:
        if force:
            # uuendame kõik õpilased
            isikukoodid = koik_isikukoodid
        else:
            # leiame õpilased, keda pole ammu uuendatud
            seisuga = datetime.now() - timedelta(hours=cache_hours)
            q = (model.SessionR.query(model.Kasutaja.isikukood)
                 .filter(model.Kasutaja.isikukood.in_(koik_isikukoodid))
                 .filter(model.Kasutaja.opilane_seisuga>=seisuga)
                 )
            varsked = [ik for ik, in q.all()]
            # jätame alles need, keda on vaja kontrollida
            isikukoodid = [ik for ik in koik_isikukoodid if ik not in varsked]

        # jätame välja välismaa isikukoodid
        isikukoodid = [ik for ik in isikukoodid if model.Kasutaja.is_isikukood_ee(ik)]
        
        total = len(isikukoodid)
        cnt_done = 0
        if protsess:
            progress_start = protsess.edenemisprotsent
            
        # teeme EHISe päringud 500 kaupa
        MAX_COUNT = 500
        def create_chunks(li, n):
            for i in range(0, len(li), n):
                yield li[i:i + n]
        for chunk in create_chunks(isikukoodid, MAX_COUNT):
            err = _uuenda(reg, chunk)
            if err:
                return err
            if protsess:
                cnt_done += len(chunk)
                prot = progress_start + (progress_end - progress_start) * cnt_done / total
                protsess.edenemisprotsent = prot
                model.Session.commit()
    model.Session.flush()

def uuenda_isikukaart(handler, kasutaja):
    """Uuendatakse kasutaja töötamise andmed, kui ei ole värskelt uuendatud
    """
    def add_kaart(isikukood, isikukaart):
        if not isikukaart:
            # isikukaarti EHISes ei ole
            return
        tootamised = isikukaart.find('isikukaart/tootamine') or []
        tootamised = [r for r in tootamised if r.kehtiv]
        if not tootamised:
            # isikukaart on EHISes, aga kehtivad töötamisi ei ole
            return
            
        # salvestame isikukaardi töötamise andmed EISis
        item = model.Isikukaart(isikukood=isikukood,
                                data=json.dumps(isikukaart.asdict()))
        for tootamine in tootamised:
            rcd = model.Isikukaart_too(isikukaart=item,
                                       liik=tootamine.liik,
                                       oppeasutus=tootamine.oppeasutus,
                                       oppeasutus_id=none_int(tootamine.oppeasutusId),
                                       ametikoht=tootamine.ametikoht,
                                       ametikoht_algus=none_date(tootamine.ametikohtAlgus),
                                       ametikoht_lopp=none_date(tootamine.ametikohtLopp),
                                       on_tunniandja=none_int(tootamine.onTunniandja),
                                       on_oppejoud=none_int(tootamine.onOppejoud),
                                       taitmise_viis=tootamine.taitmiseViis,
                                       ametikoht_koormus=none_float(tootamine.ametikohtKoormus),
                                       tooleping=tootamine.tooleping,
                                       ametikoht_kval_vastavus=tootamine.ametikohtKvalVastavus,
                                       ametijark=tootamine.ametijark,
                                       haridustase=tootamine.haridustase,
                                       lapsehooldus_puhkus=none_boolean(tootamine.lapsehooldusPuhkus))
            for oppekava in tootamine.oppekava or []:
                rcd1 = model.Isikukaart_too_oppekava(isikukaart_too=rcd,
                                                    kl_oppekava=oppekava.klOppekava,
                                                    oppekava_kood=oppekava.oppekavaKood,
                                                    oppekava_nimetus=oppekava.oppekavaNimetus,
                                                    kvalifikatsiooni_vastavus=oppekava.kvalifikatsiooniVastavus,
                                                    akad_kraad=oppekava.akadKraad,
                                                    kval_dokument=oppekava.kvalDokument)
            for oppeaine in tootamine.oppeaine or []:
                rcd1 = model.Isikukaart_too_oppeaine(isikukaart_too=rcd,
                                                     oppeaine=oppeaine.oppeaine,
                                                     kooliaste=oppeaine.kooliaste,
                                                     maht=none_float(oppeaine.maht),
                                                     kval_vastavus=oppeaine.kval_vastavus)
        model.Session.flush()
        return item.id
        
    if not handler.request.is_ext():
        return None
    isikukood = kasutaja.isikukood
    if not isikukood or not model.Kasutaja.is_isikukood_ee(isikukood):
        return None

    now = datetime.now()
    if kasutaja.isikukaart_seisuga:
        # kunagi varem on isikukaarti päritud
        cache_hours = float(handler.request.registry.settings.get('ehis.cache.ametikoht',1))
        if cache_hours == -1:
            # ei uuenda isikukaarte
            return None
        seisuga = now - timedelta(hours=cache_hours)
        if kasutaja.isikukaart_seisuga > seisuga:
            # on piisavalt värske isikukaart
            return None

    # teeme uue päringu
    reg = Ehis(handler=handler)
    message, isikukaart = reg.isikukaart(isikukood)
    if message:
        # ei saanud pärida
        return message

    # päring õnnestus, salvestame isikukaardi või selle puudumise
    kasutaja.isikukaart_seisuga = now
    kasutaja.isikukaart_id = add_kaart(isikukood, isikukaart)
    model.Session.commit()
    
if __name__ == '__main__':
    import pprint
    import logging
    logging.basicConfig(level=logging.DEBUG)
    log = logging.getLogger()

    from eis.scripts.scriptuser import *
    userId = 'EE30101010007'
    reg = Ehis(settings=registry.settings, userId=userId)

    if 0:
        res = reg.allowedMethods()
        pprint.pprint(res)

        ik = '37705132318'
        ik = '37311186013'
        err, data = reg.isikukaart(ik)
        pprint.pprint(data)
        #res = reg.klassifikaatorid('OPPEAINE')
        #pprint.pprint(res)
        #res = reg.klassifikaatorid('klassi_aste')
        #pprint.pprint(res)    
    if 1:
        koolId = None
        kooliaste = 'CLASS_STEP_13'
        oppeaine = None
        res = reg.pedagoogAmetikoht(None, koolId, kooliaste, oppeaine)
        print(res)
        print(f'{len(res[1])} isikut')
    if 0:
        res = reg.getWsdl('oppuridV2', 'v2')
        pprint.pprint(res)
        
    if 0:
        res = reg.ametikohad(['30101010007'])
        print(res)
    if 0:
        ik = '30101010007'
        ik = '38509072577'
        res = reg.oppurid_ik([ik])
        print(res)
    if 0:
        res = reg.oppurid_kool('1471', 'NA')
        print(res)

    if 0:
        err, oppurid = reg.oppurid_kool('782', 1)
        if err:
            print(err)
        # kontrollime tulemuse klassid ja ryhmad
        mk = {}
        for r in oppurid:
            key = r.klassKursus or r.ryhmNimetus
            mk[key] = (mk.get(key) or 0) + 1
        for key, cnt in mk.items():
            print(f' {key} - {cnt} tk')
            
        # Kutsekoolil puudub klass: G1
        res = reg.oppurid_kool('86', 'G1')
        print(res)
        
