-- Kommentaarid genereeritud SQLAlchemy klasside kommentaaridest.
-- Muudatused teha SQLAlchemy klassides, mitte käsitsi siin.
-- eis/model_s/ylesandevaatamine.py
COMMENT ON COLUMN ylesandevaatamine.id IS 'kirje identifikaator';
COMMENT ON COLUMN ylesandevaatamine.sooritus_id IS 'viide sooritusele';
COMMENT ON COLUMN ylesandevaatamine.valitudylesanne_id IS 'viide valitudülesandele';
COMMENT ON COLUMN ylesandevaatamine.testiylesanne_id IS 'viide testiülesandele';
COMMENT ON COLUMN ylesandevaatamine.komplekt_id IS 'viide komplektile';
COMMENT ON COLUMN ylesandevaatamine.algus IS 'ylesande lugemise aeg';
COMMENT ON COLUMN ylesandevaatamine.created IS 'kirje loomise aeg';
COMMENT ON COLUMN ylesandevaatamine.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN ylesandevaatamine.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN ylesandevaatamine.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE ylesandevaatamine IS 'Ülesande esmase lahendajale kuvamise aja salvestamise tabel.
    Aega ei salvestata kohe tabelis Ylesandevastus, sest valikülesande korral
    võib lahendaja vaadata mitut valikut ning kõigi algusaeg on vaja salvestada,
    kuid Ylesandevastuse tabelis on jooksvalt üheainsa valiku kirje';

-- eis/model_s/entityhelper.py
COMMENT ON COLUMN entityhelper.created IS 'kirje loomise aeg';
COMMENT ON COLUMN entityhelper.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN entityhelper.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN entityhelper.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE entityhelper IS 'Andmeklasside olemite baasklass, mis lisab ühised meetodid';

-- eis/model_s/esitlus.py
COMMENT ON COLUMN esitlus.id IS 'kirje identifikaator';
COMMENT ON COLUMN esitlus.ylesanne_id IS 'viide ülesandele';
COMMENT ON COLUMN esitlus.kasutaja_id IS 'viide kasutajale';
COMMENT ON COLUMN esitlus.sisu IS 'IFRAME sisu (ettetehtud esitluse korral)';
COMMENT ON COLUMN esitlus.lang IS 'esitluse keel';
COMMENT ON COLUMN esitlus.oige_nahtav IS 'kas kasutaja tohib vaadata õiget vastust';
COMMENT ON COLUMN esitlus.hindaja IS 'kas kasutaja on hindaja (hindaja näeb näidisvastuseid)';
COMMENT ON COLUMN esitlus.hindamine_id IS 'kui kasutaja on hindaja, siis hindamise id';
COMMENT ON COLUMN esitlus.lahendaja IS 'kas saab vastata';
COMMENT ON COLUMN esitlus.ettetehtud IS 'kas esitlus on ettetehtud kõigile sooritajatele (ettetehtud esitlus on genereeritud ülesande koostamisel, et testisooritamisel ei peaks kõigile sooritajatele eraldi genereerima)';
COMMENT ON COLUMN esitlus.sooritus_id IS 'viide testiosa soorituse kirjele (kui on < 0, siis on TempSooritus)';
COMMENT ON COLUMN esitlus.ylesandevastus_id IS 'viide vastusele (kui on < 0, siis on TempYlesandevastus)';
COMMENT ON COLUMN esitlus.valitudylesanne_id IS 'viide valitud ülesande kirjele';
COMMENT ON COLUMN esitlus.created IS 'kirje loomise aeg';
COMMENT ON COLUMN esitlus.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN esitlus.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN esitlus.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE esitlus IS 'Ülesande sisu laaditakse põhiaknas oleva IFRAME sisse.
    - Kui on antud kasutaja_id, siis kirje luuakse (testi) põhilehe genereerimisel
    ning on kasutusel selleks, et IFRAME laadimisel veenduda ülesande vaatamise
    õiguse olemasolus ning määrata ülesande kuvamise parameetrid.
    Ülesande sisu genereeritakse sel juhul IFRAME laadimisel ning seda ei salvestata.
    - Kui kasutaja_id=NULL ja ettetehtud=true, siis on ette valmis genereeritud sisu,
    mis kuvatakse kõigile testisooritajatele, kes alustavad ülesande lahendamist,
    et süsteem ei peaks iga testisooritaja jaoks eraldi sisu genereerima hakkama.';

-- eis/model_s/toorvastus.py
COMMENT ON COLUMN toorvastus.id IS 'kirje identifikaator';
COMMENT ON COLUMN toorvastus.ylesandevastus_id IS 'põhibaasi ylesandevastus.id';
COMMENT ON COLUMN toorvastus.kood IS 'küsimuse kood';
COMMENT ON COLUMN toorvastus.sisu IS 'tekstvastus (kui pole fail)';
COMMENT ON COLUMN toorvastus.filename IS 'failinimi (kui on fail)';
COMMENT ON COLUMN toorvastus.filesize IS 'faili suurus baitides';
COMMENT ON COLUMN toorvastus.fileversion IS 'versioon';
COMMENT ON COLUMN toorvastus.on_pickle IS 'kas filedata sisaldab pickle-pakitud sisu (kasutusel siis, kui vastus on list)';
COMMENT ON COLUMN toorvastus.created IS 'kirje loomise aeg';
COMMENT ON COLUMN toorvastus.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN toorvastus.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN toorvastus.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE toorvastus IS 'Testi sooritamise ajal saadetud ühe ülesande vastused.
    Tulemuste arvutamise ajal jagatakse need andmed põhibaasi tabelitesse
    kysimusevastus ja kvsisu, kuid see võtab aega ning testiaegse jõudluse
    optimeerimiseks tehakse seda alles siis, kui on vaja arvutada tulemusi.
    Kuni toorvastus ei ole veel põhibaasi viidud,
    seni on põhibaasis ylesandevastus.on_toorvastus = True';

-- eis/model_s/__init__.py
-- eis/model_s/beaker_cache.py
COMMENT ON COLUMN beaker_cache.id IS 'kirje identifikaator';
COMMENT ON COLUMN beaker_cache.namespace IS 'seansi identifikaator';
COMMENT ON COLUMN beaker_cache.accessed IS 'viimase kasutamise aeg';
COMMENT ON COLUMN beaker_cache.created IS 'loomise aeg';
COMMENT ON COLUMN beaker_cache.data IS 'andmed';
COMMENT ON COLUMN beaker_cache.kasutaja_id IS 'kasutaja ID';
COMMENT ON COLUMN beaker_cache.autentimine IS 'autentimisviis';
COMMENT ON COLUMN beaker_cache.kehtetu IS 'kas seanss on kehtiv';
COMMENT ON COLUMN beaker_cache.remote_addr IS 'kasutaja aadress';
COMMENT ON COLUMN beaker_cache.app IS 'rakenduse nimi';
COMMENT ON TABLE beaker_cache IS 'Kasutajate seansid';

-- eis/model_s/meta.py
-- eis/model_s/tempvastus.py
COMMENT ON COLUMN tempvastus.id IS 'kirje identifikaator';
COMMENT ON COLUMN tempvastus.temp_id IS 'vastuse id';
COMMENT ON COLUMN tempvastus.filename IS 'failinimi';
COMMENT ON COLUMN tempvastus.filedata IS 'faili sisu';
COMMENT ON COLUMN tempvastus.uuid IS 'äraarvamatu osa URList faili laadimise korral';
COMMENT ON COLUMN tempvastus.created IS 'kirje loomise aeg';
COMMENT ON COLUMN tempvastus.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN tempvastus.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN tempvastus.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE tempvastus IS 'Lahendaja poolt üles laaditud failide ajutine hoiupaik,
    kui ülesannet lahendatakse proovimiseks, ilma vastuseid salvestamata';

