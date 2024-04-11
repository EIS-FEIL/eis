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
-- Data for Name: asukohamaarus; Type: TABLE DATA; Schema: public; Owner: eisik
--

INSERT INTO public.asukohamaarus (created, modified, creator, modifier, id, seq, nimetav, kohamaarus) VALUES ('2024-04-05 05:07:25.964528', '2024-04-05 05:07:25.964545', 'ADMIN', 'ADMIN', 1, 1, 'Tallinn', 'Tallinnas');
INSERT INTO public.asukohamaarus (created, modified, creator, modifier, id, seq, nimetav, kohamaarus) VALUES ('2024-04-05 05:07:25.967365', '2024-04-05 05:07:25.967379', 'ADMIN', 'ADMIN', 2, 1, 'maa', 'maal');
INSERT INTO public.asukohamaarus (created, modified, creator, modifier, id, seq, nimetav, kohamaarus) VALUES ('2024-04-05 05:07:25.968444', '2024-04-05 05:07:25.968454', 'ADMIN', 'ADMIN', 3, 1, 'mäe', 'mäel');
INSERT INTO public.asukohamaarus (created, modified, creator, modifier, id, seq, nimetav, kohamaarus) VALUES ('2024-04-05 05:07:25.969332', '2024-04-05 05:07:25.969341', 'ADMIN', 'ADMIN', 4, 1, 'järve', 'järvel');
INSERT INTO public.asukohamaarus (created, modified, creator, modifier, id, seq, nimetav, kohamaarus) VALUES ('2024-04-05 05:07:25.970187', '2024-04-05 05:07:25.970196', 'ADMIN', 'ADMIN', 5, 1, 'Tapa', 'Tapal');
INSERT INTO public.asukohamaarus (created, modified, creator, modifier, id, seq, nimetav, kohamaarus) VALUES ('2024-04-05 05:07:25.971018', '2024-04-05 05:07:25.971028', 'ADMIN', 'ADMIN', 6, 1, 'Loksa', 'Loksal');
INSERT INTO public.asukohamaarus (created, modified, creator, modifier, id, seq, nimetav, kohamaarus) VALUES ('2024-04-05 05:07:25.971849', '2024-04-05 05:07:25.971859', 'ADMIN', 'ADMIN', 7, 1, 'Kose', 'Kosel');


--
-- Name: asukohamaarus_id_seq; Type: SEQUENCE SET; Schema: public; Owner: eisik
--

SELECT pg_catalog.setval('public.asukohamaarus_id_seq', 7, true);


--
-- PostgreSQL database dump complete
--

