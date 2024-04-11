"""Registreerimise piirangute kontrollimise funktsioonid
"""
import itertools
from eis.lib.base import *
log = logging.getLogger(__name__)
_ = i18n._

def reg_ise_rv(handler, kasutaja_id, test, kord, for_sooritaja_id=None):
    # EH-301. õpilane ise ei tohi end saada registreerida:
    # - korraga yhe võõrkeele erineva tasemega rv eksamitele
    # - korraga vene ja saksa keele rv eksamitele
    d = date.today()            
    q = (model.SessionR.query(model.Sooritaja.id)
         .filter(model.Sooritaja.kasutaja_id==kasutaja_id)
         .filter(model.Sooritaja.staatus.in_((const.S_STAATUS_REGAMATA,
                                              const.S_STAATUS_TASUMATA,
                                              const.S_STAATUS_REGATUD)))
         .join(model.Sooritaja.test)
         .filter(model.Test.testiliik_kood==const.TESTILIIK_RV)
         .filter(model.Sooritaja.testimiskord_id!=kord.id)
         .join(model.Sooritaja.testimiskord)
         .filter(model.sa.or_(model.Sooritaja.staatus>=const.S_STAATUS_REGATUD,
                            model.sa.and_(model.Testimiskord.reg_sooritaja==True,
                                          model.Testimiskord.reg_sooritaja_kuni>=d)))
         )
    if for_sooritaja_id:
        q = q.filter(model.Sooritaja.id!=for_sooritaja_id)
    if q.filter(model.Test.aine_kood==test.aine_kood).count():
        return _('Ühe õppeaine mitmele rahvusvahelisele eksamile ei saa korraga registreerida')
    if test.aine_kood == const.AINE_RU:
        if q.filter(model.Test.aine_kood==const.AINE_DE).count():
            return _('Vene ja saksa keele rahvusvahelistele eksamitele ei saa korraga registreerida')
    elif test.aine_kood == const.AINE_DE:
        if q.filter(model.Test.aine_kood==const.AINE_RU).count():
            return _('Vene ja saksa keele rahvusvahelistele eksamitele ei saa korraga registreerida')

def err_rv_cae(handler, kasutaja, opilane):
    # ES-969, CAE testile saab registreerida ainult neid isikuid:
    # - kelle kohta on laaditud CAE eeltesti sooritamise märge
    # - kes on 11. või 12. klassi õpilane (G1, G2, G11 või G12) või kutsekooli 1,2,3 klassis (ES-1315)
    
    if not opilane or opilane.on_lopetanud:
        return _('Sellele testile saab registreerida ainult õpilasi')
    if not model.Caetestitud.get_by_ik(opilane.isikukood):
        return _('Sellele testile registreerimiseks on nõutav CAE eeltesti sooritamine')
    if opilane.klass not in ('11', 'G2','G3','G11','G12'):
        # kui ei ole 11.-12. kl õpilane, siis võib olla kutsekooli 2.-3. kursuse õpilane (ilma keskhariduseta)
        on_kutsetase = False
        if opilane.klass in ('1','2','3') and not opilane.on_lopetanud:
           on_kutsetase = model.Klrida.get_by_kood('KAVATASE',
                                                   opilane.oppekava_kood,
                                                   ylem_kood=const.OPPETASE_KUTSE)
           
        if not on_kutsetase:
            return _('Sellele testile saab registreerida ainult 11. või 12. klassi õpilasi')
        
def reg_rv_cae(handler, kasutaja_id, test, kord):
    # ES-969, CAE testile saab registreerida ainult neid isikuid:
    # - kelle kohta on laaditud CAE eeltesti sooritamise märge
    # - kes on 11. või 12. klassi õpilane (G1, G2, G11 või G12) või kutsekooli 1,2,3 klassis (ES-1315)
    # - kes ei ole varem registreeritud meie korraldatavatele CAE eksamitele.
    # Eelnevalt peab olema värskendatud EHISe puhver (kirje tabelis Opilane)!
    
    kasutaja = model.Kasutaja.get(kasutaja_id)
    opilane = kasutaja.opilane
    err = err_rv_cae(handler, kasutaja, opilane)
    if err:
        return err
        
    q = (model.SessionR.query(model.Sooritaja)
         .filter(model.Sooritaja.kasutaja_id==kasutaja_id)
         .join(model.Sooritaja.testimiskord)
         .filter(model.Testimiskord.cae_eeltest==True)
         .filter(model.Sooritaja.staatus>const.S_STAATUS_TYHISTATUD)
         .filter(model.Sooritaja.testimiskord_id!=kord.id))
    if q.count():
        return _('Sellele testile ei saa registreerida, sest isik on juba varem mõnele CAE eksamile registreeritud')
        
def reg_sisse(handler, kasutaja, test):
    # Gümnaasiumi sisseastumistestile saab regada 9. kl õpilasi
    TESTIKLASS9 = '9'
    if test.testiklass_kood == TESTIKLASS9:
        opilane = kasutaja.opilane
        if not opilane or opilane.on_lopetanud:
            return _('Sellele testile saab registreerida ainult õpilasi')
        if opilane.klass != TESTIKLASS9:
            return _('Sellele testile saab registreerida ainult 9. klassi õpilasi')
        
def reg_rven_cae(handler, kasutaja_id, test, testimiskorrad):
    # ES-1982:
    # - CAE testile ja ingl k riigieksamile ei või avalikus vaates korraga regada
    # - ingl k riigieksamile ei või avalikus vaates regada, kui CAE test on regatud/tehtud

    # testimiskorrad - korraga registreeritavad testimiskorrad, sellest sõltub teate sisu
    if test.testiliik_kood == const.TESTILIIK_RIIGIEKSAM:
        # see on riigieksam; kontrollida, kas CAE test on regatud/tehtud
        koos_cae = testimiskorrad and len([r for r in testimiskorrad if r.cae_eeltest]) > 0
        if koos_cae:
            # samal ajal pyyab mõlemale regada
            return _('Saad valida ainult ühe inglise keele eksami, kas CAE test või inglise keele riigieksam. ')

        q = (model.SessionR.query(model.Sooritaja)
             .filter(model.Sooritaja.kasutaja_id==kasutaja_id)
             .filter(model.Sooritaja.staatus > const.S_STAATUS_TYHISTATUD)
             .filter(model.Sooritaja.staatus != const.S_STAATUS_PUUDUS)
             .filter(model.Sooritaja.staatus != const.S_STAATUS_EEMALDATUD)
             .join(model.Sooritaja.test)
             .filter(model.Test.testiliik_kood==const.TESTILIIK_RV)
             .join(model.Sooritaja.testimiskord)
             .filter(model.Testimiskord.cae_eeltest==True)
             )
        if q.filter(model.Sooritaja.staatus == const.S_STAATUS_TEHTUD).count():
            return _('Inglise keele eksamile ei saa registreeruda, kuna on tehtud CAE eksam. ')
        elif q.count():
            return _('Inglise keele eksamile ei saa registreeruda, kuna on valitud CAE eksam. ')
            
    elif test.testiliik_kood == const.TESTILIIK_RV:
        # see on CAE; kontrollida, kas riigieksamile on regatud
        q = (model.SessionR.query(model.Sooritaja)
             .filter(model.Sooritaja.kasutaja_id==kasutaja_id)
             .filter(model.Sooritaja.staatus.in_((const.S_STAATUS_REGAMATA,
                                                  const.S_STAATUS_TASUMATA,
                                                  const.S_STAATUS_REGATUD)))
             .join(model.Sooritaja.test)
             .filter(model.Test.testiliik_kood==const.TESTILIIK_RIIGIEKSAM)
             .filter(model.Test.aine_kood==const.AINE_EN)
             .join(model.Sooritaja.testimiskord)
             )
        if q.count():
            return _('Saad valida ainult ühe inglise keele eksami, kas CAE test või inglise keele riigieksam. ')
                    
def reg_r_lisaeksam(handler, kasutaja_id, test, kord, for_sooritaja_id=None):        
    # riigieksamile ei saa regada seda, kes on samal testsessioonil sama aine riigieksamile registreeritud või selle teinud
    q = (model.SessionR.query(model.Sooritaja.id)
         .filter(model.Sooritaja.kasutaja_id==kasutaja_id)
         .filter(model.Sooritaja.staatus.in_((const.S_STAATUS_REGAMATA,
                                              const.S_STAATUS_TASUMATA,
                                              const.S_STAATUS_REGATUD,
                                              const.S_STAATUS_TEHTUD)))
         .join(model.Sooritaja.test)
         .filter(model.Test.testiliik_kood==const.TESTILIIK_RIIGIEKSAM)
         .join(model.Sooritaja.testimiskord)
         .filter(model.Testimiskord.testsessioon_id==kord.testsessioon_id)
         .filter(model.Test.aine_kood==test.aine_kood)
         .filter(model.Testimiskord.id!=kord.id)
         )
    if for_sooritaja_id:
        q = q.filter(model.Sooritaja.id!=for_sooritaja_id)
    if q.count():
        return _('Mitmele riigieksami testimiskorrale samas aines ei saa registreerida')

def on_riigikeeletase(kasutaja_id, tase):
    "Leitakse, kas kasutajal on riigikeeleoskuse tase"

    def _get_piisavad_tasemed(tase):
        tasemed = (const.KEELETASE_A1,
                   const.KEELETASE_A2,
                   const.KEELETASE_B1,
                   const.KEELETASE_B2,
                   const.KEELETASE_C1,
                   const.KEELETASE_C2)
        piisav = [r for r in tasemed if r >= tase]
    
        # vanad tasemed:
        # algtase - vastab B1 tasemele
        # kesktase - vastab B2 tasemele
        # kõrgtase - vastab C1 tasemele
        if tase <= const.KEELETASE_C1:
            piisav.append(const.KEELETASE_KORG)
            if tase <= const.KEELETASE_B2:
                piisav.append(const.KEELETASE_KESK)
                if tase <= const.KEELETASE_B1:
                    piisav.append(const.KEELETASE_ALG)
        return piisav

    piisav = _get_piisavad_tasemed(tase)
    q = (model.SessionR.query(model.Sooritaja.id)
         .filter(model.Sooritaja.kasutaja_id==kasutaja_id)
         .join(model.Sooritaja.test)
         .filter(model.Test.testiliik_kood.in_((const.TESTILIIK_TASE,
                                                const.TESTILIIK_RIIGIEKSAM,
                                                const.TESTILIIK_POHIKOOL)))
         .filter(model.Test.aine_kood.in_((const.AINE_ET2, const.AINE_RK)))
         .filter(model.Sooritaja.staatus==const.S_STAATUS_TEHTUD)
         .filter(model.Sooritaja.keeletase_kood.in_(piisav))
         )
    return q.count() > 0 

def on_eeltestitase(kasutaja_id, tase):
    "Leitakse, kas kasutajal on eesti keele teise keelena eeltest edukalt sooritatud"

    q = (model.SessionR.query(model.Sooritaja.id)
         .filter(model.Sooritaja.kasutaja_id==kasutaja_id)
         .join(model.Sooritaja.test)
         .filter(model.Test.testiliik_kood==const.TESTILIIK_EELTEST)
         .filter(model.Test.aine_kood==const.AINE_ET2)
         .filter(model.Sooritaja.staatus==const.S_STAATUS_TEHTUD)
         .filter(model.Sooritaja.keeletase_kood==tase)
         )
    return q.count() > 0 

def reg_et2(handler, kasutaja, test, opilane):
    # ES-2069
    # 1. B1-taseme eeltestile saab registreerida ainult 7. ja 8. klassi õpilasi. 
    # 2. B2-taseme eeltestile saab registreerida ainult 9. , 10. ja 11. klassi õpilasi, kellel on olemas B1-tase. 
    # 3. Põhikooli lõpeksamile saab lisaks 9. klassi õpilastele registreerida neid 7. ja 8. klassi õpilasi,
    #    kellel on edukalt sooritatud B1-taseme eeltest (23p/31p).
    # 4. Riigieksamile saab lisaks 12. klassi õpilastele ja varemlõpetanutele registreerida neid 9., 10. ja 11. klassi õpilasi,
    #    kellel on edukalt sooritatud B2-taseme eeltest (23p/31p) ja neil on B1-taseme tunnistus.
    
    if test.aine_kood != const.AINE_ET2:
        return
    klass = opilane and opilane.klass
    if opilane:
        on_kutsetase = model.Klrida.get_by_kood('KAVATASE',
                                                opilane.oppekava_kood,
                                                ylem_kood=const.OPPETASE_KUTSE)
        if on_kutsetase:
            # ES-2156: piirangud ei kehti kutsekooli õpilastele
            return
        
    if test.testiliik_kood == const.TESTILIIK_EELTEST:
        keeletase = test.keeletase_kood
        if keeletase == const.KEELETASE_B1:
            if klass not in ('7','8'):
                return _('B1-taseme eeltestile saab registreerida ainult 7. ja 8. klassi õpilasi')
        elif keeletase == const.KEELETASE_B2:
            if klass not in ('9','10','11','G1','G2','G10','G11'):
                return _('B2-taseme eeltestile saab registreerida ainult 9., 10. ja 11. klassi õpilasi')
            if not on_riigikeeletase(kasutaja.id, const.KEELETASE_B1):
                return _('B1-taseme eksam on sooritamata')

    elif test.testiliik_kood == const.TESTILIIK_POHIKOOL:
        if klass not in ('7','8','9'):
            return _('Eesti keele teise keelena põhikooli lõpueksamile saab registreerida ainult 7., 8. ja 9. klassi õpilasi')
        if klass in ('7','8') and not on_eeltestitase(kasutaja.id, const.KEELETASE_B1):
            return _('{klass}. klassi õpilase registreerimiseks vajalik B1-taseme eeltest on sooritamata').format(klass=klass)

    elif test.testiliik_kood == const.TESTILIIK_RIIGIEKSAM:
        if klass and klass not in ('12','G3','G12'):
            if klass not in ('9','10','11','G1','G2','G10','G11'):
                return _('Eesti keele teise keelena riigieksamile ei saa registreerida {klass}. klassi õpilasi').format(klass=klass)
            if not on_riigikeeletase(kasutaja.id, const.KEELETASE_B1):
                return _('{klass}. klassi õpilase registreerimiseks vajalik riigikeele B1-taseme eksam on sooritamata').format(klass=klass)
            if not on_eeltestitase(kasutaja.id, const.KEELETASE_B2):
                return _('{klass}. klasi õpilase registreerimiseks vajalik B2-taseme eeltest on sooritamata').format(klass=klass)
                                     
def reg_se_piirang1(handler, k_id, for_sooritaja_id=None):
    q = (model.Sooritaja.query
         .filter(model.Sooritaja.kasutaja_id==k_id)
         .filter(model.Sooritaja.staatus > const.S_STAATUS_TYHISTATUD)
         .join(model.Sooritaja.test)
         .filter(model.Test.testiliik_kood==const.TESTILIIK_SEADUS)
         .join(model.Sooritaja.testimiskord)
         .filter(model.Testimiskord.tulemus_kinnitatud==False))
    if for_sooritaja_id:
        q = q.filter(model.Sooritaja.id!=for_sooritaja_id)
    if q.count():
        return _('Uut avaldust ei saa esitada, kuna olete juba avalduse mõnele eelolevale eksamile esitanud')

def reg_te_piirang1(handler, k_id, for_sooritaja_id=None, app_ekk=False):
    # Isikut ei saa regada uuele tasemeeksamile, kui ta on juba mõnele regatud
    q = (model.Sooritaja.query
         .filter(model.Sooritaja.kasutaja_id==k_id)
         .filter(model.Sooritaja.staatus > const.S_STAATUS_TYHISTATUD)
         .join(model.Sooritaja.test)
         .filter(model.Test.testiliik_kood==const.TESTILIIK_TASE)
         .join(model.Sooritaja.testimiskord)
         .filter(model.Testimiskord.tulemus_kinnitatud==False))
    if for_sooritaja_id:
        q = q.filter(model.Sooritaja.id!=for_sooritaja_id)
    if q.count():
        if app_ekk:
            msg = _('Isik on juba esitanud avalduse mõnele tasemeeksamile, mille tulemused pole veel kinnitatud')
        else:
            msg = _('Uut avaldust ei saa esitada, kuna olete juba avalduse mõnele eelolevale eksamile esitanud')
        return msg

def reg_te_piirang(handler, kasutaja_id, for_sooritaja_id=None):
    "Tasemeeksamile registreerimise piirangud"
    
    dt_min = dt_today = date.today()
    piirang = None

    # kui isik on eksamilt puudunud (või tühist. peale eksamit)
    # peab kahe eksami vahele jääma vähemalt 6 kuud
    q = model.SessionR.query(sa.func.max(model.Sooritaja.algus)).\
        filter(model.Sooritaja.kasutaja_id==kasutaja_id).\
        filter(model.Sooritaja.staatus > const.S_STAATUS_TYHISTATUD).\
        join(model.Sooritaja.test).\
        filter(model.Test.testiliik_kood==const.TESTILIIK_TASE)
    q1 = q.filter(model.Sooritaja.staatus.in_((const.S_STAATUS_PUUDUS, const.S_STAATUS_EEMALDATUD)))
    dt = q1.scalar()

    if dt:
        dt = utils.add_months(dt, 6)
        if dt > dt_min:
            dt_min = dt
            piirang = _('isik on eksamilt puudunud, kahe eksami vahele peab jääma vähemalt 6 kuud')

    # kui isiku tulemus on alla 45 % maksimumist, peab kahe eksami vahele jääma vähemalt 6 kuud
    # kui tulemus pole veel avalikustatud, peab kahe eksami vahele jääma vähemalt 6 kuud
    # alates 2024 on piir 45% (ES-3937)
    MIN_PRO = 45
    q1 = q.join(model.Sooritaja.testimiskord).\
         filter(sa.or_(model.Sooritaja.tulemus_protsent < MIN_PRO,
                       model.Testimiskord.koondtulemus_avaldet==None,
                       model.Testimiskord.koondtulemus_avaldet==False))
    dt = q1.scalar()
    if dt:
        dt = utils.add_months(dt, 6)
        if dt > dt_min:
            dt_min = dt
            piirang = _('varasem tulemus on alla 45% või pole veel avaldatud, kahe eksami vahele peab jääma vähemalt 6 kuud')            

    # ...või muidu peab kahe eksami vahele jääma vähemalt 1 kuud:
    if for_sooritaja_id:
        q = q.filter(model.Sooritaja.id!=for_sooritaja_id)
    q1 = q.filter(model.Sooritaja.staatus>const.S_STAATUS_REGAMATA)
    dt = q1.scalar()
    if dt:
        dt = utils.add_months(dt, 1)
        if dt > dt_min:
            dt_min = dt
            piirang = _('1 kuu piirang kahe eksami vahel')

    return dt_min, piirang

def check_rv(handler, sooritaja, kasutaja):
    "Kontrollime, kas rv eksami jaoks vajalikud andmed on sisestatud"
    err = None
    test = sooritaja.test
    if test and test.testiliik_kood == const.TESTILIIK_RV:
        aine = test.aine_kood
        data = list()
        if aine == const.AINE_DE:
            synniriik = sooritaja.synnikoht_kodakond_kood
            data.append((synniriik, _("sünnikoha riik")))
        if aine == const.AINE_RU:
            data.append((sooritaja.eesnimi_ru, _("eesnimi vene keeles")))
            data.append((sooritaja.perenimi_ru, _("perekonnanimi vene keeles")))
        if aine == const.AINE_FR:
            data.append((sooritaja.rahvus_kood, _("rahvus")))
            synnikoht = sooritaja.synnikoht or kasutaja.synnikoht
            data.append((synnikoht, _("sünnikoht")))            
        missing = [label for value, label in data if not value]
        if len(missing):
            buf = ', '.join(missing)
            err = _("Registreeringut ei saa kinnitada. Sisestamata on {s}. Puuduvad andmed saab sisestada avalduse esitamisel.").format(s=buf)
    return err


def str_kohtaeg(testikoht_id, algus):
    "Soorituskoha ja -aja valikväljal kasutatav väärtus"
    key = '%s,%s' % (testikoht_id, algus.strftime('%y%m%d%H%M'))        
    return key

def parse_kohtaeg(value):
    "Valikvälja väärtuselt loetakse välja testikoha ID ja alguse aeg"
    try:
        testikoht_id, time_str = value.split(',')
        dt = datetime.strptime(time_str,'%y%m%d%H%M')
        return int(testikoht_id), dt
    except:
        return None, None

def get_kohtaeg_opt(handler, testimiskord_id, koht_id):
    """Leitakse soorituskohtade ja -aegade valik (kui testimiskord.reg_kohavalik=true)"""

    ylem_piirkonnad = {}
    def get_ylem_piirkonnad(piirkond_id):
        if piirkond_id:
            value = ylem_piirkonnad.get(piirkond_id)
            if not value:
                prk = model.Piirkond.get(piirkond_id)
                if not prk:
                    return
                li = prk.get_ylemad_id()
                value = ',' + ','.join(map(str, li)) + ','
                ylem_piirkonnad[piirkond_id] = value
            return value

    def get_ta_id():
        q = (model.SessionR.query(model.Toimumisaeg.id)
             .join(model.Toimumisaeg.testiosa)
             .filter(model.Testiosa.seq==1)
             .filter(model.Toimumisaeg.testimiskord_id==testimiskord_id))
        for ta_id, in q.all():
            return ta_id
            
    # leiame kõik soorituskohad ja kellaajad
    def list_opt(ta_id, koht_id):
        "Leiame esimese testiosa ajad"

        q = (model.SessionR.query(model.Testikoht.id,
                                 model.Testiruum.algus,
                                 model.Testiruum.lopp,
                                 model.Koht.nimi,
                                 model.Testiruum.bron_arv,
                                 model.Testiruum.kohti,
                                 model.Koht.piirkond_id)
             .filter(model.Testikoht.toimumisaeg_id==ta_id)
             .join(model.Testikoht.testiruumid)
             .join(model.Testikoht.koht)
             .filter(model.Testiruum.algus!=None)
             .order_by(model.Koht.nimi, model.Testiruum.algus)
             )
        if koht_id:
            # kui õpilast võib regada vaid ta enda kooli
            q = q.filter(model.Testikoht.koht_id==koht_id)
        li = list(q.all())
        data = []
        for (tkoht_id, algus, lopp), li1 in itertools.groupby(li, key=lambda r: (r[0], r[1], r[2])):
            # testikoha ja alguse kaupa grupeeritud
            key = str_kohtaeg(tkoht_id, algus)
            li1 = list(li1)
            for r in li1:
                nimi = r[3]
                piirkond_id = r[6]
                break

            # sooritajate arvud kokku
            values = [r[4] or 0 for r in li1]
            sooritajate_arv = sum(values)

            # kohtade arv kokku
            values = [r[5] for r in li1]
            if None in values:
                # kohtade arv on määramata
                kohti = None
            else:
                kohti = sum(values)

            kell = handler.h.str_from_datetime(algus, hour0=False)
            label = '%s %s' % (nimi, kell)
            if lopp and lopp.date() != algus.date():
                kell = handler.h.str_from_datetime(lopp, hour23=False)
                label += ' - %s' % (kell)

            desc = []
            if sooritajate_arv:
                desc.append(_("registreeritud {n}").format(n=sooritajate_arv))
            on_vaba = True
            if kohti is not None:
                vabu = kohti - (sooritajate_arv or 0)
                if vabu > 0:
                    desc.append(_("vabu kohti {n}").format(n=vabu))
                else:
                    on_vaba = False
                    desc.append(_("vabu kohti pole"))
            if desc:
                label += ' (%s)' % (', '.join(desc))

            attrs = {}
            if piirkond_id:
                attrs['data-piirkond'] = get_ylem_piirkonnad(piirkond_id)
            if not on_vaba:
                attrs['disabled'] = 'disabled'
                attrs['class'] = 'bg-gray-50'
            data.append((key, label, attrs))
        return data

    # toimumisaeg
    ta_id = get_ta_id()
    # kohtade ja aegade valikud
    li = list_opt(ta_id, koht_id)
    return li

def get_kohtaeg(handler, sooritaja, for_display=False):
    "Leitakse sooritaja koha ja aja väärtus valikus"
    # tekstina vt Sooritaja.kohavalik_nimi
    if sooritaja:
        q = (model.SessionR.query(model.Testiruum.testikoht_id,
                                 model.Testiruum.algus,
                                 model.Testiruum.lopp)
             .join(model.Testiruum.sooritused)
             .join(model.Sooritus.testiosa)
             .filter(model.Testiosa.seq==1)
             .filter(model.Testiruum.algus!=None)
             .filter(model.Sooritus.sooritaja_id==sooritaja.id))
        for tkoht_id, algus, lopp in q.all():
            value = str_kohtaeg(tkoht_id, algus)
            if for_display:
                # readonly väljal kuvamiseks
                tkoht = model.Testikoht.get(tkoht_id)
                aeg = handler.h.str_from_datetime(algus, hour0=False)
                if algus and lopp and lopp.date() != algus.date():
                    aeg = '%s - %s' % (aeg, handler.h.str_from_datetime(lopp, hour23=False))
                return value, tkoht.koht.nimi, aeg
            else:
                # valikvälja kehtiv valik
                return value
