# -*- coding: utf-8 -*-
"""Püsiandmete laadimine installimisel
"""
import logging
import datetime

from eis.model import *

def insert_klassifikaator():
    k = Klassifikaator(kood='AINE', nimi='Õppeaine')
    Klassifikaator(kood='TUNNAINE', nimi='Õppeaine nimetus tunnistusel')    
    Klassifikaator(kood='TEEMA', nimi='Teema', ylem_kood='AINE')
    Klassifikaator(kood='ALATEEMA', nimi='Alateema', ylem_kood='TEEMA')
    Klassifikaator(kood='OPIAINE', nimi='Õppeaine oppekava.edu.ee süsteemis')
    Klassifikaator(kood='OSKUS', nimi='Osaoskus', ylem_kood='AINE')
    Klassifikaator(kood='KEELETASE', nimi='Keeleoskuse tase', ylem_kood='AINE').lisaread(
        [Klrida(kood='A1', nimi='A1'),
         Klrida(kood='A2', nimi='A2'),
         Klrida(kood='B1', nimi='B1'),
         Klrida(kood='B2', nimi='B2'),
         Klrida(kood='C1', nimi='C1'),
         Klrida(kood='C2', nimi='C2'),
         Klrida(kood='1', nimi='algtase', kehtib=False, kuni='2008-01-01'),
         Klrida(kood='2', nimi='kesktase', kehtib=False, kuni='2008-01-01'),
         Klrida(kood='3', nimi='kõrgtase', kehtib=False, kuni='2008-01-01'),
         ])

    Klassifikaator(kood='KURSUS', nimi='Kursus', ylem_kood='AINE')
    Klassifikaator(kood='ASPEKT', nimi='Hindamisaspekt', ylem_kood='AINE')
    Klassifikaator(kood='ALATEST', nimi='Alatesti liik', ylem_kood='AINE')
    #Klassifikaator(kood=u'YLKOGU', nimi=u'Ülesannete kogu', ylem_kood='AINE')   
    Klassifikaator(kood='RVEKSAM', nimi='Rahvusvaheliselt tunnustatud eksamid')
    Klassifikaator(kood='HTUNNUS', nimi='Hinnatav tunnus tagasisidevormil', ylem_kood='AINE')    

    Klassifikaator(kood='RASKUSASTE', nimi='Raskusaste')
    Klassifikaator(kood='OPITULEMUS', nimi='Õpitulemus', ylem_kood='TEEMA')
    insert_ained(k)

    Klassifikaator(kood='AINEVALD', nimi='Ainevaldkond').lisaread(
        [Klrida(kood='keel', nimi='Keel ja kirjandus'),
         Klrida(kood='vrk', nimi='Võõrkeeled'),
         Klrida(kood='mat', nimi='Matemaatika'),
         Klrida(kood='loodus', nimi='Loodusained'),
         Klrida(kood='sots', nimi='Sotsiaalained'),
         Klrida(kood='knst', nimi='Kunstiained'),
         Klrida(kood='tehn', nimi='Tehnoloogia'),
         Klrida(kood='kehk', nimi='Kehaline kasvatus'),
         Klrida(kood='valik', nimi='Valikõppeained'),
         Klrida(kood='yle', nimi='Ainevaldkondade ülene'),         
         ])
    aine_vald = (('keel', ('E','ee','ki','W','vv','ss')),
                 ('vrk', ('R','I','S','V','P','fi','1')),
                 ('mat', ('M',)),
                 ('loodus', ('lo','B','G','F','K','loodus')),
                 ('sots', ('io','C','A','sots')),
                 ('knst', ('knst','mu')),
                 ('tehn', ('to','tehn','kodu')),
                 ('kehk', ('kehk',)),
                 ('valik', ('info','uo','Riik','maj')),
                 ('yle', ('yld','yp')),
                 )
    for klr in Klrida.query.filter_by(klassifikaator_kood='AINE').all():
        for ryhm, ained in aine_vald:
            if klr.kood in ained:
                klr.ryhm_kood = ryhm
                break
                   
    
    Klassifikaator(kood='VAHEND', nimi='Ülesande lahendamiseks kasutatav abivahend')

    Klassifikaator(kood='MOTE', nimi='Mõtlemistasand').lisaread(
        [Klrida(kood='t', nimi='Teadmine'),
         Klrida(kood='a', nimi='Arusaamine'),
         Klrida(kood='r', nimi='Rakendamine'),
         Klrida(kood='s', nimi='Analüüs ja süntees'),
         Klrida(kood='h', nimi='Hinnangu andmine'),
         Klrida(kood='n', nimi='Äratundmine'),
         Klrida(kood='p', nimi='Reprodutseerimine'),
         ])
    Klassifikaator(kood='ASTE', nimi='Kooliaste').lisaread(
        [Klrida(kood=const.ASTE_I, nimi='I kooliaste - 1.-3. kl'),
         Klrida(kood=const.ASTE_II, nimi='II kooliaste - 4.-6. kl'),
         Klrida(kood=const.ASTE_III, nimi='III kooliaste - 7.-9. kl'),
         Klrida(kood=const.ASTE_G, nimi='Gümnaasium'),
         ])

    Klassifikaator(kood='TESTILIIK', nimi='Testi liik').lisaread(
        [Klrida(kood=const.TESTILIIK_RIIGIEKSAM, nimi='Riigieksam'),
         Klrida(kood=const.TESTILIIK_POHIKOOL, nimi='Põhikooli lõpueksam'),
         Klrida(kood=const.TESTILIIK_TASEMETOO, nimi='Tasemetöö'),
         Klrida(kood=const.TESTILIIK_EELTEST, nimi='Eeltest'),
         Klrida(kood=const.TESTILIIK_TASE, nimi='Tasemeeksam'),
         Klrida(kood=const.TESTILIIK_SEADUS, nimi='Seaduse tundmise eksam'),         
         Klrida(kood=const.TESTILIIK_RV, nimi='Rahvusvaheline eksam'),
         Klrida(kood=const.TESTILIIK_KOOLIPSYH, nimi='Koolipsühholoogi test'),                  
         Klrida(kood=const.TESTILIIK_LOGOPEED, nimi='Logopeeditest'),                  
         Klrida(kood=const.TESTILIIK_SISSE, nimi='Sisseastumistest'),
         Klrida(kood=const.TESTILIIK_DIAG2, nimi='Diagnostiline test'),
         Klrida(kood=const.TESTILIIK_AVALIK, nimi='Avaliku vaate test'),
         Klrida(kood=const.TESTILIIK_TKY, nimi='Taustaküsitlus'),
         Klrida(kood=const.TESTILIIK_KOOLITUS, nimi='Koolitus'),
         ])

    Klassifikaator(kood='KASUTLIIK', nimi='Ülesande kasutus').lisaread(
        [Klrida(kood='h', nimi='Harjutusülesanne'),
         Klrida(kood='c', nimi='Kontekstiga ülesanne'),
         Klrida(kood='k', nimi='Kokkuvõttev ülesanne'),
         Klrida(kood='u', nimi='Uurimuslik ülesanne'),
         Klrida(kood='x', nimi='Muu ülesanne'),
         ])

    Klassifikaator(kood='PERIOOD', nimi='Periood').lisaread(
        [Klrida(kood='2016', nimi='2016'),
         ])

    #k = Klassifikaator(kood=u'MK', nimi=u'Maakond')
    #Klassifikaator(kood=u'KOV', nimi=u'KOV', ylem_kood='MK')
    #Klassifikaator(kood=u'ASULA', nimi=u'Asula', ylem_kood='KOV')
    # insert_ehak(k)

    Klassifikaator(kood='SOORKEEL', nimi='Soorituskeel').lisaread(
        [Klrida(kood='et', nimi='Eesti keel'),
         Klrida(kood='ru', nimi='Vene keel'),
         Klrida(kood='en', nimi='Inglise keel'),
         Klrida(kood='de', nimi='Saksa keel'),
         Klrida(kood='fr', nimi='Prantsuse keel'),
         ])
    Klassifikaator(kood='KVALITEET', nimi='Kvaliteedimärk').lisaread(
        [Klrida(kood='Inn', nimi='Harno'),
         Klrida(kood='AV', nimi='Õpetaja')])
    
    # Statistika klassifikaatorid
    Klassifikaator(kood='OPPEKEEL', nimi='Õppekeel').lisaread(
        [Klrida(kood='et', nimi='Eesti keel'),
         Klrida(kood='ru', nimi='Vene keel'),
         Klrida(kood='m', nimi='Mitmekeelne'),
         ])
    Klassifikaator(kood='KOOLITYYP', nimi='Õppeasutuse tüüp').lisaread(
        [Klrida(nimi="koolieelne lasteasutus", kood="ALUSKOOL"),
         Klrida(nimi="põhikool või gümnaasium", kood="POHIKOOL"),
         Klrida(nimi="kutseõppeasutus", kood="KUTSEKOOL"),
         Klrida(nimi="rakenduskõrgkool", kood="RAKKRGKOOL"),
         Klrida(nimi="ülikool", kood="YLIKOOL"),
         Klrida(nimi="filiaal", kood="FILIAAL"),
         Klrida(nimi="huvikool", kood="HUVIKOOL"),
         Klrida(nimi="TKH", kood="OPPEASUTUSE_TYYP_TKH"),
        ])
    Klassifikaator(kood='ALAMLIIK', nimi='Õppeasutuse alamliik').lisaread(
        [Klrida(nimi="lastesõim - kuni kolmeaastastele lastele", kood="46-1"),
         Klrida(nimi="lasteaed - kuni seitsmeaastastele lastele", kood="46-2"),
         Klrida(nimi="erilasteaed - kuni seitsmeaastastele erivajadustega lastele", kood="46-3"),
         Klrida(nimi="lasteaed-algkool", kood="45-4"),
         Klrida(nimi="algkool", kood="45-5"),
         Klrida(nimi="põhikool", kood="45-6"),
         Klrida(nimi="gümnaasium", kood="45-7"),
         Klrida(nimi="gümnaasium, mille juures on põhikooli klasse", kood="45-8"),
         Klrida(nimi="põhikool ja gümnaasium, mis tegutsevad ühe asutusena", kood="45-9"),
         Klrida(nimi="lastesõim", kood="45-1"),
         Klrida(nimi="lasteaed", kood="45-2"),
         Klrida(nimi="erilasteaed", kood="45-3"),
         Klrida(nimi="lasteaed-põhikool", kood="45-10"),
         ])
    
    Klassifikaator(kood='OPPEVORM', nimi='Õppevorm').lisaread(
        [Klrida(kood='E', nimi='eksternõpe'),
         Klrida(kood='MS', nimi='mittestatsionaarne õpe'),
         Klrida(kood='R', nimi='riigieksami sooritaja'),
         Klrida(kood='S', nimi='statsionaarne õpe'),
         Klrida(kood='Y', nimi='üksikud õppeained mittestatsionaarses õppes'),
         Klrida(kood='K', nimi='kaugõpe'),
         Klrida(kood='M', nimi='määramata'),
         Klrida(kood='P', nimi='päevane'),
         Klrida(kood='Q', nimi='õhtune'),
         Klrida(kood='Z', nimi='statsionaarne õpe - koolipõhine õpe'),
         Klrida(kood='W', nimi='statsionaarne õpe - töökohapõhine õpe'),
         ])

    Klassifikaator(kood='SUGU', nimi='Sugu').lisaread(
        [Klrida(kood='m', nimi='Mees'),
         Klrida(kood='n', nimi='Naine'),
         ])
    Klassifikaator(kood='OMANDIVORM', nimi='Õppeasutuse omandivorm').lisaread(
        [#Klrida(kood=u'm', nimi=u'Munitsipaalomand'),
         #Klrida(kood=u'e', nimi=u'Eraomand'),
         Klrida(nimi="avalik-õiguslik", kood="OMANDIVORM_AVALIK"),
         Klrida(nimi="eraomand", kood="OMANDIVORM_ERAOMAND"),
         Klrida(nimi="munitsipaal", kood="OMANDIVORM_MUNITSIPAAL"),
         Klrida(nimi="riigiomandus", kood="OMANDIVORM_RIIGIOMAND"),
         ])
    Klassifikaator(kood='TUNNUS1', nimi='Statistiline tunnus 1')
    Klassifikaator(kood='TUNNUS2', nimi='Statistiline tunnus 2')
    Klassifikaator(kood='TUNNUS3', nimi='Statistiline tunnus 3')

    # Koodilistid
    # Klassifikaator(kood=u'REGVIIS', nimi=u'Registreerimisviis').lisaread(
    #     [Klrida(kood=u's', nimi=u'Sooritaja'),
    #      Klrida(kood=u'ehis', nimi=u'Õppeasutus (EHISe kaudu)'),
    #      Klrida(kood=u'eis', nimi=u'Õppeasutus (EISi kaudu)'),
    #      Klrida(kood=u'ekk', nimi=u'Eksamikeskus'),
    #      ])
    
    Klassifikaator(kood='VASTVORM', nimi='Vastamise vorm').lisaread(
        [Klrida(kood=const.VASTVORM_KE, nimi='Kirjalik'),
         Klrida(kood=const.VASTVORM_SE, nimi='Suuline'),
         Klrida(kood=const.VASTVORM_I, nimi='Suuline (intervjuu)'),         
         Klrida(kood=const.VASTVORM_SH, nimi='Suuline (hindajaga)'),         
         Klrida(kood=const.VASTVORM_KP, nimi='Kirjalik (p-test)'),         
         Klrida(kood=const.VASTVORM_SP, nimi='Suuline (p-test)'),         
         #Klrida(kood=const.VASTVORM_KONS, nimi='Konsultatsioon'), # ei taha valikutesse
         ])
    Klassifikaator(kood='HINDAMINE', nimi='Hindamise meetod').lisaread(
        [Klrida(kood=const.HINDAMINE_SUBJ, nimi='Subjektiivne'),
         Klrida(kood=const.HINDAMINE_OBJ, nimi='Objektiivne'),
         ])
    Klassifikaator(kood='ARVUTUS', nimi='Kahe hindaja hinnangutest lõpliku hindepallide arvu arvutamise meetod').lisaread(
        [Klrida(kood=const.ARVUTUS_KESKMINE, nimi='Aritmeetiline keskmine'),
         Klrida(kood=const.ARVUTUS_SUMMA, nimi='Summeerimine'),
         ])
    Klassifikaator(kood='NULLIPOHJ', nimi='Nulli põhjus').lisaread(
        [Klrida(kood='9', nimi='Vastamata'),
         Klrida(kood='8', nimi='Loetamatu'),
         Klrida(kood='m', nimi='Muu vastus'),
         Klrida(kood='t', nimi='Tühistatud'),
         ])
    Klassifikaator(kood='HINDPROB', nimi='Hindamisprobleem').lisaread(
        [Klrida(kood='s', nimi='Sisestamata'),
         Klrida(kood='v', nimi='Sisestusvead'),
         Klrida(kood='e', nimi='Tulemuste erisused'),
         ])

    Klassifikaator(kood='Y_STAATUS', nimi='Ülesande olek').lisaread(
        [Klrida(kood=const.Y_STAATUS_KOOSTAMISEL, nimi='Koostamisel'),
         Klrida(kood=const.Y_STAATUS_PEATATUD, nimi='Peatatud'),
         Klrida(kood=const.Y_STAATUS_EELTEST, nimi='Eeltestimise kandidaat'),
         Klrida(kood=const.Y_STAATUS_TEST, nimi='Testitöö kandidaat'),
         Klrida(kood=const.Y_STAATUS_ANKUR, nimi='Ankur'),
         Klrida(kood=const.Y_STAATUS_AVALIK, nimi='Avalik'),
         Klrida(kood=const.Y_STAATUS_PEDAGOOG, nimi='Pedagoogidele kasutamiseks'),
         Klrida(kood=const.Y_STAATUS_ARHIIV, nimi='Arhiveeritud'),
         Klrida(kood=const.Y_STAATUS_YLEANDA, nimi='Üleandmiseks'),
         Klrida(kood=const.Y_STAATUS_VALMIS, nimi='Valmis kasutamiseks'),
         Klrida(kood=const.Y_STAATUS_MALL, nimi='Mall siseveebis'),
         Klrida(kood=const.Y_STAATUS_AV_MALL, nimi='Mall avalikus vaates ja siseveebis'),
         Klrida(kood=const.Y_STAATUS_AV_KOOSTAMISEL, nimi='Minu koostamisel'),
         Klrida(kood=const.Y_STAATUS_AV_VALMIS, nimi='Minu valmis'),
         Klrida(kood=const.Y_STAATUS_AV_ARHIIV, nimi='Minu arhiveeritud'),
         ])

    Klassifikaator(kood='T_STAATUS', nimi='Testi olek').lisaread(
        [Klrida(kood=const.T_STAATUS_KOOSTAMISEL, nimi='Koostamisel'),
         Klrida(kood=const.T_STAATUS_KINNITATUD, nimi='Kinnitatud'),
         #Klrida(kood=const.T_STAATUS_MAARATUD, nimi=u'Määratud pedagoogidele kasutamiseks'),
         #Klrida(kood=const.T_STAATUS_TEST, nimi=u'Testitöö'),
         #Klrida(kood=const.T_STAATUS_PEDAGOOG, nimi=u'Kõigile pedagoogidele kasutamiseks'),         
         #Klrida(kood=const.T_STAATUS_AVALIK, nimi=u'Avalik'),
         Klrida(kood=const.T_STAATUS_ARHIIV, nimi='Arhiveeritud'),
         ])

    Klassifikaator(kood='K_STAATUS', nimi='Komplekti olek').lisaread(
        [Klrida(kood=const.K_STAATUS_KOOSTAMISEL, nimi='Koostamisel'),
         Klrida(kood=const.K_STAATUS_KINNITATUD, nimi='Kinnitatud'),
         #Klrida(kood=const.K_STAATUS_TEST, nimi=u'Testitöö'),
         #Klrida(kood=const.K_STAATUS_AVALIK, nimi=u'Avalik'),
         Klrida(kood=const.K_STAATUS_ARHIIV, nimi='Arhiveeritud'),
         ])        

    Klassifikaator(kood='S_STAATUS', nimi='Testisooritamise olek').lisaread(
        [Klrida(kood=const.S_STAATUS_TYHISTATUD, nimi='Tühistatud'),
         Klrida(kood=const.S_STAATUS_REGAMATA, nimi='Registreerimata'),
         Klrida(kood=const.S_STAATUS_TASUMATA, nimi='Tasumata'),
         Klrida(kood=const.S_STAATUS_REGATUD, nimi='Registreeritud'),
         Klrida(kood=const.S_STAATUS_ALUSTAMATA, nimi='Alustamata'),
         Klrida(kood=const.S_STAATUS_POOLELI, nimi='Pooleli'),
         Klrida(kood=const.S_STAATUS_KATKESTATUD, nimi='Katkestatud'),
         Klrida(kood=const.S_STAATUS_TEHTUD, nimi='Tehtud'),
         Klrida(kood=const.S_STAATUS_EEMALDATUD, nimi='Eemaldatud'),
         Klrida(kood=const.S_STAATUS_PUUDUS, nimi='Puudus'),
         Klrida(kood=const.S_STAATUS_KATKESPROT, nimi='Katkestatud'),         
         ])        

    Klassifikaator(kood='ERIVAJADUS', nimi='Erivajadused (vanad)').lisaread(
        [Klrida(bitimask=const.ASTE_BIT_I, nimi='Eraldi ruum'),
         Klrida(bitimask=const.ASTE_BIT_I, nimi='Lisaaeg'),
         Klrida(bitimask=const.ASTE_BIT_I, nimi='Puhkepausid'),
         Klrida(bitimask=const.ASTE_BIT_I, nimi='Tugiisik'),
         Klrida(bitimask=const.ASTE_BIT_I, nimi='Suurendatud kirjas töö'),
         Klrida(bitimask=const.ASTE_BIT_I, nimi='Punktikirjas töö'),
         Klrida(bitimask=const.ASTE_BIT_I, nimi='Viipekeeles töö'),
         Klrida(bitimask=const.ASTE_BIT_I, nimi='Viipekeele tõlk'),
         Klrida(bitimask=const.ASTE_BIT_I, nimi='Abivahendid'),
         Klrida(bitimask=const.ASTE_BIT_I, nimi='Diferentseeritud hindamine'),
         # erivajadused põhikoolis
         Klrida(jrk=1, bitimask=const.ASTE_BIT_III, kood='P1', nimi='Lisaaeg'),
         Klrida(jrk=2, bitimask=const.ASTE_BIT_III, kood='P2', nimi='Eraldi ruum'),         
         Klrida(jrk=3, bitimask=const.ASTE_BIT_III, kood='P3', nimi='Puhkepausid'),
         Klrida(jrk=4, bitimask=const.ASTE_BIT_III, kood='P4', nimi='Vastuse üleskirjutamine tugiisiku poolt'),
         Klrida(jrk=5, bitimask=const.ASTE_BIT_III, kood='P5', nimi='Eksamiküsimuste ja teksti ettelugemine'),
         Klrida(jrk=6, bitimask=const.ASTE_BIT_III, kood='P6', nimi='Kirjalikud juhtnöörid'),
         Klrida(jrk=7, bitimask=const.ASTE_BIT_III, kood='P7', nimi='Täiendavad õppevahendid'),
         Klrida(jrk=8, bitimask=const.ASTE_BIT_III, kood='P8', nimi='Töökorralduste selgitamine'),
         Klrida(jrk=9, bitimask=const.ASTE_BIT_III, kood='P9', nimi='Emakeele eksamitöö diferentseeritud hindamine'),
         Klrida(jrk=10, bitimask=const.ASTE_BIT_III, kood='P10', nimi='Viipekeele tõlk'),
         Klrida(jrk=11, bitimask=const.ASTE_BIT_III, kood='P11', nimi='Eksamitöö vormistamine arvutil'),
         Klrida(jrk=12, bitimask=const.ASTE_BIT_III, kood='P12', nimi='Suurendatud eksamitöö'),
         Klrida(jrk=13, bitimask=const.ASTE_BIT_III, kood='P13', nimi='Punktkirjas eksamitöö'),
         Klrida(jrk=14, bitimask=const.ASTE_BIT_III, kood='P14', nimi='Lisatöö soorituskeelest erinevas keeles'),
         # erivajadused gümnaasiumis
         Klrida(jrk=1, bitimask=const.ASTE_BIT_G, kood='G1', nimi='Lisaaeg'),
         Klrida(jrk=2, bitimask=const.ASTE_BIT_G, kood='G2', nimi='Eraldi ruum'),
         Klrida(jrk=3, bitimask=const.ASTE_BIT_G, kood='G3', nimi='Puhkepausid'),
         Klrida(jrk=4, bitimask=const.ASTE_BIT_G, kood='G4', nimi='Eksamitöö vormistamine arvutil'),
         Klrida(jrk=5, bitimask=const.ASTE_BIT_G, kood='G5', nimi='Vastuse üleskirjutamine tugiisiku poolt'),
         Klrida(jrk=6, bitimask=const.ASTE_BIT_G, kood='G6', nimi='Eksamiküsimuste ja teksti ettelugemine'),
         Klrida(jrk=7, bitimask=const.ASTE_BIT_G, kood='G7', nimi='Kirjalikud juhtnöörid'),
         Klrida(jrk=8, bitimask=const.ASTE_BIT_G, kood='G8', nimi='Emakeele eksamitöö diferentseeritud hindamine'),
         Klrida(jrk=9, bitimask=const.ASTE_BIT_G, kood='G9', nimi='Suurendatud eksamitöö'),
         Klrida(jrk=10, bitimask=const.ASTE_BIT_G, kood='G10', nimi='Punktkirjas eksamitöö'),
         Klrida(jrk=11, bitimask=const.ASTE_BIT_G, kood='G11', nimi='Eksamitöö ilma kuulamis- ja suulise osata'),
         Klrida(jrk=12, bitimask=const.ASTE_BIT_G, kood='G12', nimi='Viipekeele tõlk'),
         Klrida(jrk=13, bitimask=const.ASTE_BIT_G, kood='G13', nimi='Eksamitöö ilma suulise osata'),
         Klrida(jrk=14, bitimask=const.ASTE_BIT_G, kood='G14', nimi='Individuaalsest õppekavast lähtuv eksamitöö'),
         Klrida(jrk=15, bitimask=const.ASTE_BIT_G, kood='G15', nimi='Individuaalsest õppekavast lähtuv eksamitöö eesti keel teise keelena'),
         Klrida(jrk=16, bitimask=const.ASTE_BIT_G, kood='G16', nimi='Lisatöö soorituskeelest erinevas keeles'),
         ])

    Klassifikaator(kood='REGVIIS', nimi='Testile registreerimise viis').lisaread(
        [Klrida(kood=const.REGVIIS_SOORITAJA, nimi='Sooritaja (EISi kaudu)'),
         Klrida(kood=const.REGVIIS_KOOL_EIS, nimi='Kool (EISi kaudu)'),
         Klrida(kood=const.REGVIIS_EKK, nimi='Eksamikeskus'),
         Klrida(kood=const.REGVIIS_XTEE, nimi='Sooritaja (eesti.ee kaudu)'),
         ])

    Klassifikaator(kood='LANG', nimi='Keel').lisaread(
        [Klrida(kood='et', nimi='Eesti keel'),
         Klrida(kood='ru', nimi='Vene keel'),
         Klrida(kood='en', nimi='Inglise keel'),
         Klrida(kood='de', nimi='Saksa keel'),
         Klrida(kood='fr', nimi='Prantsuse keel'),
         ])

    Klassifikaator(kood='AMETIKOHT', nimi='Ametikoht').lisaread(
        [Klrida(kood='d', nimi='Direktor (juhataja)'),
         Klrida(kood='o', nimi='Õpetaja'),
         Klrida(kood='t', nimi='Treener'),
         ])

    Klassifikaator(kood='YHISFAIL', nimi='Ühise faili tüüp').lisaread(
        [Klrida(kood='txt', nimi='Tekst'),
         Klrida(kood='au', nimi='Helifail'),
         Klrida(kood='mov', nimi='Video'),
         Klrida(kood='img', nimi='Pilt'),
         Klrida(kood='map', nimi='Kaart'),
         Klrida(kood='joon', nimi='Joonis'),
         ])

    Klassifikaator(kood='MAHAKANDP', nimi='Plangi mahakandmise põhjus').lisaread(
        [Klrida(kood='R', nimi='Rikutud'),
         Klrida(kood='H', nimi='Hävinud'),
         Klrida(kood='K', nimi='Kadunud'),
         Klrida(kood='A', nimi='Aegunud'),
         Klrida(kood='M', nimi='Muu'),
         ])

    y = Klrida(kood='y', nimi='Üldharidus')
    o = Klrida(kood='u', nimi='Kutseharidus')
    u = Klrida(kood='o', nimi='Kõrgharidus')
    a = Klrida(kood='a', nimi='Alusharidus')
    h = Klrida(kood='h', nimi='Huviharidus')

    Klassifikaator(kood='OPPETASE', nimi='Õppetase').lisaread([y,u,o,a,h])
    #Klassifikaator(kood=u'OPPEKAVA', nimi=u'Õppekava', ylem_kood='OPPEKAVA')  
    Klassifikaator(kood='KAVATASE', nimi='Õppekavajärgne haridustase', ylem_kood='OPPETASE')

    y.lisaalamad('KAVATASE',
        [Klrida(nimi="Põhiharidus", kood="OPPETASE_YLD"),
         Klrida(nimi="Gümnaasium", kood="OPPETASE_GYMN"),
         Klrida(nimi="Hariduslike erivajadustega laste kool", kood="OPPETASE_ERIVAJADUS"),
         Klrida(nimi="Kasvatuse eritingimusi vajavate laste kool", kood="OPPETASE_ERIKASVATUS"),
         ])
    a.lisaalamad('KAVATASE',
        [Klrida(nimi="Alusharidus", kood="OPPETASE_ALUS"),
         ])
    h.lisaalamad('KAVATASE',
        [Klrida(nimi="Huviharidus", kood="OPPETASE_HUVI"),
         ])    
    o.lisaalamad('KAVATASE',
                 [Klrida(nimi="215 kutsealane eelkoolitus põhihariduse omandajatele", kood="215"),
                  Klrida(nimi="216 kutsealane eelkoolitus koolikohustuse ea ületanud põhihariduseta isikutele", kood="216"),
                  Klrida(nimi="233 kutseharidus erivaj. või põhihariduseta isikutele", kood="233"),
                  Klrida(nimi="315 kutsealane eelkoolitus gümnaasiumihariduse omandajatele", kood="315"),
                  Klrida(nimi="323 kutsekeskharidus põhihariduse baasil", kood="323"),
                  Klrida(nimi="408 kutseõpe põhikoolis ja gümnaasiumis (vv alates 01.01.2006)", kood="408"),
                  Klrida(nimi="409 põhihariduse nõudeta kutseõpe", kood="409"),
                  Klrida(nimi="410 kutseõpe põhihariduse baasil (vv alates 01.01.2006)", kood="410"),
                  Klrida(nimi="411 kutsekeskharidusõpe (vv alates 01.01.2006)", kood="411"),
                  Klrida(nimi="412 kutseõpe keskhariduse baasil (vv alates 01.01.2006)", kood="412"),
                  Klrida(nimi="413 kutsekeskharidus keskhariduse baasil", kood="413"),
                  ])
    u.lisaalamad('KAVATASE',
                 [Klrida(nimi="501 arsti-, hambaarstiõpe", kood="501"),
                  Klrida(nimi="502 proviisor, loomaarst, arhitektiõpe, ehitusinsener jne", kood="502"),
                  Klrida(nimi="503 integreeritud õpe", kood="503"),
                  Klrida(nimi="511 bakalaureuseõpe (vv alates 01.06.2002)", kood="511"),
                  Klrida(nimi="512 bakalaureuseõpe", kood="512"),
                  Klrida(nimi="513 rakenduskõrgkooli ja ülikooli diplomiõpe (vv kuni 1.09.2002)", kood="513"),
                  Klrida(nimi="514 rakenduskõrgharidusõpe", kood="514"),
                  Klrida(nimi="523 kutsekõrgharidus (vv kuni 1.09.2002)", kood="523"),
                  Klrida(nimi="523T kutsekõrghar. keskharidust eeldaval keskeriharidusel", kood="524T"),
                  Klrida(nimi="612 magistriõpe, teadusmagister", kood="612"),
                  Klrida(nimi="613 magistriõpe, kutsemagister", kood="613"),
                  Klrida(nimi="614 magistriõpe (3+2)", kood="614"),
                  Klrida(nimi="633 kõrghar. eeldav 1-a. õpetajakoolitus, interniõpe", kood="633"),
                  Klrida(nimi="732 doktoriõpe", kood="732"),
                  Klrida(nimi="733 residendiõpe", kood="733"),
                  Klrida(nimi="734 doktoriõpe", kood="734"),
                  Klrida(nimi="7R residentuur (arst, hambaarst) alates 2001", kood="7R"),
                  ])
    # y.lisaalamad('KAVATASE', 
    #              [Klrida(kood=u'4.P', jrk=-1, nimi=u'põhiharidus').lisaalamad('OPPEKAVA',
    #                      [Klrida(kood=u'4.2010101', nimi=u'põhikooli, gümnaasiumi  riiklik õppekava, põhik. 1.-9. klass'),

    #                       Klrida(kood=u'4.3010101', nimi=u'põhikooli, gümnaasiumi  riiklik õppekava, gümn. 10.-12. klass'),
    #                       Klrida(kood=u'4.1010102', nimi=u'põhikooli lihtsustatud riiklik õppekava lihtsustatud õpe'),
    #                       Klrida(kood=u'4.1010107', nimi=u'põhikooli lihtsustatud riiklik õppekava hooldusõpe'),
    #                       Klrida(kood=u'4.1010109', nimi=u'põhikooli lihtsustatud riiklik õppekava toimetulekuõpe'),
    #                       ]),
    #               Klrida(kood=u'4.G', jrk=0, nimi=u'gümnaasiumiharidus').lisaalamad('OPPEKAVA',
    #                      [Klrida(kood=u'4.1010101', nimi=u'põhikooli, gümnaasiumi riiklik õppekava (RÕK)'),
    #                       Klrida(kood=u'4.3010101', nimi=u'põhikooli, gümnaasiumi  riiklik õppekava, gümn. 10.-12. klass'),
    #                       ]),
    #               ])
    #               # Klrida(kood=u'4.1010103', nimi=u'Rahvusvahelise bakalaureuseõppe õppekava (IB)'),
    # u.lisaalamad('KAVATASE', 
    #              [Klrida(kood=u"50.215", jrk=1, nimi=u"215 kutsealane eelkoolitus põhihariduse omandajatele"),
    #               Klrida(kood=u"50.216", jrk=2, nimi=u"216 kutsealane eelkoolitus koolikohustuse ea ületanud põhihariduseta isikutele"),
    #               Klrida(kood=u"50.233", jrk=3, nimi=u"233 kutseharidus erivaj. või põhihariduseta isikutele"),
    #               Klrida(kood=u"50.315", jrk=7, nimi=u"315 kutsealane eelkoolitus gümnaasiumihariduse omandajatele"),
    #               Klrida(kood=u"50.323", jrk=8, nimi=u"323 kutsekeskharidus põhihariduse baasil"),
    #               Klrida(kood=u"50.408", jrk=10, nimi=u"408 kutseõpe põhikoolis ja gümnaasiumis (vv alates 01.01.2006)"),
    #               Klrida(kood=u"50.409", jrk=11, nimi=u"409 põhihariduse nõudeta kutseõpe"),
    #               Klrida(kood=u"50.410", jrk=12, nimi=u"410 kutseõpe põhihariduse baasil (vv alates 01.01.2006)"),
    #               Klrida(kood=u"50.411", jrk=13, nimi=u"411 kutsekeskharidusõpe (vv alates 01.01.2006)"),
    #               Klrida(kood=u"50.412", jrk=14, nimi=u"412 kutseõpe keskhariduse baasil (vv alates 01.01.2006)"),
    #               Klrida(kood=u"50.413", jrk=15, nimi=u"413 kutsekeskharidus keskhariduse baasil"),
    #               Klrida(kood=u"50.414", jrk=16, nimi=u"414 keskharidust eeldav keskeri-/tehnikumiharidus (vv kuni 01.09.99)"),
    #               ])
    # o.lisaalamad('KAVATASE',
    #              [Klrida(kood=u"50.501", jrk=17, nimi=u"501 arsti-, hambaarstiõpe"),
    #               Klrida(kood=u"50.502", jrk=18, nimi=u"502 proviisor, loomaarst, arhitektiõpe, ehitusinsener jne"),
    #               Klrida(kood=u"50.503", jrk=19, nimi=u"503 integreeritud õpe"),
    #               Klrida(kood=u"50.511", jrk=20, nimi=u"511 bakalaureuseõpe (vv alates 01.06.2002)"),
    #               Klrida(kood=u"50.512", jrk=21, nimi=u"512 bakalaureuseõpe"),
    #               Klrida(kood=u"50.513", jrk=22, nimi=u"513 rakenduskõrgkooli ja ülikooli diplomiõpe (vv kuni 1.09.2002)"),
    #               Klrida(kood=u"50.514", jrk=23, nimi=u"514 rakenduskõrgharidusõpe"),
    #               Klrida(kood=u"50.523", jrk=24, nimi=u"523 kutsekõrgharidus (vv kuni 1.09.2002)"),
    #               Klrida(kood=u"50.523T", jrk=25, nimi=u"523T kutsekõrghar. keskharidust eeldaval keskeriharidusel"),
    #               Klrida(kood=u"50.612", jrk=26, nimi=u"612 magistriõpe, teadusmagister"),
    #               Klrida(kood=u"50.613", jrk=27, nimi=u"613 magistriõpe, kutsemagister"),
    #               Klrida(kood=u"50.614", jrk=28, nimi=u"614 magistriõpe (3+2)"),
    #               Klrida(kood=u"50.633", jrk=29, nimi=u"633 kõrghar. eeldav 1-a. õpetajakoolitus, interniõpe"),
    #               Klrida(kood=u"50.732", jrk=30, nimi=u"732 doktoriõpe"),
    #               Klrida(kood=u"50.733", jrk=31, nimi=u"733 residendiõpe"),
    #               Klrida(kood=u"50.734", jrk=32, nimi=u"734 doktoriõpe"),
    #               Klrida(kood=u"50.7R", jrk=33, nimi=u"7R residentuur (arst, hambaarst) alates 2001"),
    #               ])

    Klassifikaator(kood='EHIS_AINE', nimi='EHISe õppeaine')
    Klassifikaator(kood='EHIS_ASTE', nimi='EHISe kooliaste')
    Klassifikaator(kood='SPTYYP', nimi='Ülesandetüüp').lisaread([
            Klrida(kood=const.BLOCK_RUBRIC, nimi="Alustekst"),
            Klrida(kood=const.BLOCK_IMAGE, nimi="Pilt"),
            Klrida(kood=const.BLOCK_MEDIA, nimi="Multimeedia"),
            Klrida(kood=const.BLOCK_CUSTOM, nimi="Muu fail"),
            Klrida(kood=const.BLOCK_MATH, nimi="Matemaatiline tekst"),
            Klrida(kood=const.BLOCK_HEADER, nimi="HTML päis"),
            #Klrida(kood=const.BLOCK_TCOLUMN, nimi=u"Screen column"),
            Klrida(kood=const.INTER_CHOICE, nimi="Valikvastusega küsimus"),
            Klrida(kood=const.INTER_MCHOICE, nimi="Mitme valikuga tabel"),
            Klrida(kood=const.INTER_MATCH2, nimi="Sobitamine"),
            Klrida(kood=const.INTER_MATCH3, nimi="Sobitamine kolme hulgaga (ühe küsimusega)"),            
            Klrida(kood=const.INTER_MATCH3A, nimi="Sobitamine kolme hulgaga"),            
            Klrida(kood=const.INTER_MATCH3B, nimi="Sobitamine kolme hulgaga kolmikute hindamisega"),            
            Klrida(kood=const.INTER_ORDER, nimi="Järjestamine"),
            Klrida(kood=const.INTER_ASSOCIATE, nimi="Seostamine"),
            Klrida(kood=const.INTER_TEXT, nimi="Lühivastusega küsimus"), # Klrida(kood=const.TextEntry
            Klrida(kood=const.INTER_EXT_TEXT, nimi="Avatud vastusega küsimus"),		
            Klrida(kood=const.INTER_INL_TEXT, nimi="Avatud vastusega lünk"), # mitu TextEntry
            Klrida(kood=const.INTER_INL_CHOICE, nimi="Valikvastusega lünk"), # mitu InlineChoice
            Klrida(kood=const.INTER_GAP, nimi="Pangaga lünk"), # GapMatch
            Klrida(kood=const.INTER_PUNKT, nimi="Kirjavahemärkide lisamine"),
            Klrida(kood=const.INTER_MATH, nimi="Matemaatilise teksti sisestamine"),
            Klrida(kood=const.INTER_HOTTEXT, nimi="Tekstiosa valik"), # Hottext
            Klrida(kood=const.INTER_COLORTEXT, nimi="Tekstiosa värvimine"), 
            Klrida(kood=const.INTER_SLIDER, nimi="Liugur"),
            Klrida(kood=const.INTER_POS, nimi="Piltide lohistamine"),
            Klrida(kood=const.INTER_POS2, nimi="Piltide lohistamine II"),
            Klrida(kood=const.INTER_GR_GAP, nimi="Piltide lohistamine kujunditele"),
            Klrida(kood=const.INTER_TRAIL, nimi="Teekonna märkimine"),
            Klrida(kood=const.INTER_TXPOS, nimi="Tekstide lohistamine"),
            Klrida(kood=const.INTER_TXPOS2, nimi="Tekstide lohistamine II"),
            Klrida(kood=const.INTER_TXGAP, nimi="Tekstide lohistamine kujunditele"),        
            Klrida(kood=const.INTER_TXASS, nimi="Tekstide seostamine kujunditega"),        
            Klrida(kood=const.INTER_HOTSPOT, nimi="Pildil oleva kujundi valik"),
            Klrida(kood=const.INTER_GR_ORDER, nimi="Järjestamine pildil"),
            Klrida(kood=const.INTER_GR_ORDASS, nimi="Võrguülesanne"),            
            Klrida(kood=const.INTER_SELECT, nimi="Märkimine pildil"),
            Klrida(kood=const.INTER_SELECT2, nimi="Märkimine pildil II"),
            Klrida(kood=const.INTER_GR_ASSOCIATE, nimi="Seostamine pildil"),
            Klrida(kood=const.INTER_COLORAREA, nimi="Alade värvimine"),
            Klrida(kood=const.INTER_UNCOVER, nimi="Pildi avamine"),
            Klrida(kood=const.INTER_DRAW, nimi="Joonistamine"),
            Klrida(kood=const.INTER_AUDIO, nimi="Kõne salvestamine"),
            Klrida(kood=const.INTER_UPLOAD, nimi="Faili salvestamine"),
            Klrida(kood=const.INTER_GEOGEBRA, nimi="GeoGebra"),
            Klrida(kood=const.INTER_KRATT, nimi="Kratt"),
            Klrida(kood=const.INTER_DESMOS, nimi="Desmos"),
            Klrida(kood=const.INTER_CROSSWORD, nimi="Ristsõna"),
            Klrida(kood=const.BLOCK_GOOGLECHARTS, nimi="Google Charts"),
            Klrida(kood=const.BLOCK_FORMULA, nimi="Arvutatud väärtus"),
            Klrida(kood=const.BLOCK_RANDOM, nimi="Juhuarv"),        
        ])
    Klassifikaator(kood='TOOKASK', nimi='Tehniline töökäsk', ylem_kood='SPTYYP')

    Klassifikaator(kood='KODAKOND', nimi='Kodakondsus').lisaread(
        [Klrida(kood='AFG', kood2='AF', nimi='﻿Afganistan'),
         Klrida(kood='ALA', kood2='AX', nimi='Ahvenamaa (Soome)'),
         Klrida(kood='ALB', kood2='AL', nimi='Albaania'),
         Klrida(kood='DZA', kood2='DZ', nimi='Alžeeria'),
         Klrida(kood='ASM', kood2='AS', nimi='Ameerika Samoa'),
         Klrida(kood='USA', kood2='US', nimi='Ameerika Ühendriigid'),
         Klrida(kood='AND', kood2='AD', nimi='Andorra'),
         Klrida(kood='AGO', kood2='AO', nimi='Angola'),
         Klrida(kood='AIA', kood2='AI', nimi='Anguilla (Br)'),
         Klrida(kood='ATA', kood2='AQ', nimi='Antarktis'),
         Klrida(kood='ATG', kood2='AG', nimi='Antigua ja Barbuda'),
         Klrida(kood='ARE', kood2='AE', nimi='Araabia Ühendemiraadid'),
         Klrida(kood='ARG', kood2='AR', nimi='Argentina'),
         Klrida(kood='ARM', kood2='AM', nimi='Armeenia'),
         Klrida(kood='ABW', kood2='AW', nimi='Aruba (Holl)'),
         Klrida(kood='AZE', kood2='AZ', nimi='Aserbaidžaan'),
         Klrida(kood='AUS', kood2='AU', nimi='Austraalia'),
         Klrida(kood='AUT', kood2='AT', nimi='Austria'),
         Klrida(kood='BHS', kood2='BS', nimi='Bahama'),
         Klrida(kood='BHR', kood2='BH', nimi='Bahrein'),
         Klrida(kood='BGD', kood2='BD', nimi='Bangladesh'),
         Klrida(kood='BRB', kood2='BB', nimi='Barbados'),
         Klrida(kood='PLW', kood2='PW', nimi='Belau'),
         Klrida(kood='BEL', kood2='BE', nimi='Belgia'),
         Klrida(kood='BLZ', kood2='BZ', nimi='Belize'),
         Klrida(kood='BEN', kood2='BJ', nimi='Benin'),
         Klrida(kood='BMU', kood2='BM', nimi='Bermuda (Br)'),
         Klrida(kood='BTN', kood2='BT', nimi='Bhutan'),
         Klrida(kood='BOL', kood2='BO', nimi='Boliivia'),
         Klrida(kood='BES', kood2='BQ', nimi='Bonaire, Sint Eustatius ja Saba (Holl)'),
         Klrida(kood='BIH', kood2='BA', nimi='Bosnia ja Hertsegoviina'),
         Klrida(kood='BWA', kood2='BW', nimi='Botswana'),
         Klrida(kood='BVT', kood2='BV', nimi="Bouvet' saar (Norra)"),
         Klrida(kood='BRA', kood2='BR', nimi='Brasiilia'),
         Klrida(kood='IOT', kood2='IO', nimi='Briti India ookeani ala'),
         Klrida(kood='VGB', kood2='VG', nimi='Briti Neitsisaared'),
         Klrida(kood='BRN', kood2='BN', nimi='Brunei'),
         Klrida(kood='BGR', kood2='BG', nimi='Bulgaaria'),
         Klrida(kood='BFA', kood2='BF', nimi='Burkina Faso'),
         Klrida(kood='BDI', kood2='BI', nimi='Burundi'),
         Klrida(kood='COL', kood2='CO', nimi='Colombia'),
         Klrida(kood='COK', kood2='CK', nimi='Cooki saared (U-Mer)'),
         Klrida(kood='CRI', kood2='CR', nimi='Costa Rica'),
         Klrida(kood='CUW', kood2='CW', nimi='Curaçao (Holl)'),
         Klrida(kood='DJI', kood2='DJ', nimi='Djibouti'),
         Klrida(kood='DMA', kood2='DM', nimi='Dominica'),
         Klrida(kood='DOM', kood2='DO', nimi='Dominikaani Vabariik'),
         Klrida(kood='ECU', kood2='EC', nimi='Ecuador'),
         Klrida(kood='EST', kood2='EE', nimi='Eesti'),
         Klrida(kood='EGY', kood2='EG', nimi='Egiptus'),
         Klrida(kood='GNQ', kood2='GQ', nimi='Ekvatoriaal-Guinea'),
         Klrida(kood='CIV', kood2='CI', nimi="Elevandiluurannik (Côte d'Ivoire)"),
         Klrida(kood='SLV', kood2='SV', nimi='El Salvador'),
         Klrida(kood='ERI', kood2='ER', nimi='Eritrea'),
         Klrida(kood='ETH', kood2='ET', nimi='Etioopia'),
         Klrida(kood='FLK', kood2='FK', nimi='Falklandi saared (Br)'),
         Klrida(kood='FJI', kood2='FJ', nimi='Fidži'),
         Klrida(kood='PHL', kood2='PH', nimi='Filipiinid'),
         Klrida(kood='FRO', kood2='FO', nimi='Fääri saared (Taani)'),
         Klrida(kood='GAB', kood2='GA', nimi='Gabon'),
         Klrida(kood='GMB', kood2='GM', nimi='Gambia'),
         Klrida(kood='GHA', kood2='GH', nimi='Ghana'),
         Klrida(kood='GIB', kood2='GI', nimi='Gibraltar (Br)'),
         Klrida(kood='GRD', kood2='GD', nimi='Grenada'),
         Klrida(kood='GEO', kood2='GE', nimi='Gruusia'),
         Klrida(kood='GRL', kood2='GL', nimi='Gröönimaa (Taani)'),
         Klrida(kood='GLP', kood2='GP', nimi='Guadeloupe (Pr)'),
         Klrida(kood='GUM', kood2='GU', nimi='Guam (USA)'),
         Klrida(kood='GTM', kood2='GT', nimi='Guatemala'),
         Klrida(kood='GGY', kood2='GG', nimi='Guernsey (Br)'),
         Klrida(kood='GIN', kood2='GN', nimi='Guinea'),
         Klrida(kood='GNB', kood2='GW', nimi='Guinea-Bissau'),
         Klrida(kood='GUY', kood2='GY', nimi='Guyana'),
         Klrida(kood='HTI', kood2='HT', nimi='Haiti'),
         Klrida(kood='HMD', kood2='HM', nimi='Heard ja McDonald (Austrl)'),
         Klrida(kood='CHN', kood2='CN', nimi='Hiina'),
         Klrida(kood='ESP', kood2='ES', nimi='Hispaania'),
         Klrida(kood='NLD', kood2='NL', nimi='Holland'),
         Klrida(kood='HND', kood2='HN', nimi='Honduras'),
         Klrida(kood='HKG', kood2='HK', nimi='Hongkong (Hiina)'),
         Klrida(kood='HRV', kood2='HR', nimi='Horvaatia'),
         Klrida(kood='TLS', kood2='TL', nimi='Ida-Timor (Timor-Leste)'),
         Klrida(kood='IRL', kood2='IE', nimi='Iirimaa'),
         Klrida(kood='ISR', kood2='IL', nimi='Iisrael'),
         Klrida(kood='IND', kood2='IN', nimi='India'),
         Klrida(kood='IDN', kood2='ID', nimi='Indoneesia'),
         Klrida(kood='IRQ', kood2='IQ', nimi='Iraak'),
         Klrida(kood='IRN', kood2='IR', nimi='Iraan'),
         Klrida(kood='ISL', kood2='IS', nimi='Island'),
         Klrida(kood='ITA', kood2='IT', nimi='Itaalia'),
         Klrida(kood='JPN', kood2='JP', nimi='Jaapan'),
         Klrida(kood='JAM', kood2='JM', nimi='Jamaica'),
         Klrida(kood='YEM', kood2='YE', nimi='Jeemen'),
         Klrida(kood='JEY', kood2='JE', nimi='Jersey (Br)'),
         Klrida(kood='JOR', kood2='JO', nimi='Jordaania'),
         Klrida(kood='CXR', kood2='CX', nimi='Jõulusaar (Austrl)'),
         Klrida(kood='CYM', kood2='KY', nimi='Kaimanisaared (Br)'),
         Klrida(kood='KHM', kood2='KH', nimi='Kambodža'),
         Klrida(kood='CMR', kood2='CM', nimi='Kamerun'),
         Klrida(kood='CAN', kood2='CA', nimi='Kanada'),
         Klrida(kood='KAZ', kood2='KZ', nimi='Kasahstan'),
         Klrida(kood='QAT', kood2='QA', nimi='Katar'),
         Klrida(kood='KEN', kood2='KE', nimi='Keenia'),
         Klrida(kood='CAF', kood2='CF', nimi='Kesk-Aafrika Vabariik'),
         Klrida(kood='KIR', kood2='KI', nimi='Kiribati'),
         Klrida(kood='COM', kood2='KM', nimi='Komoorid'),
         Klrida(kood='COD', kood2='CD', nimi='Kongo DV'),
         Klrida(kood='COG', kood2='CG', nimi='Kongo Vabariik'),
         Klrida(kood='CCK', kood2='CC', nimi='Kookossaared (Austrl)'),
         Klrida(kood='GRC', kood2='GR', nimi='Kreeka'),
         Klrida(kood='CUB', kood2='CU', nimi='Kuuba'),
         Klrida(kood='KWT', kood2='KW', nimi='Kuveit'),
         Klrida(kood='KGZ', kood2='KG', nimi='Kõrgõzstan'),
         Klrida(kood='CYP', kood2='CY', nimi='Küpros'),
         Klrida(kood='LAO', kood2='LA', nimi='Laos'),
         Klrida(kood='LTU', kood2='LT', nimi='Leedu'),
         Klrida(kood='LSO', kood2='LS', nimi='Lesotho'),
         Klrida(kood='LBR', kood2='LR', nimi='Libeeria'),
         Klrida(kood='LIE', kood2='LI', nimi='Liechtenstein'),
         Klrida(kood='LBN', kood2='LB', nimi='Liibanon'),
         Klrida(kood='LBY', kood2='LY', nimi='Liibüa'),
         Klrida(kood='LUX', kood2='LU', nimi='Luksemburg'),
         Klrida(kood='ZAF', kood2='ZA', nimi='Lõuna-Aafrika Vabariik'),
         Klrida(kood='SGS', kood2='GS', nimi='Lõuna-Georgia ja Lõuna-Sandwichi saared (Br)'),
         Klrida(kood='KOR', kood2='KR', nimi='Lõuna-Korea'),
         Klrida(kood='SSD', kood2='SS', nimi='Lõuna-Sudaan'),
         Klrida(kood='LVA', kood2='LV', nimi='Läti'),
         Klrida(kood='ESH', kood2='EH', nimi='Lääne-Sahara'),
         Klrida(kood='MAC', kood2='MO', nimi='Macau (Hiina)'),
         Klrida(kood='MDG', kood2='MG', nimi='Madagaskar'),
         Klrida(kood='MYS', kood2='MY', nimi='Malaisia'),
         Klrida(kood='MWI', kood2='MW', nimi='Malawi'),
         Klrida(kood='MDV', kood2='MV', nimi='Maldiivid'),
         Klrida(kood='MLI', kood2='ML', nimi='Mali'),
         Klrida(kood='MLT', kood2='MT', nimi='Malta'),
         Klrida(kood='IMN', kood2='IM', nimi='Mani saar (Br)'),
         Klrida(kood='MAR', kood2='MA', nimi='Maroko'),
         Klrida(kood='MHL', kood2='MH', nimi='Marshalli Saared'),
         Klrida(kood='MTQ', kood2='MQ', nimi='Martinique'),
         Klrida(kood='MRT', kood2='MR', nimi='Mauritaania'),
         Klrida(kood='MUS', kood2='MU', nimi='Mauritius'),
         Klrida(kood='MYT', kood2='YT', nimi='Mayotte (Pr)'),
         Klrida(kood='MEX', kood2='MX', nimi='Mehhiko'),
         Klrida(kood='FSM', kood2='FM', nimi='Mikroneesia'),
         Klrida(kood='MDA', kood2='MD', nimi='Moldova'),
         Klrida(kood='MCO', kood2='MC', nimi='Monaco'),
         Klrida(kood='MNG', kood2='MN', nimi='Mongoolia'),
         Klrida(kood='MNE', kood2='ME', nimi='Montenegro'),
         Klrida(kood='MSR', kood2='MS', nimi='Montserrat (Br)'),
         Klrida(kood='MOZ', kood2='MZ', nimi='Mosambiik'),
         Klrida(kood='MMR', kood2='MM', nimi='Myanmar (Birma)'),
         Klrida(kood='NAM', kood2='NA', nimi='Namiibia'),
         Klrida(kood='NRU', kood2='NR', nimi='Nauru'),
         Klrida(kood='NPL', kood2='NP', nimi='Nepal'),
         Klrida(kood='NIC', kood2='NI', nimi='Nicaragua'),
         Klrida(kood='NGA', kood2='NG', nimi='Nigeeria'),
         Klrida(kood='NER', kood2='NE', nimi='Niger'),
         Klrida(kood='NIU', kood2='NU', nimi='Niue (U-Mer)'),
         Klrida(kood='NFK', kood2='NF', nimi='Norfolk (Austrl)'),
         Klrida(kood='NOR', kood2='NO', nimi='Norra'),
         Klrida(kood='OMN', kood2='OM', nimi='Omaan'),
         Klrida(kood='PNG', kood2='PG', nimi='Paapua Uus-Guinea'),
         Klrida(kood='PAK', kood2='PK', nimi='Pakistan'),
         Klrida(kood='PSE', kood2='PS', nimi='Palestiina'),
         Klrida(kood='PAN', kood2='PA', nimi='Panama'),
         Klrida(kood='PRY', kood2='PY', nimi='Paraguay'),
         Klrida(kood='PER', kood2='PE', nimi='Peruu'),
         Klrida(kood='PCN', kood2='PN', nimi='Pitcairn (Br)'),
         Klrida(kood='POL', kood2='PL', nimi='Poola'),
         Klrida(kood='PRT', kood2='PT', nimi='Portugal'),
         Klrida(kood='GUF', kood2='GF', nimi='Prantsuse Guajaana'),
         Klrida(kood='ATF', kood2='TF', nimi='Prantsuse Lõunaalad'),
         Klrida(kood='PYF', kood2='PF', nimi='Prantsuse Polüneesia'),
         Klrida(kood='FRA', kood2='FR', nimi='Prantsusmaa'),
         Klrida(kood='PRI', kood2='PR', nimi='Puerto Rico (USA)'),
         Klrida(kood='PRK', kood2='KP', nimi='Põhja-Korea'),
         Klrida(kood='MKD', kood2='MK', nimi='Põhja-Makedoonia'),
         Klrida(kood='MNP', kood2='MP', nimi='Põhja-Mariaanid (USA)'),
         Klrida(kood='REU', kood2='RE', nimi='Réunion (Pr)'),
         Klrida(kood='CPV', kood2='CV', nimi='Roheneemesaared (Cabo Verde)'),
         Klrida(kood='SWE', kood2='SE', nimi='Rootsi'),
         Klrida(kood='ROU', kood2='RO', nimi='Rumeenia'),
         Klrida(kood='RWA', kood2='RW', nimi='Rwanda'),
         Klrida(kood='SLB', kood2='SB', nimi='Saalomoni Saared'),
         Klrida(kood='BLM', kood2='BL', nimi='Saint-Barthélemy (Pr)'),
         Klrida(kood='SHN', kood2='SH', nimi='Saint Helena (Br)'),
         Klrida(kood='KNA', kood2='KN', nimi='Saint Kitts ja Nevis'),
         Klrida(kood='LCA', kood2='LC', nimi='Saint Lucia'),
         Klrida(kood='MAF', kood2='MF', nimi='Saint-Martin (Prantsuse osa)'),
         Klrida(kood='SPM', kood2='PM', nimi='Saint-Pierre ja Miquelon (Pr)'),
         Klrida(kood='VCT', kood2='VC', nimi='Saint Vincent'),
         Klrida(kood='DEU', kood2='DE', nimi='Saksamaa'),
         Klrida(kood='ZMB', kood2='ZM', nimi='Sambia'),
         Klrida(kood='WSM', kood2='WS', nimi='Samoa'),
         Klrida(kood='SMR', kood2='SM', nimi='San Marino'),
         Klrida(kood='STP', kood2='ST', nimi='São Tomé ja Príncipe'),
         Klrida(kood='SAU', kood2='SA', nimi='Saudi Araabia'),
         Klrida(kood='SYC', kood2='SC', nimi='Seišellid'),
         Klrida(kood='SEN', kood2='SN', nimi='Senegal'),
         Klrida(kood='SRB', kood2='RS', nimi='Serbia'),
         Klrida(kood='SLE', kood2='SL', nimi='Sierra Leone'),
         Klrida(kood='SGP', kood2='SG', nimi='Singapur'),
         Klrida(kood='SXM', kood2='SX', nimi='Sint Maarten (Holl)'),
         Klrida(kood='SVK', kood2='SK', nimi='Slovakkia'),
         Klrida(kood='SVN', kood2='SI', nimi='Sloveenia'),
         Klrida(kood='SOM', kood2='SO', nimi='Somaalia'),
         Klrida(kood='FIN', kood2='FI', nimi='Soome'),
         Klrida(kood='LKA', kood2='LK', nimi='Sri Lanka'),
         Klrida(kood='SDN', kood2='SD', nimi='Sudaan'),
         Klrida(kood='SUR', kood2='SR', nimi='Suriname'),
         Klrida(kood='GBR', kood2='GB', nimi='Suurbritannia'),
         Klrida(kood='SWZ', kood2='SZ', nimi='Svaasimaa'),
         Klrida(kood='SJM', kood2='SJ', nimi='Svalbard ja Jan Mayen (Norra)'),
         Klrida(kood='SYR', kood2='SY', nimi='Süüria'),
         Klrida(kood='CHE', kood2='CH', nimi='Šveits'),
         Klrida(kood='ZWE', kood2='ZW', nimi='Zimbabwe'),
         Klrida(kood='DNK', kood2='DK', nimi='Taani'),
         Klrida(kood='TJK', kood2='TJ', nimi='Tadžikistan'),
         Klrida(kood='THA', kood2='TH', nimi='Tai'),
         Klrida(kood='TWN', kood2='TW', nimi='Taiwan (Hiina)'),
         Klrida(kood='TZA', kood2='TZ', nimi='Tansaania'),
         Klrida(kood='TGO', kood2='TG', nimi='Togo'),
         Klrida(kood='TKL', kood2='TK', nimi='Tokelau (U-Mer)'),
         Klrida(kood='TON', kood2='TO', nimi='Tonga'),
         Klrida(kood='TTO', kood2='TT', nimi='Trinidad ja Tobago'),
         Klrida(kood='TCD', kood2='TD', nimi='Tšaad'),
         Klrida(kood='CZE', kood2='CZ', nimi='Tšehhi'),
         Klrida(kood='CHL', kood2='CL', nimi='Tšiili'),
         Klrida(kood='TUN', kood2='TN', nimi='Tuneesia'),
         Klrida(kood='TCA', kood2='TC', nimi='Turks ja Caicos (Br)'),
         Klrida(kood='TUV', kood2='TV', nimi='Tuvalu'),
         Klrida(kood='TUR', kood2='TR', nimi='Türgi'),
         Klrida(kood='TKM', kood2='TM', nimi='Türkmenistan'),
         Klrida(kood='UGA', kood2='UG', nimi='Uganda'),
         Klrida(kood='UKR', kood2='UA', nimi='Ukraina'),
         Klrida(kood='HUN', kood2='HU', nimi='Ungari'),
         Klrida(kood='URY', kood2='UY', nimi='Uruguay'),
         Klrida(kood='VIR', kood2='VI', nimi='USA Neitsisaared'),
         Klrida(kood='UZB', kood2='UZ', nimi='Usbekistan'),
         Klrida(kood='NCL', kood2='NC', nimi='Uus-Kaledoonia (Pr)'),
         Klrida(kood='NZL', kood2='NZ', nimi='Uus-Meremaa'),
         Klrida(kood='BLR', kood2='BY', nimi='Valgevene'),
         Klrida(kood='VUT', kood2='VU', nimi='Vanuatu'),
         Klrida(kood='VAT', kood2='VA', nimi='Vatikan'),
         Klrida(kood='RUS', kood2='RU', nimi='Venemaa'),
         Klrida(kood='VEN', kood2='VE', nimi='Venezuela'),
         Klrida(kood='VNM', kood2='VN', nimi='Vietnam'),
         Klrida(kood='WLF', kood2='WF', nimi='Wallis ja Futuna (Pr)'),
         Klrida(kood='UMI', kood2='UM', nimi='Ühendriikide hajasaared'),
         ])

    Klassifikaator(kood='TVALDKOND', nimi='Töövaldkond').lisaread(
        [Klrida(kood='1', nimi='Majandus'),
         Klrida(kood='2', nimi='Ehitus, kinnisvara'),
         Klrida(kood='3', nimi='Tööstus, tootmine, energeetika'),
         Klrida(kood='4', nimi='Haridus, teadus'),
         Klrida(kood='5', nimi='Kultuur'),
         Klrida(kood='6', nimi='Infotehnoloogia'),
         Klrida(kood='7', nimi='Tervishoid, sotsiaalhoolekanne'),
         Klrida(kood='8', nimi='Transport, logistika'),
         Klrida(kood='9', nimi='Teenindus, kaubandus'),
         Klrida(kood='10', nimi='Toitlustus, majutus'),
         Klrida(kood='11', nimi='Avalik haldus'),
         Klrida(kood='12', nimi='Õigus'),
         Klrida(kood='13', nimi='Riigikaitse'),
         Klrida(kood='14', nimi='Korrakaitse ja päästeteenistus'),
         Klrida(kood='15', nimi='Rahandus'),
         Klrida(kood='X', nimi='Muu'),
         ])

    Klassifikaator(kood='AMET', nimi='Amet').lisaread(
        [Klrida(kood='1', nimi='tippjuht'),
         Klrida(kood='2', nimi='keskastmejuht'),
         Klrida(kood='3', nimi='peaspetsialist'),
         Klrida(kood='4', nimi='spetsialist'),
         Klrida(kood='5', nimi='sõjaväelane'),
         Klrida(kood='6', nimi='ametnik'),
         Klrida(kood='7', nimi='politseiametnik'),
         Klrida(kood='8', nimi='päästeametnik'),
         Klrida(kood='9', nimi='vanglaametnik'),
         Klrida(kood='10', nimi='teenindus- või müügitöötaja'),
         Klrida(kood='11', nimi='oskustöötaja/käsitööline'),
         Klrida(kood='12', nimi='lihttööline'),
         Klrida(kood='13', nimi='õpilane'),
         Klrida(kood='14', nimi='üliõpilane'),
         Klrida(kood='15', nimi='pensionär'),
         Klrida(kood='16', nimi='ei tööta'),
         Klrida(kood='X', nimi='muu'),
         ])

    Klassifikaator(kood='HARIDUS', nimi='Haridus').lisaread(
        [Klrida(kood='1', nimi='Põhiharidus'),
         Klrida(kood='2', nimi='Keskharidus'),
         Klrida(kood='3', nimi='Kõrgharidus'),
         Klrida(kood='4', nimi='Keskeriharidus'),
         Klrida(kood='X', nimi='TEADMATA'),
         ])

    Klassifikaator(kood='OPPEKOHT', nimi='Keele õppimise koht').lisaread(
        [Klrida(kood='1', nimi='Kursustel'),
         Klrida(kood='2', nimi='Koolis'),
         Klrida(kood='3', nimi='Iseseisvalt'),
         ])

    Klassifikaator(kood='OPPEKOHTET', nimi='Eesti keele õppimise koht').lisaread(
        [Klrida(kood='P', nimi='Põhikoolis', jrk=1),
         Klrida(kood='G', nimi='Keskkoolis/gümnaasiumis', jrk=2),
         Klrida(kood='K', nimi='Kutsekoolis', jrk=3),
         Klrida(kood='Y', nimi='Ülikoolis', jrk=4),
         Klrida(kood='E', nimi='Keeltekoolis', jrk=5),
         Klrida(kood='X', nimi='Mujal', jrk=6),
         ])

    k = Klassifikaator(kood='TESTIKLASS', nimi='Testi klass')
    for klass in range(1, 13):
        k.read.append(Klrida(kood=str(klass), nimi=str(klass), jrk=klass))
    
    # rahvuste koodid on RR-i WSDList
    k = Klassifikaator(kood='RAHVUS', nimi='Rahvus')
    data = """
ABA;abasiin
ABK;abhaas
ADY;adõgee
AFR;afrikander
AAM;afroameeriklane
AGU;agul
AYM;aimara
AIN;ainu
ALB;albaanlane
ALT;altailane
AMH;amhar
AND;andorralane
ARA;araablane
ARG;argentiinlane
ARM;armeenlane
AZE;aserbaidžaan
SYR;assüürlane
NAH;asteek
AUT;austerlane
AUE;austraallane (ingliskeelne)
AVA;avaar
BAL;balkaar
BRB;barbadoslane
BAQ;bask
BAK;baškiir
BEN;bengal
BER;berber
BUR;birmalane
BOL;boliivlane
BOS;bosnialane
BRA;brasiillane
BRE;bretoon 
BUL;bulgaarlane
BUA;burjaat
COL;colombialane
DAR;darg
DOL;dolgaan
DMA;dominicalane
DOM;dominikaanlane
ECU;ecuadorlane
EST;eestlane
ESK;eskimo
EVE;eveen
TUN;evenk
FIJ;fidžilane
FLE;flaam
FRY;friis
FAO;fäärlane
GAG;gagauus
GLG;galeeg
GEO;grusiin
GRL;gröönlane
GRN;guaranii
GTM;guatemalalane
GUD;gudžarat
GIN;guinealane
KHA;hakass
OST;hant
HAU;hausa
CHI;hiinlane
HIN;hindu
SPA;hispaanlane
DUT;hollandlane
HON;honduraslane
SCR;horvaat
DUN;huei
IBO;ibo
GLE;iirlane
IND;indoneeslane
ING;ingerisoomlane
ENG;inglane
INU;ingušš
ICE;islandlane
IZH;isur
ITA;itaallane
ITE;itelmeen
JPN;jaapanlane
JAV;jaavalane
SAH;jakuut
JAM;jamaicalane
YOR;joruba
YUG;jugoslaavlane
YKG;jukagiir
HEB;juut
KAB;kabard
KAL;kalmõkk
CAE;kanadalane
KAN;kannada
KRA;karaiim
KAA;karakalpakk
KRT;karatšai
KAR;karjalane
KAZ;kasahh
KAS;kašmiir
CAT;katalaan
QUE;ketšua
KET;kett
KHM;khmeer
KIR;kirgiis
KOM;komi
KON;kongo
KOR;korealane
KRY;korjakk
COS;korsiklane
GRE;kreeklane
CPE;kreool (inglise põhjal)
CRP;kreool (muud)
CPP;kreool (portugali põhjal)
CPF;kreool (prantsuse põhjal)
KUM;kumõkk
KUR;kurd
CUB;kuubalane
WLS;kõmr
LAK;lakk
LIT;leedulane
LEZ;lesgi
LTZ;letseburglane
LIV;liivlane
LAV;lätlane
YUK;maaja
MAC;makedoonlane
MLG;malagassi
MAY;malailane
MAL;malajalam
MLT;maltalane
MAN;mansi
MAO;maoori
CHM;mari
MTQ;martiniquelane
MAS;masai
MEX;mehhiklane
MOL;moldovlane
MON;mongol
MNT;montenegrolane
MOR;mordvalane
ROM;mustlane
NAN;nanai
NAU;naurulane
SAM;neenets
NEG;negidal
NEP;nepallane
NGA;nganassaan
NIC;nicaragualane
NIV;nivh
NOG;nogai
NOR;norralane
ORM;oromo
ORO;orotš
OSS;osseet
PAA;paapua
PAK;pakistanlane
PAM;panamalane
PAN;pandžab
PAR;paraguaylane
KPO;permikomi
PEV;peruulane
POL;poolakas
POR;portugallane
FRE;prantslane
PRI;puertoricolane
PUS;puštu
PER;pärslane
ROH;retoromaan
SWE;rootslane
RWA;ruanda
RUM;rumeenlane
RUN;rundi
RUT;rutul
SMI;saam
STV;saintvincentlane
GER;sakslane
SAL;salvadorlane
SMO;samoalane
SRD;sard
SCC;serblane
SRH;serbohorvaat
SND;sindhi
SIN;singal
SIO;siuu
SLO;slovakk
SLV;sloveen
SOM;somaal
FIN;soomlane
WEN;sorb
SOT;sotho
SWA;suahiili
SUN;sunda
ZUL;suulu
SIS;svaasi
SEL;sölkup
SNA;šona
SHO;šoor
SCO;šotlane
CHD;šveitslane
DAN;taanlane
TTI;taatlane
TAB;tabassaraan
TGK;tadžikk
THA;tailane
TAL;talõšš
TAM;tamil
TAT;tatarlane
TEL;telugu
TEM;temne
TIB;tiibetlane
TOG;tonga
TRI;trinidadlane
TSA;tsahur
SET;tsvana
CZE;tšehh
CIR;tšerkess
CHE;tšetšeen
CHL;tšiillane
CHU;tšuktši
CHV;tšuvašš
TUA;tuareeg
TYV;tõvalane
TUR;türklane
TUK;türkmeen
UDM;udmurt
UIG;uiguur
UKR;ukrainlane
UKW;ukwuani
HUN;ungarlane
URY;uruguaylane
USA;USA ameeriklane
UZB;usbekk
NEW;uusmeremaalane (ingliskeelne)
VOT;vadjalane
BEL;valgevenelane
WAL;valloon
RUS;venelane
VEN;venezuelalane
VEP;vepslane
VIE;vietnamlane
"""
    for line in data.splitlines():
        if line:
            kood, nimi = line.lower().split(';')
            k.read.append(Klrida(kood=kood, nimi=nimi))

    k = Klassifikaator(kood='KEEL', nimi='Keel')
    data = """
aar;afari
abk;abhaasi
ace;atšehi
ach;akoli
ada;adangme
ady;adõgee
afa;afroaasia keeled
afh;afrihili
afr;afrikaani
agx;aguli
ain;ainu
aka;akani
akk;akadi
alb;albaania
ale;aleuudi
alg;algonkini keeled
alt;altai
amh;amhara
ang;vanainglise (u 450–1100)
anp;angika
apa;apatši keeled
ara;araabia
arc;aramea
arg;aragoni
arm;armeenia
arn;mapudunguni
arp;arapaho
art;tehiskeeled
arw;aravaki
asm;assami
ast;astuuria
aze;aserbaidžaani
ath;atapaski keeled
aus;Austraalia keeled
ava;avaari
awa;avadhi
ave;avesta
aym;aimara
bad;banda keeled
bai;bamileke keeled
bak;baškiiri
bal;belutši
bam;bambara
ban;bali
baq;baski
bas;basaa
bat;balti keeled
bej;bedža
bel;valgevene
bem;bemba
ben;bengali
ber;berberi keeled
bho;bhodžpuri
bih;bihaari keeled
bik;bikoli
bin;edo
bis;bislama
bla;mustjalaindiaani
bnt;bantu keeled
bos;bosnia
bra;bradži
bre;bretooni
btk;bataki keeled
bua;burjaadi
bug;bugi
bul;bulgaaria
bur;birma
byn;bilini
cad;kado
cai;Kesk-Ameerika indiaani keeled
car;kariibi
cat;katalaani
cau;Kaukaasia keeled
ceb;sebu
cel;keldi keeled
cha;tšamorro
chb;tšibtša
che;tšetšeeni
chg;tšagatai
chi;hiina
chk;tšuugi
chm;mari
chn;tšinuki žargoon
cho;tšokto
chp;tšipevai
chr;tšerokii
chu;kirikuslaavi
chv;tšuvaši
chy;šaieeni
cmc;tšaami keeled
cop;kopti
cor;korni
cos;korsika
cpe;inglispõhjalised kreool- ja pidžinkeeled
cpf;prantsuspõhjalised kreool- ja pidžinkeeled
cpp;portugalipõhjalised kreool- ja pidžinkeeled
cre;krii
crh;krimmitatari
crp;kreool- ja pidžinkeeled
csb;kašuubi
cze;tšehhi
cus;kuši keeled
dak;dakota
dan;taani
dar;dargi
day;sisemaadajaki keeled
del;delavari
den;sleivi
dgr;dogribi
din;dinka
div;maldiivi
doi;dogri
dra;draviidi keeled
dsb;alamsorbi
dzo;dzongkha
dua;duala
dum;keskhollandi (u 1050–1350)
dut;hollandi
dyu;djula
efi;efiki
egy;egiptuse
eka;ekadžuki
elx;eelami
eng;inglise
enm;keskinglise (1100–1500)
epo;esperanto
eso;eesti viipekeel
est;eesti
ewe;eve
ewo;evondo
fan;fangi
fao;fääri
fat;fanti
fij;fidži
fil;filipiini
fin;soome
fiu;soome-ugri keeled
fon;foni
fre;prantsuse
frm;keskprantsuse (1400–1600)
fro;vanaprantsuse (842 – u 1400)
frr;põhjafriisi
frs;idafriisi
fry;friisi
ful;fula
fur;friuuli
gaa;gaa
gag;gagauusi
gay;gajo
gba;gbaja
gem;germaani keeled
geo;gruusia
ger;saksa
gez;geezi
gil;kiribati
gla;gaeli
gle;iiri
glg;galeegi
glv;mänksi
gmh;keskülemsaksa (u 1050–1500)
goh;vanaülemsaksa (u 750–1050)
gon;gondi
gor;gorontalo
got;gooti
grb;grebo
grc;vanakreeka (1453. a-ni)
gre;kreeka (pärast 1453. a)
grn;guaranii
gsw;šveitsisaksa
guj;gudžarati
gwi;gvitšini
hai;haida
hat;haiti
hau;hausa
haw;havai
hbo;vanaheebrea keel
hbs;serbia-horvaadi 
heb;heebrea
her;herero
hil;hiligainoni
him;himatšali keeled
hin;hindi
hit;heti
hmn;hmongi
hmo;hirimotu
hrv;horvaadi
hsb;ülemsorbi
hun;ungari
hup;hupa
iba;ibani
ibo;ibo
ice;islandi
ido;ido
iii;nuosu
ijo;idžo keeled
iku;inuktituti
ile;interlingue
ilo;iloko
ils;rahvusvaheline viipekeel
ina;interlingua
inc;India keeled
ind;indoneesia
ine;indoeuroopa keeled
inh;inguši
ipk;injupiaki
ira;Iraani keeled
iro;irokeesi keeled
izh;isuri
ita;itaalia
jav;jaava
jbo;ložban
jpn;jaapani
jpr;juudipärsia
jrb;juudiaraabia
kaa;karakalpaki
kab;kabiili
kac;katšini
kal;grööni
kam;kamba
kan;kannada
kar;kareni keeled
kas;kašmiiri
kaz;kasahhi
kau;kanuri
kaw;kaavi
kbd;kabardi-tšerkessi
kha;khasi
khi;khoisani keeled
khm;khmeeri
kho;saka
kik;kikuju
kin;ruanda
kir;kirgiisi
kjh;hakassi
kmb;mbundu
koi;permikomi
kok;konkani
kom;komi
kon;kongo
kor;korea
kos;kosrae
kpe;kpelle
krc;karatšai-balkaari
krl;karjala
kro;kruu keeled
kru;kuruhhi
kua;kvanjama (ambo)
kum;kumõki
kur;kurdi
kut;kutenai
lad;ladiino
lah;lahnda
lam;lamba
lao;lao
lat;ladina
lav;läti
lbe;laki
lez;lesgi
lim;limburgi
lin;lingala
lit;leedu
liv;liivi
lol;mongo
loz;lozi
ltz;letseburgi
lua;Kasai luba
lub;Katanga luba
lug;ganda
lui;luisenjo
lun;lunda
luo;luo (Keenia ja Tansaania)
lus;mizo
mac;makedoonia
mad;madura
mag;magahi
mah;maršalli
mai;maithili
mak;makassari
mal;malajalami
man;malinke
mao;maoori
map;austroneesia keeled
mar;marathi
mas;maasai
may;malai
mdf;mokša
mdr;mandari
men;mende
mfe;Mauritiuse kreoolkeel
mga;keskiiri (900–1200)
mic;mikmaki
min;minangkabau
mis;kodeerimata keeled
mkh;moni-khmeeri keeled
mlg;malagassi
mlt;malta
mnc;mandžu
mni;manipuri
mno;manobo keeled
moh;mohoogi
mol;moldova
mon;mongoli
mos;moore
mul;mitu keelt
mun;munda keeled
mus;maskogi
mwl;miranda
mwr;maarvari
myn;maaja keeled
myv;ersa
nah;asteegi keeled
nai;Põhja-Ameerika indiaani keeled
nap;napoli
nau;nauru
nav;navaho
nbl;lõunandebele
nde;ndebele
ndo;ndonga
nds;alamsaksa
nep;nepali
new;nevari
nia;niasi
nic;Nigeri-Kordofani keeled
niu;niue
nno;uusnorra
nob;norra bokmål
nog;nogai
non;vanapõhja
nor;norra
nqo;nkoo
nso;pedi
nzi;nzima
nub;Nuubia keeled
nwc;vananevari
nya;njandža
nym;njamvesi
nyn;njankole
nyo;njoro
oci;oksitaani (pärast 1500. a)
oji;odžibvei
ori;oria
orm;oromo
osa;oseidži
oss;osseedi
ota;osmanitürgi (1500-1928)
oto;otomi keeled
paa;Paapua keeled
pag;pangasinani
pal;pahlavi
pam;pampanga
pan;pandžabi
pap;papiamento
pau;belau
peo;vanapärsia (u 600–400 eKr)
per;pärsia
phi;Filipiini keeled
phn;foiniikia
pli;paali
pol;poola
pon;poonpei
por;portugali
pra;praakriti keeled
pro;vanaprovansi (1500. a-ni)
pus;puštu
que;ketšua
raj;radžastani
rap;rapanui
rar;rarotonga
roa;romaani keeled
roh;romanši
rom;mustlaskeel
rsl;vene viipekeel
rum;rumeenia
run;rundi
rup;aromuuni
rus;vene
rut;rutuli
sad;sandave
sag;sango
sah;jakuudi
sai;Lõuna-Ameerika indiaani keeled
sal;sališi keeled
sam;Samaaria aramea
san;sanskriti
sas;sasaki
sat;santali
scn;sitsiilia
sco;šoti
sel;sölkupi
sem;semi keeled
sga;vanaiiri (900. a-ni)
sgn;viipekeeled
shn;šani
sid;sidamo
sin;singali
sio;siuu keeled
sit;hiina-tiibeti keeled
sla;slaavi keeled
slo;slovaki
slv;sloveeni
sma;lõunasaami
sme;põhjasaami
smi;saami keeled
smj;Lule saami
smn;Inari saami
smo;samoa
sms;koltasaami
sna;šona
snd;sindhi
snk;soninke
sog;sogdi
som;somaali
son;songai keeled
sot;sotho
spa;hispaania
srd;sardi
srn;sranani
srp;serbia
srr;sereri
ssa;Niiluse-Sahara keeled
ssw;svaasi
suk;sukuma
sun;sunda
sus;susu
sux;sumeri
swa;suahiili
swe;rootsi
syc;vanasüüria
syr;süüria
zap;sapoteegi
zbl;Blissi sümbolid
zen;zenaga
zgh;Maroko tamasikti kirjakeel
zha;tšuangi
znd;zande keeled
zza;zaza
zul;suulu
zun;sunji
zxx;keelelise sisuta
tah;tahiti
tai;kami-tai keeled
tam;tamili
tat;tatari
tcy;tulu
tel;telugu
tem;temne
ter;terena
tet;tetumi
tgk;tadžiki
tgl;tagalogi
tha;tai
tib;tiibeti
tig;tigree
tir;tigrinja
tiv;tivi
tkl;tokelau
tlh;klingoni
tli;tlingiti
tmh;tamašeki
tog;tonga (Malawis)
ton;tonga (Okeaanias)
tpi;tok-pisini
tsi;tsimši keeled
tsn;tsvana
tso;tsonga
tuk;türkmeeni
tum;tumbuka
tup;tupii keeled
tur;türgi
tut;Altai keeled
twi;tvii
tvl;tuvalu
tyv;tõva
udm;udmurdi
uga;ugariti
uig;uiguuri
ukr;ukraina
umb;umbundu
und;määratlemata keeled
urd;urdu
uzb;usbeki
vai;vai
wak;vakaši keeled
wal;volaita
war;varai
was;vašo
wel;kõmri
ven;venda
wen;sorbi keeled
vep;vepsa
vie;vietnami
wln;vallooni
vol;volapük
wol;volofi
vot;vadja
xal;kalmõki
xho;koosa
yao;jao
yap;japi
yid;jidiš
yor;joruba
ypk;jupiki keeled
yrk;neenetsi
"""
    for line in data.splitlines():
        if line:
            kood, nimi = line.lower().split(';')
            k.read.append(Klrida(kood=kood, nimi=nimi))

    k = Klassifikaator(kood='RIIK', nimi='Riik')
    data = """
﻿Albania;AL;ALB
Andorra;AD;AND
Austria;AT;AUT
Belarus;BY;BLR
Belgium;BE;BEL
Bosnia and Herzegovina;BA;BIH
Bulgaria;BG;BGR
Croatia;HR;HRV
Cyprus;CY;CYP
Czech Republic;CZ;CZE
Denmark;DK;DNK
Estonia;EE;EST
Finland;FI;FIN
France;FR;FRA
Germany;DE;DEU
Gibraltar;GI;GIB
Greece;GR;GRC
Hungary;HU;HUN
Iceland;IS;ISL
Ireland;IE;IRL
Italy;IT;ITA
Latvia;LV;LVA
Liechtenstein;LI;LIE
Lithuania;LT;LTU
Luxembourg;LU;LUX
Macedonia;MK;MKD
Malta;MT;MLT
Moldova;MD;MDA
Monaco;MC;MCO
Netherlands;NL;NLD
Norway;NO;NOR
Poland;PL;POL
Portugal;PT;PRT
Romania;RO;ROU
Russia;RU;RUS
San Marino;SM;SMR
Serbia;RS;SRB
Slovakia;SK;SVK
Slovenia;SI;SVN
Spain;ES;ESP
Sweden;SE;SWE
Switzerland;CH;CHE
Ukraine;UA;UKR
United Kingdom;GB;GBR
Kosovo;RS;XKX
Montenegro;ME;MNE
"""
    for line in data.splitlines():
        if line:
            nimi, kood2, kood3 = line.split(';')
            k.read.append(Klrida(kood=kood3, nimi=nimi))

def insert_tulemusmall():
    Tulemusmall(rp_uri=const.RPT_MATCH_CORRECT,
                nimi='match_correct',
                kirjeldus='Tulemuseks on 1 pall, kui valiti õige vastus')
    Tulemusmall(rp_uri=const.RPT_MAP_RESPONSE,
                nimi='map_response',
                kirjeldus='Tulemuseks on valitud vastusele määratud pallid')
    Tulemusmall(rp_uri=const.RPT_MAP_RESPONSE_POINT,
                nimi='map_response_point',
                kirjeldus='Tulemuseks on valitud punkt')

def insert_koht():
    k = Koht(nimi='Eksamikeskus')
    k.flush()
    assert k.id == const.KOHT_EKK

    # k1 = Koht(nimi=u'Gustav Adolfi Gümnaasium', piirkond_id=298) # Kesklinn
    # k2 = Koht(nimi=u'Tallinna Nõmme Gümnaasium', piirkond_id=524) # Nõmme
    # k3 = Koht(nimi=u'Tallinna Pae Gümnaasium', piirkond_id=387) # Lasnamäe
    # k4 = Koht(nimi=u'Tallinna Arte Gümnaasium', piirkond_id=176) # Haabersti
    # k5 = Koht(nimi=u'Tallinna Lilleküla Gümnaasium', piirkond_id=339) # Kristiine
    # k6 = Koht(nimi=u'Kose Gümnaasium', piirkond_id=37) # Harju
    # k7 = Koht(nimi=u'Jüri Gümnaasium', piirkond_id=37) # Harju
    # k8 = Koht(nimi=u'Tallinna Saksa Gümnaasium', piirkond_id=482) # Mustamäe

    Asukohamaarus(nimetav='Tallinn', kohamaarus='Tallinnas')
    Asukohamaarus(nimetav='maa', kohamaarus='maal')
    Asukohamaarus(nimetav='mäe', kohamaarus='mäel')    
    Asukohamaarus(nimetav='järve', kohamaarus='järvel')
    Asukohamaarus(nimetav='Tapa', kohamaarus='Tapal')
    Asukohamaarus(nimetav='Loksa', kohamaarus='Loksal')
    Asukohamaarus(nimetav='Kose', kohamaarus='Kosel')

def insert_ained(k):    
    k_et = Klrida(kood='E', nimi='Eesti keel, kirjandus (eesti õppekeel)')
    k_ru = Klrida(kood='W', nimi='Vene keel, kirjandus (vene õppekeel)')
    en = Klrida(kood='I', nimi='Inglise keel')
    de = Klrida(kood='S', nimi='Saksa keel')
    ru = Klrida(kood='V', nimi='Vene keel')
    fr = Klrida(kood='P', nimi='Prantsuse keel')
    et = Klrida(kood='R', nimi='Eesti keel teise keelena')
    m = Klrida(kood='M', nimi='Matemaatika')
    lo = Klrida(kood='lo', nimi='Loodusõpetus')
    b = Klrida(kood='B', nimi='Bioloogia')
    g = Klrida(kood='G', nimi='Geograafia')
    f = Klrida(kood='F', nimi='Füüsika')
    km = Klrida(kood='K', nimi='Keemia')
    io = Klrida(kood='io', nimi='Inimeseõpetus')
    a = Klrida(kood='A', nimi='Ajalugu')
    yo = Klrida(kood='C', nimi='Ühiskonnaõpetus')
    mu = Klrida(kood='mu', nimi='Muusika')
    knst = Klrida(kood='knst', nimi='Kunst')
    to = Klrida(kood='to', nimi='Tööõpetus')
    kodu = Klrida(kood='kodu', nimi='Käsitöö ja kodundus')
    tehn = Klrida(kood='tehn', nimi='Tehnoloogiaõpetus')
    kehk = Klrida(kood='kehk', nimi='Kehaline kasvatus')

    # gümnaasiumis lisanduvad:
    ee = Klrida(kood='ee', nimi='Eesti keel')
    ki = Klrida(kood='ki', nimi='Kirjandus')

    # eesti keele tasemeeksamite õppeaine
    rk = Klrida(kood='RK', nimi='Riigikeel')
    # seaduse tundmise eksamite õppeaine
    c = Klrida(kood='kod', nimi='Kodakondsus')        

    # yldõpetus
    yld = Klrida(kood='yld', nimi='Üldõpetus')
    yp = Klrida(kood='yp', nimi='Üldpädevus')    
    
    k.lisaread([k_et, k_ru, en, de, ru, fr, et, m, lo, b, g, f, 
                km, io, a, yo, mu, knst, to, kodu, tehn, kehk, ee, ki, rk, c, yld, yp])
   

    # füüsika
    f.lisaalamad('TEEMA',
                 [Klrida(kood='opt', nimi='Optika', bitimask=15),
                  Klrida(kood='meh', nimi='Mehaanika', bitimask=15)\
                      .lisaalamad('ALATEEMA',
                                  [Klrida(kood='1', nimi='Kinemaatika'),
                                   Klrida(kood='2', nimi='Dünaamika'),
                                   Klrida(kood='3', nimi='Võnkumised ja lained'),
                                   Klrida(kood='4', nimi='Jäävusseadused mehaanikas'),
                                   ]),
                  Klrida(kood='soe', nimi='Soojusõpetus', bitimask=15),
                  Klrida(kood='elop', nimi='Elektriõpetus', bitimask=15),
                  Klrida(kood='aat', nimi='Aatomi- ja universumiõpetus', bitimask=15),
                  Klrida(kood='alus', nimi='Füüsikalise looduskäsitluse alused', bitimask=15)\
                      .lisaalamad('ALATEEMA',
                                  [Klrida(kood='1', nimi='Sissejuhatus füüsikasse'),
                                   Klrida(kood='2', nimi='Füüsika uurimismeetodid'),
                                   Klrida(kood='3', nimi='Füüsika üldmudelid'),
                                   Klrida(kood='4', nimi='Füüsika üldprintsiibid'),
                                   ]),
                  Klrida(kood='elmag', nimi='Elektromagnetism', bitimask=15)\
                      .lisaalamad('ALATEEMA',
                                  [Klrida(kood='1', nimi='Elektriväli ja magnetväli'),
                                   Klrida(kood='2', nimi='Elektromagnetväli'),
                                   Klrida(kood='3', nimi='Elektromagnetlained'),
                                   Klrida(kood='4', nimi='Valguse ja aine vastastikmõju'),
                                   ]),
                  Klrida(kood='ene', nimi='Energia', bitimask=15)\
                      .lisaalamad('ALATEEMA',
                                  [Klrida(kood='1', nimi='Elektrivool'),
                                   Klrida(kood='2', nimi='Elektromagnetismi rakendused'),
                                   Klrida(kood='3', nimi='Soojusnähtused'),
                                   Klrida(kood='4', nimi='Termodünaamika ja energeetika alused'),
                                   ]),
                  Klrida(kood='mega', nimi='Mikro- ja megamaailma füüsika', bitimask=15)\
                      .lisaalamad('ALATEEMA',
                                  [Klrida(kood='1', nimi='Aine ehituse alused'),
                                   Klrida(kood='2', nimi='Mikromaailma füüsika'),
                                   Klrida(kood='3', nimi='Megamaailma füüsika'),
                                   ]),
                  ])

    # ajalugu
    a.lisaalamad('TEEMA',
                 [Klrida(kood='yld', nimi='Üldajalugu', bitimask=15)\
                      .lisaalamad('ALATEEMA',
                                  [Klrida(kood='1', nimi='Antiikaeg'),
                                   Klrida(kood='2', nimi='Keskaeg'),
                                   Klrida(kood='3', nimi='Uusaeg'),
                                   ]),
                  Klrida(kood='ee16', nimi='Eesti ajalugu kuni 16.-17. sajandi vahetuseni', bitimask=15)\
                      .lisaalamad('ALATEEMA',
                                  [Klrida(kood='1', nimi='Esiaeg'),
                                   Klrida(kood='2', nimi='Keskaeg'),
                                   Klrida(kood='3', nimi='Üleminekuaeg keskajast uusaega'),
                                   ]),
                  Klrida(kood='ee19', nimi='Eesti ajalugu kuni 19. sajandi lõpuni', bitimask=15)\
                      .lisaalamad('ALATEEMA',
                                  [Klrida(kood='1', nimi='Rootsi aeg'),
                                   Klrida(kood='2', nimi='Eesti XVIII sajandil'),
                                   Klrida(kood='3', nimi='Eesti XIX sajandil ja XX sajandi algul'),
                                   ]),
                 # [Klrida(nimi=u'Lähiajalugu', bitimask=15)\
                 #      .lisaalamad('ALATEEMA',
                 #                  [Klrida(nimi=u'Maailm kahe maailmasõja vahel 1918-1939'),
                 #                   Klrida(nimi=u'Teine maailmasõda 1939-1945'),
                 #                   Klrida(nimi=u'Maailm pärast Teist maailmasõda 1945-2000'),
                 #                   ]),
                  Klrida(kood='la1', nimi='Lähiajalugu I - Eesti ja maailm 20. sajandi esimesel poolel', bitimask=15)\
                      .lisaalamad('ALATEEMA',
                                  [Klrida(kood='1', nimi='Maailm Esimese maailmasõja eel'),
                                   Klrida(kood='2', nimi='Esimene maailmasõda'),
                                   Klrida(kood='3', nimi='Teine maailmasõda'),
                                   ]),
                  Klrida(kood='la2', nimi='Lähiajalugu II - Eesti ja maailm 20. sajandi teisel poolel', bitimask=15)\
                      .lisaalamad('ALATEEMA',
                                  [Klrida(kood='1', nimi='Külm sõda'),
                                   Klrida(kood='2', nimi='Demokraatlik maailm pärast Teist maailmasõda'),
                                   Klrida(kood='3', nimi='NSVL ja kommunistlik süsteem'),
                                   Klrida(kood='4', nimi='Maailm sajandivahetusel'),
                                   ]),
                  Klrida(kood='la3', nimi='Lähiajalugu III - 20. sajandi arengu põhijooned: Eesti ja maailm', bitimask=15)\
                      .lisaalamad('ALATEEMA',
                                  [Klrida(kood='1', nimi='Eluolu ja kultuur'),
                                   Klrida(kood='2', nimi='Sõja ja rahu küsimus'),
                                   Klrida(kood='3', nimi='Inimsusvastased kuriteod'),
                                   Klrida(kood='4', nimi='Muu maailm'),
                                   ]),

                  ])

    # keemia
    km.lisaalamad('TEEMA',
                 [Klrida(kood='mis', nimi='Millega tegeleb keemia?', bitimask=4)\
                      .lisaalamad('ALATEEMA',
                                  [Klrida(nimi='Keemia meie ümber. Füüsikalised omadused'),
                                   Klrida(nimi='Keemilised reaktsioonid'),
                                   Klrida(nimi='Lahused ja pihused'),
                                   Klrida(nimi='Lahuste protsendilise koostise arvutused'),
                                   ]),
                  Klrida(kood='ehitus', nimi='Aatomi ehitus, perioodilisustabel. Ainete ehitus', bitimask=4)\
                      .lisaalamad('ALATEEMA',
                                  [Klrida(nimi='Aatomi ehitus'),
                                   Klrida(nimi='Keemilised elemendid'),
                                   Klrida(nimi='Perioodilisustabeli seos aatomite elektronstruktuuriga'),
                                   Klrida(nimi='Metallid ja mittemetallid'),
                                   Klrida(nimi='Liht- ja liitained. Molekulid, aine valem'),
                                   Klrida(nimi='Keemiline side'),
                                   Klrida(nimi='Aatommass ja molekulmass'),
                                   Klrida(nimi='Ioonid, ioonsed ained'),
                                   Klrida(nimi='Molekulaarsed ja mittemolekulaarsed ained'),
                                   ]),
                  Klrida(kood='HO', nimi='Hapnik ja vesinik', bitimask=4)\
                      .lisaalamad('ALATEEMA',
                                  [Klrida(nimi='Hapnik, hapnik kui oksüdeerija'),
                                   Klrida(nimi='Oksiidid'),
                                   Klrida(nimi='Oksüdatsiooniaste'),
                                   Klrida(nimi='Võrrandite koostamine ja tasakaalustamine'),
                                   Klrida(nimi='Vesinik. Vesi'),
                                   ]),
                  Klrida(kood='hape', nimi='Happed ja alused', bitimask=4)\
                      .lisaalamad('ALATEEMA',
                                  [Klrida(nimi='Happed'),
                                   Klrida(nimi='Neutralisatsioonireaktsioon'),
                                   Klrida(nimi='Hüdroksiidid, leelised. Ohutusnõuded tugevate hapete ja leeliste kasutamisel'),
                                   Klrida(nimi='Lahuste ph-skaala'),
                                   Klrida(nimi='Soolad'),
                                   Klrida(nimi='Happed, alused ja soolad igapäevaelus'),
                                   ]),
                  Klrida(kood='metal', nimi='Tuntumaid metalle', bitimask=4)\
                      .lisaalamad('ALATEEMA',
                                  [Klrida(nimi='Metallid, metalliline side'),
                                   Klrida(nimi='Metallid kui redutseerijad'),
                                   Klrida(nimi='Raktsiooni kiirus'),
                                   Klrida(nimi='Metallide pingerida'),
                                   Klrida(nimi='Metallide korrosioon'),
                                   ]),
                  Klrida(kood='anorg', nimi='Anorgaaniliste ainete põhiklassid', bitimask=4)\
                      .lisaalamad('ALATEEMA',
                                  [Klrida(nimi='Oksiidid'),
                                   Klrida(nimi='Happed, happed argielus'),
                                   Klrida(nimi='Alused. Lagunemisreaktsioonid'),
                                   Klrida(nimi='Soolad. Lahustuvustabel'),
                                   Klrida(nimi='Seosed anorgaaniliste ainete põhiklasside vahel'),
                                   Klrida(nimi='Vee karedus, väetised, ehitusmaterjalid'),
                                   Klrida(nimi='Põhilised keemilise saaste allikad, keskkonnaprobleemid'),
                                   ]),
                  Klrida(kood='lahustub', nimi='Lahustumisprotsess, lahustuvus', bitimask=4)\
                      .lisaalamad('ALATEEMA',
                                  [Klrida(nimi='Lahustumisprotsess, lahustumise soojusefekt'),
                                   Klrida(nimi='Lahuste koostise arvutamine (tiheduse arvestamisega)'),
                                   Klrida(nimi='Mahuprotsent'),
                                   ]),
                  Klrida(kood='mool', nimi='Aine hulk, moolarvutused', bitimask=4)\
                      .lisaalamad('ALATEEMA',
                                  [Klrida(nimi='Aine hulk, mool'),
                                   Klrida(nimi='Molaarmass, gaasi molaarruumala'),
                                   Klrida(nimi='Arvutused reaktsioonivõrrandite põhjal'),
                                   ]),
                  Klrida(kood='sysi', nimi='Süsinik ja süsinikuühendid', bitimask=4)\
                      .lisaalamad('ALATEEMA',
                                  [Klrida(nimi='Süsinik lihtainena'),
                                   Klrida(nimi='Süsiniku oksiidid'),
                                   Klrida(nimi='Süsivesinikud'),
                                   Klrida(nimi='Ettekujutus polümeeridest, polümeerid igapäevaelus'),
                                   Klrida(nimi='Tähtsamad alkoholid ja karboksüülhapped'),
                                   Klrida(nimi='Etanooli füsioloogiline toime'),
                                   ]),
                  Klrida(kood='sysr', nimi='Süsinikuühendite roll looduses, süsinikuühendid materjalidena', bitimask=4)\
                      .lisaalamad('ALATEEMA',
                                  [Klrida(nimi='Ekso- ja endotermilised reaktsioonid'),
                                   Klrida(nimi='Sahhariidid, rasvad, valgud, nende roll organismis'),
                                   Klrida(nimi='Tervisliku toitumise põhimõtted'),
                                   Klrida(nimi='Süsinikuühendid kütusena'),
                                   Klrida(nimi='Tarbekeemia saadused'),
                                   Klrida(nimi='Olmekemikaalide kasutamise ohutusnõuded'),
                                   Klrida(nimi='Keemia ja elukeskkond'),
                                   ]),
                  ## Gümnaasium
                  Klrida(kood='alk', nimi='Alkaanid', bitimask=8)\
                      .lisaalamad('ALATEEMA',
                                  [Klrida(nimi='Süsiniku aatomi olekud'),
                                   Klrida(nimi='Süsinikuühendite nimetamise põhimõtted'),
                                   Klrida(nimi='Struktuurivalemid'),
                                   Klrida(nimi='Alkaanide vastastikmõju veega'),
                                   Klrida(nimi='Orgaaniliste ühendite oksüdeerumine ja põlemine'),
                                   ]),
                  Klrida(kood='asysv', nimi='Asendatud ja küllastumata süsivesinikud', bitimask=8)\
                      .lisaalamad('ALATEEMA',
                                  [Klrida(nimi='Halogeeniühendid'),
                                   Klrida(nimi='Alkoholid, vesinikside'),
                                   Klrida(nimi='Alkohol ja ühiskond'),
                                   Klrida(nimi='Eetrid'),
                                   Klrida(nimi='Amiinid'),
                                   Klrida(nimi='Alkaloididega (narkootikumidega) seotud probleemid'),
                                   Klrida(nimi='Küllastumata ühendid; alkeenid ja alküünid'),
                                   Klrida(nimi='Areenid'),
                                   Klrida(nimi='Fenoolid, keskkonnaprobleemid Eestis'),
                                   Klrida(nimi='Aldehüüdid ja ketoonid'),
                                   Klrida(nimi='Sahhariidid'),
                                   Klrida(nimi='Karboksüülhapped'),
                                   ]),
                  Klrida(kood='estr', nimi='Estrid, amiidid, polümeerid', bitimask=8)\
                      .lisaalamad('ALATEEMA',
                                  [Klrida(nimi='Estrid ja amiidid'),
                                   Klrida(nimi='Pöörduvad reaktsioonid'),
                                   Klrida(nimi='Katalüüs'),
                                   Klrida(nimi='Reaktsiooni kiiruse ja tasakaalu mõisted'),
                                   Klrida(nimi='Polümeerid ja plastmassid'),
                                   ]),
                  Klrida(kood='biol', nimi='Bioloogiliselt olulised ained', bitimask=8)\
                      .lisaalamad('ALATEEMA',
                                  [Klrida(nimi='Di- ja polüsahhariidid, nende hüdrolüüs'),
                                   Klrida(nimi='Tselluloosi tüüpi materjalid'),
                                   Klrida(nimi='Aminohapped ja valgud'),
                                   Klrida(nimi='Rasvad kui estrid'),
                                   Klrida(nimi='Cis-transisomeeria'),
                                   Klrida(nimi='Transhapped'),
                                   Klrida(nimi='Seep ja sünteetilised pesemisvahendid'),
                                   ]),
                  Klrida(kood='orgk', nimi='Orgaaniline keemiatööstus ja energeetika', bitimask=8)\
                      .lisaalamad('ALATEEMA',
                                  [Klrida(nimi='Kütused ja nafta'),
                                   Klrida(nimi='Orgaaniline keemiatööstus'),
                                   Klrida(nimi='Keemiatööstuse seos keskkonna, majanduse ja poliitikaga'),
                                   ]),
                  Klrida(kood='per', nimi='Perioodilised trendid ainete omadustes', bitimask=8)\
                      .lisaalamad('ALATEEMA',
                                  [Klrida(nimi='Keemiliste elementide metalliliste ja mittemetalliliste omaduste muutus perioodilisustabelis'),
                                   Klrida(nimi='Perioodilised trendid lihtainete omadustes'),
                                   Klrida(nimi='Perioodilised trendid ühendite omadustes'),
                                   Klrida(nimi='Keemiliste elementide tüüpiliste oksüdatsiooniastmete seos aatomiehitusega'),
                                   Klrida(nimi='Metallide pingerida'),
                                   Klrida(nimi='Metallide reageerimine vee ning hapete ja soolade lahustega'),
                                   Klrida(nimi='Metallid ja mittemetallid igapäevaelus'),
                                   ]),
                  Klrida(kood='praktika', nimi='Keemilised protsessid praktikas', bitimask=8)\
                      .lisaalamad('ALATEEMA',
                                  [Klrida(nimi='Metallide saamine maagist'),
                                   Klrida(nimi='Elektrolüüs'),
                                   Klrida(nimi='Metallide korrosioon, korrosioonitõrje'),
                                   Klrida(nimi='Keemilised vooluallikad'),
                                   Klrida(nimi='Arvutused reaktsioonivõrrandi järgi (keemiatööstuses või igapäevaelus)'),
                                   ]),
                  Klrida(kood='lahus', nimi='Keemilised reaktsioonid lahustes', bitimask=8)\
                      .lisaalamad('ALATEEMA',
                                  [Klrida(nimi='Ioone sisaldavate lahuste teke'),
                                   Klrida(nimi='Hüdraatumine, kristallhüdraadid'),
                                   Klrida(nimi='Tugevad ja nõrgad happed ning alused, dissotsiatsioonimäär'),
                                   Klrida(nimi='Ioonidevahelised reaktsioonid lahustes'),
                                   Klrida(nimi='Hüdrolüüsuv sool'),
                                   Klrida(nimi='Happed, alused ja soolad looduses ja igapäevaelus'),
                                   Klrida(nimi='Lahuse molaarne kontsentratsioon'),
                                   Klrida(nimi='Lahuste koostise arvutused'),
                                   ]),
                  ])

    # yhiskonnaõpetus
    yo.lisaalamad('TEEMA',
                 ## III kooliaste
                 [Klrida(kood='yhisk', nimi='Ühiskond ja sotsiaalsed suhted', bitimask=4)\
                      .lisaalamad('ALATEEMA',
                                  [Klrida(nimi='Meedia ja teave'),
                                   Klrida(nimi='Ühiskonna sotsiaalne struktuur'),
                                   Klrida(nimi='Ühiskonna institutsionaalne struktuur'),
                                   Klrida(nimi='Ühiskonnaliikmete õigused ja kohustused'),
                                   ]),
                  Klrida(kood='riik', nimi='Riik ja valitsemine', bitimask=4)\
                      .lisaalamad('ALATEEMA',
                                  [Klrida(nimi='Demokraatia'),
                                   Klrida(nimi='Eesti valitsemiskord'),
                                   ]),
                  Klrida(kood='kod', nimi='Kodanikuühiskond'),
                  Klrida(kood='maj', nimi='Majandus', bitimask=4)\
                      .lisaalamad('ALATEEMA',
                                  [Klrida(nimi='Turumajandus'),
                                   Klrida(nimi='Riigieelarve. Maksud'),
                                   Klrida(nimi='Tarbijakaitse'),
                                   ]),
                  ## Gümnaasium
                  Klrida(kood='yhiska', nimi='Ühiskond ja selle areng', bitimask=8)\
                      .lisaalamad('ALATEEMA',
                                  [Klrida(nimi='Ühiskonna uurimine'),
                                   Klrida(nimi='Sotsiaalsed suhted ja institutsioonid'),
                                   Klrida(nimi='Nüüdisühiskond ja selle kujunemine'),
                                   ]),
                  Klrida(kood='demo', nimi='Demokraatliku ühiskonna valitsemine ja kodanikuosalus', bitimask=8)\
                      .lisaalamad('ALATEEMA',
                                  [Klrida(nimi='Riik ja riigi vormid'),
                                   Klrida(nimi='Õigusriik ja võimude lahusus'),
                                   Klrida(nimi='Inimõigused'),
                                   Klrida(nimi='Poliitilised ideoloogiad'),
                                   Klrida(nimi='Valimised'),
                                   Klrida(nimi='Erakonnad ja kodanikuühendused'),
                                   Klrida(nimi='Euroopa Liidu valitsemiskord ja toimimine'),
                                   ]),
                  Klrida(kood='ymaj', nimi='Ühiskonna majandamine', bitimask=8)\
                      .lisaalamad('ALATEEMA',
                                  [Klrida(nimi='Riik ja majandus'),
                                   Klrida(nimi='Tööturg ja hõive'),
                                   Klrida(nimi='Tarbimine ja investeerimine'),
                                   ]),
                  Klrida(kood='maailm', nimi='Maailma areng ja maailmapoliitika', bitimask=8)\
                      .lisaalamad('ALATEEMA',
                                  [Klrida(nimi='Nüüdisaja maailma mitmekesisus ja rahvusvaheline suhtlemine'),
                                   ]),
                  ])

    # geograafia
    g.lisaalamad('TEEMA',
                 ## Põhikool
                 [Klrida(kood='k', nimi='Kaardiõpetus'),
                  Klrida(kood='g', nimi='Geoloogia'),
                  Klrida(kood='p', nimi='Pinnamood'),
                  Klrida(kood='kl', nimi='Kliima'),
                  Klrida(kood='v', nimi='Veestik'),
                  Klrida(kood='lv', nimi='Loodusvööndid'),
                  Klrida(kood='rhv', nimi='Rahvastik ja asustus'),
                  Klrida(kood='maj', nimi='Majandus'),
                  Klrida(kood='kk', nimi='Keskkond ja inimene'),
                  ## Gümnaasium: kaardiõpetus
                  Klrida(kood='yh', nimi='Ühiskonna areng ja globaliseerumine'),
                  Klrida(kood='mrhv', nimi='Maailma rahvastik ja asustus'),
                  Klrida(kood='mmaj', nimi='Maailmamajandus'),
                  Klrida(kood='lit', nimi='Litosfäär'),
                  Klrida(kood='atm', nimi='Atmosfäär'),
                  Klrida(kood='hyd', nimi='Hüdrosfäär'),
                  Klrida(kood='bio', nimi='Biosfäär'),
                  Klrida(kood='ini', nimi='Keskkonna ja inimtegevuse vastasmõjud'),
                  ])
    # bioloogia
    b.lisaalamad('TEEMA',
                 # põhikool
                 [Klrida(kood='uuri', nimi='Uurimisvaldkond', bitimask=7)\
                      .lisaalamad('ALATEEMA',
                                  [Klrida(nimi='Uurimismeetodid'),
                                   Klrida(nimi='Eluavaldused'),
                                   Klrida(nimi='Organismide jaotumine'),
                                   ]),
                  Klrida(kood='loom', nimi='Loomariik', bitimask=7)\
                      .lisaalamad('ALATEEMA',
                                  [Klrida(nimi='Selgroogsete loomade tunnused'),
                                   Klrida(nimi='Selgroogsete loomade aine- ja energiavahetus'),
                                   Klrida(nimi='Selgroogsete loomade paljunemine ja areng'),
                                   Klrida(nimi='Selgrootute loomade tunnused ja eluprotsessid'),
                                   ]),
                  Klrida(kood='taim', nimi='Taimeriik', bitimask=7)\
                      .lisaalamad('ALATEEMA',
                                  [Klrida(nimi='Taimede ehitus ja talitlus'),
                                   Klrida(nimi='Taimede hõimkonnad'),
                                   Klrida(nimi='Taimede tähtsus'),
                                   Klrida(nimi='Taimeraku ehitus'),
                                   Klrida(nimi='Fotosüntees'),
                                   Klrida(nimi='Taimede paljunemine ja levimine'),
                                   ]),
                  Klrida(kood='seen', nimi='Seeneriik', bitimask=7)\
                      .lisaalamad('ALATEEMA',
                                  [Klrida(nimi='Seente tunnused ja eluprotsessid'),
                                   Klrida(nimi='Seente paljunemine'),
                                   Klrida(nimi='Samblikud'),
                                   ]),
                  Klrida(kood='mikro', nimi='Mikroorganismid', bitimask=7)\
                      .lisaalamad('ALATEEMA',
                                  [Klrida(nimi='Bakterid'),
                                   Klrida(nimi='Algloomad'),
                                   Klrida(nimi='Viirused'),
                                   ]),
                  Klrida(kood='okokk', nimi='Ökoloogia ja keskkonnakaitse', bitimask=7)\
                      .lisaalamad('ALATEEMA',
                                  [Klrida(nimi='Ökoloogia'),
                                   Klrida(nimi='Keskkonnakaitse'),
                                   ]),
                  Klrida(kood='ini', nimi='Inimene', bitimask=7)\
                      .lisaalamad('ALATEEMA',
                                  [Klrida(nimi='Elundkonnad'),
                                   Klrida(nimi='Nahk'),
                                   Klrida(nimi='Luud ja lihased'),
                                   Klrida(nimi='Vereringe'),
                                   Klrida(nimi='Seedimine ja eritamine'),
                                           Klrida(nimi='Hingamine'),
                                   Klrida(nimi='Paljunemine ja areng'),
                                   Klrida(nimi='Talitluste regulatsioon'),
                                   Klrida(nimi='Infovahetus'),
                                   ]),
                  Klrida(kood='paril', nimi='Pärilikkus ja muutlikkus', bitimask=7)\
                      .lisaalamad('ALATEEMA',
                                  [Klrida(nimi='Pärilikkus ja muutlikkus'),
                                   Klrida(nimi='Mittepärilik muutlikkus'),
                                   ]),
                  Klrida(kood='evo', nimi='Evolutsioon', bitimask=7)\
                      .lisaalamad('ALATEEMA',
                                  [Klrida(nimi='Evolutsioon'),
                                   ]),
                  # gümnaasium
                  Klrida(kood='buur', nimi='Bioloogia uurimisvaldkonnad', bitimask=8)\
                      .lisaalamad('ALATEEMA',
                                  [Klrida(nimi='Elu tunnused'),
                                   Klrida(nimi='Eluslooduse organiseerituse tasemed'),
                                   Klrida(nimi='Loodusteaduslik meetod'),
                                   ]),
                  Klrida(kood='org', nimi='Organismide koostis', bitimask=8)\
                      .lisaalamad('ALATEEMA',
                                  [Klrida(nimi='Elus ja eluta looduse keemiline koostis'),
                                   Klrida(nimi='Vesi organismides'),
                                   Klrida(nimi='Mineraalained'),
                                   Klrida(nimi='Süsivesikud'),
                                   Klrida(nimi='Lipiidid'),
                                   Klrida(nimi='Valgud'),
                                   Klrida(nimi='DNA ja RNA'),
                                   ]),
                  Klrida(kood='rakk', nimi='Rakk', bitimask=8)\
                      .lisaalamad('ALATEEMA',
                                  [Klrida(nimi='Rakuteooria'),
                                   Klrida(nimi='Koed'),
                                   Klrida(nimi='Raku ehitus'),
                                   ]),
                  Klrida(kood='rakkm', nimi='Rakkude mitmekesisus', bitimask=8)\
                      .lisaalamad('ALATEEMA',
                                  [Klrida(nimi='Taimerakk'),
                                   Klrida(nimi='Seenerakk'),
                                   Klrida(nimi='Seente tähtsus'),
                                   Klrida(nimi='Eeltuumne rakk'),
                                   Klrida(nimi='Bakterite tähtsus'),
                                   Klrida(nimi='Rakkude võrdlus'),
                                   ]),
                  Klrida(kood='orgen', nimi='Organismide energiavajadus', bitimask=8)\
                      .lisaalamad('ALATEEMA',
                                  [Klrida(nimi='Energia saamise viisid'),
                                   Klrida(nimi='ATP'),
                                   Klrida(nimi='Hingamine'),
                                   Klrida(nimi='Käärimine'),
                                   Klrida(nimi='Fotosüntees'),
                                   ]),
                  Klrida(kood='orgar', nimi='Organismide areng', bitimask=8)\
                      .lisaalamad('ALATEEMA',
                                  [Klrida(nimi='Suguline ja mittesugulien paljunemine'),
                                   Klrida(nimi='Rakutsükkel'),
                                   Klrida(nimi='Mitoos, meioos'),
                                   Klrida(nimi='Sugurakkude areng'),
                                   Klrida(nimi='Viljastumine'),
                                   Klrida(nimi='Sünnieelne areng'),
                                   Klrida(nimi='Lootejärgne areng'),
                                   Klrida(nimi='Vananemine'),
                                   ]),
                  Klrida(kood='init', nimi='Inimese talituse regulatsioon', bitimask=8)\
                      .lisaalamad('ALATEEMA',
                                  [Klrida(nimi='Närvisüsteemi ehitus ja talitlus'),
                                   Klrida(nimi='Neuraalne regulatsioon'),
                                   Klrida(nimi='Humoraalne regulatsioon'),
                                   Klrida(nimi='Sisekeskkonna stabiilsuse tagamine'),
                                   Klrida(nimi='Kaitsemehhanismid'),
                                   Klrida(nimi='Termoregulatsioon'),
                                   ]),
                  Klrida(kood='mol', nimi='Molekulaarbioloogilised põhiprotsessid', bitimask=8)\
                      .lisaalamad('ALATEEMA',
                                  [Klrida(nimi='Tunnuste kujunemine'),
                                   Klrida(nimi='Geenide avaldumine'),
                                   Klrida(nimi='Replikatsioon'),
                                   Klrida(nimi='Transkriptsioon'),
                                   Klrida(nimi='Translatsioon'),
                                   Klrida(nimi='Geneetiline kood'),
                                   ]),
                  Klrida(kood='viirus', nimi='Viirused ja bakterid', bitimask=8)\
                      .lisaalamad('ALATEEMA',
                                  [Klrida(nimi='Viiruste ehitus'),
                                   Klrida(nimi='Viiruste paljunemine'),
                                   Klrida(nimi='Viirushaigused'),
                                   Klrida(nimi='Bakterite levik ja paljunemine'),
                                   Klrida(nimi='Geenitehnoloogia'),
                                   ]),
                  Klrida(kood='parm', nimi='Pärilikkus ja muutlikkus (gümn)', bitimask=8)\
                      .lisaalamad('ALATEEMA',
                                  [Klrida(nimi='Pärilik muutlikkus'),
                                   Klrida(nimi='Mittepärilik muutlikkus'),
                                   Klrida(nimi='Mendeli seadused'),
                                   Klrida(nimi='Soo määramine'),
                                   Klrida(nimi='Suguliiteline pärandumine'),
                                   Klrida(nimi='Geneetikaülesanded'),
                                   Klrida(nimi='Pärilikkuse ja keskkonna mõju inimese tervisele'),
                                   ]),
                  Klrida(kood='bioevo', nimi='Bioevolutsioon', bitimask=8)\
                      .lisaalamad('ALATEEMA',
                                  [Klrida(nimi='Darwini evolutsiooniteooria'),
                                   Klrida(nimi='Evolutsioonitõendid'),
                                   Klrida(nimi='Elu päritolu Maail'),
                                   Klrida(nimi='Bioevolutsioon'),
                                   Klrida(nimi='Olelusvõitlus'),
                                   Klrida(nimi='Looduslik valik'),
                                   Klrida(nimi='Kohastumine'),
                                   Klrida(nimi='Liigiteke'),
                                   Klrida(nimi='Makroevolutsioon'),
                                   Klrida(nimi='Süstemaatika ja bioevolutsioon'),
                                   Klrida(nimi='Inimese evolutsioon'),
                                   Klrida(nimi='Bioevolutsiooni käsitlused'),
                                   ]),
                  Klrida(kood='oko', nimi='Ökoloogia', bitimask=8)\
                      .lisaalamad('ALATEEMA',
                                  [Klrida(nimi='Ökoloogilised tegurid'),
                                   Klrida(nimi='Ökosüsteem'),
                                   Klrida(nimi='Toiduahel'),
                                   Klrida(nimi='Ökoloogiline püramiid'),
                                   ]),
                  Klrida(kood='kk', nimi='Keskkonnakaitse', bitimask=8)\
                      .lisaalamad('ALATEEMA',
                                  [Klrida(nimi='Liikide hävimine, kaitse'),
                                   Klrida(nimi='Bioloogiline mitmekesisus'),
                                   Klrida(nimi='Loodus- ja keskkonnakaitse'),
                                   Klrida(nimi='Säästev areng'),
                                   ]),
                  ])

    # matemaatika
    m.lisaalamad('TEEMA',
                 [Klrida(kood='arv', nimi='Arvutamine'),
                  Klrida(kood='geom', nimi='Geomeetria'),              
                  Klrida(kood='moot', nimi='Mõõtmine'),              
                  Klrida(kood='txt', nimi='Tekstülesanded'),              
                  Klrida(kood='alg', nimi='Algebra'),
                  Klrida(kood='pr', nimi='Protsendid'),
                  Klrida(kood='ruum', nimi='Ruumilised kujundid'),
                  Klrida(kood='tn', nimi='Tõenäosusteooria ja statistika'),
                  Klrida(kood='vrr', nimi='Võrrandid'),
                  Klrida(kood='f', nimi='Funktsioonid'),
                  Klrida(kood='hulk', nimi='Arvuhulgad'),
                  Klrida(kood='int', nimi='Integraal'),
                  Klrida(kood='jada', nimi='Jadad'),
                  Klrida(kood='ster', nimi='Stereomeetria'),
                  Klrida(kood='trig', nimi='Trigonomeetria'),
                  Klrida(kood='vekt', nimi='Vektorid'),
                  Klrida(kood='vrrt', nimi='Võrratused'),
                  ])
    m.lisaalamad('ASPEKT',
                 [Klrida(nimi='Lahenduse lihtsus'),
                  Klrida(nimi='Arutluskäik'),
                  Klrida(nimi='Vastuse õigsus'),
                  ])
    m.lisaalamad('KURSUS',
                  [Klrida(kood='L', nimi='Lai'),
                   Klrida(kood='K', nimi='Kitsas'),
                   ])

    # füüsika
    # f
    
    # eesti keel
    ee.lisaalamad('TEEMA',
                  [Klrida(kood='ielu', nimi='Isiklik elu', bitimask=15)\
                       .lisaalamad('ALATEEMA',
                                   [Klrida(nimi='Mina ja teised'),
                                    Klrida(nimi='Kodu ja lähiümbrus'),
                                    Klrida(nimi='Kodukoht Eesti'),
                                    Klrida(nimi='Vaba aeg'),
                                    ]),
                   Klrida(kood='aelu', nimi='Avalik elu', bitimask=15)\
                       .lisaalamad('ALATEEMA',
                                   [Klrida(nimi='Kodu ja lähiümbrus'),
                                    Klrida(nimi='Kodukoht Eesti'),
                                    Klrida(nimi='Riigid ja nende kultuur'),
                                    Klrida(nimi='Vaba aeg'),
                                    ]),
                   Klrida(kood='too', nimi='Töö', bitimask=15)\
                       .lisaalamad('ALATEEMA',
                                   [Klrida(nimi='Mina ja teised'),
                                    Klrida(nimi='Igapäevaelu. Õppimine ja töö'),
                                    ]),
                   Klrida(kood='haridus', nimi='Haridus', bitimask=15)\
                       .lisaalamad('ALATEEMA',
                                   [Klrida(nimi='Igapäevaelu. Õppimine ja töö'),
                                    ]),
                   ])

    ee.lisaalamad('OSKUS',
                  [Klrida(kood='l', nimi='Lugemine'),
                   Klrida(kood='k', nimi='Kõne'),
                   Klrida(kood='u', nimi='Kuulamine'),
                   ])

    ee.lisaalamad('ASPEKT',
                  [Klrida(nimi='Õigekiri'),
                   Klrida(nimi='Teadmised'),
                   Klrida(nimi='Arusaamine',
                          kirjeldus="""
<table>
<tr>
<th>Ülesande täitmine ja teksti sisu</th>
<th>Pallid</th>
<th>Keelekasutus</th>
</tr>

<tr>
<td>
Ülesandest saadakse aru ja see täidetakse täpselt ja laitmatult.
Sisu ammendav, tekst õige pikkusega (esimene ülesanne u 120 sõna, teine u 160 sõna), loogiline ja ladus.
Kirjutis  eeskätt esimene ülesanne  vastab üldtunnustatud vorminõuetele.
</td>
<td>
5
</td>
<td>
Kontekstile ja stiilinormile vastav keelekasutus. 
Lausestus loogiline ja mitmekesine. Kasutatakse sisu täpseks edastamiseks vajalikke keelestruktuure. 
Sõnavara osutab võimet praktiliselt igasuguste ülesannetega toime tulla, on asjakohase   ulatusega, sõnakasutus täpne. Üksikuid lünki sõnavaras osatakse enamasti kompenseerida sünonüümsete keelenditega.
Võib esineda üksikuid kirja- ja keelevigu ning stiilikonarusi, mis ei häiri tekstist arusaamist.
</td>
</tr>

<tr>
<td>
Ülesandest saadakse aru ja selle täitmisega saadakse üsna hästi hakkama.
Sisu asjakohane, tekst õige pikkusega (120/160 sõna), loogiline ja küllaltki sidus.
Kirjutis  eeskätt esimene ülesanne  vastab üldtunnustatud vorminõuetele.
</td>
<td>
4
</td>
<td>
Hea keelekasutus. Kirjutaja on valinud sobiva registri.
Lausestus loogiline ja mitmekesine.
Sõnavara ülesande täitmiseks piisav, aga väljendus lakooniline. 
Esineb üksikuid kontekstilisi tähendusvääratusi ning kirja- ning keelevigu, mis ei sega tekstist arusaamist.
</td>
</tr>

<tr>
<td>
Ülesandest saadakse aru ja selle täitmisega saadakse rahuldavalt hakkama.
Sisu pealiskaudne, tekst enam-vähem õige pikkusega (120/160 sõna) ja piisavalt sidus, et selle mõttest aru saada.
Kirjutis  eeskätt esimene ülesanne  vastab üldtunnustatud vorminõuetele osaliselt.
</td>
<td>
3
</td>
<td>
Rahuldav keelekasutus. Kirjutaja on valinud sobiva registri.
Üksikutes kohtades võib esineda ebaloogilist lausestust või pisut lihtsakoelist sidumist.
Sõnavara üsna piiratud, mistõttu väljendus lakooniline. Üksikutes kohtades esineb ebatäpset sõna- ja vormikasutust.
Esineb kirja- ja keelevigu, kuid teksti mõte on siiski enamasti arusaadav.
</td>
</tr>

<tr>
<td>
Ülesandest saadakse üldjoontes aru, kuid selle täitmises on puudujääke.
Kirjutis võib olla õige pikkusega (120/160 sõna) või mõnevõrra  nt kolmandiku  lühem, sisu aga pealiskaudne ja tekst halvasti struktureeritud, mistõttu teksti mõttest arusaamine nõuab lugejapoolset pingutust.
Kirjutis ei vasta üldtunnustatud vorminõuetele.
</td>
<td>
2
</td>
<td>
Ebarahuldav keelekasutus. Eksimused registri valikul.
Võib esineda ebaloogilist lausestust, mistõttu teksti mõttest arusaamine häiritud. Sidumine on ebaloomulik, esineb sidumata üleminekuid ja madalamatele tasemetele omast hakitust vm süntaktilisi lihtsustusi.
Sõnavara piiratud, esineb sõnakasutusvigu.
Palju eri tüüpi keele- ja/või kirjavigu, mistõttu teksti mõistmine häiritud. 
</td>
</tr>

<tr>
<td>
Ülesandest saadakse aru raskustega ning see jääb suures osas täitmata.
Kirjutis õige pikkusega, kuid tekst katkendlik ja kohati seosetu, või kirjutis nõutust oluliselt (poole võrra) lühem.
Kirjutis ei vasta üldtunnustatud vorminõuetele.
</td>
<td>
1
</td>
<td>
Väga halb keelekasutus. 
Lihtsakoeline madalamatele tasemetele omane lausestus või lõikude sidumatus.
Sõnavara ülesande täitmiseks ebapiisav. 
Keele- ja/või kirjavead takistavad tekstist arusaamist.
</td>
</tr>

<tr>
<td>
Ülesandest ei saada aru ja/või seda ei suudeta täita. Kirjutatu ei täida ülesannet.
Kirjutis liiga lühike (alla poole nõutust) või vastus hindamiseks ebaadekvaatne (kirjutise sisul pole ülesandega midagi ühist).
</td>
<td>
0
</td>
<td>
Tekst nii ebaloomulik ja vigane, et sellest pole võimalik aru saada. 
Sõnavara ja grammatika ei vasta ka kõige madalamale tasemele. 
</td>
</tr>

</table>

""")
                   ])
                
    # saksa keel
    lisa_voorkeele_valdkonnad(de)

    de.lisaalamad('ASPEKT',
                  [Klrida(nimi='Ülesande täitmine ja interaktiivsus',
                          kirjeldus="""5 punkti: Eksaminandi vastus on põhjalik, täielikult ülesandepüstitusele vastav ning eksaminand panustab aktiivselt kogu vestluse jooksul vestluse kulgu.<br/>
4 punkti: Eksaminandi vastus on veel sobiva pikkusega, eksaminand tuleb veel ülesannetega tulemuslikult toime ja panustab enamjaolt aktiivselt vestluse kulgu.<br/>
3 punkti: Eksaminandi vastus on pigem lühike, vastab ülesandepüstitusele vaid osaliselt ning eksaminand osaleb vestluses enamasti passiivselt. <br/>
2 punkti: Eksaminandi vastus on lühike, öeldu jääb tihti ebaselgeks, eksaminandil on raskusi üldse vestluses osalemisega.<br/>
1 punkt: Eksaminandi vastus on liiga lühike, öeldu jääb ebaselgeks, eksaminandil on raskusi vestluses osalemisega. Edasisi aspekte ei hinnata, kuna alus selleks puudub. Eksaminandi kogu suulise eksamiosa vastus hinnatakse 1 punktiga.<br/>
0 punkti: Eksaminand keeldub eksamiülesandeid täitmast, tema kogu suulise eksamiosa vastus hinnatakse  0 punktiga.<br/>
"""),
                   Klrida(nimi='Väljendusoskus', 
                          kirjeldus="""5 punkti: Sõnavara on vaheldusrikas ja kogu vastuse lõikes peaaegu veatu. Eksaminand kasutab situatsioonikohaseid sõnu ja väljendeid. Puuduvaid mõisted on eksaminand suuteline sobivalt ümber sõnastama.<br/>
4 punkti: Eksaminand kasutab situatsioonikohaseid sõnu ja väljendeid, kuid esineb mõningaid vigu. Puuduvaid mõisted on eksaminand suuteline lihilähedaselt ümber sõnastama.<br/>
3 punkti:  Situatsioonikohane sõnavara puudub ja esineb suuremal arvul vigu. Eksaminandil puuduvad mõned vajalikud mõisted, kuid see ei takista  mõistmist.<br/>
1-2 punkti: Lihtne väljenduslaad ja sagedased vead, mis võivad takistada mõistmist.<br/>
0 punkti: Väga lihtne väljenduslaad ja sagedased vead, mis oluliselt takistavad mõistmist.<br/>
"""),
                   Klrida(nimi='Grammatika',
                          kirjeldus="""5 punkti: Veatu või ainult väga üksikud eksimused, lauseehituselt mitmekesine.<br/>
4 punkti: Mõned eksimused, mis ei takista mõistmist ja/või lauseehituselt mitmekesine.<br/>
3 punkti: Rida eksimusi, mis ei takista mõistmist ja/või vähene variatiivsus lauseehituses.<br/>
1-2 punkti: Sagedased vead, mis kohati raskendavad mõistmist, peamiselt lihtlaused.<br/>
0 punkti: Väga sagedased vead. Kohati on mõistmine tagatud vaid tänu selgitavatele küsimustele.<br/>
"""),
                   Klrida(nimi='Hääldus ja intonatsioon',
                          kirjeldus="""5 punkti: Hääldus ja intonatsioon vastavad suulisele standardkeelele, kõnetempo loomulik.<br/>
4 punkti: Kõnes ei ole silmatorkavaid kõrvalekaldeid suulisest standardkeelest. Kõnetempo on enamjaolt loomulik.<br/>
3 punkti: Mõned hääldus- ja intonatsioonivead, mis ei takista mõistmist. Kõnetempo on enamjaolt veel aktsepteeritav.<br/>
1-2 punkti: Olulised kõrvalekalded suulisest standardkeelest nõuavad suhtluspartnerilt teravdatud tähelepanu. Puuduvatest keelenditest tingitud takerduv kõneviis raskendab kohati mõistmist.<br/>
0 punkti: Rasked hääldus- ja intonatsioonivead, samuti katkendlik kõneviis takistavad mõistmist.<br/>
"""),
                   ])

    # prantsuse keel
    lisa_voorkeele_valdkonnad(fr)

    # vene keel
    lisa_voorkeele_valdkonnad(ru)
    
    # inglise keel
    lisa_voorkeele_valdkonnad(en)

    # eesti keel teise keelena
    lisa_voorkeele_valdkonnad(et)
    et.lisaalamad('TEEMA',
                  [Klrida(kood='tase', nimi='Tasemeeksamid', bitimask=15)\
                       .lisaalamad('ALATEEMA',
                                   [Klrida(nimi='Isikuandmed'),
                                    Klrida(nimi='Maja ja kodu, ümbruskond'),
                                    Klrida(nimi='Igapäevaelu'),
                                    Klrida(nimi='Vaba aeg ja meelelahutus'),
                                    Klrida(nimi='Reisimine'),
                                    Klrida(nimi='Suhted teiste inimestega'),
                                    Klrida(nimi='Tervis ja kehahooldus'),
                                    Klrida(nimi='Haridus'),
                                    Klrida(nimi='Sisseostude tegemine'),
                                    Klrida(nimi='Söök ja jook'),
                                    Klrida(nimi='Teenused'),
                                    Klrida(nimi='Kohad'),
                                    Klrida(nimi='Keel'),
                                    Klrida(nimi='Ilm'),
                                    ]),
                   ])
    et.lisaalamad('KEELETASE',
                  [Klrida(kood='A2', nimi='A2'),
                   Klrida(kood='B1', nimi='B1'),
                   Klrida(kood='B2', nimi='B2'),
                   Klrida(kood='C1', nimi='C1'),
                   ])
    rk.lisaalamad('KEELETASE',
                  [Klrida(kood='A2', nimi='A2'),
                   Klrida(kood='B1', nimi='B1'),
                   Klrida(kood='B2', nimi='B2'),
                   Klrida(kood='C1', nimi='C1'),
                   Klrida(kood='1', nimi='algtase', kehtib=False, kuni='2008-01-01'),
                   Klrida(kood='2', nimi='kesktase', kehtib=False, kuni='2008-01-01'),
                   Klrida(kood='3', nimi='kõrgtase', kehtib=False, kuni='2008-01-01'),                   
                   ])

    rk.lisaalamad('ALATEST',
                 [Klrida(kood=const.ALATEST_RK_KIRJUTAMINE, nimi='kirjutamine'),
                  Klrida(kood=const.ALATEST_RK_KUULAMINE, nimi='kuulamine'),
                  Klrida(kood=const.ALATEST_RK_LUGEMINE, nimi='lugemine'),
                  Klrida(kood=const.ALATEST_RK_RAAKIMINE, nimi='rääkimine'),
                  ])


def lisa_voorkeele_valdkonnad(keel):
    keel.lisaalamad('TEEMA',
                  [Klrida(kood='ielu', nimi='Isiklik elu', bitimask=15)\
                       .lisaalamad('ALATEEMA',
                                   [Klrida(nimi='Mina ja teised'),
                                    Klrida(nimi='Kodu ja lähiümbrus'),
                                    Klrida(nimi='Kodukoht Eesti'),
                                    Klrida(nimi='Vaba aeg'),
                                    ]),
                   Klrida(kood='aelu', nimi='Avalik elu', bitimask=15)\
                       .lisaalamad('ALATEEMA',
                                   [Klrida(nimi='Kodu ja lähiümbrus'),
                                    Klrida(nimi='Kodukoht Eesti'),
                                    Klrida(nimi='Riigid ja nende kultuur'),
                                    Klrida(nimi='Vaba aeg'),
                                    Klrida(nimi='Inimene ja ühiskond'), # ainult võõrkeeltes
                                    Klrida(nimi='Kultuur ja looming'), # ainult võõrkeeltes
                                    Klrida(nimi='Keskkond ja tehnoloogia'), # ainult võõrkeeltes
                                    ]),
                   Klrida(kood='too', nimi='Töö', bitimask=15)\
                       .lisaalamad('ALATEEMA',
                                   [Klrida(nimi='Mina ja teised'),
                                    Klrida(nimi='Igapäevaelu. Õppimine ja töö'),
                                    ]),
                   Klrida(kood='haridus', nimi='Haridus', bitimask=15)\
                       .lisaalamad('ALATEEMA',
                                   [Klrida(nimi='Igapäevaelu. Õppimine ja töö'),
                                    ]),
                   ])

