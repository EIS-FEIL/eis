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
-- Data for Name: kasutajaroll; Type: TABLE DATA; Schema: public; Owner: eisik
--

INSERT INTO public.kasutajaroll (created, modified, creator, modifier, id, kasutaja_id, kasutajagrupp_id, koht_id, piirkond_id, aine_kood, oskus_kood, testiliik_kood, kehtib_alates, kehtib_kuni, rolliplokk, lang, allkiri_jrk, allkiri_tiitel1, allkiri_tiitel2) VALUES ('2024-04-05 05:07:25.975569', '2024-04-05 05:07:25.975589', 'ADMIN', 'ADMIN', 1, 1, 1, 1, NULL, NULL, NULL, NULL, '2000-01-01', '3000-01-01', NULL, NULL, NULL, NULL, NULL);
INSERT INTO public.kasutajaroll (created, modified, creator, modifier, id, kasutaja_id, kasutajagrupp_id, koht_id, piirkond_id, aine_kood, oskus_kood, testiliik_kood, kehtib_alates, kehtib_kuni, rolliplokk, lang, allkiri_jrk, allkiri_tiitel1, allkiri_tiitel2) VALUES ('2024-04-05 05:07:26.234997', '2024-04-05 05:07:26.235022', 'ADMIN', 'ADMIN', 2, 1, 41, 1, NULL, NULL, NULL, NULL, '2000-01-01', '3000-01-01', NULL, NULL, NULL, NULL, NULL);


--
-- Name: kasutajaroll_id_seq; Type: SEQUENCE SET; Schema: public; Owner: eisik
--

SELECT pg_catalog.setval('public.kasutajaroll_id_seq', 2, true);


--
-- PostgreSQL database dump complete
--

