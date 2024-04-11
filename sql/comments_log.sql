-- Kommentaarid genereeritud SQLAlchemy klasside kommentaaridest.
-- Muudatused teha SQLAlchemy klassides, mitte käsitsi siin.
-- eis/model_log/logi.py
COMMENT ON COLUMN logi.id IS 'kirje identifikaator';
COMMENT ON COLUMN logi.uuid IS 'logikirje identifikaator';
COMMENT ON COLUMN logi.request_id IS 'brauseri pöördumise identifikaator';
COMMENT ON COLUMN logi.aeg IS 'logikirje aeg';
COMMENT ON COLUMN logi.isikukood IS 'kasutaja isikukood';
COMMENT ON COLUMN logi.kontroller IS 'rakenduse kontroller, milles logisündmus tekkis (või muu lk identifikaator)';
COMMENT ON COLUMN logi.tegevus IS 'rakenduse tegevus, milles logisündmus tekkis';
COMMENT ON COLUMN logi.param IS 'rakenduse parameetrid, kui logisündmus tekkis';
COMMENT ON COLUMN logi.tyyp IS 'logitüüp: 1 - kasutuslogi; 2 - vealogi; 3 - sisselogimise logi; 4 - kasutajaõiguste muutmine; 5 - X-tee kliendi sõnumite logi; 6 - muu info; 7 - JSON sõnum; 8 - koha valik; 9 - webhook';
COMMENT ON COLUMN logi.sisu IS 'logi sisu';
COMMENT ON COLUMN logi.url IS 'tegevuse URL';
COMMENT ON COLUMN logi.path IS 'URLis sisalduv rada';
COMMENT ON COLUMN logi.meetod IS 'HTTP meetod (get, post)';
COMMENT ON COLUMN logi.remote_addr IS 'klient';
COMMENT ON COLUMN logi.server_addr IS 'server';
COMMENT ON COLUMN logi.user_agent IS 'brauser';
COMMENT ON COLUMN logi.app IS 'rakendus: eis, ekk, plank, adapter';
COMMENT ON COLUMN logi.koht_id IS 'viide töökohale';
COMMENT ON COLUMN logi.oppekoht_id IS 'viide koolile, kus kasutaja õpib';
COMMENT ON COLUMN logi.testiosa_id IS 'viide testiosale, kui see on testi sooritamisel tekkinud logi (testisoorituste arvu saamiseks ajavahemikul)';
COMMENT ON COLUMN logi.kestus IS 'päringu kestus sekundites';
COMMENT ON TABLE logi IS 'Sündmuste ja veateadete logi';

-- eis/model_log/entityhelper.py
COMMENT ON COLUMN entityhelper.created IS 'kirje loomise aeg';
COMMENT ON COLUMN entityhelper.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN entityhelper.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN entityhelper.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE entityhelper IS 'Andmeklasside olemite baasklass, mis lisab ühised meetodid';

-- eis/model_log/ltest.py
COMMENT ON COLUMN ltest.id IS 'kirje identifikaator';
COMMENT ON COLUMN ltest.aeg IS 'logikirje aeg';
COMMENT ON COLUMN ltest.algus IS 'pöördumise alguse aeg (sama pöördumise transaktsioonide sidumiseks)';
COMMENT ON COLUMN ltest.isikukood IS 'kasutaja isikukood';
COMMENT ON COLUMN ltest.kestus IS 'transaktsiooni kestus ms';
COMMENT ON COLUMN ltest.liik IS 'transaktsiooni lõpp: commit/rollback';
COMMENT ON COLUMN ltest.url IS 'tegevuse URL';
COMMENT ON COLUMN ltest.meetod IS 'HTTP meetod (get, post)';
COMMENT ON COLUMN ltest.remote_addr IS 'klient';
COMMENT ON COLUMN ltest.server_addr IS 'server';
COMMENT ON COLUMN ltest.user_agent IS 'brauser';
COMMENT ON COLUMN ltest.test_jrk IS 'koormustesti jrk nr (omistatakse peale testi lõppu)';
COMMENT ON TABLE ltest IS 'Koormustesti logiandmed';

-- eis/model_log/haridlog.py
COMMENT ON COLUMN haridlog.id IS 'kirje identifikaator';
COMMENT ON COLUMN haridlog.state IS 'genereeritud juharvu räsi';
COMMENT ON COLUMN haridlog.nonce IS 'genereeritud juhuarv';
COMMENT ON COLUMN haridlog.aut_aeg IS 'autentimispäringu aeg';
COMMENT ON COLUMN haridlog.aut_params IS 'autentimispäringu parameetrid';
COMMENT ON COLUMN haridlog.resp_params IS 'autentimispäringu vastus GET URL';
COMMENT ON COLUMN haridlog.resp_aeg IS 'autentimispäringu vastuse aeg';
COMMENT ON COLUMN haridlog.token_data IS 'identifitseerimistõendi kest';
COMMENT ON COLUMN haridlog.token_msg IS 'identifitseerimistõendi sisu peale lahti kodeerimist';
COMMENT ON COLUMN haridlog.userinfo_msg IS 'infopäringu vastus';
COMMENT ON COLUMN haridlog.isikukood IS 'autenditud kasutaja riik ja isikukood';
COMMENT ON COLUMN haridlog.eesnimi IS 'autenditud kasutaja eesnimi';
COMMENT ON COLUMN haridlog.perenimi IS 'autenditud kasutaja perekonnanimi';
COMMENT ON COLUMN haridlog.err IS 'vea kood (vt loginharid.py)';
COMMENT ON COLUMN haridlog.request_url IS 'EISi URL, mille poole pöördudes suunati kasutaja autentima ja kuhu peale autentimist kasutaja tagasi suuname';
COMMENT ON COLUMN haridlog.remote_addr IS 'klient';
COMMENT ON COLUMN haridlog.server1_addr IS 'server, kust autentimist alustati';
COMMENT ON COLUMN haridlog.server2_addr IS 'server, kuhu kasutaja HarIDist tagasi suunati';
COMMENT ON COLUMN haridlog.created IS 'kirje loomise aeg';
COMMENT ON COLUMN haridlog.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN haridlog.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN haridlog.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE haridlog IS 'HarID autentimispäringute logi';

-- eis/model_log/__init__.py
-- eis/model_log/meta.py
-- eis/model_log/logi_adapter.py
COMMENT ON COLUMN logi_adapter.id IS 'kirje identifikaator';
COMMENT ON COLUMN logi_adapter.algus IS 'päringu alguse aeg';
COMMENT ON COLUMN logi_adapter.aeg IS 'logikirje aeg (päringu lõpp)';
COMMENT ON COLUMN logi_adapter.client IS 'kliendi andmed';
COMMENT ON COLUMN logi_adapter.userid IS 'riigi kood ja isikukood';
COMMENT ON COLUMN logi_adapter.service IS 'kasutatud teenuse nimi';
COMMENT ON COLUMN logi_adapter.input_xml IS 'sisendi XML/JSON';
COMMENT ON COLUMN logi_adapter.output_xml IS 'väljundi XML/JSON';
COMMENT ON COLUMN logi_adapter.remote_addr IS 'klient';
COMMENT ON COLUMN logi_adapter.server_addr IS 'server';
COMMENT ON COLUMN logi_adapter.url IS 'URL';
COMMENT ON COLUMN logi_adapter.tyyp IS 'J - JSON; X - XML';
COMMENT ON TABLE logi_adapter IS 'X-tee serveri logi';

-- eis/model_log/taralog.py
COMMENT ON COLUMN taralog.id IS 'kirje identifikaator';
COMMENT ON COLUMN taralog.state IS 'genereeritud juharvu räsi';
COMMENT ON COLUMN taralog.nonce IS 'genereeritud juhuarv';
COMMENT ON COLUMN taralog.aut_aeg IS 'autentimispäringu aeg';
COMMENT ON COLUMN taralog.aut_params IS 'autentimispäringu parameetrid';
COMMENT ON COLUMN taralog.resp_params IS 'autentimispäringu vastus GET URL';
COMMENT ON COLUMN taralog.resp_aeg IS 'autentimispäringu vastuse aeg';
COMMENT ON COLUMN taralog.token_data IS 'identifitseerimistõendi kest';
COMMENT ON COLUMN taralog.token_msg IS 'identifitseerimistõendi sisu peale lahti kodeerimist';
COMMENT ON COLUMN taralog.isikukood IS 'autenditud kasutaja riik ja isikukood';
COMMENT ON COLUMN taralog.eesnimi IS 'autenditud kasutaja eesnimi';
COMMENT ON COLUMN taralog.perenimi IS 'autenditud kasutaja perekonnanimi';
COMMENT ON COLUMN taralog.err IS 'vea kood (vt logintara.py)';
COMMENT ON COLUMN taralog.request_url IS 'EISi URL, mille poole pöördudes suunati kasutaja autentima ja kuhu peale autentimist kasutaja tagasi suuname';
COMMENT ON COLUMN taralog.remote_addr IS 'klient';
COMMENT ON COLUMN taralog.created IS 'kirje loomise aeg';
COMMENT ON COLUMN taralog.modified IS 'kirje viimase muutmise aeg';
COMMENT ON COLUMN taralog.creator IS 'kirje looja isikukood';
COMMENT ON COLUMN taralog.modifier IS 'kirje viimase muutja isikukood';
COMMENT ON TABLE taralog IS 'TARA autentimispäringute logi';

