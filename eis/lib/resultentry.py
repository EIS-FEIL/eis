"""Ülesannete hindepallide ja vastuste sisestamise funktsioonid,
mida kasutatakse e-hindamisel ja p-hinnete või p-vastuste sisestamisel.
"""
import random
from eiscore.examwrapper import MemYlesandevastus, MemKV, MemKS
from eis.lib.base import *
from eis.lib.blockcalc import BlockCalc
from eis.lib.blockentry import BlockEntry
from eis.lib.blockresponse import BlockResponse
from eis.lib.helpers import fstr
from eis.lib.npcalc import Npcalc
log = logging.getLogger(__name__)
_ = i18n._

class ResultEntry(object):
    
    def __init__(self, handler, sisestusviis, test, testiosa, on_jagatudtoo=False):
        self.handler = handler
        if handler:
            self.c = handler.c
            self.user = handler.c.user
            self.request = handler.request
        else:
            self.user = model.usersession.get_user()

        self.sisestusviis = sisestusviis # kui on None, siis kasutatakse ty.sisestusviisi
        self.on_jagatudtoo = test.testityyp == const.TESTITYYP_TOO
        self.error_lopeta = None # lõpetamist takistava vea teade, mis pole seotud konkreetse väljaga
        self.errors = {} # väljade veateated, mis takistavad salvestamist
        self.warnings = {} # väljade hoiatused, mis ei takista salvestamist

        self.sisestuserinevus = False # kas on erinevusi teise sisestusega
        self.molemad = True # kas mõlemad sisestused on sisestatud

        self.ekspert_labivaatus = False # kas toimub vaide korral eksperdi poolt läbivaatamine
        self.ekspert_ettepanek = False # kas toimub vaide korral ettepaneku salvestamine
        # muudel juhtudel toimub hinnete salvestamine

        # läbiviijad, kelle kirjed just lõime negatiivsetest id-dest
        self.neg_labiviijad = list()
        self.on_diagnoosiv = False # kas on diagnoosiv test
        self.on_hindamiskogumita = False # kas on testimiskorrata ja hindamiskogumita hindamine
        self.testiosa = testiosa
        self.test = test
        
    def save_sisestamine(self, sooritaja, rcd, lopeta, prefix, tos, holek, testiosa, hindamine, komplekt, soorituskomplekt, compare2, is_update_sooritus=True):
        """Hinnete või vastuste sisestamine eksamikeskuses.
        """
        # kutsub ekk/sisestamine/vastused.py
        # kutsub ekk/sisestamine/suulisedhindamised.py

        if not self._save_labiviijad(sooritaja, tos, hindamine, rcd, prefix, lopeta, holek):
            return

        # salvestatakse komplekti valik (väljadele hindamine.komplekt ja holek.komplekt)
        self._save_komplekt(hindamine, komplekt, soorituskomplekt, holek, tos)
        
        # leitakse teise sisestamise kirje ja kas läbiviijad või komplekt erineb
        if compare2:
            hindamine2, sisestuserinevus = self._get_hindamine2(holek, hindamine, prefix)
        else:
            hindamine2, sisestuserinevus = None, False
            
        # hinnete salvestamine
        self.save_hindamine(sooritaja, rcd, lopeta, prefix, tos, holek, testiosa, hindamine, hindamine2, sisestuserinevus, is_update_sooritus=is_update_sooritus)

    def save_hindamine(self, sooritaja, rcd, lopeta, prefix, tos, holek, testiosa, hindamine, hindamine2, sisestuserinevus, ty_id=None, is_update_sooritus=True, del_old=True):
        """Ühe soorituse ühe hindamiskogumi ühe hindaja hinnete salvestamine.
        """
        # kutsub avalik/shindamine/hindamised
        # kutsub avalik/khindamine/hindamised
        # kutsub ekk/hindamine/eksperthindamised
        yhinded = []
        pallid = 0
        sisestamata = None
        komplekt_id = None
        komplekt = hindamine.komplekt
        hindamiskogum = model.Hindamiskogum.get(holek.hindamiskogum_id)
        on_kriteeriumid = hindamiskogum.on_kriteeriumid
        if on_kriteeriumid:
            # hindamiskogumi kõigi ylesannete koos hindamine kriteeriumite kaupa
            kr_pallid, kr_sisestamata = \
                self._save_kr(hindamiskogum, rcd, tos, testiosa, hindamine, hindamine2, lopeta, prefix)
            pallid += kr_pallid or 0
            if sisestamata is None or kr_sisestamata:
                sisestamata = kr_sisestamata
            if sisestamata is None:
                # ei olnud midagi hinnata
                sisestamata = False
                
        elif komplekt:
            # hindamine ylesannete kaupa
            # komplekt on määratud ja saab hindeid salvestada
            komplekt_id = komplekt.id
            yhinded_ty_id = []
            for n1, rcd_ty in enumerate(rcd.get('ty')):        
                # iga testiylesande kohta
                ty_prefix = (prefix and '%s.' % prefix) + 'ty-%d' % (n1)
                ty_hinded, ty_pallid, ty_eri, ty_sisestamata = \
                    self._save_ty(sooritaja, rcd_ty, tos, testiosa, hindamine, hindamine2, lopeta, ty_prefix)
                yhinded.extend(ty_hinded)
                yhinded_ty_id.append(rcd_ty['ty_id'])
                pallid += ty_pallid or 0
                sisestuserinevus |= ty_eri
                if sisestamata is None or ty_sisestamata:
                    sisestamata = ty_sisestamata

            # otsime ylesandehinded nende testiylesannete kohta, mida praegu ei salvestatud
            for vy in komplekt.valitudylesanded:
                if vy.testiylesanne_id not in yhinded_ty_id:
                    yhinne = hindamine.get_vy_ylesandehinne(vy.id)
                    if yhinne and yhinne.pallid == 0:
                        # kui on hinne olemas ja 0p, siis säästame kustutamisest
                        # kuna see on tyhja vastuse eest automaatselt antud 0p
                        yhinded.append(yhinne)
            if sisestamata is None:
                # ei olnud midagi hinnata (sooritaja ei vastanud ja sai automaatselt 0p)
                sisestamata = False

        else:
            # kui komplekti ei ole, siis ei saa hindeid salvestada, 
            # sest pole teada, millise ylesande hinded need on
            pallid = None
            sisestamata = True

        if del_old:
            # kustutame varem salvestatud hinded, mida enam ei ole
            # (kui pole antud ty_id, siis sisestati korraga kõigi ülesannete vastused;
            # kui on antud ty_id, siis sisestati ainult selle ylesande vastused)
            for hinne in hindamine.ylesandehinded:
                if hinne not in yhinded:
                    if not ty_id or hinne.valitudylesanne.testiylesanne_id==ty_id:
                        hinne.delete()
            if not on_kriteeriumid:
                for hinne in hindamine.kriteeriumihinded:
                    hinne.delete()
        if ty_id:
            # vaide ettepaneku sisestamisel sisestatakse yhe ylesande kaupa
            # hindamiskogumi kogupallide saamiseks liidame selle ylesande pallidele
            # juurde teiste eksperdi poolt hinnatud ylesannete pallid
            # ja eksperdi poolt hindamata jäetud ylesannete kehtivad pallid
            pallid = 0
            for ty in hindamiskogum.testiylesanded:
                yv = ExamSaga(self.handler).sooritus_get_ylesandevastus(tos, ty.id, komplekt_id)
                if yv:
                    yhinne = hindamine.get_ylesandehinne(yv)
                    if yhinne:
                        # ekspert on hinnanud
                        self._calc_hindamine_yhinne(sooritaja, tos, yhinne, hindamine.liik, testiosa)
                        pallid += yhinne.pallid or 0
                    else:
                        # ekspert pole hinnanud, jõus on kehtiv hinne
                        pallid += yv.pallid or 0

        hindamine.pallid = pallid
        hindamine.sisestuserinevus = sisestuserinevus
        if hindamine2:
            hindamine2.sisestuserinevus = sisestuserinevus
        
        # kui on sisestamata, siis salvestame selle hindamise kirje juures:
        hindamine.sisestatud = sisestamata == False
        if sisestamata and lopeta:
            self.error_lopeta = _("Ei saa kinnitada, sest kõik pole veel sisestatud")

        if not sisestamata and lopeta:
            hindamine.staatus = const.H_STAATUS_HINNATUD
        else:
            hindamine.staatus = const.H_STAATUS_POOLELI

        model.Session.flush()
        self.update_hindamisolek(sooritaja, tos, holek, False, is_update_sooritus)

    def save_ty_hindamine(self, sooritaja, rcd, lopeta, prefix, tos, holek, testiosa, hindamine, hindamine2, sisestuserinevus, ty_id=None, is_update_sooritus=True):
        """Ühe soorituse ühe hindamiskogumi ühe hindaja hinnete salvestamine.
        """
        yhinded = []
        pallid = 0
        sisestamata = None
        sisestamata_tahised = []
        komplekt_id = None
        komplekt = hindamine.komplekt
        hindamiskogum = model.Hindamiskogum.get(holek.hindamiskogum_id)
        on_kriteeriumid = hindamiskogum and hindamiskogum.on_kriteeriumid
        if on_kriteeriumid:
            # hindamiskogumi kõigi ylesannete koos hindamine kriteeriumite kaupa
            kr_pallid, kr_sisestamata = \
                self._save_kr(hindamiskogum, rcd, tos, testiosa, hindamine, hindamine2, lopeta, prefix)
            pallid += kr_pallid or 0
            if sisestamata is None or kr_sisestamata:
                sisestamata = kr_sisestamata
            if sisestamata is None:
                # ei olnud midagi hinnata
                sisestamata = False
                
        elif komplekt or not hindamiskogum:
            # hindamine ylesannete kaupa
            # testimiskorraga testis: komplekt on määratud ja saab hindeid salvestada
            # testimiskorrata testis: korraga hinnatavad ylesanded võivad olla erinevatest komplektivalikutest
            if komplekt:
                komplekt_id = komplekt.id
            yhinded_ty_id = []
            for n1, rcd_ty in enumerate(rcd.get('ty')):
                # iga testiylesande kohta
                ty_prefix = (prefix and '%s.' % prefix) + 'ty-%d' % (n1)
                ty_hinded, ty_pallid, ty_eri, ty_sisestamata = \
                       self._save_ty(sooritaja, rcd_ty, tos, testiosa, hindamine, hindamine2, lopeta, ty_prefix)
                if sisestamata is None or ty_sisestamata:
                    sisestamata = ty_sisestamata
                sisestuserinevus |= ty_eri
                
            model.Session.flush()
            # minu hindamises kõigi hinnatud ylesannete pallide summa
            q = (model.Session.query(sa.func.sum(model.Ylesandehinne.pallid))
                 .filter(model.Ylesandehinne.hindamine_id==hindamine.id)
                 )
            pallid = q.scalar()
            if not sisestamata:
                sisestamata_tahised = self._sisestamata_ty(testiosa, tos.id, hindamiskogum and hindamiskogum.id, hindamine.id)
                sisestamata = bool(sisestamata_tahised)
        else:
            # kui komplekti ei ole, siis ei saa hindeid salvestada, 
            # sest pole teada, millise ylesande hinded need on
            pallid = None
            sisestamata = True

        # kustutame varem salvestatud hinded, mida enam ei ole
        if on_kriteeriumid:
            for hinne in hindamine.ylesandehinded:
                hinne.delete()
        else:
            for hinne in hindamine.kriteeriumihinded:
                hinne.delete()
        if hindamine.liik >= const.HINDAJA4:
            # vaide ettepaneku sisestamisel sisestatakse yhe ylesande kaupa
            # hindamiskogumi kogupallide saamiseks liidame selle ylesande pallidele
            # juurde teiste eksperdi poolt hinnatud ylesannete pallid
            # ja eksperdi poolt hindamata jäetud ylesannete kehtivad pallid
            pallid = 0
            for ty in hindamiskogum.testiylesanded:
                yv = ExamSaga(self.handler).sooritus_get_ylesandevastus(tos, ty.id, komplekt_id)
                if yv:
                    yhinne = hindamine.get_ylesandehinne(yv)
                    if yhinne:
                        # ekspert on hinnanud
                        self._calc_hindamine_yhinne(sooritaja, tos, yhinne, hindamine.liik, testiosa)
                        pallid += yhinne.pallid or 0
                    else:
                        # ekspert pole hinnanud, jõus on kehtiv hinne
                        pallid += yv.pallid or 0
        
        hindamine.pallid = pallid
        hindamine.sisestuserinevus = sisestuserinevus
        if hindamine2:
            hindamine2.sisestuserinevus = sisestuserinevus

        # kui on sisestamata, siis salvestame selle hindamise kirje juures:
        hindamine.sisestatud = sisestamata == False and not hindamine.on_probleem
        if sisestamata and lopeta:
            if sisestamata_tahised:
                self.error_lopeta = _("Hindamist ei saa kinnitada, kuna ülesannete {tahised} hindamine pole veel sisestatud").format(tahised=', '.join(sisestamata_tahised))
            else:
                self.error_lopeta = _("Ei saa kinnitada, sest kõik pole veel sisestatud")

        if hindamine.sisestatud and (lopeta != False):
            # lopeta = True - kõik peab olema sisestatud, soovitakse hindamine kinnitada
            # lopeta = False - ei pea olema sisestatud, hindamist ei kinnitata
            # lopeta = None - ei pea olema sisestatud, aga kui on, siis kinnitatakse hindamine
            hindamine.staatus = const.H_STAATUS_HINNATUD
        elif not hindamine.sisestatud or hindamine.staatus < const.H_STAATUS_POOLELI:
            hindamine.staatus = const.H_STAATUS_POOLELI

        model.Session.flush()
        self.update_hindamisolek(sooritaja, tos, holek, False, is_update_sooritus)

    def _sisestamata_ty(self, testiosa, sooritus_id, hindamiskogum_id, hindamine_id):
        # kas selle hindamise mõni ylesandehinne on puudu või lõpuni sisestamata
        q = (model.Session.query(model.Testiylesanne.tahis)
             .join((model.Ylesandevastus,
                    model.Ylesandevastus.testiylesanne_id==model.Testiylesanne.id))
             .filter(model.Ylesandevastus.sooritus_id==sooritus_id)
             .filter(model.Ylesandevastus.mittekasitsi==False)
             .filter(model.Ylesandevastus.kehtiv==True)
             .outerjoin((model.Ylesandehinne,
                         sa.and_(model.Ylesandehinne.ylesandevastus_id==model.Ylesandevastus.id,
                                 model.Ylesandehinne.hindamine_id==hindamine_id,
                                 model.Ylesandehinne.sisestatud==True)))
             .filter(model.Ylesandehinne.id==None)
             )
        if hindamiskogum_id:
            if testiosa.lotv:
                q = (q.join((model.Valitudylesanne,
                             model.Valitudylesanne.id==model.Ylesandevastus.valitudylesanne_id))
                     .filter(model.Valitudylesanne.hindamiskogum_id==hindamiskogum_id))
            else:
                q = q.filter(model.Testiylesanne.hindamiskogum_id==hindamiskogum_id)
        q = q.order_by(model.Testiylesanne.alatest_seq,
                       model.Testiylesanne.seq)
        model.log_query(q)
        tahised = [t for t, in q.all()]
        log.debug('sisestamata_ty:%s' % tahised)
        return tahised
        
    def _save_kr(self, hindamiskogum, rcd, tos, testiosa, hindamine, hindamine2, lopeta, prefix):
        """Ühe soorituse ühe kriteeriumi tulemuse salvestamine
        """
        pallid = 0 # hindamiskogumi pallid kokku
        kr_sisestamata = False
        arvutus = hindamiskogum.arvutus_kood
        krhinded = []
        
        if self.ekspert_labivaatus:
            # vaide korral, ekspertrühma liige vaatab läbi, aga ei pane hindeid
            return hindamine.pallid, False

        #if self.ekspert_ettepanek...

        kriteeriumid = hindamiskogum.hindamiskriteeriumid
        for n2, rcd_ha in enumerate(rcd.get('kr')):
            a_kood = rcd_ha['a_kood']
            krit = None
            for kr in kriteeriumid:
                if kr.aspekt_kood == a_kood:
                    krit = kr
                    break
            if not krit:
                log.debug('Hindamiskogumil {s} pole aspekti {kood}'.format(s=hindamiskogum.tahis, kood=a_kood))
                continue

            if prefix:
                ha_prefix = '%s.kr-%d' % (prefix, n2)
            else:
                ha_prefix = 'kr-%d' % n2
            krithinne = hindamine.give_kriteeriumihinne(krit.id)
            krhinded.append(krithinne)
            
            # hindepallide sisestamine
            if self.ekspert_ettepanek:
                # vaide korral, tehakse ettepanek
                # hindepallid, mis on määramata, asendatakse kehtivate pallidega
                # (neid eksperdid ei muutnud)
                if rcd_ha['toorpunktid'] == None:
                    kritvastus = sooritus.get_kriteeriumivastus(krit.id)
                    if kritvastus:
                        rcd_ha['toorpunktid'] = kritvastus.toorpunktid
                        if rcd_ha['toorpunktid'] is None:
                            rcd_ha['toorpunktid'] = kritvastus.toorpunktid_enne_vaiet
                        # kui kehtivad punktid on saadud kahe hindaja punktide liitmise teel,
                        # siis on yhe hindaja punktid kaks korda väiksemad
                        if arvutus == const.ARVUTUS_SUMMA and rcd_ha['toorpunktid']:
                            rcd_ha['toorpunktid'] /= 2.

            sisestamata = self._save_krithinne(krithinne, krit, rcd_ha, lopeta, ha_prefix)
            pallid += krithinne.pallid or 0
            kr_sisestamata |= sisestamata

        for hinne in list(hindamine.kriteeriumihinded):
            if hinne not in krhinded:
                hinne.delete()
        return pallid, kr_sisestamata
        
    def _save_ty(self, sooritaja, rcd_ty, tos, testiosa, hindamine, hindamine2, lopeta, ty_prefix):
        """Ühe soorituse ühe ülesande tulemuse salvestamine
        """
        ty_hinded = [] # testiylesande hinnete kirjed
        ty_pallid = 0 # testiylesande pallid 
        komplekt_id = hindamine.komplekt_id
        ty = model.Testiylesanne.get(rcd_ty['ty_id'])
        vy_id = rcd_ty.get('vy_id')
        if vy_id:
            # vy_id on kaasas
            vy = model.Valitudylesanne.get(vy_id)
            assert vy.testiylesanne_id == ty.id, 'vale ty'
        else:
            # vy_id ei tea
            vy_seq = rcd_ty.get('vy_seq') or 1
            vy = ty.get_valitudylesanne(hindamine.komplekt, vy_seq)
        if not vy:
            log.error('Puudub valitudylesanne (%s,%s)' % (tos.id, ty.id))
            return ty_hinded, ty_pallid, False, False

        if self.on_jagatudtoo:
            ylesandevastus = tos.getq_ylesandevastus(ty.id, vy.komplekt_id, muudetav=False)
            if not ylesandevastus:
                log.error('Puudub ylesandevastus (%s,%s)' % (tos.id, ty.id))
                return ty_hinded, ty_pallid, False, False
        else:
            ylesandevastus = tos.give_ylesandevastus(ty.id, vy.id)
        ylesandevastus.valitudylesanne_id = vy.id
        # kui varem on pallid arvutatud, siis tyhistame arvutuse
        ylesandevastus.staatus = const.B_STAATUS_KEHTETU
        #log.debug('_save_ty %s' % ty.tahis)
        sisestusviis = self.sisestusviis or ty.sisestusviis
        if sisestusviis == const.SISESTUSVIIS_PALLID:
            # sisestatakse hindepalle
            ty_hinded, ty_pallid, ty_eri, ty_sisestamata = \
                self._save_ty_hinded(ylesandevastus, hindamine, hindamine2, ty, vy, rcd_ty, lopeta, ty_prefix)
        else:
            # sisestatakse vastused või õige/vale
            ty_hinded, ty_eri, ty_sisestamata = \
                self._save_ty_vastused(sooritaja, tos, ylesandevastus, testiosa, hindamine, hindamine2, ty, vy, rcd_ty, lopeta, ty_prefix, sisestusviis)

        # kontrollime, et mõlemad sisestajad on sama valikylesannet sisestanud
        if ty.on_valikylesanne:
            if hindamine2:
                vy2 = hindamine2.get_vy_by_ty(ty)
                if vy2 and vy2.id != vy.id:
                    self.warnings[ty_prefix+'.vy_seq'] = _("Erineb")        
                    ty_eri = True
            if not ty_eri:
                # võimalik teine kirje märkida kehtetuks
                for yv2 in ExamSaga(self.handler).sooritus_get_ylesandevastused(tos, ty.id, komplekt_id=vy.komplekt_id):
                    if yv2 != ylesandevastus:
                        yv2.loplik = None
        return ty_hinded, ty_pallid, ty_eri, ty_sisestamata

    def _save_ty_hinded(self, ylesandevastus, hindamine, hindamine2, ty, vy, rcd_ty, lopeta, ty_prefix):
        """Ühe soorituse ühe testiylesande pallide salvestamine.
        """
        ty_hinded = []
        ty_pallid = 0
        #log.debug('_save_ty_hinded %s' % ty.tahis)
        # ylesande kogupallid
        hinne = hindamine.give_ylesandehinne(ylesandevastus, vy)
        hinne2 = hindamine2 and hindamine2.get_ylesandehinne(ylesandevastus)
        ty_eri = a_eri = k_eri = False
        ty_sisestamata = a_sisestamata = k_sisestamata = False
        arvutus = ty.hindamiskogum.arvutus_kood
                    
        if self.ekspert_labivaatus:
            # vaide korral, ekspertrühma liige vaatab läbi, aga ei pane hindeid
            log.debug('  ekspert_labivaatus')
            if hinne.toorpunktid is None or hinne.pallid is None:
                # eksperdi korral vaikimisi ei muudeta tulemust
                if ylesandevastus.toorpunktid_kasitsi is None:
                    hinne.toorpunktid_kasitsi = 0
                elif arvutus == const.ARVUTUS_SUMMA:
                    hinne.toorpunktid_kasitsi = ylesandevastus.toorpunktid_kasitsi / 2.
                else:
                    hinne.toorpunktid_kasitsi = ylesandevastus.toorpunktid_kasitsi
                sm = (hinne.toorpunktid_kasitsi or 0) + (ylesandevastus.toorpunktid_arvuti or 0)
                # ylesande tulemus ei või olla < 0
                hinne.toorpunktid = max(sm, 0)

                if ylesandevastus.pallid_kasitsi is None:
                    hinne.pallid_kasitsi = 0
                elif arvutus == const.ARVUTUS_SUMMA:
                    hinne.pallid_kasitsi = ylesandevastus.pallid_kasitsi / 2.
                else:
                    hinne.pallid_kasitsi = ylesandevastus.pallid_kasitsi
                sm = (hinne.pallid_kasitsi or 0) + (ylesandevastus.pallid_arvuti or 0)
                hinne.pallid = max(sm, 0)
                
            ty_hinded.append(hinne)
            hinne.set_ylesandehindemarkus(rcd_ty.get('markus'),
                                          self.c.ekspert_labiviija.id)
            return ty_hinded, hinne.pallid, ty_eri, ty_sisestamata

        if self.ekspert_ettepanek:
            # vaide korral, tehakse ettepanek
            # hindepallid, mis on määramata, asendatakse kehtivate pallidega
            # (neid eksperdid ei muutnud)
            if rcd_ty['toorpunktid'] == None:
                tp = ylesandevastus.toorpunktid_kasitsi
                if tp is None:
                    tp = ylesandevastus.toorpunktid_enne_vaiet
                    if tp is not None:
                        tp_a = ylesandevastus.toorpunktid_arvuti
                        if tp_a:
                            tp = max(0, tp - tp_a)
                rcd_ty['toorpunktid'] = tp
                # kui kehtivad punktid on saadud kahe hindaja punktide liitmise teel,
                # siis on yhe hindaja punktid kaks korda väiksemad
                if arvutus == const.ARVUTUS_SUMMA and rcd_ty['toorpunktid']:
                    rcd_ty['toorpunktid'] /= 2.

        # kas ylesandel on hindamisaspekte 
        on_aspekt = on_kysimus = False
        # aspektide eest antud hindepallide summa
        y_toorpunktid = 0
        # aspektide hindepallide summa maksimaalne võimalik väärtus
        y_max_toorpunktid = 0

        ylesanne = vy.ylesanne
        hindamisaspektid = ylesanne.hindamisaspektid
        aspektihinded = []
        # juhul, kui ylesandel on aspektid
        for n2, rcd_ha in enumerate(rcd_ty.get('ha')):
            a_kood = rcd_ha['a_kood']
            aspekt = None
            for ha in hindamisaspektid:
                if ha.aspekt_kood == a_kood:
                    aspekt = ha
                    break
            if not aspekt:
                log.debug('Ülesandes %s pole aspekti %s' % (vy.ylesanne_id, a_kood))
                continue

            on_aspekt = True # ylesandel on vähemalt yks aspekt
            y_max_toorpunktid += aspekt.max_pallid * aspekt.kaal

            ha_prefix = '%s.ha-%d' % (ty_prefix, n2)
            aspektihinne = hinne.give_aspektihinne(aspekt.id)
            aspektihinded.append(aspektihinne)
            
            # hindepallide sisestamine
            if self.ekspert_ettepanek:
                # vaide korral, tehakse ettepanek
                # hindepallid, mis on määramata, asendatakse kehtivate pallidega
                # (neid eksperdid ei muutnud)
                if rcd_ha['toorpunktid'] == None:
                    vastusaspekt = ylesandevastus.get_vastusaspekt(aspekt.id)
                    if vastusaspekt:
                        rcd_ha['toorpunktid'] = vastusaspekt.toorpunktid
                        if rcd_ha['toorpunktid'] is None:
                            rcd_ha['toorpunktid'] = vastusaspekt.toorpunktid_enne_vaiet
                        # kui kehtivad punktid on saadud kahe hindaja punktide liitmise teel,
                        # siis on yhe hindaja punktid kaks korda väiksemad
                        if arvutus == const.ARVUTUS_SUMMA and rcd_ha['toorpunktid']:
                            rcd_ha['toorpunktid'] /= 2.

            eri, sisestamata = \
                self._save_aspektihinne(aspektihinne, hinne, hinne2, ty, vy, aspekt, rcd_ha, lopeta, ha_prefix)
            y_toorpunktid += (aspektihinne.toorpunktid or 0) * aspekt.kaal
            a_eri |= eri                        
            a_sisestamata |= sisestamata

        # kustutame liigsed kirjed, mis võisid olla varasemast jäänud
        for ah in list(hinne.aspektihinded):
            if ah not in aspektihinded:
                ah.delete()
        
        # juhul, kui ei ole aspekte, sisestatakse kysimuste hinded
        kysimusehinded = []
        for n2, rcd_k in enumerate(rcd_ty.get('k')):
            # kysimused
            k_id = rcd_k['k_id']
            k = ylesanne.get_kysimus(kysimus_id=k_id)
            if not k:
                log.debug('Ülesandes %s (vy %s, ty %s) pole kysimust %s' % (vy.ylesanne_id, vy.id, ty.id, k_id))
                continue

            on_kysimus = True
            #### TODO? kas luua kv siin?
            kysimusevastus = ylesandevastus.give_kysimusevastus(k.id, hindamine.sisestus)
            kysimusehinne = hinne.give_kysimusehinne(kysimusevastus)
            k_prefix = '%s.k-%d' % (ty_prefix, n2)
            kysimusehinded.append(kysimusehinne)
            if self.ekspert_labivaatus:
                # vaide korral, ekspertrühma liige vaatab läbi, aga ei pane hindeid
                hinne.set_ylesandehindemarkus(rcd_seq.get('markus'),
                                              self.c.ekspert_labiviija.id,
                                              aspekt.id)
            else:
                # hindepallide sisestamine
                if self.ekspert_ettepanek:
                    # vaide korral, tehakse ettepanek
                    # hindepallid, mis on määramata, asendatakse kehtivate pallidega
                    # (neid eksperdid ei muutnud)
                    if rcd_k['toorpunktid'] == None:
                        rcd_k['toorpunktid'] = kysimusevastus.toorpunktid
                        # kui kehtivad punktid on saadud kahe hindaja punktide liitmise teel,
                        # siis on yhe hindaja punktid kaks korda väiksemad
                        if arvutus == const.ARVUTUS_SUMMA and rcd_k['toorpunktid']:
                            rcd_k['toorpunktid'] /= 2.

                kysimusevastus2 = hindamine2 and ylesandevastus.give_kysimusevastus(k.id, hindamine2.sisestus)
                eri, sisestamata = \
                    self._save_kysimusehinne(kysimusehinne, hinne, hinne2, ty, vy, kysimusevastus, kysimusevastus2,
                                             k, rcd_k, lopeta, k_prefix)
                if not k.ei_arvesta:
                    y_toorpunktid += kysimusehinne.toorpunktid or 0
                k_eri |= eri                        
                k_sisestamata |= sisestamata

        # kustutame liigsed kirjed, mis võivad olla varasemast jäänud
        for kh in list(hinne.kysimusehinded):
            if kh not in kysimusehinded:
                kh.delete()

        if on_aspekt or on_kysimus:
            # kui aspektide hindeid ega kysimuste hindeid ei postitatud,
            # siis on vist arvutihinnatav ylesanne?
            ## siis on vist postitatud terve ylesande toorpunktid
            # muidu kasutame aspektide või kysimuste toorpunktide summat
            if ylesanne.max_pallid is not None:
                if y_toorpunktid > ylesanne.max_pallid:
                    y_toorpunktid = ylesanne.max_pallid
            rcd_ty['toorpunktid'] = y_toorpunktid

        # hinnete sisestamine
        ty_eri, ty_sisestamata = \
            self._save_hinne(ylesandevastus, hinne, hinne2, ty, vy, rcd_ty, lopeta, ty_prefix, on_aspekt or on_kysimus)
        #log.debug('sisestamata:ty %s, a %s, k %s' % (ty_sisestamata, a_sisestamata, k_sisestamata))
        ty_eri |= a_eri | k_eri

        # ylesande hindamise probleem (avalikus vaates hindamisel)
        hinne.on_probleem = rcd_ty.get('on_probleem') and True or None
        if hinne.on_probleem:
            hinne.probleem_varv = rcd_ty.get('probleem_varv')
            hinne.probleem_sisu = rcd_ty.get('probleem_sisu')
            ty_sisestamata = True
        else:
            hinne.probleem_varv = None
            hinne.probleem_sisu = None

        ty_sisestamata |= a_sisestamata | k_sisestamata
        hinne.sisestatud = not ty_sisestamata
        ty_hinded.append(hinne)
       
        log.debug('  hinne %s pallid=%s sisestamata=%s' % (hinne.id, fstr(hinne.pallid), ty_sisestamata))

        if self.on_hindamiskogumita:
            if not ty_sisestamata:
                # kui on testimiskorrata testi hindamine, siis kantakse punktid kohe edasi
                self._set_ty_hinded_hindamiskogumita(ylesandevastus, hinne, ylesanne)
            elif hinne.on_probleem:
                # probleemi korral ei ole punkte
                ylesandevastus.pallid_kasitsi = None
                ylesandevastus.toorpunktid_kasitsi = None
                ylesandevastus.pallid = None
                ylesandevastus.toorpunktid = None
                log.debug(f'hinne {hinne.id} on probleem')
        return ty_hinded, hinne.pallid, ty_eri, ty_sisestamata

    def _set_ty_hinded_hindamiskogumita(self, ylesandevastus, hinne, ylesanne):
        # testimiskorrata hindamisel ei kasutata hindamiskogumeid
        # ja hindamisi ei kinnitata,
        # hindaja antud punktid kantakse kohe vastuse kirjesse
        on_aspektid = False
        for ah in hinne.aspektihinded:
            ha_id = ah.hindamisaspekt_id
            vaspekt = ylesandevastus.give_vastusaspekt(ha_id)
            vaspekt.toorpunktid = ah.toorpunktid
            vaspekt.pallid = ah.pallid
            on_aspektid = True

        if not on_aspektid:
            di_kh = {kh.kysimusevastus_id: kh for kh in hinne.kysimusehinded}
            #log.debug('DIKH=%s' % di_kh)
            for kv in ylesandevastus.kysimusevastused:
                kh = di_kh.get(kv.id)
                if kh:
                    kv.toorpunktid = kh.toorpunktid
                    kv.pallid = kh.pallid
                    #log.debug('kv%s pallid=%s' % (kv.id,kv.pallid))

        if hinne.pallid_kasitsi is not None:
            ylesandevastus.pallid_kasitsi = hinne.pallid_kasitsi
            ylesandevastus.toorpunktid_kasitsi = hinne.toorpunktid_kasitsi
            sm = hinne.pallid_kasitsi + (ylesandevastus.pallid_arvuti or 0)
            ylesandevastus.pallid = max(sm, 0)
            sm = hinne.toorpunktid_kasitsi + (ylesandevastus.toorpunktid_arvuti or 0)
            ylesandevastus.toorpunktid = max(sm, 0)
            ylesandevastus.staatus = const.B_STAATUS_KEHTIV

    def _save_hinne(self, ylesandevastus, hinne, hinne2, ty, vy, rcd, lopeta, prefix, on_liidetud=False):
        """Ühe hinde salvestamine. 
        """
        sisestuserinevus = False
        sisestamata = False

        hinne.markus = rcd.get('markus')

        toorpunktid, nullipohj_kood = _nullpunktid(rcd['toorpunktid'])
        ylesanne = vy.ylesanne
        if hinne.toorpunktid_kasitsi != toorpunktid:
            # palle muudeti
            vanad_toorpunktid = hinne.toorpunktid_kasitsi
            hinne.toorpunktid_kasitsi = toorpunktid
            if vanad_toorpunktid is not None:
                # kui varem olid pallid juba sisestatud, siis logime muudatuse
                model.Sisestuslogi(hindamine=hinne.hindamine,
                                   ylesandehinne=hinne, 
                                   kasutaja_id=self.user.id,
                                   liik=model.Sisestuslogi.LIIK_PALLID,
                                   vana=self.handler.h.fstr(vanad_toorpunktid),
                                   uus=self.handler.h.fstr(toorpunktid))

        if hinne.nullipohj_kood != nullipohj_kood:
            hinne.nullipohj_kood = nullipohj_kood

        if hinne.toorpunktid_kasitsi is None:
            hinne.pallid_kasitsi = None
            if not ylesanne.arvutihinnatav and not ylesandevastus.mittekasitsi:
                sisestamata = True
                if lopeta:
                    self.errors[prefix+'.toorpunktid'] = _("Palun sisestada väärtus")
        else:
            hinne.pallid_kasitsi = hinne.toorpunktid_kasitsi * (vy.koefitsient or 0)
            sm = hinne.toorpunktid_kasitsi + (ylesandevastus.toorpunktid_arvuti or 0)
            hinne.toorpunktid = max(sm, 0)
            sm = hinne.pallid_kasitsi + (ylesandevastus.pallid_arvuti or 0)
            hinne.pallid = max(sm, 0)
            err = None
            if hinne.toorpunktid > (ylesanne.max_pallid or 0):
                err = _("Ülesande {s} toorpunktide summa ei tohi olla suurem kui {p}").format(
                    s=ty.seq, p=self.handler.h.fstr(ylesanne.max_pallid or 0))
            elif hinne2:
                if hinne2.toorpunktid is not None:
                    if hinne2.toorpunktid != hinne.toorpunktid or hinne2.nullipohj_kood != hinne.nullipohj_kood:
                        if not on_liidetud:
                            err = _("Erineb")        
                        sisestuserinevus = True
            if err:
                self.errors[prefix+'.toorpunktid'] = err
                log.info(err)

        return sisestuserinevus, sisestamata
    
    def _save_aspektihinne(self, aspektihinne, hinne, hinne2, ty, vy, aspekt, rcd, lopeta, prefix):
        """Ühe aspekti hinde salvestamine.
        """
        sisestuserinevus = False
        sisestamata = False

        toorpunktid, nullipohj_kood = _nullpunktid(rcd['toorpunktid'])

        aspektihinne.nullipohj_kood = rcd.get('nullipohj_kood') or nullipohj_kood
        aspektihinne.markus = rcd.get('markus')

        if aspektihinne.toorpunktid != toorpunktid:
            # palle muudeti
            vanad_toorpunktid = aspektihinne.toorpunktid
            aspektihinne.toorpunktid = toorpunktid
            if vanad_toorpunktid is not None:
                # kui varem olid pallid juba sisestatud, siis logime muudatuse
                model.Sisestuslogi(hindamine=hinne.hindamine,
                                   ylesandehinne=hinne, 
                                   aspektihinne=aspektihinne,
                                   kasutaja_id=self.user.id,
                                   liik=model.Sisestuslogi.LIIK_PALLID,
                                   vana=self.handler.h.fstr(vanad_toorpunktid),
                                   uus=self.handler.h.fstr(toorpunktid))

        if aspektihinne.toorpunktid is None:
            aspektihinne.pallid = None
            sisestamata = True
            if lopeta:
                self.errors[prefix+'.toorpunktid'] = _("Palun sisestada väärtus")
        else:
            DIFF = 1e-10
            def _equal(f1, f2):
                return 0 - DIFF < f1 - f2 < DIFF
            
            pintervall = aspekt.pintervall
            aspektihinne.pallid = aspektihinne.toorpunktid * (vy.koefitsient or 0) * aspekt.kaal
            t_max_pallid = aspekt.max_pallid
            if t_max_pallid < aspektihinne.toorpunktid:
                self.errors[prefix+'.toorpunktid'] = _("Arv ei tohi olla suurem kui {s}").format(s=self.handler.h.fstr(t_max_pallid))
            elif pintervall \
                 and not _equal(toorpunktid, t_max_pallid) \
                 and not _equal(toorpunktid % pintervall, 0):
                self.errors[prefix + '.toorpunktid'] = _("Punktide lubatud intervall on {s}").format(s=self.handler.h.fstr(pintervall))
                
            elif hinne2:
                aspektihinne2 = hinne2.get_aspektihinne(aspekt.id)
                if aspektihinne2 and aspektihinne2.toorpunktid is not None:
                    if aspektihinne2.toorpunktid != aspektihinne.toorpunktid or \
                           aspektihinne2.nullipohj_kood != aspektihinne.nullipohj_kood:
                        self.warnings[prefix+'.toorpunktid'] = _("Erineb")        
                        sisestuserinevus = True

        return sisestuserinevus, sisestamata

    def _save_krithinne(self, krithinne, kriteerium, rcd, lopeta, prefix):
        """Ühe kriteeriumi hinde salvestamine.
        """
        sisestamata = False
        toorpunktid, nullipohj_kood = _nullpunktid(rcd['toorpunktid'])

        krithinne.nullipohj_kood = rcd.get('nullipohj_kood') or nullipohj_kood
        krithinne.markus = rcd.get('markus')

        if krithinne.toorpunktid != toorpunktid:
            # palle muudeti
            vanad_toorpunktid = krithinne.toorpunktid
            krithinne.toorpunktid = toorpunktid

        if krithinne.toorpunktid is None:
            krithinne.pallid = None
            sisestamata = True
            if lopeta:
                self.errors[prefix+'.toorpunktid'] = _("Palun sisestada väärtus")
        else:
            krithinne.pallid = krithinne.toorpunktid * kriteerium.kaal
            if kriteerium.max_pallid < krithinne.toorpunktid:
                self.errors[prefix+'.toorpunktid'] = _("Arv ei tohi olla suurem kui {s}").format(s=self.handler.h.fstr(kriteerium.max_pallid))

        return sisestamata

    def _save_kysimusehinne(self, kysimusehinne, hinne, hinne2, ty, vy, kysimusevastus, kysimusevastus2, k, rcd, lopeta, prefix):
        """Ühe küsimuse hinde salvestamine.
        """
        sisestuserinevus = False
        sisestamata = False

        toorpunktid, nullipohj_kood = _nullpunktid(rcd['toorpunktid'])
        kysimusehinne.nullipohj_kood = rcd.get('nullipohj_kood') or nullipohj_kood
        kysimusehinne.markus = rcd.get('markus')

        if kysimusehinne.toorpunktid != toorpunktid:
            # palle muudeti
            vanad_toorpunktid = kysimusehinne.toorpunktid
            kysimusehinne.toorpunktid = toorpunktid
            if vanad_toorpunktid is not None:
                # kui varem olid pallid juba sisestatud, siis logime muudatuse
                model.Sisestuslogi(hindamine=hinne.hindamine,
                                   ylesandehinne=hinne, 
                                   kysimusehinne=kysimusehinne,
                                   kasutaja_id=self.user.id,
                                   liik=model.Sisestuslogi.LIIK_PALLID,
                                   vana=self.handler.h.fstr(vanad_toorpunktid),
                                   uus=self.handler.h.fstr(toorpunktid))

        if kysimusehinne.toorpunktid is None:
            kysimusehinne.pallid = None
            sisestamata = True
            if lopeta:
                self.errors[prefix+'.toorpunktid'] = _("Palun sisestada väärtus")
        else:
            kysimusehinne.pallid = toorpunktid * (vy.koefitsient or 0)
            tulemus = k.tulemus
            if tulemus:
                t_max_pallid = tulemus.get_max_pallid()
                t_min_pallid = tulemus.min_pallid
            else:
                t_max_pallid = t_min_pallid = None
            DIFF = 1e-10
            def _equal(f1, f2):
                return 0 - DIFF < f1 - f2 < DIFF
            
            pintervall = tulemus.pintervall
            if t_max_pallid is not None and t_max_pallid < toorpunktid:
                self.errors[prefix+'.toorpunktid'] = _("Arv ei tohi olla suurem kui {s}").format(s=self.handler.h.fstr(t_max_pallid))
            elif t_min_pallid is not None and t_min_pallid > toorpunktid:
                self.errors[prefix+'.toorpunktid'] = _("Arv ei tohi olla väiksem kui {s}").format(s=self.handler.h.fstr(t_min_pallid))        
            elif pintervall \
                 and not _equal(toorpunktid, t_max_pallid) \
                 and not _equal(toorpunktid, t_min_pallid) \
                 and not _equal((toorpunktid - t_min_pallid + DIFF/2) % pintervall, 0):
                self.errors[prefix + '.toorpunktid'] = _("Punktide lubatud intervall on {s}").format(s=self.handler.h.fstr(pintervall))
                 
            elif hinne2:
                kysimusehinne2 = hinne2.get_kysimusehinne(kysimusevastus2)
                if kysimusehinne2 and kysimusehinne2.toorpunktid is not None:
                    if kysimusehinne2.toorpunktid != kysimusehinne.toorpunktid or \
                           kysimusehinne2.nullipohj_kood != kysimusehinne.nullipohj_kood:
                        # ei taha seda teadet Erineb
                        self.warnings[prefix+'.toorpunktid'] = _("Erineb")        
                        sisestuserinevus = True

        return sisestuserinevus, sisestamata

    def _save_ty_vastused(self, sooritaja, sooritus, ylesandevastus, testiosa, hindamine, hindamine2, ty, vy, rcd_ty, lopeta, ty_prefix, sisestusviis):
        """Ühe soorituse ühe testiylesande vastuste salvestamine.
        """
        # tekitame ylesandehinde kirje - see on peamiselt lihtsalt selleks, 
        # et oleks yks koht, kust saaks vaadata, mis vy on sisestatud
        hinne = hindamine.give_ylesandehinne(ylesandevastus, vy) 
        ty_eri = False # kas esineb sisestuserinevusi

        params = rcd_ty.get('r')
        blockentry = BlockEntry(self, lopeta and ty_prefix)
        ylesandevastus.valitudylesanne_id = vy.id
        responses = blockentry.save_entry(ylesandevastus, vy, params, hindamine.sisestus, sisestusviis)
        sisestamata = blockentry.sisestamata

        if self.ekspert_ettepanek:
            # kui vaide ettepaneku sisestamisel sisestati vastuseid,
            # siis arvutame igaks juhuks kokku arvutihinnatavad punktid
            self._calc_ty(sooritaja, sooritus, ylesandevastus, ty, vy, testiosa)

        msg = _("Erineb")
        
        # vastused on salvestatud, võrdleme neid teise sisestusega
        if hindamine2 and hindamine2.staatus == const.H_STAATUS_HINNATUD:
            ylesanne = vy.ylesanne
            # responses on dict, milles kysimuste koodidele vastab list kv kirjetest
            for kood, kv in responses.items():
                # kood on kysimuse kood
                # vastused on list selle kysimuse vastustest
                # otsime teise sisestuse sama kysimuse vastuste kirjed
                vastused = list(kv.kvsisud)

                kysimus = ylesanne.get_kysimus(kood)
                kv2 = ylesandevastus.get_kysimusevastus(kysimus.id, hindamine2.sisestus)
                vastused2 = kv2 and list(kv2.kvsisud) or []
                
                cnt1 = len(vastused)
                cnt2 = len(vastused2)
                cnt = max(cnt1, cnt2)

                if kysimus.vastusesisestus:
                    # valikväärtuse sisestamine märkeruutudelt
                    # sel juhul lubame erinevuste kontrollimisel samal vastusel asuda 
                    # vastuste jadas teisel kohal
                    vastused_str = [kvs.as_string() for kvs in vastused]
                    vastused2_str = [kvs.as_string() for kvs in vastused2]
                    vastusekoodid = [v.kood for v in kysimus.valikud]

                    # kas iga minu sisestatud vastus on olemas teises sisestuses?
                    for n in range(cnt1):
                        kvs = vastused[n] # minu sisestuse vastused
                        kvs_s = kvs.as_string()
                        # kui on mõni sisestuserinevus, siis ei pruugi ylejäänud
                        # vastused olla jadas samal kohal
                        if kvs_s not in vastused2_str:
                            ty_eri = True

                            # erijuhul, kui toimub valikvälja vastuste sisestamine märkeruutudelt,
                            # siis on n linnutatud märkeruutude indeks, mitte kõigi valikute indeks
                            # ja õige prefiksi saamiseks tuleb pisut pingutada
                            try:
                                n_valik = vastusekoodid.index(kvs.kood1)
                            except ValueError:
                                n_valik = 0
                            prefix = '%s.r.%s-%d' % (ty_prefix, kood, n_valik)
                            self.warnings['%s.kood1' % prefix] = msg
                            log.debug('kv %s erineb: minu valikvastus "%s" puudub teises sisestuses (%s vs %s)' % (kv.id, kvs_s, vastused_str, vastused2_str))
                            
                    # kas iga teise sisestuse vastus on olemas minu sisestuses?
                    for n in range(cnt2):
                        kvs = vastused2[n] # minu sisestuse vastused
                        # kui on mõni sisestuserinevus, siis ei pruugi ylejäänud
                        # vastused olla jadas samal kohal
                        kvs_s = kvs.as_string()
                        if kvs_s not in vastused_str:
                            ty_eri = True

                            # erijuhul, kui toimub valikvälja vastuste sisestamine märkeruutudelt,
                            # siis on n linnutatud märkeruutude indeks, mitte kõigi valikute indeks
                            # ja õige prefiksi saamiseks tuleb pisut pingutada
                            try:
                                n_valik = vastusekoodid.index(kvs.kood1)
                            except ValueError:
                                n_valik = 0
                            prefix = '%s.r.%s-%d' % (ty_prefix, kood, n_valik)
                            self.warnings['%s.kood1' % prefix] = msg
                            log.debug('kv %s erineb: teine valikvastus "%s" puudub minu sisestuses (%s vs %s)' % (kv.id, kvs_s, vastused_str, vastused2_str))

                    continue
                
                # tavaline sisestamine
                # võrdleme kõiki selle kysimuse vastuseid kirjete kaupa
                for n in range(cnt):
                    kvs = len(vastused) > n and vastused[n] # minu sisestuse vastused
                    kvs2 = len(vastused2) > n and vastused2[n] # teise sisestuse vastused

                    on_erinevus = False
                    if kvs and kvs2:
                        # mõlemas sisestuses on vastus sisestatud
                        # samad vastused peavad olema jadas samal kohal
                        kvs_s = kvs.as_string()
                        kvs2_s = kvs2.as_string()
                        on_erinevus = kvs_s != kvs2_s
                        if on_erinevus:
                            log.debug('kv %s erineb: "%s" vs "%s"' % (kv.id, kvs_s, kvs2_s))
                    elif kv2 and kv.nullipohj_kood != kv2.nullipohj_kood:
                        # nullipõhjus erineb
                        on_erinevus = True
                        log.debug('kv %s erineb: nullip "%s" vs "%s"' % (kv.id, kv.nullipohj_kood, kv2.nullipohj_kood))
                    else:
                        # yhes sisestuses on rohkem vastuseid kui teises
                        on_erinevus = True
                        log.debug('kv %s erineb: vastuste arv, minu vastused %s vs teise vastused %s' % (kv.id, vastused, vastused2))
                    if on_erinevus:
                        ty_eri = True
                        tyyp = kvs and kvs.tyyp or kvs2 and kvs2.tyyp

                        # siin seatakse veateade
                        # vastused.mako all on skript, mis veateate eemaldab
                        # ja selle kohal olevale tabelile annab id=flasherror
                        # mis teeb punase kasti ymber

                        # vastusele vastav sisestusvormi väljanimeprefiks
                        prefix = '%s.r.%s-%d' % (ty_prefix, kood, n) 
                        if tyyp == const.RTYPE_CORRECT:
                            self.warnings['%s.oige' % prefix] = msg
                        elif tyyp == const.RTYPE_IDENTIFIER:
                            self.warnings['%s.kood1' % prefix] = msg
                        elif tyyp == const.RTYPE_PAIR:
                            if not kvs or not kvs2 or kvs.kood1!=kvs2.kood1:
                                self.warnings['%s.kood1' % prefix] = msg
                            if not kvs or not kvs2 or kvs.kood2!=kvs2.kood2:
                                self.warnings['%s.kood2' % prefix] = msg
                        elif tyyp == const.RTYPE_ORDERED:
                            prefix = '%s.r.%s' % (ty_prefix, kood) 
                            jarjestus = kvs and kvs.jarjestus or []
                            jarjestus2 = kvs2 and kvs2.jarjestus or []
                            for j_n in range(max(len(jarjestus),len(jarjestus2))):
                                if j_n < len(jarjestus) or j_n < len(jarjestus2) or \
                                       jarjestus[j_n] != jarjestus2[j_n]:
                                    self.warnings['%s-%d' % (prefix, j_n)] = msg
                        elif tyyp == const.RTYPE_STRING:
                            self.warnings['%s.sisu' % prefix] = msg
                        else:
                            log.info('erineb tyyp %s' % tyyp)

        return [hinne], ty_eri, sisestamata

    def _save_labiviijad(self, sooritaja, tos, hindamine, rcd, prefix, lopeta, holek):
        """Leitakse ja salvestatakse sooritusega seotud hindaja ja intervjueerija
        """
        # kontrollitakse hindaja ja intervjueerija 
        rc1, labiviija = self._check_labiviija(sooritaja, tos, rcd, prefix, lopeta, holek, hindamine.liik)
        rc2, intervjuu_labiviija = self._check_intervjuu_labiviija(sooritaja, tos, rcd, prefix, lopeta, holek)
        rc3, kontroll_labiviija = self._check_kontroll_labiviija(sooritaja, tos, rcd, prefix, lopeta, holek, hindamine.liik)        

        if not rc1 or not rc2 or not rc3:
            # ei saa edasi salvestada
            return False

        # kantakse läbiviijate muudatused sisestuslogisse
        def _logi(vana_labiviija, labiviija, liik):
            if vana_labiviija and vana_labiviija != labiviija:
                vana_kasutaja = vana_labiviija.kasutaja
                vana = '%s %s' % (vana_labiviija.tahis,
                                  vana_kasutaja and vana_kasutaja.nimi)
                if labiviija and labiviija.kasutaja:
                    uus = '%s %s' % (labiviija.tahis,
                                     labiviija.kasutaja.nimi)
                else:
                    uus = ''
                model.Sisestuslogi(hindamine=hindamine,
                                   kasutaja_id=self.user.id,
                                   liik=liik,
                                   vana=vana[:50],
                                   uus=uus[:50])

        _logi(hindamine.labiviija, labiviija, model.Sisestuslogi.LIIK_HINDAJA)
        _logi(hindamine.kontroll_labiviija, kontroll_labiviija, model.Sisestuslogi.LIIK_HINDAJA)
        _logi(hindamine.intervjuu_labiviija, intervjuu_labiviija, model.Sisestuslogi.LIIK_INTERVJUEERIJA)        

        hindamine.labiviija = labiviija
        hindamine.hindaja_kasutaja_id = labiviija and labiviija.kasutaja_id
        hindamine.intervjuu_labiviija = intervjuu_labiviija
        hindamine.kontroll_labiviija = kontroll_labiviija
        
        #if labiviija:
        #    log.debug('labiviija=%s %s' % (labiviija.id, labiviija.kasutaja.nimi))
        return True

    def _check_labiviija(self, sooritaja, tos, rcd, prefix, lopeta, holek, liik):
        rc = True
        labiviija = None
        testiosa = self.testiosa                
        test = self.test
        ta = self.c.toimumisaeg
        vastvorm = testiosa.vastvorm_kood
        assert vastvorm in (const.VASTVORM_SP, const.VASTVORM_KP), 'pole p-test'
        labiviija_id = rcd['labiviija_id']
        if labiviija_id:
            if labiviija_id < 0 and test.testiliik_kood == const.TESTILIIK_TASE:
                # negatiivne väärtus on viide kasutaja.id järgi tasemeeksami hindajale
                # tasemeeksami hindajad ei pea olema sellele testile määratud - 
                # loome läbiviija kirje, kui vaja
                kasutaja_id = 0 - labiviija_id
                if vastvorm == const.VASTVORM_SP and liik <= const.HINDAJA2:
                    testiruum = holek.sooritus.testiruum
                    hkogum_id = None
                else:
                    testiruum = None
                    hkogum_id = holek.hindamiskogum_id
                labiviija = model.Labiviija.give_hindaja(ta.id, kasutaja_id, liik, testiosa, hkogum_id, testiruum=testiruum)
                self.neg_labiviijad.append(labiviija)

            elif labiviija_id < 0:
                # EH-346 - läbiviija on sama testikoha teise ruumi määratud, loome kirje õiges ruumis
                kasutaja_id = 0 - labiviija_id
                if vastvorm == const.VASTVORM_SP and liik <= const.HINDAJA2:
                    testiruum = holek.sooritus.testiruum
                    hkogum_id = None
                else:
                    testiruum = None
                    hkogum_id = holek.hindamiskogum_id
                labiviija = model.Labiviija.give_hindaja(ta.id, kasutaja_id, liik, testiosa, hkogum_id, testiruum=testiruum)
                self.neg_labiviijad.append(labiviija)
                
            else:
                labiviija = model.Labiviija.get(labiviija_id)
                if not labiviija or not labiviija.kasutaja_id or \
                    labiviija.toimumisaeg_id != ta.id:
                    self.errors[prefix+'.labiviija_id'] = _("Sellist hindajat pole")            
                    rc = False

        elif lopeta:
            hkogum = model.Hindamiskogum.get(holek.hindamiskogum_id)
            if vastvorm == const.VASTVORM_KP and \
                   hkogum.arvutihinnatav:
                # kui on kirjalik p-test ja arvutihinnatav hindamiskogum,
                # siis võib hindaja puududa
                pass
            elif vastvorm == const.VASTVORM_KP and \
                 (not sooritaja.valimis and ta.hindaja1_maaraja == const.MAARAJA_POLE or \
                  sooritaja.valimis and ta.hindaja1_maaraja_valim == const.MAARAJA_POLE):
                # kui on kirjalik test ja hindaja pole nõutav, siis võib hindaja puududa
                pass
            elif vastvorm == const.VASTVORM_SP and \
                     ta.hindaja1_maaraja == const.MAARAJA_POLE and \
                     ta.hindaja2_maaraja == const.MAARAJA_POLE:                     
                # kui on suuline test ja kumbki hindaja pole nõutav, siis võib hindaja puududa
                pass
            else:
                # muudel juhtudel on hindaja kohustuslik
                self.errors[prefix+'.labiviija_id'] = _("Väärtus puudub")         
                rc = False

        return rc, labiviija

    def _check_kontroll_labiviija(self, sooritaja, sooritus, rcd, prefix, lopeta, holek, liik):
        rc = True
        labiviija = None
        testiosa = self.testiosa                
        hkogum = model.Hindamiskogum.get(holek.hindamiskogum_id)
        ta = self.c.toimumisaeg
        labiviija_id = rcd.get('kontroll_labiviija_id')
        if labiviija_id:
            if not hkogum.kontrollijaga_hindamine:
                # Hindamiskogumi seaded ei luba kaht hindajat
                pass
            elif labiviija_id == rcd['labiviija_id']:
                self.errors[prefix+'.kontroll_labiviija_id'] = _("Sama isik ei saa mõlema hindaja rollis olla")                            
                rc = False
            elif labiviija_id < 0 and testiosa.test.testiliik_kood == const.TESTILIIK_TASE:
                # negatiivne väärtus on viide kasutaja.id järgi tasemeeksami hindajale
                # tasemeeksami hindajad ei pea olema sellele testile määratud - 
                # loome läbiviija kirje, kui vaja
                kasutaja_id = 0 - labiviija_id
                labiviija = model.Labiviija.give_hindaja(ta.id, kasutaja_id, liik, testiosa, holek.hindamiskogum_id)
                self.neg_labiviijad.append(labiviija)
            elif labiviija_id < 0:
                # EH-346 - läbiviija on sama testikoha teise ruumi määratud, loome kirje õiges ruumis
                kasutaja_id = 0 - labiviija_id
                if testiosa.vastvorm_kood == const.VASTVORM_SP:
                    testiruum = holek.sooritus.testiruum
                else:
                    testiruum = None
                labiviija = model.Labiviija.give_hindaja(ta.id, kasutaja_id, liik, testiosa, holek.hindamiskogum_id, testiruum=testiruum, lang=sooritaja.lang)
                self.neg_labiviijad.append(labiviija)
            else:
                labiviija = model.Labiviija.get(labiviija_id)
                if not labiviija or not labiviija.kasutaja_id or \
                    labiviija.toimumisaeg_id != ta.id:
                    self.errors[prefix+'.kontroll_labiviija_id'] = _("Sellist hindajat pole")            
                    rc = False

        elif lopeta:
            if hkogum.kontrollijaga_hindamine:
                self.errors[prefix+'.kontroll_labiviija_id'] = _("Väärtus puudub")         
                rc = False

        return rc, labiviija

    def _check_intervjuu_labiviija(self, sooritaja, sooritus, rcd, prefix, lopeta, holek):
        rc = True
        intervjuu_labiviija = None
        if self.c.toimumisaeg.intervjueerija_maaraja:
            labiviija_id = rcd['intervjuu_labiviija_id']
            if labiviija_id:
                if labiviija_id < 0:
                    # EH-346 - läbiviija on sama testikoha teise ruumi määratud, loome kirje õiges ruumis
                    kasutaja_id = 0 - labiviija_id
                    testiruum = sooritus.testiruum
                    intervjuu_labiviija = model.Labiviija.give_hindaja(self.c.toimumisaeg.id, kasutaja_id, None, self.testiosa, holek.hindamiskogum_id, testiruum=testiruum, grupp_id=const.GRUPP_INTERVJUU, lang=sooritaja.lang)
                    self.neg_labiviijad.append(intervjuu_labiviija)
                else:
                    intervjuu_labiviija = model.Labiviija.get(labiviija_id)
                    if not intervjuu_labiviija or not intervjuu_labiviija.kasutaja_id:
                        self.errors[prefix+'.intervjuu_labiviija_id'] = _("Sellist läbiviijat pole")
                        rc = False
            elif lopeta:
                self.errors[prefix+'.intervjuu_labiviija_id'] = _("Väärtus puudub")         
                rc = False
        return rc, intervjuu_labiviija

    def _save_komplekt(self, hindamine, komplekt, soorituskomplekt, holek, tos):
        """Soorituse komplekti salvestamine
        """
        
        if komplekt and hindamine.komplekt_id and hindamine.komplekt_id != komplekt.id:
            vana_komplekt = model.Komplekt.getR(hindamine.komplekt_id)
            model.Sisestuslogi(hindamine=hindamine,
                               kasutaja_id=self.user.id,
                               liik=model.Sisestuslogi.LIIK_KOMPLEKT,
                               vana=vana_komplekt.tahis,
                               uus=komplekt.tahis or '')
            
        hindamine.komplekt = komplekt
        if komplekt:
            hindamine.komplekt_id = komplekt.id
            holek.komplekt = komplekt
            holek.komplekt_id = komplekt.id
            soorituskomplekt.komplekt_id = komplekt.id

    def _get_hindamine2(self, holek, hindamine, prefix):
        """Leitakse teise sisestuse kirje.
        Ühtlasi kontrollitakse erinevusi läbiviijates ja komplektis.
        """
        sisestuserinevus = False
        # erinevusi otsime ka parandamise puhul, et teada staatuse määramisel, 
        # kas on sisestuserinevusi või mitte 

        # võrdleme andmeid teise sisestusega
        sisestus2 = hindamine.sisestus == 1 and 2 or 1
        hindamine2 = holek.get_hindamine(hindamine.liik, sisestus2)
        if not hindamine2:
            self.molemad = False
        else:
            sisestatud2 = hindamine2.staatus == const.H_STAATUS_HINNATUD
            
            # intervjueerija
            lv_id = hindamine.intervjuu_labiviija and hindamine.intervjuu_labiviija.id or hindamine.intervjuu_labiviija_id
            if (lv_id and hindamine2.intervjuu_labiviija_id or sisestatud2) and \
                   hindamine2.intervjuu_labiviija_id != lv_id:
                self.warnings[prefix+'.intervjuu_labiviija_id'] = _("Erineb")
                sisestuserinevus = True

            # suuline hindaja
            lv_id = hindamine.labiviija and hindamine.labiviija.id or hindamine.labiviija_id
            if (lv_id and hindamine2.labiviija_id or sisestatud2) and \
                   hindamine2.labiviija_id != lv_id:
                self.warnings[prefix+'.labiviija_id'] = _("Erineb")
                sisestuserinevus = True
            # else:
            #     log.info('hpr#%s h#%s.lv=%s == h2#%s.lv=%s' % (hindamine.hindamisprotokoll_id,
            #                                                    hindamine.id,
            #                                                    lv_id,
            #                                                    hindamine2.id,
            #                                                    hindamine2.labiviija_id))

            # komplekti valik
            komplekt_id = hindamine.komplekt and hindamine.komplekt.id or hindamine.komplekt_id
            if komplekt_id and hindamine2.komplekt_id and \
                   hindamine2.komplekt_id != komplekt_id:
                self.warnings[prefix+'.komplekt_id'] = _("Erineb")
                sisestuserinevus = True           
        return hindamine2, sisestuserinevus

    def get_h_staatus(self, tos):
        "Leiame soorituse hindamise oleku"
        
        # kõige väiksem hindamistase nende hindamisolekute seas, 
        # kus on hindamisprobleem
        min_probleemne_tase = 100
        min_staatus = max_staatus = None
        pallid = 0
        
        if tos.staatus > const.S_STAATUS_POOLELI and tos.staatus != const.S_STAATUS_TEHTUD:
            # ei ole midagi hinnata, saab 0p
            pallid = 0
            staatus = const.H_STAATUS_HINNATUD
        elif tos.hindamiskogumita:
            # hindamiskogumita hindamine
            # hinnatud on siis, kui kõigil ylesannetel on tulemus
            q = (model.Session.query(model.Ylesandevastus.id)
                 .filter(model.Ylesandevastus.sooritus_id==tos.id)
                 .filter(model.Ylesandevastus.pallid==None))
            if self.on_jagatudtoo:
                # arvestada ainult kinnitatud ylesandeid
                q = q.filter(model.Ylesandevastus.kehtiv==True)
            if q.first():
                # ei ole veel kõik ylesanded hinnatud
                q = q.join(model.Ylesandevastus.ylesandehinded)
                if q.first():
                    staatus = const.H_STAATUS_POOLELI
                else:
                    staatus = const.H_STAATUS_HINDAMATA
            else:
                # kõik ylesanded hinnatud
                # kas on märgitud probleemseks?
                q = (model.Session.query(model.Hindamine.id)
                     .filter(model.Hindamine.on_probleem==True)
                     .filter(model.Hindamine.staatus.in_((const.H_STAATUS_POOLELI, const.H_STAATUS_HINNATUD)))
                     .filter(model.Hindamine.tyhistatud==False)
                     .join(model.Hindamine.hindamisolek)
                     .filter(model.Hindamisolek.sooritus_id==tos.id)
                     )
                if q.first():
                    # mõnel hindamisel on probleem
                    staatus = const.H_STAATUS_POOLELI
                else:
                    staatus = const.H_STAATUS_HINNATUD
                    q = (model.Session.query(sa.func.sum(model.Ylesandevastus.pallid))
                         .filter(model.Ylesandevastus.sooritus_id==tos.id))
                    pallid = q.scalar()
        else:
            # oli midagi hinnata
            on_toopuudu = False
            for holek in tos.hindamisolekud:
                log.debug('holek %s hkogum=%s staatus=%s, min_staatus=%s, pallid=%s' % (holek.id, holek.hindamiskogum_id, holek.staatus, min_staatus, holek.pallid))
                if min_staatus is None or min_staatus > holek.staatus:
                    min_staatus = holek.staatus
                if max_staatus is None or max_staatus < holek.staatus:
                    max_staatus = holek.staatus
                if holek.staatus == const.H_STAATUS_HINNATUD and pallid is not None:
                    pallid += holek.pallid or 0
                else:
                    min_probleemne_tase = min(holek.hindamistase, min_probleemne_tase)
                if holek.hindamisprobleem == const.H_PROBLEEM_TOOPUUDU:
                    on_toopuudu = True

            if on_toopuudu:
                staatus = const.H_STAATUS_TOOPUUDU
            elif min_staatus is None:
                staatus = const.H_STAATUS_HINDAMATA
            elif max_staatus > const.H_STAATUS_HINDAMATA and min_staatus == const.H_STAATUS_HINDAMATA:
                staatus = const.H_STAATUS_POOLELI
            else:
                staatus = min_staatus

            if staatus != const.H_STAATUS_HINNATUD:
                pallid = None
        return staatus, pallid, min_probleemne_tase

    def arvutayle(self, sooritaja, tos, yv_id):
        "Ühe soorituse tulemuse üle arvutamine"
        if sooritaja.klaster_id and tos.klastrist_toomata:
            # tõmbame klastrist andmed ja arvutame
            host = model.Klaster.get_host(sooritaja.klaster_id)
            ExamSaga(self.handler).from_examdb(host, tos, sooritaja, sooritaja.test, tos.testiosa, tos.toimumisaeg, sooritaja.lang, False)
                        
        holekud = []
        if yv_id:
            # ainult kindla ylesanne arvutamine
            yv = model.Ylesandevastus.get(yv_id)
            tos = yv.sooritus
            hk = yv.valitudylesanne.hindamiskogum or\
                 yv.testiylesanne.hindamiskogum
            holek = tos.get_hindamisolek(hk)
            if holek:
                holekud.append(holek)
            force = True
        else:
            # kogu testiosa arvutamine
            yv = None
            force = True
            tos.give_hindamisolekud()
            model.Session.flush()
            holekud = list(tos.hindamisolekud)
            
        sooritaja = tos.sooritaja
        for holek in holekud:
            if yv:
                # ainult yhe ylesande arvutamine
                self.update_hindamisolek(sooritaja, tos, holek, force, False, force_yv=yv)
            else:
                # kui force == True, siis kõigi ylesannete arvutamine
                # kui force == False, siis normipunktide arvuamine
                self.update_hindamisolek(sooritaja, tos, holek, force, False)
        self.update_sooritus(sooritaja, tos)
        sooritaja.update_staatus()
    
    def update_sooritus(self, sooritaja, tos, is_update_sooritaja=True):
        "Soorituse kirje oleku muutmine peale hindamist"
        testiosa = self.testiosa
        test = self.test
        on_tseis = test.testiliik_kood in (const.TESTILIIK_TASE, const.TESTILIIK_SEADUS)

        def _set_protsent(tos):
            max_pallid = tos.max_pallid           
            # TSEISi korral alatestide ja testiosa pallid ymardatakse
            if on_tseis:
                max_pallid = round(max_pallid + .000001)            
            pallid = tos.pallid
            if pallid is None or not max_pallid:
                tos.tulemus_protsent = None
            else:
                sooritus_id = tos.id
                assert pallid < max_pallid + .0001, '%s sooritusel %s (%s) liiga suur tulemus (%sp, max %sp)' % \
                    (tos.sooritaja.kasutaja.isikukood, tos.tahised, tos.id, pallid, max_pallid)
                tos.tulemus_protsent = pallid * 100. / max_pallid
            log.debug('tos%s tulemus_protsent=%s, pallid=%s, max=%s' % (tos.id, fstr(tos.tulemus_protsent), fstr(pallid), fstr(max_pallid)))

        def _remove_old_var(tos):
            "Kustutame teiste proovitud komplektide ylesannete vastused"
            #komplektid_id = [r.komplekt_id for r in tos.hindamisolekud]
            komplektid_id = [r.komplekt_id for r in model.Soorituskomplekt.get_by_sooritus(tos.id)]            
            if None in komplektid_id:
                # kui on hindamiskogumita hindamine, siis komplekti siit ei saa
                return
            if not komplektid_id:
                # mingil põhjusel on soorituskomplektide kirjed puudu, hoidume vastuste kustutamisest
                return
            for yv in ExamSaga(self.handler).sooritus_ylesandevastused(tos):
                # märgime teiste komplektide vastused mittelõplikuks
                if yv.loplik:
                    vy = model.Valitudylesanne.get(yv.valitudylesanne_id)
                    if vy and vy.komplekt_id not in komplektid_id:
                        yv.loplik = None

                # kui test on tehtud, siis kustutame teiste komplektide vastused ära
                if not yv.loplik and yv.muudetav:
                    vy = model.Valitudylesanne(yv.valitudylesanne_id)
                    log.info('sooritus %s: kustutan mittelopliku vastuse %s (komplekt %s, ylesanne %s, soorituskomplektid: %s) ' % \
                              (tos.id, yv.id, vy and vy.komplekt_id, vy and vy.ylesanne_id,
                               str(komplektid_id)))
                    for yh in yv.ylesandehinded:
                        yh.delete()
                    yv.delete()

        if tos.on_rikkumine:
            # VI hindaja on märkinud, et toimus rikkumine ja töö hinnatakse 0 punktiga
            tos.pallid = tos.tulemus_protsent = 0
            tos.hindamine_staatus = const.H_STAATUS_HINNATUD            
            if is_update_sooritaja:
                self.update_sooritaja(sooritaja)
            return
        
        if tos.ylesanneteta_tulemus:
            # ei arvuta testiosa tulemust, kuna see on sisestatud toimumise protokollile
            # ja ylesannete kaupa tulemusi ei olegi olemas
            tos.calc_max_pallid()
            _set_protsent(tos)
            tos.hindamine_staatus = const.H_STAATUS_HINNATUD
            if is_update_sooritaja:
                self.update_sooritaja(sooritaja)
            return

        h_staatus, pallid, min_probleemne_tase = self.get_h_staatus(tos)
        log.debug('update_sooritus sooritus.hindamine_staatus=%s pallid=%s' % (h_staatus, pallid))
        tos.hindamine_staatus = h_staatus
        if self.on_jagatudtoo:
            # jagatud töö pallid on kõik juba sooritatud ylesannete pallid
            qs = (model.Session.query(sa.func.sum(model.Ylesandevastus.pallid))
                  .filter(model.Ylesandevastus.sooritus_id==tos.id)
                  .filter(model.Ylesandevastus.kehtiv==True)
                  .filter(model.Ylesandevastus.muudetav==False))
            pallid = qs.scalar()

        if tos.staatus == const.S_STAATUS_TEHTUD:
            vastvorm_e = (const.VASTVORM_KE, const.VASTVORM_SE, const.VASTVORM_I, const.VASTVORM_SH)
            if testiosa.vastvorm_kood in vastvorm_e or \
                h_staatus == const.H_STAATUS_HINNATUD:
                # p-testi korral ei saa kustutada enne, kui mõlemad sisestajad
                # on sisestanud, sest sisestused võivad erineda
                _remove_old_var(tos)

        # arvutame soorituse max pallid
        tos.calc_max_pallid()

        # soorituse pallid muudame ainult siis, kui töö on hinnatud
        if h_staatus == const.H_STAATUS_HINNATUD:
            # arvutame õigete ja valede vastuste arvud ning õigete suhte
            tos.calc_vastustearvud()
            if testiosa.on_alatestid:
                # arvutame alatestide pallid ja protsendid kokku
                is_delf = 'DELFscolaire' in test.nimi
                pallid = tos.calc_alatestitulemus(pallid, is_delf)

            # arvutame yhisosa pallid
            self._update_yhisosa(tos, h_staatus)
                
            # muudame soorituse pallid
            if testiosa.skoorivalem and pallid is not None:
                # arvutame testiosa pallid valemiga
                # SKOOR - alatestidega testis alatestide tulemuste summa,
                #         alatestideta testis ülesannete pallide summa
                e_locals = {'SKOOR': pallid}
                pallid, err0, err, buf1 = model.eval_formula(testiosa.skoorivalem, e_locals, divzero=0)
                log.info('s_id=%s: %s' % (tos.id, buf1))
                max_pallid = tos.max_pallid
                if pallid and pallid > max_pallid:
                    log.error('testiosa %d sooritus %d arvutatud tulemus %s, lubatud max %s' % \
                              (tos.testiosa_id, tos.id, pallid, max_pallid))
                    pallid = max_pallid
                if pallid:
                    pallid = round(pallid + .0001)

            if on_tseis and pallid:
                pallid = round(pallid + .000001)            
            if pallid and pallid < 0:
                pallid = 0
            if test.diagnoosiv:
                pallid = None

            tos.pallid = pallid
            
            # liidame kokku testiosa arvutipallid ja käsitsipallid
            kasitsi1 = kasitsi2 = None
            # ylesannete pallid
            qs = (model.SessionR.query(sa.func.sum(model.Ylesandevastus.pallid_arvuti),
                                      sa.func.sum(model.Ylesandevastus.pallid_kasitsi))
                  .filter(model.Ylesandevastus.sooritus_id==tos.id))
            if self.on_jagatudtoo:
                qs = (qs.filter(model.Ylesandevastus.kehtiv==True)
                      .filter(model.Ylesandevastus.muudetav==False))
            for r in qs.all():
                tos.pallid_arvuti = r[0]
                kasitsi1 = r[1]

            # kriteeriumite pallid
            qs = (model.SessionR.query(sa.func.sum(model.Kriteeriumivastus.pallid))
                  .filter(model.Kriteeriumivastus.sooritus_id==tos.id))
            for r in qs.all():
                kasitsi2 = r[0]
            if kasitsi1 is not None or kasitsi2 is not None:
                tos.pallid_kasitsi = (kasitsi1 or 0) + (kasitsi2 or 0)

            _set_protsent(tos)

        if is_update_sooritaja:
            self.update_sooritaja(sooritaja)

    def update_sooritaja(self, sooritaja):
        "Sooritaja kirje oleku muutmine peale hindamist"

        def _calc_keeletase(test, sooritaja):
            # leiame keeleoskuse taseme
            keeletase_kood = None
            for testitase in test.testitasemed:
                # testitase.pallid on tegelikult protsendid, millest rohkem peab sooritaja taseme pälvimiseks saama
                if testitase.pallid is None:
                    # EH-342 - kui taseme protsenti pole antud, siis meie taset ei arvuta
                    break
                if not testitase.pallid or sooritaja.tulemus_protsent is not None and testitase.pallid - .0001 < sooritaja.tulemus_protsent:
                    keeletase_kood = testitase.keeletase_kood

                    # kui mõni osaoskus on 0, siis taset ei saa (EH-189)
                    # välja arvatud need alatestid/testiosad, milles polegi võimalik rohkem kui 0p saada (ES-4075)
                    for tos in sooritaja.sooritused:
                        if tos.staatus != const.S_STAATUS_VABASTATUD and tos.max_pallid != 0:
                            if not tos.pallid:
                                keeletase_kood = None
                                break
                            for atos in tos.alatestisooritused:
                                if atos.staatus != const.S_STAATUS_VABASTATUD:
                                    if not atos.pallid and atos.alatest.max_pallid:
                                        # sooritaja ei saanud alatesti eest punkte, aga alatest annab punkte (pole nt küsitlus)
                                        keeletase_kood = None
                                        break
                    break
                
            if not keeletase_kood and sooritaja.keeletase_kood:
                # kui siin ei anta taset, siis vaatame, kas see on tulnud rv eksamilt
                for rvs in sooritaja.rvsooritajad:
                    if rvs.keeletase_kood == sooritaja.keeletase_kood:
                        # rv eksam on sama taseme andnud, ei muuda taset
                        keeletase_kood = sooritaja.keeletase_kood
                        break
            return keeletase_kood

        def _calc_hinne(test, sooritaja):
            # leiame hinde
            hinne = None
            if sooritaja.tulemus_protsent is not None:
                auto_hinne = False
                for testihinne in test.testihinded:
                    # testihinne.pallid on tegelikult protsendid, millest rohkem peab sooritaja hinde pälvimiseks saama
                    auto_hinne = True
                    if not testihinne.pallid or testihinne.pallid - .0001 < sooritaja.tulemus_protsent:
                        hinne = testihinne.hinne
                        break
                if not auto_hinne:
                    # hinnet ei saa arvutada, kasutame seda, mis on käsitsi sisestatud
                    hinne = sooritaja.hinne
                log.debug('sooritaja %s, pallid %s, protsent %s, hinne %s' % \
                          (sooritaja.id, sooritaja.pallid, sooritaja.tulemus_protsent, hinne))
            return hinne

        def _calc_protsent(test, sooritaja, osapallid, max_osapallid):
            if sooritaja.mujalt_tulemus:
                max_pallid = sooritaja.max_pallid
                pallid = sooritaja.pallid
                protsent = pallid * 100. / max_pallid
            else:
                protsent = osapallid * 100. / max_osapallid
                max_pallid = sooritaja.max_pallid
                if max_pallid == max_osapallid:
                    # ei ole yhestki osast vabastatud või pole riigieksam
                    pallid = osapallid
                else:
                    # riigieksam, kus sooritaja on mõnest osast vabastatud
                    pallid = protsent * max_pallid / 100.
                        
                if test.ymardamine:
                    pallid = round(pallid + .0001)
                    #sooritaja.tulemus_protsent = round(protsent + .0001)
                    protsent = pallid * 100. / max_pallid
            sooritaja.tulemus_protsent = protsent
            if sooritaja.pallid != pallid:
                if not (sooritaja.pallid is not None and pallid is not None and \
                        abs(sooritaja.pallid - pallid) < .0001):
                    # kui pallid muutusid
                    sooritaja.teavitatud_epost = None
                sooritaja.pallid = pallid

        def _calc_piisav(test, sooritaja):
            # teeme märke, kas eksam on sooritatud positiivselt
            # (kui testile on seatud lävi - seda esineb TE, SE testiliikide korral)
            piisav = None
            if test.lavi_pr is not None and sooritaja.tulemus_protsent is not None:
                # kui testile on seatud läbisaamise lävi, siis märgime, kas tulemus on piisav
                piisav = False
                if sooritaja.tulemus_protsent > test.lavi_pr - 0.500001:
                    piisav = True
                    for sooritus in sooritaja.sooritused:
                        if sooritus.staatus == const.S_STAATUS_VABASTATUD:
                            continue
                        # ükski osatulemus ei tohi olla 0
                        if sooritus.staatus != const.S_STAATUS_TEHTUD or \
                          not sooritus.tulemus_protsent or not (sooritus.tulemus_protsent > .499999):
                            piisav = False
                            break

                        for alatestisooritus in sooritus.alatestisooritused:
                            if alatestisooritus.staatus == const.S_STAATUS_VABASTATUD:
                                continue
                            if alatestisooritus.staatus != const.S_STAATUS_TEHTUD or \
                              not alatestisooritus.tulemus_protsent or \
                              not (alatestisooritus.tulemus_protsent > 0.499999):
                                piisav = False
                                break                            
                log.debug('piisav=%s' % piisav)
            if sooritaja.tulemus_piisav != piisav:
                sooritaja.tulemus_piisav = piisav

        def _calc_osapallid(test, sooritaja):
            min_h_staatus = max_h_staatus = None
            osapallid = 0 # sooritaja pallide summa testis
            yhisosa_pallid = None # yhisossa kuuluvate kysimuste pallide summa
            for tos in sooritaja.sooritused:
                if tos.staatus > const.S_STAATUS_POOLELI:
                    # sooritus on läbi
                    if tos.staatus == const.S_STAATUS_TEHTUD:
                        # sooritus on tehtud, tarvis oli hinnata
                        h_staatus = tos.hindamine_staatus
                        t_pallid = tos.pallid
                    
                        if h_staatus >= const.H_STAATUS_HINNATUD:
                            osapallid += t_pallid or 0
                            if tos.yhisosa_pallid is not None:
                                yhisosa_pallid = (yhisosa_pallid or 0) + tos.yhisosa_pallid
                    else:
                        # sooritus on katkestatud või kõrvaldatud või eemaldatud või vabastatud, saab 0p
                        h_staatus = const.H_STAATUS_HINNATUD
                        t_pallid = 0

                    # sooritus on tehtud
                    if min_h_staatus is None or min_h_staatus > h_staatus:
                        min_h_staatus = h_staatus
                    if max_h_staatus is None or max_h_staatus < h_staatus:
                        max_h_staatus = h_staatus

                else:
                    # sooritus on veel pooleli ja ei saa palle kokku arvutada
                    min_h_staatus = const.H_STAATUS_HINDAMATA

            if sooritaja.mujalt_tulemus:
                # tulemus kantud yle rv tunnistuselt
                h_staatus = const.H_STAATUS_HINNATUD
            else:
                if min_h_staatus is None:
                    h_staatus = const.H_STAATUS_HINDAMATA
                #if max_h_staatus == const.H_STAATUS_TOOPUUDU:
                if max_h_staatus == const.H_STAATUS_TOOPUUDU and self.test.id != 9220: # ES-3361 ajutine häkk
                    h_staatus = max_h_staatus
                elif max_h_staatus and max_h_staatus > const.H_STAATUS_HINDAMATA and \
                  min_h_staatus == const.H_STAATUS_HINDAMATA:
                    h_staatus = const.H_STAATUS_POOLELI
                else:
                    h_staatus = min_h_staatus

                if sooritaja.staatus in (const.S_STAATUS_PUUDUS, const.S_STAATUS_REGATUD, const.S_STAATUS_ALUSTAMATA):
                    # kui pole ühelgi testiosal osalenud, siis on pallid None, mitte 0
                    h_staatus = const.H_STAATUS_HINDAMATA
                    osapallid = None

                if sooritaja.staatus == const.S_STAATUS_TEHTUD and h_staatus != const.H_STAATUS_HINNATUD:
                    osapallid = None
                if test.diagnoosiv:
                    osapallid = yhisosa_pallid = None
            return h_staatus, osapallid, yhisosa_pallid
 
        test = self.test
        max_osapallid = sooritaja.max_osapallid
        h_staatus, osapallid, yhisosa_pallid = _calc_osapallid(test, sooritaja)
        sooritaja.hindamine_staatus = h_staatus
        sooritaja.osapallid = osapallid
        sooritaja.yhisosa_pallid = yhisosa_pallid
            
        if h_staatus == const.H_STAATUS_HINNATUD:
            # kui on hinnatud, siis muudame tulemuse
            if osapallid is None or not max_osapallid \
              or (sooritaja.mujalt_tulemus and sooritaja.pallid is None):
                sooritaja.tulemus_protsent = sooritaja.hinne = None
            else:
                _calc_protsent(test, sooritaja, osapallid, max_osapallid)
                sooritaja.keeletase_kood = _calc_keeletase(test, sooritaja)
                sooritaja.hinne = _calc_hinne(test, sooritaja)            

            _calc_piisav(test, sooritaja)
            if sooritaja.staatus == const.S_STAATUS_TEHTUD \
              and not test.diagnoosiv:
                for tos in sooritaja.sooritused:
                    # arvutame normipunktid
                    npc = Npcalc(self.handler, test, tos.testiosa, sooritaja, tos)
                    npc.calc_npvastused()
        
    def _update_yhisosa(self, tos, staatus):
        "Testiosasoorituse ja sellest alamate soorituste juures kitsa/laia matemaatika ühisosa tulemuse arvutamine"
        params = {'sooritus_id': tos.id}

        if tos.staatus == const.S_STAATUS_EEMALDATUD:
            tos.yhisosa_pallid = 0
            
        elif staatus != const.H_STAATUS_HINNATUD:
            sql = "UPDATE ylesandevastus SET yhisosa_pallid=NULL "+\
                  "WHERE sooritus_id=:sooritus_id"
            model.Session.execute(model.sa.text(sql), params)

            tos.yhisosa_pallid = None

        else:
            sql = "UPDATE ylesandevastus SET yhisosa_pallid="+\
                  "CASE WHEN (ty.yhisosa_kood IS NULL OR ty.yhisosa_kood='') THEN NULL ELSE (SELECT sum(kv.pallid) "+\
                  "FROM kysimusevastus kv, kysimus k, tulemus t "+\
                  "WHERE ylesandevastus.id=kv.ylesandevastus_id "+\
                  "AND kv.kysimus_id=k.id "+\
                  "AND k.tulemus_id=t.id "+\
                  "AND t.yhisosa_kood IS NOT NULL AND t.yhisosa_kood<>'') END "+\
                  "FROM testiylesanne ty "+\
                  "WHERE ylesandevastus.sooritus_id=:sooritus_id "+\
                  "AND ylesandevastus.testiylesanne_id=ty.id "
            model.Session.execute(model.sa.text(sql), params)

            sql = "SELECT sum(yv.yhisosa_pallid) "+\
                  "FROM ylesandevastus yv "+\
                  "WHERE yv.sooritus_id=:sooritus_id "
            tos.yhisosa_pallid = model.Session.execute(model.sa.text(sql), params).scalar()

                
    def update_hindamisolek(self, sooritaja, sooritus, holek, force=False, is_update_sooritus=True, force_yv=None, tyy_id=None):
        "Hindamisoleku kirje oleku muutmine peale hindamist"
        # sisestuserinevus - kas antud liiki hindamise sisestamine I ja II erinevad
        # kutsub avalik/shindamine/hindamised
        # kutsub avalik/khindamine/hindamised
        # kutsub: ekk.hindamine.arvutused

        # kui on sisestuserinevus, siis salvestame selle mõlema antud antud liigi hindamise sisestamise kirje juures
        # kas on alatestidega test ja kas on selle hindamiskogumi alateste sooritanud
        testiosa = self.testiosa
        test = self.test
        self.on_diagnoosiv = test.diagnoosiv

        hkogum = model.Hindamiskogum.get(holek.hindamiskogum_id)
        hindamiskogum_id = hkogum and hkogum.id or None
        mittekasitsi = False

        buf = f'Hindamisolek {holek.id} (hk {hkogum and hkogum.tahis}, sooritus {sooritus.tahised} {sooritus.id})'
        log.debug(buf)
        
        logparam = f'holek={holek.id} sooritus={sooritus.id}'
        if sooritus.staatus in (const.S_STAATUS_PUUDUS, const.S_STAATUS_EEMALDATUD):
            puudus = True
        else:
            if sooritus.staatus != const.S_STAATUS_TEHTUD:
                buf += ' soorituse olek %s' % sooritus.staatus_nimi
                self._trace(buf, logparam, 'update_hindamisolek')
                return
            # kui sooritus on tehtud, siis ei saa olla pooleli alatestisooritusi
            for atos in sooritus.alatestisooritused:
                if atos.staatus == const.S_STAATUS_POOLELI:
                    atos.staatus = const.S_STAATUS_TEHTUD
            # alatestidega testiosa korral vaatame, kas on vähemalt mõnel selle hindamiskogumi alatestil osalenud
            # e-testi korral saame kontrollida ka ylesannete kaupa
            puudus = sooritus.check_hk_puudus(hkogum, testiosa, sooritus.hindamiskogumita)
            
        if holek.hindamisprobleem == const.H_PROBLEEM_TOOPUUDU:
            # töö puudub, pole midagi teha
            buf += ' toopuudu'
            self._trace(buf, logparam, 'update_hindamisolek')
            return

        if sooritus.ylesanneteta_tulemus:
            # hindamisi ei ole, ylesannete hinded on sisestatud otse toimumise protokolli
            buf += '\nülesanneteta tulemus'
            self._trace(buf, logparam, 'update_hindamisolek')
            return

        if not puudus:
            # testimiskorraga testi hindamina, võib olla mitu hindamist
            # leitakse hindamisprobleemid, lähtudes algsest hindamisoleku hindamistasemest
            buf += self._loplik_hindamine(sooritaja, sooritus, holek, force, hkogum, testiosa)

        # arvutatakse tulemused, puudumise korral luuakse kv kirjed
        self.calc_holek(sooritaja, sooritus, holek, testiosa, force, force_yv=force_yv, tyy_id=tyy_id)
        # tagame, et yv.pallid on kettale kirjutatud
        model.Session.flush()
        
        mittekasitsi = False
        if not puudus and testiosa.vastvorm_kood in (const.VASTVORM_KE, const.VASTVORM_SE, const.VASTVORM_I):
            # kontrollime yle, kas käsitsi hindamine on veel vajalik
            q = (model.Session.query(model.sa.func.count(model.Ylesandevastus.id))
                 .filter(model.Ylesandevastus.sooritus_id==sooritus.id)                 
                 .filter(model.Ylesandevastus.loplik==True)                 
                 .join((model.Valitudylesanne,
                        model.Valitudylesanne.id==model.Ylesandevastus.valitudylesanne_id))
                 )

            if hindamiskogum_id:
                # pole hindamiskogumita hindamisolek
                if testiosa.lotv:
                    q = q.filter(model.Valitudylesanne.hindamiskogum_id==hindamiskogum_id)
                else:
                    q = (q.join((model.Testiylesanne,
                                 model.Testiylesanne.id==model.Ylesandevastus.testiylesanne_id))
                         .filter(model.Testiylesanne.hindamiskogum_id==hindamiskogum_id))
            q1 = q.filter(model.Ylesandevastus.mittekasitsi==False)
            # ylesandevastus.mittekasitsi võib vajada ise muutmist juhul,
            # kui mittekasitsi=False, aga ei ole arvutihindamata kysimustevastuseid
            q2 = q1.filter(model.Ylesandevastus.kysimusevastused.any(
                model.Kysimusevastus.arvutihinnatud==False))
            mittekasitsi = (q2.scalar() == 0)

        holek.puudus = puudus
        holek.mittekasitsi = puudus or mittekasitsi

        if holek.mittekasitsi or holek.puudus:
            # kui pole midagi hinnata
            holek.hindamisprobleem = const.H_PROBLEEM_POLE
            holek.staatus = const.H_STAATUS_HINNATUD
            holek.selgitus = None
            log.debug('holek %s tase %s > %s' % (holek.id, holek.hindamistase, const.HTASE_ARVUTI))
            holek.hindamistase = const.HTASE_ARVUTI

        if holek.puudus:
            # kui on alatestidega test ja selle hindamiskogumi kõik ülesanded
            # kuuluvad sellistesse alatestidesse, mida sooritaja ei teinud,
            # siis ei ole midagi hinnata, saab hindamiskogumi eest 0p.
            holek.pallid = holek.toorpunktid = 0

        if holek.hindamisprobleem:
            # hindamine on pooleli, sest on probleeme
            if holek.staatus != const.H_STAATUS_HINDAMATA:
                if len(holek.hindamised) == 0:
                    holek.staatus = const.H_STAATUS_HINDAMATA
                else:
                    holek.staatus = const.H_STAATUS_POOLELI

            if holek.hindamisprobleem == const.H_PROBLEEM_HINDAMISERINEVUS and \
                   test.testiliik_kood == const.TESTILIIK_TASE and \
                   holek.hindamistase < const.HINDAJA3:
                # tasemeeksami hindamiserinevuste korral loome kohe kolmanda hindamise kirjed,
                # kuna tasemeeksami korral hindajaid ette ei määrata
                holek.give_hindamine3(None, None)
        else:
            # kui on kõik vajalikud hindamised olemas ja sisestatud,
            # siis on soorituse hindamiskogum hinnatud
            holek.staatus = const.H_STAATUS_HINNATUD
            buf1 = 'Hindamiskogumi %s pallid: %s mittekasitsi=%s\n' % (hkogum and hkogum.tahis or '', holek.pallid, holek.mittekasitsi)
            log.debug(buf1)
            buf += '\n' + buf1

        self._trace(buf, logparam, 'update_hindamisolek')
        if is_update_sooritus:
            self.update_sooritus(sooritaja, sooritus)
        
    def _loplik_hindamine(self, sooritaja, sooritus, holek, force, hkogum, testiosa):
        """Kontrollitakse, kas kõik vajalikud hindamised on olemas ja kas on hindamisprobleem.
        """
        buf = ''
        # vaatame, millist liiki ja sisestusega hindamised on kinnitatud
        hindamised_sis1 = {} # hindamiste I sisestus
        hindamised_sis2 = {} # hindamiste II sisestus
        for h in holek.hindamised:
            if h.staatus == const.H_STAATUS_HINNATUD and not h.tyhistatud:
                # suuliste hindajate gruppide ID-d erinevad kirjalike hindajate gruppidest
                liik = h.liik
                if h.sisestus == 1:
                    hindamised_sis1[liik] = h
                elif h.sisestus == 2:
                    hindamised_sis2[liik] = h
                if force:
                    # arvutame iga hindamise pallid uuesti kokku
                    # arvestame, et peale hindamise sisestamist võidi muuta koefitsiente
                    self._calc_hindamine(sooritaja, sooritus, h, hkogum, testiosa)
                    
        if hindamised_sis1:
            buf1 = 'olemas I sisestus hindamistele: %s' % ','.join([str(l) for l in hindamised_sis1])
            log.debug(buf1)
            buf += '\n' + buf1
        if hindamised_sis2:
            buf1 = 'olemas II sisestus hindamistele: %s' % ','.join([str(l) for l in hindamised_sis2])
            log.debug(buf1)
            buf += '\n' + buf1

        # vaatame, millist liiki hindamised peavad olemas olema
        liigid = [] # kohustuslikud hindamise liigid, millest moodustatakse lõplik tulemus
        arvestamata_liigid = [] # kohustuslikud liigid, mida tulemuses ei arvestata
        if holek.hindamistase == const.HINDAJA1:
            # peab olema I hindamise kirje
            liigid.append(const.HINDAJA1)
        elif holek.hindamistase == const.HINDAJA2:
            # peavad olema I ja II hindamise kirjed
            liigid.append(const.HINDAJA1)
            liigid.append(const.HINDAJA2)
        elif holek.hindamistase == const.HINDAJA3:
            liigid.append(const.HINDAJA1)
            if sooritaja.valimis:
                kkh = hkogum and hkogum.kahekordne_hindamine_valim
            else:
                kkh = hkogum and hkogum.kahekordne_hindamine
            if kkh:
                # kui hindamiskogum on mõeldud kahekordseks hindamiseks, siis toimub tavaline kolme hindajaga hindamine:
                # leitakse sarnaseim hindamiste paar ja nende põhjal määratakse lõplik hinne
                liigid.append(const.HINDAJA2)
                liigid.append(const.HINDAJA3)
            else:
                # kui II hindamist pole olemas, aga III hindamine on, siis määrab lõpliku hinde I hindaja
                # (III hindamine tehakse selleks, et seda võrrelda süsteemiväliselt I hindamisega)
                arvestamata_liigid = [const.HINDAJA3]
        elif holek.hindamistase == const.HINDAJA4:
            # peab olema eksperthindamine, IV hindamine
            liigid.append(const.HINDAJA4)
        elif holek.hindamistase == const.HINDAJA5:
            # peab olema eksperthindamine vaide korral
            liigid.append(const.HINDAJA5)
        elif holek.hindamistase == const.HINDAJA6:
            # peab olema eksperthindamine, VI hindamine
            liigid.append(const.HINDAJA6)            

        buf1 = 'Hindamistasemel %s on vaja hindamisi: %s' % (holek.hindamistase, ','.join([str(l) for l in liigid]))
        log.debug(buf1)
        buf += '\n' + buf1

        # kontrollime, et kõik vajalikud hindamised on olemas
        # ja nendega pole probleeme
        vastvorm_kood = testiosa.vastvorm_kood
        hindamisprobleem = 0
        selgitus = None

        # need hindamise kirjed, millest tuleb lõplik tulemus; yldiselt yks kirje, 
        # aga kolmekordse hindamise korral tuleb lõplik tulemus kahest hindamisest
        hindamine1 = hindamine2 = None

        ta = sooritus.toimumisaeg or sooritus.toimumisaeg_id and model.Toimumisaeg.get(sooritus.toimumisaeg_id)
                
        kahekordne_sisestamine = ta and ta.kahekordne_sisestamine
        for liik in liigid:
            h = hindamised_sis1.get(liik)
            #log.debug('Hindamisolek %d, liik %d, hindamine %s' % (holek.id, liik, h and h.id))
            if not h:
                selgitus = _("Sisestamata hindamine {s}").format(s=liik)
                log.debug('Hindamisolek %s: %s' % (holek.id, selgitus))
                hindamisprobleem = const.H_PROBLEEM_SISESTAMATA
                break
            elif h.sisestuserinevus:
                selgitus = _("Sisestuserinevus hindamisel {s}").format(s=liik)
                hindamisprobleem = const.H_PROBLEEM_SISESTUSERINEVUS
                break
            if h.komplekt_id != holek.komplekt_id and holek.komplekt_id:
                selgitus = _("Hinnati erinevaid komplekte")
                log.debug('Hindamine %s komplekt %s (%s), hindamisolek %s komplekt %s (%s)' % \
                              (h.id, h.komplekt_id, h.komplekt and h.komplekt.tahis, 
                               holek.id, holek.komplekt_id, holek.komplekt.tahis))
                hindamisprobleem = const.H_PROBLEEM_SISESTUSERINEVUS
                break
            if kahekordne_sisestamine:
                # kahekordset sisestust on vaja siis, 
                # kui toimumisaja juures on kahekordse sisestamise märge 
                # ja on olemas esimene sisestaja (st kui on olnud e-hindamine, siis ei ole sisestajaid üldse)
                # ja kui pole eksperthindamine (ekspert sisestab süsteemi)
                vaja_sisestus2 = vastvorm_kood in (const.VASTVORM_KP, const.VASTVORM_SP)\
                                 and h.sisestaja_kasutaja_id != None and liik < const.HINDAJA4
                if vaja_sisestus2:
                    # peab olema teine sisestus
                    h2 = hindamised_sis2.get(liik)
                    if not h2:
                        selgitus = _("Sisestamata hindamine {s}, sisestus 2").format(s=liik)
                        hindamisprobleem = const.H_PROBLEEM_SISESTAMATA
                        break

            # jätame meelde viimase hindamise kui lõpliku
            hindamine1 = h

        for liik in arvestamata_liigid:
            h = hindamised_sis1.get(liik)
            if not h:
                selgitus = _("Sisestamata hindamine {s}").format(s=liik)
                log.debug('Hindamisolek %s: %s' % (holek.id, selgitus))
                hindamisprobleem = const.H_PROBLEEM_SISESTAMATA

        if len(liigid) <= 1:
            # kui on yhekordne hindamine või eksperthindamine, siis pole hindamiserinevusi
            holek.hindamiserinevus = None

        elif not hindamisprobleem or liik == const.HINDAJA3:
            # hindamiserinevusi kontrollime ainult siis,
            # kui on mitmekordne hindamine (ja pole eksperthindamist)

            # kui seni probleeme pole, siis kontrollime, 
            # kas eri hindajate hindamiserinevus on lubatud piirides;
            # kui probleem on kolmanda hindamisega, 
            # siis kontrollime, kas kolmandat hindamist on ikka vaja

            # leiame kaks hindamist, mille hindepallide summade erinevus on väikseim
            # kui sama erinevusega on mitu, siis eelistame kõrgemaid palle
            diff = None # erinevus kahe valitud hindamise vahel
            p_sum = 0 # kahe valitud hindamise pallide summa
            hindamine1 = hindamine2 = hindamine3 = None # üks valitud hindamine

            # leiame parima hindamiste paari ja nende erinevuse diff
            for liik1, h1 in hindamised_sis1.items():
                for liik2, h2 in hindamised_sis1.items():
                    if hindamisprobleem and liik2 > const.HINDAJA2:
                        # kui kolmanda hindamisega on probleem, siis seda ei arvesta
                        continue
                    if liik2 > liik1: # et mitte kontrollida samu paare topelt
                        if liik2 == const.HINDAJA3:
                            # jätame meelde III hindamise
                            hindamine3 = h2
                        d = abs(h2.pallid - h1.pallid)
                        if diff is None or diff > d or \
                               diff == d and h2.pallid + h1.pallid > p_sum:
                            # parim hindamiste paar, millel on väikseim erinevus
                            # või millel on sama erinevus, aga kõrgemad pallid
                            hindamine1 = h1
                            hindamine2 = h2
                            diff = d
                            p_sum = hindamine1.pallid + hindamine2.pallid

            # leiame hindamisoleku max lubatud hindamiserinevuse pallides
            if hkogum and hkogum.hindajate_erinevus is not None:
                # lubatud hindamiste erinevus on määratud
                max_diff = hkogum.max_pallid * hkogum.hindajate_erinevus / 100. + 1e-12
                buf1 = 'Hindamiserinevus %s, lubatud %s' % (fstr(diff),fstr(max_diff))
            else:
                max_diff = None
                buf1 = 'Lubatud hindamiserinevuse piir on seadmata'
            log.debug(buf1)
            buf += '\n' + buf1
            if hindamisprobleem and diff is not None and (max_diff is None or diff < max_diff) \
                   and holek.min_hindamistase <= const.HINDAJA2:
                # kolmanda hindamisega oli probleem, aga kolmandat hindamist polegi vaja
                buf1 = 'Tühistame hindamistaseme 3, uus tase on 2'
                log.debug(buf1)
                buf += '\n' + buf1
                holek.hindamistase = const.HINDAJA2
                hindamisprobleem = 0
                selgitus = None
                for hindamine3 in list(holek.hindamised):
                    if hindamine3.liik == const.HINDAJA3:
                        hindamine3.delete()
                hindamine3 = None
            elif max_diff is not None:
                if holek.hindamistase == const.HINDAJA3 and hkogum and hkogum.hindamine3_loplik and hindamine3:
                    # eesti keel teise keelena - hindamine III on lõplik
                    # ja seda ei võrrelda lähima I või II hindamisega
                    hindamine1 = hindamine3
                    hindamine2 = None
                elif max_diff < diff and not hindamisprobleem:
                    # hindajate erinevus on liiga suur
                    # (kui juba on leitud probleem, et III hindamine sisestamata,
                    # siis ei muuda hindamisprobleemi)
                    hindamisprobleem = const.H_PROBLEEM_HINDAMISERINEVUS
                    selgitus = _("Hindamiserinevus {s1}, lubatud {s2}").format(s1=fstr(diff), s2=fstr(max_diff))

            if hindamisprobleem:
                holek.hindamiserinevus = diff
            else:
                # pole probleemi
                holek.hindamiserinevus = None

        if hindamisprobleem:
            # ykski hindamine pole veel lõplik
            hindamine1 = hindamine2 = None

        # märgime, milliseid hindamisi arvestatakse ja milliseid mitte
        for h in holek.hindamised:
            h.loplik = h == hindamine1 or h == hindamine2

        if holek.hindamistase == const.HINDAJA5 and not hindamisprobleem:
            # kas vaideotsuse eelnõu on loodud?
            on_eelnou = (model.Session.query(sa.func.count(model.Vaie.id))
                         .filter(model.Vaie.sooritaja_id==sooritus.sooritaja_id)
                         .filter(model.Vaie.h_arvestada==True)
                         .scalar())
            if on_eelnou == 0:
                # kui eelnõu on koostamata, siis vaidehindamist ei arvestata
                # ja tööl ei ole punkte
                selgitus = _("Eelnõu koostamata")
                hindamisprobleem = const.H_PROBLEEM_VAIE

        # jätame hindamisprobleemi meelde
        holek.hindamisprobleem = hindamisprobleem
        holek.selgitus = selgitus
        
        buf1 = 'Hindamisprobleem: %s %s' % (hindamisprobleem, selgitus or '')
        log.debug(buf1)
        buf += '\n' + buf1
        return buf
       
    def _calc_hindamine(self, sooritaja, sooritus, hindamine, hkogum, testiosa):
        """Arvutame hindepallid hinnete toorpunktides,
           arvestades, et koefitsient võib olla muutunud
        """
        # võtame selle ylesande hinded nendest hindamistest, mis on kehtivad
        hindamine_pallid = 0
        prev_id = None
        if hkogum and hkogum.on_kriteeriumid:
            # hinnatakse kriteeriumite kaupa
            for hinne in hindamine.kriteeriumihinded:
                if hinne.id == prev_id:
                    continue
                prev_id = hinne.id
                hindamine_pallid += hinne.pallid or 0
        else:
            # hinnatakse ylesannete kaupa
            for hinne in hindamine.ylesandehinded:
                if hinne.id == prev_id:
                    # väldime sama kirje mitmekordset arvestamist (kohe peale kirje loomist)
                    continue
                prev_id = hinne.id
                self._calc_hindamine_yhinne(sooritaja, sooritus, hinne, hindamine.liik, testiosa)
                hindamine_pallid += hinne.pallid or 0

        hindamine.pallid = hindamine_pallid
        return hindamine.pallid

    def _calc_hindamine_yhinne(self, sooritaja, sooritus, hinne, liik, testiosa):
        vy = hinne.valitudylesanne
        ty = vy.testiylesanne
        arvutus = ty.hindamiskogum.arvutus_kood
        on_aspektid = on_kysimused = False

        a_toorpunktid = a_pallid = 0
        for ah in set(hinne.aspektihinded):
            # hindaja on hinnanud aspekte
            hindamisaspekt = ah.hindamisaspekt or model.Hindamisaspekt.get(ah.hindamisaspekt_id)
            if hindamisaspekt.ylesanne_id != vy.ylesanne_id:
                ah.delete()
                continue
            ah_kaal_punktid = (ah.toorpunktid or 0) * (hindamisaspekt.kaal or 1)
            ah.pallid = ah_kaal_punktid * (vy.koefitsient or 0)
            #toorpunktid += ah.toorpunktid or 0
            a_toorpunktid += ah_kaal_punktid
            a_pallid += ah.pallid or 0
            on_aspektid = True

        if not on_aspektid:
            sisestusviis = self.sisestusviis or ty.sisestusviis
            if testiosa.vastvorm_kood in (const.VASTVORM_SP, const.VASTVORM_SH) \
              or (testiosa.vastvorm_kood == const.VASTVORM_KP and sisestusviis == const.SISESTUSVIIS_PALLID):
                # kui on p-testi pallide sisestamine või suuline hindamine,
                # siis ei ole kysimuste tasemel punkte ja ei saa neid kokku lugeda
                return hinne.pallid
            
            for kh in set(hinne.kysimusehinded):
                # hindaja on hinnanud kysimusi
                if kh.kysimusevastus.kysimus.sisuplokk.ylesanne_id != vy.ylesanne_id:
                    kh.delete()
                    continue
                kh.pallid = (kh.toorpunktid or 0) * (vy.koefitsient or 0)
                #toorpunktid += kh.toorpunktid or 0
                #pallid += kh.pallid or 0
                on_kysimused = True

        yv = hinne.ylesandevastus
        ty = yv.testiylesanne
        ylesanne = vy.ylesanne
        k_pallid, k_toorpunktid, pallid_arvuti, pallid_kasitsi, tp_arvuti, tp_kasitsi = \
            self._calc_ty_kysimused(sooritaja, sooritus, yv, ty, yv.valitudylesanne, oige=None, yhinne=hinne)
        if k_toorpunktid is not None:
            k_toorpunktid = max(0, k_toorpunktid)
        if k_pallid is not None:
            k_pallid = max(0, k_pallid)

        #log.debug(f'calc_hindamine_yhinne#{hinne.id} on_a={on_aspektid} on_k={on_kysimused} k_pallid={k_pallid} a_pallid={a_pallid}')
        if on_aspektid:
            # on hinnatud aspekte
            hinne.toorpunktid_kasitsi = a_toorpunktid
            hinne.pallid_kasitsi = a_pallid
            sm = a_toorpunktid + (tp_arvuti or 0)
            hinne.toorpunktid = max(sm, 0)
            sm = a_pallid + (pallid_arvuti or 0)
            hinne.pallid = max(sm, 0)
            yv = None
        elif on_kysimused:
            # on hinnatud kysimusi
            hinne.toorpunktid_kasitsi = tp_kasitsi
            hinne.pallid_kasitsi = pallid_kasitsi
            hinne.toorpunktid = k_toorpunktid
            hinne.pallid = k_pallid
        else:
            if len(ylesanne.hindamisaspektid) > 0 and len(yv.vastusaspektid) > 0:
                # kui on vaide korral hindamine ja tulemust pole muudetud,
                # siis ei ole aspektide kaupa hinnete kirjeid olemas,
                # võtame punktid kehtivast tulemusest
                # (ei saa toorpunktidest arvutada, sest aspektidel võivad kaalud olla)
                pallid = yv.pallid
                pallid_kasitsi = yv.pallid_kasitsi
                if pallid_kasitsi is None and pallid:
                    # juhuks, kui on hinnatud enne tööd ES-1234
                    pallid_kasitsi = pallid
                    
                if arvutus == const.ARVUTUS_SUMMA and pallid:
                    pallid /= 2.
                    pallid_kasitsi /= 2.

                hinne.pallid_kasitsi = pallid_kasitsi
                hinne.pallid = pallid
            else:
                # aspekte pole - arvutame pallid toorpunktidest
                hinne.toorpunktid_kasitsi = tp_kasitsi
                hinne.toorpunktid = k_toorpunktid
                hinne.pallid = (hinne.toorpunktid or 0) * (vy.koefitsient or 0)
                hinne.pallid_kasitsi = (hinne.toorpunktid_kasitsi or 0) * (vy.koefitsient or 0)
                
        if (hinne.toorpunktid or 0) > (ylesanne.max_pallid or 0) + .00001:
            ik = sooritaja and sooritaja.kasutaja.isikukood
            raise Exception('%s soorituse %s ülesande %s tulemus liiga suur (%s > %s)' % \
                       (ik, sooritus and sooritus.tahised, ylesanne.id, fstr(hinne.toorpunktid), fstr(ylesanne.max_pallid)))
        return hinne.pallid

    def _get_komplekt(self, tos, hindamiskogum):
        """Leitakse komplekt hindamisolekule, kus komplekt puudus.
        Vajalik selleks, et luua ylesandevastuste kirjed ja neid statistikas arvestada.
        """
        komplekt = None
        
        # leiame komplektivaliku
        kvalik = None
        for ty in hindamiskogum.testiylesanded:
            alatest = ty.alatest
            if alatest:
                kvalik = alatest.komplektivalik
            else:
                for kvalik2 in ty.testiosa.komplektivalikud:
                    if kvalik2.kursus_kood == tos.sooritaja.kursus_kood:
                        kvalik = kvalik2
                        break
        if not kvalik:
            # testi struktuur on puudulik
            return

        # komplekt peab olema soorituskomplekti kirjes olemas
        for sk in model.Soorituskomplekt.get_by_sooritus(tos.id):
            if sk.komplektivalik_id == kvalik.id:
                komplekt = sk.komplekt
                break

        # if not komplekt:
        #     # vaatame, kas sama komplektivaliku mõnes teises hindamiskogumis on komplekt olemas
        #     for holek2 in tos.hindamisolekud:
        #         komplekt2 = holek2.komplekt
        #         if komplekt2 and komplekt2.komplektivalik == kvalik:
        #             komplekt = komplekt2
        #             break

        if not komplekt:
            # ei olnud komplekt valitud, valime nyyd
            if tos.toimumisaeg:
                ta_komplektid = list(tos.toimumisaeg.komplektid)
                komplektid = [k for k in kvalik.komplektid if k in ta_komplektid]
            else:
                komplektid = list(kvalik.komplektid)
            cnt = len(komplektid)
            if cnt == 1:
                # oligi ainult yks komplekt
                komplekt = komplektid[0]
            # mitme komplekti korral tagantjärele valikut ei toimu
        return komplekt

    def calc_holek(self, sooritaja, sooritus, holek, testiosa, force=False, force_yv=None, tyy_id=None):
        """Soorituse ühe hindamiskogumi kõigi ülesannete lõplike hindepallide arvutamine.
        force_yv - kui on antud ja force==False, siis arvutada ainult see ylesandevastus
        tyy_id - kui on antud, siis arvutada ainult need testiylesanded
        Peale esmast arvutamist on vaja uuesti arvutada, kui:
        - ülesande hindamismaatriksit muudetakse;
        - ülesande vastuseid muudetakse.
        """
        # kutsub: avalik.sooritamine.lahendamine
        pallid = toorpunktid = 0
        hindamiskogum = model.Hindamiskogum.get(holek.hindamiskogum_id)
        komplekt = holek.komplekt
        if not komplekt and hindamiskogum:
            komplekt = holek.komplekt = self._get_komplekt(sooritus, hindamiskogum)

        komplekt_id = komplekt and komplekt.id or None
        on_valimikoopia = holek.hindamistase == const.HTASE_VALIMIKOOPIA

        if hindamiskogum and hindamiskogum.on_kriteeriumid:
            # hindamine hindamiskriteeriumitega
            pallid, toorpunktid = self._calc_kr_hinded_hindamistest(sooritus, holek, hindamiskogum)
        else:
            # hindamine ylesannete kaupa
            if not hindamiskogum:
                liy = [(ty, None) for ty in sooritus.testiosa.testiylesanded]
            elif not testiosa.lotv:
                liy = [(ty, None) for ty in hindamiskogum.testiylesanded]
            else:
                liy = [(vy.testiylesanne, vy) for vy in hindamiskogum.valitudylesanded if vy.komplekt_id==komplekt_id]

            # üle soorituse kõigi ülesannete selles hindamiskogumis
            for ty, vy in liy:
                # leiame ylesandevastuse
                #log.debug(f'hkogum {hindamiskogum and hindamiskogum.tahis} komplekt {komplekt_id} ty {ty.id} vy {vy and vy.id} force {force}')
                ylesandevastus = ExamSaga(self.handler).sooritus_get_ylesandevastus(sooritus, ty.id, komplekt_id=komplekt_id, vy=vy)
                if not vy and ylesandevastus:
                    vy = model.Valitudylesanne.get(ylesandevastus.valitudylesanne_id)
                if komplekt and not vy:
                    vy = komplekt.get_valitudylesanne(None, ty.id)
                    if ty.on_jatk:
                        # diagnoosiva testi jätkuylesanne ei pea olema tehtud
                        ylesandevastus = ExamSaga(self.handler).sooritus_get_ylesandevastus(sooritus, ty.id, komplekt_id=komplekt.id)
                    elif not self.on_jagatudtoo:
                        log.error(f'ylesandevastus puudub sooritus {sooritus.id} vy {vy and vy.id}')
                        # puudub nt suulise vastamise korral, luuakse alles siin
                        ylesandevastus = sooritus.give_ylesandevastus(ty.id, vy.id)
                        
                if ylesandevastus and vy and vy.ylesanne_id:
                    # liidame pallid
                    if tyy_id and ty.id not in tyy_id or \
                      not force and ylesandevastus.staatus == const.B_STAATUS_KEHTIV and ylesandevastus != force_yv:
                        # kui arvutatakse kindlaid ylesandeid ja see pole nende seast
                        # või kui ylesande pallid on juba arvutatud ja rohkem ei arvutata
                        y_pallid = ylesandevastus.pallid
                        y_toorpunktid = ylesandevastus.toorpunktid
                    else:
                        # arvutame ylesande pallid
                        y_pallid, y_toorpunktid = self._calc_ty(sooritaja, sooritus, ylesandevastus, ty, vy, testiosa, on_valimikoopia, holek)
                    # liidame pallid (kui seni pole olnud hindamata ylesandeid või on jagatud töö)
                    if pallid is not None:
                        if y_pallid is not None and y_toorpunktid is not None:
                            pallid += ylesandevastus.pallid
                            toorpunktid += ylesandevastus.toorpunktid
                        elif not self.on_jagatudtoo:
                            # jagatud töö kogupunktid loeme kokku ka siis, kui kõik ylesanded pole veel tehtud
                            # testide punkte ei loe, kui mõni ylesanne on hindamata
                            pallid = None
                            toorpunktid = None
                    log.debug(f'  ty {ty.tahis} {ty.id} yv {ylesandevastus.id} pallid={ylesandevastus.pallid}')
            # # jagatudtoo?
            # if pallid is None:
            #     holek.hindamisprobleem = const.H_PROBLEEM_SISESTAMATA
            # else:
            #     holek.hindamisprobleem = const.H_PROBLEEM_POLE
                 
        # soorituse pallid kõigi selle hindamiskogumi ylesannete eest
        if pallid and pallid < 0:
            pallid = toorpunktid = 0

        holek.pallid = pallid
        holek.toorpunktid = toorpunktid
        
    def _calc_ty(self, sooritaja, sooritus, ylesandevastus, ty, vy, testiosa, on_valimikoopia=False, holek=None):
        """Arvutame lõplikud hindepallid üle kõigi hindamiste.
        """
        log.debug('TY %s (Y %s)' % (ty.tahis, vy.ylesanne_id))
        ylesanne = vy.ylesanne
        on_aspektid = ylesanne and len(ylesanne.hindamisaspektid) > 0
        on_yl_p = False
        sisestusviis = self.sisestusviis or ty.sisestusviis
        pallid = toorpunktid = pallid_kasitsi = toorpunktid_kasitsi = None
        if sisestusviis == const.SISESTUSVIIS_OIGE:
            # sisestatud on õige/vale ja on arvutihinnatav
            oige = True
        elif sisestusviis == const.SISESTUSVIIS_VASTUS and ylesanne.arvutihinnatav:
            # sisestatud on vastused ja on arvutihinnatav
            if self.sisestusviis:
                # kirjalik e-test
                oige = False
            else:
                # vastused sisestatakse - sel juhul ei pruugi alati olla vastuste sisestamine,
                # sest osadel sisuplokityypidel (vabatekstilistel) vastuseid ei sisestata
                oige = None
        else:
            # sisestusviis == const.SISESTUSVIIS_PALLID or not ty.arvutihinnatav
            # sisestatud on hinded
            # aga mitte-arvutihinnatavas ylesandes võib olla 
            # sellegipoolest mõni kysimus arvutihinnatav
            if not on_valimikoopia:
                pallid_kasitsi, tp_kasitsi = self._calc_ty_hinded_hindamistest(ylesandevastus, ty, vy)
                log.debug('  hindamistest yv.mittekasitsi=%s, kasitsi=%s' % (ylesandevastus.mittekasitsi, fstr(pallid_kasitsi)))
                if ylesandevastus.mittekasitsi:
                    pallid_kasitsi = tp_kasitsi = 0
            else:
                pallid_kasitsi, tp_kasitsi = ylesandevastus.pallid_kasitsi, ylesandevastus.toorpunktid_kasitsi

            if sisestusviis == const.SISESTUSVIIS_PALLID and testiosa.vastvorm_kood in (const.VASTVORM_KP, const.VASTVORM_SP, const.VASTVORM_SH):
                # kui on p-testi pallide sisestamine, siis ei ole kysimuste tasemel punkte
                on_yl_p = True
            if on_aspektid or on_yl_p or not len(ylesandevastus.kysimusevastused):
                # kui hinnatakse aspekte, siis on siin aspektide summa
                # kui pole kysimustevastuseid, siis on siin ylesandehinnete summa
                ylesandevastus.pallid_kasitsi = pallid_kasitsi
                ylesandevastus.toorpunktid_kasitsi = tp_kasitsi
                ylesandevastus.staatus = const.B_STAATUS_KEHTIV     
                if pallid_kasitsi is not None:
                    sm = pallid_kasitsi + (ylesandevastus.pallid_arvuti or 0)
                    ylesandevastus.pallid = max(sm, 0)
                    if tp_kasitsi is not None:
                        sm = tp_kasitsi + (ylesandevastus.toorpunktid_arvuti or 0)
                        ylesandevastus.toorpunktid = max(sm, 0)
                log.debug('  asp/sis pallid=%s kokku=%s' % (fstr(pallid_kasitsi), fstr(ylesandevastus.pallid)))
            # siis loeme kokku kysimuste kaupa antud punktid
            oige = False

        # kas on hinnatud?
        pallid, toorpunktid, arvuti, kasitsi, tp_arvuti, tp_kasitsi =\
            self._calc_ty_vastused(sooritaja, sooritus, ylesandevastus, ty, vy, oige)
        if pallid is not None:
            pallid = max(pallid, 0)
        if toorpunktid is not None:
            toorpunktid = max(toorpunktid, 0)
        ylesandevastus.pallid_arvuti = arvuti
        ylesandevastus.toorpunktid_arvuti = tp_arvuti
        log.debug('  kysimuste pallid=%s tp=%s (a=%s k=%s tp_a=%s tp_k=%s)' % \
                  (fstr(pallid), fstr(toorpunktid),
                   fstr(arvuti), fstr(kasitsi),
                   fstr(tp_arvuti), fstr(tp_kasitsi)))
        if vy.koefitsient == 0:
            ylesandevastus.pallid = ylesandevastus.toorpunktid = 0
        elif on_valimikoopia:
            # mitte yle kirjutada algselt toimumisajalt kopeeritud hindeid
            if tp_arvuti is not None and ylesandevastus.toorpunktid_kasitsi is not None:
                ylesandevastus.toorpunktid = tp_arvuti + ylesandevastus.toorpunktid_kasitsi
                ylesandevastus.pallid = arvuti + ylesandevastus.pallid_kasitsi
        elif on_aspektid or on_yl_p:
            # käsitsi punkte ei saa kysimuste vastustest, sest on p-test või on aspektid
            if ylesandevastus.pallid_kasitsi is not None:
                # käsitsi on juba hinnatud
                sm = (arvuti or 0) + ylesandevastus.pallid_kasitsi
                ylesandevastus.pallid = max(sm, 0)
                if ylesandevastus.toorpunktid_kasitsi is not None:
                    sm = (tp_arvuti or 0) + ylesandevastus.toorpunktid_kasitsi
                    ylesandevastus.toorpunktid = max(sm, 0)
                else:
                    ylesandevastus.toorpunktid = None
            elif not (holek and holek.hindamistase == const.HINDAJA5):
                # (vaidehindamisel ei tohiks punktid puududa, sest vaikimisi kehtivad algsed punktid)
                # käsitsi ei ole veel hinnatud, ylesande tulemus ei ole teada
                ylesandevastus.pallid = ylesandevastus.toorpunktid = None
        else:
            # käsitsi punktid loeti nyyd kokku kysimuste hinnetest
            ylesandevastus.toorpunktid_kasitsi = tp_kasitsi
            ylesandevastus.pallid_kasitsi = kasitsi
            ylesandevastus.toorpunktid = toorpunktid
            ylesandevastus.pallid = pallid
        log.debug('  kokku=%s' % fstr(ylesandevastus.pallid))

        ylesandevastus.staatus = const.B_STAATUS_KEHTIV
        ylesandevastus.calc_max_pallid(ty.id, vy.id)

        return ylesandevastus.pallid, ylesandevastus.toorpunktid

    def _calc_kr_hinded_hindamistest(self, sooritus, holek, hindamiskogum):
        """Arvutame lõplikud hindepallid kriteeriumite hinnetest
        """
        # võtame selle ylesande hinded nendest hindamistest, mis on kehtivad
        hindamised = [h for h in holek.hindamised \
                       if h.pallid is not None and \
                       h.loplik and \
                       h.staatus == const.H_STAATUS_HINNATUD and\
                       h.sisestus == 1]
        log.debug('holek %d kr hindamisi %d' % (holek.id, len(hindamised)))
        
        pallid = None # lõplikud hindepallid
        toorpunktid = None
        aspektipallid = {} # ylesande lõplikud aspektide pallid 
        aspektipunktid = {}
        arvutus_kood = hindamiskogum.arvutus_kood
        
        hindamine1 = len(hindamised) >= 1 and hindamised[0] or None
        hindamine2 = len(hindamised) >= 2 and hindamised[1] or None

        if hindamine1:
            # viimane eksperthindamine või ainuke hindamine üldse
            pallid = hindamine1.pallid
            toorpunktid = 0
            for ah in hindamine1.kriteeriumihinded:
                aspektipallid[ah.hindamiskriteerium_id] = ah.pallid or 0
                aspektipunktid[ah.hindamiskriteerium_id] = ah.toorpunktid or 0
                toorpunktid += ah.toorpunktid or 0
                if not hindamine2 and arvutus_kood == const.ARVUTUS_SUMMA:
                    # arvutusviis eeldab kahte hindamist, aga on üksainus hindamine
                    # arvestame ainukest hindamist topelt
                    aspektipallid[ah.hindamiskriteerium_id] *= 2
                    aspektipunktid[ah.hindamiskriteerium_id] *= 2
                    
            if not hindamine2 and arvutus_kood == const.ARVUTUS_SUMMA:
                # eksperthindamine sellises hindamiskogumis, kus kahe hindaja punktid liidetakse
                pallid *= 2
                toorpunktid *= 2
                
        if hindamine2:
            # aluseks võetav hindamiste paar
            toorpunktid2 = 0
            for ah in hindamine2.kriteeriumihinded:
                if ah.hindamiskriteerium_id not in aspektipallid:
                    aspektipallid[ah.hindamiskriteerium_id] = 0
                    aspektipunktid[ah.hindamiskriteerium_id] = 0
                aspektipallid[ah.hindamiskriteerium_id] += ah.pallid or 0
                aspektipunktid[ah.hindamiskriteerium_id] += ah.toorpunktid or 0
                if arvutus_kood != const.ARVUTUS_SUMMA:
                    aspektipallid[ah.hindamiskriteerium_id] /= 2.
                    aspektipunktid[ah.hindamiskriteerium_id] /= 2.
                toorpunktid2 += ah.toorpunktid or 0
            pallid += hindamine2.pallid
            toorpunktid += toorpunktid2
            if arvutus_kood != const.ARVUTUS_SUMMA:
                pallid /= 2.
                toorpunktid /= 2.
            
        kriteeriumivastused = []
        for ha_id in aspektipallid:
            krv = sooritus.give_kriteeriumivastus(ha_id)
            krv.pallid = aspektipallid[ha_id]
            krv.toorpunktid = aspektipunktid[ha_id]
            kriteeriumivastused.append(krv)
        for krv in sooritus.kriteeriumivastused:
            if krv not in kriteeriumivastused:
                hkriteerium = krv.hindamiskriteerium
                if hkriteerium.hindamiskogum_id == hindamiskogum.id:
                    krv.delete()
        log.debug('hkogum %s pallid=%s, punktid=%s' % (hindamiskogum.tahis, pallid, toorpunktid))
        return pallid or 0, toorpunktid or 0

    def _calc_ty_hinded_hindamistest(self, ylesandevastus, ty, vy):
        """Arvutame lõplikud hindepallid hinnetest
        """
        # võtame selle ylesande hinded nendest hindamistest, mis on kehtivad
        hinne1 = hinne2 = None
        for h in ylesandevastus.ylesandehinded:
            if h.pallid is not None:
                hindamine = h.hindamine
                log.debug(f'   yhinne#{h.id} liik={hindamine.liik} pallid={h.pallid} loplik={hindamine.loplik}')
                if hindamine.loplik and hindamine.staatus == const.H_STAATUS_HINNATUD and hindamine.sisestus == 1:
                    # leitud kehtiv hindamine
                    if not hinne1:
                        hinne1 = h
                    else:
                        hinne2 = h
                        break

        pallid_kasitsi = toorpunktid_kasitsi = None
        aspektipallid = {} # ylesande lõplikud aspektide pallid 
        aspektipunktid = {} # ylesande lõplikud aspektide toorpunktid
        aspektinullip = {} # aspekti nullipõhjus
        hindamiskogum = ty.hindamiskogum
        arvutus_kood = hindamiskogum.arvutus_kood
        
        #log.debug('   calc_ty_hinded yv.id=%s ty.id=%s arvutus=%s hinne1.id=%s hinne2.id=%s' % \
        #          (ylesandevastus.id, ty.id, arvutus_kood, hinne1 and hinne1.id, hinne2 and hinne2.id))
        if hinne1:
            # viimane eksperthindamine või ainuke hindamine üldse
            toorpunktid_kasitsi = hinne1.toorpunktid_kasitsi
            pallid_kasitsi = hinne1.pallid_kasitsi 
            for ah in hinne1.aspektihinded:
                aspektipunktid[ah.hindamisaspekt_id] = ah.toorpunktid or 0
                aspektipallid[ah.hindamisaspekt_id] = ah.pallid or 0
                if ah.nullipohj_kood:
                    aspektinullip[ah.hindamisaspekt_id] = ah.nullipohj_kood
                if not hinne2 and arvutus_kood == const.ARVUTUS_SUMMA:
                    # arvutusviis eeldab kahte hindamist, aga on üksainus hindamine
                    # arvestame ainukest hindamist topelt
                    aspektipallid[ah.hindamisaspekt_id] *= 2
                    aspektipunktid[ah.hindamisaspekt_id] *= 2

            if not hinne2 and arvutus_kood == const.ARVUTUS_SUMMA:
                # eksperthindamine sellises hindamiskogumis, kus kahe hindaja punktid liidetakse
                pallid_kasitsi *= 2
                toorpunktid_kasitsi *= 2
            log.debug(f'   hinne1 {hinne1.id} pallid={fstr(hinne1.pallid)} kasitsi={fstr(hinne1.pallid_kasitsi)}')
            
        if hinne2:
            # aluseks võetav hindamiste paar
            if hinne2.toorpunktid_kasitsi is None:
                tos = ylesandevastus.sooritus
                msg = _("Töö {s1} hindamiskogum {s2} ülesanne {s3} on hindamata").format(
                    s1=tos.tahised, s2=hindamiskogum.tahis, s3=ty.tahis)
                log.error(msg + f', tos {tos.id}, yh {hinne2.id}')
                raise Exception(msg)
            toorpunktid_kasitsi += hinne2.toorpunktid_kasitsi
            pallid_kasitsi += hinne2.pallid_kasitsi
            if arvutus_kood != const.ARVUTUS_SUMMA:
                pallid_kasitsi /= 2.
                toorpunktid_kasitsi /= 2.

            for ah in hinne2.aspektihinded:
                if ah.hindamisaspekt_id not in aspektipallid:
                    aspektipallid[ah.hindamisaspekt_id] = 0
                    aspektipunktid[ah.hindamisaspekt_id] = 0

                aspektipunktid[ah.hindamisaspekt_id] += ah.toorpunktid or 0
                #ah.pallid = (ah.toorpunktid or 0) * (ah.hindamisaspekt.kaal or 1) * (vy.koefitsient or 0)
                aspektipallid[ah.hindamisaspekt_id] += ah.pallid or 0
                if ah.nullipohj_kood:
                    aspektinullip[ah.hindamisaspekt_id] = ah.nullipohj_kood
                
                if arvutus_kood != const.ARVUTUS_SUMMA:
                    aspektipallid[ah.hindamisaspekt_id] /= 2.
                    aspektipunktid[ah.hindamisaspekt_id] /= 2.
            log.debug(f'   hinne2 {hinne2.id} pallid={fstr(hinne2.pallid)} kasitsi={fstr(hinne2.pallid_kasitsi)}')
            
        vastusaspektid = []
        for ha_id in aspektipallid:
            vaspekt = ylesandevastus.give_vastusaspekt(ha_id)
            vaspekt.pallid = aspektipallid[ha_id]
            vaspekt.toorpunktid = aspektipunktid[ha_id]
            vaspekt.nullipohj_kood = aspektinullip.get(ha_id)
            vastusaspektid.append(vaspekt)
        for vaspekt in ylesandevastus.vastusaspektid:
            if vaspekt not in vastusaspektid:
                if vaspekt.hindamisaspekt.ylesanne_id != vy.ylesanne_id:
                    vaspekt.delete()

        # märgime inimhinnatud kysimuste lõplikud tulemused
        for kv in ylesandevastus.kysimusevastused:
            khinne1 = khinne2 = None
            if hinne1:
                for kh in kv.kysimusehinded:
                    if kh.ylesandehinne_id == hinne1.id:
                        khinne1 = kh
                        break
                #log.debug('kv %d khinne1 %s' % (kv.id, khinne1 and khinne1.id or '-'))
            if hinne2:
                for kh in kv.kysimusehinded:
                    if kh.ylesandehinne_id == hinne1.id:
                        khinne2 = kh
                        break
            if khinne1:
                ktoorpunktid = khinne1.toorpunktid or 0
                kpallid = khinne1.pallid or 0
                if khinne2:
                    ktoorpunktid += khinne2.toorpunktid or 0
                    kpallid += khinne2.pallid or 0
                    if ty.hindamiskogum.arvutus_kood != const.ARVUTUS_SUMMA:
                        ktoorpunktid /= 2.
                        kpallid /= 2.
                kv.pallid = kpallid
                kv.toorpunktid = ktoorpunktid
                kv.nullipohj_kood = khinne1.nullipohj_kood

                # märgime vastuse õigsuse
                tulemus = kv.kysimus.tulemus
                t_max_p = tulemus.get_max_pallid()
                if t_max_p is not None and ktoorpunktid > t_max_p - .001:
                    ks_oige = const.C_OIGE
                elif ktoorpunktid > 0:
                    ks_oige = const.C_OSAOIGE
                else:
                    ks_oige = const.C_VALE
                for ks in kv.kvsisud:
                    if ks.oige is None or ks.oige in (const.C_OIGE, const.C_OSAOIGE, const.C_VALE):
                        #log.debug('OIGE HINNE %s=%s' % (ks.id, ks_oige))
                        ks.oige = ks_oige
        log.debug(f'   kasitsi={fstr(pallid_kasitsi)}')
        return pallid_kasitsi, toorpunktid_kasitsi

    def _yv_to_obj(self, yv):
        responses = {}
        for kv in yv.kysimusevastused:
            if kv.sisestus == 1:
                kysimus = kv.kysimus
                if kysimus:
                    kood = kysimus.kood
                    responses[kood] = kv
        return yv, responses
        
    def _calc_ty_kysimused(self, sooritaja, sooritus, ylesandevastus, ty, vy, oige=False, yhinne=None):
        """Arvutame kysimuste tulemused
        oige - True=arvutada õige/vale järgi; False=vastuste järgi; None=sisestatud vastuste järgi
        
        #yhinded - hindajate poolt antud kehtivad hinded, 
        #millest võtta mitte-arvutihinnatavate kysimuste tulemused
        """
        toorpunktid = 0 # terve ylesande punktid
        koef = vy.koefitsient or 0

        tp_arvuti = tp_kasitsi = arvuti = kasitsi = None
        yv, responses = self._yv_to_obj(ylesandevastus)

        if responses and self.testiosa.vastvorm_kood not in (const.VASTVORM_SH, const.VASTVORM_SP):
            blockcalc = BlockCalc(self.handler)
            lang = sooritaja.lang
            
            toorpunktid, tp_arvuti, tp_kasitsi, max_pallid, buf, on_arvuti, on_kasitsi, f_locals = \
                blockcalc.calculate(vy.ylesanne, responses, lang, yv, oige, koefitsient=koef, testiosa=ty.testiosa, yhinne=yhinne)
            ylesandevastus.arvutuskaik = buf
            if not on_arvuti:
                tp_arvuti = None
        else:
            if yhinne:
                kasitsi = toorpunktid = yhinne.toorpunktid
            f_locals = {}
        if koef == 0:
            # testiylesanne, mis annab alati 0p
            pallid = toorpunktid = tp_arvuti = 0
        elif toorpunktid is not None:
            # kui testiylesande max pallid erinevad ylesande max pallidest,
            # siis arvutame pallid testiülesande skaala järgi ümber 
            pallid = toorpunktid * koef
        else:
            # ylesanne polnud yleni arvutihinnatav
            pallid = None

        if tp_arvuti is not None:
            arvuti = tp_arvuti * koef
        if tp_kasitsi is not None:
            kasitsi = tp_kasitsi * koef

        return pallid, toorpunktid, arvuti, kasitsi, tp_arvuti, tp_kasitsi

    def _calc_ty_vastused(self, sooritaja, sooritus, ylesandevastus, ty, vy, oige):
        """Arvutame lõplikud hindepallid vastustest (kysimuste punktidega ülesanded)
        oige - True=arvutada õige/vale järgi; False=vastuste järgi; None=sisestatud vastuste järgi
        """
        # moodustame igale kysimusele vastuse kirje, et statistikas kajastuks puuduvad vastused õigesti
        ylesanne = vy.ylesanne
        on_kysimusi = False
        for sp in ylesanne.sisuplokid:
            for kysimus in sp.kysimused:
                if kysimus.kood and kysimus.tulemus and not kysimus.pseudo:
                    ylesandevastus.give_kysimusevastus(kysimus.id)
                    on_kysimusi = True
        # kui ylesandes pole kysimusi, siis märgime, et ei vaja käsitsi hindamist
        if not on_kysimusi and not ylesandevastus.mittekasitsi and ylesanne.arvutihinnatav:
            ylesandevastus.mittekasitsi = True
        model.Session.flush()

        # arvutame
        return self._calc_ty_kysimused(sooritaja, sooritus, ylesandevastus, ty, vy, oige)

    def unresponded_zero(self, sooritus, hindamine, holek, hindamiskogum, ty_id=None):
        """Anname vastamate kysimuste eest automaatselt 0p
        ning märgime ära ülesandevastused, milles pole ühtki käsitsihinnatavat vastust
        """
        # ty_id - kui on yhe ylesande kaupa hindamine ja teisi ei vaadata

        komplekt = hindamine.komplekt or holek.komplekt
        if not komplekt:
            # arvatavasti on jätnud osa testist sooritamata
            # kas sama komplektivaliku mõnes teises hindamiskogumis on komplekt?
            komplekt = sooritus.get_komplekt_by_kv(hindamiskogum.komplektivalik_id)
            if komplekt:
                hindamine.komplekt = holek.komplekt = komplekt
            else:
                # ei tea komplekti
                log.info('ei tea komplekti sooritus %s hindamine %s hkogum %s' % \
                         (sooritus.id, hindamine.id, hindamiskogum.id))
                return []
        if ty_id:
            # yhe ylesande kaupa hindamine, teisi ei vaadata
            komplektis_ty_id = [ty_id]
        else:
            # hindamiskogumi kaupa hindamine
            komplektis_ty_id = komplekt.get_testiylesanded_id(hindamiskogum)

        def _on_kv_vastuseta(kv, tulemus):
            if kv.id:
                for kvs in kv.kvsisud:
                    if not kvs.on_vastuseta(tulemus):
                        # midagi on vastatud
                        return False
            return True

        # nende ty_id list, kus pole midagi hinnata
        ignore_ty_id = []

        for ty_id in komplektis_ty_id:
            ty = model.Testiylesanne.get(ty_id)

            # kas on käsitsi hinnatavaid vastuseid
            mitte_hinnata_kasitsi = True

            yv = ExamSaga(self.handler).sooritus_get_ylesandevastus(sooritus, ty.id, komplekt.id)
            if not yv and ty.on_jatk:
                ignore_ty_id.append(ty_id)
                continue
            elif not yv:
                vy = komplekt.get_valitudylesanne(None, ty_id)
            else:
                vy = yv.valitudylesanne
            ylesanne = vy.ylesanne
            if ylesanne.arvutihinnatav:
                ignore_ty_id.append(ty_id)
            else:
                if not yv:
                    if self.on_jagatudtoo:
                        continue
                    yv = sooritus.give_ylesandevastus(ty.id, vy.id)

                yhinne = hindamine.give_ylesandehinne(yv, vy)
                on_aspektid = vy.on_aspektid

                # vaatame ylesande kõik kysimused läbi, kas on vastatud
                o_vastatud = [] # vastatud mujal hinnatavate tulemuste id
                kvastused = [] # hinnatavad vastused
                for tulemus in ylesanne.tulemused:
                    if tulemus.oigsus_kysimus_id or not tulemus.arvutihinnatav:
                        for kysimus in tulemus.kysimused:
                            kv = yv.give_kysimusevastus(kysimus.id)
                            kv.vastuseta = _on_kv_vastuseta(kv, tulemus)
                                
                            if not tulemus.oigsus_kysimus_id:
                                # iseseisva hindamisega kysimus
                                kvastused.append((kv, kysimus))
                            elif not kv.vastuseta:
                                # mujal hinnatav kysimus, millel on vastus
                                o_vastatud.append(tulemus.id)
                                
                yv_mittekasitsi = True
                for kv, kysimus in kvastused:
                    if kv.vastuseta:
                        # kui kysimus on vastuseta, siis vaatame, kas
                        # muud sama maatriksiga hinnatavad kysimused on vastatud
                        kv_mittekasitsi = True
                        for t2 in kysimus.oigsus_tulemused:
                            if t2.id in o_vastatud:
                                # mõnele korraga hinnatavale kysimusele on vastatud
                                kv_mittekasitsi = False
                                break
                        if kv_mittekasitsi:
                            kv.arvutihinnatud = True
                            if not on_aspektid:
                                # kysimusele pole vastatud, anname 0p
                                khinne = yhinne.give_kysimusehinne(kv)
                                khinne.pallid = khinne.toorpunktid = 0
                                khinne.nullipohj_kood = const.NULLIPOHJ_VASTAMATA
                    if not kv.arvutihinnatud:
                        # mõnele kysimusele on vastatud ja pole hybriidhinnatud
                        yv_mittekasitsi = False

                # ARVUTIHINNATUD KYSIMUSTE ASPEKTHINDAMISE KORRAL
                #if yv_mittekasitsi and on_aspektid and not yv.vastuseta:
                #    # käsitsihinnatavaid kysimusi ei ole,
                #    # aga arvutihinnatud kysimustele on vastatud ja on aspektid
                #    yv_mittekasitsi = False
                if yv_mittekasitsi:
                    # ylesande yhelegi käsitsihinnatavale kysimusele pole vastatud
                    ignore_ty_id.append(ty_id)
                    if on_aspektid:
                        # käsitsi hinnatavatele kysimustele pole vastatud, anname 0p igale aspektile
                        for ha in ylesanne.hindamisaspektid:
                            ahinne = yhinne.give_aspektihinne(ha.id)
                            ahinne.pallid = ahinne.toorpunktid = 0
                            ahinne.nullipohj_kood = const.NULLIPOHJ_VASTAMATA

                    if yhinne.pallid is None:
                        # arvutihinnatavaid punkte pole veel lisatud
                        yhinne.pallid = yhinne.toorpunktid = 0
                        yhinne.pallid_kasitsi = yhinne.toorpunktid_kasitsi = 0
                    # märgime ylesandevastuse yle arvutamiseks
                    if yv.pallid is None:
                        yv.staatus = const.B_STAATUS_KEHTETU
                    yv.mittekasitsi = yv_mittekasitsi
                
        return ignore_ty_id

    def add_missing_kv(self, tos):
        """Tagantjärele tulemuste arvutamisel lisatakse 
        puuduvad kysimusevastuse kirjed (statistika jaoks).
        """
        if self.testiosa.vastvorm_kood not in (const.VASTVORM_KE, const.VASTVORM_SE, const.VASTVORM_I):
            # kui hindamiseks ei pea olema andmebaasis kysimuste vastuseid, siis ei tee midagi
            return
        if self.test.diagnoosiv:
            # d-testis ei lisata puuduvaid ylesandeid
            return
            
        # lisame ylesandevastuse kirjed,
        # kus ylesanne on jäänud avamata, aga komplekt on teada
        qf = (model.SessionR.query(model.Valitudylesanne)
              .join((model.Hindamisolek, sa.and_(model.Hindamisolek.sooritus_id==tos.id,
                                                 model.Hindamisolek.komplekt_id==model.Valitudylesanne.komplekt_id)))
              .filter(model.Valitudylesanne.seq==1)
              .filter(model.Valitudylesanne.ylesanne_id!=None)
              .filter(~ sa.exists().where(
                  sa.and_(model.Ylesandevastus.sooritus_id==tos.id,
                          model.Ylesandevastus.testiylesanne_id==model.Valitudylesanne.testiylesanne_id)))
              )
        for vy in qf.all():
            log.debug('lisan ylesandevastuse tos_id=%s vy_id=%s' % (tos.id, vy.id))
            yv = tos.give_ylesandevastus(vy.testiylesanne_id, vy.id)
            for sp in vy.ylesanne.sisuplokid:
                for kysimus in sp.kysimused:
                    tulemus = kysimus.tulemus
                    if kysimus.kood and tulemus and not kysimus.pseudo:
                        kv = yv.give_kysimusevastus(kysimus.id, 1)
                        if sp.tyyp != const.BLOCK_FORMULA:
                            kv.pallid = kv.toorpunktid = 0
                            kv.nullipohj_kood = const.NULLIPOHJ_VASTAMATA
                            kv.vastuseta = True
            yv.pallid = yv.toorpunktid = 0
            yv.vastuseta = yv.mittekasitsi = True

        # lisame kysimusevastuse kirjed nendele arvutatud väärtustele,
        # mis on lisatud ylesandesse alles peale sooritamist
        qf = (model.Session.query(model.Ylesandevastus, model.Kysimus)
              .filter(model.Ylesandevastus.sooritus_id==tos.id)
              .join((model.Valitudylesanne,
                     model.Valitudylesanne.id==model.Ylesandevastus.valitudylesanne_id))
              .join((model.Sisuplokk, model.Sisuplokk.ylesanne_id==model.Valitudylesanne.ylesanne_id))
              .filter(model.Sisuplokk.tyyp==const.BLOCK_FORMULA)
              .join(model.Sisuplokk.kysimused)
              .filter(~ model.Ylesandevastus.kysimusevastused.any(
                  model.Kysimusevastus.kysimus_id==model.Kysimus.id))
              )
        for yv, kysimus in qf.all():
            log.debug('lisan kysimuse %s' % kysimus.kood)
            yv.give_kysimusevastus(kysimus.id, 1)
        model.Session.flush()
    
    def _trace(self, sisu, param, tegevus):
        log.debug(f'trace {sisu} param={param} {tegevus}')
        if self.handler:
            self.handler.log_add(const.LOG_TRACE,
                                 sisu,
                                 param,
                                 tegevus=tegevus)
    
def _nullpunktid(s_toorpunktid):
    """Kasutajaliideses toorpunktide väljale sisestatud väärtuse
    teisendamine toorpunktideks ja nullipõhjuseks
    """
    if s_toorpunktid == const.PUNKTID_VASTAMATA:
        return 0, const.NULLIPOHJ_VASTAMATA
    else:
        return s_toorpunktid, None

