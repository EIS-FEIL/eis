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
-- Data for Name: koht; Type: TABLE DATA; Schema: public; Owner: eisik
--

INSERT INTO public.koht (created, modified, creator, modifier, id, nimi, piirkond_id, haldusoigus, riik_kood, ruumidearv, ptestikohti, etestikohti, valitsus_tasekood, on_soorituskoht, on_plangikoht, staatus, kool_regnr, kool_id, koolityyp_kood, alamliik_kood, omandivorm_kood, diplomiseeria, aadress_id, postiindeks, normimata, klassi_kompl_arv, opilased_arv, ehis_seisuga, telefon, epost, varustus, seisuga) VALUES ('2024-04-05 05:07:25.950573', '2024-04-05 05:07:25.950587', 'ADMIN', 'ADMIN', 1, 'Eksamikeskus', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 1, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);


--
-- Name: koht_id_seq; Type: SEQUENCE SET; Schema: public; Owner: eisik
--

SELECT pg_catalog.setval('public.koht_id_seq', 1, true);


--
-- PostgreSQL database dump complete
--

