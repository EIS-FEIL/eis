-- Indeksid, mida ei loo SQLAlchemy

--CREATE INDEX ix_aadresskomponent_tase_kood ON aadresskomponent USING btree (tase, kood);
CREATE INDEX ix_aadresskomponent_ylem_tase_kood ON aadresskomponent USING btree (ylemkomp_tase, ylemkomp_kood);

CREATE INDEX aadress_idx ON aadress USING gin(to_tsvector('simple',tais_aadress));

CREATE INDEX ix_aadress_kood1 ON aadress USING btree (kood1);
CREATE INDEX ix_aadress_kood2 ON aadress USING btree (kood2);
CREATE INDEX ix_aadress_kood3 ON aadress USING btree (kood3);
CREATE INDEX ix_aadress_kood4 ON aadress USING btree (kood4);
CREATE INDEX ix_aadress_kood5 ON aadress USING btree (kood5);
CREATE INDEX ix_aadress_kood6 ON aadress USING btree (kood6);
CREATE INDEX ix_aadress_kood7 ON aadress USING btree (kood7);
CREATE INDEX ix_aadress_kood8 ON aadress USING btree (kood8);

CREATE INDEX ix_aadress_adr_id ON aadress USING btree (adr_id);

CREATE INDEX ix_test_staatus ON test USING btree (staatus);

CREATE INDEX ix_ylesanne_staatus ON ylesanne USING btree (staatus);

--CREATE INDEX ix_kasutaja_isikukood ON kasutaja USING btree (isikukood);

-- klassifikaatorite indeksid

--  select 'CREATE INDEX ix_'||table_name||'_'||replace(column_name,'_kood','')||' ON '||table_schema||'.'||table_name||' USING btree ('||column_name||');' 
--  from information_Schema.columns where column_name like '%_kood' and is_updatable='YES'
--  order by table_schema, table_name

CREATE INDEX ix_kyse_shvaldkond ON kysi.kyse USING btree (shvaldkond_kood);
CREATE INDEX ix_kysesihtryhm_sihtryhm ON kysi.kysesihtryhm USING btree (sihtryhm_kood);
CREATE INDEX ix_kysitlus_sihtryhm ON kysi.kysitlus USING btree (sihtryhm_kood);
CREATE INDEX ix_kysitlusvaldkond_shvaldkond ON kysi.kysitlusvaldkond USING btree (shvaldkond_kood);
CREATE INDEX ix_taustsihtryhm_sihtryhm ON kysi.taustsihtryhm USING btree (sihtryhm_kood);
CREATE INDEX ix_vastus_vastamata ON kysi.vastus USING btree (vastamata_kood);

CREATE INDEX ix_plangiliik_oppetase ON plank.plangiliik USING btree (oppetase_kood);
CREATE INDEX ix_plangitase_kavatase ON plank.plangitase USING btree (kavatase_kood);
CREATE INDEX ix_plank_isikukood ON plank.plank USING btree (isikukood);
CREATE INDEX ix_vahemik_mahakandp ON plank.vahemik USING btree (mahakandp_kood);

CREATE INDEX ix_aadresskomponent_ylemkomp ON public.aadresskomponent USING btree (ylemkomp_kood);
CREATE INDEX ix_ainelabiviija_aine ON public.ainelabiviija USING btree (aine_kood);
CREATE INDEX ix_ainepdf_aine ON public.ainepdf USING btree (aine_kood);
CREATE INDEX ix_aineprofiil_aine ON public.aineprofiil USING btree (aine_kood);
CREATE INDEX ix_aineprofiil_keeletase ON public.aineprofiil USING btree (keeletase_kood);
--CREATE INDEX ix_aineprofiil_aine_koolitusaeg ON public.aineprofiil USING btree (aine_kood, koolitusaeg);
--CREATE INDEX ix_aineprofiil_aine_kaskkiri ON public.aineprofiil USING btree (aine_kood, kaskkiri_kpv);
CREATE INDEX ix_alatest_vastvorm ON public.alatest USING btree (vastvorm_kood);
CREATE INDEX ix_aspektihinne_nullipohj ON public.aspektihinne USING btree (nullipohj_kood);
CREATE INDEX ix_erivajadus_erivajadus ON public.erivajadus USING btree (erivajadus_kood);
CREATE INDEX ix_hindamisaspekt_aspekt ON public.hindamisaspekt USING btree (aspekt_kood);
CREATE INDEX ix_hindamiskogum_hindamine ON public.hindamiskogum USING btree (hindamine_kood);
CREATE INDEX ix_hindamiskogum_arvutus ON public.hindamiskogum USING btree (arvutus_kood);
CREATE INDEX ix_kasutaja_haridus ON public.kasutaja USING btree (haridus_kood);
CREATE INDEX ix_kasutaja_isikukood ON public.kasutaja USING btree (isikukood);
CREATE INDEX ix_kasutaja_kodakond ON public.kasutaja USING btree (kodakond_kood);
CREATE INDEX ix_kasutaja_amet ON public.kasutaja USING btree (amet_kood);
CREATE INDEX ix_kasutaja_tvaldkond ON public.kasutaja USING btree (tvaldkond_kood);
CREATE INDEX ix_kasutajaroll_testiliik ON public.kasutajaroll USING btree (testiliik_kood);
CREATE INDEX ix_kasutajaroll_aine ON public.kasutajaroll USING btree (aine_kood);
CREATE INDEX ix_kasutajaroll_oskus ON public.kasutajaroll USING btree (oskus_kood);
CREATE INDEX ix_khstatistika_nullipohj ON public.khstatistika USING btree (nullipohj_kood);
CREATE INDEX ix_kiirvalik_testiliik ON public.kiirvalik USING btree (testiliik_kood);
CREATE INDEX ix_koht_koolityyp ON public.koht USING btree (koolityyp_kood);
CREATE INDEX ix_koht_omandivorm ON public.koht USING btree (omandivorm_kood);
CREATE INDEX ix_koht_oppetase ON public.koht USING btree (oppetase_kood);
CREATE INDEX ix_koht_valitsus_tasekood ON public.koht USING btree (valitsus_tasekood);
CREATE INDEX ix_koolioppekava_kavatase ON public.koolioppekava USING btree (kavatase_kood);
CREATE INDEX ix_koolioppekava_oppekava ON public.koolioppekava USING btree (oppekava_kood);
CREATE INDEX ix_kysimus_vorming ON public.kysimus USING btree (vorming_kood);
CREATE INDEX ix_kysimusehinne_nullipohj ON public.kysimusehinne USING btree (nullipohj_kood);
CREATE INDEX ix_kysimusevastus_nullipohj ON public.kysimusevastus USING btree (nullipohj_kood);
CREATE INDEX ix_logi_isikukood ON public.logi USING btree (isikukood);
--CREATE INDEX ix_opilane_isikukood ON public.opilane USING btree (isikukood);
CREATE INDEX ix_paring_blokeering_isikukood ON public.paring_blokeering USING btree (isikukood);
CREATE INDEX ix_paring_logi_isikukood ON public.paring_logi USING btree (isikukood);
CREATE INDEX ix_paring_tunnistus_isikukood ON public.paring_tunnistus USING btree (isikukood);
CREATE INDEX ix_sisestuskogum_hindamine ON public.sisestuskogum USING btree (hindamine_kood);
CREATE INDEX ix_sooritaja_regviis ON public.sooritaja USING btree (regviis_kood);
CREATE INDEX ix_sooritaja_synnikoht ON public.sooritaja USING btree (synnikoht_kodakond_kood);
CREATE INDEX ix_sooritaja_rahvus ON public.sooritaja USING btree (rahvus_kood);
CREATE INDEX ix_sooritaja_emakeel ON public.sooritaja USING btree (ema_keel_kood);
CREATE INDEX ix_sooritaja_modified ON public.sooritaja USING btree (modified);
CREATE INDEX ix_sooritaja_keeletase ON public.sooritaja USING btree (keeletase_kood);
CREATE INDEX ix_sooritaja_kursus ON public.sooritaja USING btree (kursus_kood);
CREATE INDEX ix_sooritus_modified ON public.sooritus USING btree (modified);
CREATE INDEX ix_test_periood ON public.test USING btree (periood_kood);
CREATE INDEX ix_test_testiliik ON public.test USING btree (testiliik_kood);
CREATE INDEX ix_test_aine ON public.test USING btree (aine_kood);
CREATE INDEX ix_testiosa_lahliik ON public.testiosa USING btree (lahliik_kood);
CREATE INDEX ix_testiosa_vastvorm ON public.testiosa USING btree (vastvorm_kood);
CREATE INDEX ix_testiylesanne_valdkond ON public.testiylesanne USING btree (valdkond_kood);
CREATE INDEX ix_testiylesanne_hindamine ON public.testiylesanne USING btree (hindamine_kood);
CREATE INDEX ix_testiylesanne_aste ON public.testiylesanne USING btree (aste_kood);
CREATE INDEX ix_testiylesanne_mote ON public.testiylesanne USING btree (mote_kood);
CREATE INDEX ix_testiylesanne_teema ON public.testiylesanne USING btree (teema_kood);
CREATE INDEX ix_testiylesanne_keeletase ON public.testiylesanne USING btree (keeletase_kood);
CREATE INDEX ix_testsessioon_testiliik ON public.testsessioon USING btree (testiliik_kood);
CREATE INDEX ix_tunnistus_kool ON public.tunnistus USING btree (kool_kood);
CREATE INDEX ix_tunnistus_testiliik ON public.tunnistus USING btree (testiliik_kood);
CREATE INDEX ix_yhisfail_yhisfail ON public.yhisfail USING btree (yhisfail_kood);
CREATE INDEX ix_ylesandehinne_nullipohj ON public.ylesandehinne USING btree (nullipohj_kood);
CREATE INDEX ix_ylesandeteema_teema ON public.ylesandeteema USING btree (teema_kood);
CREATE INDEX ix_ylesandeteema_valdkond ON public.ylesandeteema USING btree (valdkond_kood);
CREATE INDEX ix_ylesanne_oskus ON public.ylesanne USING btree (oskus_kood);
CREATE INDEX ix_ylesanne_keeletase ON public.ylesanne USING btree (keeletase_kood);
CREATE INDEX ix_kooliaste_aste ON public.kooliaste USING btree (aste_kood);
CREATE INDEX ix_ylesanne_vastvorm ON public.ylesanne USING btree (vastvorm_kood);
CREATE INDEX ix_ylesanne_hindamine ON public.ylesanne USING btree (hindamine_kood);
CREATE INDEX ix_ylesanne_aine ON public.ylesanne USING btree (aine_kood);
CREATE INDEX ix_beaker_cache_accessed ON public.beaker_cache USING btree (accessed);

CREATE INDEX ix_sisuobjekt_sisuplokk_seq ON public.sisuobjekt USING btree (sisuplokk_id, seq);

CREATE UNIQUE INDEX ylesandestatistika_toimumisaeg_valitudylesanne_testikoht
ON ylesandestatistika (toimumisaeg_id, valitudylesanne_id, testikoht_id) 
WHERE testiruum_id IS NULL AND kool_koht_id IS NULL AND testikoht_id IS NOT NULL;

CREATE UNIQUE INDEX ylesandestatistika_toimumisaeg_valitudylesanne_kool
ON ylesandestatistika (toimumisaeg_id, valitudylesanne_id, kool_koht_id) 
WHERE testiruum_id IS NULL AND kool_koht_id IS NOT NULL AND testikoht_id IS NULL;

-- läbiviija unikaalsuse indeksid
CREATE UNIQUE INDEX ix_labiviija_kirj ON labiviija (toimumisaeg_id, kasutaja_id, kasutajagrupp_id, liik, lang, hindamiskogum_id, valimis) 
	WHERE on_paaris=false AND testiruum_id IS NULL AND testikoht_id IS NULL;
CREATE UNIQUE INDEX ix_labiviija_kirj2 ON labiviija (toimumisaeg_id, kasutaja_id, kasutajagrupp_id, liik, lang, hindamiskogum_id, testikoht_id, valimis) 
	WHERE on_paaris=false AND testiruum_id IS NULL;    

--CREATE UNIQUE INDEX ix_labiviija_kirj ON labiviija (toimumisaeg_id, kasutaja_id, kasutajagrupp_id, liik, lang, hindamiskogum_id) 
--	WHERE hindaja1_id IS NULL AND testikoht_id IS NULL AND testiruum_id IS NULL AND hindamiskogum_id IS NOT NULL;
--CREATE UNIQUE INDEX ix_labiviija_kirj2 ON labiviija (toimumisaeg_id, kasutaja_id, kasutajagrupp_id, liik, lang, hindamiskogum_id, hindaja1_id) 
--	WHERE hindaja1_id IS NOT NULL AND testikoht_id IS NULL AND testiruum_id IS NULL AND hindamiskogum_id IS NOT NULL;
--CREATE UNIQUE INDEX ix_labiviija_ruum ON labiviija (toimumisaeg_id, kasutaja_id, kasutajagrupp_id, liik, lang, hindamiskogum_id, testiruum_id) 
--	WHERE hindaja1_id IS NULL AND testikoht_id IS NOT NULL AND testiruum_id IS NOT NULL AND hindamiskogum_id IS NOT NULL;

-- ei ei tekiks topelt hindamise kirjeid
CREATE UNIQUE INDEX ix_hindamine_topelt ON hindamine (hindamisolek_id, liik, sisestus) 
	WHERE tyhistatud=false;
    
CREATE UNIQUE INDEX ix_ylesandevastus_ty_not_vy ON ylesandevastus (sooritus_id, testiylesanne_id)
    WHERE valitudylesanne_id IS NULL;

--ALTER TABLE ONLY public.ylesandevastus
--    ADD CONSTRAINT ylesandevastus_sooritus_id_testiylesanne_id_valitudylesanne_key UNIQUE (sooritus_id, testiylesanne_id, valitudylesanne_id) DEFERRABLE INITIALLY DEFERRED;




--CREATE UNIQUE INDEX ix_testiruum_testikoht_toimumispaev ON testiruum (testikoht_id, toimumispaev_id)
--    WHERE ruum_id IS NULL;

--CREATE UNIQUE INDEX ix_tagasisidevorm_test_id_liik ON tagasisidevorm USING btree (test_id, liik, lang) WHERE staatus=1;
CREATE UNIQUE INDEX ix_tagasisidevorm_test_id_liik_lang ON tagasisidevorm USING btree (test_id, liik, COALESCE(lang,'-')) WHERE staatus=1;

-- jagatudtööde jaoks kasutatakse tabelit test, aga suuremaid id väärtusi,
-- et testide id väärtused ei läheks kiiresti suureks
CREATE SEQUENCE test_jagatudtoo_id_seq START WITH 500000001;

CREATE UNIQUE INDEX ix_ylesanne_orig_id_lang ON t_ylesanne (orig_id, lang) WHERE ylesandeversioon_id IS NULL;
CREATE UNIQUE INDEX ix_lahendusjuhis_orig_id_lang ON t_lahendusjuhis (orig_id, lang) WHERE ylesandeversioon_id IS NULL;
CREATE UNIQUE INDEX ix_hindamisaspekt_orig_id_lang ON t_hindamisaspekt (orig_id, lang) WHERE ylesandeversioon_id IS NULL;
CREATE UNIQUE INDEX ix_punktikirjeldus_orig_id_lang ON t_punktikirjeldus (orig_id, lang) WHERE ylesandeversioon_id IS NULL;
CREATE UNIQUE INDEX ix_sisuplokk_orig_id_lang ON t_sisuplokk (orig_id, lang) WHERE ylesandeversioon_id IS NULL;
CREATE UNIQUE INDEX ix_sisuobjekt_orig_id_lang ON t_sisuobjekt (orig_id, lang) WHERE ylesandeversioon_id IS NULL;
CREATE UNIQUE INDEX ix_tulemus_orig_id_lang ON t_tulemus (orig_id, lang) WHERE ylesandeversioon_id IS NULL;
CREATE UNIQUE INDEX ix_ylesandefail_orig_id_lang ON t_ylesandefail (orig_id, lang) WHERE ylesandeversioon_id IS NULL;
CREATE UNIQUE INDEX ix_kysimus_orig_id_lang ON t_kysimus (orig_id, lang) WHERE ylesandeversioon_id IS NULL;
CREATE UNIQUE INDEX ix_kyslisa_orig_id_lang ON t_kyslisa (orig_id, lang) WHERE ylesandeversioon_id IS NULL;
CREATE UNIQUE INDEX ix_valik_orig_id_lang ON t_valik (orig_id, lang) WHERE ylesandeversioon_id IS NULL;
CREATE UNIQUE INDEX ix_hindamismaatriks_orig_id_lang ON t_hindamismaatriks (orig_id, lang) WHERE ylesandeversioon_id IS NULL;

CREATE UNIQUE INDEX ix_potext_lang_msgid ON potext USING btree (lang, msgid);
