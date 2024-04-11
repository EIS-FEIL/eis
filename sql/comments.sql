-- Kommentaarid genereeritud SQLAlchemy klasside kommentaaridest.
-- Muudatused teha SQLAlchemy klassides, mitte käsitsi siin.
-- eis/model/entityhelper.py
COMMENT ON COLUMN entityhelper.created IS 'kirje loomise aeg';
COMMENT ON COLUMN entityhelper.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN entityhelper.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN entityhelper.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE entityhelper IS 'Andmeklasside olemite baasklass, mis lisab ühised meetodid';

-- eis/model/seade.py
COMMENT ON COLUMN seade.id IS 'kirje identifikaator';
COMMENT ON COLUMN seade.key IS 'parameetri nimi';
COMMENT ON COLUMN seade.svalue IS 'tekstilise parameetri väärtus';
COMMENT ON COLUMN seade.nvalue IS 'täisarvulise parameetri väärtus';
COMMENT ON COLUMN seade.created IS 'kirje loomise aeg';
COMMENT ON COLUMN seade.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN seade.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN seade.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE seade IS 'Süsteemi üldised seaded';

-- eis/model/avaleheinfologi.py
COMMENT ON COLUMN avaleheinfologi.id IS 'kirje identifikaator';
COMMENT ON COLUMN avaleheinfologi.aeg IS 'logi aeg';
COMMENT ON COLUMN avaleheinfologi.avaleheinfo_id IS 'viide teate kirjele';
COMMENT ON COLUMN avaleheinfologi.liik IS 'tegevuse liik: U - muutmine; I - lisamine; D - kustutamine';
COMMENT ON COLUMN avaleheinfologi.data IS 'andmed (pickle)';
COMMENT ON COLUMN avaleheinfologi.kasutaja_id IS 'viide kasutajale';
COMMENT ON COLUMN avaleheinfologi.created IS 'kirje loomise aeg';
COMMENT ON COLUMN avaleheinfologi.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN avaleheinfologi.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN avaleheinfologi.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE avaleheinfologi IS 'Avalehe teadete muudatused';

-- eis/model/deletelog.py
COMMENT ON COLUMN deletelog.id IS 'kirje identifikaator';
COMMENT ON COLUMN deletelog.deleted_id IS 'kustutatud kirje ID';
COMMENT ON COLUMN deletelog.deleted_table IS 'kustutatud kirje tabeli nimi';
COMMENT ON COLUMN deletelog.data IS 'kustutatud kirje sisu stringina';
COMMENT ON COLUMN deletelog.bdata IS 'kustutatud kirje pickle-formaadis';
COMMENT ON COLUMN deletelog.created IS 'kirje loomise aeg';
COMMENT ON COLUMN deletelog.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN deletelog.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN deletelog.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE deletelog IS 'Kustutatud kirjete logi.
    Vajalik jälgede ajamiseks ja ka selleks,
    et kohalikus serveris teaks kustutada keskserveris kustutatud kirjed.';

COMMENT ON COLUMN deletelog_parent.id IS 'kirje identifikaator';
COMMENT ON COLUMN deletelog_parent.deletelog_id IS 'viide kustutatud kirje logile';
COMMENT ON COLUMN deletelog_parent.parent_id IS 'kustutatud kirje vanemtabeli ID';
COMMENT ON COLUMN deletelog_parent.parent_table IS 'kustutatud kirje vanemtabeli nimi';
COMMENT ON COLUMN deletelog_parent.created IS 'kirje loomise aeg';
COMMENT ON COLUMN deletelog_parent.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN deletelog_parent.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN deletelog_parent.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE deletelog_parent IS 'Kustutatud kirjete vanemtabelite logi.
    Vajalik selleks, et ka kohalikus serveris teaks kustutada keskserveris kustutatud kirjed.';

-- eis/model/potext.py
COMMENT ON COLUMN potext.id IS 'kirje identifikaator';
COMMENT ON COLUMN potext.msgid IS 'tekst algkeeles (eesti keeles)';
COMMENT ON COLUMN potext.msgstr IS 'tekst tõlkekeeles';
COMMENT ON COLUMN potext.lang IS 'tõlkekeel';
COMMENT ON COLUMN potext.created IS 'kirje loomise aeg';
COMMENT ON COLUMN potext.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN potext.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN potext.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE potext IS 'Tõlketekstid';

-- eis/model/avalehepilt.py
COMMENT ON COLUMN avalehepilt.id IS 'kirje identifikaator';
COMMENT ON COLUMN avalehepilt.filename IS 'failinimi';
COMMENT ON COLUMN avalehepilt.filesize IS 'faili suurus baitides';
COMMENT ON COLUMN avalehepilt.fileversion IS 'versioon';
COMMENT ON COLUMN avalehepilt.laius_orig IS 'pildi/video tegelik laius';
COMMENT ON COLUMN avalehepilt.korgus_orig IS 'pildi/video tegelik kõrgus';
COMMENT ON COLUMN avalehepilt.alates IS 'kuvamise alguse kuupäev';
COMMENT ON COLUMN avalehepilt.kuni IS 'kuvamise lõpu kuupäev';
COMMENT ON COLUMN avalehepilt.autor IS 'autor';
COMMENT ON COLUMN avalehepilt.allikas IS 'allikas';
COMMENT ON COLUMN avalehepilt.created IS 'kirje loomise aeg';
COMMENT ON COLUMN avalehepilt.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN avalehepilt.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN avalehepilt.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE avalehepilt IS 'Avalehe pilt';

-- eis/model/opt.py
-- eis/model/avaleheinfo.py
COMMENT ON COLUMN avaleheinfo.id IS 'kirje identifikaator';
COMMENT ON COLUMN avaleheinfo.tyyp IS 'teate tüüp: 1 - hoiatus (punane); 2 - tulemus (roheline); 3 - teavitus/info (sinine)';
COMMENT ON COLUMN avaleheinfo.pealkiri IS 'teate pealkiri';
COMMENT ON COLUMN avaleheinfo.sisu IS 'teate sisu';
COMMENT ON COLUMN avaleheinfo.lisasisu IS 'rohkem infot';
COMMENT ON COLUMN avaleheinfo.kellele IS 'kellele kuvatakse (komaga eraldatud): X - kõigile; J - sooritajatele; P - õpetajatele; Ox - kõigile õpilastele; O9 - 9. kl õpilastele; M - soorituskoha admin';
COMMENT ON COLUMN avaleheinfo.alates IS 'kuvamise alguse kuupäev';
COMMENT ON COLUMN avaleheinfo.kuni IS 'kuvamise lõpu kuupäev';
COMMENT ON COLUMN avaleheinfo.created IS 'kirje loomise aeg';
COMMENT ON COLUMN avaleheinfo.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN avaleheinfo.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN avaleheinfo.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE avaleheinfo IS 'Olulise info teated avalehel kuvamiseks';

-- eis/model/usersession.py
-- eis/model/klassifikaator.py
COMMENT ON COLUMN klassifikaator.kood IS 'kirje identifikaator';
COMMENT ON COLUMN klassifikaator.nimi IS 'nimi';
COMMENT ON COLUMN klassifikaator.kehtib IS 'olek: 1 - kehtib; 0 - ei kehti';
COMMENT ON COLUMN klassifikaator.app IS 'rakendus, mille administraator klassifikaatorit haldab: eis=const.APP_EIS - EISi põhimoodul; plank=const.APP_PLANK - plankide moodul';
COMMENT ON COLUMN klassifikaator.seisuga IS 'EHISe klassifikaatori korral viimane EHISest andmete kontrollimise aeg';
COMMENT ON COLUMN klassifikaator.created IS 'kirje loomise aeg';
COMMENT ON COLUMN klassifikaator.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN klassifikaator.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN klassifikaator.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE klassifikaator IS 'Klassifikaatori liik';

COMMENT ON COLUMN klrida.id IS 'kirje identifikaator';
COMMENT ON COLUMN klrida.jrk IS 'järjekorranumber valikutes';
COMMENT ON COLUMN klrida.kood IS 'väärtuse kood (EISi klassifikaatoritel kuni 10 kohta, EHISest üle võetud klassifikaatoritel kuni 25 kohta)';
COMMENT ON COLUMN klrida.kood2 IS 'kood teises klassifikaatoris (KODAKOND korral, ISO2)';
COMMENT ON COLUMN klrida.hkood IS 'hierarhia kood (TEEMA, ALATEEMA korral): ülemkirje hierarhia kood + punkt + selle kirje kood';
COMMENT ON COLUMN klrida.nimi IS 'nimetus';
COMMENT ON COLUMN klrida.idurl IS 'URL identifikaatorina (oppekava.edu.ee klassifikaatorite korral)';
COMMENT ON COLUMN klrida.kirjeldus IS 'täiendav kirjeldus';
COMMENT ON COLUMN klrida.kehtib IS 'olek: 1 - kehtib; 0 - ei kehti';
COMMENT ON COLUMN klrida.alates IS 'kehtivuse algus';
COMMENT ON COLUMN klrida.kuni IS 'kehtivuse lõpp';
COMMENT ON COLUMN klrida.avalik IS 'kas kehtib ka avalikus vaates (ülesandetüübi korral)';
COMMENT ON COLUMN klrida.ylem_id IS 'viide ülemale väärtusele (üldjuhul teisest klassifikaatorist)';
COMMENT ON COLUMN klrida.bitimask IS 'valdkonna või teema või töökäsu puhul kooliastmete bittide summa, kooliastme bitimask on 2 astmes astme kood, vaikimisi kooliastmete korral on astme koodi asemel astendajaks I aste - 0, II  aste - 1, III aste - 2, gümnaasium - 3; õppeainete puhul: 1 - soorituskoha administraator saab isikutele lisada selle aine läbiviija profiili; NULL - soorituskoha administraator ei saa isikutele lisada selle aine läbiviija profiili; erivajaduste puhul: 4=const.ASTE_BIT_III - põhikool; 8=const.ASTE_BIT_G - gümnaasium; nulli põhjuse puhul: 1=const.NULLIP_BIT_P - kasutusel p-testides; 2=const.NULLIP_BIT_E - kasutusel e-testides';
COMMENT ON COLUMN klrida.kirjeldus2 IS 'kirjeldus 2. isikus (tagasisidevormi tunnuse korral)';
COMMENT ON COLUMN klrida.kirjeldus3 IS 'kirjeldus 3. isikus (tagasisidevormi tunnuse korral)';
COMMENT ON COLUMN klrida.kirjeldus_t IS 'tasemete kirjeldused (tagasisidevormi tunnuse korral)';
COMMENT ON COLUMN klrida.testiklass_kood IS 'viide klassile (tagasisidevormi tunnuse korral)';
COMMENT ON COLUMN klrida.ryhm_kood IS 'klassifikaatoriväärtuste rühma klassifikaatori kood (ainete korral ainevaldkond)';
COMMENT ON COLUMN klrida.nullipohjus IS 'kas e-testi hindamisel on kasutusel null punkti põhjuse valikväli (aine korral)';
COMMENT ON COLUMN klrida.kinnituseta IS 'kas taotlus ei vaja EKK kinnitust (erivajaduse korral)';
COMMENT ON COLUMN klrida.created IS 'kirje loomise aeg';
COMMENT ON COLUMN klrida.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN klrida.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN klrida.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE klrida IS 'Klassifikaatori väärtus';

COMMENT ON COLUMN klvastavus.id IS 'kirje identifikaator';
COMMENT ON COLUMN klvastavus.eis_klrida_id IS 'viide EISi klassifikaatorile';
COMMENT ON COLUMN klvastavus.ehis_klrida_id IS 'viide teise süsteemi klassifikaatorile';
COMMENT ON COLUMN klvastavus.ehis_kl IS 'teise (EHISe) klassifikaatori kood';
COMMENT ON COLUMN klvastavus.created IS 'kirje loomise aeg';
COMMENT ON COLUMN klvastavus.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN klvastavus.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN klvastavus.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE klvastavus IS 'EISi ja teiste infosüsteemide (EHIS, oppekava.edu.ee) klassifikaatorite vastavus';

COMMENT ON COLUMN klseos.id IS 'kirje identifikaator';
COMMENT ON COLUMN klseos.ylem_klrida_id IS 'viide ülemkirjele';
COMMENT ON COLUMN klseos.alam_klrida_id IS 'viide alamkirjele';
COMMENT ON COLUMN klseos.created IS 'kirje loomise aeg';
COMMENT ON COLUMN klseos.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN klseos.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN klseos.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE klseos IS 'Klassifikaatorikirjete vahelised seosed';

COMMENT ON COLUMN t_klassifikaator.id IS 'kirje identifikaator';
COMMENT ON COLUMN t_klassifikaator.orig_kood IS 'viide lähtetabelile';
COMMENT ON COLUMN t_klassifikaator.lang IS 'tõlkekeel';
COMMENT ON COLUMN t_klassifikaator.nimi IS 'nimetus';
COMMENT ON COLUMN t_klassifikaator.created IS 'kirje loomise aeg';
COMMENT ON COLUMN t_klassifikaator.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN t_klassifikaator.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN t_klassifikaator.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE t_klassifikaator IS 'Tabeli Klassifikaator tõlge';

COMMENT ON COLUMN t_klrida.id IS 'kirje identifikaator';
COMMENT ON COLUMN t_klrida.orig_id IS 'viide lähtetabelile';
COMMENT ON COLUMN t_klrida.lang IS 'tõlkekeel';
COMMENT ON COLUMN t_klrida.nimi IS 'nimetus';
COMMENT ON COLUMN t_klrida.kirjeldus IS 'täiendav kirjeldus';
COMMENT ON COLUMN t_klrida.pais IS 'HTML päisesse lisatav osa (vahendite korral)';
COMMENT ON COLUMN t_klrida.created IS 'kirje loomise aeg';
COMMENT ON COLUMN t_klrida.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN t_klrida.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN t_klrida.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE t_klrida IS 'Tabeli Klrida tõlge';

-- eis/model/__init__.py
-- eis/model/abiinfo.py
COMMENT ON COLUMN abiinfo.vorm IS 'vormi nimi';
COMMENT ON COLUMN abiinfo.kood IS 'välja nimi vormil';
COMMENT ON COLUMN abiinfo.sisu IS 'abiinfo sisu';
COMMENT ON COLUMN abiinfo.url IS 'juhendi URL';
COMMENT ON COLUMN abiinfo.created IS 'kirje loomise aeg';
COMMENT ON COLUMN abiinfo.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN abiinfo.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN abiinfo.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE abiinfo IS 'Abiinfo';

-- eis/model/testfail.py
COMMENT ON COLUMN testfail.id IS 'kirje identifikaator';
COMMENT ON COLUMN testfail.fail_dok IS 'vaide avalduse digiallkirjastatud dokument';
COMMENT ON COLUMN testfail.fail_ext IS 'avalduse vorming: ddoc või bdoc või asice';
COMMENT ON COLUMN testfail.created IS 'kirje loomise aeg';
COMMENT ON COLUMN testfail.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN testfail.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN testfail.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE testfail IS 'Digiallkirjastamise testimise testfail';

-- eis/model/deletefile.py
COMMENT ON COLUMN deletefile.id IS 'kirje identifikaator';
COMMENT ON COLUMN deletefile.object_name IS 'MinIO objekt';
COMMENT ON COLUMN deletefile.created IS 'kirje loomise aeg';
COMMENT ON COLUMN deletefile.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN deletefile.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN deletefile.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE deletefile IS 'Viited S3 failidele, mis tuleks kustutada, kuna on salvestatud uus versioon';

-- eis/model/meta.py
-- eis/model/countchar.py
-- eis/model/googlecharts_metadata.py
-- eis/model/arvutusprotsess.py
COMMENT ON COLUMN arvutusprotsess.id IS 'kirje identifikaator';
COMMENT ON COLUMN arvutusprotsess.liik IS 'protsessi liik: 1 - testi tulemuste arvutamine; 2 - lõpetamiste kontroll; 3 - statistikaraportite genereerimine; 4 - testi statistika arvutamine; 5 - EHISest õppurite andmete uuendamine; 6 - EHISest õpetajate andmete uuendamine';
COMMENT ON COLUMN arvutusprotsess.testimiskord_id IS 'viide testimiskorrale, mille tulemusi arvutatakse';
COMMENT ON COLUMN arvutusprotsess.toimumisaeg_id IS 'viide toimumisajale, kui arvutatakse ühe toimumisaja tulemusi';
COMMENT ON COLUMN arvutusprotsess.aasta IS 'aastaarv, mille lõpetamisi arvutatakse (lõpetamise kontrolli korral)';
COMMENT ON COLUMN arvutusprotsess.nimekiri_id IS 'viide nimekirjale, kui arvutatakse ühe nimekirja tulemusi';
COMMENT ON COLUMN arvutusprotsess.testsessioon_id IS 'testsessiooni ID, mille raporteid genereeritakse (statistikaraportite genereerimise korral)';
COMMENT ON COLUMN arvutusprotsess.param IS 'muud parameetrid (nt regamise protsessis)';
COMMENT ON COLUMN arvutusprotsess.filename IS 'failinimi';
COMMENT ON COLUMN arvutusprotsess.filesize IS 'faili suurus baitides';
COMMENT ON COLUMN arvutusprotsess.fileversion IS 'versioon';
COMMENT ON COLUMN arvutusprotsess.kirjeldus IS 'protsessi sisu kirjeldus protsesside logi tabelis kuvamiseks';
COMMENT ON COLUMN arvutusprotsess.viga IS 'protsessis tekkinud vea kirjeldus';
COMMENT ON COLUMN arvutusprotsess.pid IS 'protsessi ID opsüsteemis';
COMMENT ON COLUMN arvutusprotsess.kasutaja_id IS 'protsessi käivitanud kasutaja';
COMMENT ON COLUMN arvutusprotsess.algus IS 'protsessi käivitamise aeg';
COMMENT ON COLUMN arvutusprotsess.lopp IS 'protsessi lõppemise aeg';
COMMENT ON COLUMN arvutusprotsess.edenemisprotsent IS 'mitu protsenti tööst on tehtud';
COMMENT ON COLUMN arvutusprotsess.hostname IS 'rakendusserveri nimi';
COMMENT ON COLUMN arvutusprotsess.created IS 'kirje loomise aeg';
COMMENT ON COLUMN arvutusprotsess.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN arvutusprotsess.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN arvutusprotsess.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE arvutusprotsess IS 'Toimumisaja tulemuste arvutamise protsesside logi';

-- eis/model/koht/klaster.py
COMMENT ON COLUMN klaster.id IS 'kirje identifikaator';
COMMENT ON COLUMN klaster.int_host IS 'serveri nimi sisevõrgus, andmevahetuseks';
COMMENT ON COLUMN klaster.staatus IS 'staatus: 0 - pole kasutusel; 1 - kasutusel';
COMMENT ON COLUMN klaster.seqmult IS '100 000 000 kordaja, sekventside algus';
COMMENT ON COLUMN klaster.created IS 'kirje loomise aeg';
COMMENT ON COLUMN klaster.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN klaster.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN klaster.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE klaster IS 'Eksamiserverite klastrid, milles toimub testi sooritamine';

-- eis/model/koht/aadress.py
COMMENT ON COLUMN aadress.id IS 'ADR_ID';
COMMENT ON COLUMN aadress.kood1 IS '1. taseme komponent - maakond';
COMMENT ON COLUMN aadress.kood2 IS '2. taseme komponent - omavalitsus';
COMMENT ON COLUMN aadress.kood3 IS '3. taseme komponent - asustusüksus';
COMMENT ON COLUMN aadress.kood4 IS '4. taseme komponent - väikekoht';
COMMENT ON COLUMN aadress.kood5 IS '5. taseme komponent - liikluspind';
COMMENT ON COLUMN aadress.kood6 IS '6. taseme komponent - nimi';
COMMENT ON COLUMN aadress.kood7 IS '7. taseme komponent - aadressnumber';
COMMENT ON COLUMN aadress.kood8 IS '8. taseme komponent - hoone osa';
COMMENT ON COLUMN aadress.tais_aadress IS 'täisaadress tekstina';
COMMENT ON COLUMN aadress.lahi_aadress IS 'lähiaadress tekstina';
COMMENT ON COLUMN aadress.sihtnumber IS 'sihtnumber';
COMMENT ON COLUMN aadress.staatus IS 'olek: 0 - kehtetu; 1 - kehtiv';
COMMENT ON COLUMN aadress.ads_log_id IS 'ADS muudatuse kirje logId';
COMMENT ON COLUMN aadress.uus_adr_id IS 'kui kirje on tühistatud, siis kehtiva kirje ID';
COMMENT ON COLUMN aadress.created IS 'kirje loomise aeg';
COMMENT ON COLUMN aadress.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN aadress.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN aadress.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE aadress IS 'Isiku või koha aadress';

-- eis/model/koht/aadresskomponent.py
COMMENT ON COLUMN aadresskomponent.created IS 'kirje loomise aeg';
COMMENT ON COLUMN aadresskomponent.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN aadresskomponent.id IS 'kirje identifikaator';
COMMENT ON COLUMN aadresskomponent.tase IS 'komponendi tase: 1 - maakond; 2 - omavalitsus; 3 - asustusüksus; 4 - väikekoht (AÜ AK, GÜ); 5 - liikluspind (tee, tänav); 6 - nimi; 7 - aadressnumber (maja, krunt); 8 - hoone osa (number- ja/või tähtlisand)';
COMMENT ON COLUMN aadresskomponent.kood IS 'komponendi kood, unikaalne taseme piires; tasemel 1 on 2 kohta; tasemel 2 on 3 kohta; tasemetel 3-8 on 4 kohta';
COMMENT ON COLUMN aadresskomponent.nimetus IS 'nimetus';
COMMENT ON COLUMN aadresskomponent.nimetus_liigiga IS 'nimetus liigiga';
COMMENT ON COLUMN aadresskomponent.ylemkomp_tase IS 'ülemkomponendi tase';
COMMENT ON COLUMN aadresskomponent.ylemkomp_kood IS 'ülemkomponendi kood';
COMMENT ON COLUMN aadresskomponent.staatus IS 'olek: 1 - kehtiv; 0 - kehtetu';
COMMENT ON COLUMN aadresskomponent.ads_log_id IS 'ADS muudatuse kirje logId';
COMMENT ON TABLE aadresskomponent IS 'Koopia aadressiandmete süsteemi (ADS) aadressikomponentide klassifikaatorist';

-- eis/model/koht/aadress.vana.py
COMMENT ON COLUMN aadress.id IS 'kirje identifikaator';
COMMENT ON COLUMN aadress.kood1 IS '1. taseme komponent - maakond';
COMMENT ON COLUMN aadress.kood2 IS '2. taseme komponent - omavalitsus';
COMMENT ON COLUMN aadress.kood3 IS '3. taseme komponent - asustusüksus';
COMMENT ON COLUMN aadress.kood4 IS '4. taseme komponent - väikekoht';
COMMENT ON COLUMN aadress.kood5 IS '5. taseme komponent - liikluspind';
COMMENT ON COLUMN aadress.kood6 IS '6. taseme komponent - nimi';
COMMENT ON COLUMN aadress.kood7 IS '7. taseme komponent - aadressnumber';
COMMENT ON COLUMN aadress.kood8 IS '8. taseme komponent - hoone osa';
COMMENT ON COLUMN aadress.normimata IS 'normaliseerimata aadress - vabatekstiliselt sisestatud aadressi lõpp, mida ei olnud võimalik sisestada ADSi komponentide klassifikaatori abil';
COMMENT ON COLUMN aadress.tais_aadress IS 'täisaadress tekstina';
COMMENT ON COLUMN aadress.lahi_aadress IS 'lähiaadress tekstina';
COMMENT ON COLUMN aadress.adr_id IS 'aadressi identifikaatori ADSis, kui aadress on ADSist üles leitud';
COMMENT ON COLUMN aadress.staatus IS 'olek: 0=const.A_STAATUS_PUUDUB - aadress on sisestamata; 1=const.A_STAATUS_N_TEGEMATA - aadress on sisestatud, kuid selle vastet ADSis ei ole veel otsitud; 2=const.A_STAATUS_N_LUHTUS - ADSist ühest vastet ei leitud; 3=const.A_STAATUS_N_TEHTUD - ADSi vaste on leitud; 4=const.A_STAATUS_N_KEHTETU - ADSis kehtetu;';
COMMENT ON COLUMN aadress.leitud IS 'mitu aadressi ADSist leiti';
COMMENT ON COLUMN aadress.meetod IS 'millise teenuse abil ADSi aadress leiti (kompotsing, normal, tekstotsing)';
COMMENT ON COLUMN aadress.teade IS 'viimasel normaliseerimisel saadud teade';
COMMENT ON COLUMN aadress.created IS 'kirje loomise aeg';
COMMENT ON COLUMN aadress.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN aadress.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN aadress.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE aadress IS 'Isiku või koha aadress';

-- eis/model/koht/ryhm.py
COMMENT ON COLUMN ryhm.id IS 'rühma ID, pärit EHISest';
COMMENT ON COLUMN ryhm.koht_id IS 'koha id';
COMMENT ON COLUMN ryhm.nimi IS 'rühma nimetus';
COMMENT ON COLUMN ryhm.liik IS 'rühma liik';
COMMENT ON COLUMN ryhm.created IS 'kirje loomise aeg';
COMMENT ON COLUMN ryhm.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN ryhm.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN ryhm.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE ryhm IS 'Lasteaiarühm';

-- eis/model/koht/oppekeel.py
COMMENT ON COLUMN oppekeel.id IS 'kirje identifikaator';
COMMENT ON COLUMN oppekeel.koht_id IS 'viide õppeasutuse kohale';
COMMENT ON COLUMN oppekeel.oppekeel IS 'õppekeele kood EHISe klassifikaatoris: E - eesti; I - inglise; D - saksa; S - soome; V - vene';
COMMENT ON COLUMN oppekeel.created IS 'kirje loomise aeg';
COMMENT ON COLUMN oppekeel.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN oppekeel.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN oppekeel.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE oppekeel IS 'Õppeasutuse õppekeeled';

-- eis/model/koht/piirkond.py
COMMENT ON COLUMN piirkond.id IS 'kirje identifikaator';
COMMENT ON COLUMN piirkond.nimi IS 'nimi';
COMMENT ON COLUMN piirkond.ylem_id IS 'viide ülemale piirkonnale, mille alampiirkond on antud piirkond';
COMMENT ON COLUMN piirkond.staatus IS 'olek';
COMMENT ON COLUMN piirkond.created IS 'kirje loomise aeg';
COMMENT ON COLUMN piirkond.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN piirkond.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN piirkond.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE piirkond IS 'Testide korraldamise piirkond';

-- eis/model/koht/koht.py
COMMENT ON COLUMN koht.id IS 'kirje identifikaator';
COMMENT ON COLUMN koht.nimi IS 'nimi';
COMMENT ON COLUMN koht.piirkond_id IS 'viide piirkonnale, millesse antud soorituskoht kuulub';
COMMENT ON COLUMN koht.haldusoigus IS 'kas soorituskoht võib ise oma andmeid hallata või mitte';
COMMENT ON COLUMN koht.riik_kood IS 'riigi 3-kohaline ISO kood';
COMMENT ON COLUMN koht.ruumidearv IS 'ruumide arv';
COMMENT ON COLUMN koht.ptestikohti IS 'kohti p-testi sooritajatele';
COMMENT ON COLUMN koht.etestikohti IS 'kohti e-testi sooritajatele';
COMMENT ON COLUMN koht.valitsus_tasekood IS 'viide maakonnale või linnale, mida antud koht valitseb (maa- või omavalitsuse korral); viitab tabeli Aadresskomponent kirjele ja on kujul "tase.kood"';
COMMENT ON COLUMN koht.on_soorituskoht IS 'kas koht on EISi põhisüsteemis kasutusel';
COMMENT ON COLUMN koht.on_plangikoht IS 'kas koht on plankide moodulis kasutusel';
COMMENT ON COLUMN koht.staatus IS 'olek: 1=const.B_STAATUS_KEHTIV - koht on kuskil kasutusel; 0=const.B_STAATUS_KEHTETU - koht pole kasutusel';
COMMENT ON COLUMN koht.kool_regnr IS 'õppeasutuse registreerimisnumber, kui soorituskoht asub mõnes õppeasutuses';
COMMENT ON COLUMN koht.kool_id IS 'õppeasutuse ID EHISes';
COMMENT ON COLUMN koht.koolityyp_kood IS 'kooliliikide klassifikaator EHISes, EISi klassifikaator KOOLITYYP';
COMMENT ON COLUMN koht.alamliik_kood IS 'koolide alamliikide klassifikaator EHISes';
COMMENT ON COLUMN koht.omandivorm_kood IS 'omandivorm';
COMMENT ON COLUMN koht.diplomiseeria IS 'diplomi seeria teine täht; kui on kaks tähte, siis väljastab kool kaht erinevat seeriat (kõrgharidust andva õppeasutuse korral, kasutatakse plankide moodulis)';
COMMENT ON COLUMN koht.aadress_id IS 'viide aadressile';
COMMENT ON COLUMN koht.postiindeks IS 'postiindeks';
COMMENT ON COLUMN koht.normimata IS 'normaliseerimata aadress - vabatekstiliselt sisestatud aadressi lõpp, mida ei olnud võimalik sisestada ADSi komponentide klassifikaatori abil';
COMMENT ON COLUMN koht.klassi_kompl_arv IS 'klassikomplektide arv';
COMMENT ON COLUMN koht.opilased_arv IS 'õpilaste arv';
COMMENT ON COLUMN koht.ehis_seisuga IS 'viimane EHISes uuendamise aeg';
COMMENT ON COLUMN koht.telefon IS 'kooli telefon';
COMMENT ON COLUMN koht.epost IS 'kooli e-posti aadress';
COMMENT ON COLUMN koht.varustus IS 'koolis oleva varustuse vabatekstiline kirjeldus';
COMMENT ON COLUMN koht.seisuga IS 'kohalikus serveris: koha ja sellega seotud kirjete viimase uuendamise aeg';
COMMENT ON COLUMN koht.created IS 'kirje loomise aeg';
COMMENT ON COLUMN koht.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN koht.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN koht.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE koht IS 'Soorituskoht';

-- eis/model/koht/koolinimi.py
COMMENT ON COLUMN koolinimi.id IS 'kirje identifikaator';
COMMENT ON COLUMN koolinimi.koht_id IS 'viide kohale';
COMMENT ON COLUMN koolinimi.nimi IS 'nimi';
COMMENT ON COLUMN koolinimi.alates IS 'kuupäev, millest alates nimi kehtib';
COMMENT ON COLUMN koolinimi.created IS 'kirje loomise aeg';
COMMENT ON COLUMN koolinimi.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN koolinimi.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN koolinimi.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE koolinimi IS 'Soorituskoha kõik nimed, mille järgi saab kohta otsida 
    (nii endised kui ka praegune)';

-- eis/model/koht/ruum.py
COMMENT ON COLUMN ruum.id IS 'kirje identifikaator';
COMMENT ON COLUMN ruum.koht_id IS 'viide soorituskohale';
COMMENT ON COLUMN ruum.tahis IS 'tähis';
COMMENT ON COLUMN ruum.etestikohti IS 'kohti e-testi sooritajatele';
COMMENT ON COLUMN ruum.ptestikohti IS 'kohti p-testi sooritajatele';
COMMENT ON COLUMN ruum.staatus IS 'olek';
COMMENT ON COLUMN ruum.varustus IS 'varustus';
COMMENT ON COLUMN ruum.created IS 'kirje loomise aeg';
COMMENT ON COLUMN ruum.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN ruum.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN ruum.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE ruum IS 'Testi sooritamise ruum';

-- eis/model/koht/olekuinfo.py
COMMENT ON COLUMN olekuinfo.id IS 'kirje identifikaator: 1 - ADSi komponentide klassifikaatori uuendamise aeg; 2 - ADSi aadresside logi jälgimise aeg; 3 - kasutajate arv';
COMMENT ON COLUMN olekuinfo.seisuga IS 'viimase uuendamise aeg';
COMMENT ON COLUMN olekuinfo.seis_id IS 'viimase saadud logikirje id';
COMMENT ON COLUMN olekuinfo.created IS 'kirje loomise aeg';
COMMENT ON COLUMN olekuinfo.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN olekuinfo.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN olekuinfo.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE olekuinfo IS 'ADSi klassifikaatori jm viimase uuendamise aeg';

-- eis/model/koht/kohalogi.py
COMMENT ON COLUMN kohalogi.id IS 'kirje identifikaator';
COMMENT ON COLUMN kohalogi.kasutaja_id IS 'viide muudatuse teinud kasutajale (puudub automaatse ADS uuenduse korral)';
COMMENT ON COLUMN kohalogi.allikas IS 'muudatuse allikas: 1 - EKK, 2 - soorituskoht; 3 - EHIS';
COMMENT ON COLUMN kohalogi.koht_id IS 'viide muudetud kohale';
COMMENT ON COLUMN kohalogi.vali IS 'muudetud välja nimi';
COMMENT ON COLUMN kohalogi.vana IS 'vana väärtus';
COMMENT ON COLUMN kohalogi.uus IS 'uus väärtus';
COMMENT ON COLUMN kohalogi.created IS 'kirje loomise aeg';
COMMENT ON COLUMN kohalogi.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN kohalogi.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN kohalogi.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE kohalogi IS 'Soorituskoha andmete muudatuste logi';

-- eis/model/koht/koolioppekava.py
COMMENT ON COLUMN koolioppekava.id IS 'kirje identifikaator';
COMMENT ON COLUMN koolioppekava.koht_id IS 'viide kohale';
COMMENT ON COLUMN koolioppekava.oppetase_kood IS 'õppetase, EISi klassifikaator OPPETASE: y=const.OPPETASE_YLD - üldharidus; u=const.OPPETASE_KUTSE - kutseharidus; o=const.OPPETASE_KORG - kõrgharidus; NULL - plangivaba tase (alusharidus või huviharidus)';
COMMENT ON COLUMN koolioppekava.kavatase_kood IS 'õppetase/haridustase, klassifikaator KAVATASE (kutse- ja kõrghariduse korral õppekava õppetaseme kood EHISes; alus-, kesk- ja gümnaasiumitaseme korral õppetaseme kood EHISes)';
COMMENT ON COLUMN koolioppekava.on_ehisest IS 'kas andmed on pärit EHISest (kui pole, siis seda kirjet EHISe päringu tulemuse põhjal ei kustutata)';
COMMENT ON COLUMN koolioppekava.created IS 'kirje loomise aeg';
COMMENT ON COLUMN koolioppekava.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN koolioppekava.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN koolioppekava.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE koolioppekava IS 'Soorituskoha õppekavad ja õppekavajärgsed haridustasemed.';

-- eis/model/koht/sert.py
COMMENT ON COLUMN sert.id IS 'kirje identifikaator';
COMMENT ON COLUMN sert.koht_id IS 'viide soorituskohale; keskserveri korral 1; CA korral NULL';
COMMENT ON COLUMN sert.key_pem IS 'CA võti (CA korral)';
COMMENT ON COLUMN sert.req_pem IS 'serditaotlus PEM kujul (kohaliku serveri korral)';
COMMENT ON COLUMN sert.cert_pem IS 'sert PEM kujul: kohaliku serveri korral kohalikule serverile keskserveri poolt väljastatud sert; keskserveri korral koormusjaoturi veebiserveri sert või selle väljastaja sert, millega kohalik server saab vastaspoolt valideerida; CA korral CA sert';
COMMENT ON COLUMN sert.notbefore IS 'serveri serdi kehtivuse algusaeg';
COMMENT ON COLUMN sert.notafter IS 'serveri serdi kehtivuse lõppaeg';
COMMENT ON COLUMN sert.srl IS 'kohaliku serveri serdi seerianumber; keskserveri korral ca.srl';
COMMENT ON COLUMN sert.created IS 'kirje loomise aeg';
COMMENT ON COLUMN sert.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN sert.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN sert.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE sert IS 'Kohalike serverite serdid ja keskserveri sert';

-- eis/model/koht/__init__.py
-- eis/model/koht/asukohamaarus.py
COMMENT ON COLUMN asukohamaarus.id IS 'kirje identifikaator';
COMMENT ON COLUMN asukohamaarus.seq IS 'järjekorranumber';
COMMENT ON COLUMN asukohamaarus.nimetav IS 'kohanime lõpp nimetavas käändes';
COMMENT ON COLUMN asukohamaarus.kohamaarus IS 'kohanime lõpp sees- või alalütlevas käändes';
COMMENT ON COLUMN asukohamaarus.created IS 'kirje loomise aeg';
COMMENT ON COLUMN asukohamaarus.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN asukohamaarus.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN asukohamaarus.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE asukohamaarus IS 'Eksamikohtade asukohamäärus (kohanimed sees- või alalütlevas käändes).
    Taseme- ja seaduse tundmise eksami diplomile kirjutatakse eksamikoht käändes (kus?).
    Kui eksamikoha asula nime lõpp leitakse siit tabelist, siis rakendatakse tabelis toodud vormi.
    Kui asula nime lõppu siit ei leita, siis lisatakse asula nimele "s".';

-- eis/model/kogu/koguylesanne.py
COMMENT ON COLUMN koguylesanne.id IS 'kirje identifikaator';
COMMENT ON COLUMN koguylesanne.ylesandekogu_id IS 'viide kogule';
COMMENT ON COLUMN koguylesanne.ylesanne_id IS 'viide kogusse kuuluvale ülesandele';
COMMENT ON COLUMN koguylesanne.created IS 'kirje loomise aeg';
COMMENT ON COLUMN koguylesanne.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN koguylesanne.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN koguylesanne.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE koguylesanne IS 'Ülesandekogusse kuuluv ülesanne';

-- eis/model/kogu/tktest.py
COMMENT ON COLUMN tktest.id IS 'kirje identifikaator';
COMMENT ON COLUMN tktest.seq IS 'osasisene järjekorranumber';
COMMENT ON COLUMN tktest.tkosa_id IS 'viide töökogumiku osale';
COMMENT ON COLUMN tktest.test_id IS 'viide kogusse kuuluvale testile';
COMMENT ON COLUMN tktest.ylesandekogu_id IS 'viide kogule, millest ülesanne on võetud';
COMMENT ON COLUMN tktest.created IS 'kirje loomise aeg';
COMMENT ON COLUMN tktest.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN tktest.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN tktest.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE tktest IS 'Töökogumikku kuuluv test';

-- eis/model/kogu/tkvaataja.py
COMMENT ON COLUMN tkvaataja.id IS 'kirje identifikaator';
COMMENT ON COLUMN tkvaataja.tookogumik_id IS 'töökogumik';
COMMENT ON COLUMN tkvaataja.kasutaja_id IS 'õpetaja, kellele töökogumik jagati';
COMMENT ON COLUMN tkvaataja.created IS 'kirje loomise aeg';
COMMENT ON COLUMN tkvaataja.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN tkvaataja.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN tkvaataja.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE tkvaataja IS 'Töökogumiku jagamine teisele õpetajale. Jagamisel tekib töökogumiku vaatamise õigus
    ja võimalus töökogumikust enda jaoks koopia teha.';

-- eis/model/kogu/kogufail.py
COMMENT ON COLUMN kogufail.id IS 'kirje identifikaator';
COMMENT ON COLUMN kogufail.ylesandekogu_id IS 'viide ülesandekogule';
COMMENT ON COLUMN kogufail.sisu IS 'eristuskiri tekstina';
COMMENT ON COLUMN kogufail.filename IS 'failinimi';
COMMENT ON COLUMN kogufail.filesize IS 'faili suurus baitides';
COMMENT ON COLUMN kogufail.fileversion IS 'versioon';
COMMENT ON COLUMN kogufail.created IS 'kirje loomise aeg';
COMMENT ON COLUMN kogufail.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN kogufail.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN kogufail.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE kogufail IS 'Ülesandekogu eristuskiri';

-- eis/model/kogu/kogutest.py
COMMENT ON COLUMN kogutest.id IS 'kirje identifikaator';
COMMENT ON COLUMN kogutest.ylesandekogu_id IS 'viide kogule';
COMMENT ON COLUMN kogutest.test_id IS 'viide kogusse kuuluvale testile';
COMMENT ON COLUMN kogutest.created IS 'kirje loomise aeg';
COMMENT ON COLUMN kogutest.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN kogutest.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN kogutest.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE kogutest IS 'Ülesandekogusse kuuluv test';

-- eis/model/kogu/koguteema.py
COMMENT ON COLUMN koguteema.id IS 'kirje identifikaator';
COMMENT ON COLUMN koguteema.teema_kood IS 'teema (varasem valdkond) kogu õppeaines, klassifikaator TEEMA';
COMMENT ON COLUMN koguteema.alateema_kood IS 'alateema (varasem teema), klassifikaator ALATEEMA';
COMMENT ON COLUMN koguteema.ylesandekogu_id IS 'viide kogule';
COMMENT ON COLUMN koguteema.created IS 'kirje loomise aeg';
COMMENT ON COLUMN koguteema.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN koguteema.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN koguteema.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE koguteema IS 'Ülesandekogu valdkonnad ja teemad';

-- eis/model/kogu/tkylesanne.py
COMMENT ON COLUMN tkylesanne.id IS 'kirje identifikaator';
COMMENT ON COLUMN tkylesanne.seq IS 'osasisene järjekorranumber';
COMMENT ON COLUMN tkylesanne.tkosa_id IS 'viide töökogumiku osale';
COMMENT ON COLUMN tkylesanne.ylesanne_id IS 'viide kogusse kuuluvale ülesandele';
COMMENT ON COLUMN tkylesanne.ylesandekogu_id IS 'viide kogule, millest ülesanne on võetud';
COMMENT ON COLUMN tkylesanne.created IS 'kirje loomise aeg';
COMMENT ON COLUMN tkylesanne.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN tkylesanne.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN tkylesanne.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE tkylesanne IS 'Töökogumikku kuuluv ülesanne';

-- eis/model/kogu/tkosa.py
COMMENT ON COLUMN tkosa.id IS 'kirje identifikaator';
COMMENT ON COLUMN tkosa.seq IS 'osa järjekorranumber struktuuris';
COMMENT ON COLUMN tkosa.nimi IS 'nimekirja nimetus';
COMMENT ON COLUMN tkosa.tookogumik_id IS 'töökogumik, mille osa see on';
COMMENT ON COLUMN tkosa.ylem_tkosa_id IS 'viide ülemosa, kui on alamosa';
COMMENT ON COLUMN tkosa.created IS 'kirje loomise aeg';
COMMENT ON COLUMN tkosa.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN tkosa.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN tkosa.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE tkosa IS 'Töökogumiku struktuur';

-- eis/model/kogu/__init__.py
-- eis/model/kogu/tookogumik.py
COMMENT ON COLUMN tookogumik.id IS 'kirje identifikaator';
COMMENT ON COLUMN tookogumik.nimi IS 'nimekirja nimetus';
COMMENT ON COLUMN tookogumik.aine_kood IS 'õppeaine, klassifikaator AINE';
COMMENT ON COLUMN tookogumik.klass IS 'klass';
COMMENT ON COLUMN tookogumik.kasutaja_id IS 'töökogumiku omanik';
COMMENT ON COLUMN tookogumik.avalik IS 'kas kõik pedagoogid võivad seda töökogumikku vaadata';
COMMENT ON COLUMN tookogumik.created IS 'kirje loomise aeg';
COMMENT ON COLUMN tookogumik.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN tookogumik.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN tookogumik.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE tookogumik IS 'Töökogumik';

-- eis/model/kogu/ylesandekogu.py
COMMENT ON COLUMN ylesandekogu.id IS 'kirje identifikaator';
COMMENT ON COLUMN ylesandekogu.nimi IS 'ülesandekogu nimetus';
COMMENT ON COLUMN ylesandekogu.staatus IS 'olek: 0 - kehtetu, 1 - kasutusel';
COMMENT ON COLUMN ylesandekogu.aine_kood IS 'õppeaine, klassifikaator AINE';
COMMENT ON COLUMN ylesandekogu.seotud_ained IS 'seotud õppeainete koodid (kui põhiaine on üldõpetus)';
COMMENT ON COLUMN ylesandekogu.ainevald_kood IS 'õppeaine ainevaldkond (üldõpetuse korral seotud ainete valdkond, kui neil on ühine valdkond)';
COMMENT ON COLUMN ylesandekogu.oskus_kood IS 'osaoskus, klassifikaator OSKUS';
COMMENT ON COLUMN ylesandekogu.keeletase_kood IS 'keeleoskuse tase, klassifikaator KEELETASE';
COMMENT ON COLUMN ylesandekogu.aste_mask IS 'kooliastmed/erialad kodeeritud bittide summana; biti järjekorranumber on astme kood (või vaikimisi astmete korral 0 - I aste; 1 - II aste; 2 - III aste; 3 - gümnaasium)';
COMMENT ON COLUMN ylesandekogu.aste_kood IS 'peamine kooliaste';
COMMENT ON COLUMN ylesandekogu.klass IS 'klass';
COMMENT ON COLUMN ylesandekogu.created IS 'kirje loomise aeg';
COMMENT ON COLUMN ylesandekogu.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN ylesandekogu.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN ylesandekogu.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE ylesandekogu IS 'Ülesandekogu';

-- eis/model/kogu/ylesandekogulogi.py
COMMENT ON COLUMN ylesandekogulogi.id IS 'kirje identifikaator';
COMMENT ON COLUMN ylesandekogulogi.aeg IS 'logi aeg';
COMMENT ON COLUMN ylesandekogulogi.liik IS 'logitava olemi kirjeldus';
COMMENT ON COLUMN ylesandekogulogi.vanad_andmed IS 'vanad andmed';
COMMENT ON COLUMN ylesandekogulogi.uued_andmed IS 'uued andmed';
COMMENT ON COLUMN ylesandekogulogi.ylesandekogu_id IS 'viide ülesandekogule';
COMMENT ON COLUMN ylesandekogulogi.kasutaja_id IS 'viide kasutajale';
COMMENT ON COLUMN ylesandekogulogi.created IS 'kirje loomise aeg';
COMMENT ON COLUMN ylesandekogulogi.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN ylesandekogulogi.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN ylesandekogulogi.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE ylesandekogulogi IS 'Ülesandekogu koostamise ajalugu';

-- eis/model/testimine/vastusaspekt.py
COMMENT ON COLUMN vastusaspekt.id IS 'kirje identifikaator';
COMMENT ON COLUMN vastusaspekt.ylesandevastus_id IS 'viide ülesande vastusele';
COMMENT ON COLUMN vastusaspekt.hindamisaspekt_id IS 'viide hinnatavale aspektile';
COMMENT ON COLUMN vastusaspekt.toorpunktid IS 'toorpunktid (ülesande skaala järgi)';
COMMENT ON COLUMN vastusaspekt.pallid IS 'hindepallid (testiülesande skaala järgi)';
COMMENT ON COLUMN vastusaspekt.toorpunktid_enne_vaiet IS 'toorpunktid enne vaidlustamist';
COMMENT ON COLUMN vastusaspekt.pallid_enne_vaiet IS 'hindepallid enne vaidlustamist';
COMMENT ON COLUMN vastusaspekt.nullipohj_kood IS 'null punkti andmise põhjus, klassifikaator NULLIPOHJ';
COMMENT ON COLUMN vastusaspekt.created IS 'kirje loomise aeg';
COMMENT ON COLUMN vastusaspekt.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN vastusaspekt.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN vastusaspekt.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE vastusaspekt IS 'Ühele ülesandele antud vastuse tulemus ühes aspektis.
    Erinevalt tabelis Hinne olevatest ühe hindaja pandud hinnetest
    on siin lõplikud hinded.';

-- eis/model/testimine/labiviijaklass.py
COMMENT ON COLUMN labiviijaklass.id IS 'kirje identifikaator';
COMMENT ON COLUMN labiviijaklass.labiviija_id IS 'viide hindaja kirjele';
COMMENT ON COLUMN labiviijaklass.klass IS 'klass';
COMMENT ON COLUMN labiviijaklass.paralleel IS 'paralleel';
COMMENT ON COLUMN labiviijaklass.created IS 'kirje loomise aeg';
COMMENT ON COLUMN labiviijaklass.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN labiviijaklass.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN labiviijaklass.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE labiviijaklass IS 'Millise klassi õpilasi hindaja hindab (kasutusel kooli poolt määratud hindaja korral)';

-- eis/model/testimine/hindamine.py
COMMENT ON COLUMN hindamine.id IS 'kirje identifikaator';
COMMENT ON COLUMN hindamine.hindamisolek_id IS 'viide soorituse hindamiskogumi hindamisolekule';
COMMENT ON COLUMN hindamine.staatus IS 'hindamise/sisestamise olek: 0=const.H_STAATUS_HINDAMATA - hindamata; 1=const.H_STAATUS_POOLELI - hindamisel; 2=const.H_STAATUS_LYKATUD - tagasi lükatud; 4=const.H_STAATUS_SUUNATUD - ümber suunatud; 6=const.H_STAATUS_HINNATUD - hinnatud (hindaja poolt kinnitatud)';
COMMENT ON COLUMN hindamine.tyhistatud IS 'kas hindamine on tühistatud (sama soorituse sama liigiga tühistamata hindamise kirjeid ei saa olla rohkem kui üks)';
COMMENT ON COLUMN hindamine.sisestatud IS 'kas kõigi ülesannete hinded on sisestatud';
COMMENT ON COLUMN hindamine.liik IS 'hindamise liik (kui hindamisprotokoll on olemas, siis sama, mis hindamisprotokollis): 1=const.HINDAJA1 - I hindamine; 2=const.HINDAJA2 - II hindamine ; 3=const.HINDAJA3 - III hindamine; 4=const.HINDAJA4 - eksperthindamine; 5=const.HINDAJA5 - vaide korral hindamine; 6=const.HINDAJA6 - kohtuhindamine';
COMMENT ON COLUMN hindamine.hindaja_kasutaja_id IS 'viide hindaja kasutajale (igasuguse hindamise korral)';
COMMENT ON COLUMN hindamine.labiviija_id IS 'viide hindajale (puudub vaide korral hindamisel)';
COMMENT ON COLUMN hindamine.kontroll_labiviija_id IS 'viide teisele hindajale objektiivhinnatava p-testi korral, kui üks hindaja hindab ja teine kontrollib';
COMMENT ON COLUMN hindamine.ekspertmuutis IS 'eksperthindamise korral märge, kas kehtivaid palle muudeti';
COMMENT ON COLUMN hindamine.intervjuu_labiviija_id IS 'viide intervjueerijale (p-testi korral, kui intervjueerija sisestatakse hindamise protokollilt)';
COMMENT ON COLUMN hindamine.hindamisprotokoll_id IS 'viide hindamisprotokollile (hindamisprotokollilt sisestamise korral';
COMMENT ON COLUMN hindamine.lykkamispohjus IS 'kirjaliku soorituse korral hindaja põhjendus, kui ta hindamise tagasi lükkas';
COMMENT ON COLUMN hindamine.hindamispohjus IS 'VI hindamise korral hindamise alus ja põhjendus, miks tulemust muudetakse';
COMMENT ON COLUMN hindamine.uus_hindamine_id IS 'kirjaliku soorituse korral uue hindaja hindamise kirje, kui antud hindaja lükkas soorituse hindamise tagasi ja määrati uus hindaja';
COMMENT ON COLUMN hindamine.pallid IS 'hindamise hindepallide summa';
COMMENT ON COLUMN hindamine.loplik IS 'kas hindamine on lõplik';
COMMENT ON COLUMN hindamine.ksm_naeb_hindaja IS 'kas märkused on nähtavad teistele hindajatele';
COMMENT ON COLUMN hindamine.ksm_naeb_sooritaja IS 'kas märkused on nähtavad sooritajale';
COMMENT ON COLUMN hindamine.on_probleem IS 'kas hindaja on märkinud töö probleemseks';
COMMENT ON COLUMN hindamine.probleem_sisu IS 'kui hindaja on märkinud töö probleemseks, siis probleemi sisu';
COMMENT ON COLUMN hindamine.probleem_varv IS 'probleemse töö värv (#rrggbb või #rgb)';
COMMENT ON COLUMN hindamine.unikaalne IS 'True - hindamiskogumiga hindamise korral, piirang ei luba mitut sama liiki hindamist; False - avaliku vaate hindamiskogumita hindamise korral, kus võib olla mitu hindajat, iga hindab oma ylesannet';
COMMENT ON COLUMN hindamine.komplekt_id IS 'viide komplektile (väärtus peaks olema sama kui hindamisoleku tabelis olev komplekt, aga on siin tabelis vajalik mitmekordse sisestamise võimaldamiseks)';
COMMENT ON COLUMN hindamine.sisestuserinevus IS 'kas I ja II sisestus erinevad (p-testi hindamisprotokolli sisestamise korral)';
COMMENT ON COLUMN hindamine.sisestus IS 'mitmes sisestamine (p-testi hindamisprotokolli kahekordse sisestamise korral on sisestused 1 ja 2, muidu ainult 1)';
COMMENT ON COLUMN hindamine.sisestaja_kasutaja_id IS 'sisestaja kasutaja (ainult sisestamise korral, e-hindamise korral puudub)';
COMMENT ON COLUMN hindamine.created IS 'kirje loomise aeg';
COMMENT ON COLUMN hindamine.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN hindamine.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN hindamine.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE hindamine IS 'Soorituse ja hindamiskogumi hindamine ja/või sisestamine.
    Iga soorituse, hindamisliigi ja sisestuse kohta on üks kirje, 
    mida erinevad sisestajad võivad sisestada, 
    välja arvatud eksperthindamise korral, kus on igal eksperdil oma kirje.
    Kui on p-test, siis on kahekordne sisestamine.';

-- eis/model/testimine/testiosareglogi.py
COMMENT ON COLUMN soorituslogi.id IS 'kirje identifikaator';
COMMENT ON COLUMN soorituslogi.sooritus_id IS 'viide sooritusele';
COMMENT ON COLUMN soorituslogi.tahised IS 'soorituskoha ja soorituse tähised, kriips vahel';
COMMENT ON COLUMN soorituslogi.reg_toimumispaev_id IS 'registreerimisel määratud toimumispäev';
COMMENT ON COLUMN soorituslogi.kavaaeg IS 'sooritajale kavandatud alguse aeg';
COMMENT ON COLUMN soorituslogi.staatus IS 'sooritamise olek';
COMMENT ON COLUMN soorituslogi.hindamine_staatus IS 'hindamise olek';
COMMENT ON COLUMN soorituslogi.pallid IS 'saadud hindepallid';
COMMENT ON COLUMN soorituslogi.pallid_arvuti IS '(esialgne) arvutihinnatav osa hindepallidest';
COMMENT ON COLUMN soorituslogi.pallid_kasitsi IS 'mitte-arvutihinnatav osa hindepallidest';
COMMENT ON COLUMN soorituslogi.tulemus_protsent IS 'saadud hindepallid protsentides suurimast võimalikust tulemusest';
COMMENT ON COLUMN soorituslogi.max_pallid IS 'võimalikud max pallid (sõltub alatestidest vabastusest ja lõdva struktuuri korral komplektist)';
COMMENT ON COLUMN soorituslogi.testiarvuti_id IS 'viide testi sooritamiseks kasutatud arvutile';
COMMENT ON COLUMN soorituslogi.testikoht_id IS 'viide testikohale';
COMMENT ON COLUMN soorituslogi.testiruum_id IS 'viide testiruumile';
COMMENT ON COLUMN soorituslogi.tugiisik_kasutaja_id IS 'viide tugiisikule';
COMMENT ON COLUMN soorituslogi.url IS 'andmeid muutnud tegevuse URL';
COMMENT ON COLUMN soorituslogi.remote_addr IS 'muutja klient';
COMMENT ON COLUMN soorituslogi.server_addr IS 'muutja server';
COMMENT ON COLUMN soorituslogi.created IS 'kirje loomise aeg';
COMMENT ON COLUMN soorituslogi.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN soorituslogi.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN soorituslogi.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE soorituslogi IS 'Soorituse kirje muudatuste logi';

-- eis/model/testimine/aspektihindemarkus.py
COMMENT ON COLUMN aspektihindemarkus.id IS 'kirje identifikaator';
COMMENT ON COLUMN aspektihindemarkus.aspektihinne_id IS 'viide ülesande aspekti hindepallide kirjele, mille kohta märkus käib';
COMMENT ON COLUMN aspektihindemarkus.ekspert_labiviija_id IS 'viide eksperthindajale, kelle märkusega on tegu';
COMMENT ON COLUMN aspektihindemarkus.markus IS 'märkuse tekst';
COMMENT ON COLUMN aspektihindemarkus.created IS 'kirje loomise aeg';
COMMENT ON COLUMN aspektihindemarkus.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN aspektihindemarkus.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN aspektihindemarkus.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE aspektihindemarkus IS 'Eksperthindaja märkus aspekti hinde kohta (vaide korral hindamisel)';

-- eis/model/testimine/toimumisaeg.py
COMMENT ON COLUMN toimumisaeg.id IS 'kirje identifikaator';
COMMENT ON COLUMN toimumisaeg.tahised IS 'testi, testiosa ja testimiskorra tähised, kriips vahel';
COMMENT ON COLUMN toimumisaeg.alates IS 'toimumise ajavahemiku algus';
COMMENT ON COLUMN toimumisaeg.kuni IS 'toimumise ajavahemiku lõpp';
COMMENT ON COLUMN toimumisaeg.testimiskord_id IS 'viide testimiskorrale';
COMMENT ON COLUMN toimumisaeg.testiosa_id IS 'viide testiosale';
COMMENT ON COLUMN toimumisaeg.vaatleja_maaraja IS 'kas eksamikeskus määrab vaatleja';
COMMENT ON COLUMN toimumisaeg.hindaja1_maaraja IS 'hindaja1 määraja: eksamikeskus/soorituskoht/ei';
COMMENT ON COLUMN toimumisaeg.hindaja1_maaraja_valim IS 'valimi hindaja1 määraja: eksamikeskus/soorituskoht/ei';
COMMENT ON COLUMN toimumisaeg.hindaja2_maaraja IS 'hindaja2 määraja: ekk/koht/ei (suulise testi korral või kahekordse mitte-paarishindamisega kirjaliku testi korral)';
COMMENT ON COLUMN toimumisaeg.hindaja2_maaraja_valim IS 'valimi hindaja2 määraja: ekk/koht/ei (suulise testi korral või kahekordse mitte-paarishindamisega kirjaliku testi korral)';
COMMENT ON COLUMN toimumisaeg.intervjueerija_maaraja IS 'kas eksamikeskus määrab intervjueerija (suulise testi korral)';
COMMENT ON COLUMN toimumisaeg.admin_maaraja IS 'kas on vaja testi administraatorit; p-testi korral pole vaja; e-testi korral on administraatorit vaja parajasti siis, kui on kirjalik test';
COMMENT ON COLUMN toimumisaeg.admin_teade IS 'kas saata testi administraatorile administraatoriks määramisel teade';
COMMENT ON COLUMN toimumisaeg.vaatleja_koolituskp IS 'kuupäev, millest varasem koolitus ei tule vaatleja puhul kõne alla';
COMMENT ON COLUMN toimumisaeg.hindaja_koolituskp IS 'kuupäev, millest varasem koolitus ei tule hindaja puhul kõne alla';
COMMENT ON COLUMN toimumisaeg.intervjueerija_koolituskp IS 'kuupäev, millest varasem koolitus ei tule intervjueerija puhul kõne alla';
COMMENT ON COLUMN toimumisaeg.verif IS 'verifitseerimine: V=const.VERIF_VERIFF - Veriff; P=const.VERIF_PROCTORIO - Proctorio';
COMMENT ON COLUMN toimumisaeg.verif_param IS 'Proctorio seaded (Proctorio korral); Veriffi integratsiooni ID konfis (Veriffi korral)';
COMMENT ON COLUMN toimumisaeg.verif_seb IS 'kas on kasutusel Safe Exam Browser (SEB)';
COMMENT ON COLUMN toimumisaeg.seb_konf IS 'SEB konfifail XML kujul';
COMMENT ON COLUMN toimumisaeg.on_arvuti_reg IS 'kas sooritajate arvutite registreerimine on nõutav';
COMMENT ON COLUMN toimumisaeg.on_reg_test IS 'kas teistel sama testimiskorra toimumisaegadel samasse ruumi tehtud arvutite registreeringud kehtivad ka sellel toimumisajal';
COMMENT ON COLUMN toimumisaeg.kahekordne_sisestamine IS 'kas on kahekordne sisestamine (enamasti on, aga eeltestide korral sisestatakse ühekordselt, kuna tulemusi on vaja vaid statistika jaoks)';
COMMENT ON COLUMN toimumisaeg.esimees_maaraja IS 'kas eksamikomisjoni esimehe määramine on kohustuslik';
COMMENT ON COLUMN toimumisaeg.esimees_koolituskp IS 'kuupäev, millest varasem koolitus ei tule komisjoni esimehe puhul kõne alla (TE,SE eksami korral)';
COMMENT ON COLUMN toimumisaeg.komisjoniliige_maaraja IS 'kas eksamikomisjoni liikme määramine on kohustuslik';
COMMENT ON COLUMN toimumisaeg.komisjoniliige_koolituskp IS 'kuupäev, millest varasem koolitus ei tule komisjoni liikme puhul kõne alla (TE,SE eksami korral)';
COMMENT ON COLUMN toimumisaeg.komisjon_maaramise_tahtaeg IS 'komisjoni esimehe ja liikmete määramise tähtaeg';
COMMENT ON COLUMN toimumisaeg.konsultant_koolituskp IS 'kuupäev, millest varasem koolitus ei tule konsultandi puhul kõne alla (konsultatsiooni korral)';
COMMENT ON COLUMN toimumisaeg.reg_labiviijaks IS 'kas läbiviijaks registreerimine on avatud';
COMMENT ON COLUMN toimumisaeg.hindaja_kaskkirikpv IS 'varaseim lubatud kuupäev, millal hindajad on käskkirja lisatud; kui puudub, siis ei ole hindajate käskkirja lisamine nõutav';
COMMENT ON COLUMN toimumisaeg.intervjueerija_kaskkirikpv IS 'varaseim lubatud kuupäev, millal intervjueerijad on käskkirja lisatud; kui puudub, siis ei ole intervjueerijate käskkirja lisamine nõutav';
COMMENT ON COLUMN toimumisaeg.ruumide_jaotus IS 'kas on lubatud soorituskohtades ruume määrata';
COMMENT ON COLUMN toimumisaeg.ruum_voib_korduda IS 'kas ruumi saab samal toimumispäeval kasutada sama toimumisaja mitme testiruumina';
COMMENT ON COLUMN toimumisaeg.ruum_noutud IS 'kas korraldamisel peab määrama päris ruumi (või võib kasutada määramata ruumi)';
COMMENT ON COLUMN toimumisaeg.labiviijate_jaotus IS 'kas on lubatud soorituskohtades läbiviijaid määrata';
COMMENT ON COLUMN toimumisaeg.kohad_avalikud IS 'kas sooritajatele võib neile määratud soorituskohad avaldada (eesti.ee portaalis või soorituskohateateid saates)';
COMMENT ON COLUMN toimumisaeg.kohad_kinnitatud IS 'kas soorituskohtade andmed on kinnitatud (kui on kinnitatud, siis ei saa sooritajaid testimiskorrale suunata ja testiosa tähise muutmine ei too kaasa toimumisaja tähise muutmist)';
COMMENT ON COLUMN toimumisaeg.hinnete_sisestus IS 'kas hindajad saavad tulemusi sisestada';
COMMENT ON COLUMN toimumisaeg.oma_prk_hindamine IS 'kas hindaja saab hinnata ainult oma piirkonna õpilasi (või ka muid)';
COMMENT ON COLUMN toimumisaeg.oma_kooli_hindamine IS 'kas hindaja saab ka oma kooli töid hinnata (või ainult muude koolide õpilaste töid)';
COMMENT ON COLUMN toimumisaeg.sama_kooli_hinnatavaid IS 'ühest koolist hinnatavate õpilaste max arv';
COMMENT ON COLUMN toimumisaeg.hindamise_algus IS 'hetk, millest varem ei saa hinnata';
COMMENT ON COLUMN toimumisaeg.hindamise_luba IS 'kas hindajad võivad hinnata';
COMMENT ON COLUMN toimumisaeg.hindamise_tahtaeg IS 'hindamise tähtaeg';
COMMENT ON COLUMN toimumisaeg.protok_ryhma_suurus IS 'sooritajaid protokollis';
COMMENT ON COLUMN toimumisaeg.samaaegseid_vastajaid IS 'samaaegsete vastajate lubatud max arv';
COMMENT ON COLUMN toimumisaeg.tulemus_kinnitatud IS 'kas tulemused on kinnitatud';
COMMENT ON COLUMN toimumisaeg.aja_jargi_alustatav IS 'true - registreeritud olekus sooritajad saavad automaatselt lahendamist alustada peale algusaja saabumist, administraator ei pea selleks andma alustamise luba; false - lahendamist võib alustada siis, kui testi administraator annab sooritajale alustamise loa';
COMMENT ON COLUMN toimumisaeg.algusaja_kontroll IS 'true - alustamise luba ei võimalda alustada sooritamist enne sooritamise kellaaega; false - alustamise loa olemasolul on võimalik sooritada ka enne alguse kellaaega';
COMMENT ON COLUMN toimumisaeg.kell_valik IS 'true - soorituskohale saab valida ainult toimumisaja seadetes kirjeldatud kellaaja; false - soorituskohale saab kellaaja vabalt sisestada';
COMMENT ON COLUMN toimumisaeg.jatk_voimalik IS 'kas testi administraator saab lubada sooritajal jätkata sooritamist peale seda, kui ta on sooritamise juba lõpetanud';
COMMENT ON COLUMN toimumisaeg.keel_admin IS 'kas testi administraator saab sooritaja soorituskeelt muuta';
COMMENT ON COLUMN toimumisaeg.eelvaade_admin IS 'kas testi administraator saab testi eelvaadet vaadata';
COMMENT ON COLUMN toimumisaeg.prot_admin IS 'kas testi administraator saab toimumise protokolli sisestada/kinnitada: 0=const.PROT_NULL - ei saa; 1=const.PROT_SISEST - saab sisestada, mitte kinnitada; 2=const.PROT_KINNIT - saab sisestada ja kinnitada';
COMMENT ON COLUMN toimumisaeg.prot_eikinnitata IS 'kui True, siis toimumise protokolle soorituskohtades ei kinnitata';
COMMENT ON COLUMN toimumisaeg.nimi_jrk IS 'kas PDF protokollides (üleandmisprotokollides, toimumisprotokollides, hindamisprotokollides) järjestada sooritajad nime järgi (kui ei, siis järjestatakse töö koodi järgi)';
COMMENT ON COLUMN toimumisaeg.valjastuskoti_maht IS 'mitu testitööd mahub ühte kotti';
COMMENT ON COLUMN toimumisaeg.tagastuskoti_maht IS 'mitu testitööd mahub ühte kotti';
COMMENT ON COLUMN toimumisaeg.komplekt_valitav IS 'kas sooritaja saab ise komplekti valida (või valib süsteem juhuslikult)';
COMMENT ON COLUMN toimumisaeg.komplekt_valitav_y1 IS 'kui sooritaja saab komplekti valida, siis kas valida saab ainult iga komplekti esimese ülesande juures (või võib ka mujal valida)';
COMMENT ON COLUMN toimumisaeg.vaatleja_tasu IS 'vaatleja töötasu';
COMMENT ON COLUMN toimumisaeg.vaatleja_lisatasu IS 'läbiviija lisatasu, mida makstakse vaatlejatele, komisjoniliikmetele ja komisjoniesimeestele üleajalise töö eest';
COMMENT ON COLUMN toimumisaeg.komisjoniliige_tasu IS 'eksamikomisjoni liikme tasu';
COMMENT ON COLUMN toimumisaeg.esimees_tasu IS 'eksamikomisjoni esimehe tasu';
COMMENT ON COLUMN toimumisaeg.konsultant_tasu IS 'konsultandi tasu (konsultatsiooni toimumisaja korral)';
COMMENT ON COLUMN toimumisaeg.admin_tasu IS 'testi administraatori tasu';
COMMENT ON COLUMN toimumisaeg.on_kogused IS 'kas ümbrike ja kottide kogused on arvutatud';
COMMENT ON COLUMN toimumisaeg.on_ymbrikud IS 'kas ümbrike ja kottide kirjed on loodud';
COMMENT ON COLUMN toimumisaeg.on_hindamisprotokollid IS 'kas hindamisprotokollid ja muud hindamiseks vajalikud kirjed on loodud';
COMMENT ON COLUMN toimumisaeg.hindajad_seq IS 'toimumisaja hindajate tähiste sekvents';
COMMENT ON COLUMN toimumisaeg.labiviijad_seq IS 'toimumisaja läbiviijate tähiste sekvents';
COMMENT ON COLUMN toimumisaeg.testikohad_seq IS 'toimumisaja testikohtade tähiste sekvents';
COMMENT ON COLUMN toimumisaeg.created IS 'kirje loomise aeg';
COMMENT ON COLUMN toimumisaeg.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN toimumisaeg.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN toimumisaeg.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE toimumisaeg IS 'Testiosa toimumisaeg. Igal testimiskorral on iga testiosa jaoks oma toimumisaeg';

-- eis/model/testimine/kvskann.py
COMMENT ON COLUMN kvskann.id IS 'kirje identifikaator';
COMMENT ON COLUMN kvskann.kysimusevastus_id IS 'viide sooritusele';
COMMENT ON COLUMN kvskann.seq IS 'mitmes skann (küsimuse piires)';
COMMENT ON COLUMN kvskann.skann IS 'skannitud vastus JPG-pildina';
COMMENT ON COLUMN kvskann.laius_orig IS 'pildi tegelik laius';
COMMENT ON COLUMN kvskann.korgus_orig IS 'pildi tegelik kõrgus';
COMMENT ON COLUMN kvskann.created IS 'kirje loomise aeg';
COMMENT ON COLUMN kvskann.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN kvskann.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN kvskann.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE kvskann IS 'Küsimuse vastuse skann';

-- eis/model/testimine/tunnistus.py
COMMENT ON COLUMN tunnistus.id IS 'kirje identifikaator';
COMMENT ON COLUMN tunnistus.kasutaja_id IS 'viide tunnistatud kasutajale';
COMMENT ON COLUMN tunnistus.tunnistusenr IS 'tunnistuse nr, riigieksami korral kujul 2AA-KKKSSS-J, kus: AA - aasta; KKK - kooli kood; SSS - tunnistus.seq sooritaja järjenr oma koolis); J - 1,2,3... (tunnistuse järjenr sooritaja jaoks)';
COMMENT ON COLUMN tunnistus.valjastamisaeg IS 'väljaandmise aeg';
COMMENT ON COLUMN tunnistus.avaldamisaeg IS 'tunnistuse avaldamise aeg (vajalik tasemeeksami sooritusteatel kuvamiseks)';
COMMENT ON COLUMN tunnistus.testsessioon_id IS 'testsessioon, mille soorituste kohta tunnistus antakse (EISi antud tunnistuste korral kohustuslik)';
COMMENT ON COLUMN tunnistus.oppeaasta IS 'õppeaasta (EISi antud tunnistuste korral kohustuslik)';
COMMENT ON COLUMN tunnistus.kool_koht_id IS 'kool, milles sooritaja õppis';
COMMENT ON COLUMN tunnistus.kool_kood IS 'kooli kood - algselt tunnistuse numbri sees olev kooli tähistav arv, enam ei kasutata';
COMMENT ON COLUMN tunnistus.seq IS 'sooritaja järjekorranumber testiliigi ja aasta piires (kasutusel tunnistuse numbri sees)';
COMMENT ON COLUMN tunnistus.filename IS 'failinimi';
COMMENT ON COLUMN tunnistus.filesize IS 'faili suurus baitides';
COMMENT ON COLUMN tunnistus.fileversion IS 'versioon';
COMMENT ON COLUMN tunnistus.staatus IS 'olek: 0=const.N_STAATUS_KEHTETU - kehtetu; 1=const.N_STAATUS_KEHTIV - kehtiv, dok salvestamata; 3=const.N_STAATUS_SALVESTATUD - kehtiv, dok salvestatud; 2=const.N_STAATUS_AVALDATUD - avaldatud';
COMMENT ON COLUMN tunnistus.uuendada IS 'kas on vaja uus tunnistus teha (seatakse peale vaideotsust)';
COMMENT ON COLUMN tunnistus.eesnimi IS 'sooritaja eesnimi tunnistuse andmise ajal';
COMMENT ON COLUMN tunnistus.perenimi IS 'sooritaja perekonnanimi tunnistuse andmise ajal';
COMMENT ON COLUMN tunnistus.testiliik_kood IS 'tunnistuse liik, klassifikaator TESTILIIK';
COMMENT ON COLUMN tunnistus.mallinimi IS 'kasutatud PDF malli nimi';
COMMENT ON COLUMN tunnistus.alus IS 'väljastamise alus (käskkirja nr)';
COMMENT ON COLUMN tunnistus.pohjendus IS 'väljastamise põhjendus (sisestatakse samas sessioonis sooritajale tunnistuse korduva väljastamise korral)';
COMMENT ON COLUMN tunnistus.tyh_pohjendus IS 'tühistamise põhjendus';
COMMENT ON COLUMN tunnistus.aeg_registris IS 'tunnistuste registris andmete lisamise või muutmise aeg või NULL, kui on lisamata';
COMMENT ON COLUMN tunnistus.created IS 'kirje loomise aeg';
COMMENT ON COLUMN tunnistus.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN tunnistus.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN tunnistus.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE tunnistus IS 'Eksamitunnistus';

-- eis/model/testimine/testikonsultatsioon.py
COMMENT ON COLUMN testikonsultatsioon.id IS 'kirje identifikaator';
COMMENT ON COLUMN testikonsultatsioon.eksam_testimiskord_id IS 'viide eksami testimiskorrale';
COMMENT ON COLUMN testikonsultatsioon.kons_testimiskord_id IS 'viide konsultatsiooni toimumiskorrale';
COMMENT ON COLUMN testikonsultatsioon.created IS 'kirje loomise aeg';
COMMENT ON COLUMN testikonsultatsioon.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN testikonsultatsioon.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN testikonsultatsioon.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE testikonsultatsioon IS 'Eksamite testimiskordade seos konsultatsioonikordadega';

-- eis/model/testimine/tagastusymbrikuliik.py
COMMENT ON COLUMN tagastusymbrikuliik.id IS 'kirje identifikaator';
COMMENT ON COLUMN tagastusymbrikuliik.tahis IS 'ümbriku liigi tähis';
COMMENT ON COLUMN tagastusymbrikuliik.nimi IS 'ümbriku liigi nimetus';
COMMENT ON COLUMN tagastusymbrikuliik.toimumisaeg_id IS 'viide toimumisajale';
COMMENT ON COLUMN tagastusymbrikuliik.maht IS 'mitu testitööd mahub ühte ümbrikusse';
COMMENT ON COLUMN tagastusymbrikuliik.sisukohta IS 'mille kohta ümbrik teha: 1 - testiprotokollirühma kohta; 2 - sama ruumi kahe testiprotokollirühma kohta; 3 - testipaketi kohta';
COMMENT ON COLUMN tagastusymbrikuliik.created IS 'kirje loomise aeg';
COMMENT ON COLUMN tagastusymbrikuliik.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN tagastusymbrikuliik.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN tagastusymbrikuliik.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE tagastusymbrikuliik IS 'Tagastusümbriku liik vastab üldjuhul alatestile
    (st testiprotokollirühmas on iga alatesti ülesannete jaoks oma ümbrik)';

-- eis/model/testimine/skannfail.py
COMMENT ON COLUMN skannfail.id IS 'kirje identifikaator';
COMMENT ON COLUMN skannfail.filename IS 'failinimi';
COMMENT ON COLUMN skannfail.filesize IS 'faili suurus baitides';
COMMENT ON COLUMN skannfail.fileversion IS 'versioon';
COMMENT ON COLUMN skannfail.sooritus_id IS 'viide soorituse kirjele';
COMMENT ON COLUMN skannfail.teatatud IS 'millal saadeti sooritajale e-postiga teade skannitud faili saadvale jõudmise kohta';
COMMENT ON COLUMN skannfail.created IS 'kirje loomise aeg';
COMMENT ON COLUMN skannfail.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN skannfail.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN skannfail.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE skannfail IS 'Skannitud eksamitööde failide viited';

-- eis/model/testimine/toimumisprotokoll.py
COMMENT ON COLUMN toimumisprotokoll.id IS 'kirje identifikaator';
COMMENT ON COLUMN toimumisprotokoll.testimiskord_id IS 'viide testimiskorrale (puudub kutseeksami korral)';
COMMENT ON COLUMN toimumisprotokoll.koht_id IS 'viide kohale';
COMMENT ON COLUMN toimumisprotokoll.testikoht_id IS 'viide testikohale ja toimumisajale (kui toimumise protokoll ei ole toimumisajaga seotud, siis viide esimese testiosa toimumisaja testikohale)';
COMMENT ON COLUMN toimumisprotokoll.testiruum_id IS 'viide testiruumile, kui toimumise protokoll on testiruumiga seotud (SE, TE)';
COMMENT ON COLUMN toimumisprotokoll.lang IS 'soorituskeel (e-testis ja p-testi tulemustega protokollil puudub, sest on ühine kõigi keelte kohta)';
COMMENT ON COLUMN toimumisprotokoll.staatus IS 'testi toimumise protokolli olek: 0=const.B_STAATUS_KEHTETU - kehtetu; 1=const.B_STAATUS_KEHTIV - kehtiv; 2=const.B_STAATUS_KINNITATUD - kinnitatud; 3=const.B_STAATUS_EKK_KINNITATUD - kinnitatud eksamikeskuse poolt';
COMMENT ON COLUMN toimumisprotokoll.markus IS 'märkused';
COMMENT ON COLUMN toimumisprotokoll.filename IS 'failinimi';
COMMENT ON COLUMN toimumisprotokoll.filesize IS 'faili suurus baitides';
COMMENT ON COLUMN toimumisprotokoll.fileversion IS 'versioon';
COMMENT ON COLUMN toimumisprotokoll.kehtivuskinnituseta IS 'kohalikust serverist saadud DDOCi kohta: kas on Sertifitseerimiskeskuse poolt kehtivuskinnitatud või ei ole veel (kohalikus serveris ei ole võimalik kehtivuskinnitusteenust kasutada)';
COMMENT ON COLUMN toimumisprotokoll.edastatud IS 'kohaliku serveri korral: protokolli ja vastuste faili keskserverisse edastamise aeg';
COMMENT ON COLUMN toimumisprotokoll.created IS 'kirje loomise aeg';
COMMENT ON COLUMN toimumisprotokoll.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN toimumisprotokoll.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN toimumisprotokoll.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE toimumisprotokoll IS 'Testi toimumise protokoll.
    Võib olla seotud:
    - testimiskorra ja kohaga (põhikooli eksamid)
    - ühe toimumisaja ühe testikohaga (riigieksamid)
    - testikoha ühe testiruumiga (TE, SE)
    - pedagoogile määratud testi ühe testiruumiga (kutseeksam).';

-- eis/model/testimine/oppekoht.py
COMMENT ON COLUMN oppekoht.id IS 'kirje identifikaator';
COMMENT ON COLUMN oppekoht.sooritaja_id IS 'viide registreeringule';
COMMENT ON COLUMN oppekoht.oppekoht_kood IS 'kus on vene keelt õppinud (kasutusel oli kuni 2017-10)';
COMMENT ON COLUMN oppekoht.oppekohtet_kood IS 'kus on eesti keelt õppinud';
COMMENT ON COLUMN oppekoht.oppekoht_muu IS 'keeltekooli nimi või muu õppimiskoht, kus on eesti keelt õppinud';
COMMENT ON COLUMN oppekoht.created IS 'kirje loomise aeg';
COMMENT ON COLUMN oppekoht.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN oppekoht.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN oppekoht.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE oppekoht IS 'Sooritaja eesti keele õppimise koht (tasemeeksami korral) või vene keele õppimise koht (vene keele rahvusvahelise eksami korral)';

-- eis/model/testimine/hindamisprotokoll.py
COMMENT ON COLUMN hindamisprotokoll.id IS 'kirje identifikaator';
COMMENT ON COLUMN hindamisprotokoll.liik IS 'hindamise liik (kui hindamisprotokoll on olemas, siis sama, mis hindamisprotokollis): 1=const.HINDAJA - I hindamine; 2=const.HINDAJA2 - II hindamine ; 3=const.HINDAJA3 - III hindamine; 4=const.HINDAJA4 - eksperthindamine';
COMMENT ON COLUMN hindamisprotokoll.sisestuskogum_id IS 'viide sisestuskogumile';
COMMENT ON COLUMN hindamisprotokoll.testiprotokoll_id IS 'viide testiprotokollile';
COMMENT ON COLUMN hindamisprotokoll.staatus IS 'sisestamise olek: 0=const.H_STAATUS_HINDAMATA - alustamata; 1=const.H_STAATUS_POOLELI - sisestamisel; 2=const.H_STAATUS_LYKATUD - loobutud; 3=const.H_STAATUS_HINNATUD - sisestatud';
COMMENT ON COLUMN hindamisprotokoll.staatus1 IS 'I sisestamise olek: 0=const.H_STAATUS_HINDAMATA - alustamata; 1=const.H_STAATUS_POOLELI - sisestamisel; 2=const.H_STAATUS_LYKATUD - loobutud; 3=const.H_STAATUS_HINNATUD - sisestatud';
COMMENT ON COLUMN hindamisprotokoll.staatus2 IS 'II sisestamise olek: 0=const.H_STAATUS_HINDAMATA - alustamata; 1=const.H_STAATUS_POOLELI - sisestamisel; 2=const.H_STAATUS_LYKATUD - loobutud; 3=const.H_STAATUS_HINNATUD - sisestatud';
COMMENT ON COLUMN hindamisprotokoll.sisestaja2_kasutaja_id IS 'viide II sisestaja kasutajale';
COMMENT ON COLUMN hindamisprotokoll.tehtud_toodearv IS 'tehtud ja valimis olevate hindamiskogumisoorituste arv (arvutatakse protokolli kinnitamisel)';
COMMENT ON COLUMN hindamisprotokoll.created IS 'kirje loomise aeg';
COMMENT ON COLUMN hindamisprotokoll.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN hindamisprotokoll.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN hindamisprotokoll.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE hindamisprotokoll IS 'Hindamisprotokoll ühendab sama liiki hindamise kirjed, 
    mille hinnatavad kuuluvad samasse testiprotokolli ja 
    hindamiskogumid kuuluvad samasse sisestuskogumisse.';

-- eis/model/testimine/testiruum.py
COMMENT ON COLUMN testiruum.id IS 'kirje identifikaator';
COMMENT ON COLUMN testiruum.tahis IS 'testiruumi tähis, unikaalne testikoha piires';
COMMENT ON COLUMN testiruum.markus IS 'märkus';
COMMENT ON COLUMN testiruum.ruum_id IS 'viide ruumile soorituskohas (kui ruum on määramata või ajutine, siis väärtus puudub)';
COMMENT ON COLUMN testiruum.toimumispaev_id IS 'päev, millal toimub';
COMMENT ON COLUMN testiruum.algus IS 'toimumispäeva kuupäev + suulise testi korral soorituskohas valitud kell';
COMMENT ON COLUMN testiruum.alustamise_lopp IS 'kellaaeg, millest varem peab sooritamist alustama (kutseeksami korral, kui aja_jargi_alustatav=True)';
COMMENT ON COLUMN testiruum.lopp IS 'kellaaeg, millal hiljemalt peab sooritamine lõppema (isegi, kui piiraeg ei ole täis)';
COMMENT ON COLUMN testiruum.aja_jargi_alustatav IS 'true - lahendamist võib alustada peale algusaega; false - lahendamist võib alustada siis, kui testi administraator annab sooritajale alustamise loa (testimiskorrata testi korral)';
COMMENT ON COLUMN testiruum.algusaja_kontroll IS 'true - alustamise luba ei võimalda alustada sooritamist enne sooritamise kellaaega; false - alustamise loa olemasolul on võimalik sooritada ka enne alguse kellaaega (testimiskorrata testi korral)';
COMMENT ON COLUMN testiruum.kohti IS 'kohtade arv';
COMMENT ON COLUMN testiruum.testikoht_id IS 'viide testikohale';
COMMENT ON COLUMN testiruum.parool IS 'sooritajate arvutite registreerimise parool';
COMMENT ON COLUMN testiruum.on_arvuti_reg IS 'kas sooritajate arvutite registreerimine on nõutav (kutseeksami korral)';
COMMENT ON COLUMN testiruum.arvuti_reg IS 'sooritajate arvutite registreerimine: 0=const.ARVUTI_REG_POLE - ei ole vajalik; 1=const.ARVUTI_REG_ON - on käimas; 2=const.ARVUTI_REG_LUKUS - on lõppenud';
COMMENT ON COLUMN testiruum.bron_arv IS 'ruumi suunatud või ruumi valinud sooritajate arv, sh pooleli regamised';
COMMENT ON COLUMN testiruum.sooritajate_arv IS 'regatud sooritajate arv ruumis';
COMMENT ON COLUMN testiruum.valimis_arv IS 'valimis olevate regatud sooritajate arv ruumis';
COMMENT ON COLUMN testiruum.nimekiri_id IS 'avaliku vaate testi korral viide nimekirjale';
COMMENT ON COLUMN testiruum.created IS 'kirje loomise aeg';
COMMENT ON COLUMN testiruum.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN testiruum.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN testiruum.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE testiruum IS 'Testi sooritamise ruum';

-- eis/model/testimine/piirkond_kord.py
COMMENT ON TABLE piirkond_kord IS '';

-- eis/model/testimine/testipakett.py
COMMENT ON COLUMN testipakett.id IS 'kirje identifikaator';
COMMENT ON COLUMN testipakett.testikoht_id IS 'viide testikohale';
COMMENT ON COLUMN testipakett.testiruum_id IS 'viide testiruumile, on olemas ainult siis, kui igal testiruumil on oma testipakett ehk SE ja TE liiki testide korral';
COMMENT ON COLUMN testipakett.lang IS 'soorituskeel (klassifikaator SOORKEEL)';
COMMENT ON COLUMN testipakett.toodearv IS 'sooritajate arv (ei arvestata lisatöid)';
COMMENT ON COLUMN testipakett.valjastuskottidearv IS 'väljastuskottide arv';
COMMENT ON COLUMN testipakett.valjastusymbrikearv IS 'testiruumide igat liiki väljastusümbrike arv kokku';
COMMENT ON COLUMN testipakett.tagastuskottidearv IS 'tagastuskottide arv';
COMMENT ON COLUMN testipakett.tagastusymbrikearv IS 'testiruumide igat liiki tagastusümbrike arv kokku';
COMMENT ON COLUMN testipakett.erivajadustoodearv IS 'erivajadustega tööde arv';
COMMENT ON COLUMN testipakett.created IS 'kirje loomise aeg';
COMMENT ON COLUMN testipakett.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN testipakett.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN testipakett.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE testipakett IS 'Testisoorituspakett
    Üldjuhul on iga testikoha ja keele kohta on üks pakett.
    Erandiks on seaduse tundmise eksam ja riigikeele tasemeeksam, 
    kus on iga testiruumi kohta oma pakett.';

-- eis/model/testimine/ylesandehinne.py
COMMENT ON COLUMN ylesandehinne.id IS 'kirje identifikaator';
COMMENT ON COLUMN ylesandehinne.hindamine_id IS 'viide hindamise/sisestamise kirjele';
COMMENT ON COLUMN ylesandehinne.valitudylesanne_id IS 'viide testi valitud ülesandele; mitme sisestamise korral võib sisestusvea korral ajutiselt erineda ylesandevastuses olevast väärtusest';
COMMENT ON COLUMN ylesandehinne.ylesandevastus_id IS 'viide ylesandele antud vastusele ja ylesande hindele';
COMMENT ON COLUMN ylesandehinne.toorpunktid IS 'küsimustele või aspektidele antud toorpunktide summa (ülesande skaala järgi)';
COMMENT ON COLUMN ylesandehinne.pallid IS 'küsimustele või aspektidele antud hindepallide summa (testiülesande skaala järgi)';
COMMENT ON COLUMN ylesandehinne.toorpunktid_kasitsi IS 'küsimustele või aspektidele antud toorpunktide summa ilma arvutihinnatud punktideta (ülesande skaala järgi)';
COMMENT ON COLUMN ylesandehinne.pallid_kasitsi IS 'küsimustele või aspektidele antud hindepallide summa ilma arvutihinnatud pallideta (testiülesande skaala järgi)';
COMMENT ON COLUMN ylesandehinne.nullipohj_kood IS 'null punkti andmise põhjus, klassifikaator NULLIPOHJ (kasutusel siis, kui antakse terve ülesande punktid korraga)';
COMMENT ON COLUMN ylesandehinne.markus IS 'märkused';
COMMENT ON COLUMN ylesandehinne.sisestus IS 'mitmes sisestamine (1 või 2)';
COMMENT ON COLUMN ylesandehinne.sisestatud IS 'kas kõigi küsimuste hinded on sisestatud';
COMMENT ON COLUMN ylesandehinne.on_probleem IS 'kas hindaja on märkinud töö probleemseks (avaliku vaate hindamisel)';
COMMENT ON COLUMN ylesandehinne.probleem_sisu IS 'kui hindaja on märkinud töö probleemseks, siis probleemi sisu';
COMMENT ON COLUMN ylesandehinne.probleem_varv IS 'probleemse töö värv (#rrggbb või #rgb)';
COMMENT ON COLUMN ylesandehinne.created IS 'kirje loomise aeg';
COMMENT ON COLUMN ylesandehinne.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN ylesandehinne.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN ylesandehinne.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE ylesandehinne IS 'Hindaja antud hindepallid ühe ülesande vastusele.';

-- eis/model/testimine/tunnistusekontroll.py
COMMENT ON COLUMN tunnistusekontroll.id IS 'kirje identifikaator';
COMMENT ON COLUMN tunnistusekontroll.tunnistus_id IS 'viide tunnistusele';
COMMENT ON COLUMN tunnistusekontroll.seisuga IS 'viimase kontrollimise aeg';
COMMENT ON COLUMN tunnistusekontroll.korras IS 'kontrolli tulemus: true - korras; false - viga';
COMMENT ON COLUMN tunnistusekontroll.viga IS 'vea korral vea kirjeldus';
COMMENT ON COLUMN tunnistusekontroll.created IS 'kirje loomise aeg';
COMMENT ON COLUMN tunnistusekontroll.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN tunnistusekontroll.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN tunnistusekontroll.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE tunnistusekontroll IS 'Tunnistuse PDFi metaandmete kontroll';

-- eis/model/testimine/integritysig.py
-- eis/model/testimine/valjastusymbrik.py
COMMENT ON COLUMN valjastusymbrik.id IS 'kirje identifikaator';
COMMENT ON COLUMN valjastusymbrik.testipakett_id IS 'viide testipaketile';
COMMENT ON COLUMN valjastusymbrik.kursus_kood IS 'valitud kursus, lai või kitsas (matemaatika korral), klassifikaator KURSUS';
COMMENT ON COLUMN valjastusymbrik.testiruum_id IS 'viide testiruumile, kui ümbrik on ruumikaupa (ümbriku liigis on sisukohta=3)';
COMMENT ON COLUMN valjastusymbrik.valjastusymbrikuliik_id IS 'väljastusümbrikuliik';
COMMENT ON COLUMN valjastusymbrik.toodearv IS 'väljastatavate tööde arv, mis on saadud testiruumi sooritajate arvule lisatööde koefitsienti ja ümarduskordajat rakendades';
COMMENT ON COLUMN valjastusymbrik.ymbrikearv IS 'ümbrike arv, mis on saadud tööde arvu jagamisel ümbriku mahuga';
COMMENT ON COLUMN valjastusymbrik.arvutus IS 'arvutusprotsessi tunnus';
COMMENT ON COLUMN valjastusymbrik.created IS 'kirje loomise aeg';
COMMENT ON COLUMN valjastusymbrik.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN valjastusymbrik.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN valjastusymbrik.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE valjastusymbrik IS 'Testiruumi ja väljastusümbrikuliigiga seotud ümbrike kogus.';

-- eis/model/testimine/testimiskord.py
COMMENT ON COLUMN testimiskord.id IS 'kirje identifikaator';
COMMENT ON COLUMN testimiskord.tahis IS 'tähis';
COMMENT ON COLUMN testimiskord.nimi IS 'nimetus (malli korral)';
COMMENT ON COLUMN testimiskord.aasta IS 'aastaarv, statistika päringute jaoks';
COMMENT ON COLUMN testimiskord.alates IS 'varaseim toimumisaja algus, dubleeritud otsingute optimeerimiseks';
COMMENT ON COLUMN testimiskord.kuni IS 'hiliseim toimumisaja lõpp, dubleeritud otsingute optimeerimiseks';
COMMENT ON COLUMN testimiskord.reg_sooritaja IS 'kas sooritaja võib ise end EISi kasutajaliideses registreerida';
COMMENT ON COLUMN testimiskord.reg_sooritaja_alates IS 'sooritaja poolt EISis ise registreerimise algus';
COMMENT ON COLUMN testimiskord.reg_sooritaja_kuni IS 'sooritaja poolt EISis ise registreerimise lõpp';
COMMENT ON COLUMN testimiskord.reg_xtee IS 'kas sooritaja võib ise end eesti.ee portaali kaudu registreerida';
COMMENT ON COLUMN testimiskord.reg_xtee_alates IS 'sooritaja poolt eesti.ee kaudu ise registreerimise algus';
COMMENT ON COLUMN testimiskord.reg_xtee_kuni IS 'sooritaja poolt eesti.ee kaudu ise registreerimise lõpp';
COMMENT ON COLUMN testimiskord.reg_kool_ehis IS 'kas õppeasutus võib EHISe kaudu sooritajaid registreerida';
COMMENT ON COLUMN testimiskord.reg_kool_eis IS 'kas õppeasutus võib EISi kaudu sooritajaid registreerida';
COMMENT ON COLUMN testimiskord.reg_kool_valitud IS 'kas õppeasutus võib EISi kaudu sooritajaid registreerida (lubatud õppeasutuste loetelu on Innove poolt valitud)';
COMMENT ON COLUMN testimiskord.reg_kool_alates IS 'õppeasutuste poolt registreerimise algus';
COMMENT ON COLUMN testimiskord.reg_kool_kuni IS 'õppeasutuste poolt registreerimise lõpp';
COMMENT ON COLUMN testimiskord.reg_ekk IS 'kas eksamikeskus võib sooritajaid registreerida';
COMMENT ON COLUMN testimiskord.korduv_reg_keelatud IS 'kas on keelatud registreerida isikuid, kes on sama testi mõnele teisele testimiskorrale juba olnud registreeritud';
COMMENT ON COLUMN testimiskord.cae_eeltest IS 'kas registreerimiseks on vajalik CAE eeltesti sooritamine (rahvusvahelisele ingl k eksami korral)';
COMMENT ON COLUMN testimiskord.reg_piirang IS 'registreerimise piirang: H=const.REGPIIRANG_H - haridustöötajad';
COMMENT ON COLUMN testimiskord.erivajadus_alates IS 'õppeasutuste poolt väljaspool registreerimisaega erivajaduste taotluste sisestamise algus';
COMMENT ON COLUMN testimiskord.erivajadus_kuni IS 'õppeasutuste poolt väljaspool registreerimisaega erivajaduste taotluste sisestamise lõpp';
COMMENT ON COLUMN testimiskord.reg_kohavalik IS 'kas registreerimisel on võimalik valida soorituskoht';
COMMENT ON COLUMN testimiskord.reg_voorad IS 'kas kool võib sooritajaks registreerida neid, kes ei ole oma kooli õpilased';
COMMENT ON COLUMN testimiskord.kordusosalemistasu IS 'kordusosalemistasu';
COMMENT ON COLUMN testimiskord.osalemistasu IS 'osalemistasu';
COMMENT ON COLUMN testimiskord.sooritajad_peidus_kuni IS 'aeg, enne mida koolid ei näe sooritajate identiteete (kui puudub, siis näevad)';
COMMENT ON COLUMN testimiskord.korraldamata_teated IS 'kas saata koolile automaatseid korraldamise meeldetuletusi';
COMMENT ON COLUMN testimiskord.arvutada_hiljem IS 'kas tulemuse arvutamine peale testi sooritamist ära jätta (jõudluse huvides)';
COMMENT ON COLUMN testimiskord.tulemus_kinnitatud IS 'kas tulemused on kinnitatud';
COMMENT ON COLUMN testimiskord.tulemus_kontrollitud IS 'kas tulemused on kontrollitud; kui on kontrollitud, siis saab ainult administraator tulemusi ja statistikat arvutada, ainespetsialist ei saa';
COMMENT ON COLUMN testimiskord.statistika_arvutatud IS 'kas tulemuste statistika on arvutatud';
COMMENT ON COLUMN testimiskord.osalemise_naitamine IS 'kas näidata sooritamist lahendajale oma tulemuste all sooritatud testide loetelus (nt eeltestidel osalemist ei soovita näidata)';
COMMENT ON COLUMN testimiskord.prot_vorm IS 'toimumise protokolli vorm: 0=const.PROT_VORM_VAIKIMISI- vaikimisi; 1=const.PROT_VORM_DOKNR - protokoll dok numbritega; 2=const.PROT_VORM_TULEMUS - protokoll tulemusega; 3=const.PROT_VORM_YLTULEMUS - protokoll ülesannete tulemustega; 5=const.PROT_VORM_ALATULEMUS - protokoll alatestide tulemustega';
COMMENT ON COLUMN testimiskord.on_helifailid IS 'kas toimumise protokolli sisestamisel on helifailide laadimise sakk';
COMMENT ON COLUMN testimiskord.on_turvakotid IS 'kas toimumise protokolli sisestamisel avalikus vaates on helifailide laadimise sakk';
COMMENT ON COLUMN testimiskord.analyys_eraldi IS 'kas vastuste analüüs toimub testimiskorra kaupa (või kogu testi kaupa)';
COMMENT ON COLUMN testimiskord.tulemus_koolile IS 'kas kool saab tulemusi vaadata';
COMMENT ON COLUMN testimiskord.tulemus_admin IS 'kas testi administraator saab hiljem oma läbiviidud testis oma kooli õpilaste tulemusi vaadata';
COMMENT ON COLUMN testimiskord.koondtulemus_avaldet IS 'kas koondtulemus on avaldatud';
COMMENT ON COLUMN testimiskord.koondtulemus_aval_kpv IS 'koondtulemuse avaldamise kuupäev';
COMMENT ON COLUMN testimiskord.alatestitulemused_avaldet IS 'kas alatestide tulemused on avaldatud';
COMMENT ON COLUMN testimiskord.alatestitulemused_aval_kpv IS 'alatestide tulemuste avaldamise kuupäev';
COMMENT ON COLUMN testimiskord.ylesandetulemused_avaldet IS 'kas ülesannete tulemused on avaldatud';
COMMENT ON COLUMN testimiskord.ylesandetulemused_aval_kpv IS 'ülesannete tulemuste avaldamise kuupäev';
COMMENT ON COLUMN testimiskord.aspektitulemused_avaldet IS 'kas aspektide tulemused on avaldatud';
COMMENT ON COLUMN testimiskord.aspektitulemused_aval_kpv IS 'aspektide tulemuste avaldamise kuupäev';
COMMENT ON COLUMN testimiskord.ylesanded_avaldet IS 'kas ülesanded ja vastused on avaldatud';
COMMENT ON COLUMN testimiskord.ylesanded_aval_kpv IS 'ülesannete avaldamise kuupäev';
COMMENT ON COLUMN testimiskord.statistika_aval_kpv IS 'eksamistatistika avaldamise kuupäev';
COMMENT ON COLUMN testimiskord.statistika_ekk_kpv IS 'kuupäev, millest alates on eksamistatistika Innove vaates (enne avaldamist üle vaatamiseks)';
COMMENT ON COLUMN testimiskord.testsessioon_id IS 'viide testsessioonile';
COMMENT ON COLUMN testimiskord.test_id IS 'viide testile';
COMMENT ON COLUMN testimiskord.vaide_algus IS 'vaiete esitamise ajavahemiku algus (kui puudub, siis saab vaidlustada kohe peale tulemuste kinnitamist)';
COMMENT ON COLUMN testimiskord.vaide_tahtaeg IS 'vaiete esitamise ajavahemiku lõpp (kui puudub, siis ei saa üldse vaidlustada)';
COMMENT ON COLUMN testimiskord.on_avalik_vaie IS 'kas sooritaja saab vaiete esitamise ajavahemikul ise avalikus vaates vaide esitada (false - vaideid saab ainult Innove vaates sisestada, vajalik tasemeeksamitel)';
COMMENT ON COLUMN testimiskord.kool_testikohaks IS 'kas sooritajate õppeasutustest teha automaatselt testikohad';
COMMENT ON COLUMN testimiskord.sisestus_isikukoodiga IS 'kas on võimalik töid ja hindamisprotokolle sisestada isikukoodi järgi';
COMMENT ON COLUMN testimiskord.skeeled IS 'testimiskorra keelte koodid eraldatuna tühikuga';
COMMENT ON COLUMN testimiskord.on_mall IS 'kas testimiskorra andmeid kasutatakse korraldamise mallina teiste testimiskordade loomiseks';
COMMENT ON COLUMN testimiskord.sisaldab_valimit IS 'kas valim on eraldatud testimiskorra siseselt (ilma valimi jaoks eraldi testimiskorda loomata)';
COMMENT ON COLUMN testimiskord.valim_testimiskord_id IS 'valimi korral viide testimiskorrale, millest valim eraldati ja millelt saab tulemuste arvutamisel lõpptulemusi kopeerida';
COMMENT ON COLUMN testimiskord.stat_valim IS 'kas on statistikas arvestatav valim (valimi korral); õpilaste tulemuste tabelis (gtbl) kuvatakse konkreetse õpilase tulemuste erinevusi ka nende valimitega, kus stat_valim=False';
COMMENT ON COLUMN testimiskord.tutv_taotlus_alates IS 'testitööga tutvumise taotlemise esitamise ajavahemiku alguskuupäev';
COMMENT ON COLUMN testimiskord.tutv_taotlus_kuni IS 'testitööga tutvumise taotlemise esitamise ajavahemiku lõppkuupäev';
COMMENT ON COLUMN testimiskord.tutv_hindamisjuhend_url IS 'hindamisjuhendi URL, lisatakse teatele, mis saadetakse sooritajale, kui tema töö on skannitud';
COMMENT ON COLUMN testimiskord.markus IS 'selgitus selle kohta, mille jaoks testimiskorda kasutatakse';
COMMENT ON COLUMN testimiskord.created IS 'kirje loomise aeg';
COMMENT ON COLUMN testimiskord.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN testimiskord.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN testimiskord.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE testimiskord IS 'Testimiskord (ühel testil võib olla mitu testimiskorda)';

-- eis/model/testimine/turvakott.py
COMMENT ON COLUMN turvakott.id IS 'kirje identifikaator';
COMMENT ON COLUMN turvakott.kotinr IS 'koti nr';
COMMENT ON COLUMN turvakott.testipakett_id IS 'viide testipaketile';
COMMENT ON COLUMN turvakott.suund IS 'suund: 1=const.SUUND_VALJA - väljastuskott; 2=const.SUUND_TAGASI - tagastuskott';
COMMENT ON COLUMN turvakott.staatus IS 'olek, M_STAATUS';
COMMENT ON COLUMN turvakott.created IS 'kirje loomise aeg';
COMMENT ON COLUMN turvakott.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN turvakott.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN turvakott.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE turvakott IS 'Materjalide eksamikeskusest väljastamise või 
    eksamikeskusse tagastamise turvakott';

-- eis/model/testimine/vaideallkiri.py
COMMENT ON COLUMN vaideallkiri.id IS 'kirje identifikaator';
COMMENT ON COLUMN vaideallkiri.kasutaja_id IS 'allkirjastaja';
COMMENT ON COLUMN vaideallkiri.jrk IS 'allkirjastamise jrk nr (kasutajarollist)';
COMMENT ON COLUMN vaideallkiri.allkirjastatud IS 'allkirjastamise aeg (kui puudub, siis ei ole veel allkirjastatud)';
COMMENT ON COLUMN vaideallkiri.created IS 'kirje loomise aeg';
COMMENT ON COLUMN vaideallkiri.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN vaideallkiri.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN vaideallkiri.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE vaideallkiri IS 'Vaideotsuse allkirjastajad, lisatakse kasutajarollide järgi otsuse genereerimisel.
    Hiljem, kui allkiri antakse, tehakse kirjes vastav märge.';

-- eis/model/testimine/regkoht_kord.py
COMMENT ON TABLE regkoht_kord IS '';

-- eis/model/testimine/testiparoolilogi.py
COMMENT ON COLUMN testiparoolilogi.id IS 'kirje identifikaator';
COMMENT ON COLUMN testiparoolilogi.sooritaja_id IS 'viide testisooritusele';
COMMENT ON COLUMN testiparoolilogi.testiparool IS 'testiparooli räsi';
COMMENT ON COLUMN testiparoolilogi.created IS 'kirje loomise aeg';
COMMENT ON COLUMN testiparoolilogi.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN testiparoolilogi.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN testiparoolilogi.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE testiparoolilogi IS 'Testiparoolide andmise logi';

-- eis/model/testimine/testiopetaja.py
COMMENT ON COLUMN testiopetaja.id IS 'kirje identifikaator';
COMMENT ON COLUMN testiopetaja.sooritaja_id IS 'viide sooritajale (testisoorituse kirjele)';
COMMENT ON COLUMN testiopetaja.opetaja_kasutaja_id IS 'viide aineõpetajale';
COMMENT ON COLUMN testiopetaja.created IS 'kirje loomise aeg';
COMMENT ON COLUMN testiopetaja.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN testiopetaja.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN testiopetaja.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE testiopetaja IS 'Test.sooritaja seos aineõpetajatega, kes sooritajale antud testi ainet õpetavad';

-- eis/model/testimine/ainepdf.py
COMMENT ON COLUMN ainepdf.id IS 'kirje identifikaator';
COMMENT ON COLUMN ainepdf.aine_kood IS 'ainete klassifikaator';
COMMENT ON COLUMN ainepdf.tyyp IS 'PDF malli tyyp (faili nimi on kujul TYYP_NIMI.py)';
COMMENT ON COLUMN ainepdf.nimi IS 'PDF malli nimi (faili nimi on kujul TYYP_NIMI.py)';
COMMENT ON COLUMN ainepdf.created IS 'kirje loomise aeg';
COMMENT ON COLUMN ainepdf.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN ainepdf.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN ainepdf.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE ainepdf IS 'Ainete seosed eksamikorralduse materjalide väljatrükkimise PDF mallidega';

-- eis/model/testimine/statvastus_t.py
COMMENT ON COLUMN statvastus_t.id IS 'kirje identifikaator';
COMMENT ON COLUMN statvastus_t.statvastus_t_seis_id IS 'arvutusprotsessi ID, millega andmed on leitud';
COMMENT ON COLUMN statvastus_t.kood1 IS 'küsimuse kood, eripaari korral koos kooloni ja esimese valiku koodiga';
COMMENT ON COLUMN statvastus_t.selgitus1 IS 'küsimuse selgitus või eripaari esimese valiku selgitus';
COMMENT ON COLUMN statvastus_t.kysimus_seq IS 'küsimuse jrk';
COMMENT ON COLUMN statvastus_t.valik1_seq IS 'eripaari korral esimese valiku jrk';
COMMENT ON COLUMN statvastus_t.ks_punktid IS 'antud vastuse punktid; vastamata jätmisel alati 0';
COMMENT ON COLUMN statvastus_t.svpunktid IS 'eripaari korral eripaari punktid, muidu küsimuse punktid';
COMMENT ON COLUMN statvastus_t.kv_punktid IS 'küsimuse punktid';
COMMENT ON COLUMN statvastus_t.max_punktid IS 'eripaari korral eripaari max toorpunktid, muidu küsimuse toorpunktid';
COMMENT ON COLUMN statvastus_t.oige IS 'vastuse õigsus (1 - õige; 0,5 - osaliselt õige, 0 - vale või loetamatu või vastamata)';
COMMENT ON COLUMN statvastus_t.vastus IS 'vastus või eripaari teise valiku kood';
COMMENT ON COLUMN statvastus_t.selgitus IS 'vastuse selgitus';
COMMENT ON COLUMN statvastus_t.kvsisu_seq IS 'vastuse jrk nr';
COMMENT ON COLUMN statvastus_t.kvsisu_id IS 'viide vastuse sisu kirjele';
COMMENT ON COLUMN statvastus_t.kysimus_id IS 'viide küsimuse kirjele';
COMMENT ON COLUMN statvastus_t.kysimusevastus_id IS 'viide küsimusevastuse kirjele';
COMMENT ON COLUMN statvastus_t.ylesandevastus_id IS 'viide ülesandevastuse kirjele';
COMMENT ON COLUMN statvastus_t.max_vastus IS 'kood1 max vastuste arv';
COMMENT ON COLUMN statvastus_t.staatus IS 'soorituse staatus';
COMMENT ON TABLE statvastus_t IS 'Küsimuste vastused Exceli väljavõtte kiirendamiseks.
    Uuendatakse vaate statvastus põhjal testi või toimumisaja kaupa siis,
    kui tulemusi arvutatakse';

COMMENT ON COLUMN statvastus_t_seis.id IS 'kirje identifikaator';
COMMENT ON COLUMN statvastus_t_seis.testiosa_id IS 'viide testiosale, mille andmed uuendati';
COMMENT ON COLUMN statvastus_t_seis.toimumisaeg_id IS 'viide toimumisajale, mille andmed uuendati';
COMMENT ON COLUMN statvastus_t_seis.seisuga IS 'andmete uuendamise aeg';
COMMENT ON COLUMN statvastus_t_seis.protsess_id IS 'arvutusprotsessi ID, millega andmed uuendati';
COMMENT ON COLUMN statvastus_t_seis.created IS 'kirje loomise aeg';
COMMENT ON COLUMN statvastus_t_seis.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN statvastus_t_seis.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN statvastus_t_seis.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE statvastus_t_seis IS 'Tabeli statvastus_t uuendamise andmed';

-- eis/model/testimine/kysimusestatistika.py
COMMENT ON COLUMN kysimusestatistika.id IS 'kirje identifikaator';
COMMENT ON COLUMN kysimusestatistika.testiosa_id IS 'viide testiosale';
COMMENT ON COLUMN kysimusestatistika.tkorraga IS 'kas on testimiskorraga soorituste statistika (või avaliku testi statistika)';
COMMENT ON COLUMN kysimusestatistika.valimis IS 'NULL - valimi ja mitte-valimi statistika koos; true - valimi statistika; false - mitte-valimi statistika';
COMMENT ON COLUMN kysimusestatistika.toimumisaeg_id IS 'viide toimumisajale eksamikeskuse testi korral';
COMMENT ON COLUMN kysimusestatistika.nimekiri_id IS 'viide testi sooritajate nimekirjale oma nimekirja sisese statistika korral';
COMMENT ON COLUMN kysimusestatistika.valitudylesanne_id IS 'viide komplekti valitud ülesandele, kui statistika on komplektisisene';
COMMENT ON COLUMN kysimusestatistika.kysimus_id IS 'viide kysimusele';
COMMENT ON COLUMN kysimusestatistika.vastuste_arv IS 'vastuste arv (tabeli Kvsisu kirjete arv) - mõne küsimuse korral võib üks vastaja anda mitu vastust, kasutusel tabeli Kvstatistika kirjete sageduse arvutamiseks';
COMMENT ON COLUMN kysimusestatistika.vastajate_arv IS 'vastajate arv (tabeli Kysimusevastus kirjete arv), kasutusel tabeli Khstatistika kirjete sageduse arvutamiseks';
COMMENT ON COLUMN kysimusestatistika.test_hinnatud_arv IS 'vastajate arv, kelle kogu testitöö on hinnatud';
COMMENT ON COLUMN kysimusestatistika.klahendusprotsent IS 'keskmine lahendusprotsent, keskmise tulemuse ja maksimaalse võimaliku tulemuse suhe';
COMMENT ON COLUMN kysimusestatistika.rit IS 'korrelatsioonikordaja küsimuse punktide ja testi kogutulemuse vahel, küsimuse eristusjõu näitaja: corr(kv.pallid, sooritaja.pallid)';
COMMENT ON COLUMN kysimusestatistika.rir IS 'korrelatsioonikordaja küsimuse punktide ja testi ülejäänud küsimuste punktide vahel: corr(kv.pallid, sooritaja.pallid-kv.pallid)';
COMMENT ON COLUMN kysimusestatistika.created IS 'kirje loomise aeg';
COMMENT ON COLUMN kysimusestatistika.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN kysimusestatistika.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN kysimusestatistika.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE kysimusestatistika IS 'Küsimuse statistika';

-- eis/model/testimine/kriteeriumivastus.py
COMMENT ON COLUMN kriteeriumivastus.id IS 'kirje identifikaator';
COMMENT ON COLUMN kriteeriumivastus.sooritus_id IS 'viide sooritusele';
COMMENT ON COLUMN kriteeriumivastus.hindamiskriteerium_id IS 'viide hindamiskriteeriumile';
COMMENT ON COLUMN kriteeriumivastus.toorpunktid IS 'toorpunktid (hindamiskriteeriumi skaala järgi)';
COMMENT ON COLUMN kriteeriumivastus.pallid IS 'hindepallid (peale kaaluga korrutamist)';
COMMENT ON COLUMN kriteeriumivastus.toorpunktid_enne_vaiet IS 'toorpunktid enne vaidlustamist';
COMMENT ON COLUMN kriteeriumivastus.pallid_enne_vaiet IS 'hindepallid enne vaidlustamist';
COMMENT ON COLUMN kriteeriumivastus.created IS 'kirje loomise aeg';
COMMENT ON COLUMN kriteeriumivastus.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN kriteeriumivastus.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN kriteeriumivastus.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE kriteeriumivastus IS 'Sooritusele hindamiskriteeriumi eest antud pallid
    Erinevalt tabelis Kriteeriumihinne olevatest ühe hindaja pandud hinnetest
    on siin lõplikud hinded.';

-- eis/model/testimine/vaidelogi.py
COMMENT ON COLUMN vaidelogi.id IS 'kirje identifikaator';
COMMENT ON COLUMN vaidelogi.tegevus IS 'tegevus: 0 - menetlusse võtmine; 1 - tulemuse arvutamine; 2 - otsuse loomine; 3 - allkirjastamine; 4 - edastamine; 5 - lõpetatuks märkimine; 11 - otsuse eelnõu loomine; 12 - otsuse eelnõu edastamine; 13 - otsustamisele võtmine; 14 - vaide tagasi võtmine';
COMMENT ON COLUMN vaidelogi.tapsustus IS 'tegevuse täpsustus';
COMMENT ON COLUMN vaidelogi.created IS 'kirje loomise aeg';
COMMENT ON COLUMN vaidelogi.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN vaidelogi.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN vaidelogi.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE vaidelogi IS 'Vaide menetlemise logi';

-- eis/model/testimine/toimumisaeg_komplekt.py
COMMENT ON TABLE toimumisaeg_komplekt IS '';

-- eis/model/testimine/tagastusymbrikuliik_hk.py
COMMENT ON TABLE tagastusymbrikuliik_hk IS '';

-- eis/model/testimine/npstatistika.py
COMMENT ON COLUMN npstatistika.id IS 'kirje identifikaator';
COMMENT ON COLUMN npstatistika.statistika_id IS 'viide statistika kirjele';
COMMENT ON COLUMN npstatistika.normipunkt_id IS 'viide normipunkti kirjele';
COMMENT ON COLUMN npstatistika.vastuste_arv IS 'selle vastusega sooritajate arv';
COMMENT ON COLUMN npstatistika.nvaartus IS 'arvuline väärtus (kui on arv)';
COMMENT ON COLUMN npstatistika.svaartus IS 'tekstiline väärtus (kui pole arv)';
COMMENT ON COLUMN npstatistika.created IS 'kirje loomise aeg';
COMMENT ON COLUMN npstatistika.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN npstatistika.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN npstatistika.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE npstatistika IS 'Normipunktide vastuste statistika';

-- eis/model/testimine/labiviija.py
COMMENT ON COLUMN labiviija.id IS 'kirje identifikaator';
COMMENT ON COLUMN labiviija.tahis IS 'hindaja tähis, kopeerib välja Ainelabiviija.tahis';
COMMENT ON COLUMN labiviija.staatus IS 'olek, 0=const.L_STAATUS_KEHTETU - kehtetu; 1=const.L_STAATUS_MAARATUD - määramata või määratud; 3=const.L_STAATUS_OSALENUD - osalenud; 4=const.L_STAATUS_PUUDUNUD - puudunud';
COMMENT ON COLUMN labiviija.kasutaja_id IS 'viide läbiviija kasutajale';
COMMENT ON COLUMN labiviija.kasutajagrupp_id IS 'kasutajagrupp, mis näitab läbiviija õigused';
COMMENT ON COLUMN labiviija.liik IS 'hindaja liik: 1=const.HINDAJA1 - hindaja I; 2=const.HINDAJA2 - hindaja II; 3=const.HINDAJA3 - hindaja III';
COMMENT ON COLUMN labiviija.lang IS 'hindamise keel';
COMMENT ON COLUMN labiviija.hindamiskogum_id IS 'viide hinnatavale hindamiskogumile, hindaja korral kohustuslik';
COMMENT ON COLUMN labiviija.hindaja1_id IS 'paaris hindamise korral viide I hindaja kirjele; hindaja-intervjueerija korral viide intervjueerija kirjele';
COMMENT ON COLUMN labiviija.on_paaris IS 'kas on paarishindaja';
COMMENT ON COLUMN labiviija.planeeritud_toode_arv IS 'hindajale planeeritud hinnatavate tööde arv';
COMMENT ON COLUMN labiviija.toode_arv IS 'määratud või ette võetud tööde arv (hinnatud tööd ja pooleli tööd)';
COMMENT ON COLUMN labiviija.hinnatud_toode_arv IS 'hinnatud (hindamine kinnitatud) tööde arv (hindaja korral); intervjueeritud tööde arv, kus intervjueerija oli ise hindaja (hindaja-intervjueerija korral); intervjueeritud tööde arv, kus intervjueerija polnud hindaja (intervjueerija korral)';
COMMENT ON COLUMN labiviija.tasu_toode_arv IS 'tasustatud tööde arv - hinnatud tööde arv ilma oma kooli õpilasteta (hindaja korral); intervjueeritud tööde arv, kus intervjueerija oli ise hindaja (hindaja-intervjueerija korral); intervjueeritud tööde arv, kus intervjueerija polnud hindaja (intervjueerija korral)';
COMMENT ON COLUMN labiviija.tasustatav IS 'kas töötasu arvestatakse (kui läbiviija osaleb samal kuupäeval mitmes testis ja kõigi eest ei soovita talle maksta, siis märgitakse siia, et pole tasustatav)';
COMMENT ON COLUMN labiviija.tasu IS 'läbiviija töötasu';
COMMENT ON COLUMN labiviija.meeldetuletusaeg IS 'meeldetuletuse aeg';
COMMENT ON COLUMN labiviija.teateaeg IS 'teate aeg';
COMMENT ON COLUMN labiviija.yleaja IS 'kas tööaeg läks üle aja';
COMMENT ON COLUMN labiviija.toolopp IS 'töö lõpetamise kellaaeg (kui läks üle aja)';
COMMENT ON COLUMN labiviija.testikoht_id IS 'viide testikohale (kohustuslik kõigile peale kirjaliku hindaja)';
COMMENT ON COLUMN labiviija.testiruum_id IS 'viide testiruumile (kohustuslik kõigile peale kirjaliku hindaja)';
COMMENT ON COLUMN labiviija.aktiivne IS 'kas läbiviija on parajasti aktiivne (ekspertrühma liige ei pruugi kogu aeg aktiivne olla)';
COMMENT ON COLUMN labiviija.valimis IS 'kas on valimi hindaja';
COMMENT ON COLUMN labiviija.muu_koha_hindamine IS 'soorituskohas määratud hindaja korral: false - hindab oma soorituskoha töid; true - hindab teiste soorituskohtade töid';
COMMENT ON COLUMN labiviija.created IS 'kirje loomise aeg';
COMMENT ON COLUMN labiviija.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN labiviija.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN labiviija.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE labiviija IS 'Testi läbiviijad.';

-- eis/model/testimine/nimekiri.py
COMMENT ON COLUMN nimekiri.id IS 'kirje identifikaator';
COMMENT ON COLUMN nimekiri.nimi IS 'nimekirja nimetus';
COMMENT ON COLUMN nimekiri.esitaja_kasutaja_id IS 'nimekirja esitaja';
COMMENT ON COLUMN nimekiri.esitaja_koht_id IS 'õppeasutus, nimekirja esitaja';
COMMENT ON COLUMN nimekiri.test_id IS 'viide testile, millele registreeritakse (kui on ühe testi jaoks koostatud nimekiri)';
COMMENT ON COLUMN nimekiri.testimiskord_id IS 'viide testimiskorrale, millele registreeritakse (kui on ühe testimiskorra jaoks koostatud nimekiri)';
COMMENT ON COLUMN nimekiri.staatus IS 'olek';
COMMENT ON COLUMN nimekiri.alates IS 'varaseim lahendamise kuupäev (jagatud töö korral ja kutseeksami korral)';
COMMENT ON COLUMN nimekiri.kuni IS 'hiliseim lahendamise kuupäev (jagatud töö korral)';
COMMENT ON COLUMN nimekiri.pedag_nahtav IS 'kas nimekiri on nähtav teistele sama kooli õpetajatele';
COMMENT ON COLUMN nimekiri.tulemus_nahtav IS 'kas oma tulemus on sooritajale nähtav (kutseeksami korral koondtulemus)';
COMMENT ON COLUMN nimekiri.alatestitulemus_nahtav IS 'kas oma alatestide tulemused on sooritajale nähtavad (kutseeksami korral)';
COMMENT ON COLUMN nimekiri.vastus_peidus IS 'kas oma tehtud töö on sooritajale mittenähtav (kutseeksami korral)';
COMMENT ON COLUMN nimekiri.stat_arvutatud IS 'millal on arvutatud viimati nimekirja statistika';
COMMENT ON COLUMN nimekiri.created IS 'kirje loomise aeg';
COMMENT ON COLUMN nimekiri.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN nimekiri.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN nimekiri.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE nimekiri IS 'Testile registreeritute nimekiri.
    Kui õpetaja kasutab sama avaliku vaate testi mitmes klassis, 
    siis ta teeb iga klassi jaoks oma nimekirja.
    Avaliku vaate testidel testimiskord puudub.';

-- eis/model/testimine/labiviijaylesanne.py
COMMENT ON COLUMN labiviijaylesanne.id IS 'kirje identifikaator';
COMMENT ON COLUMN labiviijaylesanne.labiviija_id IS 'viide hindaja kirjele';
COMMENT ON COLUMN labiviijaylesanne.created IS 'kirje loomise aeg';
COMMENT ON COLUMN labiviijaylesanne.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN labiviijaylesanne.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN labiviijaylesanne.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE labiviijaylesanne IS 'Testimiskorrata testile määratud hindaja korral valitud ülesanded, mida hindaja võib hinnata';

-- eis/model/testimine/labivaatus.py
COMMENT ON COLUMN labivaatus.id IS 'kirje identifikaator';
COMMENT ON COLUMN labivaatus.hindamine_id IS 'viide hindamise kirjele';
COMMENT ON COLUMN labivaatus.ekspert_labiviija_id IS 'viide vaidehindajale';
COMMENT ON COLUMN labivaatus.markus IS 'märkused';
COMMENT ON COLUMN labivaatus.staatus IS 'olek: 0 - läbi vaatamata; 1 - läbi vaadatud';
COMMENT ON COLUMN labivaatus.created IS 'kirje loomise aeg';
COMMENT ON COLUMN labivaatus.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN labivaatus.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN labivaatus.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE labivaatus IS 'Eksperthindaja poolne hindamise läbivaatus (vaide korral rühmaga hindamisel).';

-- eis/model/testimine/toovaataja.py
COMMENT ON COLUMN toovaataja.id IS 'kirje identifikaator';
COMMENT ON COLUMN toovaataja.sooritaja_id IS 'viide testitööle, mille vaatamiseks on õigus';
COMMENT ON COLUMN toovaataja.kasutaja_id IS 'viide kasutajale, kellel on õigus testitööd vaadata';
COMMENT ON COLUMN toovaataja.kehtib_kuni IS 'õiguse kehtimise lõpp';
COMMENT ON COLUMN toovaataja.created IS 'kirje loomise aeg';
COMMENT ON COLUMN toovaataja.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN toovaataja.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN toovaataja.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE toovaataja IS 'Testitöö vaatamise õigus
    (kasutusel gümnaasiumite sisseastumistestides, kui.sooritaja vaidlustab oma tulemuse
    ning kooli töötajale antakse õigus tema testitööd vaadata)';

-- eis/model/testimine/kysimusehinne.py
COMMENT ON COLUMN kysimusehinne.id IS 'kirje identifikaator';
COMMENT ON COLUMN kysimusehinne.ylesandehinne_id IS 'viide ylesande hinde kirjele';
COMMENT ON COLUMN kysimusehinne.kysimusevastus_id IS 'viide hinnatavale vastusele';
COMMENT ON COLUMN kysimusehinne.toorpunktid IS 'hindaja antud toorpunktid (ülesande skaala järgi)';
COMMENT ON COLUMN kysimusehinne.pallid IS 'hindepallid (testiülesande skaala järgi)';
COMMENT ON COLUMN kysimusehinne.markus IS 'märkused';
COMMENT ON COLUMN kysimusehinne.nullipohj_kood IS 'null punkti andmise põhjus, klassifikaator NULLIPOHJ';
COMMENT ON COLUMN kysimusehinne.created IS 'kirje loomise aeg';
COMMENT ON COLUMN kysimusehinne.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN kysimusehinne.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN kysimusehinne.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE kysimusehinne IS 'Hindaja antud hinne ülesande ühele küsimusele.';

-- eis/model/testimine/sisestusolek.py
COMMENT ON COLUMN sisestusolek.id IS 'kirje identifikaator';
COMMENT ON COLUMN sisestusolek.sooritus_id IS 'viide hinnatavale sooritusele';
COMMENT ON COLUMN sisestusolek.staatus IS 'sisestamise olek: 0=const.H_STAATUS_HINDAMATA - alustamata; 1=const.H_STAATUS_POOLELI - sisestamisel; 2=const.H_STAATUS_LYKATUD - loobutud; 6=const.H_STAATUS_HINNATUD - sisestatud';
COMMENT ON COLUMN sisestusolek.sisestuskogum_id IS 'viide sisestuskogumile';
COMMENT ON COLUMN sisestusolek.staatus1 IS 'I sisestamise olek: 0=const.H_STAATUS_HINDAMATA - alustamata; 1=const.H_STAATUS_POOLELI - sisestamisel; 2=const.H_STAATUS_LYKATUD - loobutud; 6=const.H_STAATUS_HINNATUD - sisestatud';
COMMENT ON COLUMN sisestusolek.sisestaja1_kasutaja_id IS 'viide I sisestaja kasutajale';
COMMENT ON COLUMN sisestusolek.sisestaja1_algus IS 'esimese sisestamise algus, vajalik hiljem tunnis sisestamiste arvu väljavõtte jaoks';
COMMENT ON COLUMN sisestusolek.staatus2 IS 'II sisestamise olek: 0=const.H_STAATUS_HINDAMATA - alustamata; 1=const.H_STAATUS_POOLELI - sisestamisel; 2=const.H_STAATUS_LYKATUD - loobutud; 6=const.H_STAATUS_HINNATUD - sisestatud';
COMMENT ON COLUMN sisestusolek.sisestaja2_kasutaja_id IS 'viide II sisestaja kasutajale';
COMMENT ON COLUMN sisestusolek.sisestaja2_algus IS 'teise sisestamise algus, vajalik hiljem tunnis sisestamiste arvu väljavõtte jaoks';
COMMENT ON COLUMN sisestusolek.skann IS 'skannitud testitöö PDF-failina';
COMMENT ON COLUMN sisestusolek.liik IS 'hindamisprotokolli liik: 1=const.HINDAJA - I hindamine; 2=const.HINDAJA2 - II hindamine ; 3=const.HINDAJA3 - III hindamine; 4=const.HINDAJA4 - eksperthindamine; 0=const.VASTUSTESISESTUS - vastuste sisestamine';
COMMENT ON COLUMN sisestusolek.pallid IS 'soorituse pallid antud sisestuskogumi eest';
COMMENT ON COLUMN sisestusolek.toorpunktid IS 'soorituse toorpunktide summa antud sisestuskogumi eest';
COMMENT ON COLUMN sisestusolek.created IS 'kirje loomise aeg';
COMMENT ON COLUMN sisestusolek.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN sisestusolek.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN sisestusolek.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE sisestusolek IS 'Soorituse sisestamise kehtiv olek sisestuskogumite ja sisestuste lõikes.
    Sisestatakse vastuseid või hindamisprotokolle.
    Vastuste sisestamisel (liik=NULL) toimub selle tabeli põhjal arvestus,
    millises olekus on soorituse sisestuskogumi sisestamine
    (mis on veel sisestamata ja kes saab sisestada).
    Hindamisprotokollide sisestamisel toimub arvestus hindamisprotokolli kirje põhjal ja
    sisestusoleku kirje on vajalik ainult hiljem sisestajate töömahu kokku arvutamiseks.
    Selle tabeli põhjal toimib läbiviijate aruande sisestajate osa.';

-- eis/model/testimine/erikomplekt.py
COMMENT ON COLUMN erikomplekt.id IS 'kirje identifikaator';
COMMENT ON COLUMN erikomplekt.sooritus_id IS 'viide sooritusele (millega on määratud.sooritaja ja testiosa toimumisaeg, foreign_keys=sooritus_id)';
COMMENT ON COLUMN erikomplekt.komplekt_id IS 'viide komplektile';
COMMENT ON COLUMN erikomplekt.created IS 'kirje loomise aeg';
COMMENT ON COLUMN erikomplekt.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN erikomplekt.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN erikomplekt.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE erikomplekt IS 'Komplekti seos erivajadustega sooritustega,
    mis näitab, milliste sooritajate jaoks komplekt on mõeldud';

-- eis/model/testimine/kandideerimiskoht.py
COMMENT ON COLUMN kandideerimiskoht.id IS 'kirje identifikaator';
COMMENT ON COLUMN kandideerimiskoht.sooritaja_id IS 'viide registreeringule';
COMMENT ON COLUMN kandideerimiskoht.koht_id IS 'viide koolile';
COMMENT ON COLUMN kandideerimiskoht.automaatne IS 'true - valitud seetõttu, et on.sooritaja õppimiskoht, aga õpilane sinna ei kandideeri; false - valitud seepärast, et õpilane sinna kandideerib';
COMMENT ON COLUMN kandideerimiskoht.created IS 'kirje loomise aeg';
COMMENT ON COLUMN kandideerimiskoht.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN kandideerimiskoht.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN kandideerimiskoht.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE kandideerimiskoht IS 'Sooritaja valitud kool, kuhu ta kandideerib ja mis võib näha tema testi tulemusi (gümnaasiumi sisseastumistesti korral)';

-- eis/model/testimine/kysimusehindemarkus.py
COMMENT ON COLUMN kysimusehindemarkus.id IS 'kirje identifikaator';
COMMENT ON COLUMN kysimusehindemarkus.kysimusehinne_id IS 'viide ülesande küsimuse hindepallide kirjele, mille kohta märkus käib';
COMMENT ON COLUMN kysimusehindemarkus.ekspert_labiviija_id IS 'viide eksperthindajale, kelle märkusega on tegu';
COMMENT ON COLUMN kysimusehindemarkus.markus IS 'märkuse tekst';
COMMENT ON COLUMN kysimusehindemarkus.created IS 'kirje loomise aeg';
COMMENT ON COLUMN kysimusehindemarkus.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN kysimusehindemarkus.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN kysimusehindemarkus.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE kysimusehindemarkus IS 'Eksperthindaja märkus küsimuse hinde kohta (vaide korral hindamisel)';

-- eis/model/testimine/soorituslogi.py
COMMENT ON COLUMN soorituslogi.id IS 'kirje identifikaator';
COMMENT ON COLUMN soorituslogi.sooritus_id IS 'viide sooritusele';
COMMENT ON COLUMN soorituslogi.tahised IS 'soorituskoha ja soorituse tähised, kriips vahel';
COMMENT ON COLUMN soorituslogi.reg_toimumispaev_id IS 'registreerimisel määratud toimumispäev';
COMMENT ON COLUMN soorituslogi.kavaaeg IS 'sooritajale kavandatud alguse aeg';
COMMENT ON COLUMN soorituslogi.staatus IS 'sooritamise olek';
COMMENT ON COLUMN soorituslogi.stpohjus IS 'viimase oleku muutmise põhjus';
COMMENT ON COLUMN soorituslogi.hindamine_staatus IS 'hindamise olek';
COMMENT ON COLUMN soorituslogi.pallid IS 'saadud hindepallid';
COMMENT ON COLUMN soorituslogi.pallid_arvuti IS '(esialgne) arvutihinnatav osa hindepallidest';
COMMENT ON COLUMN soorituslogi.pallid_kasitsi IS 'mitte-arvutihinnatav osa hindepallidest';
COMMENT ON COLUMN soorituslogi.tulemus_protsent IS 'saadud hindepallid protsentides suurimast võimalikust tulemusest';
COMMENT ON COLUMN soorituslogi.max_pallid IS 'võimalikud max pallid (sõltub alatestidest vabastusest ja lõdva struktuuri korral komplektist)';
COMMENT ON COLUMN soorituslogi.testiarvuti_id IS 'viide testi sooritamiseks kasutatud arvutile';
COMMENT ON COLUMN soorituslogi.testikoht_id IS 'viide testikohale';
COMMENT ON COLUMN soorituslogi.testiruum_id IS 'viide testiruumile';
COMMENT ON COLUMN soorituslogi.tugiisik_kasutaja_id IS 'viide tugiisikule';
COMMENT ON COLUMN soorituslogi.url IS 'andmeid muutnud tegevuse URL';
COMMENT ON COLUMN soorituslogi.remote_addr IS 'muutja klient';
COMMENT ON COLUMN soorituslogi.server_addr IS 'muutja server';
COMMENT ON COLUMN soorituslogi.created IS 'kirje loomise aeg';
COMMENT ON COLUMN soorituslogi.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN soorituslogi.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN soorituslogi.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE soorituslogi IS 'Soorituse kirje muudatuste logi';

-- eis/model/testimine/nousolek.py
COMMENT ON COLUMN nousolek.id IS 'kirje identifikaator';
COMMENT ON COLUMN nousolek.staatus IS 'olek';
COMMENT ON COLUMN nousolek.toimumisaeg_id IS 'viide toimumisajale';
COMMENT ON COLUMN nousolek.kasutaja_id IS 'viide läbiviija kasutajale';
COMMENT ON COLUMN nousolek.on_vaatleja IS 'kas on nõus vaatlema';
COMMENT ON COLUMN nousolek.on_hindaja IS 'kas on nõus hindama';
COMMENT ON COLUMN nousolek.on_intervjueerija IS 'kas on nõus intervjueerima';
COMMENT ON COLUMN nousolek.vaatleja_ekk IS 'kas vaatlemise nõusoleku sisestas eksamikeskus';
COMMENT ON COLUMN nousolek.hindaja_ekk IS 'kas hindamise nõusoleku sisestas eksamikeskus';
COMMENT ON COLUMN nousolek.intervjueerija_ekk IS 'kas intervjueerimise nõusoleku sisestas eksamikeskus';
COMMENT ON COLUMN nousolek.vaatleja_aeg IS 'millal anti vaatlemise nõusolek';
COMMENT ON COLUMN nousolek.hindaja_aeg IS 'millal anti hindamise nõusolek';
COMMENT ON COLUMN nousolek.intervjueerija_aeg IS 'millal anti intervjueerimise nõusolek';
COMMENT ON COLUMN nousolek.created IS 'kirje loomise aeg';
COMMENT ON COLUMN nousolek.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN nousolek.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN nousolek.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE nousolek IS 'Testi läbiviimise nõusolekud.';

-- eis/model/testimine/sooritajalogi.py
COMMENT ON COLUMN sooritajalogi.id IS 'kirje identifikaator';
COMMENT ON COLUMN sooritajalogi.sooritaja_id IS 'viide registreeringule';
COMMENT ON COLUMN sooritajalogi.kursus_kood IS 'valitud kursus';
COMMENT ON COLUMN sooritajalogi.staatus IS 'omistatud olek, vt Sooritaja.staatus';
COMMENT ON COLUMN sooritajalogi.eesnimi IS 'testi sooritamise ajal kehtinud eesnimi';
COMMENT ON COLUMN sooritajalogi.perenimi IS 'testi sooritamise ajal kehtinud perekonnanimi';
COMMENT ON COLUMN sooritajalogi.lang IS 'soorituskeel';
COMMENT ON COLUMN sooritajalogi.pallid IS 'testi eest saadud hindepallid, testi lõpptulemus pallides';
COMMENT ON COLUMN sooritajalogi.hinne IS 'testi eest saadud hinne, vahemikus 1-5';
COMMENT ON COLUMN sooritajalogi.keeletase_kood IS 'eksamiga hinnatud keeleoskuse tase';
COMMENT ON COLUMN sooritajalogi.tulemus_aeg IS 'tulemuse viimase muutmise aeg';
COMMENT ON COLUMN sooritajalogi.pohjus IS 'oleku muutmise põhjus';
COMMENT ON COLUMN sooritajalogi.data_sig IS 'räsitavad andmed: isikukood, nimi, testi ID, õppeaine, tulemus pallides, tulemuse kuupäev (semikooloniga eraldatud)';
COMMENT ON COLUMN sooritajalogi.data_hash IS 'andmete SHA-256 räsi (base64)';
COMMENT ON COLUMN sooritajalogi.sig_status IS 'allkirjastamise olek: 0=const.G_STAATUS_NONE - ei ole vaja allkirjastada; 1=const.G_STAATUS_UNSIGNED - ootab allkirja; 2=const.G_STAATUS_SIGNED - allkirjastatud; 3=const.G_STAATUS_OLD - aegunud andmed (olemas on uuem kirje); 4=const.G_STAATUS_ERROR - andmed ei vasta tegelikkusele';
COMMENT ON COLUMN sooritajalogi.err_msg IS 'tervikluse kontrolli veateade';
COMMENT ON COLUMN sooritajalogi.url IS 'andmeid muutnud tegevuse URL';
COMMENT ON COLUMN sooritajalogi.remote_addr IS 'muutja klient';
COMMENT ON COLUMN sooritajalogi.server_addr IS 'muutja server';
COMMENT ON COLUMN sooritajalogi.created IS 'kirje loomise aeg';
COMMENT ON COLUMN sooritajalogi.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN sooritajalogi.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN sooritajalogi.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE sooritajalogi IS 'Sooritaja registreeringu ja tulemuste muudatuste logi';

-- eis/model/testimine/vaie.py
COMMENT ON COLUMN vaie.id IS 'kirje identifikaator';
COMMENT ON COLUMN vaie.sooritaja_id IS 'viide.sooritaja kirjele';
COMMENT ON COLUMN vaie.vaide_nr IS 'vaide number, sisestatakse vaide registreerimisel, hiljem kasutatakse otsuse numbrina';
COMMENT ON COLUMN vaie.esitamisaeg IS 'vaide esitamise aeg';
COMMENT ON COLUMN vaie.avaldus_dok IS 'vaide avalduse digiallkirjastatud dokument';
COMMENT ON COLUMN vaie.avaldus_ext IS 'avalduse vorming: ddoc või bdoc või asice';
COMMENT ON COLUMN vaie.ettepanek_pohjendus IS 'ettepaneku põhjendus';
COMMENT ON COLUMN vaie.ettepanek_pdok IS 'pooleli digiallkirjastamisega ettepaneku dokument (kui allkirjastamine pole pooleli, siis tühi)';
COMMENT ON COLUMN vaie.ettepanek_dok IS 'vaide kohta tehtud ettepaneku digiallkirjastatud dokument';
COMMENT ON COLUMN vaie.ettepanek_ext IS 'ettepaneku vorming: ddoc või bdoc või asice';
COMMENT ON COLUMN vaie.h_arvestada IS 'kas tulemuse arvutamisel arvestada vaidehindamist: kui otsuse eelnõu on juba olemas, siis jah; enne eelnõu loomist loetakse hindamist pooleliolevana ja tulemust pole';
COMMENT ON COLUMN vaie.eelnou_pohjendus IS 'otsuse eelnõu põhjendus';
COMMENT ON COLUMN vaie.eelnou_pdf IS 'otsuse eelnõu PDFina';
COMMENT ON COLUMN vaie.arakuulamine_kuni IS 'ärakuulamise tähtaeg, kuni milleni on vaidlustajal võimalik eelnõu kohta arvamust esitada (peale seda läheb vaie otsustamisele)';
COMMENT ON COLUMN vaie.tagasivotmine_dok IS 'avaldus vaide tagasivõtmiseks (vaiet saab tagasi võtta kuni otsuse langetamiseni)';
COMMENT ON COLUMN vaie.tagasivotmine_ext IS 'tagasivõtmise avalduse failitüüp';
COMMENT ON COLUMN vaie.otsus_pohjendus IS 'otsuse põhjendus';
COMMENT ON COLUMN vaie.otsus_kp IS 'otsuse kuupäev';
COMMENT ON COLUMN vaie.otsus_pdf IS 'vaide kohta tehtud otsus PDFina';
COMMENT ON COLUMN vaie.otsus_pdok IS 'pooleli digiallkirjastamisega otsuse dokument (kui allkirjastamine pole pooleli, siis tühi)';
COMMENT ON COLUMN vaie.otsus_dok IS 'vaide kohta tehtud otsuse digiallkirjastatud dokument';
COMMENT ON COLUMN vaie.otsus_ext IS 'otsuse vorming: ddoc või bdoc või asice';
COMMENT ON COLUMN vaie.otsus_epostiga IS 'kas vaidlustaja soovib otsust e-postiga';
COMMENT ON COLUMN vaie.staatus IS 'staatus: 0=const.V_STAATUS_ESITAMATA - esitamata; 1=const.V_STAATUS_ESITATUD - esitatud; 2=const.V_STAATUS_MENETLEMISEL - menetlemisel; 4=const.V_STAATUS_ETTEPANDUD - ettepanek esitatud vaidekomisjonile; 5=const.V_STAATUS_OTSUSTAMISEL - ärakuulamise tähtaeg on läbi; 6=const.V_STAATUS_OTSUSTATUD - otsustatud; 7=const.V_STAATUS_TAGASIVOETUD - tagasi võetud';
COMMENT ON COLUMN vaie.valjaotsitud IS 'kas on välja otsitud (vaiete loetelus linnukesega)';
COMMENT ON COLUMN vaie.allkirjad IS 'antud allkirjade arv otsusel';
COMMENT ON COLUMN vaie.pallid_enne IS 'vaide esitamise ajal kehtinud tulemus';
COMMENT ON COLUMN vaie.pallid_parast IS 'vaidlustusjärgne tulemus';
COMMENT ON COLUMN vaie.muutus IS 'hindepallide muutus (pallid_parast-pallid_enne)';
COMMENT ON COLUMN vaie.tunnistada IS 'mida teha tunnistusega: NULL - mitte midagi (pole vaja tunnistust muuta või on juba tehtud); 1=const.U_STAATUS_UUENDADA - uuendada; 2=const.U_STAATUS_VALJASTADA - väljastada uus; 3=const.U_STAATUS_TYHISTADA - tühistada';
COMMENT ON COLUMN vaie.created IS 'kirje loomise aeg';
COMMENT ON COLUMN vaie.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN vaie.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN vaie.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE vaie IS 'Tesi.sooritaja vaie Haridus- ja Teadusministeeriumile';

-- eis/model/testimine/ruumifail.py
COMMENT ON COLUMN ruumifail.id IS 'kirje identifikaator';
COMMENT ON COLUMN ruumifail.toimumisprotokoll_id IS 'viide toimumise protokollile (määrab soorituskeele)';
COMMENT ON COLUMN ruumifail.testiruum_id IS 'viide testiruumile, mille kohta fail käib';
COMMENT ON COLUMN ruumifail.filename IS 'failinimi laadimisel';
COMMENT ON COLUMN ruumifail.filesize IS 'faili suurus';
COMMENT ON COLUMN ruumifail.fileversion IS 'versioon';
COMMENT ON COLUMN ruumifail.created IS 'kirje loomise aeg';
COMMENT ON COLUMN ruumifail.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN ruumifail.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN ruumifail.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE ruumifail IS 'Toimumise protokollile lisatud fail, nt ruumi istumisplaan';

-- eis/model/testimine/sooritus.py
COMMENT ON COLUMN sooritus.id IS 'kirje identifikaator';
COMMENT ON COLUMN sooritus.sooritaja_id IS 'viide sooritaja kirjele';
COMMENT ON COLUMN sooritus.testiosa_id IS 'viide testiosale';
COMMENT ON COLUMN sooritus.toimumisaeg_id IS 'viide toimumisajale, puudub avaliku vaate testi korral';
COMMENT ON COLUMN sooritus.tahis IS 'testiosasoorituse tähis (kui testikoht on määratud, unikaalne testikoha piires), selle järgi sorditakse sooritajaid protokollis või ruumis; pikkus üldjuhul 3, vajadusel 4';
COMMENT ON COLUMN sooritus.tahised IS 'soorituskoha ja soorituse tähised, kriips vahel';
COMMENT ON COLUMN sooritus.reg_toimumispaev_id IS 'registreerimisel määratud toimumispäev (kui on antud, siis sooritajat saab suunata ainult selle toimumispäeva testiruumi)';
COMMENT ON COLUMN sooritus.kavaaeg IS 'sooritajale kavandatud alguse aeg';
COMMENT ON COLUMN sooritus.algus IS 'testiosasoorituse esimese seansi tegelik algus';
COMMENT ON COLUMN sooritus.lopp IS 'testiosasoorituse viimase seansi lõpp';
COMMENT ON COLUMN sooritus.seansi_algus IS 'testiosasoorituse viimase seansi algus';
COMMENT ON COLUMN sooritus.lisaaeg IS 'sooritajale antud lisaaeg, lisandub testiosa piirajale';
COMMENT ON COLUMN sooritus.ajakulu IS 'kulutatud sekundite arv kõigi lõpetatud seansside peale kokku';
COMMENT ON COLUMN sooritus.peatus_algus IS 'kui sooritamine on katkestatud, siis viimase katkestamise aeg (nullitakse sooritamise jätkamisel)';
COMMENT ON COLUMN sooritus.peatatud_aeg IS 'sekundite arv, millal sooritamine oli katkestatud (arvutatakse sooritamise jätkamisel)';
COMMENT ON COLUMN sooritus.piiraeg_muutus IS 'märge, et testi sooritamise ajal on muudetud testiosa või alatesti piiraega ja peab brauseris piiraja arvestust muutma (peale brauseris taimeri muutmist nullitakse);';
COMMENT ON COLUMN sooritus.markus IS 'läbiviija märkus sooritaja kohta';
COMMENT ON COLUMN sooritus.staatus IS 'sooritamise olek: 0=const.S_STAATUS_TYHISTATUD - tühistatud; 1=const.S_STAATUS_REGAMATA - registreerimata; 2=const.S_STAATUS_TASUMATA - tasumata; 3=const.S_STAATUS_REGATUD - registreeritud; 5=const.S_STAATUS_ALUSTAMATA - alustamata; 6=const.S_STAATUS_POOLELI - pooleli; 7=const.S_STAATUS_KATKESTATUD - ise katkestanud; 8=const.S_STAATUS_TEHTUD - tehtud; 9=const.S_STAATUS_EEMALDATUD - eemaldatud; 10=const.S_STAATUS_PUUDUS - puudus; 11=const.S_STAATUS_VABASTATUD - vabastatud; 12=const.S_STAATUS_KATKESPROT - protokollil katkestanuks märgitud';
COMMENT ON COLUMN sooritus.stpohjus IS 'viimase oleku muutmise põhjus';
COMMENT ON COLUMN sooritus.luba_veriff IS 'true - luba sooritada ilma isikut tõendamata (kui toimumisaeg.verif või toimumisaeg.verif_seb on seatud, st kasutusel on Veriff või Proctorio või SEB)';
COMMENT ON COLUMN sooritus.puudumise_pohjus IS 'puudumise põhjus, kui staatus on 10: 12=const.S_STAATUS_PUUDUS_VANEM - puudus lapsevanema keeldumise tõttu; 13=const.S_STAATUS_PUUDUS_HEV - puudus erievajduste tõttu';
COMMENT ON COLUMN sooritus.hindamine_staatus IS 'hindamise olek: 0=const.H_STAATUS_HINDAMATA - kõik hindamiskogumid hindamata; 1=const.H_STAATUS_POOLELI - mõni hindamiskogum hindamisel; 6=const.H_STAATUS_HINNATUD - kõik hindamiskogumid hinnatud; 10=const.H_STAATUS_TOOPUUDU - töö puudub';
COMMENT ON COLUMN sooritus.pallid IS 'saadud hindepallid';
COMMENT ON COLUMN sooritus.pallid_arvuti IS '(esialgne) arvutihinnatav osa hindepallidest';
COMMENT ON COLUMN sooritus.pallid_kasitsi IS 'mitte-arvutihinnatav osa hindepallidest';
COMMENT ON COLUMN sooritus.pallid_enne_vaiet IS 'hindepallid enne vaidlustamist';
COMMENT ON COLUMN sooritus.pallid_peale_vaiet IS 'ettepanek, millised võiksid olla pallid peale vaiet';
COMMENT ON COLUMN sooritus.yhisosa_pallid IS 'testimiskordade ühisossa kuuluvate küsimuste eest saadud hindepallid';
COMMENT ON COLUMN sooritus.tulemus_protsent IS 'saadud hindepallid protsentides suurimast võimalikust tulemusest';
COMMENT ON COLUMN sooritus.max_pallid IS 'võimalikud max pallid (sõltub alatestidest vabastusest ja lõdva struktuuri korral komplektist)';
COMMENT ON COLUMN sooritus.ylesanneteta_tulemus IS 'kas testiosa tulemus on sisestatud toimumise protokollile või tuleb rv tunnistuselt (siis ülesannete kaupa tulemusi EISis ei ole)';
COMMENT ON COLUMN sooritus.on_rikkumine IS 'VI hindamise korral märge, kui tuvastati rikkumine ja testitöö tuleb hinnata 0 punktiga (ülesannete tulemusi ei muudeta)';
COMMENT ON COLUMN sooritus.rikkumiskirjeldus IS 'rikkumise märkimise põhjendus';
COMMENT ON COLUMN sooritus.hindamiskogumita IS 'kas hinnatakse hindamiskogumita (jah, kui on testimiskorrata test või eeltesti testimiskorraga test)';
COMMENT ON COLUMN sooritus.testikoht_id IS 'viide testi sooritamise kohale';
COMMENT ON COLUMN sooritus.testiruum_id IS 'viide testi sooritamise ruumile';
COMMENT ON COLUMN sooritus.testiarvuti_id IS 'viide testi sooritamiseks kasutatud arvutile';
COMMENT ON COLUMN sooritus.verifflog_id IS 'viide viimasele verifitseerimisele';
COMMENT ON COLUMN sooritus.on_erivajadused IS 'kas sooritaja on taotlenud eritingimusi';
COMMENT ON COLUMN sooritus.on_erivajadused_kinnitatud IS 'kas sooritaja eritingimused on Harnos kinnitatud';
COMMENT ON COLUMN sooritus.on_erivajadused_vaadatud IS 'kas sooritaja eritingimused on Harnos üle vaadatud (kui kinnitamist ei toimu)';
COMMENT ON COLUMN sooritus.on_erivajadused_tagasilykatud IS 'kas kõik sooritaja eritingimused on Harnos tagasi lükatud';
COMMENT ON COLUMN sooritus.erivajadused_teavitatud IS 'eritingimuste teate saatmise aeg';
COMMENT ON COLUMN sooritus.tugiisik_kasutaja_id IS 'viide tugiisikule';
COMMENT ON COLUMN sooritus.intervjuu_labiviija_id IS 'viide intervjueerijale suulise (hindajaga) vastamise vormi korral';
COMMENT ON COLUMN sooritus.piirkond_id IS 'testikoha piirkond, dubleeritud päringute kiirendamiseks';
COMMENT ON COLUMN sooritus.testiprotokoll_id IS 'viide testiprotokollile; p-testitöö on jaotatud vastava testiprotokolli kõigi tagastusümbrike vahel';
COMMENT ON COLUMN sooritus.toimumisprotokoll_id IS 'viide toimumisprotokollile, tekib protokolli salvestamisel ja on kasutusel protokolli kinnituse kontrollimiseks; valimi korral viitab mittevalimi protokollile, mille kaudu soorituse olek märgiti';
COMMENT ON COLUMN sooritus.viimane_valitudylesanne_id IS 'viimane vaadatud valitudylesanne';
COMMENT ON COLUMN sooritus.viimane_testiylesanne_id IS 'viimane vaadatud testiylesanne';
COMMENT ON COLUMN sooritus.tutv_esit_aeg IS 'tööga tutvumise soovi esitamise aeg';
COMMENT ON COLUMN sooritus.soovib_skanni IS 'kas soovib saada oma töö skannitud koopiat';
COMMENT ON COLUMN sooritus.valjaotsitud IS 'kas töö on välja otsitud (tööga tutvumise soovi korral): true - välja otsitud; false - välja otsimata';
COMMENT ON COLUMN sooritus.valikujrk IS 'ülesannete järjekord antud soorituses (kui on juhusliku järjekorraga testiosa)';
COMMENT ON COLUMN sooritus.klastrist_seisuga IS 'aeg, mil viimati soorituse andmed klastrist võeti';
COMMENT ON COLUMN sooritus.klastrist_toomata IS 'true - olek on tehtud, aga andmed veel klastris';
COMMENT ON COLUMN sooritus.created IS 'kirje loomise aeg';
COMMENT ON COLUMN sooritus.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN sooritus.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN sooritus.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE sooritus IS 'Testiosasooritus';

COMMENT ON TABLE tempsooritus IS 'Testiosasooritus';

-- eis/model/testimine/khstatistika.py
COMMENT ON COLUMN khstatistika.id IS 'kirje identifikaator';
COMMENT ON COLUMN khstatistika.kysimusestatistika_id IS 'viide küsimusele';
COMMENT ON COLUMN khstatistika.vastuste_arv IS 'antud vastuse andnute arv';
COMMENT ON COLUMN khstatistika.toorpunktid IS 'hindaja antud toorpunktid (ülesande skaala järgi)';
COMMENT ON COLUMN khstatistika.pallid IS 'hindepallid (testiülesande skaala järgi)';
COMMENT ON COLUMN khstatistika.nullipohj_kood IS 'null punkti andmise põhjus, klassifikaator NULLIPOHJ';
COMMENT ON COLUMN khstatistika.created IS 'kirje loomise aeg';
COMMENT ON COLUMN khstatistika.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN khstatistika.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN khstatistika.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE khstatistika IS 'Üksikküsimuste eest antud punktide statistika.
    Mõeldud eeskätt nende küsimuste jaoks, mille vastuseid andmebaasis ei hoita.
    Erinevalt kvstatistika tabelist ei käi see statistika vastuste kaupa,
    vaid küsimuse kaupa (ühel küsimusel võib olla mitu vastust).';

-- eis/model/testimine/statistikaraport.py
COMMENT ON COLUMN statistikaraport.id IS 'kirje identifikaator';
COMMENT ON COLUMN statistikaraport.test_id IS 'viide testile, kui fail käib teatud testi kohta ja on loetav koolides, kus on selle testi sooritajaid';
COMMENT ON COLUMN statistikaraport.kursus_kood IS 'lai või kitsas (matemaatika korral), klassifikaator KURSUS';
COMMENT ON COLUMN statistikaraport.aasta IS 'aastaarv';
COMMENT ON COLUMN statistikaraport.filename IS 'failinimi';
COMMENT ON COLUMN statistikaraport.filesize IS 'faili suurus baitides';
COMMENT ON COLUMN statistikaraport.fileversion IS 'versioon';
COMMENT ON COLUMN statistikaraport.avalik IS 'kas raport on üle vaadatud ja avalik';
COMMENT ON COLUMN statistikaraport.format IS 'faili formaat: pdf, html';
COMMENT ON COLUMN statistikaraport.created IS 'kirje loomise aeg';
COMMENT ON COLUMN statistikaraport.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN statistikaraport.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN statistikaraport.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE statistikaraport IS 'Eksami statistika raport avalikus vaates alla laadimiseks';

-- eis/model/testimine/sisestuslogi.py
COMMENT ON COLUMN sisestuslogi.id IS 'kirje identifikaator';
COMMENT ON COLUMN sisestuslogi.kasutaja_id IS 'sisestaja kasutaja';
COMMENT ON COLUMN sisestuslogi.hindamine_id IS 'viide hindamise kirjele';
COMMENT ON COLUMN sisestuslogi.ylesandehinne_id IS 'hindepallide muutmise korral viide hinde kirjele';
COMMENT ON COLUMN sisestuslogi.kysimusehinne_id IS 'hindepallide muutmise korral viide küsimuse hinde kirjele';
COMMENT ON COLUMN sisestuslogi.aspektihinne_id IS 'aspekti hindepallide muutmise korral viide aspektihinde kirjele';
COMMENT ON COLUMN sisestuslogi.liik IS 'mida muudeti: 1 - hindepallid; 2 - komplekt; 3 - hindaja; 4 - intervjueerija';
COMMENT ON COLUMN sisestuslogi.vana IS 'uus väärtus';
COMMENT ON COLUMN sisestuslogi.uus IS 'vana väärtus';
COMMENT ON COLUMN sisestuslogi.aeg IS 'andmete muutmise aeg';
COMMENT ON COLUMN sisestuslogi.created IS 'kirje loomise aeg';
COMMENT ON COLUMN sisestuslogi.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN sisestuslogi.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN sisestuslogi.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE sisestuslogi IS 'Sisestamise muudatused';

-- eis/model/testimine/erivajadus.py
COMMENT ON COLUMN erivajadus.id IS 'kirje identifikaator';
COMMENT ON COLUMN erivajadus.erivajadus_kood IS 'eritingimused vanade kirjete korral, eritingimuste klassifikaator ERIVAJADUS';
COMMENT ON COLUMN erivajadus.taotlus IS 'kas eritingimusi on taotletud';
COMMENT ON COLUMN erivajadus.taotlus_markus IS 'selgitus eritingimuste taotlemise juurde';
COMMENT ON COLUMN erivajadus.kinnitus IS 'kas eritingimused on kinnitatud';
COMMENT ON COLUMN erivajadus.kinnitus_markus IS 'selgitus eritingimuste kinnitamise juurde';
COMMENT ON COLUMN erivajadus.sooritus_id IS 'viide soorituse kirjele';
COMMENT ON COLUMN erivajadus.kasutamata IS 'kas lubatud eritingimust ei kasutatud (märgitakse toimumise protokollile)';
COMMENT ON COLUMN erivajadus.created IS 'kirje loomise aeg';
COMMENT ON COLUMN erivajadus.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN erivajadus.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN erivajadus.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE erivajadus IS 'Sooritajate eritingimused';

-- eis/model/testimine/__init__.py
-- eis/model/testimine/ksmarkus.py
COMMENT ON COLUMN ksmarkus.id IS 'kirje identifikaator';
COMMENT ON COLUMN ksmarkus.kysimusevastus_id IS 'viide kommenteeritavale vastusele';
COMMENT ON COLUMN ksmarkus.seq IS 'mitmes vastus (küsimuse piires)';
COMMENT ON COLUMN ksmarkus.ylesandehinne_id IS 'viide ylesande hinde kirjele, puudub automaatse tekstianalüüsi märkuste kirjel';
COMMENT ON COLUMN ksmarkus.markus IS 'hindaja märkused json-stringina kujul [[offset,tüüp,tekst]] või [[offset,tüüp,tekst,pikkus]]';
COMMENT ON COLUMN ksmarkus.created IS 'kirje loomise aeg';
COMMENT ON COLUMN ksmarkus.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN ksmarkus.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN ksmarkus.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE ksmarkus IS 'Avatud küsimuse vastuse sisse hindaja poolt lisatud kommentaarid ja vead';

-- eis/model/testimine/tagastusymbrik.py
COMMENT ON COLUMN tagastusymbrik.id IS 'kirje identifikaator';
COMMENT ON COLUMN tagastusymbrik.tahised IS 'tagastusümbrikuliigile vastava ümbriku korral: testi, testiosa, testimiskorra, testikoha, testiprotokolli, tagastusümbrikuliigi tähised, kriips vahel (2 protokolli ümbrikul on testiprotokollide tähised kaldkriipsuga eraldatud); peaümbriku korral: testi, testiosa, testimiskorra, testikoha tähised, kriips vahel (peaümbriku korral ei ole tähis unikaalne, kuna kõigil sama koha testipakettidel on sama tähis; triipkoodile trükitakse seepärast lisaks tähisele ka paketi keele kood)';
COMMENT ON COLUMN tagastusymbrik.testipakett_id IS 'viide testipaketile';
COMMENT ON COLUMN tagastusymbrik.testiprotokoll_id IS 'viide testiprotokollile; kui puudub, siis on peaümbrik';
COMMENT ON COLUMN tagastusymbrik.testiprotokoll2_id IS 'viide teisele testiprotokollile, kui tagastusymbrikuliik.arvutus=2';
COMMENT ON COLUMN tagastusymbrik.tagastusymbrikuliik_id IS 'tagastusümbrikuliik; kui puudub, siis on peaümbrik';
COMMENT ON COLUMN tagastusymbrik.staatus IS 'olek, M_STAATUS';
COMMENT ON COLUMN tagastusymbrik.labiviija_id IS 'viide hindajale (või hindajate paarile), kui ümbrik on hindajale hindamiseks väljastatud';
COMMENT ON COLUMN tagastusymbrik.ymbrikearv IS 'ümbrike arv, mis on saadud tööde arvu jagamisel ümbriku mahuga';
COMMENT ON COLUMN tagastusymbrik.valjastatud IS 'hindajale väljastamise aeg, vajalik hindaja ümbrike sortimiseks väljastamise järjekorras';
COMMENT ON COLUMN tagastusymbrik.arvutus IS 'arvutusprotsessi tunnus';
COMMENT ON COLUMN tagastusymbrik.created IS 'kirje loomise aeg';
COMMENT ON COLUMN tagastusymbrik.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN tagastusymbrik.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN tagastusymbrik.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE tagastusymbrik IS 'Testiprotokollirühma ja tagastusümbrikuliigiga seotud tagastusümbrike kogus. 
    Igast tagastusümbrikuliigist on oma ümbrik.
    Ilma liigita ümbrik on peaümbrik.
    Kui protokollirühma suurus on suurem kui tagastusümbriku maht, siis on ühe 
    kirje kohta tegelikkuses mitu ümbrikut (sama numbriga). 
    Eeldame, et kõiki ühele kirjele vastavaid ümbrikke liigutatakse alati koos.
    See on sellepärast nii, et vastasel juhul tekiks ümbrike 
    hindajatele hindamiseks väljastamisel probleem,
    kuna ei ole teada, milliste sooritajate tööd millises ümbrikus asuvad.
    Kui ühe protokolli ümbrikud satuks erinevate hindajate kätte,
    siis poleks teada, milliste sooritajate tööd milliste hindajate käes on.';

-- eis/model/testimine/testireglogi.py
COMMENT ON COLUMN sooritajalogi.id IS 'kirje identifikaator';
COMMENT ON COLUMN sooritajalogi.sooritaja_id IS 'viide registreeringule';
COMMENT ON COLUMN sooritajalogi.kursus_kood IS 'valitud kursus';
COMMENT ON COLUMN sooritajalogi.staatus IS 'omistatud olek, vt Sooritaja.staatus';
COMMENT ON COLUMN sooritajalogi.eesnimi IS 'testi sooritamise ajal kehtinud eesnimi';
COMMENT ON COLUMN sooritajalogi.perenimi IS 'testi sooritamise ajal kehtinud perekonnanimi';
COMMENT ON COLUMN sooritajalogi.lang IS 'soorituskeel';
COMMENT ON COLUMN sooritajalogi.pallid IS 'testi eest saadud hindepallid, testi lõpptulemus pallides';
COMMENT ON COLUMN sooritajalogi.hinne IS 'testi eest saadud hinne, vahemikus 1-5';
COMMENT ON COLUMN sooritajalogi.keeletase_kood IS 'eksamiga hinnatud keeleoskuse tase';
COMMENT ON COLUMN sooritajalogi.tulemus_aeg IS 'tulemuse viimase muutmise aeg';
COMMENT ON COLUMN sooritajalogi.pohjus IS 'oleku muutmise põhjus';
COMMENT ON COLUMN sooritajalogi.data_sig IS 'räsitavad andmed: isikukood, nimi, testi ID, õppeaine, tulemus pallides, tulemuse kuupäev (semikooloniga eraldatud)';
COMMENT ON COLUMN sooritajalogi.data_hash IS 'andmete SHA-256 räsi (base64)';
COMMENT ON COLUMN sooritajalogi.sig_status IS 'allkirjastamise olek: 0=const.G_STAATUS_NONE - ei ole vaja allkirjastada; 1=const.G_STAATUS_UNSIGNED - ootab allkirja; 2=const.G_STAATUS_SIGNED - allkirjastatud; 3=const.G_STAATUS_OLD - aegunud andmed (olemas on uuem kirje); 4=const.G_STAATUS_ERROR - andmed ei vasta tegelikkusele';
COMMENT ON COLUMN sooritajalogi.err_msg IS 'tervikluse kontrolli veateade';
COMMENT ON COLUMN sooritajalogi.url IS 'andmeid muutnud tegevuse URL';
COMMENT ON COLUMN sooritajalogi.remote_addr IS 'muutja klient';
COMMENT ON COLUMN sooritajalogi.server_addr IS 'muutja server';
COMMENT ON COLUMN sooritajalogi.created IS 'kirje loomise aeg';
COMMENT ON COLUMN sooritajalogi.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN sooritajalogi.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN sooritajalogi.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE sooritajalogi IS 'Sooritaja registreeringu ja tulemuste muudatuste logi';

-- eis/model/testimine/valjastusymbrikuliik.py
COMMENT ON COLUMN valjastusymbrikuliik.id IS 'kirje identifikaator';
COMMENT ON COLUMN valjastusymbrikuliik.tahis IS 'liigi tähis, määratakse automaatselt kujul 1,2,...';
COMMENT ON COLUMN valjastusymbrikuliik.nimi IS 'nimetus';
COMMENT ON COLUMN valjastusymbrikuliik.toimumisaeg_id IS 'viide toimumisajale';
COMMENT ON COLUMN valjastusymbrikuliik.maht IS 'mitu testitööd mahub ühte ümbrikusse';
COMMENT ON COLUMN valjastusymbrikuliik.lisatoode_koef IS 'lisatööde koefitsient, millega korrutatakse sooritajate arv läbi ja ümardatakse üles ning saadakse antud liiki ümbrikus saadetavate tööde arv';
COMMENT ON COLUMN valjastusymbrikuliik.lisatoode_arv IS 'lisatööde arv, mis liidetakse sooritajate arvule';
COMMENT ON COLUMN valjastusymbrikuliik.ymarduskordaja IS 'testiruumi saadetavate tööde arv peab selle arvuga jaguma (tavaliselt 1, 5 või 10)';
COMMENT ON COLUMN valjastusymbrikuliik.keeleylene IS 'false - eraldi väljastusümbrik iga keele ja kursuse kohta; true - ühine väljastusümbrik kõigile keeltele ja kursustele (tehtud matemaatika riigieksami mustandite jaoks)';
COMMENT ON COLUMN valjastusymbrikuliik.sisukohta IS 'mille kohta ümbrik teha: 3 - testipaketi kohta; 4 - testiruumi kohta';
COMMENT ON COLUMN valjastusymbrikuliik.created IS 'kirje loomise aeg';
COMMENT ON COLUMN valjastusymbrikuliik.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN valjastusymbrikuliik.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN valjastusymbrikuliik.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE valjastusymbrikuliik IS 'Väljastusümbriku liik';

-- eis/model/testimine/ylesandehindemarkus.py
COMMENT ON COLUMN ylesandehindemarkus.id IS 'kirje identifikaator';
COMMENT ON COLUMN ylesandehindemarkus.ylesandehinne_id IS 'viide ülesande hindepallide kirjele, mille kohta märkus käib';
COMMENT ON COLUMN ylesandehindemarkus.ekspert_labiviija_id IS 'viide eksperthindajale, kelle märkusega on tegu';
COMMENT ON COLUMN ylesandehindemarkus.markus IS 'märkuse tekst';
COMMENT ON COLUMN ylesandehindemarkus.created IS 'kirje loomise aeg';
COMMENT ON COLUMN ylesandehindemarkus.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN ylesandehindemarkus.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN ylesandehindemarkus.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE ylesandehindemarkus IS 'Eksperthindaja märkus ülesande vastuse kohta (vaide korral hindamisel)';

-- eis/model/testimine/hindamisolek.py
COMMENT ON COLUMN hindamisolek.id IS 'kirje identifikaator';
COMMENT ON COLUMN hindamisolek.sooritus_id IS 'viide hinnatavale sooritusele';
COMMENT ON COLUMN hindamisolek.staatus IS 'sisestamise olek: 0=const.H_STAATUS_HINDAMATA - alustamata; 1=const.H_STAATUS_POOLELI - hindamisel; 2=const.H_STAATUS_LYKATUD - loobutud; 3=const.H_STAATUS_HINNATUD - hinnatud';
COMMENT ON COLUMN hindamisolek.hindamiskogum_id IS 'viide hindamiskogumile (puudub testimiskorrata testi hindamisel)';
COMMENT ON COLUMN hindamisolek.hindamistase IS 'kõrgeim vajalik hindamine: 0 - ei vaja hindamist (hindamiskogum on täielikult arvutihinnatav); 1=const.HINDAJA1 - ühekordne hindamine; 2=const.HINDAJA2 - kahekordne hindamine; 3=const.HINDAJA3 - kolmas hindamine; 4=const.HINDAJA4 - eksperthindamine erinevuste korral (IV hindamine); 5=const.HINDAJA5 - eksperthindamine vaide korral; 6=const.HINDAJA6 - eksperthindamine kohtu poolt';
COMMENT ON COLUMN hindamisolek.hindamisprobleem IS 'antud hindamistaseme hindamisprobleem: 0=const.H_PROBLEEM_POLE - pole; 1=const.H_PROBLEEM_SISESTAMATA - sisestamata; 2=const.H_PROBLEEM_SISESTUSERINEVUS - sisestusvead; 3=const.H_PROBLEEM_HINDAMISERINEVUS - hindamiserinevus; 4=const.H_PROBLEEM_TOOPUUDU - töö puudu või jääb hindamata; 5=const.H_PROBLEEM_VAIE - vaidehindamine tehtud, kuid vaideotsuse eelnõud veel pole ja vaidehindamist ei arvestata';
COMMENT ON COLUMN hindamisolek.selgitus IS 'hindamisprobleemi vabatekstiline selgitus';
COMMENT ON COLUMN hindamisolek.puudus IS 'true - ühtki hindamisoleku ülesannet pole sooritatud; false - on midagi hinnata';
COMMENT ON COLUMN hindamisolek.mittekasitsi IS 'kas kõik on arvutiga hinnatav (käsitsihinnatavate küsimuste vastuseid pole)';
COMMENT ON COLUMN hindamisolek.min_hindamistase IS 'hindamistase, millest madalamaks ei saa tagasi minna (ilma hindamiserinevuseta kolmandat hindamist vajavate tööde määramisel antakse väärtus 3)';
COMMENT ON COLUMN hindamisolek.pallid IS 'soorituse lõplikud pallid antud hindamiskogumi eest';
COMMENT ON COLUMN hindamisolek.toorpunktid IS 'soorituse toorpunktide summa antud hindamiskogumi eest';
COMMENT ON COLUMN hindamisolek.hindamiserinevus IS 'hindamiserinevus (pallide vahe) juhul, kui on vaja olnud kolmandat hindamist';
COMMENT ON COLUMN hindamisolek.komplekt_id IS 'viide komplektile';
COMMENT ON COLUMN hindamisolek.created IS 'kirje loomise aeg';
COMMENT ON COLUMN hindamisolek.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN hindamisolek.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN hindamisolek.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE hindamisolek IS 'Soorituse hindamise kehtiv olek hindamiskogumite lõikes.
    Iga soorituse ja hindamiskogumi kohta on üks kirje.';

-- eis/model/testimine/testiarvuti.py
COMMENT ON COLUMN testiarvuti.id IS 'kirje identifikaator';
COMMENT ON COLUMN testiarvuti.seq IS 'arvuti järjekorranumber testiruumis';
COMMENT ON COLUMN testiarvuti.tahis IS 'arvuti unikaalne ID testimiskorral, kujul TESTIOSA-TESTIKOHT-SEQ';
COMMENT ON COLUMN testiarvuti.parool IS 'arvuti brauserisse registreerimisel jäetud cookie';
COMMENT ON COLUMN testiarvuti.ip IS 'arvuti IP-aadress (ei pruugi olla unikaalne)';
COMMENT ON COLUMN testiarvuti.testiruum_id IS 'viide testiruumile';
COMMENT ON COLUMN testiarvuti.staatus IS 'olek: 0 - kehtetu; 1 - kehtiv';
COMMENT ON COLUMN testiarvuti.algne_id IS 'arvuti unikaalne ID (kui arvutis on samaaegselt mitu registreeringut)';
COMMENT ON COLUMN testiarvuti.kehtib_kuni IS 'kehtimise lõpp';
COMMENT ON COLUMN testiarvuti.created IS 'kirje loomise aeg';
COMMENT ON COLUMN testiarvuti.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN testiarvuti.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN testiarvuti.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE testiarvuti IS 'Testi sooritamiseks registreeritud arvuti andmed';

-- eis/model/testimine/kvstatistika.py
COMMENT ON COLUMN kvstatistika.id IS 'kirje identifikaator';
COMMENT ON COLUMN kvstatistika.kysimusestatistika_id IS 'viide küsimusele';
COMMENT ON COLUMN kvstatistika.vastuste_arv IS 'antud vastuse andnute arv';
COMMENT ON COLUMN kvstatistika.tyyp IS 'vastuse tüüp: NULL - vastust pole (kirjet kasutatakse hindepallide jaoks); t=const.RTYPE_CORRECT - õige/vale; s=const.RTYPE_STRING - sisu; f=const.RTYPE_FILE - filedata ja filename; i=const.RTYPE_IDENTIFIER - kood1; p=const.RTYPE_PAIR - kood1 ja kood2; o=const.RTYPE_ORDERED - järjestus; c=const.RTYPE_COORDS - koordinaadid; x=const.RTYPE_POINT - punkt';
COMMENT ON COLUMN kvstatistika.sisu IS 'vabatekstiline vastus või muu mitte-valikvastus (nt punkti koordinaadid)';
COMMENT ON COLUMN kvstatistika.kood1 IS 'valikvastuse korral valiku kood';
COMMENT ON COLUMN kvstatistika.kood2 IS 'valikvastuste paari korral teise valiku kood';
COMMENT ON COLUMN kvstatistika.oige IS 'kas vastus oli õige või vale: 0=const.C_VALE - vale; 2=const.C_OIGE - õige; 8=const.C_LOETAMATU - loetamatu; 9=const.C_VASTAMATA - vastamata (õige/vale sisestamise korral sisestatakse; vastuse olemasolu korral arvutihinnatavas ülesandes arvutatakse hindamismaatriksi põhjal; kui hindaja määrab pallid; siis max pallide korral 2=const.C_OIGE; muu positiivse palli korral 1=const.C_OSAOIGE; 0p korral 0=const.C_VALE; - korral 9=const.C_VASTAMATA)';
COMMENT ON COLUMN kvstatistika.maatriks IS 'mitmenda hindamismaatriksiga see vastus on hinnatav';
COMMENT ON COLUMN kvstatistika.hindamismaatriks_id IS 'viide hindamismaatriksi kirjele, vajalik statistikas vastuse selgituse otsimisel';
COMMENT ON COLUMN kvstatistika.created IS 'kirje loomise aeg';
COMMENT ON COLUMN kvstatistika.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN kvstatistika.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN kvstatistika.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE kvstatistika IS 'Üksikküsimuste vastuste statistika';

-- eis/model/testimine/aspektihinne.py
COMMENT ON COLUMN aspektihinne.id IS 'kirje identifikaator';
COMMENT ON COLUMN aspektihinne.toorpunktid IS 'hindaja antud toorpunktid (ülesande skaala järgi)';
COMMENT ON COLUMN aspektihinne.pallid IS 'hindepallid (testiülesande skaala järgi)';
COMMENT ON COLUMN aspektihinne.markus IS 'märkused';
COMMENT ON COLUMN aspektihinne.nullipohj_kood IS 'null punkti andmise põhjus, klassifikaator NULLIPOHJ';
COMMENT ON COLUMN aspektihinne.created IS 'kirje loomise aeg';
COMMENT ON COLUMN aspektihinne.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN aspektihinne.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN aspektihinne.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE aspektihinne IS 'Hindaja antud hinne ülesande aspektile.
    Kui ülesandel on hindamisaspektid, siis iga aspekti kohta on eraldi kirje.
    Muidu ei ole ühtki kirjet.';

-- eis/model/testimine/testitunnistus.py
COMMENT ON COLUMN testitunnistus.id IS 'kirje identifikaator';
COMMENT ON COLUMN testitunnistus.tunnistus_id IS 'viide tunnistusele';
COMMENT ON COLUMN testitunnistus.sooritaja_id IS 'viide sooritajale (testisoorituse kirjele)';
COMMENT ON COLUMN testitunnistus.created IS 'kirje loomise aeg';
COMMENT ON COLUMN testitunnistus.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN testitunnistus.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN testitunnistus.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE testitunnistus IS 'Tunnistuse seos tunnistusele kantud testisooritustega';

-- eis/model/testimine/testikoht.py
COMMENT ON COLUMN testikoht.id IS 'kirje identifikaator';
COMMENT ON COLUMN testikoht.tahis IS 'testikoha tähis, unikaalne toimumisaja piires (testimiskorraga testi korral)';
COMMENT ON COLUMN testikoht.tahised IS 'testi, testiosa, testimiskorra ja testikoha tähised, kriips vahel (testimiskorraga testi korral)';
COMMENT ON COLUMN testikoht.testiosa_id IS 'viide testiosale';
COMMENT ON COLUMN testikoht.toimumisaeg_id IS 'viide toimumisajale (puudub avaliku vaate testi korral)';
COMMENT ON COLUMN testikoht.koht_id IS 'viide soorituskohale (kui avaliku testi koostaja pole pedagoog, siis võib NULL olla)';
COMMENT ON COLUMN testikoht.alates IS 'algus';
COMMENT ON COLUMN testikoht.staatus IS 'olek: 0=const.B_STAATUS_KEHTETU - kehtetu; 1=const.B_STAATUS_KEHTIV - kehtiv';
COMMENT ON COLUMN testikoht.sooritused_seq IS 'testikoha soorituste tähiste sekvents';
COMMENT ON COLUMN testikoht.markus IS 'märkused';
COMMENT ON COLUMN testikoht.koolinimi_id IS 'viide testi sooritamise ajal kehtinud koha nime kirjele';
COMMENT ON COLUMN testikoht.koht_aadress_kood1 IS 'koha maakonna kood testi sooritamise ajal (statistika jaoks)';
COMMENT ON COLUMN testikoht.koht_aadress_kood2 IS 'koha omavalitsuse kood testi sooritamise ajal (statistika jaoks)';
COMMENT ON COLUMN testikoht.koht_piirkond_id IS 'koha piirkond testi sooritamise ajal (statistika jaoks)';
COMMENT ON COLUMN testikoht.meeldetuletus IS 'viimase korraldamise meeldetuletuse saatmise aeg';
COMMENT ON COLUMN testikoht.created IS 'kirje loomise aeg';
COMMENT ON COLUMN testikoht.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN testikoht.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN testikoht.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE testikoht IS 'Testikoht, testi sooritamise koht ehk soorituskoht';

-- eis/model/testimine/kriteeriumihinne.py
COMMENT ON COLUMN kriteeriumihinne.id IS 'kirje identifikaator';
COMMENT ON COLUMN kriteeriumihinne.hindamine_id IS 'viide hindamise/sisestamise kirjele';
COMMENT ON COLUMN kriteeriumihinne.hindamiskriteerium_id IS 'viide hindamiskriteeriumile';
COMMENT ON COLUMN kriteeriumihinne.toorpunktid IS 'toorpunktid (hindamiskriteeriumi skaala järgi)';
COMMENT ON COLUMN kriteeriumihinne.pallid IS 'hindepallid (peale kaaluga korrutamist)';
COMMENT ON COLUMN kriteeriumihinne.markus IS 'märkused';
COMMENT ON COLUMN kriteeriumihinne.nullipohj_kood IS 'null punkti andmise põhjus, klassifikaator NULLIPOHJ';
COMMENT ON COLUMN kriteeriumihinne.created IS 'kirje loomise aeg';
COMMENT ON COLUMN kriteeriumihinne.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN kriteeriumihinne.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN kriteeriumihinne.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE kriteeriumihinne IS 'Hindaja antud hinne hindamiskogumi hindamiskriteeriumile.';

-- eis/model/testimine/testiprotokoll.py
COMMENT ON COLUMN testiprotokoll.id IS 'kirje identifikaator';
COMMENT ON COLUMN testiprotokoll.tahis IS 'protokollirühma tähis (01, 02, ...), unikaalne testikoha piires';
COMMENT ON COLUMN testiprotokoll.tahised IS 'testi, testiosa, testimiskorra, testikoha, testiprotokolli tähised, kriips vahel';
COMMENT ON COLUMN testiprotokoll.testipakett_id IS 'viide testipaketile (puudub e-testi korral)';
COMMENT ON COLUMN testiprotokoll.testiruum_id IS 'viide testiruumile';
COMMENT ON COLUMN testiprotokoll.kursus_kood IS 'valitud kursus, lai või kitsas (matemaatika korral), klassifikaator KURSUS';
COMMENT ON COLUMN testiprotokoll.toodearv IS 'sooritajate arv (arvutatakse koguste arvutamisel ja seal ka kuvatakse)';
COMMENT ON COLUMN testiprotokoll.tehtud_toodearv IS 'tehtud ja valimis olevate sooritajate arv (arvutatakse protokolli kinnitamisel)';
COMMENT ON COLUMN testiprotokoll.algus IS 'testi alguse kellaaeg protokollirühmas (kasutusel sisseastumiseksami korral)';
COMMENT ON COLUMN testiprotokoll.created IS 'kirje loomise aeg';
COMMENT ON COLUMN testiprotokoll.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN testiprotokoll.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN testiprotokoll.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE testiprotokoll IS 'Testiprotokollirühm';

-- eis/model/testimine/vaidefail.py
COMMENT ON COLUMN vaidefail.id IS 'kirje identifikaator';
COMMENT ON COLUMN vaidefail.filename IS 'failinimi';
COMMENT ON COLUMN vaidefail.filesize IS 'faili suurus';
COMMENT ON COLUMN vaidefail.fileversion IS 'versioon';
COMMENT ON COLUMN vaidefail.created IS 'kirje loomise aeg';
COMMENT ON COLUMN vaidefail.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN vaidefail.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN vaidefail.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE vaidefail IS 'Vaide juurde lisatud fail';

-- eis/model/testimine/toimumispaev.py
COMMENT ON COLUMN toimumispaev.id IS 'kirje identifikaator';
COMMENT ON COLUMN toimumispaev.toimumisaeg_id IS 'viide toimumisajale';
COMMENT ON COLUMN toimumispaev.seq IS 'toimumispäeva jrk nr toimumisajal (toimumise sessioon)';
COMMENT ON COLUMN toimumispaev.aeg IS 'testi kuupäev koos alguskellaga (kui kell on 00.00, siis kell puudub)';
COMMENT ON COLUMN toimumispaev.alustamise_lopp IS 'kellaaeg, millest varem peab sooritamist alustama (kui toimumisaeg.aja_jargi_alustatav=True)';
COMMENT ON COLUMN toimumispaev.lopp IS 'kellaaeg, millal hiljemalt peab sooritamine lõppema (isegi, kui piiraeg ei ole täis)';
COMMENT ON COLUMN toimumispaev.valim IS 'True - sellele ajale saab valimisse kuuluvaid sooritajaid suunata; False - sellele ajale ei või valimi sooritajaid suunata; None - sellel toimumisajal ei ole määratud valimi sooritajate aeg';
COMMENT ON COLUMN toimumispaev.created IS 'kirje loomise aeg';
COMMENT ON COLUMN toimumispaev.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN toimumispaev.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN toimumispaev.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE toimumispaev IS 'Toimumisaja kuupäev ja kellaaeg';

-- eis/model/testimine/sooritaja.py
COMMENT ON COLUMN sooritaja.id IS 'kirje identifikaator';
COMMENT ON COLUMN sooritaja.test_id IS 'viide testile';
COMMENT ON COLUMN sooritaja.testimiskord_id IS 'viide testimiskorrale (avaliku vaate testi korral puudub)';
COMMENT ON COLUMN sooritaja.kursus_kood IS 'valitud kursus, lai või kitsas (matemaatika korral), klassifikaator KURSUS';
COMMENT ON COLUMN sooritaja.nimekiri_id IS 'viide registreerimisnimekirjale';
COMMENT ON COLUMN sooritaja.klaster_id IS 'sooritamiseks määratud klaster';
COMMENT ON COLUMN sooritaja.staatus IS 'olek, soorituste madalaim olek, välja arvatud "registreeritud": 0=const.S_STAATUS_TYHISTATUD - tühistatud; 1=const.S_STAATUS_REGAMATA - registreerimata; 2=const.S_STAATUS_TASUMATA - tasumata; 3=const.S_STAATUS_REGATUD - registreeritud; 5=const.S_STAATUS_ALUSTAMATA - alustamata; 6=const.S_STAATUS_POOLELI - pooleli; 7=const.S_STAATUS_KATKESTATUD - ise katkestanud; 8=const.S_STAATUS_TEHTUD - tehtud; 9=const.S_STAATUS_EEMALDATUD - eemaldatud; 10=const.S_STAATUS_PUUDUS - puudus; 12=const.S_STAATUS_KATKESPROT - protokollil katkestanuks märgitud';
COMMENT ON COLUMN sooritaja.opetajatest IS 'kas on õpetaja test.sooritus (taustaküsitluse korral, kus nimekirjas on koos õpilaste küsitlused ja õpetaja küsitlus)';
COMMENT ON COLUMN sooritaja.reg_aeg IS 'registreerimise aeg';
COMMENT ON COLUMN sooritaja.regviis_kood IS 'registreerimisviis: 1=const.REGVIIS_SOORITAJA - ise EISi kaudu; 3=const.REGVIIS_KOOL_EIS - kool EISi kaudu; 4=const.REGVIIS_EKK - eksamikeskus; 5=const.REGVIIS_XTEE - ise eesti.ee portaali kaudu; 6=const.REGVIIS_EELVAADE - testi sooritamine eelvaates (ajutine kirje)';
COMMENT ON COLUMN sooritaja.reg_auto IS 'kas registreering jäi pooleli ja kinnitati Innove poolt automaatselt';
COMMENT ON COLUMN sooritaja.muutmatu IS 'NULL - kool saab registreeringut muuta ja kustutada; 1=const.MUUTMATU_TYHISTAMATU - kool saab registreeringut muuta, kuid ei saa kustutada; 2=const.MUUTMATU_MUUTMATU - kool ei saa registreeringut muuta ega kustutada';
COMMENT ON COLUMN sooritaja.vanem_nous IS 'vanema nõusolek (psühholoogilise testi korral)';
COMMENT ON COLUMN sooritaja.esitaja_kasutaja_id IS 'nimekirja esitaja';
COMMENT ON COLUMN sooritaja.esitaja_koht_id IS 'õppeasutus, nimekirja esitaja';
COMMENT ON COLUMN sooritaja.kasutaja_id IS 'viide.sooritaja kirjele';
COMMENT ON COLUMN sooritaja.eesnimi IS 'testi sooritamise ajal kehtinud eesnimi';
COMMENT ON COLUMN sooritaja.perenimi IS 'testi sooritamise ajal kehtinud perekonnanimi';
COMMENT ON COLUMN sooritaja.algus IS 'varaseima soorituse algus';
COMMENT ON COLUMN sooritaja.lang IS 'soorituskeel';
COMMENT ON COLUMN sooritaja.piirkond_id IS 'soovitud piirkond';
COMMENT ON COLUMN sooritaja.pallid IS 'testi eest saadud hindepallid, testi lõpptulemus pallides';
COMMENT ON COLUMN sooritaja.osapallid IS 'testiosade hindepallide summa (riigieksami korral võib see erineda lõpptulemusest, juhul kui.sooritaja on mõnest testiosast vabastatud)';
COMMENT ON COLUMN sooritaja.tulemus_protsent IS 'testiosade hindepallide summa protsentides.sooritaja suurimast võimalikust pallide summast';
COMMENT ON COLUMN sooritaja.tulemus_piisav IS 'kas test on sooritatud positiivselt (TE, SE korral saab väljastada tunnistuse)';
COMMENT ON COLUMN sooritaja.yhisosa_pallid IS 'testimiskordade ühisossa kuuluvate küsimuste eest saadud hindepallid';
COMMENT ON COLUMN sooritaja.hinne IS 'testi eest saadud hinne, vahemikus 1-5';
COMMENT ON COLUMN sooritaja.hindamine_staatus IS 'hindamise olek: 0=const.H_STAATUS_HINDAMATA - kõik testiosad hindamata; 1=const.H_STAATUS_POOLELI - mõni testiosa hindamisel; 6=const.H_STAATUS_HINNATUD - kõik testiosad hinnatud; 10=const.H_STAATUS_TOOPUUDU - töö puudub ja ei hinnata';
COMMENT ON COLUMN sooritaja.mujalt_tulemus IS 'kas testi kogutulemus on saadud mujalt (rv tunnistuselt) või liidab EIS testiosade tulemused kokku';
COMMENT ON COLUMN sooritaja.keeletase_kood IS 'eksamiga hinnatud keeleoskuse tase';
COMMENT ON COLUMN sooritaja.ajakulu IS 'kulutatud sekundite arv kõigi testiosade peale kokku';
COMMENT ON COLUMN sooritaja.tasu IS 'testi sooritamise eest tasutav summa';
COMMENT ON COLUMN sooritaja.tasutud IS 'kas on tasutud (NULL - pole tasuline, false - tasuline ja tasumata, true - tasuline ja tasutud)';
COMMENT ON COLUMN sooritaja.soovib_konsultatsiooni IS 'kas.sooritaja soovib konsultatsiooni';
COMMENT ON COLUMN sooritaja.markus IS 'märkused';
COMMENT ON COLUMN sooritaja.on_erivajadused IS 'kas on eritingimusi';
COMMENT ON COLUMN sooritaja.kontakt_nimi IS 'eritingimustega.sooritaja kontaktisiku nimi';
COMMENT ON COLUMN sooritaja.kontakt_epost IS 'eritingimustega.sooritaja kontaktisiku e-posti aadress';
COMMENT ON COLUMN sooritaja.regteateaeg IS 'viimati registreerimise teate saatmise aeg';
COMMENT ON COLUMN sooritaja.meeldetuletusaeg IS 'viimati meeldetuletuse (soorituskoha teate) aeg';
COMMENT ON COLUMN sooritaja.teavitatud_epost IS 'viimati tulemusest e-postiga teavitamise aeg';
COMMENT ON COLUMN sooritaja.teavitatud_sms IS 'viimati tulemusest SMSiga teavitamise aeg';
COMMENT ON COLUMN sooritaja.kool_koht_id IS 'viide.sooritaja õppeasutusele, kui sooritaja käib kuskil koolis';
COMMENT ON COLUMN sooritaja.koolinimi_id IS 'viide testi sooritamise ajal kehtinud õppimiskoha nime kirjele';
COMMENT ON COLUMN sooritaja.kool_aadress_kood1 IS 'õppimiskoha maakonna kood testi sooritamise ajal (statistika jaoks)';
COMMENT ON COLUMN sooritaja.kool_aadress_kood2 IS 'õppimiskoha omavalitsuse kood testi sooritamise ajal (statistika jaoks)';
COMMENT ON COLUMN sooritaja.kool_piirkond_id IS 'õppimiskoha piirkond testi sooritamise ajal (statistika jaoks)';
COMMENT ON COLUMN sooritaja.klass IS 'klass, milles õpib (statistika jaoks)';
COMMENT ON COLUMN sooritaja.paralleel IS 'paralleel, milles õpib (statistika jaoks)';
COMMENT ON COLUMN sooritaja.oppekeel IS 'õppekeele kood EHISe klassifikaatoris: E - eesti; I - inglise; D - saksa; S - soome; V - vene';
COMMENT ON COLUMN sooritaja.oppeaasta IS 'õppeaasta (kevade aasta), millal.sooritaja oli näidatud klassis (statistika jaoks)';
COMMENT ON COLUMN sooritaja.oppevorm_kood IS 'õppevorm, klassifikaator OPPEVORM (statistika jaoks)';
COMMENT ON COLUMN sooritaja.oppekava_kood IS 'õppekava EHISe klassifikaatoris (statistika jaoks)';
COMMENT ON COLUMN sooritaja.amet_muu IS 'amet (kui amet_kood on muu või kui pole klassifikaatorist valitud)';
COMMENT ON COLUMN sooritaja.tvaldkond_muu IS 'töövaldkond (kui tvaldkond_kood on muu)';
COMMENT ON COLUMN sooritaja.isikukaart_id IS 'EHISe isikukaardi ID (kui testimiskord.reg_piirang=H)';
COMMENT ON COLUMN sooritaja.haridus_kood IS 'sooritaja haridus, klassifikaator HARIDUS';
COMMENT ON COLUMN sooritaja.rahvus_kood IS 'rahvus (rahvusvahelise keeleeksami korral), klassifikaatorist';
COMMENT ON COLUMN sooritaja.synnikoht_kodakond_kood IS 'sünnikoha riik (rahvusvahelise keeleeksami korral), kodakondsuse klassifikaatorist';
COMMENT ON COLUMN sooritaja.synnikoht IS 'sünnikoha asula';
COMMENT ON COLUMN sooritaja.kodakond_kood IS 'sooritaja kodakondsus, klassifikaator KODAKOND (Statistikaameti riikide ja territooriumide klassifikaator RTK)';
COMMENT ON COLUMN sooritaja.ema_keel_kood IS 'emakeel (oli kuni 2017-10 rahvusvahelise vene keele eksami korral), keelte klassifikaatorist';
COMMENT ON COLUMN sooritaja.doknr IS 'passi või id-kaardi number (oli kuni 2017-10 rahvusvahelise vene keele eksami korral)';
COMMENT ON COLUMN sooritaja.oppimisaeg IS 'mitu aastat on keelt õppinud (oli kuni 2017-10 rahvusvahelise vene keele eksami korral)';
COMMENT ON COLUMN sooritaja.eesnimi_ru IS 'eesnimi vene keeles (rahvusvahelise vene keele eksami korral)';
COMMENT ON COLUMN sooritaja.perenimi_ru IS 'perekonnanimi vene keeles (rahvusvahelise vene keele eksami korral)';
COMMENT ON COLUMN sooritaja.valimis IS 'true - sooritaja on valimis (kui valim on eraldatud testimiskorra sees, mitte eraldi testimiskorraga)';
COMMENT ON COLUMN sooritaja.vabastet_kirjalikust IS 'kas soovib vabastust kirjalikust osast (B1 tasemeeksami korral, kui.sooritaja on vähemalt 65-aastane)';
COMMENT ON COLUMN sooritaja.tulemus_aeg IS 'tulemuse viimase muutmise aeg';
COMMENT ON COLUMN sooritaja.testiparool IS 'testiparooli räsi';
COMMENT ON COLUMN sooritaja.created IS 'kirje loomise aeg';
COMMENT ON COLUMN sooritaja.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN sooritaja.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN sooritaja.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE sooritaja IS 'Testi.sooritaja (registreerimisnimekirja kanne)';

-- eis/model/testimine/ylesandestatistika.py
COMMENT ON COLUMN ylesandestatistika.id IS 'kirje identifikaator';
COMMENT ON COLUMN ylesandestatistika.valitudylesanne_id IS 'viide testi valitud ülesandele, mille kohta statistika käib';
COMMENT ON COLUMN ylesandestatistika.ylesanne_id IS 'viide ülesandele, mille kohta statistika käib';
COMMENT ON COLUMN ylesandestatistika.tkorraga IS 'kas on testimiskorraga soorituste statistika (või avaliku testi statistika)';
COMMENT ON COLUMN ylesandestatistika.valimis IS 'NULL - valim ja mitte-valim koos; true - valimi statistika; false - mitte-valimi statistika';
COMMENT ON COLUMN ylesandestatistika.toimumisaeg_id IS 'viide toimumisajale (testimiskorraga testi statistika korral)';
COMMENT ON COLUMN ylesandestatistika.testiruum_id IS 'viide nimekirjale (avaliku vaate testi statistika korral)';
COMMENT ON COLUMN ylesandestatistika.testikoht_id IS 'viide soorituskohale';
COMMENT ON COLUMN ylesandestatistika.kool_koht_id IS 'viide õppimiskohale';
COMMENT ON COLUMN ylesandestatistika.sooritajate_arv IS 'sooritajate arv';
COMMENT ON COLUMN ylesandestatistika.keskmine IS 'keskmine tulemus toorpunktides';
COMMENT ON COLUMN ylesandestatistika.lahendatavus IS 'keskmine lahendusprotsent, keskmise tulemuse ja maksimaalse võimaliku tulemuse suhe protsentides (EIS arvutab)';
COMMENT ON COLUMN ylesandestatistika.rit IS 'korrelatsioonikordaja ülesande punktide ja testi kogutulemuse vahel, ülesande eristusjõu näitaja: corr(yv.pallid, sooritaja.pallid)';
COMMENT ON COLUMN ylesandestatistika.rir IS 'korrelatsioonikordaja ülesande punktide ja testi ülejäänud ülesannete punktide vahel: corr(yv.pallid, sooritaja.pallid-yv.pallid)';
COMMENT ON COLUMN ylesandestatistika.aeg_avg IS 'keskmine lahendusaeg sekundites (koolipsühholoogi testi korral)';
COMMENT ON COLUMN ylesandestatistika.aeg_min IS 'min lahendusaeg sekundites (koolipsühholoogi testi korral)';
COMMENT ON COLUMN ylesandestatistika.aeg_max IS 'max lahendusaeg sekundites (koolipsühholoogi testi korral)';
COMMENT ON COLUMN ylesandestatistika.created IS 'kirje loomise aeg';
COMMENT ON COLUMN ylesandestatistika.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN ylesandestatistika.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN ylesandestatistika.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE ylesandestatistika IS 'Ülesande statistika toimumisaja piires.';

-- eis/model/kasutaja/ainelabiviija.py
COMMENT ON COLUMN ainelabiviija.id IS 'kirje identifikaator';
COMMENT ON COLUMN ainelabiviija.profiil_id IS 'viide kasutaja profiilile';
COMMENT ON COLUMN ainelabiviija.aine_kood IS 'viide õppeainele, klassifikaator AINE';
COMMENT ON COLUMN ainelabiviija.tahis IS 'läbiviija tähis antud aines, unikaalne aine piires';
COMMENT ON COLUMN ainelabiviija.created IS 'kirje loomise aeg';
COMMENT ON COLUMN ainelabiviija.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN ainelabiviija.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN ainelabiviija.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE ainelabiviija IS 'Kasutaja konkreetses aines testi läbiviijana rakendamise tähis';

-- eis/model/kasutaja/labiviijaleping.py
COMMENT ON COLUMN leping.id IS 'kirje identifikaator';
COMMENT ON COLUMN leping.testsessioon_id IS 'viide testsessioonile';
COMMENT ON COLUMN leping.nimetus IS 'lepingu nimetus';
COMMENT ON COLUMN leping.url IS 'link lepingu teksti PDFile Innove veebis';
COMMENT ON COLUMN leping.sessioonita IS 'kas leping sõlmitakse testsessiooniüleselt';
COMMENT ON COLUMN leping.yldleping IS 'kas leping on üldine teenuste leping, mis ei lähe akti (kuni 2020)';
COMMENT ON COLUMN leping.aasta_alates IS 'õppeaasta, alates';
COMMENT ON COLUMN leping.aasta_kuni IS 'õppeaasta, kuni';
COMMENT ON COLUMN leping.created IS 'kirje loomise aeg';
COMMENT ON COLUMN leping.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN leping.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN leping.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE leping IS 'Testide läbiviijatega sõlmitavate lepingute liigid';

COMMENT ON COLUMN lepinguroll.id IS 'kirje identifikaator';
COMMENT ON COLUMN lepinguroll.leping_id IS 'viide lepingule';
COMMENT ON COLUMN lepinguroll.kasutajagrupp_id IS 'roll';
COMMENT ON COLUMN lepinguroll.aine_kood IS 'õppeaine, klassifikaator AINE';
COMMENT ON COLUMN lepinguroll.testiliik_kood IS 'testi liik, klassifikaator TESTILIIK';
COMMENT ON COLUMN lepinguroll.created IS 'kirje loomise aeg';
COMMENT ON COLUMN lepinguroll.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN lepinguroll.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN lepinguroll.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE lepinguroll IS 'Rollid, mille jaoks leping sõlmitakse';

COMMENT ON COLUMN labiviijaleping.id IS 'kirje identifikaator';
COMMENT ON COLUMN labiviijaleping.kasutaja_id IS 'viide kasutajale';
COMMENT ON COLUMN labiviijaleping.testsessioon_id IS 'viide testsessioonile';
COMMENT ON COLUMN labiviijaleping.leping_id IS 'viide lepingule';
COMMENT ON COLUMN labiviijaleping.noustunud IS 'lepinguga nõustumise aeg';
COMMENT ON COLUMN labiviijaleping.on_hindaja3 IS 'kas on nõus osalema kolmanda hindajana';
COMMENT ON COLUMN labiviijaleping.created IS 'kirje loomise aeg';
COMMENT ON COLUMN labiviijaleping.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN labiviijaleping.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN labiviijaleping.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE labiviijaleping IS 'Testide läbiviija nõusolek testsessiooni ja rolliga seotud lepingu tingimustega';

COMMENT ON COLUMN testileping.id IS 'kirje identifikaator';
COMMENT ON COLUMN testileping.testimiskord_id IS 'viide testimiskorrale';
COMMENT ON COLUMN testileping.leping_id IS 'viide lepingule';
COMMENT ON COLUMN testileping.kasutajagrupp_id IS 'läbiviija roll, mille korral leping on vajalik';
COMMENT ON COLUMN testileping.created IS 'kirje loomise aeg';
COMMENT ON COLUMN testileping.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN testileping.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN testileping.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE testileping IS 'Testimiskorra seos lepingutega, mis on testimiskorra läbiviimiseks vajalikud';

-- eis/model/kasutaja/kasutaja.py
COMMENT ON COLUMN kasutaja.id IS 'kirje identifikaator';
COMMENT ON COLUMN kasutaja.isikukood IS 'isikukood (Eesti isikukood ilma riigi koodita, teiste riikide korral ees riigi ISO2 kood)';
COMMENT ON COLUMN kasutaja.synnikpv IS 'sünnikuupäev';
COMMENT ON COLUMN kasutaja.eesnimi IS 'eesnimi';
COMMENT ON COLUMN kasutaja.perenimi IS 'perekonnanimi';
COMMENT ON COLUMN kasutaja.nimi IS 'ees- ja perekonnanimi (otsingute lihtsustamiseks)';
COMMENT ON COLUMN kasutaja.parool IS 'püsiparooli räsi';
COMMENT ON COLUMN kasutaja.muuda_parool IS 'pannakse True siis, kui parooli seab ametnik (mitte kasutaja ise); kui on True, siis sisselogimisel soovitatakse parooli muutma ja pannakse False (ka siis, kui kasutaja parooli ei muutnud)';
COMMENT ON COLUMN kasutaja.epost IS 'e-posti aadress';
COMMENT ON COLUMN kasutaja.epost_seisuga IS 'millal viimati kasutajalt e-posti aadress üle küsiti';
COMMENT ON COLUMN kasutaja.aadress_id IS 'viide aadressile';
COMMENT ON COLUMN kasutaja.postiindeks IS 'postiindeks';
COMMENT ON COLUMN kasutaja.normimata IS 'normaliseerimata aadress - vabatekstiliselt sisestatud aadressi lõpp, mida ei olnud võimalik sisestada ADSi komponentide klassifikaatori abil';
COMMENT ON COLUMN kasutaja.telefon IS 'telefon';
COMMENT ON COLUMN kasutaja.sugu IS 'sugu (M,N) statistika jaoks, võetakse isikukoodist';
COMMENT ON COLUMN kasutaja.staatus IS 'olek: 1 - aktiivne, 0 - kehtetu';
COMMENT ON COLUMN kasutaja.on_ametnik IS 'kas kasutaja on eksamikeskuse vaate kasutaja (kaasneb EKK vaate kasutaja roll, kehtivuse kuupäev on rolli juures)';
COMMENT ON COLUMN kasutaja.on_labiviija IS 'kas kasutaja on testide läbiviimisega seotud isik';
COMMENT ON COLUMN kasutaja.uiroll IS 'vaikimisi roll avalikus vaates: S=const.UIROLL_S - testisooritaja; K=const.UIROLL_K - kool (õpetaja või admin); P=const.UIROLL_P - koolipsühholoog';
COMMENT ON COLUMN kasutaja.koht_id IS 'vaikimisi koht avalikus vaates (0 - sooritaja)';
COMMENT ON COLUMN kasutaja.ametikoht_seisuga IS 'aeg, millal viimati uuendati EHISest pedagoogi ametikohti (juhul, kui EHISe päring õnnestus)';
COMMENT ON COLUMN kasutaja.ametikoht_proovitud IS 'aeg, millal viimati prooviti uuendada EHISest pedagoogi ametikohti (ka siis, kui päringu sooritamine ebaõnnestus)';
COMMENT ON COLUMN kasutaja.opilane_seisuga IS 'aeg, millal viimati uuendati EHISest õpilase andmeid (erineb tabeli Opilane seisust selle poolest, et mitte-õpilastel ei ole tabeli Opilane kirjet)';
COMMENT ON COLUMN kasutaja.isikukaart_seisuga IS 'aeg, millal viimati uuendati EHISest töötamise andmeid';
COMMENT ON COLUMN kasutaja.isikukaart_id IS 'viide viimasele isikukaardile';
COMMENT ON COLUMN kasutaja.rr_seisuga IS 'aeg, millal viimati uuendati isikuandmed Rahvastikuregistrist';
COMMENT ON COLUMN kasutaja.session_id IS 'viimase Innove vaate seansi id (beaker_cache.namespace, request.session.id)';
COMMENT ON COLUMN kasutaja.viimati_ekk IS 'millal viimati Innove vaatesse logis';
COMMENT ON COLUMN kasutaja.tunnistus_nr IS 'keskharidust tõendava tunnistuse nr';
COMMENT ON COLUMN kasutaja.tunnistus_kp IS 'keskharidust tõendava dokumendi väljastamise kuupäev';
COMMENT ON COLUMN kasutaja.lopetanud IS 'kas on täidetud lõpetamise tingimused (EISi kontrollitud)';
COMMENT ON COLUMN kasutaja.lopetanud_kasitsi IS 'kas on täidetud lõpetamise tingimused (käsitsi märgitud)';
COMMENT ON COLUMN kasutaja.lopetanud_pohjus IS 'lõpetamise tingimuste täidetuse käsitsi märkimise põhjus';
COMMENT ON COLUMN kasutaja.lopetamisaasta IS 'eeldatav keskhariduse lõpetamise aasta (lõpetamise tingimuste täidetuse kontrolli jaoks)';
COMMENT ON COLUMN kasutaja.kool_koht_id IS 'keskhariduse omandamise kool';
COMMENT ON COLUMN kasutaja.kool_nimi IS 'lõpetatud keskhariduse kooli nimi';
COMMENT ON COLUMN kasutaja.oppekeel IS 'õppekeele kood EHISe klassifikaatoris: E - eesti; I - inglise; D - saksa; S - soome; V - vene';
COMMENT ON COLUMN kasutaja.kodakond_kood IS 'sooritaja kodakondsus, klassifikaator KODAKOND (Statistikaameti riikide ja territooriumide klassifikaator RTK)';
COMMENT ON COLUMN kasutaja.synnikoht IS 'sünnikoht RRis (rahvusvahelise DELF prantsuse keele eksami jaoks, saadakse RRist, ise ei sisestata)';
COMMENT ON COLUMN kasutaja.lisatingimused IS 'sooritaja lisatingimused';
COMMENT ON COLUMN kasutaja.markus IS 'märkused kasutaja kohta';
COMMENT ON COLUMN kasutaja.bgcolor IS 'kasutajaliidese värv';
COMMENT ON COLUMN kasutaja.created IS 'kirje loomise aeg';
COMMENT ON COLUMN kasutaja.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN kasutaja.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN kasutaja.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE kasutaja IS 'Kasutajakontod';

-- eis/model/kasutaja/opilane.py
COMMENT ON COLUMN opilane.id IS 'kirje identifikaator';
COMMENT ON COLUMN opilane.isikukood IS 'isikukood';
COMMENT ON COLUMN opilane.kasutaja_id IS 'viide kasutaja kirjele';
COMMENT ON COLUMN opilane.eesnimi IS 'eesnimi';
COMMENT ON COLUMN opilane.perenimi IS 'perekonnanimi';
COMMENT ON COLUMN opilane.koht_id IS 'õppeasutus';
COMMENT ON COLUMN opilane.kool_id IS 'EHISe kooli id';
COMMENT ON COLUMN opilane.klass IS 'klass';
COMMENT ON COLUMN opilane.paralleel IS 'paralleel';
COMMENT ON COLUMN opilane.ryhm_id IS 'viide lasteaiarühmale';
COMMENT ON COLUMN opilane.oppekeel IS 'õppekeele kood EHISe klassifikaatoris: E - eesti; I - inglise; D - saksa; S - soome; V - vene';
COMMENT ON COLUMN opilane.lang IS 'õppekeelele vastav EISi soorituskeel';
COMMENT ON COLUMN opilane.sugu IS 'sugu (M,N)';
COMMENT ON COLUMN opilane.synnikpv IS 'sünnikuupäev';
COMMENT ON COLUMN opilane.oppevorm_kood IS 'õppevorm, klassifikaator OPPEVORM';
COMMENT ON COLUMN opilane.oppekava_kood IS 'õppekava EHISe klassifikaatoris (kutseharidus nagu meie klassifikaator KAVATASE, üldharidus erineb)';
COMMENT ON COLUMN opilane.on_lopetanud IS 'kas on keskhariduse omandanud';
COMMENT ON COLUMN opilane.lopetamisaasta IS 'keskhariduse omandamise aasta';
COMMENT ON COLUMN opilane.tunnistus_nr IS 'keskharidust tõendava tunnistuse nr';
COMMENT ON COLUMN opilane.tunnistus_kp IS 'keskharidust tõendava tunnistuse kuupäev';
COMMENT ON COLUMN opilane.seisuga IS 'viimane EHISest andmete kontrollimise aeg';
COMMENT ON COLUMN opilane.on_ehisest IS 'kas andmed on pärit EHISest (kui pole, siis seda kirjet EHISe päringu tulemuse põhjal ei kustutata)';
COMMENT ON COLUMN opilane.prioriteet IS 'kui EHISe andmetel õpib isik korraga mitmes koolis, siis registreeringute juurde märgitakse kõrgema prioriteediga kool (vaikimisi NULL, üldhariduskooli korral 1, käsitsi saab panna 2)';
COMMENT ON COLUMN opilane.created IS 'kirje loomise aeg';
COMMENT ON COLUMN opilane.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN opilane.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN opilane.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE opilane IS 'Õppurite andmed, kopeeritakse EHISest';

-- eis/model/kasutaja/opperyhmaliige.py
COMMENT ON COLUMN opperyhmaliige.id IS 'kirje identifikaator';
COMMENT ON COLUMN opperyhmaliige.opperyhm_id IS 'rühm';
COMMENT ON COLUMN opperyhmaliige.kasutaja_id IS 'õpilane';
COMMENT ON COLUMN opperyhmaliige.created IS 'kirje loomise aeg';
COMMENT ON COLUMN opperyhmaliige.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN opperyhmaliige.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN opperyhmaliige.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE opperyhmaliige IS 'Õpilaste rühma liige';

-- eis/model/kasutaja/teavitustellimus.py
COMMENT ON COLUMN teavitustellimus.id IS 'kirje identifikaator';
COMMENT ON COLUMN teavitustellimus.kasutaja_id IS 'viide kasutajale';
COMMENT ON COLUMN teavitustellimus.teatekanal IS 'tellimuse kanal: 3=const.TEATEKANAL_KALENDER - eesti.ee teavituskalendri kaudu';
COMMENT ON COLUMN teavitustellimus.syndmuseliik IS 'testiliigi kood, millele vastavad sündmused on tellitud (teavituskalendri korral)';
COMMENT ON COLUMN teavitustellimus.created IS 'kirje loomise aeg';
COMMENT ON COLUMN teavitustellimus.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN teavitustellimus.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN teavitustellimus.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE teavitustellimus IS 'Kasutaja poolt tellitud teavitusviisid eesti.ee vanas teavituskalendris
    (uuelt me ei saa enam seda infot küsida)';

-- eis/model/kasutaja/legacy.py
COMMENT ON COLUMN legacy.id IS 'kirje identifikaator';
COMMENT ON COLUMN legacy.kood IS 'genereeritud juhuarv, mille seostab URLi kirjega';
COMMENT ON COLUMN legacy.risikukood IS 'riik ja isikukood, X-tee päisevälja userId väärtus';
COMMENT ON COLUMN legacy.eesnimi IS 'X-tee päisevälja userName algus kuni viimase tühikuni';
COMMENT ON COLUMN legacy.perenimi IS 'X-tee päisevälja userName lõpp alates viimasest tühikust';
COMMENT ON COLUMN legacy.aeg IS 'aeg';
COMMENT ON COLUMN legacy.param IS 'testiliik, kui on vaja suunata kindla testiliigi regamisele';
COMMENT ON COLUMN legacy.created IS 'kirje loomise aeg';
COMMENT ON COLUMN legacy.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN legacy.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN legacy.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE legacy IS '';

-- eis/model/kasutaja/makse.py
COMMENT ON COLUMN makse.id IS 'kirje identifikaator';
COMMENT ON COLUMN makse.kasutaja_id IS 'viide kasutajale';
COMMENT ON COLUMN makse.stamp IS 'päringu ID, VK_STAMP';
COMMENT ON COLUMN makse.msg IS 'mille eest maksti, VK_MSG';
COMMENT ON COLUMN makse.amount IS 'kui palju maksti, VK_AMOUNT';
COMMENT ON COLUMN makse.saadud IS 'kas pangast on vastus saadud';
COMMENT ON COLUMN makse.created IS 'kirje loomise aeg';
COMMENT ON COLUMN makse.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN makse.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN makse.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE makse IS 'Pangalingi maksed';

-- eis/model/kasutaja/sooritajakiri.py
COMMENT ON COLUMN sooritajakiri.id IS 'kirje identifikaator';
COMMENT ON COLUMN sooritajakiri.kiri_id IS 'viide kirjale';
COMMENT ON COLUMN sooritajakiri.sooritaja_id IS 'viide sooritaja kirjele, kui on registreeringuga seotud kiri';
COMMENT ON COLUMN sooritajakiri.created IS 'kirje loomise aeg';
COMMENT ON COLUMN sooritajakiri.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN sooritajakiri.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN sooritajakiri.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE sooritajakiri IS 'Sooritaja kirje seos välja saadetud kirjadega';

-- eis/model/kasutaja/pedagoog.py
COMMENT ON COLUMN pedagoog.id IS 'kirje identifikaator';
COMMENT ON COLUMN pedagoog.isikukood IS 'isikukood';
COMMENT ON COLUMN pedagoog.kasutaja_id IS 'kasutaja';
COMMENT ON COLUMN pedagoog.eesnimi IS 'eesnimi';
COMMENT ON COLUMN pedagoog.perenimi IS 'perekonnanimi';
COMMENT ON COLUMN pedagoog.koht_id IS 'õppeasutus (puudub siis, kui EISis on koolide andmed uuendamata ja vahepeal on EHISesse uus kool lisatud';
COMMENT ON COLUMN pedagoog.kool_id IS 'kooli ID EHISes (puudub siis, kui kool ei ole EHISes - seda võib juhtuda ainult juhul, kui ka töötamise andmed ei ole võetud EHISest, vaid sisestatud käsitsi)';
COMMENT ON COLUMN pedagoog.seisuga IS 'viimane EHISest andmete kontrollimise aeg (sellise päringuga, mis ei tehtud kindla kooliastme ega õppeaine järgi)';
COMMENT ON COLUMN pedagoog.kehtib_kuni IS 'rolli kehtivuse lõppkuupäev (EISis käsitsi lisatud rolli korral)';
COMMENT ON COLUMN pedagoog.kasutajagrupp_id IS 'viide kasutajagrupile: 56=const.GRUPP_K_JUHT - koolijuht (soorituskoha admin, foreign_keys=kasutajagrupp_id); 25=const.GRUPP_OPETAJA - tavaline õpetaja';
COMMENT ON COLUMN pedagoog.on_ehisest IS 'kas andmed on pärit EHISest (kui pole, siis seda kirjet EHISe päringu tulemuse põhjal ei kustutata)';
COMMENT ON COLUMN pedagoog.created IS 'kirje loomise aeg';
COMMENT ON COLUMN pedagoog.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN pedagoog.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN pedagoog.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE pedagoog IS 'Õppeasutuste töötajate andmed, kopeeritakse EHISest';

-- eis/model/kasutaja/kasutajaajalugu.py
COMMENT ON COLUMN kasutajaajalugu.id IS 'kirje identifikaator';
COMMENT ON COLUMN kasutajaajalugu.kasutaja_id IS 'viide kasutajale';
COMMENT ON COLUMN kasutajaajalugu.created IS 'kirje loomise aeg';
COMMENT ON COLUMN kasutajaajalugu.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN kasutajaajalugu.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN kasutajaajalugu.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE kasutajaajalugu IS 'Kasutajale paroolide andmise ajalugu';

-- eis/model/kasutaja/kasutajaoigus.py
COMMENT ON COLUMN kasutajaoigus.id IS 'kirje identifikaator';
COMMENT ON COLUMN kasutajaoigus.nimi IS 'õiguse nimi ehk kood';
COMMENT ON COLUMN kasutajaoigus.kirjeldus IS 'õiguse kirjeldus';
COMMENT ON COLUMN kasutajaoigus.created IS 'kirje loomise aeg';
COMMENT ON COLUMN kasutajaoigus.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN kasutajaoigus.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN kasutajaoigus.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE kasutajaoigus IS 'Kasutajaõigus (kasutajagrupile antud õigus)';

-- eis/model/kasutaja/labiviijakiri.py
COMMENT ON COLUMN labiviijakiri.id IS 'kirje identifikaator';
COMMENT ON COLUMN labiviijakiri.kiri_id IS 'viide kirjale';
COMMENT ON COLUMN labiviijakiri.labiviija_id IS 'viide läbiviija kirjele';
COMMENT ON COLUMN labiviijakiri.created IS 'kirje loomise aeg';
COMMENT ON COLUMN labiviijakiri.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN labiviijakiri.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN labiviijakiri.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE labiviijakiri IS 'Läbiviija kirje seos välja saadetud kirjadega';

-- eis/model/kasutaja/tyyptekst.py
COMMENT ON COLUMN tyyptekst.id IS 'kirje identifikaator';
COMMENT ON COLUMN tyyptekst.tyyp IS 'kirja tüüp (vt Kiri.TYYP_*)';
COMMENT ON COLUMN tyyptekst.teema IS 'kirja teema';
COMMENT ON COLUMN tyyptekst.sisu IS 'kirja sisu';
COMMENT ON COLUMN tyyptekst.created IS 'kirje loomise aeg';
COMMENT ON COLUMN tyyptekst.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN tyyptekst.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN tyyptekst.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE tyyptekst IS 'Kirjade tüüptekstid';

-- eis/model/kasutaja/kasutajaprotsess.py
COMMENT ON COLUMN kasutajaprotsess.id IS 'kirje identifikaator';
COMMENT ON COLUMN kasutajaprotsess.kasutaja_id IS 'seos kasutajaga';
COMMENT ON COLUMN kasutajaprotsess.arvutusprotsess_id IS 'seos arvutusprotsessiga';
COMMENT ON COLUMN kasutajaprotsess.created IS 'kirje loomise aeg';
COMMENT ON COLUMN kasutajaprotsess.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN kasutajaprotsess.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN kasutajaprotsess.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE kasutajaprotsess IS 'Sooritaja seos registreerimise arvutusprotsessiga';

-- eis/model/kasutaja/kasutajakoht.py
COMMENT ON COLUMN kasutajakoht.id IS 'kirje identifikaator';
COMMENT ON COLUMN kasutajakoht.kasutaja_id IS 'viide kasutajale';
COMMENT ON COLUMN kasutajakoht.koht_id IS 'viide soorituskohale';
COMMENT ON COLUMN kasutajakoht.created IS 'kirje loomise aeg';
COMMENT ON COLUMN kasutajakoht.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN kasutajakoht.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN kasutajakoht.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE kasutajakoht IS 'Kasutajaga seotud soorituskohad (kus kasutaja on hindajate, korraldajate jne kiirvalikus)';

-- eis/model/kasutaja/kiri.py
COMMENT ON COLUMN kiri.id IS 'kirje identifikaator';
COMMENT ON COLUMN kiri.saatja_kasutaja_id IS 'viide kasutajale, kes algatas saatmise';
COMMENT ON COLUMN kiri.tyyp IS 'kirja tüüp';
COMMENT ON COLUMN kiri.teema IS 'kirja teema';
COMMENT ON COLUMN kiri.sisu IS 'kirja sisu (võib puududa paberkirja korral)';
COMMENT ON COLUMN kiri.filename IS 'manuse failinimi';
COMMENT ON COLUMN kiri.filedata IS 'manuse faili sisu';
COMMENT ON COLUMN kiri.sisu_url IS 'teatega kaasa saadetud URL (StateOS)';
COMMENT ON COLUMN kiri.teatekanal IS 'kirja saatmise viis: 1=const.TEATEKANAL_EPOST - e-posti teel; 2=const.TEATEKANAL_POST - posti teel; 3=const.TEATEKANAL_KALENDER - eesti.ee teavituskalendri kaudu; 4=const.TEATEKANAL_STATEOS - StateOS kaudu (kuni 31.03.2023); 5=const.TEATEKANAL_EIS - ainult EISis';
COMMENT ON COLUMN kiri.created IS 'kirje loomise aeg';
COMMENT ON COLUMN kiri.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN kiri.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN kiri.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE kiri IS 'Välja saadetud kirjad (teated)';

-- eis/model/kasutaja/isikukaart.py
COMMENT ON COLUMN isikukaart.id IS 'kirje identifikaator';
COMMENT ON COLUMN isikukaart.isikukood IS 'isikukood';
COMMENT ON COLUMN isikukaart.data IS 'isikukaardi päringu vastus JSONina';
COMMENT ON COLUMN isikukaart.created IS 'kirje loomise aeg';
COMMENT ON COLUMN isikukaart.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN isikukaart.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN isikukaart.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE isikukaart IS 'EHISe isikukaart';

COMMENT ON COLUMN isikukaart_too.id IS 'kirje identifikaator';
COMMENT ON COLUMN isikukaart_too.isikukaart_id IS 'viide isikukaardi kirjele';
COMMENT ON COLUMN isikukaart_too.liik IS 'haridustase (HUVIKOOL, POHIKOOL, ...)';
COMMENT ON COLUMN isikukaart_too.oppeasutus IS 'õppeasutus';
COMMENT ON COLUMN isikukaart_too.oppeasutus_id IS 'õppeasutuse EHIS ID';
COMMENT ON COLUMN isikukaart_too.ametikoht IS 'ametikoht';
COMMENT ON COLUMN isikukaart_too.ametikoht_algus IS 'töötamise algus';
COMMENT ON COLUMN isikukaart_too.ametikoht_lopp IS 'töötamise lõpp';
COMMENT ON COLUMN isikukaart_too.on_tunniandja IS 'on tunniandja';
COMMENT ON COLUMN isikukaart_too.on_oppejoud IS 'on õppejõud';
COMMENT ON COLUMN isikukaart_too.taitmise_viis IS 'ametikoha täitmise viis';
COMMENT ON COLUMN isikukaart_too.ametikoht_koormus IS 'koormus';
COMMENT ON COLUMN isikukaart_too.tooleping IS 'tööleping';
COMMENT ON COLUMN isikukaart_too.ametikoht_kval_vastavus IS 'kvalifikatsiooninõuetele vastavus';
COMMENT ON COLUMN isikukaart_too.ametijark IS 'ametijärk';
COMMENT ON COLUMN isikukaart_too.haridustase IS 'omandatud haridustase';
COMMENT ON COLUMN isikukaart_too.lapsehooldus_puhkus IS 'lapsehoolduspuhkusel';
COMMENT ON COLUMN isikukaart_too.created IS 'kirje loomise aeg';
COMMENT ON COLUMN isikukaart_too.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN isikukaart_too.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN isikukaart_too.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE isikukaart_too IS 'EHISe isikukaardi töötamise kirje';

COMMENT ON COLUMN isikukaart_too_oppekava.id IS 'kirje identifikaator';
COMMENT ON COLUMN isikukaart_too_oppekava.isikukaart_too_id IS 'viide isikukaardi töötamise kirjele';
COMMENT ON COLUMN isikukaart_too_oppekava.kl_oppekava IS 'õppekava klassifikaator';
COMMENT ON COLUMN isikukaart_too_oppekava.oppekava_kood IS 'kood';
COMMENT ON COLUMN isikukaart_too_oppekava.oppekava_nimetus IS 'nimetus';
COMMENT ON COLUMN isikukaart_too_oppekava.kvalifikatsiooni_vastavus IS 'kvalifikatsiooni vastavus kehtivas raamistikus';
COMMENT ON COLUMN isikukaart_too_oppekava.akad_kraad IS 'akadeemiline kraad või diplom';
COMMENT ON COLUMN isikukaart_too_oppekava.kval_dokument IS 'kvalifikatsiooni dokument';
COMMENT ON COLUMN isikukaart_too_oppekava.created IS 'kirje loomise aeg';
COMMENT ON COLUMN isikukaart_too_oppekava.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN isikukaart_too_oppekava.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN isikukaart_too_oppekava.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE isikukaart_too_oppekava IS 'EHISe isikukaardi töötamise õppekava kirje';

COMMENT ON COLUMN isikukaart_too_oppeaine.id IS 'kirje identifikaator';
COMMENT ON COLUMN isikukaart_too_oppeaine.isikukaart_too_id IS 'viide isikukaardi töötamise kirjele';
COMMENT ON COLUMN isikukaart_too_oppeaine.oppeaine IS 'õppeaine';
COMMENT ON COLUMN isikukaart_too_oppeaine.kooliaste IS 'kooliaste';
COMMENT ON COLUMN isikukaart_too_oppeaine.maht IS 'koormus õppeaineti';
COMMENT ON COLUMN isikukaart_too_oppeaine.kval_vastavus IS 'kvalifikatsiooninõuetele vastavus';
COMMENT ON COLUMN isikukaart_too_oppeaine.created IS 'kirje loomise aeg';
COMMENT ON COLUMN isikukaart_too_oppeaine.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN isikukaart_too_oppeaine.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN isikukaart_too_oppeaine.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE isikukaart_too_oppeaine IS 'EHISe isikukaardi töötamise õppeaine kirje';

-- eis/model/kasutaja/kirjasaaja.py
COMMENT ON COLUMN kirjasaaja.id IS 'kirje identifikaator';
COMMENT ON COLUMN kirjasaaja.kiri_id IS 'viide kirjale';
COMMENT ON COLUMN kirjasaaja.kasutaja_id IS 'viide saaja kasutajale (puudub soorituskohale saadetud kirjas)';
COMMENT ON COLUMN kirjasaaja.epost IS 'e-posti aadress';
COMMENT ON COLUMN kirjasaaja.isikukood IS 'isikukood (StateOS)';
COMMENT ON COLUMN kirjasaaja.staatus IS 'kirja olek: 1=const.KIRI_UUS - lugemata; 2=const.KIRI_LOETUD - loetud; 3=const.KIRI_ARHIIV - arhiveeritud';
COMMENT ON COLUMN kirjasaaja.koht_id IS 'viide soorituskohale, kuhu kiri saadeti';
COMMENT ON COLUMN kirjasaaja.toimumisaeg_id IS 'viide toimumisajale';
COMMENT ON COLUMN kirjasaaja.created IS 'kirje loomise aeg';
COMMENT ON COLUMN kirjasaaja.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN kirjasaaja.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN kirjasaaja.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE kirjasaaja IS 'Kirja saaja';

-- eis/model/kasutaja/kasutajagrupp.py
COMMENT ON COLUMN kasutajagrupp.id IS 'kirje identifikaator';
COMMENT ON COLUMN kasutajagrupp.nimi IS 'grupi nimi';
COMMENT ON COLUMN kasutajagrupp.kirjeldus IS 'kirjeldus';
COMMENT ON COLUMN kasutajagrupp.tyyp IS 'grupi tüüp: 1=const.USER_TYPE_EKK - eksamikeskuse kasutaja; 2=const.USER_TYPE_Y - grupp isiku sidumiseks ülesandega; 3=const.USER_TYPE_T - grupp isiku sidumiseks testiga; 4=const.USER_TYPE_KOOL - soorituskoha kasutaja; 5=const.USER_TYPE_AV - EKK vaate avalik kasutaja';
COMMENT ON COLUMN kasutajagrupp.staatus IS 'olek: 1 - kehtib; 0 - kehtetu';
COMMENT ON COLUMN kasutajagrupp.max_koormus IS 'maksimaalne kasutajate arv, mille korral selle grupi kasutajal lubatakse sisse logida';
COMMENT ON COLUMN kasutajagrupp.created IS 'kirje loomise aeg';
COMMENT ON COLUMN kasutajagrupp.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN kasutajagrupp.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN kasutajagrupp.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE kasutajagrupp IS 'Kasutajagrupp';

-- eis/model/kasutaja/klass.py
COMMENT ON COLUMN klass.id IS 'kirje identifikaator';
COMMENT ON COLUMN klass.kool_id IS 'EHISe kooli id';
COMMENT ON COLUMN klass.klass IS 'klass';
COMMENT ON COLUMN klass.paralleel IS 'paralleel';
COMMENT ON COLUMN klass.seisuga IS 'viimane EHISest andmete kontrollimise aeg';
COMMENT ON COLUMN klass.created IS 'kirje loomise aeg';
COMMENT ON COLUMN klass.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN klass.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN klass.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE klass IS 'Klassi andmete uuendamise seis';

-- eis/model/kasutaja/kasutajaroll.py
COMMENT ON COLUMN kasutajaroll.id IS 'kirje identifikaator';
COMMENT ON COLUMN kasutajaroll.kasutaja_id IS 'viide kasutajale';
COMMENT ON COLUMN kasutajaroll.kasutajagrupp_id IS 'viide kasutajagrupile';
COMMENT ON COLUMN kasutajaroll.koht_id IS 'viide soorituskohale, kus kasutajagurupp kehtib';
COMMENT ON COLUMN kasutajaroll.piirkond_id IS 'viide piirkonnale, kus kasutajagrupp kehtib';
COMMENT ON COLUMN kasutajaroll.aine_kood IS 'viide õppeainele, milles kasutajagrupp kehtib, klassifikaator AINE';
COMMENT ON COLUMN kasutajaroll.oskus_kood IS 'viide osaoskusele, milles kasutajagrupp kehtib, klassifikaator OSKUS';
COMMENT ON COLUMN kasutajaroll.testiliik_kood IS 'viide testiliigile, milles kasutajagrupp kehtib, klassifikaator TESTILIIK';
COMMENT ON COLUMN kasutajaroll.kehtib_alates IS 'õiguse kehtimise algus';
COMMENT ON COLUMN kasutajaroll.kehtib_kuni IS 'õiguse kehtimise lõpp';
COMMENT ON COLUMN kasutajaroll.rolliplokk IS 'kui pole NULL, siis muudetakse kõigi sama väärtusega kirjete andmeid koos, nt mitme aine ainespetsialisti korral; väärtuseks võetakse ühe kirje ID';
COMMENT ON COLUMN kasutajaroll.lang IS 'keele kood (kasutajaliidese tõlkija korral)';
COMMENT ON COLUMN kasutajaroll.allkiri_jrk IS 'järjekord vaideotsuse allkirjastamisel (kui roll on vaidekomisjoni liige)';
COMMENT ON COLUMN kasutajaroll.allkiri_tiitel1 IS 'dokumendi jaluses allkirjastaja tiitli rida 1 (ametinimetus)';
COMMENT ON COLUMN kasutajaroll.allkiri_tiitel2 IS 'dokumendi jaluses allkirjastaja tiitli rida 2 (roll komisjonis)';
COMMENT ON COLUMN kasutajaroll.created IS 'kirje loomise aeg';
COMMENT ON COLUMN kasutajaroll.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN kasutajaroll.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN kasutajaroll.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE kasutajaroll IS 'Kasutajaroll (kasutajagrupp koos kontekstiga)';

-- eis/model/kasutaja/paring_blokeering.py
COMMENT ON COLUMN paring_blokeering.id IS 'kirje identifikaator';
COMMENT ON COLUMN paring_blokeering.isikukood IS 'X-tee päise isikukood, teenuse kasutaja';
COMMENT ON COLUMN paring_blokeering.paring IS 'blokeeritava X-tee teenuse nimi';
COMMENT ON COLUMN paring_blokeering.eksimuste_arv IS 'eksimuste arv 10 minuti jooksul';
COMMENT ON COLUMN paring_blokeering.aeg IS 'esimese eksimuse aeg';
COMMENT ON COLUMN paring_blokeering.kuni IS 'blokeeringu kehtivuse lõpp, kui on blokeeritud';
COMMENT ON COLUMN paring_blokeering.created IS 'kirje loomise aeg';
COMMENT ON COLUMN paring_blokeering.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN paring_blokeering.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN paring_blokeering.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE paring_blokeering IS 'X-tee teenuste kasutamise blokeerimine 
    valede sisendandmete kasutamise eest.
    Kui 10 minuti jooksul tehakse 3 eksimust, siis 
    blokeeritakse teenuse kasutamine 24 tunniks.';

-- eis/model/kasutaja/paring_logi.py
COMMENT ON COLUMN paring_logi.id IS 'kirje identifikaator';
COMMENT ON COLUMN paring_logi.isikukood IS 'X-tee päise isikukood, teenuse kasutaja';
COMMENT ON COLUMN paring_logi.paring IS 'X-tee teenuse nimi';
COMMENT ON COLUMN paring_logi.asutus IS 'X-tee päise asutus (v4 MemberCode), teenuse kasutaja';
COMMENT ON COLUMN paring_logi.paritav IS 'isiku isikukood, kelle andmeid päritakse';
COMMENT ON COLUMN paring_logi.aeg IS 'esimese eksimuse aeg';
COMMENT ON COLUMN paring_logi.klient IS 'X-tee protokolli v4 päise klient, teenuse kasutaja';
COMMENT ON COLUMN paring_logi.created IS 'kirje loomise aeg';
COMMENT ON COLUMN paring_logi.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN paring_logi.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN paring_logi.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE paring_logi IS 'X-tee teenuste kasutamise logi';

-- eis/model/kasutaja/aineprofiil.py
COMMENT ON COLUMN aineprofiil.id IS 'kirje identifikaator';
COMMENT ON COLUMN aineprofiil.kasutaja_id IS 'viide kasutajale';
COMMENT ON COLUMN aineprofiil.aine_kood IS 'viide õppeainele, klassifikaator AINE';
COMMENT ON COLUMN aineprofiil.keeletase_kood IS 'keeleoskuse tase, klassifikaator KEELETASE (riigikeele aine korral)';
COMMENT ON COLUMN aineprofiil.kasutajagrupp_id IS 'viide kasutajagrupile: 29=const.GRUPP_HINDAJA_S - suuline hindaja; 30=const.GRUPP_HINDAJA_K - kirjalik hindaja; 36=const.GRUPP_INTERVJUU - intervjueerija; 38=const.GRUPP_KOMISJON - eksamikomisjoni liige (SE ja TE); 46=const.GRUPP_KOMISJON_ESIMEES - eksamikomisjoni esimees (SE ja TE, foreign_keys=kasutajagrupp_id); 47=const.GRUPP_KONSULTANT - konsultant';
COMMENT ON COLUMN aineprofiil.rangus IS 'rangus';
COMMENT ON COLUMN aineprofiil.halve IS 'ranguse standardhälve';
COMMENT ON COLUMN aineprofiil.koolitusaeg IS 'koolituse kuupäev';
COMMENT ON COLUMN aineprofiil.kaskkirikpv IS 'läbiviija käskkirja lisamise kuupäev';
COMMENT ON COLUMN aineprofiil.created IS 'kirje loomise aeg';
COMMENT ON COLUMN aineprofiil.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN aineprofiil.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN aineprofiil.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE aineprofiil IS 'Kasutaja konkreetses aines testi läbiviijana rakendamise profiil';

-- eis/model/kasutaja/caetestitud.py
COMMENT ON COLUMN caetestitud.id IS 'kirje identifikaator';
COMMENT ON COLUMN caetestitud.isikukood IS 'isikukood';
COMMENT ON COLUMN caetestitud.created IS 'kirje loomise aeg';
COMMENT ON COLUMN caetestitud.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN caetestitud.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN caetestitud.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE caetestitud IS 'Õppurite isikukoodid, kes on sooritanud CAE eeltesti,
    mis on üks eeltingimusi CAE rahvusvahelisele eksamile registreerimiseks';

-- eis/model/kasutaja/__init__.py
-- eis/model/kasutaja/ettepanek.py
COMMENT ON COLUMN ettepanek.id IS 'kirje identifikaator';
COMMENT ON COLUMN ettepanek.kasutaja_id IS 'viide kasutajale, kes algatas saatmise';
COMMENT ON COLUMN ettepanek.saatja IS 'saatja nimi';
COMMENT ON COLUMN ettepanek.epost IS 'e-posti aadress';
COMMENT ON COLUMN ettepanek.koht_id IS 'kasutaja koht';
COMMENT ON COLUMN ettepanek.teema IS 'teema';
COMMENT ON COLUMN ettepanek.sisu IS 'sisu';
COMMENT ON COLUMN ettepanek.url IS 'tegevuse URL, kust tagasisidet anti';
COMMENT ON COLUMN ettepanek.ootan_vastust IS 'kas pöörduja ootab vastuskirja';
COMMENT ON COLUMN ettepanek.on_vastatud IS 'kas on vastatud';
COMMENT ON COLUMN ettepanek.vastus IS 'vastuse sisu';
COMMENT ON COLUMN ettepanek.created IS 'kirje loomise aeg';
COMMENT ON COLUMN ettepanek.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN ettepanek.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN ettepanek.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE ettepanek IS 'Avaliku vaate kasutajate küsimused ja ettepanekud';

-- eis/model/kasutaja/kasutajagrupp_oigus.py
COMMENT ON COLUMN kasutajagrupp_oigus.kasutajagrupp_id IS 'viide kasutajagrupile';
COMMENT ON COLUMN kasutajagrupp_oigus.kasutajaoigus_id IS 'viide kasutajaõigusele';
COMMENT ON COLUMN kasutajagrupp_oigus.nimi IS 'õiguse nimi, päringute lihtsustamiseks dubleerib Kasutajaoigus.nimi';
COMMENT ON COLUMN kasutajagrupp_oigus.grupp_tyyp IS 'grupi tüüp, päringute lihtsustamiseks dubleerib Kasutajagrupp.tyyp';
COMMENT ON COLUMN kasutajagrupp_oigus.grupp_staatus IS 'grupi olek, päringute lihtsustamiseks dubleerib Kasutajagrupp.staatus';
COMMENT ON COLUMN kasutajagrupp_oigus.bitimask IS 'õiguste bitimask (1 - loetelu, 2 - vaatamine, 4 - lisamine, 8 - muutmine, 16 - kustutamine)';
COMMENT ON COLUMN kasutajagrupp_oigus.created IS 'kirje loomise aeg';
COMMENT ON COLUMN kasutajagrupp_oigus.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN kasutajagrupp_oigus.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN kasutajagrupp_oigus.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE kasutajagrupp_oigus IS 'Seos kasutajagruppide ja õiguste vahel';

-- eis/model/kasutaja/profiil.py
COMMENT ON COLUMN profiil.id IS 'kirje identifikaator';
COMMENT ON COLUMN profiil.kasutaja_id IS 'viide kasutajale';
COMMENT ON COLUMN profiil.on_vaatleja IS 'kas on vaatleja';
COMMENT ON COLUMN profiil.v_skeeled IS 'vaatlemise keeled eraldatuna tühikuga';
COMMENT ON COLUMN profiil.v_koolitusaeg IS 'vaatlemiskoolituse kuupäev';
COMMENT ON COLUMN profiil.v_kaskkirikpv IS 'vaatlejana käskkirja lisamise kuupäev';
COMMENT ON COLUMN profiil.s_skeeled IS 'suulise hindamise keeled eraldatuna tühikuga';
COMMENT ON COLUMN profiil.k_skeeled IS 'kirjaliku hindamise keeled eraldatuna tühikuga';
COMMENT ON COLUMN profiil.on_testiadmin IS 'kas on testide administraator';
COMMENT ON COLUMN profiil.markus IS 'märkused (sisestab Innove)';
COMMENT ON COLUMN profiil.oma_markus IS 'märkused (sisestab isik ise, nt kuhu saata eksamimaterjalid)';
COMMENT ON COLUMN profiil.arveldusarve IS 'kasutaja arveldusarve nr';
COMMENT ON COLUMN profiil.on_psammas IS 'kas on liitunud pensionikindlustuse II sambaga';
COMMENT ON COLUMN profiil.psammas_protsent IS '2 - vanaduspension 2%; 3 - vanaduspension 3% (kui on liitunud II sambaga)';
COMMENT ON COLUMN profiil.on_pensionar IS 'kas on vanaduspensionär';
COMMENT ON COLUMN profiil.on_ravikindlustus IS 'kas on kehtiv ravikindlustusleping';
COMMENT ON COLUMN profiil.created IS 'kirje loomise aeg';
COMMENT ON COLUMN profiil.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN profiil.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN profiil.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE profiil IS 'Kasutaja testi läbiviijana rakendamise profiil';

-- eis/model/kasutaja/pedagoogiuuendus.py
COMMENT ON COLUMN pedagoogiuuendus.id IS 'kirje identifikaator';
COMMENT ON COLUMN pedagoogiuuendus.kool_id IS 'EHISe kooli id';
COMMENT ON COLUMN pedagoogiuuendus.ehis_aine_kood IS 'aine (EHISe klassifikaator)';
COMMENT ON COLUMN pedagoogiuuendus.ehis_aste_kood IS 'kooliaste (EHISe klassifikaator)';
COMMENT ON COLUMN pedagoogiuuendus.seisuga IS 'viimane EHISest andmete kontrollimise aeg';
COMMENT ON COLUMN pedagoogiuuendus.created IS 'kirje loomise aeg';
COMMENT ON COLUMN pedagoogiuuendus.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN pedagoogiuuendus.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN pedagoogiuuendus.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE pedagoogiuuendus IS 'Pedagoogide andmete EHISest uuendamise seis';

-- eis/model/kasutaja/kasutajarollilogi.py
COMMENT ON COLUMN kasutajarollilogi.id IS 'kirje identifikaator';
COMMENT ON COLUMN kasutajarollilogi.kasutaja_id IS 'viide kasutajale, kelle õigusi muudeti';
COMMENT ON COLUMN kasutajarollilogi.kasutajagrupp_id IS 'kasutajagrupp';
COMMENT ON COLUMN kasutajarollilogi.tyyp IS 'grupi tüüp: 1=const.USER_TYPE_EKK - eksamikeskuse grupp; 4=const.USER_TYPE_KOOL - soorituskoha grupp';
COMMENT ON COLUMN kasutajarollilogi.kasutajaroll_id IS 'viide kasutajarollile, mida muudeti';
COMMENT ON COLUMN kasutajarollilogi.muutja_kasutaja_id IS 'viide kasutajale, kes muutis';
COMMENT ON COLUMN kasutajarollilogi.aeg IS 'õiguse muutmise aeg';
COMMENT ON COLUMN kasutajarollilogi.sisu IS 'muudetud andmed';
COMMENT ON COLUMN kasutajarollilogi.jira_nr IS 'õiguse muutmiseks tehtud JIRA pileti nr';
COMMENT ON COLUMN kasutajarollilogi.selgitus IS 'õiguse muutmise selgitus';
COMMENT ON COLUMN kasutajarollilogi.created IS 'kirje loomise aeg';
COMMENT ON COLUMN kasutajarollilogi.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN kasutajarollilogi.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN kasutajarollilogi.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE kasutajarollilogi IS 'Kasutajarollide andmise logi';

-- eis/model/kasutaja/volitus.py
COMMENT ON COLUMN volitus.id IS 'kirje identifikaator';
COMMENT ON COLUMN volitus.opilane_kasutaja_id IS 'viide kasutajale, kelle tulemusi lubatakse vaadata';
COMMENT ON COLUMN volitus.volitatu_kasutaja_id IS 'viide kasutajale, kellel on luba vaadata teise kasutaja tulemusi';
COMMENT ON COLUMN volitus.andja_kasutaja_id IS 'viide kasutajale, kes volituse andis';
COMMENT ON COLUMN volitus.tyhistaja_kasutaja_id IS 'viide kasutajale, kes volituse tühistas (kui on tühistatud, foreign_keys=tyhistaja_kasutaja_id)';
COMMENT ON COLUMN volitus.kehtib_alates IS 'volituse kehtimise algus';
COMMENT ON COLUMN volitus.kehtib_kuni IS 'volituse kehtimise lõpp';
COMMENT ON COLUMN volitus.tyhistatud IS 'volituse tühistamise aeg';
COMMENT ON COLUMN volitus.created IS 'kirje loomise aeg';
COMMENT ON COLUMN volitus.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN volitus.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN volitus.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE volitus IS 'Volitused teiste sooritajate tulemuste vaatamiseks';

-- eis/model/kasutaja/kasutajapiirkond.py
COMMENT ON COLUMN kasutajapiirkond.id IS 'kirje identifikaator';
COMMENT ON COLUMN kasutajapiirkond.kasutaja_id IS 'viide kasutajale';
COMMENT ON COLUMN kasutajapiirkond.piirkond_id IS 'viide piirkonnale';
COMMENT ON COLUMN kasutajapiirkond.created IS 'kirje loomise aeg';
COMMENT ON COLUMN kasutajapiirkond.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN kasutajapiirkond.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN kasutajapiirkond.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE kasutajapiirkond IS 'Piirkonnad, milles saab kasutajat testide läbiviimises rakendada';

-- eis/model/kasutaja/opperyhm.py
COMMENT ON COLUMN opperyhm.id IS 'kirje identifikaator';
COMMENT ON COLUMN opperyhm.nimi IS 'rühma nimetus';
COMMENT ON COLUMN opperyhm.kasutaja_id IS 'õpetaja, kelle rühm see on';
COMMENT ON COLUMN opperyhm.koht_id IS 'õppeasutus';
COMMENT ON COLUMN opperyhm.created IS 'kirje loomise aeg';
COMMENT ON COLUMN opperyhm.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN opperyhm.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN opperyhm.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE opperyhm IS 'Õpilaste rühm. Õpetaja jagab ise oma õpilased rühmadesse.
    Õpetaja kasutab rühmi tööde jagamisel.';

-- eis/model/kasutaja/paring_tunnistus.py
COMMENT ON COLUMN paring_tunnistus.id IS 'kirje identifikaator';
COMMENT ON COLUMN paring_tunnistus.isikukood IS 'X-tee päise isikukood, teenuse kasutaja';
COMMENT ON COLUMN paring_tunnistus.paring IS 'X-tee teenuse nimi';
COMMENT ON COLUMN paring_tunnistus.asutus IS 'X-tee päise asutus, teenuse kasutaja';
COMMENT ON COLUMN paring_tunnistus.tunnistus_id IS 'viide alla laaditud tunnistusele';
COMMENT ON COLUMN paring_tunnistus.aeg IS 'esimese eksimuse aeg';
COMMENT ON COLUMN paring_tunnistus.created IS 'kirje loomise aeg';
COMMENT ON COLUMN paring_tunnistus.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN paring_tunnistus.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN paring_tunnistus.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE paring_tunnistus IS 'X-tee kaudu tunnistuste allalaadimise logi';

-- eis/model/kasutaja/ainepedagoog.py
COMMENT ON COLUMN ainepedagoog.id IS 'kirje identifikaator';
COMMENT ON COLUMN ainepedagoog.pedagoog_id IS 'pedagoogi kirje';
COMMENT ON COLUMN ainepedagoog.ehis_aine_kood IS 'aine (EHISe klassifikaator)';
COMMENT ON COLUMN ainepedagoog.ehis_aste_kood IS 'kooliaste (EHISe klassifikaator)';
COMMENT ON COLUMN ainepedagoog.seisuga IS 'viimane EHISest andmete kontrollimise aeg';
COMMENT ON COLUMN ainepedagoog.created IS 'kirje loomise aeg';
COMMENT ON COLUMN ainepedagoog.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN ainepedagoog.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN ainepedagoog.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE ainepedagoog IS 'Pedagoogi seos õppeainetega, mida õpetab';

-- eis/model/eksam/verifflog.py
COMMENT ON COLUMN verifflog.id IS 'kirje identifikaator';
COMMENT ON COLUMN verifflog.sooritus_id IS 'soorituse ID, millelt verifitseerimisele suunati';
COMMENT ON COLUMN verifflog.kasutaja_id IS 'kasutaja ID';
COMMENT ON COLUMN verifflog.session_id IS 'Veriff sessiooni ID';
COMMENT ON COLUMN verifflog.sess_data IS 'sessiooni loomise päringu vastus (json)';
COMMENT ON COLUMN verifflog.started IS 'verifitseerimise algus veriffis (webhooki saamise aeg)';
COMMENT ON COLUMN verifflog.submitted IS 'verifitseerimise lõpp veriffis (webhooki saamise aeg)';
COMMENT ON COLUMN verifflog.dec_data IS 'verifitseerimise otsuse andmed (json)';
COMMENT ON COLUMN verifflog.code IS 'verifitseerimise tulemuse kood (9001,9102,9103,9104,9121)';
COMMENT ON COLUMN verifflog.riik IS 'verifitseerimisel kasutatud dokumendi riik';
COMMENT ON COLUMN verifflog.isikukood IS 'verifitseeritud isikukood';
COMMENT ON COLUMN verifflog.rc IS 'True - verifitseeritud isik on sama, mis autenditud; False - ei ole sama või ei saanud verifitseerida';
COMMENT ON COLUMN verifflog.created IS 'kirje loomise aeg';
COMMENT ON COLUMN verifflog.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN verifflog.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN verifflog.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE verifflog IS 'Veriff verifitseerimispäringute logi';

-- eis/model/eksam/kvskann.py
-- eis/model/eksam/seblog.py
COMMENT ON COLUMN seblog.id IS 'kirje identifikaator';
COMMENT ON COLUMN seblog.sooritus_id IS 'soorituse ID';
COMMENT ON COLUMN seblog.url_key IS 'EISi testisoorituse URLi osa SEBiga lahendamisel';
COMMENT ON COLUMN seblog.avatud IS 'SEBi avamise aeg';
COMMENT ON COLUMN seblog.remote_addr IS 'sooritaja IP';
COMMENT ON COLUMN seblog.namespace IS 'tavalise brauseri seansi identifikaator (millega SEB konf alla laaditi)';
COMMENT ON COLUMN seblog.created IS 'kirje loomise aeg';
COMMENT ON COLUMN seblog.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN seblog.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN seblog.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE seblog IS 'SEB avamise logi';

-- eis/model/eksam/skannfail.py
COMMENT ON COLUMN skannfail.id IS 'kirje identifikaator';
COMMENT ON COLUMN skannfail.filename IS 'failinimi';
COMMENT ON COLUMN skannfail.filesize IS 'faili suurus baitides';
COMMENT ON COLUMN skannfail.fileversion IS 'versioon';
COMMENT ON COLUMN skannfail.sooritus_id IS 'viide soorituse kirjele';
COMMENT ON COLUMN skannfail.teatatud IS 'millal saadeti sooritajale e-postiga teade skannitud faili saadvale jõudmise kohta';
COMMENT ON COLUMN skannfail.created IS 'kirje loomise aeg';
COMMENT ON COLUMN skannfail.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN skannfail.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN skannfail.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE skannfail IS 'Skannitud eksamitööde failide viited';

-- eis/model/eksam/alatestisoorituslogi.py
COMMENT ON COLUMN alatestisoorituslogi.id IS 'kirje identifikaator';
COMMENT ON COLUMN alatestisoorituslogi.alatestisooritus_id IS 'viide alatestisooritusele';
COMMENT ON COLUMN alatestisoorituslogi.staatus IS 'sooritamise olek';
COMMENT ON COLUMN alatestisoorituslogi.pallid IS 'saadud hindepallid';
COMMENT ON COLUMN alatestisoorituslogi.url IS 'andmeid muutnud tegevuse URL';
COMMENT ON COLUMN alatestisoorituslogi.remote_addr IS 'muutja klient';
COMMENT ON COLUMN alatestisoorituslogi.server_addr IS 'muutja server';
COMMENT ON COLUMN alatestisoorituslogi.created IS 'kirje loomise aeg';
COMMENT ON COLUMN alatestisoorituslogi.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN alatestisoorituslogi.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN alatestisoorituslogi.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE alatestisoorituslogi IS 'Alatestisoorituse kirje muudatuste logi';

-- eis/model/eksam/statvastus_t.py
COMMENT ON COLUMN statvastus_t.id IS 'kirje identifikaator';
COMMENT ON COLUMN statvastus_t.statvastus_t_seis_id IS 'arvutusprotsessi ID, millega andmed on leitud';
COMMENT ON COLUMN statvastus_t.kood1 IS 'küsimuse kood, eripaari korral koos kooloni ja esimese valiku koodiga';
COMMENT ON COLUMN statvastus_t.selgitus1 IS 'küsimuse selgitus või eripaari esimese valiku selgitus';
COMMENT ON COLUMN statvastus_t.kysimus_seq IS 'küsimuse jrk';
COMMENT ON COLUMN statvastus_t.valik1_seq IS 'eripaari korral esimese valiku jrk';
COMMENT ON COLUMN statvastus_t.ks_punktid IS 'antud vastuse punktid; vastamata jätmisel alati 0';
COMMENT ON COLUMN statvastus_t.svpunktid IS 'eripaari korral eripaari punktid, muidu küsimuse punktid';
COMMENT ON COLUMN statvastus_t.kv_punktid IS 'küsimuse punktid';
COMMENT ON COLUMN statvastus_t.max_punktid IS 'eripaari korral eripaari max toorpunktid, muidu küsimuse toorpunktid';
COMMENT ON COLUMN statvastus_t.oige IS 'vastuse õigsus (1 - õige; 0,5 - osaliselt õige, 0 - vale või loetamatu või vastamata)';
COMMENT ON COLUMN statvastus_t.vastus IS 'vastus või eripaari teise valiku kood';
COMMENT ON COLUMN statvastus_t.selgitus IS 'vastuse selgitus';
COMMENT ON COLUMN statvastus_t.kvsisu_seq IS 'vastuse jrk nr';
COMMENT ON COLUMN statvastus_t.kvsisu_id IS 'viide vastuse sisu kirjele';
COMMENT ON COLUMN statvastus_t.kysimus_id IS 'viide küsimuse kirjele';
COMMENT ON COLUMN statvastus_t.kysimusevastus_id IS 'viide küsimusevastuse kirjele';
COMMENT ON COLUMN statvastus_t.ylesandevastus_id IS 'viide ülesandevastuse kirjele';
COMMENT ON COLUMN statvastus_t.max_vastus IS 'kood1 max vastuste arv';
COMMENT ON COLUMN statvastus_t.staatus IS 'soorituse staatus';
COMMENT ON TABLE statvastus_t IS 'Küsimuste vastused Exceli väljavõtte kiirendamiseks.
    Uuendatakse vaate statvastus põhjal testi või toimumisaja kaupa siis,
    kui tulemusi arvutatakse';

COMMENT ON COLUMN statvastus_t_seis.id IS 'kirje identifikaator';
COMMENT ON COLUMN statvastus_t_seis.testiosa_id IS 'viide testiosale, mille andmed uuendati';
COMMENT ON COLUMN statvastus_t_seis.toimumisaeg_id IS 'viide toimumisajale, mille andmed uuendati';
COMMENT ON COLUMN statvastus_t_seis.seisuga IS 'andmete uuendamise aeg';
COMMENT ON COLUMN statvastus_t_seis.protsess_id IS 'arvutusprotsessi ID, millega andmed uuendati';
COMMENT ON COLUMN statvastus_t_seis.created IS 'kirje loomise aeg';
COMMENT ON COLUMN statvastus_t_seis.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN statvastus_t_seis.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN statvastus_t_seis.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE statvastus_t_seis IS 'Tabeli statvastus_t uuendamise andmed';

-- eis/model/eksam/soorituskomplekt.py
COMMENT ON COLUMN soorituskomplekt.id IS 'kirje identifikaator';
COMMENT ON COLUMN soorituskomplekt.sooritus_id IS 'viide sooritusele';
COMMENT ON COLUMN soorituskomplekt.komplektivalik_id IS 'viide komplektivalikule';
COMMENT ON COLUMN soorituskomplekt.komplekt_id IS 'viide valitud komplektile';
COMMENT ON COLUMN soorituskomplekt.created IS 'kirje loomise aeg';
COMMENT ON COLUMN soorituskomplekt.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN soorituskomplekt.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN soorituskomplekt.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE soorituskomplekt IS 'Soorituse ülesandekomplekti valik';

-- eis/model/eksam/helivastusfail.py
COMMENT ON COLUMN helivastusfail.id IS 'kirje identifikaator';
COMMENT ON COLUMN helivastusfail.filename IS 'failinimi laadimisel';
COMMENT ON COLUMN helivastusfail.filesize IS 'faili suurus';
COMMENT ON COLUMN helivastusfail.fileversion IS 'versioon';
COMMENT ON COLUMN helivastusfail.kestus IS 'kestus sekundites';
COMMENT ON COLUMN helivastusfail.valjast IS 'true - muu vahendiga salvestatud ja EISi üles laaditud helifail; false - EISi-siseselt salvestatud helifail';
COMMENT ON COLUMN helivastusfail.created IS 'kirje loomise aeg';
COMMENT ON COLUMN helivastusfail.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN helivastusfail.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN helivastusfail.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE helivastusfail IS 'Soorituse helifail (võib sisaldada mitme sooritaja vastuseid)';

-- eis/model/eksam/npstatistika.py
COMMENT ON COLUMN npstatistika.id IS 'kirje identifikaator';
COMMENT ON COLUMN npstatistika.statistika_id IS 'viide statistika kirjele';
COMMENT ON COLUMN npstatistika.normipunkt_id IS 'viide normipunkti kirjele';
COMMENT ON COLUMN npstatistika.vastuste_arv IS 'selle vastusega sooritajate arv';
COMMENT ON COLUMN npstatistika.nvaartus IS 'arvuline väärtus (kui on arv)';
COMMENT ON COLUMN npstatistika.svaartus IS 'tekstiline väärtus (kui pole arv)';
COMMENT ON COLUMN npstatistika.created IS 'kirje loomise aeg';
COMMENT ON COLUMN npstatistika.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN npstatistika.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN npstatistika.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE npstatistika IS 'Normipunktide vastuste statistika';

-- eis/model/eksam/helivastus.py
COMMENT ON COLUMN helivastus.id IS 'kirje identifikaator';
COMMENT ON COLUMN helivastus.helivastusfail_id IS 'viide faili kirjele';
COMMENT ON COLUMN helivastus.sooritus_id IS 'viide sooritusele';
COMMENT ON COLUMN helivastus.ylesanne_id IS 'viide ülesandele';
COMMENT ON COLUMN helivastus.testiylesanne_id IS 'viide testiülesandele';
COMMENT ON COLUMN helivastus.created IS 'kirje loomise aeg';
COMMENT ON COLUMN helivastus.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN helivastus.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN helivastus.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE helivastus IS 'Helifaili seosed sooritustega ja ülesannetega';

-- eis/model/eksam/loendur.py
COMMENT ON COLUMN loendur.id IS 'kirje identifikaator';
COMMENT ON COLUMN loendur.tahis IS 'tabamuste loenduri tähis';
COMMENT ON COLUMN loendur.tabamuste_arv IS 'antud tähisega hindamismaatriksis tabatud ridade arv';
COMMENT ON COLUMN loendur.created IS 'kirje loomise aeg';
COMMENT ON COLUMN loendur.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN loendur.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN loendur.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE loendur IS 'Tabamuste loenduri väärtus';

-- eis/model/eksam/npvastus.py
COMMENT ON COLUMN npvastus.id IS 'kirje identifikaator';
COMMENT ON COLUMN npvastus.sooritus_id IS 'viide sooritusele';
COMMENT ON COLUMN npvastus.ylesandevastus_id IS 'viide ylesandele antud vastusele (tagasisidega ülesande korral, jagatud töös)';
COMMENT ON COLUMN npvastus.normipunkt_id IS 'viide normipunkti kirjele';
COMMENT ON COLUMN npvastus.nvaartus IS 'arvuline väärtus (kui on arv)';
COMMENT ON COLUMN npvastus.svaartus IS 'tekstiline väärtus (kui pole arv)';
COMMENT ON COLUMN npvastus.viga IS 'valemi arvutamise veateade';
COMMENT ON COLUMN npvastus.nptagasiside_id IS 'viide antud tagasiside tekstile';
COMMENT ON COLUMN npvastus.created IS 'kirje loomise aeg';
COMMENT ON COLUMN npvastus.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN npvastus.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN npvastus.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE npvastus IS 'Normipunkti väärtus soorituse korral';

-- eis/model/eksam/sisuvaatamine.py
COMMENT ON COLUMN sisuvaatamine.id IS 'kirje identifikaator';
COMMENT ON COLUMN sisuvaatamine.sisuplokk_id IS 'viide sisuplokile';
COMMENT ON COLUMN sisuvaatamine.algus IS 'ylesande brauseris laadimise aeg (brauseri aeg)';
COMMENT ON COLUMN sisuvaatamine.lopp IS 'aeg, mil ülesandelt lahkuti või logi salvestati (brauseri aeg)';
COMMENT ON COLUMN sisuvaatamine.nahtav_logi IS 'nähtavuse logi, koosneb tekstidest [+-]SEK, kus + tähendab sisuploki kuvamist, - tähendab sisuploki peitmist ja SEK näitab, mitu sekundit peale algust kuvamine või peitmine toimus';
COMMENT ON COLUMN sisuvaatamine.nahtav_kordi IS 'nähtavaks muutmiste arv';
COMMENT ON COLUMN sisuvaatamine.nahtav_aeg IS 'nähtavana olnud sekundite arv';
COMMENT ON COLUMN sisuvaatamine.created IS 'kirje loomise aeg';
COMMENT ON COLUMN sisuvaatamine.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN sisuvaatamine.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN sisuvaatamine.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE sisuvaatamine IS 'Ülesande sisuploki lahendajale nähtavana kuvamise logi.
    Kasutusel tagasisidefunktsioonide bvcount(), bvtime() jaoks.';

-- eis/model/eksam/__init__.py
-- eis/model/eksam/kysimusevastus.py
COMMENT ON COLUMN kysimusevastus.id IS 'kirje identifikaator';
COMMENT ON COLUMN kysimusevastus.kood IS 'küsimuse kood';
COMMENT ON COLUMN kysimusevastus.sptyyp IS 'sisuploki tüüp (sisuplokk.tyyp)';
COMMENT ON COLUMN kysimusevastus.baastyyp IS 'baastüüp (tulemus.baastyyp): identifier, boolean, integer, float, string, point, pair, directedPair, duration, file, uri';
COMMENT ON COLUMN kysimusevastus.sisestus IS 'mitmes sisestamine (1 või 2)';
COMMENT ON COLUMN kysimusevastus.toorpunktid IS 'toorpunktid (ülesande skaala järgi)';
COMMENT ON COLUMN kysimusevastus.pallid IS 'hindepallid (testiülesande skaala järgi)';
COMMENT ON COLUMN kysimusevastus.max_pallid IS 'max hindepallid';
COMMENT ON COLUMN kysimusevastus.nullipohj_kood IS 'null punkti andmise põhjus, klassifikaator NULLIPOHJ';
COMMENT ON COLUMN kysimusevastus.oigete_arv IS 'õigete vastuste arv (koolipsühholoogitesti jaoks)';
COMMENT ON COLUMN kysimusevastus.valede_arv IS 'valede vastuste arv (koolipsühholoogitesti jaoks)';
COMMENT ON COLUMN kysimusevastus.vastuseta IS 'kas anti tühi vastus (siis saab käsitsihinnatav küsimus automaatselt 0p)';
COMMENT ON COLUMN kysimusevastus.arvutihinnatud IS 'arvutihinnatav või arvuti poolt hinnatud hübriidhinnatav või käsitsi hinnatav, aga vastuseta';
COMMENT ON COLUMN kysimusevastus.valikujrk IS 'valikute järjekord antud soorituses (valikute segamisega küsimuse korral)';
COMMENT ON COLUMN kysimusevastus.testjrk IS 'küsimuse jrk nr sooritaja testis (statistikute jaoks)';
COMMENT ON COLUMN kysimusevastus.created IS 'kirje loomise aeg';
COMMENT ON COLUMN kysimusevastus.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN kysimusevastus.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN kysimusevastus.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE kysimusevastus IS 'Sooritaja poolt ühe ülesande ühele küsimusele antud vastuste koondkirje';

-- eis/model/eksam/kvsisu.py
COMMENT ON COLUMN kvsisu.id IS 'kirje identifikaator';
COMMENT ON COLUMN kvsisu.seq IS 'mitmes vastus (küsimuse piires); -2=const.SEQ_ANALYSIS - kogujärjestuse kirje analüüsi jaoks';
COMMENT ON COLUMN kvsisu.svseq IS 'mitmes vastus statvastuse kood1 piires (paari korral ühe paarilise piires), lugemine algab 0-st';
COMMENT ON COLUMN kvsisu.tyyp IS 'vastuse tüüp: NULL - vastust pole (kirjet kasutatakse hindepallide jaoks); t=const.RTYPE_CORRECT - õige/vale; s=const.RTYPE_STRING - sisu; f=const.RTYPE_FILE - filedata ja filename; i=const.RTYPE_IDENTIFIER - kood1; p=const.RTYPE_PAIR - kood1 ja kood2; o=const.RTYPE_ORDERED - järjestus; c=const.RTYPE_COORDS - koordinaadid; x=const.RTYPE_POINT - punkt';
COMMENT ON COLUMN kvsisu.toorpunktid IS 'toorpunktid (ülesande skaala järgi)';
COMMENT ON COLUMN kvsisu.kood1 IS 'valikvastuse korral valiku kood';
COMMENT ON COLUMN kvsisu.kood2 IS 'valikvastuste paari korral teise valiku kood';
COMMENT ON COLUMN kvsisu.sisu IS 'vabatekstiline vastus või järjestus või lüngata panga kohaindeks vms (vastuste statistikas eristatakse eraldi reana); krati korral transkriptsioon';
COMMENT ON COLUMN kvsisu.koordinaat IS 'punkti või murdjoone koordinaadid stringina (vastuste statistikas ei eristata), kirjavahemärgi lünga asukoha indeks lauses; krati korral staatuse URL';
COMMENT ON COLUMN kvsisu.kujund IS 'koordinaatidega antud kujundi liik (line, polyline, ray)';
COMMENT ON COLUMN kvsisu.filename IS 'failinimi';
COMMENT ON COLUMN kvsisu.filesize IS 'faili suurus baitides';
COMMENT ON COLUMN kvsisu.fileversion IS 'versioon';
COMMENT ON COLUMN kvsisu.oige IS 'kas vastus oli õige või vale: 0=const.C_VALE - vale; 1=const.C_OSAOIGE - osaliselt õige; 2=const.C_OIGE - õige; 8=const.C_LOETAMATU - loetamatu; 9=const.C_VASTAMATA - vastamata (õige/vale sisestamise korral sisestatakse (sisestamisel ei kasutata 2); vastuse olemasolu korral arvutihinnatavas ülesandes arvutatakse hindamismaatriksi põhjal; kui hindaja määrab pallid, siis: max pallide korral 2=const.C_OIGE; muu positiivse palli korral 1=const.C_OSAOIGE; 0p korral 0=const.C_VALE; - korral 9=const.C_VASTAMATA)';
COMMENT ON COLUMN kvsisu.maatriks IS 'mitmenda hindamismaatriksiga on see vastus hinnatav (sobitamise küsimusel võib olla mitu hindamismaatriksit)';
COMMENT ON COLUMN kvsisu.hindamismaatriks_id IS 'arvutihinnatava ülesande korral viide hindamismaatriksi reale, mille alusel punkte anti; ei ole võti - hindamismaatriksi muutmisel võib osutada puuduvale reale; kasutusel psühholoogilises testis valimata vastuste arvu leidmisel';
COMMENT ON COLUMN kvsisu.sonade_arv IS 'sõnade arv sisu veerus olevas vastuse tekstis';
COMMENT ON COLUMN kvsisu.hindamisinfo IS 'arvutihindamisel jäetav info, järjestamise ülesande korral jada liikmete õigsus (nt 1010011)';
COMMENT ON COLUMN kvsisu.analyysitav IS 'kas kirjet tuleb arvestada vastuste analüüsis (järjestamise korral võib analüüsis kasutada üht kogujärjestuse kirjet, mitte iga üksikelemendi kirjet eraldi)';
COMMENT ON COLUMN kvsisu.created IS 'kirje loomise aeg';
COMMENT ON COLUMN kvsisu.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN kvsisu.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN kvsisu.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE kvsisu IS 'Küsimuse vastus sisu, sooritaja poolt ühe ülesande 
    ühele küsimusele antud ühe vastuse sisu
    (mitme vastusega küsimuste korral on iga vastuse jaoks eraldi kirje)';

-- eis/model/eksam/ylesandevastus.py
COMMENT ON COLUMN ylesandevastus.id IS 'kirje identifikaator';
COMMENT ON COLUMN ylesandevastus.sooritus_id IS 'viide sooritusele (puudub ülesande eelvaates lahendamisel)';
COMMENT ON COLUMN ylesandevastus.valitudylesanne_id IS 'viide testi valitud ülesandele';
COMMENT ON COLUMN ylesandevastus.testiylesanne_id IS 'viide testiülesandele (puudub ülesande eelvaates lahendamisel)';
COMMENT ON COLUMN ylesandevastus.tahis IS 'testiülesande tähis';
COMMENT ON COLUMN ylesandevastus.alatest_id IS 'viide alatestile';
COMMENT ON COLUMN ylesandevastus.loplik IS 'true - viimati valitud komplekti kuuluva ülesande vastus; null - mõne varem proovitud komplekti ülesande vastus';
COMMENT ON COLUMN ylesandevastus.algus IS 'ülesande esimese lugemise aeg';
COMMENT ON COLUMN ylesandevastus.viimane_algus IS 'ülesande viimase lugemise aeg';
COMMENT ON COLUMN ylesandevastus.lopp IS 'viimane vastuste salvestamise aeg';
COMMENT ON COLUMN ylesandevastus.ajakulu IS 'vastamiseks kulutatud sekundite arv';
COMMENT ON COLUMN ylesandevastus.staatus IS 'vastuse olek (1 - on arvutatud, 0 - vajab üle arvutamist)';
COMMENT ON COLUMN ylesandevastus.toorpunktid IS 'toorpunktid (ülesande skaala järgi)';
COMMENT ON COLUMN ylesandevastus.toorpunktid_arvuti IS 'arvutihinnatav osa toorpunktidest';
COMMENT ON COLUMN ylesandevastus.toorpunktid_kasitsi IS 'käsitsihinnatav osa toorpunktidest';
COMMENT ON COLUMN ylesandevastus.pallid IS 'hindepallid (testiülesande skaala järgi)';
COMMENT ON COLUMN ylesandevastus.pallid_arvuti IS 'arvutihinnatav osa hindepallidest';
COMMENT ON COLUMN ylesandevastus.pallid_kasitsi IS 'käsitsihinnatav osa hindepallidest';
COMMENT ON COLUMN ylesandevastus.toorpunktid_enne_vaiet IS 'toorpunktid enne vaidlustamist';
COMMENT ON COLUMN ylesandevastus.pallid_enne_vaiet IS 'hindepallid enne vaidlustamist';
COMMENT ON COLUMN ylesandevastus.yhisosa_pallid IS 'seotud testimiskordade ühisossa kuulunud küsimuste hindepallide summa';
COMMENT ON COLUMN ylesandevastus.max_pallid IS 'max hindepallid vastavalt soorituse komplektile';
COMMENT ON COLUMN ylesandevastus.arvutuskaik IS 'arvutihindamise arvutuskäik HTMLina';
COMMENT ON COLUMN ylesandevastus.muudetav IS 'kas lahendaja saaks vastust veel muuta juhul, kui sooritus oleks pooleli (testi sooritamisel alati true, jagatud töös false peale ülesande vastuse kinnitamist)';
COMMENT ON COLUMN ylesandevastus.kehtiv IS 'kas on ülesande kõigi vastuste seast viimane vaadatav vastus (testi sooritamisel alati true, jagatud töös: false - kui vastust pole veel kinnitatud ja muudetav=true; true - kui vastus on kinnitatud ja ei ole kinnitatud mõnd järgmist vastust; NULL - kui on kinnitatud juba mõni järgmine vastus)';
COMMENT ON COLUMN ylesandevastus.skann IS 'skannitud vastus JPG-pildina';
COMMENT ON COLUMN ylesandevastus.laius_orig IS 'skannitud pildi tegelik laius';
COMMENT ON COLUMN ylesandevastus.korgus_orig IS 'skannitud pildi tegelik kõrgus';
COMMENT ON COLUMN ylesandevastus.oigete_arv IS 'õigete vastuste arv (koolipsühholoogitesti jaoks)';
COMMENT ON COLUMN ylesandevastus.valede_arv IS 'valede vastuste arv (koolipsühholoogitesti jaoks)';
COMMENT ON COLUMN ylesandevastus.valimata_valede_arv IS 'valimata valede vastuste arv, sisaldub õigete arvus (koolipsühholoogitesti jaoks)';
COMMENT ON COLUMN ylesandevastus.valimata_oigete_arv IS 'valimata valede vastuste arv, sisaldub valede arvus (koolipsühholoogitesti jaoks)';
COMMENT ON COLUMN ylesandevastus.oigete_suhe IS 'õigete vastuste suhe kõikidesse vastustesse (koolipsühholoogitesti jaoks)';
COMMENT ON COLUMN ylesandevastus.vastuseta IS 'kas vastuseid pole (on ainult tühjad vastused)';
COMMENT ON COLUMN ylesandevastus.lopetatud IS 'kas kõik kohustuslikud küsimused on vastatud';
COMMENT ON COLUMN ylesandevastus.mittekasitsi IS 'kas on arvutihinnatav: true - käsitsi pole midagi hinnata (arvutihinnatavad küsimused või hübriidhinnatud või käsitsihinnatavad küsimused vastamata); false - kuulub käsitsi hindamisele; väli on mõeldud arvestamiseks ainult e-hinnatavate testide korral, sest p-hindamise korral ei peagi vastused andmebaasis olema';
COMMENT ON COLUMN ylesandevastus.on_toorvastus IS 'kas vastused on veel toorvastuse tabelist ümber paigutamata';
COMMENT ON COLUMN ylesandevastus.valikujrk IS 'sisuplokkide ID-de järjekord antud soorituses (kui ylesanne.segamini=true)';
COMMENT ON COLUMN ylesandevastus.created IS 'kirje loomise aeg';
COMMENT ON COLUMN ylesandevastus.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN ylesandevastus.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN ylesandevastus.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE ylesandevastus IS 'Sooritaja poolt ühele ülesandele antud vastus';

-- eis/model/eksam/alatestisooritus.py
COMMENT ON COLUMN alatestisooritus.id IS 'kirje identifikaator';
COMMENT ON COLUMN alatestisooritus.sooritus_id IS 'viide sooritusele';
COMMENT ON COLUMN alatestisooritus.alatest_id IS 'viide alatestile';
COMMENT ON COLUMN alatestisooritus.algus IS 'soorituse esimese seansi algus';
COMMENT ON COLUMN alatestisooritus.lopp IS 'soorituse viimase seansi lõpp';
COMMENT ON COLUMN alatestisooritus.seansi_algus IS 'soorituse viimase seansi algus';
COMMENT ON COLUMN alatestisooritus.lisaaeg IS 'sooritajale antud lisaaeg, lisandub testiosa piirajale';
COMMENT ON COLUMN alatestisooritus.ajakulu IS 'kulutatud sekundite arv kõigi lõpetatud seansside peale kokku';
COMMENT ON COLUMN alatestisooritus.staatus IS 'olek: 3=const.S_STAATUS_REGATUD - registreeritud; 5=const.S_STAATUS_ALUSTAMATA - alustamata; 6=const.S_STAATUS_POOLELI - pooleli; 7=const.S_STAATUS_KATKESTATUD - katkestatud; 8=const.S_STAATUS_TEHTUD - tehtud; 9=const.S_STAATUS_EEMALDATUD - eemaldatud; 10=const.S_STAATUS_PUUDUS - puudus; 11=const.S_STAATUS_VABASTATUD - vabastatud';
COMMENT ON COLUMN alatestisooritus.yl_arv IS 'ülesannete arv alatestis sooritaja poolt valitud komplektis';
COMMENT ON COLUMN alatestisooritus.tehtud_yl_arv IS 'ülesannete arv, milles on vähemalt mõnele küsimusele vastatud';
COMMENT ON COLUMN alatestisooritus.lopetatud_yl_arv IS 'ülesannete arv, milles on kõigile küsimustele kohustuslik arv vastuseid antud';
COMMENT ON COLUMN alatestisooritus.pallid IS 'saadud hindepallid';
COMMENT ON COLUMN alatestisooritus.pallid_enne_vaiet IS 'hindepallid enne vaidlustamist';
COMMENT ON COLUMN alatestisooritus.tulemus_protsent IS 'saadud hindepallid protsentides suurimast võimalikust tulemusest';
COMMENT ON COLUMN alatestisooritus.max_pallid IS 'max pallid (lõdva struktuuri korral sõltub valitud komplektist)';
COMMENT ON COLUMN alatestisooritus.oigete_arv IS 'õigete vastuste arv (koolipsühholoogitesti jaoks)';
COMMENT ON COLUMN alatestisooritus.valede_arv IS 'valede vastuste arv (koolipsühholoogitesti jaoks)';
COMMENT ON COLUMN alatestisooritus.valimata_valede_arv IS 'valimata valede vastuste arv, sisaldub õigete arvus (koolipsühholoogitesti jaoks)';
COMMENT ON COLUMN alatestisooritus.valimata_oigete_arv IS 'valimata valede vastuste arv, sisaldub valede arvus (koolipsühholoogitesti jaoks)';
COMMENT ON COLUMN alatestisooritus.oigete_suhe IS 'õigete vastuste suhe kõikidesse vastustesse (koolipsühholoogitesti jaoks)';
COMMENT ON COLUMN alatestisooritus.viimane_valitudylesanne_id IS 'viimane vaadatud valitudylesanne';
COMMENT ON COLUMN alatestisooritus.viimane_testiylesanne_id IS 'viimane vaadatud testiylesanne';
COMMENT ON COLUMN alatestisooritus.valikujrk IS 'ülesannete järjekord antud alatestisoorituses (kui on juhusliku järjekorraga alatest)';
COMMENT ON COLUMN alatestisooritus.created IS 'kirje loomise aeg';
COMMENT ON COLUMN alatestisooritus.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN alatestisooritus.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN alatestisooritus.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE alatestisooritus IS 'Piirajaga alatesti sooritamine';

-- eis/model/eksam/proctoriolog.py
COMMENT ON COLUMN proctoriolog.id IS 'kirje identifikaator';
COMMENT ON COLUMN proctoriolog.sooritus_id IS 'soorituse ID';
COMMENT ON COLUMN proctoriolog.kasutaja_id IS 'kasutaja ID';
COMMENT ON COLUMN proctoriolog.take_url IS 'sooritamise URL';
COMMENT ON COLUMN proctoriolog.review_url IS 'kontrollimise URL (kehtib 1 tund peale loomist)';
COMMENT ON COLUMN proctoriolog.url_key IS 'EISi testisoorituse URLi osa, mida teab ainult Proctorio (et välistada ilma Proctoriota lahendamine)';
COMMENT ON COLUMN proctoriolog.toimumisaeg_id IS 'toimumisaja ID';
COMMENT ON COLUMN proctoriolog.created IS 'kirje loomise aeg';
COMMENT ON COLUMN proctoriolog.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN proctoriolog.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN proctoriolog.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE proctoriolog IS 'Proctorio poole pöördumiste logi';

-- eis/model/ylesanne/tulemus.py
COMMENT ON COLUMN tulemus.id IS 'kirje identifikaator';
COMMENT ON COLUMN tulemus.kood IS 'küsimuse kood, seob tulemuse kirje küsimusega';
COMMENT ON COLUMN tulemus.yhisosa_kood IS 'eri ülesannete küsimuste sidumiseks kasutatav kood, kui küsimuste statistika tehakse ühiselt';
COMMENT ON COLUMN tulemus.kardinaalsus IS 'QTI cardinality: single, multiple, ordered, orderedAdj, orderedSeq';
COMMENT ON COLUMN tulemus.baastyyp IS 'QTI baseType: identifier, boolean, integer, float, string, point, pair, directedPair, duration, file, uri';
COMMENT ON COLUMN tulemus.min_pallid IS 'minimaalne pallide arv, QTI lowerBound';
COMMENT ON COLUMN tulemus.max_pallid IS 'QTI upperBound, koostaja määratud max pallide arv; kui punktiarvutus arvutab suurema pallide arvu, siis antakse max_pallid palli';
COMMENT ON COLUMN tulemus.vaikimisi_pallid IS 'hindamismaatriksis puuduva vastuse eest antavad pallid; QTI defaultValue';
COMMENT ON COLUMN tulemus.oige_pallid IS 'õige vastuse eest antavad pallid (mitme valikuga tabelis, kus õige vastus märgitakse märkeruuduga)';
COMMENT ON COLUMN tulemus.vastus_pallid IS 'kas küsimuse vastus ongi punktide arv (arvutatud väärtuse korral)';
COMMENT ON COLUMN tulemus.max_pallid_arv IS 'arvutatud max võimalik pallide arv, kui max_pallid oleks seadmata';
COMMENT ON COLUMN tulemus.max_pallid_vastus IS 'hindamismaatriksis olev max pallide arv ühe üksikvastuse eest (kasutusel üksikvastuse õigsuse määramisel)';
COMMENT ON COLUMN tulemus.max_vastus IS 'kui vastuseid on sellest arvust rohkem, siis antakse min_pallid';
COMMENT ON COLUMN tulemus.min_oige_vastus IS 'kui õigeid vastuseid on sellest arvust vähem, siis antakse min_pallid';
COMMENT ON COLUMN tulemus.min_sonade_arv IS 'kui vastuses on arvust vähem sõnu, siis antakse min_pallid (avatud vastuse korral)';
COMMENT ON COLUMN tulemus.pintervall IS 'lubatud punktide intervall (käsitsi hindamisel)';
COMMENT ON COLUMN tulemus.tyhikud IS 'kas vastuse võrdlemisel arvestada tühikuid (true - arvestada, false - ignoreerida), juhul kui baastüüp on "string"';
COMMENT ON COLUMN tulemus.lubatud_tyhi IS 'kas on lubatud tühi vastus (kui baastüüp on "string", "integer" või "float")';
COMMENT ON COLUMN tulemus.tostutunne IS 'kas vastuse võrdlemisel olla tõstutundlik (kui baastüüp on "string"): true - tõstutundlik; false - tõstutundetu';
COMMENT ON COLUMN tulemus.ladinavene IS 'kas vastuse võrdlemisel lugeda sama välimusega ladina ja vene tähed samaväärseks';
COMMENT ON COLUMN tulemus.regavaldis IS 'kas vastuse võrdlemisel võtta hindamismaatriksi vastust regulaaravaldisena, juhul kui baastüüp on "string"';
COMMENT ON COLUMN tulemus.regavaldis_osa IS 'kui kasutatakse regulaaravaldist, siis kas sellega kontrollitakse tekstiosa vastavust: true - tekstiosa vastamine avaldisele, false - terve vastuse vastamine avaldisele';
COMMENT ON COLUMN tulemus.valem IS 'kas vastuse võrdlemisel võtta hindamismaatriksi vastust valemina (võib viidata teistele küsimustele), juhul kui baastüüp on arvuline';
COMMENT ON COLUMN tulemus.vordus_eraldab IS 'kas võrdusmärk eraldab vastused, mida võrreldakse hindamismaatriksiga ükshaaval ja antakse palle kõrgeime pallide arvuga vastuse eest (matemaatika korral)';
COMMENT ON COLUMN tulemus.koik_oiged IS 'kui võrdusmärk eraldab vastused, kas siis punktide saamiseks peavad kõik osad olema õiged (matemaatika korral)';
COMMENT ON COLUMN tulemus.sallivusprotsent IS 'lubatud erinevus protsentides';
COMMENT ON COLUMN tulemus.ymard_komakohad IS 'mitme kohani peale koma vastus hindamismaatriksiga võrdlemisel ümardatakse (kui baastyyp=float)';
COMMENT ON COLUMN tulemus.ymardet IS 'kas hindamismaatriksis olevad arvud on ümardatud (true korral on tabamus juhul, kui lahendaja vastust saab ümardada hindamismaatriksis olevaks arvuks; false korral peab lahendaja vastama täpselt sama arvuga), reaalarvude korral';
COMMENT ON COLUMN tulemus.arvutihinnatav IS 'kas tulemusele vastav küsimus on arvutiga hinnatav';
COMMENT ON COLUMN tulemus.hybriidhinnatav IS 'kas käsitsihinnatav ülesanne on arvutihinnatav nende vastuste osas, mis leiduvad hindamismaatriksis';
COMMENT ON COLUMN tulemus.naidisvastus IS 'näidisvastus (selgitav tekst) või hindamisjuhend';
COMMENT ON COLUMN tulemus.naidis_naha IS 'kas näidisvastust näidata lahendajale (peale lahendamist) või ainult hindajale';
COMMENT ON COLUMN tulemus.ylesanne_id IS 'viide ülesandele';
COMMENT ON COLUMN tulemus.naide IS 'kas kysimus on vastuse näide (siis kuvatakse õige vastus alati lahendajale ja selle kysimuse eest palle ei anta); kui kogu sisuplokk on näide, siis vt sisuplokk.naide';
COMMENT ON COLUMN tulemus.maatriksite_arv IS 'hindamismaatriksite arv';
COMMENT ON COLUMN tulemus.oigsus_kysimus_id IS 'viide küsimusele, mille tulemus näitab, kas antud küsimus vastati õigesti (kasutusel õigete/valede vastuste värvimisel ja mitme küsimuse koos käsitsihindamisel)';
COMMENT ON COLUMN tulemus.created IS 'kirje loomise aeg';
COMMENT ON COLUMN tulemus.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN tulemus.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN tulemus.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE tulemus IS 'Küsimusele antud vastuse hindamise tingimused ehk hindamismaatriks.
    Kirje vastab ühele küsimusele.
    Tulemuse jaoks on eraldi tabel tehtud QTIst mõjutatult
    (QTI vaste responseDeclaration, osaliselt ka responseDeclaration/mapping),
    põhimõtteliselt võiks QTIs olla üks tulemuse kirje mitme küsimuse peale.';

-- eis/model/ylesanne/punktikirjeldus.py
COMMENT ON COLUMN punktikirjeldus.id IS 'kirje identifikaator';
COMMENT ON COLUMN punktikirjeldus.hindamisaspekt_id IS 'viide hindamisaspektile';
COMMENT ON COLUMN punktikirjeldus.punktid IS 'punktide arv (sammuga 0,5)';
COMMENT ON COLUMN punktikirjeldus.kirjeldus IS 'kirjeldus';
COMMENT ON COLUMN punktikirjeldus.created IS 'kirje loomise aeg';
COMMENT ON COLUMN punktikirjeldus.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN punktikirjeldus.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN punktikirjeldus.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE punktikirjeldus IS 'Ülesande hindamisaspekti eest antavate punktide kirjeldus';

-- eis/model/ylesanne/util.py
-- eis/model/ylesanne/lahendusjuhis.py
COMMENT ON COLUMN lahendusjuhis.id IS 'kirje identifikaator';
COMMENT ON COLUMN lahendusjuhis.juhis IS 'ülesande lahendusjuhis';
COMMENT ON COLUMN lahendusjuhis.ylesanne_id IS 'viide ülesandele';
COMMENT ON COLUMN lahendusjuhis.nupuriba IS 'lahendaja tekstitoimeti nupureal kuvatavate ikoonide nimed, komaeraldatud';
COMMENT ON COLUMN lahendusjuhis.matriba IS 'lahendaja matemaatikaredaktori nupureal kuvatavate ikoonide nimed, komaeraldatud';
COMMENT ON COLUMN lahendusjuhis.wmatriba IS 'lahendaja WIRIS MathType redaktori nupurea seaded';
COMMENT ON COLUMN lahendusjuhis.tahemargid IS 'originaalkeeles sisuploki tähemärkide arv (originaalkeeles)';
COMMENT ON COLUMN lahendusjuhis.created IS 'kirje loomise aeg';
COMMENT ON COLUMN lahendusjuhis.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN lahendusjuhis.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN lahendusjuhis.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE lahendusjuhis IS 'Ülesande lahendusjuhis';

-- eis/model/ylesanne/ylesandeversioon.py
COMMENT ON COLUMN ylesandeversioon.id IS 'kirje identifikaator';
COMMENT ON COLUMN ylesandeversioon.ylesanne_id IS 'viide ülesandele';
COMMENT ON COLUMN ylesandeversioon.seq IS 'versiooni järjekorranumber ülesande sees';
COMMENT ON COLUMN ylesandeversioon.created IS 'kirje loomise aeg';
COMMENT ON COLUMN ylesandeversioon.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN ylesandeversioon.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN ylesandeversioon.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE ylesandeversioon IS 'Ülesande versioonid';

-- eis/model/ylesanne/joonistamine.py
COMMENT ON COLUMN joonistamine.id IS 'kirje identifikaator';
COMMENT ON COLUMN joonistamine.kysimus_id IS 'viide küsimusele';
COMMENT ON COLUMN joonistamine.on_arvutihinnatav IS 'kas on arvutihinnatav murdjoon/vabakäejoon või muidu joonistus';
COMMENT ON COLUMN joonistamine.on_seadistus IS 'kas lahendaja saab vaikimisi seadeid muuta';
COMMENT ON COLUMN joonistamine.tarbed IS 'kasutatavad joonistustarbed, semikooloniga eraldatult';
COMMENT ON COLUMN joonistamine.stroke_width IS 'joone laius';
COMMENT ON COLUMN joonistamine.stroke_color IS 'joone värv';
COMMENT ON COLUMN joonistamine.fill_none IS 'kas joonistatava kujundi sisu on tühi';
COMMENT ON COLUMN joonistamine.fill_color IS 'kujundi sisu värv';
COMMENT ON COLUMN joonistamine.fill_opacity IS 'sisu läbipaistvus, vahemikus 0.1, 0.2, 0.3 kuni 1';
COMMENT ON COLUMN joonistamine.fontsize IS 'kirja suurus';
COMMENT ON COLUMN joonistamine.textfill_color IS 'kirja värv';
COMMENT ON COLUMN joonistamine.created IS 'kirje loomise aeg';
COMMENT ON COLUMN joonistamine.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN joonistamine.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN joonistamine.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE joonistamine IS 'Täiendavad vaikimisi seaded joonistamise sisuploki juurde';

-- eis/model/ylesanne/hindamismaatriks.py
COMMENT ON COLUMN hindamismaatriks.id IS 'kirje identifikaator';
COMMENT ON COLUMN hindamismaatriks.kood1 IS 'hinnatav väärtus (QTI mapKey) või selle esimene osa';
COMMENT ON COLUMN hindamismaatriks.kood2 IS 'hinnatava väärtuse (QTI mapKey) teine osa (kasutatakse siis, kui baastyyp on pair või directedPair)';
COMMENT ON COLUMN hindamismaatriks.oige IS 'kas on märgitud õigeks vastuseks (QTI correctResponse)';
COMMENT ON COLUMN hindamismaatriks.kujund IS 'hinnatava kujundi liik (QTI shape, areaMapEntry korral)';
COMMENT ON COLUMN hindamismaatriks.koordinaadid IS 'hinnatava kujundi koordinaadid (QTI coords, areaMapEntry korral; jrk nr lüngata panga ja kirjavahemärgi lisamise korral)';
COMMENT ON COLUMN hindamismaatriks.selgitus IS 'selgitus';
COMMENT ON COLUMN hindamismaatriks.jrk IS 'ridade järjestus (saab määrata ainult otse andmebaasis, kasutajaliidese kaudu ei saa)';
COMMENT ON COLUMN hindamismaatriks.pallid IS 'hinnatava väärtuse eest antavad toorpunktid (QTI mappedValue, nende valikute eest saadud punktid)';
COMMENT ON COLUMN hindamismaatriks.sallivus IS 'joonistamise sisuploki korral maksimaalne lubatud kaugus pikslites lahendaja tõmmatud joone ja koostaja antud õige joone vahel (koostamise vaates pool joone laiusest)';
COMMENT ON COLUMN hindamismaatriks.tulemus_id IS 'viide tulemuse kirjele';
COMMENT ON COLUMN hindamismaatriks.maatriks IS 'mitmes hindamismaatriks (üldjuhul alati 1, aga kolme hulgaga sobitamisel on olemas ka 2)';
COMMENT ON COLUMN hindamismaatriks.tahis IS 'tabamuste loenduri tähis (loendur suureneb ühe võrra, kui sooritaja vastust hinnatakse sellel hindamismaatriksi real)';
COMMENT ON COLUMN hindamismaatriks.tabamuste_arv IS 'täpne tabamuste arv, mille korral antakse punkte (kui on tühi, siis korduvaid tabamusi ei arvestata, st punkte annab ainult esimene tabamus)';
COMMENT ON COLUMN hindamismaatriks.tingimus IS 'lisatingimuse valem, mis võib sõltuda teistest vastustest - kui valem on antud ja valemi väärtus pole tõene, siis see maatriksirida ei anna tabamust';
COMMENT ON COLUMN hindamismaatriks.valem IS 'kas vastuse võrdlemisel võtta hindamismaatriksi vastust valemina (matemaatika korral, muudes sisuplokkides kasutatakse tabelis Tulemus olevat märget)';
COMMENT ON COLUMN hindamismaatriks.teisendatav IS 'kas vastuse võrdlemisel vastust (nii maatriksi vastust kui ka sooritaja vastust) lihtsustatakse (matemaatika korral)';
COMMENT ON COLUMN hindamismaatriks.vrd_tekst IS 'kas vastuse võrdlemisel võrreldakse ainult tekstina (matemaatilist tähendust ei arvestata, matemaatika korral)';
COMMENT ON COLUMN hindamismaatriks.created IS 'kirje loomise aeg';
COMMENT ON COLUMN hindamismaatriks.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN hindamismaatriks.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN hindamismaatriks.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE hindamismaatriks IS 'Hindamismaatriksi rida, 
    QTI vaste: mapping/mapEntry või mapping/areaMapEntry või mapping/correctResponse/value';

-- eis/model/ylesanne/salaylesandeisik.py
COMMENT ON COLUMN salaylesandeisik.id IS 'kirje identifikaator';
COMMENT ON COLUMN salaylesandeisik.salaylesanne_id IS 'viide krüptitud ülesandele';
COMMENT ON COLUMN salaylesandeisik.kasutaja_id IS 'viide kasutajale, kes saab lahti krüptida';
COMMENT ON COLUMN salaylesandeisik.created IS 'kirje loomise aeg';
COMMENT ON COLUMN salaylesandeisik.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN salaylesandeisik.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN salaylesandeisik.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE salaylesandeisik IS 'Krüptitud ülesannet lahti krüptida suutev isik';

-- eis/model/ylesanne/t_ylesanne.py
COMMENT ON COLUMN t_ylesanne.id IS 'kirje identifikaator';
COMMENT ON COLUMN t_ylesanne.orig_id IS 'viide lähtetabelile';
COMMENT ON COLUMN t_ylesanne.lang IS 'tõlkekeel';
COMMENT ON COLUMN t_ylesanne.ylesandeversioon_id IS 'versioon';
COMMENT ON COLUMN t_ylesanne.nimi IS 'nimetus';
COMMENT ON COLUMN t_ylesanne.marksonad IS 'otsingu märksõnad';
COMMENT ON COLUMN t_ylesanne.dlgop_tekst IS 'dialoogiakna tekst, kui vastamist ei alustata ooteaja jooksul (õpipädevuse ülesannetes sisuplokis "piltide lohistamine kujunditele")';
COMMENT ON COLUMN t_ylesanne.tahemargid IS 'ülesande tõlke tähemärkide arv';
COMMENT ON COLUMN t_ylesanne.yl_tagasiside IS 'tagasiside terve ülesande kohta sõltumata tulemusest';
COMMENT ON COLUMN t_ylesanne.created IS 'kirje loomise aeg';
COMMENT ON COLUMN t_ylesanne.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN t_ylesanne.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN t_ylesanne.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE t_ylesanne IS 'Tabeli Ylesanne tõlge';

COMMENT ON COLUMN t_lahendusjuhis.id IS 'kirje identifikaator';
COMMENT ON COLUMN t_lahendusjuhis.orig_id IS 'viide lähtetabelile';
COMMENT ON COLUMN t_lahendusjuhis.lang IS 'tõlkekeel';
COMMENT ON COLUMN t_lahendusjuhis.ylesandeversioon_id IS 'versioon';
COMMENT ON COLUMN t_lahendusjuhis.juhis IS 'juhis';
COMMENT ON COLUMN t_lahendusjuhis.tahemargid IS 'lahendusjuhise tõlke tähemärkide arv';
COMMENT ON COLUMN t_lahendusjuhis.created IS 'kirje loomise aeg';
COMMENT ON COLUMN t_lahendusjuhis.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN t_lahendusjuhis.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN t_lahendusjuhis.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE t_lahendusjuhis IS 'Tabeli Lahendusjuhis tõlge';

COMMENT ON COLUMN t_hindamisaspekt.id IS 'kirje identifikaator';
COMMENT ON COLUMN t_hindamisaspekt.orig_id IS 'viide lähtetabelile';
COMMENT ON COLUMN t_hindamisaspekt.lang IS 'tõlkekeel';
COMMENT ON COLUMN t_hindamisaspekt.ylesandeversioon_id IS 'versioon';
COMMENT ON COLUMN t_hindamisaspekt.hindamisjuhis IS 'juhis';
COMMENT ON COLUMN t_hindamisaspekt.created IS 'kirje loomise aeg';
COMMENT ON COLUMN t_hindamisaspekt.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN t_hindamisaspekt.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN t_hindamisaspekt.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE t_hindamisaspekt IS 'Tabeli Hindamisaspekt tõlge';

COMMENT ON COLUMN t_punktikirjeldus.id IS 'kirje identifikaator';
COMMENT ON COLUMN t_punktikirjeldus.orig_id IS 'viide lähtetabelile';
COMMENT ON COLUMN t_punktikirjeldus.lang IS 'tõlkekeel';
COMMENT ON COLUMN t_punktikirjeldus.ylesandeversioon_id IS 'versioon';
COMMENT ON COLUMN t_punktikirjeldus.kirjeldus IS 'kirjeldus';
COMMENT ON COLUMN t_punktikirjeldus.created IS 'kirje loomise aeg';
COMMENT ON COLUMN t_punktikirjeldus.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN t_punktikirjeldus.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN t_punktikirjeldus.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE t_punktikirjeldus IS 'Tabeli Punktikirjeldus tõlge';

COMMENT ON COLUMN t_sisuplokk.id IS 'kirje identifikaator';
COMMENT ON COLUMN t_sisuplokk.orig_id IS 'viide lähtetabelile';
COMMENT ON COLUMN t_sisuplokk.lang IS 'tõlkekeel';
COMMENT ON COLUMN t_sisuplokk.ylesandeversioon_id IS 'versioon';
COMMENT ON COLUMN t_sisuplokk.nimi IS 'nimetus';
COMMENT ON COLUMN t_sisuplokk.tehn_tookask IS 'tehniline töökäsk';
COMMENT ON COLUMN t_sisuplokk.sisu IS 'toimetajale näidatav sisu';
COMMENT ON COLUMN t_sisuplokk.sisuvaade IS 'lahendajale näidatav sisu';
COMMENT ON COLUMN t_sisuplokk.laius IS 'veergude arv (ristsõna korral)';
COMMENT ON COLUMN t_sisuplokk.korgus IS 'ridade arv (ristsõna korral)';
COMMENT ON COLUMN t_sisuplokk.tahemargid IS 'sisuploki tõlke tähemärkide arv';
COMMENT ON COLUMN t_sisuplokk.created IS 'kirje loomise aeg';
COMMENT ON COLUMN t_sisuplokk.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN t_sisuplokk.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN t_sisuplokk.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE t_sisuplokk IS 'Tabeli Sisuplokk tõlge';

COMMENT ON COLUMN t_sisuobjekt.id IS 'kirje identifikaator';
COMMENT ON COLUMN t_sisuobjekt.orig_id IS 'viide lähtetabelile';
COMMENT ON COLUMN t_sisuobjekt.lang IS 'tõlkekeel';
COMMENT ON COLUMN t_sisuobjekt.ylesandeversioon_id IS 'versioon';
COMMENT ON COLUMN t_sisuobjekt.tiitel IS 'pildi atribuut title (kasutatakse pildi algallikate märkimiseks)';
COMMENT ON COLUMN t_sisuobjekt.filesize IS 'faili suurus baitides';
COMMENT ON COLUMN t_sisuobjekt.fileversion IS 'versioon';
COMMENT ON COLUMN t_sisuobjekt.fileurl IS 'faili URL';
COMMENT ON COLUMN t_sisuobjekt.laius IS 'kuvamisel kasutatav laius';
COMMENT ON COLUMN t_sisuobjekt.korgus IS 'kuvamisel kasutatav kõrgus';
COMMENT ON COLUMN t_sisuobjekt.laius_orig IS 'pildi tegelik laius';
COMMENT ON COLUMN t_sisuobjekt.korgus_orig IS 'pildi tegelik kõrgus';
COMMENT ON COLUMN t_sisuobjekt.created IS 'kirje loomise aeg';
COMMENT ON COLUMN t_sisuobjekt.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN t_sisuobjekt.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN t_sisuobjekt.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE t_sisuobjekt IS 'Tabeli Sisuobjekt tõlge';

COMMENT ON COLUMN t_tulemus.id IS 'kirje identifikaator';
COMMENT ON COLUMN t_tulemus.orig_id IS 'viide lähtetabelile';
COMMENT ON COLUMN t_tulemus.lang IS 'tõlkekeel';
COMMENT ON COLUMN t_tulemus.ylesandeversioon_id IS 'versioon';
COMMENT ON COLUMN t_tulemus.naidisvastus IS 'näidisvastus (avatud vastusega küsimuse korral)';
COMMENT ON COLUMN t_tulemus.created IS 'kirje loomise aeg';
COMMENT ON COLUMN t_tulemus.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN t_tulemus.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN t_tulemus.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE t_tulemus IS 'Tabeli Tulemus tõlge';

COMMENT ON COLUMN t_ylesandefail.id IS 'kirje identifikaator';
COMMENT ON COLUMN t_ylesandefail.orig_id IS 'viide lähtetabelile';
COMMENT ON COLUMN t_ylesandefail.lang IS 'tõlkekeel';
COMMENT ON COLUMN t_ylesandefail.ylesandeversioon_id IS 'versioon';
COMMENT ON COLUMN t_ylesandefail.filesize IS 'faili suurus baitides';
COMMENT ON COLUMN t_ylesandefail.fileversion IS 'versioon';
COMMENT ON COLUMN t_ylesandefail.fileurl IS 'faili URL';
COMMENT ON COLUMN t_ylesandefail.created IS 'kirje loomise aeg';
COMMENT ON COLUMN t_ylesandefail.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN t_ylesandefail.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN t_ylesandefail.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE t_ylesandefail IS 'Tabeli Ylesandefail tõlge';

COMMENT ON COLUMN t_kysimus.id IS 'kirje identifikaator';
COMMENT ON COLUMN t_kysimus.orig_id IS 'viide lähtetabelile';
COMMENT ON COLUMN t_kysimus.lang IS 'tõlkekeel';
COMMENT ON COLUMN t_kysimus.ylesandeversioon_id IS 'versioon';
COMMENT ON COLUMN t_kysimus.pikkus IS 'avatud lünga pikkus; ristsõna sõna pikkus';
COMMENT ON COLUMN t_kysimus.max_pikkus IS 'avatud lünga vastuse max pikkus';
COMMENT ON COLUMN t_kysimus.ridu IS 'avatud lünga korral ridade arv';
COMMENT ON COLUMN t_kysimus.mask IS 'avatud lünga mask';
COMMENT ON COLUMN t_kysimus.vihje IS 'vihje, mis kuvatakse lahendajale enne vastuse sisestamist';
COMMENT ON COLUMN t_kysimus.pos_x IS 'ristsõna korral: mitmes veerg';
COMMENT ON COLUMN t_kysimus.pos_y IS 'ristsõna korral: mitmes rida';
COMMENT ON COLUMN t_kysimus.joondus IS 'ristsõna korral: teksti suund';
COMMENT ON COLUMN t_kysimus.created IS 'kirje loomise aeg';
COMMENT ON COLUMN t_kysimus.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN t_kysimus.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN t_kysimus.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE t_kysimus IS 'Tabeli Kysimus tõlge';

COMMENT ON COLUMN t_kyslisa.id IS 'kirje identifikaator';
COMMENT ON COLUMN t_kyslisa.orig_id IS 'viide lähtetabelile';
COMMENT ON COLUMN t_kyslisa.lang IS 'tõlkekeel';
COMMENT ON COLUMN t_kyslisa.ylesandeversioon_id IS 'versioon';
COMMENT ON COLUMN t_kyslisa.yhik IS 'liuguriga mõõdetava ühiku nimetus';
COMMENT ON COLUMN t_kyslisa.created IS 'kirje loomise aeg';
COMMENT ON COLUMN t_kyslisa.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN t_kyslisa.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN t_kyslisa.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE t_kyslisa IS 'Tabeli Kyslisa tõlge';

COMMENT ON COLUMN t_valik.id IS 'kirje identifikaator';
COMMENT ON COLUMN t_valik.orig_id IS 'viide lähtetabelile';
COMMENT ON COLUMN t_valik.lang IS 'tõlkekeel';
COMMENT ON COLUMN t_valik.ylesandeversioon_id IS 'versioon';
COMMENT ON COLUMN t_valik.nimi IS 'nimetus';
COMMENT ON COLUMN t_valik.created IS 'kirje loomise aeg';
COMMENT ON COLUMN t_valik.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN t_valik.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN t_valik.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE t_valik IS 'Tabeli Valik tõlge';

COMMENT ON COLUMN t_hindamismaatriks.id IS 'kirje identifikaator';
COMMENT ON COLUMN t_hindamismaatriks.orig_id IS 'viide lähtetabelile';
COMMENT ON COLUMN t_hindamismaatriks.lang IS 'tõlkekeel';
COMMENT ON COLUMN t_hindamismaatriks.ylesandeversioon_id IS 'versioon';
COMMENT ON COLUMN t_hindamismaatriks.kood1 IS 'kood1';
COMMENT ON COLUMN t_hindamismaatriks.kood2 IS 'kood2';
COMMENT ON COLUMN t_hindamismaatriks.created IS 'kirje loomise aeg';
COMMENT ON COLUMN t_hindamismaatriks.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN t_hindamismaatriks.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN t_hindamismaatriks.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE t_hindamismaatriks IS 'Tabeli Hindamismaatriks tõlge';

COMMENT ON COLUMN t_abivahend.id IS 'kirje identifikaator';
COMMENT ON COLUMN t_abivahend.orig_id IS 'viide lähtetabelile';
COMMENT ON COLUMN t_abivahend.lang IS 'tõlkekeel';
COMMENT ON COLUMN t_abivahend.nimi IS 'nimetus';
COMMENT ON COLUMN t_abivahend.kirjeldus IS 'täiendav kirjeldus';
COMMENT ON COLUMN t_abivahend.pais IS 'HTML päisesse lisatav osa (vahendite korral)';
COMMENT ON COLUMN t_abivahend.created IS 'kirje loomise aeg';
COMMENT ON COLUMN t_abivahend.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN t_abivahend.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN t_abivahend.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE t_abivahend IS 'Tabeli Abivahend tõlge';

-- eis/model/ylesanne/hindamiskysimus.py
COMMENT ON COLUMN hindamiskysimus.id IS 'kirje identifikaator';
COMMENT ON COLUMN hindamiskysimus.ylesanne_id IS 'viide ülesandele';
COMMENT ON COLUMN hindamiskysimus.kysimus IS 'küsitud küsimus';
COMMENT ON COLUMN hindamiskysimus.kysija_kasutaja_id IS 'viide küsijale';
COMMENT ON COLUMN hindamiskysimus.kysimisaeg IS 'küsimise aeg';
COMMENT ON COLUMN hindamiskysimus.vastus IS 'hindamisjuhi vastus küsimusele';
COMMENT ON COLUMN hindamiskysimus.vastaja_kasutaja_id IS 'viide vastajale';
COMMENT ON COLUMN hindamiskysimus.vastamisaeg IS 'vastamise aeg';
COMMENT ON COLUMN hindamiskysimus.avalik IS 'kas on kõigile hindajatele nähtav küsimus';
COMMENT ON COLUMN hindamiskysimus.created IS 'kirje loomise aeg';
COMMENT ON COLUMN hindamiskysimus.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN hindamiskysimus.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN hindamiskysimus.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE hindamiskysimus IS 'Hindajate poolt hindamisjuhile esitatud küsimused ja saadud vastused';

-- eis/model/ylesanne/vahend.py
COMMENT ON COLUMN vahend.id IS 'kirje identifikaator';
COMMENT ON COLUMN vahend.vahend_kood IS 'abivahendi kood tabelis Abivahend';
COMMENT ON COLUMN vahend.ylesanne_id IS 'viide ülesandele';
COMMENT ON COLUMN vahend.created IS 'kirje loomise aeg';
COMMENT ON COLUMN vahend.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN vahend.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN vahend.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE vahend IS 'Ülesande lahendajale lubatud abivahendid';

-- eis/model/ylesanne/tulemusmall.py
COMMENT ON COLUMN tulemusmall.id IS 'kirje identifikaator';
COMMENT ON COLUMN tulemusmall.nimi IS 'malli nimi';
COMMENT ON COLUMN tulemusmall.kirjeldus IS 'malli kirjeldus';
COMMENT ON COLUMN tulemusmall.rp_uri IS 'malli URI';
COMMENT ON COLUMN tulemusmall.rp_location IS 'asukoht';
COMMENT ON COLUMN tulemusmall.rp_reeglid IS 'reeglite sisu';
COMMENT ON COLUMN tulemusmall.created IS 'kirje loomise aeg';
COMMENT ON COLUMN tulemusmall.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN tulemusmall.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN tulemusmall.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE tulemusmall IS 'Tulemuste reeglite mallid. EISi siseselt ei kasutata.
    QTI responseProcessing';

-- eis/model/ylesanne/testiliik.py
COMMENT ON COLUMN testiliik.id IS 'kirje identifikaator';
COMMENT ON COLUMN testiliik.kood IS 'testiliigi kood, klassifikaator TESTILIIK';
COMMENT ON COLUMN testiliik.ylesanne_id IS 'viide ülesandele';
COMMENT ON COLUMN testiliik.created IS 'kirje loomise aeg';
COMMENT ON COLUMN testiliik.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN testiliik.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN testiliik.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE testiliik IS 'Ülesande testiliigid';

-- eis/model/ylesanne/ylopitulemus.py
COMMENT ON COLUMN ylopitulemus.id IS 'kirje identifikaator';
COMMENT ON COLUMN ylopitulemus.opitulemus_klrida_id IS 'õpitulemus, klassifikaator OPITULEMUS';
COMMENT ON COLUMN ylopitulemus.ylesandeaine_id IS 'viide ülesande õppeainele';
COMMENT ON COLUMN ylopitulemus.created IS 'kirje loomise aeg';
COMMENT ON COLUMN ylopitulemus.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN ylopitulemus.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN ylopitulemus.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE ylopitulemus IS 'Ülesande õpitulemused';

-- eis/model/ylesanne/abivahend.py
COMMENT ON COLUMN abivahend.id IS 'kirje identifikaator';
COMMENT ON COLUMN abivahend.jrk IS 'järjekorranumber valikutes';
COMMENT ON COLUMN abivahend.kood IS 'väärtuse kood';
COMMENT ON COLUMN abivahend.nimi IS 'nimetus';
COMMENT ON COLUMN abivahend.kirjeldus IS 'täiendav kirjeldus';
COMMENT ON COLUMN abivahend.pais IS 'HTML päisesse lisatav osa (vahendite korral)';
COMMENT ON COLUMN abivahend.ikoon_url IS 'ikooni failinimi (vahendite korral)';
COMMENT ON COLUMN abivahend.laius IS 'kuvamisel kasutatav laius (vahendite korral)';
COMMENT ON COLUMN abivahend.korgus IS 'kuvamisel kasutatav kõrgus (vahendite korral)';
COMMENT ON COLUMN abivahend.kehtib IS 'olek: 1 - kehtib; 0 - ei kehti';
COMMENT ON COLUMN abivahend.created IS 'kirje loomise aeg';
COMMENT ON COLUMN abivahend.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN abivahend.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN abivahend.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE abivahend IS 'Ülesande lahendamise abivahend';

-- eis/model/ylesanne/ylesandeteema.py
COMMENT ON COLUMN ylesandeteema.id IS 'kirje identifikaator';
COMMENT ON COLUMN ylesandeteema.teema_kood IS 'teema (varasem nimetus: valdkond) ülesande õppeaines, klassifikaator TEEMA';
COMMENT ON COLUMN ylesandeteema.alateema_kood IS 'alateema (varem nimetus: teema) teemas, klassifikaator ALATEEMA';
COMMENT ON COLUMN ylesandeteema.ylesandeaine_id IS 'viide ülesande õppeainele';
COMMENT ON COLUMN ylesandeteema.created IS 'kirje loomise aeg';
COMMENT ON COLUMN ylesandeteema.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN ylesandeteema.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN ylesandeteema.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE ylesandeteema IS 'Ülesande valdkonnad ja teemad';

-- eis/model/ylesanne/valjund.py
COMMENT ON COLUMN valjund.id IS 'kirje identifikaator';
COMMENT ON COLUMN valjund.kood IS 'QTI identifier';
COMMENT ON COLUMN valjund.kardinaalsus IS 'QTI cardinality: single, multiple, ordered';
COMMENT ON COLUMN valjund.baastyyp IS 'QTI baseType';
COMMENT ON COLUMN valjund.interpretatsioon IS 'interpretation';
COMMENT ON COLUMN valjund.max_norm IS 'QTI normalMaximum';
COMMENT ON COLUMN valjund.min_norm IS 'QTI normalMinimum';
COMMENT ON COLUMN valjund.oskus_norm IS 'QTI masteryValue';
COMMENT ON COLUMN valjund.vaikimisi IS 'QTI lookupTable/defaultValue';
COMMENT ON COLUMN valjund.ylesanne_id IS 'viide ülesandele';
COMMENT ON COLUMN valjund.created IS 'kirje loomise aeg';
COMMENT ON COLUMN valjund.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN valjund.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN valjund.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE valjund IS 'Väljundmuutujate deklareerimine (nt SCORE). EISi siseselt ei kasutata.
    QTI outcomeDeclaration';

-- eis/model/ylesanne/ylesandefailimarkus.py
COMMENT ON COLUMN ylesandefailimarkus.id IS 'kirje identifikaator';
COMMENT ON COLUMN ylesandefailimarkus.ylesandefail_id IS 'viide ülesandefailile';
COMMENT ON COLUMN ylesandefailimarkus.kasutaja_id IS 'viide märkuse kirjutanud kasutajale';
COMMENT ON COLUMN ylesandefailimarkus.aeg IS 'märkuse kirjutamise aeg';
COMMENT ON COLUMN ylesandefailimarkus.sisu IS 'märkuse sisu';
COMMENT ON COLUMN ylesandefailimarkus.teema IS 'märkuse teema';
COMMENT ON COLUMN ylesandefailimarkus.ylem_id IS 'viide ülemale märkusele (mida antud kirje kommenteerib)';
COMMENT ON COLUMN ylesandefailimarkus.created IS 'kirje loomise aeg';
COMMENT ON COLUMN ylesandefailimarkus.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN ylesandefailimarkus.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN ylesandefailimarkus.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE ylesandefailimarkus IS 'Ülesandefaili märkused';

-- eis/model/ylesanne/valik.py
COMMENT ON COLUMN valik.id IS 'kirje identifikaator';
COMMENT ON COLUMN valik.seq IS 'valiku järjekorranumber küsimuse sees';
COMMENT ON COLUMN valik.kood IS 'kood, kasutusel hindamismaatriksis';
COMMENT ON COLUMN valik.min_vastus IS 'min vastuste arv';
COMMENT ON COLUMN valik.max_vastus IS 'max vastuste arv';
COMMENT ON COLUMN valik.nimi IS 'valiku sisu';
COMMENT ON COLUMN valik.selgitus IS 'selgitus';
COMMENT ON COLUMN valik.varv IS 'valiku värv (alade värvimise korral)';
COMMENT ON COLUMN valik.kysimus_id IS 'viide küsimusele';
COMMENT ON COLUMN valik.eraldi IS 'kui esinemiste arv on ühest suurem, siis kas pilti kuvada pangas ühekordselt või iga eksemplar eraldi (tekstide lohistamine)';
COMMENT ON COLUMN valik.joondus IS 'lohistatava kirjavahemärgi joondus lünkadeta pangaga lünktekstis: left=const.JUSTIFY_LEFT - vasak; center=const.JUSTIFY_CENTER - kesk; right=const.JUSTIFY_RIGHT - parem';
COMMENT ON COLUMN valik.fikseeritud IS 'kas valiku asukoht on fikseeritud (järjestamise korral)';
COMMENT ON COLUMN valik.kohustuslik_kys IS 'nende küsimuste koodid, mis muutuvad valiku valimisel kohustuslikuks';
COMMENT ON COLUMN valik.sp_peida IS 'nende sisuplokkide tähised, mis valiku valimisel peidetakse';
COMMENT ON COLUMN valik.sp_kuva IS 'nende sisuplokkide tähised, mis valiku valimisel kuvatakse';
COMMENT ON COLUMN valik.max_pallid IS 'valiku maksimaalne pallide arv; kasutusel paarisvastustega küsimustes statistikute jaoks';
COMMENT ON COLUMN valik.created IS 'kirje loomise aeg';
COMMENT ON COLUMN valik.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN valik.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN valik.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE valik IS 'Valikülesande valik.';

COMMENT ON COLUMN valik.kujund IS 'piirkonna kujund: rect, circle, elliplse,...';
COMMENT ON COLUMN valik.nahtamatu IS 'kas piirkond on lahendajale nähtamatu (st kontuuri lahendajale ei kuvata, valikupiirkonna korral)';

-- eis/model/ylesanne/kysimus.py
COMMENT ON COLUMN kysimus.id IS 'kirje identifikaator';
COMMENT ON COLUMN kysimus.kood IS 'vastuse muutuja, QTI responseIdentifier (puudub kolme hulga sobitamises teises hulgas, kahe hulga sobitamises valikute küsimustes 1 ja 2, pangaga lünga valikute küsimuses)';
COMMENT ON COLUMN kysimus.seq IS 'järjekorranumber: kui kysimus on valikuhulk, siis väärtus on 1 või 2 (või 3 või ...)';
COMMENT ON COLUMN kysimus.selgitus IS 'selgitus';
COMMENT ON COLUMN kysimus.sisuplokk_id IS 'viide sisuplokile';
COMMENT ON COLUMN kysimus.sisuobjekt_id IS 'viide küsimusega seotud sisuobjektile nendes ülesandetüüpides: piltide lohistamine (pos), tekstide lohistamine (txpos), piltide lohistamine II (pos2), ristsõna (crossword), multimeedia (media)';
COMMENT ON COLUMN kysimus.objseq IS 'sisuobjektiga seotud küsimuse tähendus: 1=const.OBJSEQ_K - tavaline küsimus; 2=const.OBJSEQ_COUNTER - multimeedia kuulamiste loendur; 3=const.OBJSEQ_POS - multimeedia mängimise järg';
COMMENT ON COLUMN kysimus.vastusesisestus IS 'p-testi vastuste sisestamiseks kasutatav viis: 1 - sarnane sooritajaga';
COMMENT ON COLUMN kysimus.pseudo IS 'kas on pseudoküsimus (ei arvestata valede/õigete vastuste arvu)';
COMMENT ON COLUMN kysimus.segamini IS 'kas segada valikud (QTI shuffle)';
COMMENT ON COLUMN kysimus.max_vastus IS 'max vastuste arv (QTI maxAssociations, maxStrings)';
COMMENT ON COLUMN kysimus.max_vastus_arv IS 'arvutatud max võimalik vastuste arv';
COMMENT ON COLUMN kysimus.min_vastus IS 'min vastuste arv (QTI minAssociations, minStrings)';
COMMENT ON COLUMN kysimus.rtf IS 'kas valikute sisestamisel kasutada kirevat toimetit';
COMMENT ON COLUMN kysimus.rtf_notshared IS 'kas nupuriba on lahtri sees (või ühine, mitme lahtri vahel jagatud)';
COMMENT ON COLUMN kysimus.rtf_enter IS 'kireva teksti korral: 1=const.RTF_ENTER_P - reavahetus teeb uue lõigu; 2=const.RTF_ENTER_BR - reavahetus teeb uue rea';
COMMENT ON COLUMN kysimus.pikkus IS 'avatud lünga pikkus; ristsõna sõna pikkus';
COMMENT ON COLUMN kysimus.max_pikkus IS 'avatud lünga vastuse või avatud vastusega küsimuse maksimaalne pikkus';
COMMENT ON COLUMN kysimus.reakorgus IS 'rea kõrgus avatud lüngas';
COMMENT ON COLUMN kysimus.ridu IS 'avatud lünga korral ridade arv; järjestamise korral: 1 - ühel real; muidu - üksteise all; piltide lohistamise korral: 1 - pildid kuvatakse tausta kõrval; muidu - pildid kuvatakse tausta all; pangaga lünkteksti korral: 2 - pangast saab lohistada kõikide sõnade vahele ja lünki lahendajale ei kuvata; sobitamise valikutehulga 1 korral: küsimuste hulga seq (1 või 2), teine hulk on valikute hulk; muidu - pangast saab lohistada ainult lünkadesse';
COMMENT ON COLUMN kysimus.mask IS 'avatud lünga mask';
COMMENT ON COLUMN kysimus.pos_x IS 'ristsõna ja avatud pildi korral: mitmes veerg';
COMMENT ON COLUMN kysimus.pos_y IS 'ristsõna ja avatud pildi korral: mitmes rida';
COMMENT ON COLUMN kysimus.vorming_kood IS 'avatud lünga vorming';
COMMENT ON COLUMN kysimus.vihje IS 'vihje, mis kuvatakse lahendajale enne vastuse sisestamist';
COMMENT ON COLUMN kysimus.algvaartus IS 'true - vihje jääb vastuse algväärtuseks; false - vihjet kuvatakse ainult tühjal väljal, kuni selles pole kursorit';
COMMENT ON COLUMN kysimus.laad IS 'atribuudi style väärtus avatud lünga korral';
COMMENT ON COLUMN kysimus.joondus IS 'teksti joondus lüngas: left=const.JUSTIFY_LEFT - vasak; center=const.JUSTIFY_CENTER - kesk; right=const.JUSTIFY_RIGHT - parem; justify=const.JUSTIFY_BLOCK - rööp; ristsõna sõnaseletuse korral suund, kuhupoole jääb sõna: left=const.DIRECTION_LEFT - vasakule; down=const.DIRECTION_DOWN - alla; right=const.DIRECTION_RIGHT - paremale; up=const.DIRECTION_UP - üles';
COMMENT ON COLUMN kysimus.n_asend IS 'nupurea asend (matemaatika sisestamise korral), panga asend (pangaga lünga korral): 0 - paremal; 1 ja NULL - all; 10 - paremal ja liigub kursoriga kaasa';
COMMENT ON COLUMN kysimus.sonadearv IS 'kas kokku lugeda ja kuvada vastuses olevate sõnade arv';
COMMENT ON COLUMN kysimus.tekstianalyys IS 'avatud vastusega küsimuse korral: kas hindajale kuvatakse eestikeelse teksti analüüs (EstNLTK)';
COMMENT ON COLUMN kysimus.erand346 IS 'miinuspunkte ei anta juhul, kui on kaks vastust, millest üks on õige ja teine on vale (suur erand EH-346, kasutusel pangaga lüngas)';
COMMENT ON COLUMN kysimus.hindaja_markused IS 'kas hindaja saab teksti sisse märkida vigu ja kommentaare (ksmarkus)';
COMMENT ON COLUMN kysimus.vastus_taisekraan IS 'kas vastuse vaatajal ja hindajal on täisekraani (maksimeerimise) nupp';
COMMENT ON COLUMN kysimus.tulemus_id IS 'viide vastuste hindamise kirjele';
COMMENT ON COLUMN kysimus.evast_edasi IS 'kas vastus kandub edasi kasutamiseks alatesti järgmistes ülesannetes';
COMMENT ON COLUMN kysimus.evast_kasuta IS 'kas kasutada varasemast edasi kantud vastuseid vaikimisi algseisuna';
COMMENT ON COLUMN kysimus.muutmatu IS 'kas lahendajal ei lasta vastust muuta (kasutusel juhul, kui evast_kasuta=true)';
COMMENT ON COLUMN kysimus.ei_arvesta IS 'kas arvestastada vastust tulemustes (true - õpipädevustesti tulemuste vaates seda vastust ei kuvata)';
COMMENT ON COLUMN kysimus.matriba IS 'lahendaja matemaatikaredaktori nupureal kuvatavate ikoonide nimed, komaeraldatud (kui küsimus ei kasuta üle kogu ülesande kehtivat nupuriba)';
COMMENT ON COLUMN kysimus.peida_start IS 'kas peita alustamise nupp (heli salvestamise korral)';
COMMENT ON COLUMN kysimus.peida_paus IS 'kas peita pausi nupp (heli salvestamise korral)';
COMMENT ON COLUMN kysimus.peida_stop IS 'kas peita lõpetamise nupp (heli salvestamise korral)';
COMMENT ON COLUMN kysimus.naita_play IS 'kas lahendamisel kuvada vastuse mahamängimise nupp (heli salvestamise korral)';
COMMENT ON COLUMN kysimus.created IS 'kirje loomise aeg';
COMMENT ON COLUMN kysimus.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN kysimus.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN kysimus.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE kysimus IS 'Küsimus, valikute kogum.
    Kui sisuplokk on tekst, siis küsimus on tekstis olev lünk.
    Kui sisuplokk on sobitusplokk, siis küsimus on valikuhulk.    
    Kui on piltide lohistamise sisuplokk, siis küsimus vastab ühele lohistatavale pildile.';

-- eis/model/ylesanne/yhisfail.py
COMMENT ON COLUMN yhisfail.id IS 'kirje identifikaator';
COMMENT ON COLUMN yhisfail.filename IS 'failinimi';
COMMENT ON COLUMN yhisfail.filesize IS 'faili suurus baitides';
COMMENT ON COLUMN yhisfail.fileversion IS 'versioon';
COMMENT ON COLUMN yhisfail.mimetype IS 'failitüüp';
COMMENT ON COLUMN yhisfail.teema IS 'teema';
COMMENT ON COLUMN yhisfail.yhisfail_kood IS 'faili tüüp, klassifikaator YHISFAIL';
COMMENT ON COLUMN yhisfail.created IS 'kirje loomise aeg';
COMMENT ON COLUMN yhisfail.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN yhisfail.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN yhisfail.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE yhisfail IS 'Ühised failid, mida paljudes ülesannetes saab kasutada.';

-- eis/model/ylesanne/sisuplokk.py
COMMENT ON COLUMN sisuplokk.id IS 'kirje identifikaator';
COMMENT ON COLUMN sisuplokk.tahis IS 'sisuploki tähis, sisuploki lipiku nimetus ülesande sisu koostamise lehel (kui puudub, siis kasutatakse järjekorranumbrit seq)';
COMMENT ON COLUMN sisuplokk.seq IS 'sisuploki järjekorranumber ülesande sees';
COMMENT ON COLUMN sisuplokk.paan_seq IS 'paani järjekorranumber, milles sisuplokk kuvatakse (0 või 1)';
COMMENT ON COLUMN sisuplokk.fikseeritud IS 'kas sisuploki kuvamise järjekord on muutumatu (kui ylesanne.segamini=true)';
COMMENT ON COLUMN sisuplokk.tyyp IS 'sisuploki tüüp: 52 - alustekst; 50 - pilt; 51 - multimeedia; 54 - muu; 53 - mat tekst; 12 - valikvastusega küsimus; 15 - järjestamine; 5 - sobitamine; 18 - seostamine; 16 - lünkvastusega küsimus; 19 - avatud vastusega küsimus; 20 - lünktekst; 4 - pangaga lünktekst; 14 - tekstiosa valik; 90 - matemaatilise teksti sisestamine; 11 - liugur; 1 - kujundi lohistamine pildile; 6 - piltide lohistamine kujunditele; 7 - pildil oleva piirkonna valik; 8 - järjestamine pildil; 9 - koha märkimine pildil; 10 - sobitamine pildil; 3 - joonistamine; 91 - kõne salvestamine; 17 - faili üleslaadimine; 24 - GeoGebra; 25 - GoogleCharts; 26 - ristsõna; 27 - alade värvimine; 28 - pildi avamine';
COMMENT ON COLUMN sisuplokk.alamtyyp IS 'tüübi alamtüüp: diagrammi liik (Google Charts korral); 1 - ühetaolised hindamise seaded kõigil küsimustel (mitme valikuga tabeli korral); N - igal küsimusel oma hindamise seaded (mitme valikuga tabeli korral)';
COMMENT ON COLUMN sisuplokk.nimi IS 'pealkiri või tööjuhend';
COMMENT ON COLUMN sisuplokk.tehn_tookask IS 'tehniline töökäsk';
COMMENT ON COLUMN sisuplokk.tookask_kood IS 'tehnilise töökäsu klassifikaator';
COMMENT ON COLUMN sisuplokk.naide IS 'kas sisuplokk on vastuse näide (siis kuvatakse õige vastus alati lahendajale ja selle ploki eest palle ei anta)';
COMMENT ON COLUMN sisuplokk.sisu IS 'toimetajale näidatav sisu';
COMMENT ON COLUMN sisuplokk.sisuvaade IS 'lahendajale näidatav sisu';
COMMENT ON COLUMN sisuplokk.ylesanne_id IS 'viide ülesandele';
COMMENT ON COLUMN sisuplokk.ymardamine IS 'kas sisuploki punktide summa ümardada';
COMMENT ON COLUMN sisuplokk.min_pallid IS 'sisuploki minimaalne võimalik toorpunktide arv (kasutusel mitme küsimusega sisuplokis); kui puudub, siis ei ole piiri';
COMMENT ON COLUMN sisuplokk.max_pallid IS 'sisuploki maksimaalne võimalik toorpunktide arv (kasutusel mitme küsimusega sisuplokis); kui puudub, siis ei ole sisuplokil oma piiri';
COMMENT ON COLUMN sisuplokk.staatus IS 'kasutusel ja nähtav või mitte: 1 - kuvatakse oma kohal nähtavalt; 0 - ei kuvata oma kohal (fail, millele viidatakse mujalt URLiga); 2=const.B_STAATUS_NAHTAMATU - kuvatakse oma kohal algselt nähtamatult';
COMMENT ON COLUMN sisuplokk.reanr IS 'alusteksti korral: kas kuvada lahendajale teksti reanumbrid (1,6,11,...)';
COMMENT ON COLUMN sisuplokk.kopikeeld IS 'alusteksti korral: kas takistada lahendajal teksti kopeerida';
COMMENT ON COLUMN sisuplokk.kleepekeeld IS 'avatud teksti korral: kas takistada lahendajal teksti väljale kleepida';
COMMENT ON COLUMN sisuplokk.kommenteeritav IS 'alusteksti korral: kas lahendaja saab lahendamise ajal enda jaoks kommentaare märkida';
COMMENT ON COLUMN sisuplokk.wirismath IS 'kas tekst kasutab WIRIS matemaatikaredaktorit (alusteksti korral)';
COMMENT ON COLUMN sisuplokk.laius IS 'veergude arv (ristsõna korral)';
COMMENT ON COLUMN sisuplokk.korgus IS 'ridade arv (ristsõna korral)';
COMMENT ON COLUMN sisuplokk.suurus IS 'ristsõna ruudu suurus pikslites';
COMMENT ON COLUMN sisuplokk.kujundus IS 'kujundus: 1=const.KUJUNDUS_TAUSTATA - tekstiosa valik ilma halli taustata (tekstiosa valiku korral)';
COMMENT ON COLUMN sisuplokk.piiraeg IS 'küsimuse vastamiseks lubatud aeg sekundites (heli salvestamise korral)';
COMMENT ON COLUMN sisuplokk.hoiatusaeg IS 'mitu sekundit enne piiraja täitumist kuvada loendur punasena (heli salvestamise korral)';
COMMENT ON COLUMN sisuplokk.tahemargid IS 'originaalkeeles sisuploki tähemärkide arv (originaalkeeles)';
COMMENT ON COLUMN sisuplokk.nahtavuslogi IS 'kas salvestada sisuploki nähtavaks tegemiste ja peitmiste aeg';
COMMENT ON COLUMN sisuplokk.varvimata IS 'kas jätta vastused rohelise/punase värviga värvimata (kasutusel siis, kui õige/vale ei saa kuvada)';
COMMENT ON COLUMN sisuplokk.pausita IS 'kas pausile panek on keelatud (heli salvestamise korral)';
COMMENT ON COLUMN sisuplokk.select_promptita IS 'kas peita valikvälja tühja valiku prompt "--Vali--" (valikvastusega lünga korral)';
COMMENT ON COLUMN sisuplokk.autostart_opt IS 'automaatne algus (heli salvestamise korral): AUTOSTART_LOAD=L - ülesande avamisel; AUTOSTART_SEQ=S - eelmise salvestuse või multimeedia lõppemisel; AUTOSTART_MEDIASTART=H - mistahes eespool oleva multimeedia mängimisega koos; AUTOSTART_MEDIA=M - mistahes multimeedia lõppemisel';
COMMENT ON COLUMN sisuplokk.created IS 'kirje loomise aeg';
COMMENT ON COLUMN sisuplokk.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN sisuplokk.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN sisuplokk.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE sisuplokk IS 'Ülesande sisuplokk. Ühel ülesandel on mitu sisuplokki.';

-- eis/model/ylesanne/__init__.py
-- eis/model/ylesanne/ylesanne.py
COMMENT ON COLUMN ylesanne.id IS 'kirje identifikaator';
COMMENT ON COLUMN ylesanne.cache_valid IS 'hetk, millest varem puhverdatud õigus vajab uuendamist (muudetakse ligipääsuõiguste muutmisel)';
COMMENT ON COLUMN ylesanne.nimi IS 'ülesande pealkiri';
COMMENT ON COLUMN ylesanne.kood IS 'ülesande kood, väline ID (QTI ja CSV import-eksport)';
COMMENT ON COLUMN ylesanne.staatus IS 'olek: 1 - koostamisel; 2 - peatatud; 3 - eeltest; 4 - test; 5 - ankur; 6 - avalik; 7 - pedagoogidele; 8 - arhiveeritud; 9 - üleandmiseks; 10 - valmis kasutamiseks; 20 - ülesannete mall; 30 - ülesannete mall avalikus vaates kasutamiseks; 31 - avalikus vaates koostatud ülesanne koostamisel; 34 - avalikus vaates koostatud ülesanne valmis; 38 - avalikus vaates koostatud ülesanne arhiveeritud';
COMMENT ON COLUMN ylesanne.salastatud IS '0 - pole salastatud; 2 - loogiline salastatus; 3 - krüptitud (enam ei saa)';
COMMENT ON COLUMN ylesanne.lukus IS 'muutmise lukustus: NULL - ülesanne pole lukus; 1=const.LUKUS_KINNITATUD - ülesanne on kinnitatud komplektis ja muuta võib ainult ülesannete hindamise osa; 2=const.LUKUS_KATSE_SOORITATUD - ülesannet on sooritatud KATSE testimiskorral, ei ole hinnatud, muuta võib ainult hindamise osa, muutja saab lukust lahti võtta; 3=const.LUKUS_KATSE_HINNATUD - ülesannet on sooritatud ja hinnatud ainult KATSE testimiskorral, midagi ei või muuta, muutja saab lukust lahti võtta; 4=const.LUKUS_SOORITATUD - ülesannet on kasutatud mitte-KATSE testimiskorral või testimiskorrata, hinnatud ei ole, muuta võib ainult hindamise osa, lukust lahti võtmiseks vaja eriõigusi; 5=const.LUKUS_HINNATUD - ülesannet on kasutatud mitte-KATSE testimiskorral või testimiskorrata, on hinnatud, muuta ei või midagi, lukust lahti võtmiseks on vaja eriõigusi';
COMMENT ON COLUMN ylesanne.logitase IS 'logitase: 1 - logida õiguste andmine; 2 - logida kõigi andmete muutmine';
COMMENT ON COLUMN ylesanne.max_pallid IS 'ülesande maksimaalne võimalik toorpunktide arv: aspektideta ülesande korral küsimuste toorpunktide summa; aspektidega ülesande korral aspektide toorpunktide ja kaalude korrutiste summa';
COMMENT ON COLUMN ylesanne.ymardamine IS 'kas tulemuseks arvutatud pallid ümardada';
COMMENT ON COLUMN ylesanne.raskus IS 'ülesande raskus, vaikimisi NULL, saab kopeerida ülesannete statistikast ülesande kasutamise ajaloo vormil';
COMMENT ON COLUMN ylesanne.raskus_kood IS 'koostaja ette antud raskus: -1=const.RASKUS_KERGE - kerge; 0=const.RASKUS_KESKMINE - keskmine (vaikimisi); 1=const.RASKUS_RASKE - raske';
COMMENT ON COLUMN ylesanne.eristusindeks IS 'eristusindeks, -1..1';
COMMENT ON COLUMN ylesanne.arvamisindeks IS 'äraarvamisindeks, 0..1 (vastuse juhusliku äraarvamise tõenäosus)';
COMMENT ON COLUMN ylesanne.lahendatavus IS 'keskmine lahendusprotsent, 0..100, (keskmine pallide arv / max pallide arv)*100%';
COMMENT ON COLUMN ylesanne.keeletase_kood IS 'keeleoskuse tase, klassifikaator KEELETASE';
COMMENT ON COLUMN ylesanne.aste_kood IS 'peamine kooliaste, klassifikaator ASTE';
COMMENT ON COLUMN ylesanne.aste_mask IS 'kooliastmed/erialad kodeeritud bittide summana; peamiste kooliastmete korral on biti jrk nr: 0 - I aste; 1 - II aste; 2 - III aste; 3 - gümnaasium; 4 - ülikool; muudel juhtudel on klassifikaatori kood biti järjekorranumbriks';
COMMENT ON COLUMN ylesanne.vastvorm_kood IS 'vastamise vorm, klassifikaator VASTVORM';
COMMENT ON COLUMN ylesanne.hindamine_kood IS 'hindamise meetod, klassifikaator HINDAMINE';
COMMENT ON COLUMN ylesanne.arvutihinnatav IS 'kas ülesanne on üleni arvutiga hinnatav (arvutihinnatava ülesande kõik küsimused peavad olema arvutihinnatavad; mitte-arvutihinnatav ülesanne võib sisaldada ka arvutihinnatavaid küsimusi)';
COMMENT ON COLUMN ylesanne.adaptiivne IS 'diagnoosiva testi ülesanne';
COMMENT ON COLUMN ylesanne.ptest IS 'sobivus p-testiks (paber-pliiats-testiks)';
COMMENT ON COLUMN ylesanne.etest IS 'sobivus e-testiks';
COMMENT ON COLUMN ylesanne.nutiseade IS 'sobivus nutiseadmele';
COMMENT ON COLUMN ylesanne.pallemaara IS 'kas avaliku vaate testi koostaja saab ise ülesande palle määrata';
COMMENT ON COLUMN ylesanne.kvaliteet_kood IS 'ülesande kvaliteedimärk';
COMMENT ON COLUMN ylesanne.markus IS 'märkused';
COMMENT ON COLUMN ylesanne.marksonad IS 'otsingu märksõnad';
COMMENT ON COLUMN ylesanne.autor IS 'ülesande autor (informatiivne)';
COMMENT ON COLUMN ylesanne.konesyntees IS 'kas võimaldada kõnesünteesi';
COMMENT ON COLUMN ylesanne.rp_reeglid IS 'ResultProcessing XML-kujul, QTI import-eksport';
COMMENT ON COLUMN ylesanne.tulemusmall_id IS 'viide QTI tulemusmalli kirjele';
COMMENT ON COLUMN ylesanne.kuva_tulemus IS 'kas kuvada lahendajale tema tulemus (tagasisidega ülesande korral)';
COMMENT ON COLUMN ylesanne.on_tagasiside IS 'kas ülesande tulemus esitada tagasisidena';
COMMENT ON COLUMN ylesanne.on_pallid IS 'kas tulemused kuvada pallides või protsentides (tagasiside korral); kui on NULL, siis tehakse nii, nagu vormil vaikimisi';
COMMENT ON COLUMN ylesanne.yl_tagasiside IS 'tagasiside terve ülesande kohta sõltumata tulemusest';
COMMENT ON COLUMN ylesanne.lang IS 'põhikeel, keelte 2-kohaline klassifikaator';
COMMENT ON COLUMN ylesanne.skeeled IS 'ülesande keelte koodid eraldatuna tühikuga';
COMMENT ON COLUMN ylesanne.disain_ver IS 'CSS disaini versioon: 1=const.DISAIN_EIS1 - EIS 1 disain (kuni 2020); 2=const.DISAIN_HDS - HITSA disain (alates 2020)';
COMMENT ON COLUMN ylesanne.fixkoord IS 'fikseeritud koordinaatidega kujundus (hindamise välju ei või paigutada ülesande sisse, sest need võivad midagi kinni katta)';
COMMENT ON COLUMN ylesanne.alus_id IS 'viide alusülesandele (kui antud ülesanne on loodud alusülesande koopiana)';
COMMENT ON COLUMN ylesanne.paanide_arv IS 'paanide (ekraanipoolte) arv sisuplokkide kuvamisel';
COMMENT ON COLUMN ylesanne.paan1_laius IS 'vasaku paani (ekraanipoole) laius protsentides';
COMMENT ON COLUMN ylesanne.segamini IS 'kas sisuplokid kuvatakse juhuslikus järjekorras (välja arvatud need, millel on sisuplokk.fikseeritud=true)';
COMMENT ON COLUMN ylesanne.tahemargid IS 'ülesande tähemärkide arv (originaalkeeles)';
COMMENT ON COLUMN ylesanne.spellcheck IS 'kas lahendajale lubada sisestusväljades brauseri speller';
COMMENT ON COLUMN ylesanne.on_juhuarv IS 'kas ülesandes esineb juhuarvu sisuplokk või segatavate valikutega küsimus';
COMMENT ON COLUMN ylesanne.kasutusmaar IS 'mitmes testis on ülesanne kasutusel';
COMMENT ON COLUMN ylesanne.lahendada_lopuni IS 'kas üksikülesannet lahendades on vajalik kõik väljad täita ja ülesanne lõpuni lahendada';
COMMENT ON COLUMN ylesanne.valimata_vastused IS 'kas arvestada valede ja õigete vastuste arvus ka valimata õigeid ja valesid hindamismaatriksi kirjeid (psühholoogilise testi jaoks)';
COMMENT ON COLUMN ylesanne.dlgop_aeg IS 'mitu sekundit oodata enne dialoogiakna avamist (õpipädevuse ülesannetes)';
COMMENT ON COLUMN ylesanne.dlgop_tekst IS 'dialoogiakna tekst, kui vastamist ei alustata ooteaja jooksul (õpipädevuse ülesannetes)';
COMMENT ON COLUMN ylesanne.dlgop_ei_edasi IS 'mitme ülesande võrra edasi liikuda, kui dialoogiaknas vastatakse eitavalt (õpipädevuse ülesannetes)';
COMMENT ON COLUMN ylesanne.evast_edasi IS 'kas kanda selle ülesande vastuseid edasi järgmistesse ülesannetesse';
COMMENT ON COLUMN ylesanne.evast_kasuta IS 'kas kasutada varasemast edasi kantud vastuseid vaikimisi algseisuna';
COMMENT ON COLUMN ylesanne.created IS 'kirje loomise aeg';
COMMENT ON COLUMN ylesanne.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN ylesanne.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN ylesanne.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE ylesanne IS 'Ülesanne';

-- eis/model/ylesanne/plokimarkus.py
COMMENT ON COLUMN plokimarkus.id IS 'kirje identifikaator';
COMMENT ON COLUMN plokimarkus.sisuplokk_id IS 'viide sisuplokile';
COMMENT ON COLUMN plokimarkus.kasutaja_id IS 'viide kasutajale';
COMMENT ON COLUMN plokimarkus.aeg IS 'märkuse kirjutamise aeg';
COMMENT ON COLUMN plokimarkus.sisu IS 'märkuse sisu';
COMMENT ON COLUMN plokimarkus.teema IS 'märkuse teema';
COMMENT ON COLUMN plokimarkus.ylem_id IS 'viide ülemale märkusele (mida antud märkus kommenteerib)';
COMMENT ON COLUMN plokimarkus.created IS 'kirje loomise aeg';
COMMENT ON COLUMN plokimarkus.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN plokimarkus.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN plokimarkus.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE plokimarkus IS 'Sisuploki märkused';

-- eis/model/ylesanne/valikvastus.py
COMMENT ON COLUMN valikvastus.id IS 'kirje identifikaator';
COMMENT ON COLUMN valikvastus.tulemus_id IS 'viide tulemuse kirjele';
COMMENT ON COLUMN valikvastus.maatriks IS 'mitmes hindamismaatriks (üldjuhul alati 1, aga kolme hulgaga sobitamisel on olemas ka 2 ja 3)';
COMMENT ON COLUMN valikvastus.valik1_kysimus_id IS 'kysimus_id, mille järgi leida tabelist Valik kvsisu.kood1 kirje';
COMMENT ON COLUMN valikvastus.valik2_kysimus_id IS 'kysimus_id, mille järgi leida tabelist Valik kvsisu.kood2 kirje';
COMMENT ON COLUMN valikvastus.vahetada IS 'kas statistikute vaates statvastus vahetada valik1 ja valik2 omavahel';
COMMENT ON COLUMN valikvastus.statvastuses IS 'kas vastust näidata statistikutele statvastuse vaates';
COMMENT ON COLUMN valikvastus.mittevastus IS 'kas vastused kuvada Exceli väljavõttes: null - kuvada; true - kuvada ainult punktid, mitte vastused';
COMMENT ON COLUMN valikvastus.sisujarjestus IS 'kas on järjestuse tüüpi küsimus (kvsisu.sisu on moodustatud valik1 koodide järjestusena, semikoolonitega eraldatult)';
COMMENT ON COLUMN valikvastus.paarina IS 'NULL - vastus pole paar; false - vastus on paar, aga kuvatakse mitme eraldi küsimusena; true - vastus on paar ja kuvatakse paarina';
COMMENT ON COLUMN valikvastus.analyys1 IS 'kas statvastuses kasutada kvsisu analyysikirjet ning arvestada max_vastus=1';
COMMENT ON COLUMN valikvastus.created IS 'kirje loomise aeg';
COMMENT ON COLUMN valikvastus.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN valikvastus.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN valikvastus.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE valikvastus IS 'Andmed valikvastuse koodi seostamiseks valiku kirjega, 
    et statistikutel oleks lihtsam vastuste sisu lugeda.
    Valikvastused on tabelites kvsisu ja hindamismaatriks esitatud koodide abil.
    Käesolevas tabelis kirjeldatakse, millise küsimuse valikute seast on vaja neid koode otsida.';

-- eis/model/ylesanne/ylesandeaine.py
COMMENT ON COLUMN ylesandeaine.id IS 'kirje identifikaator';
COMMENT ON COLUMN ylesandeaine.ylesanne_id IS 'viide ülesandele';
COMMENT ON COLUMN ylesandeaine.seq IS 'õppeaine järjekorranumber, ülesande peamise õppeaine korral 0';
COMMENT ON COLUMN ylesandeaine.aine_kood IS 'õppeaine, klassifikaator AINE';
COMMENT ON COLUMN ylesandeaine.oskus_kood IS 'osaoskus, klassifikaator OSKUS';
COMMENT ON COLUMN ylesandeaine.created IS 'kirje loomise aeg';
COMMENT ON COLUMN ylesandeaine.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN ylesandeaine.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN ylesandeaine.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE ylesandeaine IS 'Ülesande õppeaine';

-- eis/model/ylesanne/hindamisaspekt.py
COMMENT ON COLUMN hindamisaspekt.id IS 'kirje identifikaator';
COMMENT ON COLUMN hindamisaspekt.ylesanne_id IS 'viide ülesandele';
COMMENT ON COLUMN hindamisaspekt.aine_kood IS 'õppeaine, mille hindamisaspekt see on (peab olema ka tabelis Ylesandeaine)';
COMMENT ON COLUMN hindamisaspekt.aspekt_kood IS 'viide aspektile, klassifikaator ASPEKT';
COMMENT ON COLUMN hindamisaspekt.max_pallid IS 'max toorpunktide arv, mida selle aspektiga hinnatakse';
COMMENT ON COLUMN hindamisaspekt.pintervall IS 'lubatud punktide intervall (käsitsi hindamisel)';
COMMENT ON COLUMN hindamisaspekt.kaal IS 'kaal, millega aspekti toorpunktid korrutatakse, kui arvutatakse kogu ülesande toorpunkte';
COMMENT ON COLUMN hindamisaspekt.hindamisjuhis IS 'kirjeldus (kui puudub, siis kasutatakse vaikimisi kirjeldusena aspektide klassifikaatoris olevat)';
COMMENT ON COLUMN hindamisaspekt.seq IS 'aspekti järjekord ülesandes (sh hindamisprotokollil)';
COMMENT ON COLUMN hindamisaspekt.kuvada_statistikas IS 'kas kuvada aspekt statistikaraportis';
COMMENT ON COLUMN hindamisaspekt.pkirj_sooritajale IS 'kas kuvada punktide kirjeldused sooritajale';
COMMENT ON COLUMN hindamisaspekt.created IS 'kirje loomise aeg';
COMMENT ON COLUMN hindamisaspekt.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN hindamisaspekt.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN hindamisaspekt.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE hindamisaspekt IS 'Ülesandega seotud hindamisaspekt';

-- eis/model/ylesanne/kasutliik.py
COMMENT ON COLUMN kasutliik.id IS 'kirje identifikaator';
COMMENT ON COLUMN kasutliik.kasutliik_kood IS 'kasutusliigi kood, klassifikaator KASUTLIIK';
COMMENT ON COLUMN kasutliik.ylesanne_id IS 'viide ülesandele';
COMMENT ON COLUMN kasutliik.created IS 'kirje loomise aeg';
COMMENT ON COLUMN kasutliik.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN kasutliik.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN kasutliik.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE kasutliik IS 'Ülesande kasutuse liigid';

-- eis/model/ylesanne/sisuobjekt.py
COMMENT ON COLUMN sisuobjekt.id IS 'kirje identifikaator';
COMMENT ON COLUMN sisuobjekt.seq IS 'järjekorranumber sisuplokis';
COMMENT ON COLUMN sisuobjekt.kood IS 'hindamismaatriksis kasutatav kood, QTI responseIdentifier';
COMMENT ON COLUMN sisuobjekt.min_vastus IS 'piltobjekti min esinemiste arv (piltide lohistamine ja piltide lohistamine kujunditele)';
COMMENT ON COLUMN sisuobjekt.max_vastus IS 'piltobjekti max esinemiste arv (piltide lohistamine ja piltide lohistamine kujunditele)';
COMMENT ON COLUMN sisuobjekt.eraldi IS 'kui esinemiste arv on ühest suurem, siis kas pilti kuvada pangas ühekordselt või iga eksemplar eraldi (piltide lohistamine kujunditele)';
COMMENT ON COLUMN sisuobjekt.nahtamatu IS 'kas kuvatakse sisuplokiga määratud asukohas (või on mõeldud mujalt viitamiseks)';
COMMENT ON COLUMN sisuobjekt.segamini IS 'kas lohistavad pildid kuvada juhuslikus järjekorras';
COMMENT ON COLUMN sisuobjekt.asend IS 'lohistatavate piltide asend: 0 - taustast paremal, 1 - tausta all, 2 - taustast vasakul, 3 - taustast üleval';
COMMENT ON COLUMN sisuobjekt.masonry_layout IS 'kas lohistatavad pildid paigutada masonry abil (müürpaigutus)';
COMMENT ON COLUMN sisuobjekt.tiitel IS 'pildi atribuut title (kasutatakse pildi algallikate märkimiseks)';
COMMENT ON COLUMN sisuobjekt.filename IS 'failinimi';
COMMENT ON COLUMN sisuobjekt.filesize IS 'faili suurus baitides';
COMMENT ON COLUMN sisuobjekt.fileversion IS 'versioon';
COMMENT ON COLUMN sisuobjekt.fileurl IS 'faili URL (kui puudub filedata)';
COMMENT ON COLUMN sisuobjekt.mimetype IS 'failitüüp';
COMMENT ON COLUMN sisuobjekt.laius IS 'kuvamisel kasutatav laius';
COMMENT ON COLUMN sisuobjekt.korgus IS 'kuvamisel kasutatav kõrgus';
COMMENT ON COLUMN sisuobjekt.laius_orig IS 'pildi/video tegelik laius';
COMMENT ON COLUMN sisuobjekt.korgus_orig IS 'pildi/video tegelik kõrgus';
COMMENT ON COLUMN sisuobjekt.sisuplokk_id IS 'viide sisuplokile';
COMMENT ON COLUMN sisuobjekt.samafail IS 'sama (mitte-null) väärtusega failid on ühe ja sama faili erinevad formaadid';
COMMENT ON COLUMN sisuobjekt.created IS 'kirje loomise aeg';
COMMENT ON COLUMN sisuobjekt.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN sisuobjekt.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN sisuobjekt.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE sisuobjekt IS 'Ülesande sisus olev fail.
    On seotud sisuplokiga';



COMMENT ON COLUMN sisuobjekt.autostart IS 'kas multimeedia käivitatakse automaatselt';
COMMENT ON COLUMN sisuobjekt.min_kordus IS 'min korduste arv';
COMMENT ON COLUMN sisuobjekt.max_kordus IS 'max korduste arv';
COMMENT ON COLUMN sisuobjekt.isekorduv IS 'kas peale mängimise lõppemist hakkab ise algusest uuesti peale';
COMMENT ON COLUMN sisuobjekt.pausita IS 'kas pausile panek on keelatud';
COMMENT ON COLUMN sisuobjekt.player IS 'MP3 ja MP4 mängija: 1 - brauseri mängija; 0 - jPlayer';
COMMENT ON COLUMN sisuobjekt.nocontrols IS 'kas kuvada <audio> ilma nuppudeta, ainult mängimise nupp';
COMMENT ON COLUMN sisuobjekt.mediainfo IS 'MediaInfo dict';

-- eis/model/ylesanne/ylesandefail.py
COMMENT ON COLUMN ylesandefail.id IS 'kirje identifikaator';
COMMENT ON COLUMN ylesandefail.filename IS 'failinimi';
COMMENT ON COLUMN ylesandefail.filesize IS 'faili suurus baitides';
COMMENT ON COLUMN ylesandefail.fileurl IS 'faili URL (kui puudub filedata)';
COMMENT ON COLUMN ylesandefail.fileversion IS 'versioon';
COMMENT ON COLUMN ylesandefail.mimetype IS 'failitüüp';
COMMENT ON COLUMN ylesandefail.laius IS 'faili kuvamise laius';
COMMENT ON COLUMN ylesandefail.korgus IS 'faili kuvamise kõrgus';
COMMENT ON COLUMN ylesandefail.ylesanne_id IS 'viide ülesandele';
COMMENT ON COLUMN ylesandefail.created IS 'kirje loomise aeg';
COMMENT ON COLUMN ylesandefail.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN ylesandefail.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN ylesandefail.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE ylesandefail IS 'Ülesande küljes olev fail.
    On seotud ülesandega';





-- eis/model/ylesanne/kyslisa.py
COMMENT ON COLUMN kyslisa.id IS 'kirje identifikaator';
COMMENT ON COLUMN kyslisa.kysimus_id IS 'viide küsimusele';
COMMENT ON COLUMN kyslisa.min_vaartus IS 'liuguri min väärtus';
COMMENT ON COLUMN kyslisa.max_vaartus IS 'liuguri max vääruts';
COMMENT ON COLUMN kyslisa.samm IS 'liuguri samm';
COMMENT ON COLUMN kyslisa.samm_nimi IS 'kas liuguril kuvada sammude skaalat';
COMMENT ON COLUMN kyslisa.tagurpidi IS 'kas liuguri vahemik on tagurpidi';
COMMENT ON COLUMN kyslisa.vertikaalne IS 'kas liugur on vertikaalne';
COMMENT ON COLUMN kyslisa.yhik IS 'liuguriga mõõdetava ühiku nimetus';
COMMENT ON COLUMN kyslisa.asend_vasakul IS 'kas kuvada vastus vasakul';
COMMENT ON COLUMN kyslisa.asend_paremal IS 'kas kuvada vastus paremal';
COMMENT ON COLUMN kyslisa.mimetype IS 'oodatav failitüüp';
COMMENT ON COLUMN kyslisa.algus IS 'teekonna sisuplokis algusruudud (nt 1_3)';
COMMENT ON COLUMN kyslisa.labimatu IS 'teekonna sisuplokis läbimatud ruudud (nt 2_0;3_1;1_1)';
COMMENT ON COLUMN kyslisa.lopp IS 'teekonna sisuplokis lõpuruudud (nt 1_3)';
COMMENT ON COLUMN kyslisa.created IS 'kirje loomise aeg';
COMMENT ON COLUMN kyslisa.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN kyslisa.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN kyslisa.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE kyslisa IS 'Täiendavad andmed lahtri juurde (liuguri ja faili laadimise korral)';

-- eis/model/ylesanne/salaylesanne.py
COMMENT ON COLUMN salaylesanne.id IS 'kirje identifikaator';
COMMENT ON COLUMN salaylesanne.parool IS 'SK sertifikaatidele krüptitud parool .cdoc (<EncryptedData>) kujul';
COMMENT ON COLUMN salaylesanne.data IS 'parooliga krüptitud andmed';
COMMENT ON COLUMN salaylesanne.ylesanne_id IS 'viide ülesandele';
COMMENT ON COLUMN salaylesanne.created IS 'kirje loomise aeg';
COMMENT ON COLUMN salaylesanne.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN salaylesanne.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN salaylesanne.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE salaylesanne IS 'Krüptitud ülesande sisu';

-- eis/model/ylesanne/ylesandelogi.py
COMMENT ON COLUMN ylesandelogi.id IS 'kirje identifikaator';
COMMENT ON COLUMN ylesandelogi.aeg IS 'logi aeg';
COMMENT ON COLUMN ylesandelogi.liik IS 'logitava olemi kirjeldus';
COMMENT ON COLUMN ylesandelogi.vanad_andmed IS 'vanad andmed';
COMMENT ON COLUMN ylesandelogi.uued_andmed IS 'uued andmed';
COMMENT ON COLUMN ylesandelogi.ylesanne_id IS 'viide ülesandele';
COMMENT ON COLUMN ylesandelogi.kasutaja_id IS 'viide kasutajale';
COMMENT ON COLUMN ylesandelogi.created IS 'kirje loomise aeg';
COMMENT ON COLUMN ylesandelogi.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN ylesandelogi.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN ylesandelogi.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE ylesandelogi IS 'Ülesande koostamise ajalugu';

-- eis/model/ylesanne/motlemistasand.py
COMMENT ON COLUMN motlemistasand.id IS 'kirje identifikaator';
COMMENT ON COLUMN motlemistasand.kood IS 'mõtlemistasandi kood, klassifikaator MOTE';
COMMENT ON COLUMN motlemistasand.ylesanne_id IS 'viide ülesandele';
COMMENT ON COLUMN motlemistasand.created IS 'kirje loomise aeg';
COMMENT ON COLUMN motlemistasand.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN motlemistasand.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN motlemistasand.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE motlemistasand IS 'Ülesande mõtlemistasandid';

-- eis/model/ylesanne/ylesandeisik.py
COMMENT ON COLUMN ylesandeisik.id IS 'kirje identifikaator';
COMMENT ON COLUMN ylesandeisik.kasutaja_id IS 'viide kasutajale';
COMMENT ON COLUMN ylesandeisik.kasutajagrupp_id IS 'viide kasutajagrupile';
COMMENT ON COLUMN ylesandeisik.ylesanne_id IS 'viide ülesandele';
COMMENT ON COLUMN ylesandeisik.kehtib_alates IS 'õiguste kehtimise algus';
COMMENT ON COLUMN ylesandeisik.kehtib_kuni IS 'õiguste kehtimise lõpp';
COMMENT ON COLUMN ylesandeisik.created IS 'kirje loomise aeg';
COMMENT ON COLUMN ylesandeisik.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN ylesandeisik.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN ylesandeisik.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE ylesandeisik IS 'Ülesandega seotud isik';

-- eis/model/test/salatestiisik.py
COMMENT ON COLUMN salatestiisik.id IS 'kirje identifikaator';
COMMENT ON COLUMN salatestiisik.salatest_id IS 'viide krüptitud andmete kirjele';
COMMENT ON COLUMN salatestiisik.kasutaja_id IS 'viide kasutajale, kes saab lahti krüptida';
COMMENT ON COLUMN salatestiisik.created IS 'kirje loomise aeg';
COMMENT ON COLUMN salatestiisik.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN salatestiisik.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN salatestiisik.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE salatestiisik IS 'Krüptitud testi lahti krüptida suutev isik';

-- eis/model/test/testitase.py
COMMENT ON COLUMN testitase.id IS 'kirje identifikaator';
COMMENT ON COLUMN testitase.test_id IS 'viide testile';
COMMENT ON COLUMN testitase.aine_kood IS 'õppeaine, klassifikaator AINE (dubleerib välja Test.aine_kood)';
COMMENT ON COLUMN testitase.keeletase_kood IS 'keeleoskuse tase (riigikeele eksami korral), klassifikaator KEELETASE';
COMMENT ON COLUMN testitase.pallid IS 'minimaalne tulemuse protsent sooritajale võimalikust kogutulemusest (mitte pallide arv!), mis peab olema tulemuseks, et vastata antud tasemele; kui on NULL, siis süsteem taset ei anna';
COMMENT ON COLUMN testitase.seq IS 'mitmes tase (kõige kõrgem peab olema 1, järgmine on 2)';
COMMENT ON COLUMN testitase.created IS 'kirje loomise aeg';
COMMENT ON COLUMN testitase.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN testitase.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN testitase.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE testitase IS 'Testiga hinnatav keeleoskuse tase (võib sõltuda saadud tulemusest, näiteks: 75-100p on B2, 50-74p on B1, alla 50p taset pole).
    Test annab vastava taseme ainult juhul, kui testiliik on rahvusvaheline eksam, riigieksam, põhikooli eksam või tasemeeksam.
    Muudel juhtudel (nt eeltest) on tase kasutusel ainult testi kirjeldamiseks.';

-- eis/model/test/testikursus.py
COMMENT ON COLUMN testikursus.id IS 'kirje identifikaator';
COMMENT ON COLUMN testikursus.test_id IS 'viide testile';
COMMENT ON COLUMN testikursus.kursus_kood IS 'lai või kitsas (matemaatika korral), klassifikaator KURSUS';
COMMENT ON COLUMN testikursus.aine_kood IS 'õppeaine, klassifikaator AINE (dubleerib test.aine_kood)';
COMMENT ON COLUMN testikursus.tunnaine_kood IS 'õppeaine nimetus tunnistusel, klassifikaator TUNNAINE';
COMMENT ON COLUMN testikursus.max_pallid IS 'max hindepallide arv antud kursuse korral';
COMMENT ON COLUMN testikursus.created IS 'kirje loomise aeg';
COMMENT ON COLUMN testikursus.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN testikursus.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN testikursus.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE testikursus IS 'Tunnistusele märgitav testi õppeaine sõltuvalt valitud kursusest';

-- eis/model/test/eeltest_komplekt.py
COMMENT ON TABLE eeltest_komplekt IS '';

-- eis/model/test/grupiylesanne.py
COMMENT ON COLUMN grupiylesanne.id IS 'kirje identifikaator';
COMMENT ON COLUMN grupiylesanne.ylesandegrupp_id IS 'viide ülesandegrupile';
COMMENT ON COLUMN grupiylesanne.valitudylesanne_id IS 'viide testi valitud ülesandele';
COMMENT ON COLUMN grupiylesanne.created IS 'kirje loomise aeg';
COMMENT ON COLUMN grupiylesanne.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN grupiylesanne.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN grupiylesanne.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE grupiylesanne IS 'Ülesannete kuulumine gruppidesse';

-- eis/model/test/tagasisidevorm.py
COMMENT ON COLUMN tagasisidevorm.id IS 'kirje identifikaator';
COMMENT ON COLUMN tagasisidevorm.nimi IS 'vormi nimi';
COMMENT ON COLUMN tagasisidevorm.test_id IS 'viide testile (puudub malli alamosa korral)';
COMMENT ON COLUMN tagasisidevorm.liik IS 'vormi liik: NULL - vormi alamosa; 0 - testi kirjeldus; 1 - õpilase tagasisidevorm; 2 - grupi tagasisidevorm klasside tulemuste sakil; 3 - õpetaja/läbiviija tagasisidevorm ühe õpilase kohta; 4 - grupi tagasisidevorm õpilaste tulemuse sakil';
COMMENT ON COLUMN tagasisidevorm.kursus_kood IS 'lai või kitsas (matemaatika korral), klassifikaator KURSUS';
COMMENT ON COLUMN tagasisidevorm.ylem_id IS 'viide ülemale väärtusele (alamosa korral)';
COMMENT ON COLUMN tagasisidevorm.sisu IS 'tagasisidevormi sisu';
COMMENT ON COLUMN tagasisidevorm.sisu_jatk IS 'tagasisidevormi täiendatud sisu, mis ilmub klikkides "Näita rohkem" (kasutusel testi kirjelduse korral)';
COMMENT ON COLUMN tagasisidevorm.staatus IS 'vormi olek: 0=const.B_STAATUS_KEHTETU - ei ole kasutusel; 1=const.B_STAATUS_KEHTIV - kehtiv käsitsi koostatud vorm; 4=const.B_STAATUS_AUTO - automaatselt loodud vorm';
COMMENT ON COLUMN tagasisidevorm.lang IS 'keel (kui puudub, siis ei sõltu soorituskeelest)';
COMMENT ON COLUMN tagasisidevorm.seq IS 'vormi alamosa korral alamosa jrk nr';
COMMENT ON COLUMN tagasisidevorm.nahtav_opetajale IS 'kas õpetaja võib näha (õpilase tagasiside korral)';
COMMENT ON COLUMN tagasisidevorm.created IS 'kirje loomise aeg';
COMMENT ON COLUMN tagasisidevorm.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN tagasisidevorm.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN tagasisidevorm.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE tagasisidevorm IS 'Testi tagasisidevormi mall';

-- eis/model/test/normipunkt.py
COMMENT ON COLUMN normipunkt.id IS 'kirje identifikaator';
COMMENT ON COLUMN normipunkt.seq IS 'järjekorranumber vanema sees (testiosa korral)';
COMMENT ON COLUMN normipunkt.testiosa_id IS 'viide testiosale (kui on testiga seotud)';
COMMENT ON COLUMN normipunkt.alatest_id IS 'viide alatestile (alatesti või testiylesande normipunktide korral, lisaks on antud testiosa_id)';
COMMENT ON COLUMN normipunkt.testiylesanne_id IS 'viide testiülesandele (testiülesande normipunktide korral, lisaks on antud testiosa_id)';
COMMENT ON COLUMN normipunkt.ylesanne_id IS 'viide ülesandele (ülesande normipunktide korral, mis pole seotud testiga, st testiosa_id on NULL)';
COMMENT ON COLUMN normipunkt.ylesandegrupp_id IS 'viide ülesandegrupile (diagnoosiva testi (tüüp 2) korral)';
COMMENT ON COLUMN normipunkt.nimi IS 'nimetus, mida tulemuste kuvamisel kasutatakse';
COMMENT ON COLUMN normipunkt.kood IS 'kood, mida kasutada valemites';
COMMENT ON COLUMN normipunkt.lang IS 'soorituskeele kood, määrab õpipädevuse normipunkti korral, millistele sooritajatele kirje kehtib (kui on tühi, siis kehtib kõigis keeltes sooritajatele)';
COMMENT ON COLUMN normipunkt.normityyp IS 'normipunktide (protsentiilide) tüüp: 1=const.NORMITYYP_PALLID - pallid; 2=const.NORMITYYP_SUHE - õigete vastuste suhe kõikidesse vastustesse; 3=const.NORMITYYP_AEG - aeg sekundites; 4=const.NORMITYYP_VEAD - vigade arv; 5=const.NORMITYYP_VASTUS - antud koodiga küsimuse vastus; 6=const.NORMITYYP_KPALLID - antud koodiga küsimuste keskmine pallide arv; 7=const.NORMITYYP_VALEM - valem vastustest; 8=const.NORMITYYP_PROTSENT - protsent maksimaalsest võimalikust tulemusest; 9=const.NORMITYYP_PUNKTID - küsimuse toorpunktid';
COMMENT ON COLUMN normipunkt.on_opilane IS 'kas normipunkt kuvatakse õpilase individuaalsel profiililehel';
COMMENT ON COLUMN normipunkt.on_grupp IS 'kas normipunkt kuvatakse grupi profiililehel';
COMMENT ON COLUMN normipunkt.kysimus_kood IS 'avaldis: küsimuse kood, kui protsentiil käib küsimuse kohta (alatesti korral liidetakse alatesti vastava koodiga küsimuste vastused); küsimuse baastüüp peab olema "täisarv"; valemi korral valem nt TASK_1.K01 + TASK_2.K02';
COMMENT ON COLUMN normipunkt.on_oigedvaled IS 'kas kuvada profiililehel õigete ja valede vastuste arvud (koolipsühholoogi testi korral)';
COMMENT ON COLUMN normipunkt.pooratud IS 'kas on pööratud (kahanev), nt aja ja vigade arvu korral';
COMMENT ON COLUMN normipunkt.pooratud_varv IS 'kas värvid kuvada teistpidi, st tumedast heledani, vaikimisi on heledast tumedani (õpipädevuse testis)';
COMMENT ON COLUMN normipunkt.varv2_mk IS 'kas kahe sooritusrühma kattumisel kasutada äärmise rühma värvi (vaikimisi kuvatakse keskmise rühma värv) (õpipädevuse testis)';
COMMENT ON COLUMN normipunkt.min_vaartus IS 'min väärtus';
COMMENT ON COLUMN normipunkt.max_vaartus IS 'max väärtus';
COMMENT ON COLUMN normipunkt.min_max IS 'võimalikud väärtused, komaga eraldatud (õpipädevuse testis)';
COMMENT ON COLUMN normipunkt.tahemargid IS 'tähemärkide arv originaalkeeles';
COMMENT ON COLUMN normipunkt.alatestigrupp_id IS 'viide grupile (testiosa normipunktide korral)';
COMMENT ON COLUMN normipunkt.created IS 'kirje loomise aeg';
COMMENT ON COLUMN normipunkt.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN normipunkt.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN normipunkt.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE normipunkt IS 'Testisoorituse tagasiside andmiseks arvutatavate suuruste kirjeldus.
    Psühholoogilise testi alatesti või testiülesande normipunktide tüübid.
    Ülesande tagasiside.';

COMMENT ON COLUMN normiprotsentiil.id IS 'kirje identifikaator';
COMMENT ON COLUMN normiprotsentiil.normipunkt_id IS 'viide alatesti või testiülesandega seotud normipunkti tüübi kirjele';
COMMENT ON COLUMN normiprotsentiil.protsent IS 'psühholoogi testis protsent (10,25,50,75,90)';
COMMENT ON COLUMN normiprotsentiil.protsentiil IS 'psühholoogi testis protsentiil (mitu punkti on selle sooritaja tulemus, kes paikneb tulemuste järjekorras antud protsendi peal (vahemiku lõpp)';
COMMENT ON COLUMN normiprotsentiil.created IS 'kirje loomise aeg';
COMMENT ON COLUMN normiprotsentiil.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN normiprotsentiil.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN normiprotsentiil.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE normiprotsentiil IS 'Psühholoogilise testi alatesti või testiülesande normipunktide tüübile vastavad protsentiilid.';

COMMENT ON COLUMN sooritusryhm.id IS 'kirje identifikaator';
COMMENT ON COLUMN sooritusryhm.normipunkt_id IS 'viide alatesti või testiülesandega seotud normipunkti tüübi kirjele';
COMMENT ON COLUMN sooritusryhm.ryhm IS 'sooritusrühm (1 - madal, 2 - keskmine, 3 - kõrge)';
COMMENT ON COLUMN sooritusryhm.lavi IS 'sooritusrühma kuulumise lävi (vahemiku algus - nt kui vahemikud on 0-15,16-21,22-30, siis andmebaasis on väärtused 0,16,22)';
COMMENT ON COLUMN sooritusryhm.created IS 'kirje loomise aeg';
COMMENT ON COLUMN sooritusryhm.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN sooritusryhm.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN sooritusryhm.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE sooritusryhm IS 'Õpipädevuse testis normipunkti sooritusrühmad (madal, keskmine, kõrge)';

-- eis/model/test/valitudylesanne.py
COMMENT ON COLUMN valitudylesanne.id IS 'kirje identifikaator';
COMMENT ON COLUMN valitudylesanne.seq IS 'valikülesande järjekorranumber (kui on valikülesanne)';
COMMENT ON COLUMN valitudylesanne.ylesanne_id IS 'viide valitud ülesandele';
COMMENT ON COLUMN valitudylesanne.testiylesanne_id IS 'viide testiülesandele';
COMMENT ON COLUMN valitudylesanne.koefitsient IS 'testiülesande max pallide ja ülesande max pallide suhe, millega hindaja antud toorpunkte korrutades saadakse hindepallid';
COMMENT ON COLUMN valitudylesanne.komplekt_id IS 'viide komplektile';
COMMENT ON COLUMN valitudylesanne.test_id IS 'viide testile (testiylesanne.testiosa.test dubleerimine päringute lihtsutamiseks)';
COMMENT ON COLUMN valitudylesanne.hindamiskogum_id IS 'viide hindamiskogumile, millesse testiülesanne kuulub (ainult lõdva struktuuriga testiosa korral, muidu on seos hindamiskogumiga testiülesande kirjes)';
COMMENT ON COLUMN valitudylesanne.selgitus IS 'selgitav tekst lahendajale (jagatud töö korral)';
COMMENT ON COLUMN valitudylesanne.created IS 'kirje loomise aeg';
COMMENT ON COLUMN valitudylesanne.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN valitudylesanne.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN valitudylesanne.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE valitudylesanne IS 'Antud ülesandekomplektis testiülesandesse valitud ülesanne';

-- eis/model/test/eristuskiri.py
COMMENT ON COLUMN eristuskiri.id IS 'kirje identifikaator';
COMMENT ON COLUMN eristuskiri.test_id IS 'viide testile';
COMMENT ON COLUMN eristuskiri.sisu IS 'eristuskiri tekstina';
COMMENT ON COLUMN eristuskiri.filename IS 'failinimi';
COMMENT ON COLUMN eristuskiri.filesize IS 'faili suurus baitides';
COMMENT ON COLUMN eristuskiri.fileversion IS 'versioon';
COMMENT ON COLUMN eristuskiri.created IS 'kirje loomise aeg';
COMMENT ON COLUMN eristuskiri.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN eristuskiri.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN eristuskiri.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE eristuskiri IS 'Testi eristuskiri';

-- eis/model/test/t_test.py
COMMENT ON COLUMN t_test.orig_id IS 'viide lähtekirjele';
COMMENT ON COLUMN t_test.lang IS 'tõlkekeel';
COMMENT ON COLUMN t_test.nimi IS 'pealkiri';
COMMENT ON COLUMN t_test.tahemargid IS 'tähemärkide arv tõlkekeeles';
COMMENT ON COLUMN t_test.created IS 'kirje loomise aeg';
COMMENT ON COLUMN t_test.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN t_test.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN t_test.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE t_test IS 'Tabeli Test tõlge';

COMMENT ON COLUMN t_testiosa.orig_id IS 'viide lähtekirjele';
COMMENT ON COLUMN t_testiosa.lang IS 'tõlkekeel';
COMMENT ON COLUMN t_testiosa.nimi IS 'testiosa nimetus';
COMMENT ON COLUMN t_testiosa.alustajajuhend IS 'juhend sooritajale, mis kuvatakse enne testi alustamist';
COMMENT ON COLUMN t_testiosa.sooritajajuhend IS 'sooritajajuhend, mis kuvatakse siis, kui sooritamist on alustatud';
COMMENT ON COLUMN t_testiosa.created IS 'kirje loomise aeg';
COMMENT ON COLUMN t_testiosa.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN t_testiosa.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN t_testiosa.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE t_testiosa IS 'Tabeli Testiosa tõlge';

COMMENT ON COLUMN t_alatest.orig_id IS 'viide lähtekirjele';
COMMENT ON COLUMN t_alatest.lang IS 'tõlkekeel';
COMMENT ON COLUMN t_alatest.nimi IS 'nimetus';
COMMENT ON COLUMN t_alatest.sooritajajuhend IS 'sooritajajuhend';
COMMENT ON COLUMN t_alatest.created IS 'kirje loomise aeg';
COMMENT ON COLUMN t_alatest.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN t_alatest.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN t_alatest.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE t_alatest IS 'Tabeli Alatest tõlge';

COMMENT ON COLUMN t_alatestigrupp.orig_id IS 'viide lähtekirjele';
COMMENT ON COLUMN t_alatestigrupp.lang IS 'tõlkekeel';
COMMENT ON COLUMN t_alatestigrupp.nimi IS 'grupi nimetus';
COMMENT ON COLUMN t_alatestigrupp.created IS 'kirje loomise aeg';
COMMENT ON COLUMN t_alatestigrupp.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN t_alatestigrupp.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN t_alatestigrupp.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE t_alatestigrupp IS 'Tabeli Alatestigrupp tõlge';

COMMENT ON COLUMN t_testiplokk.orig_id IS 'viide lähtekirjele';
COMMENT ON COLUMN t_testiplokk.lang IS 'tõlkekeel';
COMMENT ON COLUMN t_testiplokk.nimi IS 'nimetus';
COMMENT ON COLUMN t_testiplokk.created IS 'kirje loomise aeg';
COMMENT ON COLUMN t_testiplokk.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN t_testiplokk.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN t_testiplokk.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE t_testiplokk IS 'Tabeli Testiplokk tõlge';

COMMENT ON COLUMN t_testitagasiside.orig_id IS 'viide lähtekirjele';
COMMENT ON COLUMN t_testitagasiside.lang IS 'tõlkekeel';
COMMENT ON COLUMN t_testitagasiside.sissejuhatus_opilasele IS 'sissejuhatus õpilasele';
COMMENT ON COLUMN t_testitagasiside.kokkuvote_opilasele IS 'kokkuvõte õpilasele';
COMMENT ON COLUMN t_testitagasiside.sissejuhatus_opetajale IS 'sissejuhatus õpetajale';
COMMENT ON COLUMN t_testitagasiside.kokkuvote_opetajale IS 'kokkuvõte õpetajale';
COMMENT ON COLUMN t_testitagasiside.tahemargid IS 'tähemärkide arv';
COMMENT ON COLUMN t_testitagasiside.created IS 'kirje loomise aeg';
COMMENT ON COLUMN t_testitagasiside.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN t_testitagasiside.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN t_testitagasiside.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE t_testitagasiside IS 'Tabeli Testitagasiside tõlge';

COMMENT ON COLUMN t_testiylesanne.orig_id IS 'viide lähtekirjele';
COMMENT ON COLUMN t_testiylesanne.lang IS 'tõlkekeel';
COMMENT ON COLUMN t_testiylesanne.nimi IS 'nimetus';
COMMENT ON COLUMN t_testiylesanne.sooritajajuhend IS 'juhend sooritajale (kasutusel valikülesande korral)';
COMMENT ON COLUMN t_testiylesanne.pealkiri IS 'pealkiri (kasutusel valikülesande korral)';
COMMENT ON COLUMN t_testiylesanne.created IS 'kirje loomise aeg';
COMMENT ON COLUMN t_testiylesanne.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN t_testiylesanne.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN t_testiylesanne.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE t_testiylesanne IS 'Tabeli Testiylesanne tõlge';

COMMENT ON COLUMN t_nptagasiside.orig_id IS 'viide lähtekirjele';
COMMENT ON COLUMN t_nptagasiside.lang IS 'tõlkekeel';
COMMENT ON COLUMN t_nptagasiside.tagasiside IS 'sooritajale kuvatava tagasiside tekst';
COMMENT ON COLUMN t_nptagasiside.op_tagasiside IS 'õpetajale kuvatava tagasiside tekst';
COMMENT ON COLUMN t_nptagasiside.stat_tagasiside IS 'statistikas kasutatav tagasiside (grupi kohta)';
COMMENT ON COLUMN t_nptagasiside.created IS 'kirje loomise aeg';
COMMENT ON COLUMN t_nptagasiside.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN t_nptagasiside.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN t_nptagasiside.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE t_nptagasiside IS 'Tabeli Nptagasiside tõlge';

COMMENT ON COLUMN t_valitudylesanne.orig_id IS 'viide lähtekirjele';
COMMENT ON COLUMN t_valitudylesanne.lang IS 'tõlkekeel';
COMMENT ON COLUMN t_valitudylesanne.selgitus IS 'selgitav tekst lahendajale (jagatud töö korral)';
COMMENT ON COLUMN t_valitudylesanne.created IS 'kirje loomise aeg';
COMMENT ON COLUMN t_valitudylesanne.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN t_valitudylesanne.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN t_valitudylesanne.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE t_valitudylesanne IS 'Tabeli Valitudylesanne tõlge';

COMMENT ON COLUMN t_ylesandegrupp.orig_id IS 'viide lähtekirjele';
COMMENT ON COLUMN t_ylesandegrupp.lang IS 'tõlkekeel';
COMMENT ON COLUMN t_ylesandegrupp.nimi IS 'grupi nimetus';
COMMENT ON COLUMN t_ylesandegrupp.created IS 'kirje loomise aeg';
COMMENT ON COLUMN t_ylesandegrupp.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN t_ylesandegrupp.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN t_ylesandegrupp.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE t_ylesandegrupp IS 'Tabeli Nsgrupp tõlge';

COMMENT ON COLUMN t_normipunkt.orig_id IS 'viide lähtekirjele';
COMMENT ON COLUMN t_normipunkt.lang IS 'tõlkekeel';
COMMENT ON COLUMN t_normipunkt.nimi IS 'nimetus, mida tulemuste kuvamisel kasutatakse';
COMMENT ON COLUMN t_normipunkt.tahemargid IS 'tähemärkide arv';
COMMENT ON COLUMN t_normipunkt.created IS 'kirje loomise aeg';
COMMENT ON COLUMN t_normipunkt.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN t_normipunkt.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN t_normipunkt.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE t_normipunkt IS 'Tabeli Normipunkt tõlge';

COMMENT ON COLUMN t_nsgrupp.orig_id IS 'viide lähtekirjele';
COMMENT ON COLUMN t_nsgrupp.lang IS 'tõlkekeel';
COMMENT ON COLUMN t_nsgrupp.nimi IS 'grupi nimetus';
COMMENT ON COLUMN t_nsgrupp.created IS 'kirje loomise aeg';
COMMENT ON COLUMN t_nsgrupp.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN t_nsgrupp.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN t_nsgrupp.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE t_nsgrupp IS 'Tabeli Nsgrupp tõlge';

COMMENT ON COLUMN t_hindamiskriteerium.orig_id IS 'viide lähtekirjele';
COMMENT ON COLUMN t_hindamiskriteerium.lang IS 'tõlkekeel';
COMMENT ON COLUMN t_hindamiskriteerium.hindamisjuhis IS 'juhis';
COMMENT ON COLUMN t_hindamiskriteerium.created IS 'kirje loomise aeg';
COMMENT ON COLUMN t_hindamiskriteerium.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN t_hindamiskriteerium.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN t_hindamiskriteerium.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE t_hindamiskriteerium IS 'Tabeli Hindamiskriteerium tõlge';

COMMENT ON COLUMN t_kritkirjeldus.orig_id IS 'viide lähtekirjele';
COMMENT ON COLUMN t_kritkirjeldus.lang IS 'tõlkekeel';
COMMENT ON COLUMN t_kritkirjeldus.kirjeldus IS 'juhis';
COMMENT ON COLUMN t_kritkirjeldus.created IS 'kirje loomise aeg';
COMMENT ON COLUMN t_kritkirjeldus.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN t_kritkirjeldus.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN t_kritkirjeldus.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE t_kritkirjeldus IS 'Tabeli Kritkirjeldus tõlge';

-- eis/model/test/hindamiskriteerium.py
COMMENT ON COLUMN hindamiskriteerium.id IS 'kirje identifikaator';
COMMENT ON COLUMN hindamiskriteerium.hindamiskogum_id IS 'viide hindamiskogumile';
COMMENT ON COLUMN hindamiskriteerium.aine_kood IS 'õppeaine, mille hindamisaspekt see on';
COMMENT ON COLUMN hindamiskriteerium.aspekt_kood IS 'viide aspektile, klassifikaator ASPEKT';
COMMENT ON COLUMN hindamiskriteerium.max_pallid IS 'max toorpunktide arv, mida selle kriteeriumiga hinnatakse';
COMMENT ON COLUMN hindamiskriteerium.pintervall IS 'lubatud punktide intervall (käsitsi hindamisel)';
COMMENT ON COLUMN hindamiskriteerium.kaal IS 'kaal, millega kriteeriumi toorpunktid korrutatakse';
COMMENT ON COLUMN hindamiskriteerium.hindamisjuhis IS 'kirjeldus (kui puudub, siis kasutatakse vaikimisi kirjeldusena aspektide klassifikaatoris olevat)';
COMMENT ON COLUMN hindamiskriteerium.seq IS 'hindamiskriteeriumi järjekord hindamiskogumis';
COMMENT ON COLUMN hindamiskriteerium.kuvada_statistikas IS 'kas kuvada kriteerium statistikaraportis';
COMMENT ON COLUMN hindamiskriteerium.pkirj_sooritajale IS 'kas kuvada punktide kirjeldused sooritajale';
COMMENT ON COLUMN hindamiskriteerium.created IS 'kirje loomise aeg';
COMMENT ON COLUMN hindamiskriteerium.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN hindamiskriteerium.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN hindamiskriteerium.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE hindamiskriteerium IS 'Hindamiskogumi hindamiskriteerium';

-- eis/model/test/testihinne.py
COMMENT ON COLUMN testihinne.id IS 'kirje identifikaator';
COMMENT ON COLUMN testihinne.test_id IS 'viide testile';
COMMENT ON COLUMN testihinne.hinne IS 'hinne, vahemikus 1-5';
COMMENT ON COLUMN testihinne.pallid IS 'minimaalne tulemuse protsent sooritajale võimalikust kogutulemusest (mitte pallide arv!), mis peab olema tulemuseks, et saada hinne';
COMMENT ON COLUMN testihinne.created IS 'kirje loomise aeg';
COMMENT ON COLUMN testihinne.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN testihinne.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN testihinne.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE testihinne IS 'Testi tulemuse eest antav hinne vastavalt tulemuseks saadud protsendile';

-- eis/model/test/testifail.py
COMMENT ON COLUMN testifail.id IS 'kirje identifikaator';
COMMENT ON COLUMN testifail.komplekt_id IS 'viide ülesandekomplektile';
COMMENT ON COLUMN testifail.nimi IS 'selgitav nimetus';
COMMENT ON COLUMN testifail.filename IS 'failinimi';
COMMENT ON COLUMN testifail.filesize IS 'faili suurus baitides';
COMMENT ON COLUMN testifail.fileversion IS 'versioon';
COMMENT ON COLUMN testifail.mimetype IS 'failitüüp';
COMMENT ON COLUMN testifail.created IS 'kirje loomise aeg';
COMMENT ON COLUMN testifail.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN testifail.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN testifail.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE testifail IS 'Testi ülesandekomplekti juurde salvestatud fail';

-- eis/model/test/eeltest.py
COMMENT ON COLUMN eeltest.id IS 'kirje identifikaator';
COMMENT ON COLUMN eeltest.algne_test_id IS 'viide algsele testile, millest eeltest loodi';
COMMENT ON COLUMN eeltest.avalik_test_id IS 'viide avalikule testile, mis on algse testi testimiseks loodud (jääb alles ka peale avaliku testi kustutamist)';
COMMENT ON COLUMN eeltest.tagasiside_sooritajale IS 'kas sooritaja võib testimiskorraga testis tagasisidet näha kohe peale sooritamist, enne koondtulemuse avaldamist';
COMMENT ON COLUMN eeltest.tagasiside_koolile IS 'kas õpetaja võib testimiskorraga testis tagasisidet näha kohe peale sooritamist, enne koondtulemuse avaldamist';
COMMENT ON COLUMN eeltest.markus_korraldajatele IS 'testi koostaja märkused korraldajatele';
COMMENT ON COLUMN eeltest.stat_filedata IS 'eeltesti statistika PDF faili sisu';
COMMENT ON COLUMN eeltest.stat_ts IS 'eeltesti statistika PDF koostamise aeg';
COMMENT ON COLUMN eeltest.created IS 'kirje loomise aeg';
COMMENT ON COLUMN eeltest.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN eeltest.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN eeltest.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE eeltest IS 'Testikomplekti avaldamine eeltestimiseks.
    Kirje jääb alles ka peale eeltesti kustutamist.';

-- eis/model/test/alatest.py
COMMENT ON COLUMN alatest.id IS 'kirje identifikaator';
COMMENT ON COLUMN alatest.seq IS 'alatesti järjekorranumber testiosas';
COMMENT ON COLUMN alatest.nimi IS 'alatesti nimetus';
COMMENT ON COLUMN alatest.numbrita IS 'kas kuvada ilma järjekorranumbrita (nt juhendi alatesti korral)';
COMMENT ON COLUMN alatest.tahis IS 'alatesti järjekorranumber kasutajaliideses (kui nubrita alatestid välja jätta)';
COMMENT ON COLUMN alatest.alatest_kood IS 'alatesti liik (tasemeeksami korral), klassifikaator ALATEST';
COMMENT ON COLUMN alatest.kursus_kood IS 'lai või kitsas (matemaatika korral), klassifikaator KURSUS';
COMMENT ON COLUMN alatest.piiraeg IS 'alatesti sooritamiseks lubatud aeg sekundites';
COMMENT ON COLUMN alatest.piiraeg_sek IS 'true - aeg kuvada kohe sekundites; false, null - minutist suurem aeg kuvada ilma sekunditeta';
COMMENT ON COLUMN alatest.hoiatusaeg IS 'piirajaga alatesti korral: mitu sekundit enne lõppu antakse hoiatusteade';
COMMENT ON COLUMN alatest.max_pallid IS 'max pallide arv';
COMMENT ON COLUMN alatest.skoorivalem IS 'tulemuse arvutamise valem (kasutusel siis, kui tulemus ei ole ülesannete pallide summa)';
COMMENT ON COLUMN alatest.vastvorm_kood IS 'vastamise vorm, klassifikaator VASTVORM (EISis loodud testide korral sama, mis testiosa vastamise vorm; TSEISist üle kantud testide korral võib olla erinev)';
COMMENT ON COLUMN alatest.sooritajajuhend IS 'juhend sooritajale';
COMMENT ON COLUMN alatest.ylesannete_arv IS 'ülesannete arv';
COMMENT ON COLUMN alatest.on_yhekordne IS 'kas alatest on ühekordselt lahendatav (peale kinnipanekut uuesti avada ei saa)';
COMMENT ON COLUMN alatest.yhesuunaline IS 'kas alatest on ühesuunaliselt lahendatav (ülesanded tuleb lahendada kindlas järjekorras)';
COMMENT ON COLUMN alatest.peida_pais IS 'kas lahendajale kuvada EISi päis ja jalus või ainult ülesanded';
COMMENT ON COLUMN alatest.testiosa_id IS 'viide testiosale';
COMMENT ON COLUMN alatest.komplektivalik_id IS 'viide komplektivalikule, mille komplektid antud alatesti katavad';
COMMENT ON COLUMN alatest.testivaline IS 'kas vastatakse peale testi lõppemist (kasutatakse küsimustiku alatesti korral)';
COMMENT ON COLUMN alatest.yl_segamini IS 'kas ülesanded kuvatakse lahendajale segatud järjekorras';
COMMENT ON COLUMN alatest.rvosaoskus_id IS 'seos rahvusvahelise tunnistuse osaoskusega, mis vastab sellele alatestile';
COMMENT ON COLUMN alatest.created IS 'kirje loomise aeg';
COMMENT ON COLUMN alatest.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN alatest.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN alatest.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE alatest IS 'Alatest';

-- eis/model/test/tagasisidefail.py
COMMENT ON COLUMN tagasisidefail.id IS 'kirje identifikaator';
COMMENT ON COLUMN tagasisidefail.test_id IS 'viide testile';
COMMENT ON COLUMN tagasisidefail.filename IS 'failinimi';
COMMENT ON COLUMN tagasisidefail.filesize IS 'faili suurus baitides';
COMMENT ON COLUMN tagasisidefail.fileversion IS 'versioon';
COMMENT ON COLUMN tagasisidefail.mimetype IS 'failitüüp';
COMMENT ON COLUMN tagasisidefail.created IS 'kirje loomise aeg';
COMMENT ON COLUMN tagasisidefail.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN tagasisidefail.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN tagasisidefail.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE tagasisidefail IS 'Testi tagasisidevormil kasutatud piltide failid';

-- eis/model/test/alatestigrupp.py
COMMENT ON COLUMN alatestigrupp.id IS 'kirje identifikaator';
COMMENT ON COLUMN alatestigrupp.seq IS 'grupi järjekorranumber';
COMMENT ON COLUMN alatestigrupp.nimi IS 'grupi nimetus';
COMMENT ON COLUMN alatestigrupp.testiosa_id IS 'viide testiosale';
COMMENT ON COLUMN alatestigrupp.created IS 'kirje loomise aeg';
COMMENT ON COLUMN alatestigrupp.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN alatestigrupp.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN alatestigrupp.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE alatestigrupp IS 'Tagasisidetunnuste grupp';

-- eis/model/test/testilogi.py
COMMENT ON COLUMN testilogi.id IS 'kirje identifikaator';
COMMENT ON COLUMN testilogi.aeg IS 'logitava sündmuse aeg';
COMMENT ON COLUMN testilogi.tyyp IS 'tyyp olekuinfo eristamiseks: 1=TESTILOGI_TYYP_OLEK - olekuinfo, kuvatakse lisaks logile ka koostamise vormil; NULL - muu logi';
COMMENT ON COLUMN testilogi.liik IS 'logitava olemi kirjeldus';
COMMENT ON COLUMN testilogi.vanad_andmed IS 'vanad andmed';
COMMENT ON COLUMN testilogi.uued_andmed IS 'uued andmed';
COMMENT ON COLUMN testilogi.test_id IS 'viide testile';
COMMENT ON COLUMN testilogi.kasutaja_id IS 'viide kasutajale';
COMMENT ON COLUMN testilogi.created IS 'kirje loomise aeg';
COMMENT ON COLUMN testilogi.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN testilogi.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN testilogi.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE testilogi IS 'Testi koostamise ajalugu';

-- eis/model/test/komplektivalik.py
COMMENT ON COLUMN komplektivalik.id IS 'kirje identifikaator';
COMMENT ON COLUMN komplektivalik.testiosa_id IS 'viide testiosale';
COMMENT ON COLUMN komplektivalik.kursus_kood IS 'lai või kitsas (matemaatika korral), klassifikaator KURSUS (komplektivaliku kõigil alatestidel peab olema sama kursus)';
COMMENT ON COLUMN komplektivalik.alatestideta IS 'unikaalsuse kontroll, et ei tekiks mitu alatestideta komplektivalikut: kursusteta ja alatestideta komplektivaliku korral True (unikaalses indeksis); muidu NULL (unikaalset indeksit ei sega)';
COMMENT ON COLUMN komplektivalik.created IS 'kirje loomise aeg';
COMMENT ON COLUMN komplektivalik.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN komplektivalik.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN komplektivalik.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE komplektivalik IS 'Testi ülesandekomplektide valik.
    Komplektivalik ühendab alatestid, mida samad komplektid katavad.';

-- eis/model/test/salatest.py
COMMENT ON COLUMN salatest.id IS 'kirje identifikaator';
COMMENT ON COLUMN salatest.parool IS 'SK sertifikaatidele krüptitud parool .cdoc (<EncryptedData>) kujul';
COMMENT ON COLUMN salatest.data IS 'parooliga krüptitud andmed';
COMMENT ON COLUMN salatest.test_id IS 'viide testile';
COMMENT ON COLUMN salatest.created IS 'kirje loomise aeg';
COMMENT ON COLUMN salatest.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN salatest.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN salatest.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE salatest IS 'Krüptitud testi sisu';

-- eis/model/test/testifailimarkus.py
COMMENT ON COLUMN testifailimarkus.id IS 'kirje identifikaator';
COMMENT ON COLUMN testifailimarkus.testifail_id IS 'viide testifaili kirjele';
COMMENT ON COLUMN testifailimarkus.kasutaja_id IS 'viide kasutajale';
COMMENT ON COLUMN testifailimarkus.aeg IS 'märkuse kirjutamise aeg';
COMMENT ON COLUMN testifailimarkus.sisu IS 'märkuse sisu';
COMMENT ON COLUMN testifailimarkus.teema IS 'märkuse teema';
COMMENT ON COLUMN testifailimarkus.ylem_id IS 'viide ülemale märkusele, mida antud märkus kommenteerib';
COMMENT ON COLUMN testifailimarkus.created IS 'kirje loomise aeg';
COMMENT ON COLUMN testifailimarkus.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN testifailimarkus.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN testifailimarkus.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE testifailimarkus IS 'Testifaili märkused';

-- eis/model/test/toofail.py
COMMENT ON COLUMN toofail.id IS 'kirje identifikaator';
COMMENT ON COLUMN toofail.filename IS 'failinimi';
COMMENT ON COLUMN toofail.filesize IS 'faili suurus baitides';
COMMENT ON COLUMN toofail.fileversion IS 'versioon';
COMMENT ON COLUMN toofail.mimetype IS 'failitüüp';
COMMENT ON COLUMN toofail.kirjeldus IS 'kirjeldus';
COMMENT ON COLUMN toofail.test_id IS 'viide testile, kui fail käib teatud testi kohta ja on loetav koolides, kus on selle testi sooritajaid';
COMMENT ON COLUMN toofail.oppetase_kood IS 'õppetase, EISi klassifikaator OPPETASE: y=const.OPPETASE_YLD - üldharidus; u=const.OPPETASE_KUTSE - kutseharidus; o=const.OPPETASE_KORG - kõrgharidus; NULL - plangivaba tase (alusharidus või huviharidus); fail on loetav koolides, millel on antud tase';
COMMENT ON COLUMN toofail.avalik_alates IS 'kuupäev ja kellaaeg, millest alates fail on koolidele nähtav';
COMMENT ON COLUMN toofail.created IS 'kirje loomise aeg';
COMMENT ON COLUMN toofail.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN toofail.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN toofail.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE toofail IS 'Tööde PDF failid koos hindamisjuhendiga koolidele jagamiseks';

-- eis/model/test/ylesandegrupp.py
COMMENT ON COLUMN ylesandegrupp.id IS 'kirje identifikaator';
COMMENT ON COLUMN ylesandegrupp.seq IS 'järjekorranumber testiosa sees';
COMMENT ON COLUMN ylesandegrupp.nimi IS 'grupi nimetus';
COMMENT ON COLUMN ylesandegrupp.testiosa_id IS 'viide testiosale, mille ülesandeid grupp rühmitab';
COMMENT ON COLUMN ylesandegrupp.created IS 'kirje loomise aeg';
COMMENT ON COLUMN ylesandegrupp.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN ylesandegrupp.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN ylesandegrupp.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE ylesandegrupp IS 'Ülesannete grupp, millest moodustatakse normipunkte';

-- eis/model/test/nptagasiside.py
COMMENT ON COLUMN nptagasiside.id IS 'kirje identifikaator';
COMMENT ON COLUMN nptagasiside.normipunkt_id IS 'viide alatesti või testiülesandega seotud normipunkti tüübi kirjele';
COMMENT ON COLUMN nptagasiside.seq IS 'tingimuse järjekorranumber (normipunktis)';
COMMENT ON COLUMN nptagasiside.ahel_testiylesanne_id IS 'varasemate ülesannete ahelas olev ülesanne - kui tingimus kehtib ainult juhul, kui varasemas ahelas on teatud ülesanne';
COMMENT ON COLUMN nptagasiside.tingimus_tehe IS 'tingimuses kasutatav tehe <, <=, ==, >=, >';
COMMENT ON COLUMN nptagasiside.tingimus_vaartus IS 'tingimuse võrdluse parema poole väärtus';
COMMENT ON COLUMN nptagasiside.tingimus_valik IS 'tingimuse võrdluse paremal poolel olev valiku kood, kui vasakul on valikküsimuse kood (ülesande tagasiside korral)';
COMMENT ON COLUMN nptagasiside.tagasiside IS 'sooritajale kuvatava tagasiside tekst';
COMMENT ON COLUMN nptagasiside.op_tagasiside IS 'õpetajale kuvatava tagasiside tekst';
COMMENT ON COLUMN nptagasiside.stat_tagasiside IS 'statistikas kasutatav tagasiside (grupi kohta)';
COMMENT ON COLUMN nptagasiside.jatka IS 'kas peale lahendamist tuleb jätkata sama ülesannet (ülesande tagasiside korral - kui soovitakse lasta ülesannet lahendada seni, kuni vastab õigesti)';
COMMENT ON COLUMN nptagasiside.uus_testiylesanne_id IS 'viide ülesandele, millele tingimuse täidetuse korral edasi minnakse, peab olema samas alatestis (diagnoosiva testi korral)';
COMMENT ON COLUMN nptagasiside.nsgrupp_id IS 'viide tagasiside grupile';
COMMENT ON COLUMN nptagasiside.created IS 'kirje loomise aeg';
COMMENT ON COLUMN nptagasiside.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN nptagasiside.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN nptagasiside.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE nptagasiside IS 'Ülesandegrupi tingimus ja tagasiside tekst diagnoosivas testis või ülesandes';

-- eis/model/test/testiplokk.py
COMMENT ON COLUMN testiplokk.id IS 'kirje identifikaator';
COMMENT ON COLUMN testiplokk.seq IS 'järjekorranumber alatesti sees';
COMMENT ON COLUMN testiplokk.nimi IS 'testiploki nimetus';
COMMENT ON COLUMN testiplokk.max_pallid IS 'max pallide arv';
COMMENT ON COLUMN testiplokk.ylesannete_arv IS 'ülesannete arv';
COMMENT ON COLUMN testiplokk.alatest_id IS 'viide alatestile';
COMMENT ON COLUMN testiplokk.created IS 'kirje loomise aeg';
COMMENT ON COLUMN testiplokk.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN testiplokk.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN testiplokk.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE testiplokk IS 'Testiplokk';

-- eis/model/test/test.py
COMMENT ON COLUMN test.id IS 'kirje identifikaator';
COMMENT ON COLUMN test.nimi IS 'testi nimi';
COMMENT ON COLUMN test.staatus IS 'olek: 1=const.T_STAATUS_KOOSTAMISEL - koostamisel; 2=const.T_STAATUS_KINNITATUD - kinnitatud; 8=const.T_STAATUS_ARHIIV - arhiveeritud';
COMMENT ON COLUMN test.testityyp IS 'testi tüüp: 0=const.TESTITYYP_AVALIK - avaliku vaate test; 1=const.TESTITYYP_EKK - eksamikeskuse test; 2=const.TESTITYYP_KONS - konsultatsioon; 3=const.TESTITYYP_TOO - õpilasele jagatud töö';
COMMENT ON COLUMN test.testiklass_kood IS 'klass, klassifikaator TESTIKLASS';
COMMENT ON COLUMN test.aste_mask IS 'kooliastmed/erialad kodeeritud bittide summana; biti järjekorranumber on astme kood (või vaikimisi astmete korral 0 - I aste; 1 - II aste; 2 - III aste; 3 - gümnaasium)';
COMMENT ON COLUMN test.periood_kood IS 'periood, klassifikaator PERIOOD';
COMMENT ON COLUMN test.max_pallid IS 'max hindepallide arv';
COMMENT ON COLUMN test.yhisosa_max_pallid IS 'laia ja kitsa matemaatika ühisossa kuuluvate ülesannete max hindepallide arv';
COMMENT ON COLUMN test.salastatud IS 'salastatus: 0 - pole salastatud; 1 - salastatud, kuid sooritatav; 2 - loogiline salastatus; 2 - krüptitud (enam ei saa)';
COMMENT ON COLUMN test.testiliik_kood IS 'testi liik, klassifikaator TESTILIIK';
COMMENT ON COLUMN test.aine_kood IS 'õppeaine, klassifikaator AINE';
COMMENT ON COLUMN test.aine_muu IS 'õppeaine nimetus, kui ei leidu klassifikaatoris (avaliku vaate testi korral)';
COMMENT ON COLUMN test.eeltest_id IS 'eeltesti andmed ja seos algse testiga, kui antud test on mingi teise testi eeltest';
COMMENT ON COLUMN test.avaldamistase IS 'avaldamistase: 4=const.AVALIK_SOORITAJAD - kõigile lahendajatele; 3=const.AVALIK_OPETAJAD - kõikidele pedagoogidele; 2=const.AVALIK_MAARATUD - määratud kasutajatele; 1=const.AVALIK_EKSAM - testimiskorraga test; 0=const.AVALIK_POLE - keegi ei saa kasutada';
COMMENT ON COLUMN test.avalik_alates IS 'kuupäev, millest alates test on avalikus vaates (kõigile sooritajatele, kõigile pedagoogidele või määratud pedagoogidele)';
COMMENT ON COLUMN test.avalik_kuni IS 'kuupäev, milleni test on avalikus vaates';
COMMENT ON COLUMN test.korduv_sooritamine IS 'kas on võimalik testimiskorrata sooritamisel korduvalt sooritada';
COMMENT ON COLUMN test.korduv_sailitamine IS 'kas korduvalt sooritamisel jätta varasemad sooritused alles';
COMMENT ON COLUMN test.oige_naitamine IS 'kas näidata õiget vastust lahendajale peale sooritamist (kasutatakse avaliku vaate testi korral)';
COMMENT ON COLUMN test.arvutihinde_naitamine IS 'kas näidata arvutihinnatavat osa tulemusest kohe';
COMMENT ON COLUMN test.tulemus_tugiisikule IS 'kas tugiisik võib näha testi tulemust';
COMMENT ON COLUMN test.vastus_tugiisikule IS 'kas tugiisik võib näha antud vastuseid ja soorituse kirjet';
COMMENT ON COLUMN test.osalemise_peitmine IS 'kas peita osalemine sooritaja eest (testimiskorrata lahendamisel): tugiisiku kasutamise korral ei näidata sooritajale testi kuskil; tugiisikuta sooritamisel näeb sooritaja testi ainult sooritamise ajal; ei mõjuta tulemuse ja vastuste kuvamist tugiisikule';
COMMENT ON COLUMN test.ajakulu_naitamine IS 'soorituste ajakulu näitamine koolile klassi tulemuste vaatamisel: 0=const.AJAKULU_POLE - ei näidata; 1=const.AJAKULU_OSA - ainult osade kaupa; 2=const.AJAKULU_TEST - ainult koguaeg (osade summa); 3=const.AJAKULU_KOIK - osade kaupa ja koguaeg';
COMMENT ON COLUMN test.opetajale_peidus IS 'kas peita õpilase vastused ja tagasiside õpetaja eest (testimiskorrata lahendamisel, kasutusel taustaküsitlustes)';
COMMENT ON COLUMN test.tagasiside_mall IS 'tagasiside mall: NULL - ei ole tagasisidet; 0=const.TSMALL_VABA - vabalt kujundatav; 1=const.TSMALL_DIAG - diagnoosiva testi mall; 2=const.TSMALL_PSYH - koolipsühholoogi testi mall';
COMMENT ON COLUMN test.diagnoosiv IS 'kas on diagnoosiv test';
COMMENT ON COLUMN test.pallideta IS 'kas avalikus vaates ei kuvata tulemust pallides ega protsentides (õpipädevuse, koolipsühholoogi ja diagnoosiva testi korral sees) ja ei kuvata vastuste analüüsi';
COMMENT ON COLUMN test.protsendita IS 'kas pallides tulemuse kuvamisel ei kuvata protsenti (CAE korral sees, sest CAE osapunktide summa ei ole testi tulemus ja protsenti ei saa arvutada)';
COMMENT ON COLUMN test.lang IS 'põhikeele kood';
COMMENT ON COLUMN test.skeeled IS 'testi keelte koodid eraldatuna tühikuga';
COMMENT ON COLUMN test.ui_lang IS 'true - sooritamise kasutajaliides peab olema soorituskeeles; false, null - kasutatakse tavalist kasutajaliidese keelt';
COMMENT ON COLUMN test.markus IS 'märkused';
COMMENT ON COLUMN test.lavi_pr IS 'minimaalne tulemus protsentides, mille korral väljastatakse tunnistus (TE, SE korral)';
COMMENT ON COLUMN test.tulemuste_vahemikud_pr IS 'protsendivahemikud, mis kuvatakse tunnistusel saadud pallide asemel (TE, SE korral); väärtus "1,50,60,76,91" tähendab vahemikke 0-0, 1-49, 50-59, 60-75, 76-90, 91-100';
COMMENT ON COLUMN test.ymardamine IS 'kas testi kogutulemuseks arvutatud pallid ümardada';
COMMENT ON COLUMN test.kvaliteet_kood IS 'kvaliteedimärk';
COMMENT ON COLUMN test.autor IS 'testi autor (informatiivne, kasutusel d-testi korral)';
COMMENT ON COLUMN test.rveksam_id IS 'seos rahvusvahelise tunnistusega, mida võidakse selle testi tulemuste põhjal väljastada';
COMMENT ON COLUMN test.tahemargid IS 'tähemärkide arv originaalkeeles';
COMMENT ON COLUMN test.created IS 'kirje loomise aeg';
COMMENT ON COLUMN test.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN test.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN test.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE test IS 'Test';

-- eis/model/test/kiirvalik.py
COMMENT ON COLUMN kiirvalik.id IS 'kirje identifikaator';
COMMENT ON COLUMN kiirvalik.testiliik_kood IS 'kiirvalikusse kuuluvate testide liik, klassifikaator TESTILIIK';
COMMENT ON COLUMN kiirvalik.nimi IS 'nimetus';
COMMENT ON COLUMN kiirvalik.staatus IS 'olek: 1 - kasutusel; 0 - pole kasutusel';
COMMENT ON COLUMN kiirvalik.selgitus IS 'selgitus';
COMMENT ON COLUMN kiirvalik.created IS 'kirje loomise aeg';
COMMENT ON COLUMN kiirvalik.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN kiirvalik.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN kiirvalik.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE kiirvalik IS 'Testimiskordade kiirvalik, kiirendab sooritajal mitmele testile korraga registreerimist';

-- eis/model/test/testitagasiside.py
COMMENT ON COLUMN testitagasiside.id IS 'kirje identifikaator';
COMMENT ON COLUMN testitagasiside.test_id IS 'viide testile';
COMMENT ON COLUMN testitagasiside.sissejuhatus_opilasele IS 'sissejuhatus õpilasele';
COMMENT ON COLUMN testitagasiside.kokkuvote_opilasele IS 'kokkuvõte õpilasele';
COMMENT ON COLUMN testitagasiside.sissejuhatus_opetajale IS 'sissejuhatus õpetajale';
COMMENT ON COLUMN testitagasiside.kokkuvote_opetajale IS 'kokkuvõte õpetajale';
COMMENT ON COLUMN testitagasiside.ts_loetelu IS 'kas tagasiside tekstid kuvada loeteluna';
COMMENT ON COLUMN testitagasiside.ylgrupp_kuva IS 'kuidas kuvada ülesannete grupid: 0 - ei kuva gruppide kaupa; 1 - grupid üksteise all; 2 - grupid üksteise kõrval';
COMMENT ON COLUMN testitagasiside.ylgrupp_nimega IS 'kui kuvada ülesannete grupid, kas siis kuvada ka grupi nimetus';
COMMENT ON COLUMN testitagasiside.nsgrupp_kuva IS 'kuidas kuvada tagasiside grupid: 0 - ei kuva gruppide kaupa; 1 - grupid üksteise all; 2 - grupid üksteise kõrval';
COMMENT ON COLUMN testitagasiside.nsgrupp_nimega IS 'kui kuvada tagasiside grupid, kas siis kuvada ka grupi nimetus';
COMMENT ON COLUMN testitagasiside.kompaktvaade IS 'kas vaikimisi kuvada õpetajale kompaktne vaade';
COMMENT ON COLUMN testitagasiside.tahemargid IS 'tähemärkide arv';
COMMENT ON COLUMN testitagasiside.ts_sugu IS 'kas kuvada grupi tagasiside soo kaupa';
COMMENT ON COLUMN testitagasiside.created IS 'kirje loomise aeg';
COMMENT ON COLUMN testitagasiside.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN testitagasiside.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN testitagasiside.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE testitagasiside IS 'Testi tagasiside tekstid';

-- eis/model/test/komplekt.py
COMMENT ON COLUMN komplekt.id IS 'kirje identifikaator';
COMMENT ON COLUMN komplekt.staatus IS 'olek: 1=const.K_STAATUS_KOOSTAMISEL - koostamisel; 2=const.K_STAATUS_KINNITATUD - kinnitatud; 8=const.K_STAATUS_ARHIIV - arhiveeritud';
COMMENT ON COLUMN komplekt.lukus IS 'muutmise lukustus: NULL - komplekt on kinnitamata; 1=const.LUKUS_KINNITATUD - komplekt on kinnitatud ja muuta võib ainult ülesannete hindamise osa; 2=const.LUKUS_KATSE_SOORITATUD - komplekt on sooritatud KATSE testimiskorral või eelvaates, ei ole hinnatud, muuta võib ainult hindamise osa, muutja saab lukust lahti võtta; 3=const.LUKUS_KATSE_HINNATUD - komplekt on sooritatud ja hinnatud ainult KATSE testimiskorral, midagi ei või muuta, muutja saab lukust lahti võtta; 4=const.LUKUS_SOORITATUD - komplekt on kasutatud mitte-KATSE testimiskorral või testimiskorrata, hinnatud ei ole, muuta võib ainult hindamise osa, lukust lahti võtmiseks vaja eriõigusi; 5=const.LUKUS_HINNATUD - komplekti on kasutatud mitte-KATSE testimiskorral või testimiskorrata, on hinnatud, muuta ei või midagi, lukust lahti võtmiseks on vaja eriõigusi';
COMMENT ON COLUMN komplekt.tahis IS 'tähis';
COMMENT ON COLUMN komplekt.komplektivalik_id IS 'viide komplektivalikule';
COMMENT ON COLUMN komplekt.skeeled IS 'testi keelte koodid eraldatuna tühikuga';
COMMENT ON COLUMN komplekt.lisaaeg IS 'komplekti erialatestide lisaaegade summa';
COMMENT ON COLUMN komplekt.dif_hindamine IS 'kas komplekti erialatestidest mõnes on dif_hindamine';
COMMENT ON COLUMN komplekt.created IS 'kirje loomise aeg';
COMMENT ON COLUMN komplekt.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN komplekt.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN komplekt.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE komplekt IS 'Testi ülesannete komplekt (variant)';

-- eis/model/test/hindamiskogum.py
COMMENT ON COLUMN hindamiskogum.id IS 'kirje identifikaator';
COMMENT ON COLUMN hindamiskogum.testiosa_id IS 'viide testiosale';
COMMENT ON COLUMN hindamiskogum.tahis IS 'tähis (vaikimisi hindamiskogumi korral võib olla NULL)';
COMMENT ON COLUMN hindamiskogum.nimi IS 'nimetus';
COMMENT ON COLUMN hindamiskogum.staatus IS 'olek: kui kogum sisaldab ülesandeid, siis 1=const.B_STAATUS_KEHTIV, muidu 0=const.B_STAATUS_KEHTETU.';
COMMENT ON COLUMN hindamiskogum.vaikimisi IS 'kas on vaikimisi (automaatselt loodud) hindamiskogum';
COMMENT ON COLUMN hindamiskogum.kursus_kood IS 'lai või kitsas (matemaatika korral), klassifikaator KURSUS';
COMMENT ON COLUMN hindamiskogum.hindamine_kood IS 'hindamise liik, klassifikaator HINDAMINE';
COMMENT ON COLUMN hindamiskogum.kahekordne_hindamine IS 'kas on kahekordne hindamine (mitte-valimi korral)';
COMMENT ON COLUMN hindamiskogum.kahekordne_hindamine_valim IS 'kas on kahekordne hindamine (valimi korral)';
COMMENT ON COLUMN hindamiskogum.paarishindamine IS 'kas kahekordne hindamisel määratakse hindajate paarid või eraldi hindajad (paarishindamine on kasutusel ainult kirjaliku kahekordse hindamise korral)';
COMMENT ON COLUMN hindamiskogum.kontrollijaga_hindamine IS 'kas on kahe hindajaga ühekordne hindamine (üks hindab, teine kontrollib)';
COMMENT ON COLUMN hindamiskogum.on_digiteerimine IS 'kirjaliku p-testi skannimise korral (kui sisestuskogumis on määratud, et skannitakse): kas vastused digiteeritakse (tuvastatakse) või hõivatakse ainult pilt';
COMMENT ON COLUMN hindamiskogum.on_hindamisprotokoll IS 'kirjaliku p-testi sisestamise korral: kas sisestatakse hindamisprotokoll või sisestatakse vastused';
COMMENT ON COLUMN hindamiskogum.erinevad_komplektid IS 'hindamisprotokolliga p-testi korral: False - kõigil komplektidel on toorpunktid samad, printida kõigi komplektide kohta ühine hindamisprotokoll; True - eri komplektides on toorpunktid erinevad, tuleb printida iga komplekti jaoks eraldi hindamisprotokoll';
COMMENT ON COLUMN hindamiskogum.arvutihinnatav IS 'kas kõik testiülesanded on arvutihinnatavad';
COMMENT ON COLUMN hindamiskogum.on_markus_sooritajale IS 'kas hindaja saab hindamisel sooritajale märkusi kirjutada';
COMMENT ON COLUMN hindamiskogum.hindajate_erinevus IS 'lubatud erinevus hindajate vahel protsentides hindamiskogumi maksimaalse võimaliku hindepallide arvu suhtes';
COMMENT ON COLUMN hindamiskogum.hindamine3_loplik IS 'mida tehakse III hindamise tulemusega: true - III hindamise tulemus on lõplik tulemus; false - leitakse I,II,III hindamiste seast lähim paar ja kui ka selle paari hindamiserinevus on suur, siis tehakse IV hindamine';
COMMENT ON COLUMN hindamiskogum.max_pallid IS 'hindamiskogumisse kuuluvate testiülesannete pallide summa (uuendatakse testiülesande salvestamisel ning hindamiskogumisse määramisel)';
COMMENT ON COLUMN hindamiskogum.arvutus_kood IS 'hindamistulemuse arvutusviis, klassifikaator ARVUTUS: k=const.ARVUTUS_KESKMINE - hindajate punktide keskmine; s=const.ARVUTUS_SUMMA - kahe hindaja punktide summa (eeldab kahekordset hindamist)';
COMMENT ON COLUMN hindamiskogum.oma_kool_tasuta IS 'true - hindaja ja intervjueerija tasu arvestatakse ainult nende sooritajate eest, kes ei ole läbiviija oma kooli õpilased; false - tasu arvestatakse kõigi hinnatud tööde eest';
COMMENT ON COLUMN hindamiskogum.tasu IS 'kogumi hindamise tasu (korrutatakse sooritajate arvuga)';
COMMENT ON COLUMN hindamiskogum.intervjuu_lisatasu IS 'kogumi intervjueerimise eest hindamistasule juurde makstav tasu hindaja-intervjueerijale (korrutatakse sooritajate arvuga ja lisatakse hindaja tasule)';
COMMENT ON COLUMN hindamiskogum.intervjuu_tasu IS 'kogumi intervjueerimise tasu intervjueerijale, kes ei ole hindaja (korrutatakse sooritajate arvuga)';
COMMENT ON COLUMN hindamiskogum.sisestuskogum_id IS 'viide sisestuskogumile, kui mõni sisestuskogum sisaldab antud hindamiskogumit';
COMMENT ON COLUMN hindamiskogum.komplektivalik_id IS 'viide komplektivalikule';
COMMENT ON COLUMN hindamiskogum.created IS 'kirje loomise aeg';
COMMENT ON COLUMN hindamiskogum.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN hindamiskogum.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN hindamiskogum.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE hindamiskogum IS 'Ülesannete hindamiskogum.
    Hindamiskogumil on sisuline tähendus eeskätt kirjalikus testis (e-test või p-test),
    kuna hindamiskogumite kaupa antakse kirjaliku testi ülesandeid hindajatele hindamiseks.
    Kui hindamiskogumid on määratud suulises e-testis, siis antakse läbiviijale võimalus
    valida hindamiskogumit, aga ta hindab ikkagi soorituse kõik hindamiskogumid.
    Hindamiskogumite kaupa rühmitatakse ka süsteemi sees soorituse hindamisolekuid ja 
    seetõttu peab andmebaasis tegelikult igasuguse testi iga testiülesanne 
    kuuluma hindamiskogumisse. Kui kasutaja pole testiülesannet hindamiskogumisse määranud, 
    siis paigutatakse see automaatselt loodavasse vaikimisi hindamiskogumisse. 
    Ühe hindamiskogumi kõik ülesanded peavad kuuluma samasse komplektivalikusse.';

-- eis/model/test/taustakysitlus.py
COMMENT ON COLUMN taustakysitlus.id IS 'kirje identifikaator';
COMMENT ON COLUMN taustakysitlus.opilase_test_id IS 'viide õpilase testile';
COMMENT ON COLUMN taustakysitlus.opetaja_test_id IS 'viide õpetaja testile';
COMMENT ON COLUMN taustakysitlus.created IS 'kirje loomise aeg';
COMMENT ON COLUMN taustakysitlus.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN taustakysitlus.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN taustakysitlus.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE taustakysitlus IS 'Õpilase testi ja õpetaja testi seos, mis koos moodustavad taustaküsitluse';

-- eis/model/test/__init__.py
-- eis/model/test/nsgrupp.py
COMMENT ON COLUMN nsgrupp.id IS 'kirje identifikaator';
COMMENT ON COLUMN nsgrupp.testiosa_id IS 'viide testiosale';
COMMENT ON COLUMN nsgrupp.seq IS 'järjekorranumber testiosa sees';
COMMENT ON COLUMN nsgrupp.nimi IS 'grupi nimetus';
COMMENT ON COLUMN nsgrupp.created IS 'kirje loomise aeg';
COMMENT ON COLUMN nsgrupp.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN nsgrupp.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN nsgrupp.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE nsgrupp IS 'Diagnoosiva testi tagasiside grupp (nt "sa oskad", "sa ei oska")';

-- eis/model/test/sisestuskogum.py
COMMENT ON COLUMN sisestuskogum.id IS 'kirje identifikaator';
COMMENT ON COLUMN sisestuskogum.testiosa_id IS 'viide testiosale';
COMMENT ON COLUMN sisestuskogum.tahis IS 'tähis';
COMMENT ON COLUMN sisestuskogum.nimi IS 'nimetus';
COMMENT ON COLUMN sisestuskogum.hindamine_kood IS 'hindamise liik, klassifikaator HINDAMINE, peab olema sama kui selle sisestuskogumi hindamiskogumites';
COMMENT ON COLUMN sisestuskogum.on_skannimine IS 'p-testi korral: kas toimub skannimine või sisestamine';
COMMENT ON COLUMN sisestuskogum.on_hindamisprotokoll IS 'sisestatava p-testi korral: kas sisestuskogumis on mõni hindamiskogum, mida sisestatakse hindamisprotokolliga';
COMMENT ON COLUMN sisestuskogum.on_vastused IS 'sisestatava p-testi korral: kas sisestuskogumis on mõni hindamiskogum, mille korral sisestatakse vastused töölt (ühe töö kaupa)';
COMMENT ON COLUMN sisestuskogum.naita_pallid IS 'vastuste sisestamise korral: kas kuvada vastuste sisestajale sisestuskogumi eest arvutatud pallid ja toorpunktid';
COMMENT ON COLUMN sisestuskogum.tasu IS 'kogumi sisestamise tasu';
COMMENT ON COLUMN sisestuskogum.created IS 'kirje loomise aeg';
COMMENT ON COLUMN sisestuskogum.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN sisestuskogum.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN sisestuskogum.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE sisestuskogum IS 'Ülesannete sisestuskogum.
    Sisestuskogumil on mõte ainult p-testi korral.
    Sisestuskogumite kaupa toimub hindamisprotokollide sisestamine ja 
    objektiivse hindamisega sisestuskogumi korral vastuste sisestamine.
    Sisestuskogum koosneb hindamiskogumitest.
    Ühe sisestuskogumi kõik ülesanded peavad kuuluma samasse komplektivalikusse.';

-- eis/model/test/testsessioon.py
COMMENT ON COLUMN testsessioon.id IS 'kirje identifikaator';
COMMENT ON COLUMN testsessioon.seq IS 'järjekorranumber (testsessioonide loetelu järjestamiseks)';
COMMENT ON COLUMN testsessioon.nimi IS 'nimetus';
COMMENT ON COLUMN testsessioon.vaide_tahtaeg IS 'vaide tähtaeg';
COMMENT ON COLUMN testsessioon.oppeaasta IS 'õppeaasta, millesse testsessioon kuulub (läheb tunnistusele, selle põhjal genereeritakse ka tunnistuste numbreid)';
COMMENT ON COLUMN testsessioon.testiliik_kood IS 'testsessiooni kuuluvate testide liik, klassifikaator TESTILIIK';
COMMENT ON COLUMN testsessioon.staatus IS 'olek: 1 - kasutusel, 0 - pole kasutusel';
COMMENT ON COLUMN testsessioon.vaikimisi IS 'kas panna uute testimiskordade korral vaikimisi sessiooniks';
COMMENT ON COLUMN testsessioon.created IS 'kirje loomise aeg';
COMMENT ON COLUMN testsessioon.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN testsessioon.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN testsessioon.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE testsessioon IS 'Testsessioon';

-- eis/model/test/testiylesanne.py
COMMENT ON COLUMN testiylesanne.id IS 'kirje identifikaator';
COMMENT ON COLUMN testiylesanne.alatest_seq IS 'välja alatest.seq koopia, et oleks mugavam sortida';
COMMENT ON COLUMN testiylesanne.seq IS 'testiülesande järjekorranumber alatesti sees';
COMMENT ON COLUMN testiylesanne.nimi IS 'testiülesande nimetus';
COMMENT ON COLUMN testiylesanne.yhisosa_kood IS 'testiülesande kood (laia ja kitsa matemaatikaeksami ülesannete sidumiseks, samadel testiülesannetel peab olema sama kood)';
COMMENT ON COLUMN testiylesanne.tahis IS 'testiülesande järjekorranumber: alatestisisese nummerdamise korral koos alatesti järjekorranumbriga, üldise nummerdamise korral ilma; diagnoosiva testi jätkuülesande korral eelmise kobara ülesande number, punkt ja jätkuülesande jrk nr';
COMMENT ON COLUMN testiylesanne.on_jatk IS 'kas ülesanne on jätkuülesanne, milleni lahendaja jõuab ainult tabelis Nptagasiside kirjeldatud suunamise korral (diagnoosivas testis)';
COMMENT ON COLUMN testiylesanne.eristusindeks IS 'nõutav eristusindeks';
COMMENT ON COLUMN testiylesanne.hindamine_kood IS 'nõutav hindamise liik: subj=const.HINDAMINE_SUBJ - subjektiivne; obj=const.HINDAMINE_OBJ - objektiivne';
COMMENT ON COLUMN testiylesanne.arvutihinnatav IS 'kas on nõutav, et oleks arvutihinnatav';
COMMENT ON COLUMN testiylesanne.kasutusmaar IS 'nõutav kasutusmäär';
COMMENT ON COLUMN testiylesanne.aste_kood IS 'nõutav kooliaste/eriala, klassifikaator ASTE';
COMMENT ON COLUMN testiylesanne.mote_kood IS 'nõutav mõtlemistasand, klassifikaator MOTE';
COMMENT ON COLUMN testiylesanne.max_pallid IS 'max pallide arv, peab olema määratud enne struktuuri kinnitamist';
COMMENT ON COLUMN testiylesanne.yhisosa_max_pallid IS 'max pallide arv testimiskordade ühisossa kuuluvatest küsimustest';
COMMENT ON COLUMN testiylesanne.raskus IS 'nõutav raskus';
COMMENT ON COLUMN testiylesanne.teema_kood IS 'nõutav teema (varasem nimetus: valdkond) testi aines, klassifikaator TEEMA';
COMMENT ON COLUMN testiylesanne.alateema_kood IS 'nõutav alateema (varasem nimetus: teema), klassifikaator ALATEEMA';
COMMENT ON COLUMN testiylesanne.keeletase_kood IS 'nõutav keeleoskuse tase, klassifikaator KEELETASE';
COMMENT ON COLUMN testiylesanne.tyyp IS 'nõutav ülesandetüüp (vt sisuplokk.tyyp)';
COMMENT ON COLUMN testiylesanne.valikute_arv IS 'valikülesannete arv (mille seast lahendaja saab ise valida)';
COMMENT ON COLUMN testiylesanne.valik_auto IS 'true - valikülesande valib arvuti automaatselt; false - valikülesande valib lahendaja (kui valikute_arv > 1)';
COMMENT ON COLUMN testiylesanne.testiosa_id IS 'viide testiosale';
COMMENT ON COLUMN testiylesanne.testiplokk_id IS 'viide testiplokile (kui testiplokid on kasutusel, foreign_keys=testiplokk_id)';
COMMENT ON COLUMN testiylesanne.alatest_id IS 'viide alatestile (kui alatestid on kasutusel, foreign_keys=alatest_id)';
COMMENT ON COLUMN testiylesanne.hindamiskogum_id IS 'viide hindamiskogumile, millesse testiülesanne kuulub';
COMMENT ON COLUMN testiylesanne.sisestusviis IS 'vastuste sisestamise viis: 1=const.SISESTUSVIIS_VASTUS - e-test või p-testi vastuste sisestamine (ainult arvutihinnatava ülesande korral); 2=const.SISESTUSVIIS_OIGE - p-testi õige/vale hinnangu sisestamine; 3=const.SISESTUSVIIS_PALLID - p-testi toorpunktide sisestamine';
COMMENT ON COLUMN testiylesanne.hyppamisviis IS 'vastuste sisestamisel valikväljalt: 1 - kursor hüppab peale valikut automaatselt järgmisele väljale; 0 - ei hüppa automaatselt';
COMMENT ON COLUMN testiylesanne.sooritajajuhend IS 'juhend sooritajale (kasutusel valikülesande korral)';
COMMENT ON COLUMN testiylesanne.pealkiri IS 'pealkiri (kasutusel valikülesande korral)';
COMMENT ON COLUMN testiylesanne.liik IS 'testiülesande liik testi struktuuris: Y - ülesanne; T - tiitelleht; E - näide; G - juhend; K - küsimustik';
COMMENT ON COLUMN testiylesanne.kuvada_statistikas IS 'kas kuvada ülesanne statistikas';
COMMENT ON COLUMN testiylesanne.piiraeg IS 'ülesande sooritamiseks lubatud aja ülemine piir sekundites';
COMMENT ON COLUMN testiylesanne.piiraeg_sek IS 'true - aeg kuvada kohe sekundites; false, null - minutist suurem aeg kuvada ilma sekunditeta';
COMMENT ON COLUMN testiylesanne.min_aeg IS 'ülesande sooritamiseks lubatud aja alumine piir sekundites';
COMMENT ON COLUMN testiylesanne.hoiatusaeg IS 'piirajaga testiülesande korral: mitu sekundit enne lõppu antakse hoiatusteade';
COMMENT ON COLUMN testiylesanne.naita_max_p IS 'kas ülesande max pallid kuvada lahendajale';
COMMENT ON COLUMN testiylesanne.ise_jargmisele IS 'kas kohustusliku arvu vastuste andmisel minna automaatselt edasi järgmisele ülesandele';
COMMENT ON COLUMN testiylesanne.on_markus_sooritajale IS 'kas hindaja saab hindamisel sooritajale märkusi kirjutada';
COMMENT ON COLUMN testiylesanne.ei_naita_tulemustes IS 'kas ülesannet tulemustes ei näidata (jagatud töö korral)';
COMMENT ON COLUMN testiylesanne.created IS 'kirje loomise aeg';
COMMENT ON COLUMN testiylesanne.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN testiylesanne.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN testiylesanne.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE testiylesanne IS 'Testiülesanne (ülesandepesa, mis määratakse testi struktuuris
    ning mille sisse igas ülesandekomplektis valitakse ise ülesanne)';

-- eis/model/test/testimarkus.py
COMMENT ON COLUMN testimarkus.id IS 'kirje identifikaator';
COMMENT ON COLUMN testimarkus.test_id IS 'viide testile';
COMMENT ON COLUMN testimarkus.kasutaja_id IS 'viide kasutajale';
COMMENT ON COLUMN testimarkus.aeg IS 'märkuse kirjutamise aeg';
COMMENT ON COLUMN testimarkus.sisu IS 'märkuse sisu';
COMMENT ON COLUMN testimarkus.teema IS 'märkuse teema';
COMMENT ON COLUMN testimarkus.ylem_id IS 'viide ülemale märkusele, mida antud märkus kommenteerib';
COMMENT ON COLUMN testimarkus.created IS 'kirje loomise aeg';
COMMENT ON COLUMN testimarkus.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN testimarkus.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN testimarkus.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE testimarkus IS 'Testi märkused (eeltesti korral, korraldajate poolt)';

-- eis/model/test/testiosa.py
COMMENT ON COLUMN testiosa.id IS 'kirje identifikaator';
COMMENT ON COLUMN testiosa.nimi IS 'testiosa nimi';
COMMENT ON COLUMN testiosa.max_pallid IS 'max pallide arv';
COMMENT ON COLUMN testiosa.skoorivalem IS 'tulemuse arvutamise valem (kasutusel siis, kui tulemus ei ole ülesannete pallide summa)';
COMMENT ON COLUMN testiosa.alustajajuhend IS 'juhend sooritajale, mis kuvatakse enne testi alustamist';
COMMENT ON COLUMN testiosa.sooritajajuhend IS 'juhend sooritajale, mis kuvatakse siis, kui sooritamist on alustatud';
COMMENT ON COLUMN testiosa.tulemus_tunnistusele IS 'kas tulemus läheb tunnistusele';
COMMENT ON COLUMN testiosa.seq IS 'testiosa järjekorranumber testis';
COMMENT ON COLUMN testiosa.tahis IS 'testiosa tähis';
COMMENT ON COLUMN testiosa.vastvorm_kood IS 'vastamise vorm, klassifikaator VASTVORM: ke=const.VASTVORM_KE - kirjalik e-test; se=const.VASTVORM_SE - suuline e-test; i=const.VASTVORM_I - suuline (intervjuu); sh=const.VASTVORM_SH - suuline (hindajaga); kp=const.VASTVORM_KP - kirjalik (p-test); sp=const.VASTVORM_SP - suuline (p-test); n=const.VASTVORM_KONS - konsultatsioon';
COMMENT ON COLUMN testiosa.piiraeg IS 'testiosa sooritamiseks lubatud aeg sekundite';
COMMENT ON COLUMN testiosa.piiraeg_sek IS 'true - aeg kuvada kohe sekundites; false, null - minutist suurem aeg kuvada ilma sekunditeta';
COMMENT ON COLUMN testiosa.hoiatusaeg IS 'piirajaga testiosa korral: mitu sekundit enne lõppu antakse hoiatusteade';
COMMENT ON COLUMN testiosa.aeg_peatub IS 'kas testi sooritamise katkestamisel aeg peatub';
COMMENT ON COLUMN testiosa.ylesannete_arv IS 'ülesannete arv';
COMMENT ON COLUMN testiosa.on_alatestid IS 'kas testiosal on alatestid';
COMMENT ON COLUMN testiosa.test_id IS 'viide testile';
COMMENT ON COLUMN testiosa.rvosaoskus_id IS 'seos rahvusvahelise tunnistuse osaoskusega, mis vastab sellele (alatestideta, foreign_keys=rvosaoskus_id) testiosale';
COMMENT ON COLUMN testiosa.naita_max_p IS 'kas testiosa max pallid ja soorituse olek kuvada lahendajale';
COMMENT ON COLUMN testiosa.lotv IS 'kas on lõdva struktuuriga testiosa';
COMMENT ON COLUMN testiosa.yhesuunaline IS 'kas testiosa on ühesuunaliselt lahendatav (ülesanded tuleb lahendada kindlas järjekorras)';
COMMENT ON COLUMN testiosa.yl_lahk_hoiatus IS 'kas ühesuunalises testiosas ülesandelt lahkumisel kuvada hoiatus';
COMMENT ON COLUMN testiosa.yl_pooleli_hoiatus IS 'kas ühesuunalises testiosas pooleliolevalt ülesandelt lahkumisel kuvada hoiatus';
COMMENT ON COLUMN testiosa.yl_lahendada_lopuni IS 'kas kõigi ülesannete korral on vajalik kõik väljad täita ja ülesanne lõpuni lahendada';
COMMENT ON COLUMN testiosa.yl_segamini IS 'kas ülesanded kuvatakse lahendajale segatud järjekorras';
COMMENT ON COLUMN testiosa.ala_lahk_hoiatus IS 'kas ühekordselt alatestilt lahkumisel kuvada hoiatus';
COMMENT ON COLUMN testiosa.kuva_yl_nimetus IS 'kas lahendajale kuvada ülesande jrknr asemel nimetus (nii vasakul ribal kui ka ülesande kohal pealkirjas)';
COMMENT ON COLUMN testiosa.peida_yl_pealkiri IS 'kas lahendajale kuvada ülesande kohal ülesande jrknr/nimetus';
COMMENT ON COLUMN testiosa.pos_yl_list IS 'ülesannete loetelu kuvamine lahendajale: 0=const.POS_NAV_HIDDEN - ei kuva; 1=const.POS_NAV_LEFT - vasakul; 2=const.POS_NAV_TOP - ülal (ei saa kasutada)';
COMMENT ON COLUMN testiosa.peida_pais IS 'kas lahendajale kuvada EISi päis ja jalus või ainult ülesanded';
COMMENT ON COLUMN testiosa.yl_jrk_alatestiti IS 'kas ülesannete järjekorranumbrid algavad igas alatestis uuesti 1st';
COMMENT ON COLUMN testiosa.katkestatav IS 'kas sooritajale kuvatakse katkestamise nupp';
COMMENT ON COLUMN testiosa.lopetatav IS 'kas testi lõpetamise nupp on sooritajale alati nähtav (või ainult peale kõigi alatestide sooritamist)';
COMMENT ON COLUMN testiosa.created IS 'kirje loomise aeg';
COMMENT ON COLUMN testiosa.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN testiosa.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN testiosa.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE testiosa IS 'Testiosa';

-- eis/model/test/tagasisidevormidiagramm.py
-- eis/model/test/kritkirjeldus.py
COMMENT ON COLUMN kritkirjeldus.id IS 'kirje identifikaator';
COMMENT ON COLUMN kritkirjeldus.hindamiskriteerium_id IS 'viide hindamiskriteeriumile';
COMMENT ON COLUMN kritkirjeldus.punktid IS 'punktide arv (sammuga 0,5)';
COMMENT ON COLUMN kritkirjeldus.kirjeldus IS 'kirjeldus';
COMMENT ON COLUMN kritkirjeldus.created IS 'kirje loomise aeg';
COMMENT ON COLUMN kritkirjeldus.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN kritkirjeldus.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN kritkirjeldus.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE kritkirjeldus IS 'Hindamiskogumi hindamiskriteeriumi eest antavate punktide kirjeldus';

-- eis/model/test/testiisik.py
COMMENT ON COLUMN testiisik.id IS 'kirje identifikaator';
COMMENT ON COLUMN testiisik.kasutaja_id IS 'viide kasutajale';
COMMENT ON COLUMN testiisik.kasutajagrupp_id IS 'viide kasutajagrupile';
COMMENT ON COLUMN testiisik.test_id IS 'viide testile';
COMMENT ON COLUMN testiisik.kehtib_alates IS 'õiguse kehtimise algus';
COMMENT ON COLUMN testiisik.kehtib_kuni IS 'õiguse kehtimise lõpp';
COMMENT ON COLUMN testiisik.created IS 'kirje loomise aeg';
COMMENT ON COLUMN testiisik.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN testiisik.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN testiisik.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE testiisik IS 'Testiga seotud isik';

-- eis/model/test/erialatest.py
COMMENT ON COLUMN erialatest.id IS 'kirje identifikaator';
COMMENT ON COLUMN erialatest.lisaaeg IS 'testi sooritamiseks antav lisaaeg sekundites, lisandub testiosa piirajale';
COMMENT ON COLUMN erialatest.dif_hindamine IS 'kas on diferentseeritud hindamine';
COMMENT ON COLUMN erialatest.komplekt_id IS 'viide ülesandekomplektile';
COMMENT ON COLUMN erialatest.alatest_id IS 'viide alatestile';
COMMENT ON COLUMN erialatest.created IS 'kirje loomise aeg';
COMMENT ON COLUMN erialatest.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN erialatest.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN erialatest.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE erialatest IS 'Testi ülesandekomplekti erivajaduste erisused alatestide kaupa';

-- eis/model/test/toofailitase.py
COMMENT ON COLUMN toofailitase.id IS 'kirje identifikaator';
COMMENT ON COLUMN toofailitase.toofail_id IS 'viide failile';
COMMENT ON COLUMN toofailitase.kavatase_kood IS 'õppekavajärgne haridustase, klassifikaator KAVATASE';
COMMENT ON COLUMN toofailitase.created IS 'kirje loomise aeg';
COMMENT ON COLUMN toofailitase.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN toofailitase.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN toofailitase.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE toofailitase IS 'Õppekavad ja õppekavajärgsed haridustasemed, mida omaval koolil on võimalus faili alla laadida
    Võimalikud haridustasemed sõltuvad õppetasemest.';

-- eis/model/rveksam/rveksamitulemus.py
COMMENT ON COLUMN rveksamitulemus.id IS 'kirje identifikaator';
COMMENT ON COLUMN rveksamitulemus.rveksam_id IS 'viide eksamile';
COMMENT ON COLUMN rveksamitulemus.seq IS 'järjekorranumber';
COMMENT ON COLUMN rveksamitulemus.tahis IS 'tulemuse tähis';
COMMENT ON COLUMN rveksamitulemus.alates IS 'pallide või protsentide vahemiku algus';
COMMENT ON COLUMN rveksamitulemus.kuni IS 'pallide või protsentide vahemiku lõpp';
COMMENT ON COLUMN rveksamitulemus.keeletase_kood IS 'keeleoskuse tase, klassifikaator KEELETASE';
COMMENT ON COLUMN rveksamitulemus.created IS 'kirje loomise aeg';
COMMENT ON COLUMN rveksamitulemus.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN rveksamitulemus.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN rveksamitulemus.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE rveksamitulemus IS 'Rahvusvahelise eksami kogutulemuse esitamise valikud';

-- eis/model/rveksam/rveksam.py
COMMENT ON COLUMN rveksam.id IS 'kirje identifikaator';
COMMENT ON COLUMN rveksam.nimi IS 'eksami nimetus';
COMMENT ON COLUMN rveksam.rveksam_kood IS 'rahvusvaheliselt tunnustatud eksamite klassifikaator';
COMMENT ON COLUMN rveksam.aine_kood IS 'õppeaine, klassifikaator AINE (määrab keele - inglise, saksa, vene või prantsuse)';
COMMENT ON COLUMN rveksam.keeletase_kood IS 'keeleoskuse tase, klassifikaator KEELETASE (kui on NULL, siis on tase kirjeldatud tulemuste juures)';
COMMENT ON COLUMN rveksam.vastab_tasemele IS 'true - vastab tasemele; false - võrreldav tasemega';
COMMENT ON COLUMN rveksam.on_tase_tunnistusel IS 'kas tunnistusele on märgitud kogutulemus EN skaalal';
COMMENT ON COLUMN rveksam.on_tulemus_tunnistusel IS 'kas kogutulemus on märgitud tunnistusele';
COMMENT ON COLUMN rveksam.on_tulemus_sooritusteatel IS 'kas kogutulemus on märgitud sooritusteatele';
COMMENT ON COLUMN rveksam.on_osaoskused_tunnistusel IS 'kas osaoskuste tulemus on märgitud tunnistusele';
COMMENT ON COLUMN rveksam.on_osaoskused_sooritusteatel IS 'kas osaoskuste tulemus on märgitud sooritusteatele';
COMMENT ON COLUMN rveksam.on_osaoskused_jahei IS 'kas osaoskuste läbimine märgitakse linnukesega';
COMMENT ON COLUMN rveksam.on_kehtivusaeg IS 'kas sisestatakse kuupäevade vahemik, mil tunnistus kehtib';
COMMENT ON COLUMN rveksam.on_tunnistusenr IS 'kas sisestatakse tunnistusenumber';
COMMENT ON COLUMN rveksam.tulemusviis IS 'tulemuse esitamise viis (P - pallid, S - protsendid, T - tähised)';
COMMENT ON COLUMN rveksam.alates IS 'pallide või protsentide vahemiku algus';
COMMENT ON COLUMN rveksam.kuni IS 'pallide või protsentide vahemiku lõpp';
COMMENT ON COLUMN rveksam.markus IS 'märkused';
COMMENT ON COLUMN rveksam.kantav_tulem IS 'kas sisestamisel on võimalik kanda tulemusi tunnistuselt testisooritusele';
COMMENT ON COLUMN rveksam.created IS 'kirje loomise aeg';
COMMENT ON COLUMN rveksam.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN rveksam.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN rveksam.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE rveksam IS 'Niisuguse rahvusvahelise eksami kirjeldus, mida EIS ei korralda, kuid mille tunnistuste kirjed on EISis';

-- eis/model/rveksam/rvsooritus.py
COMMENT ON COLUMN rvsooritus.id IS 'kirje identifikaator';
COMMENT ON COLUMN rvsooritus.rvsooritaja_id IS 'viide eksamisooritusele';
COMMENT ON COLUMN rvsooritus.rvosaoskus_id IS 'osaoskus';
COMMENT ON COLUMN rvsooritus.rvosatulemus_id IS 'viide tulemusele';
COMMENT ON COLUMN rvsooritus.tulemus IS 'tulemus pallides või protsentides';
COMMENT ON COLUMN rvsooritus.on_labinud IS 'kas vastab osaoskusega nõutud tasemele (kui eksami juures on märgitud rveksam.on_osaoskused_jahei)';
COMMENT ON COLUMN rvsooritus.created IS 'kirje loomise aeg';
COMMENT ON COLUMN rvsooritus.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN rvsooritus.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN rvsooritus.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE rvsooritus IS 'Rahvusvahelise eksami osaoskuse soorituse andmed';

-- eis/model/rveksam/__init__.py
-- eis/model/rveksam/rvosatulemus.py
COMMENT ON COLUMN rvosatulemus.id IS 'kirje identifikaator';
COMMENT ON COLUMN rvosatulemus.rvosaoskus_id IS 'viide osaoskusele';
COMMENT ON COLUMN rvosatulemus.seq IS 'järjekorranumber';
COMMENT ON COLUMN rvosatulemus.tahis IS 'tulemuse tähis';
COMMENT ON COLUMN rvosatulemus.alates IS 'pallide või protsentide vahemiku algus';
COMMENT ON COLUMN rvosatulemus.kuni IS 'pallide või protsentide vahemiku lõpp';
COMMENT ON COLUMN rvosatulemus.created IS 'kirje loomise aeg';
COMMENT ON COLUMN rvosatulemus.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN rvosatulemus.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN rvosatulemus.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE rvosatulemus IS 'Rahvusvahelise eksami osaoskuse tulemuse esitamise valikud';

-- eis/model/rveksam/rvsooritaja.py
COMMENT ON COLUMN rvsooritaja.id IS 'kirje identifikaator';
COMMENT ON COLUMN rvsooritaja.rveksam_id IS 'viide eksamile';
COMMENT ON COLUMN rvsooritaja.tunnistus_id IS 'viide tunnistusele';
COMMENT ON COLUMN rvsooritaja.sooritaja_id IS 'viide sooritaja kirjele juhul, kui rahvusvahelise eksami tunnistus on antud EISis tehtud testi põhjal';
COMMENT ON COLUMN rvsooritaja.kehtib_kuni IS 'tunnistuse kehtivuse lõpp';
COMMENT ON COLUMN rvsooritaja.keeletase_kood IS 'keeleoskuse tase, klassifikaator KEELETASE';
COMMENT ON COLUMN rvsooritaja.rveksamitulemus_id IS 'viide tulemusele (tulemuse kirjes on ka saadud keeletase, foreign_keys=rveksamitulemus_id)';
COMMENT ON COLUMN rvsooritaja.tulemus IS 'tulemus pallides või protsentides';
COMMENT ON COLUMN rvsooritaja.arvest_lopetamisel IS 'kas tunnistust arvestatakse lõpetamise tingimuste kontrollimisel';
COMMENT ON COLUMN rvsooritaja.created IS 'kirje loomise aeg';
COMMENT ON COLUMN rvsooritaja.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN rvsooritaja.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN rvsooritaja.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE rvsooritaja IS 'Rahvusvahelise eksami soorituse andmed';

-- eis/model/rveksam/rvosaoskus.py
COMMENT ON COLUMN rvosaoskus.id IS 'kirje identifikaator';
COMMENT ON COLUMN rvosaoskus.rveksam_id IS 'viide eksamile';
COMMENT ON COLUMN rvosaoskus.seq IS 'osaoskuse järjekorranumber';
COMMENT ON COLUMN rvosaoskus.nimi IS 'osaoskuse nimetus';
COMMENT ON COLUMN rvosaoskus.alates IS 'pallide või protsentide vahemiku algus';
COMMENT ON COLUMN rvosaoskus.kuni IS 'pallide või protsentide vahemiku lõpp';
COMMENT ON COLUMN rvosaoskus.created IS 'kirje loomise aeg';
COMMENT ON COLUMN rvosaoskus.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN rvosaoskus.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN rvosaoskus.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE rvosaoskus IS 'Rahvusvahelise eksami osaoskuse kirjeldus';

-- $Id: comments.sql 2517 2011-12-14 16:58:37Z eeahtkeld $
-- Kommentaaride erandid, mis ei kajastu Elixiri klassides olevates kommentaarides

COMMENT ON TABLE beaker_cache IS 'Kasutajaseansid';
COMMENT ON COLUMN beaker_cache.namespace IS 'seansi identifikaator';
COMMENT ON COLUMN beaker_cache.accessed IS 'viimase aktiivsuse aeg';
COMMENT ON COLUMN beaker_cache.created IS 'seansi loomise aeg';
COMMENT ON COLUMN beaker_cache.data IS 'seansi andmed';
COMMENT ON COLUMN beaker_cache.kasutaja_id IS 'viide kasutajale';
COMMENT ON COLUMN beaker_cache.autentimine IS 'autentimisviis';
COMMENT ON COLUMN beaker_cache.kehtetu IS 'kas seanss on juba kehtetu';
COMMENT ON COLUMN beaker_cache.remote_addr IS 'kasutaja kliendi host';
COMMENT ON COLUMN beaker_cache.app IS 'rakendus';

COMMENT ON COLUMN klassifikaator.ylem_kood IS 'viide ülemklassifikaatorile (klassifikaatorite hierarhia korral)';
COMMENT ON COLUMN klrida.klassifikaator_kood IS 'viide klassifikaatorile, mille väärtust kirje kirjeldab';

COMMENT ON COLUMN piirkond_kord.testimiskord_id IS 'viide testimiskorrale';
COMMENT ON COLUMN piirkond_kord.piirkond_id IS 'viide piirkonnale';
COMMENT ON TABLE piirkond_kord IS 'Piirkonnad, kus testimiskord läbi viiakse';

COMMENT ON COLUMN sisuobjekt.row_type IS 'sisuobjekti tüüp: b - taustobjekt; g - lohistatav pilt; m - multimeedia';

COMMENT ON COLUMN testimiskord_kiirvalik.testimiskord_id IS 'viide testimiskorrale';
COMMENT ON COLUMN testimiskord_kiirvalik.kiirvalik_id IS 'viide kiirvalikule';
COMMENT ON TABLE testimiskord_kiirvalik IS 'Kiirvalikud, kuhu testimiskord kuulub';


COMMENT ON COLUMN toimumisaeg_komplekt.komplekt_id IS 'viide ülesandekomplektile';
COMMENT ON COLUMN toimumisaeg_komplekt.toimumisaeg_id IS 'viide toimumisajale';
COMMENT ON TABLE toimumisaeg_komplekt IS 'Ülesandekomplektid, mis on antud toimumisajal kasutusel';

COMMENT ON COLUMN valik.row_type IS 'valiku tüüp: h - piirkond pildil; NULL - tekst';

COMMENT ON COLUMN ylesandefail.row_type IS 'faili tüüp: a - ülesande fail; s - ülesande lahenduse fail; o - ülesande lähtematerjal';
