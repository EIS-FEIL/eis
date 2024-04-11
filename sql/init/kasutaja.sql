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
-- Data for Name: kasutaja; Type: TABLE DATA; Schema: public; Owner: eisik
--

INSERT INTO public.kasutaja (created, modified, creator, modifier, id, isikukood, synnikpv, eesnimi, perenimi, nimi, parool, muuda_parool, epost, epost_seisuga, aadress_id, postiindeks, normimata, telefon, sugu, staatus, on_ametnik, on_labiviija, uiroll, koht_id, ametikoht_seisuga, ametikoht_proovitud, opilane_seisuga, isikukaart_seisuga, isikukaart_id, rr_seisuga, session_id, viimati_ekk, tunnistus_nr, tunnistus_kp, lopetanud, lopetanud_kasitsi, lopetanud_pohjus, lopetamisaasta, kool_koht_id, kool_nimi, oppekeel, kodakond_kood, synnikoht, lisatingimused, markus, bgcolor) VALUES ('2024-04-05 05:07:25.957255', '2024-04-05 05:07:26.224728', 'ADMIN', 'ADMIN', 1, 'ADMIN', NULL, 'ADMIN', 'ADMIN', 'ADMIN ADMIN', '$argon2id$v=19$m=65536,t=3,p=4$qhi3rikw6eG/grKzdz/8EQ$1/8dHfx8qYgLOyE5jMNBXmhza7NqlgqW94n0i+1F2NU', true, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 1, true, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);


--
-- Name: kasutaja_id_seq; Type: SEQUENCE SET; Schema: public; Owner: eisik
--

SELECT pg_catalog.setval('public.kasutaja_id_seq', 1, true);


--
-- PostgreSQL database dump complete
--

