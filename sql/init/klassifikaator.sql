--
-- PostgreSQL database dump
--

-- Dumped from database version 16.1
-- Dumped by pg_dump version 16.2 (Ubuntu 16.2-1.pgdg22.04+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: klassifikaator; Type: TABLE DATA; Schema: public; Owner: eisik
--

INSERT INTO public.klassifikaator (created, modified, creator, modifier, kood, nimi, kehtib, ylem_kood, app, seisuga) VALUES ('2024-04-05 05:07:26.347776', '2024-04-05 05:07:26.347801', 'ADMIN', 'ADMIN', 'AINE', 'Õppeaine', true, NULL, 'eis', NULL);
INSERT INTO public.klassifikaator (created, modified, creator, modifier, kood, nimi, kehtib, ylem_kood, app, seisuga) VALUES ('2024-04-05 05:07:26.347844', '2024-04-05 05:07:26.347852', 'ADMIN', 'ADMIN', 'TUNNAINE', 'Õppeaine nimetus tunnistusel', true, NULL, 'eis', NULL);
INSERT INTO public.klassifikaator (created, modified, creator, modifier, kood, nimi, kehtib, ylem_kood, app, seisuga) VALUES ('2024-04-05 05:07:26.347882', '2024-04-05 05:07:26.347889', 'ADMIN', 'ADMIN', 'TEEMA', 'Teema', true, 'AINE', 'eis', NULL);
INSERT INTO public.klassifikaator (created, modified, creator, modifier, kood, nimi, kehtib, ylem_kood, app, seisuga) VALUES ('2024-04-05 05:07:26.347914', '2024-04-05 05:07:26.347921', 'ADMIN', 'ADMIN', 'ALATEEMA', 'Alateema', true, 'TEEMA', 'eis', NULL);
INSERT INTO public.klassifikaator (created, modified, creator, modifier, kood, nimi, kehtib, ylem_kood, app, seisuga) VALUES ('2024-04-05 05:07:26.347967', '2024-04-05 05:07:26.347975', 'ADMIN', 'ADMIN', 'OPIAINE', 'Õppeaine oppekava.edu.ee süsteemis', true, NULL, 'eis', NULL);
INSERT INTO public.klassifikaator (created, modified, creator, modifier, kood, nimi, kehtib, ylem_kood, app, seisuga) VALUES ('2024-04-05 05:07:26.348002', '2024-04-05 05:07:26.348009', 'ADMIN', 'ADMIN', 'OSKUS', 'Osaoskus', true, 'AINE', 'eis', NULL);
INSERT INTO public.klassifikaator (created, modified, creator, modifier, kood, nimi, kehtib, ylem_kood, app, seisuga) VALUES ('2024-04-05 05:07:26.348032', '2024-04-05 05:07:26.348039', 'ADMIN', 'ADMIN', 'KEELETASE', 'Keeleoskuse tase', true, 'AINE', 'eis', NULL);
INSERT INTO public.klassifikaator (created, modified, creator, modifier, kood, nimi, kehtib, ylem_kood, app, seisuga) VALUES ('2024-04-05 05:07:26.348065', '2024-04-05 05:07:26.348071', 'ADMIN', 'ADMIN', 'KURSUS', 'Kursus', true, 'AINE', 'eis', NULL);
INSERT INTO public.klassifikaator (created, modified, creator, modifier, kood, nimi, kehtib, ylem_kood, app, seisuga) VALUES ('2024-04-05 05:07:26.348094', '2024-04-05 05:07:26.348101', 'ADMIN', 'ADMIN', 'ASPEKT', 'Hindamisaspekt', true, 'AINE', 'eis', NULL);
INSERT INTO public.klassifikaator (created, modified, creator, modifier, kood, nimi, kehtib, ylem_kood, app, seisuga) VALUES ('2024-04-05 05:07:26.348124', '2024-04-05 05:07:26.348131', 'ADMIN', 'ADMIN', 'ALATEST', 'Alatesti liik', true, 'AINE', 'eis', NULL);
INSERT INTO public.klassifikaator (created, modified, creator, modifier, kood, nimi, kehtib, ylem_kood, app, seisuga) VALUES ('2024-04-05 05:07:26.348154', '2024-04-05 05:07:26.34816', 'ADMIN', 'ADMIN', 'RVEKSAM', 'Rahvusvaheliselt tunnustatud eksamid', true, NULL, 'eis', NULL);
INSERT INTO public.klassifikaator (created, modified, creator, modifier, kood, nimi, kehtib, ylem_kood, app, seisuga) VALUES ('2024-04-05 05:07:26.348183', '2024-04-05 05:07:26.348189', 'ADMIN', 'ADMIN', 'HTUNNUS', 'Hinnatav tunnus tagasisidevormil', true, 'AINE', 'eis', NULL);
INSERT INTO public.klassifikaator (created, modified, creator, modifier, kood, nimi, kehtib, ylem_kood, app, seisuga) VALUES ('2024-04-05 05:07:26.348212', '2024-04-05 05:07:26.348218', 'ADMIN', 'ADMIN', 'RASKUSASTE', 'Raskusaste', true, NULL, 'eis', NULL);
INSERT INTO public.klassifikaator (created, modified, creator, modifier, kood, nimi, kehtib, ylem_kood, app, seisuga) VALUES ('2024-04-05 05:07:26.348242', '2024-04-05 05:07:26.348249', 'ADMIN', 'ADMIN', 'OPITULEMUS', 'Õpitulemus', true, 'TEEMA', 'eis', NULL);
INSERT INTO public.klassifikaator (created, modified, creator, modifier, kood, nimi, kehtib, ylem_kood, app, seisuga) VALUES ('2024-04-05 05:07:26.348272', '2024-04-05 05:07:26.348279', 'ADMIN', 'ADMIN', 'AINEVALD', 'Ainevaldkond', true, NULL, 'eis', NULL);
INSERT INTO public.klassifikaator (created, modified, creator, modifier, kood, nimi, kehtib, ylem_kood, app, seisuga) VALUES ('2024-04-05 05:07:27.01725', '2024-04-05 05:07:27.017273', 'ADMIN', 'ADMIN', 'VAHEND', 'Ülesande lahendamiseks kasutatav abivahend', true, NULL, 'eis', NULL);
INSERT INTO public.klassifikaator (created, modified, creator, modifier, kood, nimi, kehtib, ylem_kood, app, seisuga) VALUES ('2024-04-05 05:07:27.017319', '2024-04-05 05:07:27.017327', 'ADMIN', 'ADMIN', 'MOTE', 'Mõtlemistasand', true, NULL, 'eis', NULL);
INSERT INTO public.klassifikaator (created, modified, creator, modifier, kood, nimi, kehtib, ylem_kood, app, seisuga) VALUES ('2024-04-05 05:07:27.017354', '2024-04-05 05:07:27.017361', 'ADMIN', 'ADMIN', 'ASTE', 'Kooliaste', true, NULL, 'eis', NULL);
INSERT INTO public.klassifikaator (created, modified, creator, modifier, kood, nimi, kehtib, ylem_kood, app, seisuga) VALUES ('2024-04-05 05:07:27.017387', '2024-04-05 05:07:27.017394', 'ADMIN', 'ADMIN', 'TESTILIIK', 'Testi liik', true, NULL, 'eis', NULL);
INSERT INTO public.klassifikaator (created, modified, creator, modifier, kood, nimi, kehtib, ylem_kood, app, seisuga) VALUES ('2024-04-05 05:07:27.017417', '2024-04-05 05:07:27.017423', 'ADMIN', 'ADMIN', 'KASUTLIIK', 'Ülesande kasutus', true, NULL, 'eis', NULL);
INSERT INTO public.klassifikaator (created, modified, creator, modifier, kood, nimi, kehtib, ylem_kood, app, seisuga) VALUES ('2024-04-05 05:07:27.017446', '2024-04-05 05:07:27.017452', 'ADMIN', 'ADMIN', 'PERIOOD', 'Periood', true, NULL, 'eis', NULL);
INSERT INTO public.klassifikaator (created, modified, creator, modifier, kood, nimi, kehtib, ylem_kood, app, seisuga) VALUES ('2024-04-05 05:07:27.017474', '2024-04-05 05:07:27.01748', 'ADMIN', 'ADMIN', 'SOORKEEL', 'Soorituskeel', true, NULL, 'eis', NULL);
INSERT INTO public.klassifikaator (created, modified, creator, modifier, kood, nimi, kehtib, ylem_kood, app, seisuga) VALUES ('2024-04-05 05:07:27.017503', '2024-04-05 05:07:27.017509', 'ADMIN', 'ADMIN', 'KVALITEET', 'Kvaliteedimärk', true, NULL, 'eis', NULL);
INSERT INTO public.klassifikaator (created, modified, creator, modifier, kood, nimi, kehtib, ylem_kood, app, seisuga) VALUES ('2024-04-05 05:07:27.017531', '2024-04-05 05:07:27.017537', 'ADMIN', 'ADMIN', 'OPPEKEEL', 'Õppekeel', true, NULL, 'eis', NULL);
INSERT INTO public.klassifikaator (created, modified, creator, modifier, kood, nimi, kehtib, ylem_kood, app, seisuga) VALUES ('2024-04-05 05:07:27.017561', '2024-04-05 05:07:27.017567', 'ADMIN', 'ADMIN', 'KOOLITYYP', 'Õppeasutuse tüüp', true, NULL, 'eis', NULL);
INSERT INTO public.klassifikaator (created, modified, creator, modifier, kood, nimi, kehtib, ylem_kood, app, seisuga) VALUES ('2024-04-05 05:07:27.017589', '2024-04-05 05:07:27.017596', 'ADMIN', 'ADMIN', 'ALAMLIIK', 'Õppeasutuse alamliik', true, NULL, 'eis', NULL);
INSERT INTO public.klassifikaator (created, modified, creator, modifier, kood, nimi, kehtib, ylem_kood, app, seisuga) VALUES ('2024-04-05 05:07:27.017618', '2024-04-05 05:07:27.017624', 'ADMIN', 'ADMIN', 'OPPEVORM', 'Õppevorm', true, NULL, 'eis', NULL);
INSERT INTO public.klassifikaator (created, modified, creator, modifier, kood, nimi, kehtib, ylem_kood, app, seisuga) VALUES ('2024-04-05 05:07:27.017646', '2024-04-05 05:07:27.017653', 'ADMIN', 'ADMIN', 'SUGU', 'Sugu', true, NULL, 'eis', NULL);
INSERT INTO public.klassifikaator (created, modified, creator, modifier, kood, nimi, kehtib, ylem_kood, app, seisuga) VALUES ('2024-04-05 05:07:27.017675', '2024-04-05 05:07:27.017682', 'ADMIN', 'ADMIN', 'OMANDIVORM', 'Õppeasutuse omandivorm', true, NULL, 'eis', NULL);
INSERT INTO public.klassifikaator (created, modified, creator, modifier, kood, nimi, kehtib, ylem_kood, app, seisuga) VALUES ('2024-04-05 05:07:27.017705', '2024-04-05 05:07:27.017711', 'ADMIN', 'ADMIN', 'TUNNUS1', 'Statistiline tunnus 1', true, NULL, 'eis', NULL);
INSERT INTO public.klassifikaator (created, modified, creator, modifier, kood, nimi, kehtib, ylem_kood, app, seisuga) VALUES ('2024-04-05 05:07:27.017734', '2024-04-05 05:07:27.01774', 'ADMIN', 'ADMIN', 'TUNNUS2', 'Statistiline tunnus 2', true, NULL, 'eis', NULL);
INSERT INTO public.klassifikaator (created, modified, creator, modifier, kood, nimi, kehtib, ylem_kood, app, seisuga) VALUES ('2024-04-05 05:07:27.017762', '2024-04-05 05:07:27.017769', 'ADMIN', 'ADMIN', 'TUNNUS3', 'Statistiline tunnus 3', true, NULL, 'eis', NULL);
INSERT INTO public.klassifikaator (created, modified, creator, modifier, kood, nimi, kehtib, ylem_kood, app, seisuga) VALUES ('2024-04-05 05:07:27.017791', '2024-04-05 05:07:27.017797', 'ADMIN', 'ADMIN', 'VASTVORM', 'Vastamise vorm', true, NULL, 'eis', NULL);
INSERT INTO public.klassifikaator (created, modified, creator, modifier, kood, nimi, kehtib, ylem_kood, app, seisuga) VALUES ('2024-04-05 05:07:27.01782', '2024-04-05 05:07:27.017826', 'ADMIN', 'ADMIN', 'HINDAMINE', 'Hindamise meetod', true, NULL, 'eis', NULL);
INSERT INTO public.klassifikaator (created, modified, creator, modifier, kood, nimi, kehtib, ylem_kood, app, seisuga) VALUES ('2024-04-05 05:07:27.01785', '2024-04-05 05:07:27.017856', 'ADMIN', 'ADMIN', 'ARVUTUS', 'Kahe hindaja hinnangutest lõpliku hindepallide arvu arvutamise meetod', true, NULL, 'eis', NULL);
INSERT INTO public.klassifikaator (created, modified, creator, modifier, kood, nimi, kehtib, ylem_kood, app, seisuga) VALUES ('2024-04-05 05:07:27.017878', '2024-04-05 05:07:27.017884', 'ADMIN', 'ADMIN', 'NULLIPOHJ', 'Nulli põhjus', true, NULL, 'eis', NULL);
INSERT INTO public.klassifikaator (created, modified, creator, modifier, kood, nimi, kehtib, ylem_kood, app, seisuga) VALUES ('2024-04-05 05:07:27.017906', '2024-04-05 05:07:27.017913', 'ADMIN', 'ADMIN', 'HINDPROB', 'Hindamisprobleem', true, NULL, 'eis', NULL);
INSERT INTO public.klassifikaator (created, modified, creator, modifier, kood, nimi, kehtib, ylem_kood, app, seisuga) VALUES ('2024-04-05 05:07:27.017935', '2024-04-05 05:07:27.017941', 'ADMIN', 'ADMIN', 'Y_STAATUS', 'Ülesande olek', true, NULL, 'eis', NULL);
INSERT INTO public.klassifikaator (created, modified, creator, modifier, kood, nimi, kehtib, ylem_kood, app, seisuga) VALUES ('2024-04-05 05:07:27.017963', '2024-04-05 05:07:27.01797', 'ADMIN', 'ADMIN', 'T_STAATUS', 'Testi olek', true, NULL, 'eis', NULL);
INSERT INTO public.klassifikaator (created, modified, creator, modifier, kood, nimi, kehtib, ylem_kood, app, seisuga) VALUES ('2024-04-05 05:07:27.017992', '2024-04-05 05:07:27.017999', 'ADMIN', 'ADMIN', 'K_STAATUS', 'Komplekti olek', true, NULL, 'eis', NULL);
INSERT INTO public.klassifikaator (created, modified, creator, modifier, kood, nimi, kehtib, ylem_kood, app, seisuga) VALUES ('2024-04-05 05:07:27.018022', '2024-04-05 05:07:27.018029', 'ADMIN', 'ADMIN', 'S_STAATUS', 'Testisooritamise olek', true, NULL, 'eis', NULL);
INSERT INTO public.klassifikaator (created, modified, creator, modifier, kood, nimi, kehtib, ylem_kood, app, seisuga) VALUES ('2024-04-05 05:07:27.018051', '2024-04-05 05:07:27.018057', 'ADMIN', 'ADMIN', 'ERIVAJADUS', 'Erivajadused (vanad)', true, NULL, 'eis', NULL);
INSERT INTO public.klassifikaator (created, modified, creator, modifier, kood, nimi, kehtib, ylem_kood, app, seisuga) VALUES ('2024-04-05 05:07:27.018082', '2024-04-05 05:07:27.018088', 'ADMIN', 'ADMIN', 'REGVIIS', 'Testile registreerimise viis', true, NULL, 'eis', NULL);
INSERT INTO public.klassifikaator (created, modified, creator, modifier, kood, nimi, kehtib, ylem_kood, app, seisuga) VALUES ('2024-04-05 05:07:27.018111', '2024-04-05 05:07:27.018117', 'ADMIN', 'ADMIN', 'LANG', 'Keel', true, NULL, 'eis', NULL);
INSERT INTO public.klassifikaator (created, modified, creator, modifier, kood, nimi, kehtib, ylem_kood, app, seisuga) VALUES ('2024-04-05 05:07:27.018139', '2024-04-05 05:07:27.018145', 'ADMIN', 'ADMIN', 'AMETIKOHT', 'Ametikoht', true, NULL, 'eis', NULL);
INSERT INTO public.klassifikaator (created, modified, creator, modifier, kood, nimi, kehtib, ylem_kood, app, seisuga) VALUES ('2024-04-05 05:07:27.018167', '2024-04-05 05:07:27.018174', 'ADMIN', 'ADMIN', 'YHISFAIL', 'Ühise faili tüüp', true, NULL, 'eis', NULL);
INSERT INTO public.klassifikaator (created, modified, creator, modifier, kood, nimi, kehtib, ylem_kood, app, seisuga) VALUES ('2024-04-05 05:07:27.018196', '2024-04-05 05:07:27.018202', 'ADMIN', 'ADMIN', 'MAHAKANDP', 'Plangi mahakandmise põhjus', true, NULL, 'eis', NULL);
INSERT INTO public.klassifikaator (created, modified, creator, modifier, kood, nimi, kehtib, ylem_kood, app, seisuga) VALUES ('2024-04-05 05:07:27.018225', '2024-04-05 05:07:27.018231', 'ADMIN', 'ADMIN', 'OPPETASE', 'Õppetase', true, NULL, 'eis', NULL);
INSERT INTO public.klassifikaator (created, modified, creator, modifier, kood, nimi, kehtib, ylem_kood, app, seisuga) VALUES ('2024-04-05 05:07:27.018254', '2024-04-05 05:07:27.018261', 'ADMIN', 'ADMIN', 'KAVATASE', 'Õppekavajärgne haridustase', true, 'OPPETASE', 'eis', NULL);
INSERT INTO public.klassifikaator (created, modified, creator, modifier, kood, nimi, kehtib, ylem_kood, app, seisuga) VALUES ('2024-04-05 05:07:27.018283', '2024-04-05 05:07:27.018289', 'ADMIN', 'ADMIN', 'EHIS_AINE', 'EHISe õppeaine', true, NULL, 'eis', NULL);
INSERT INTO public.klassifikaator (created, modified, creator, modifier, kood, nimi, kehtib, ylem_kood, app, seisuga) VALUES ('2024-04-05 05:07:27.018312', '2024-04-05 05:07:27.018318', 'ADMIN', 'ADMIN', 'EHIS_ASTE', 'EHISe kooliaste', true, NULL, 'eis', NULL);
INSERT INTO public.klassifikaator (created, modified, creator, modifier, kood, nimi, kehtib, ylem_kood, app, seisuga) VALUES ('2024-04-05 05:07:27.018341', '2024-04-05 05:07:27.018347', 'ADMIN', 'ADMIN', 'SPTYYP', 'Ülesandetüüp', true, NULL, 'eis', NULL);
INSERT INTO public.klassifikaator (created, modified, creator, modifier, kood, nimi, kehtib, ylem_kood, app, seisuga) VALUES ('2024-04-05 05:07:27.01837', '2024-04-05 05:07:27.018377', 'ADMIN', 'ADMIN', 'TOOKASK', 'Tehniline töökäsk', true, 'SPTYYP', 'eis', NULL);
INSERT INTO public.klassifikaator (created, modified, creator, modifier, kood, nimi, kehtib, ylem_kood, app, seisuga) VALUES ('2024-04-05 05:07:27.018398', '2024-04-05 05:07:27.018405', 'ADMIN', 'ADMIN', 'KODAKOND', 'Kodakondsus', true, NULL, 'eis', NULL);
INSERT INTO public.klassifikaator (created, modified, creator, modifier, kood, nimi, kehtib, ylem_kood, app, seisuga) VALUES ('2024-04-05 05:07:27.018429', '2024-04-05 05:07:27.018436', 'ADMIN', 'ADMIN', 'TVALDKOND', 'Töövaldkond', true, NULL, 'eis', NULL);
INSERT INTO public.klassifikaator (created, modified, creator, modifier, kood, nimi, kehtib, ylem_kood, app, seisuga) VALUES ('2024-04-05 05:07:27.018458', '2024-04-05 05:07:27.018464', 'ADMIN', 'ADMIN', 'AMET', 'Amet', true, NULL, 'eis', NULL);
INSERT INTO public.klassifikaator (created, modified, creator, modifier, kood, nimi, kehtib, ylem_kood, app, seisuga) VALUES ('2024-04-05 05:07:27.018487', '2024-04-05 05:07:27.018493', 'ADMIN', 'ADMIN', 'HARIDUS', 'Haridus', true, NULL, 'eis', NULL);
INSERT INTO public.klassifikaator (created, modified, creator, modifier, kood, nimi, kehtib, ylem_kood, app, seisuga) VALUES ('2024-04-05 05:07:27.018515', '2024-04-05 05:07:27.018521', 'ADMIN', 'ADMIN', 'OPPEKOHT', 'Keele õppimise koht', true, NULL, 'eis', NULL);
INSERT INTO public.klassifikaator (created, modified, creator, modifier, kood, nimi, kehtib, ylem_kood, app, seisuga) VALUES ('2024-04-05 05:07:27.018543', '2024-04-05 05:07:27.018549', 'ADMIN', 'ADMIN', 'OPPEKOHTET', 'Eesti keele õppimise koht', true, NULL, 'eis', NULL);
INSERT INTO public.klassifikaator (created, modified, creator, modifier, kood, nimi, kehtib, ylem_kood, app, seisuga) VALUES ('2024-04-05 05:07:27.018571', '2024-04-05 05:07:27.018578', 'ADMIN', 'ADMIN', 'TESTIKLASS', 'Testi klass', true, NULL, 'eis', NULL);
INSERT INTO public.klassifikaator (created, modified, creator, modifier, kood, nimi, kehtib, ylem_kood, app, seisuga) VALUES ('2024-04-05 05:07:27.018599', '2024-04-05 05:07:27.018605', 'ADMIN', 'ADMIN', 'RAHVUS', 'Rahvus', true, NULL, 'eis', NULL);
INSERT INTO public.klassifikaator (created, modified, creator, modifier, kood, nimi, kehtib, ylem_kood, app, seisuga) VALUES ('2024-04-05 05:07:27.018627', '2024-04-05 05:07:27.018633', 'ADMIN', 'ADMIN', 'KEEL', 'Keel', true, NULL, 'eis', NULL);
INSERT INTO public.klassifikaator (created, modified, creator, modifier, kood, nimi, kehtib, ylem_kood, app, seisuga) VALUES ('2024-04-05 05:07:27.018655', '2024-04-05 05:07:27.018662', 'ADMIN', 'ADMIN', 'RIIK', 'Riik', true, NULL, 'eis', NULL);


--
-- PostgreSQL database dump complete
--

