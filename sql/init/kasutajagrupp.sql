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
-- Data for Name: kasutajagrupp; Type: TABLE DATA; Schema: public; Owner: eisik
--

INSERT INTO public.kasutajagrupp (created, modified, creator, modifier, id, nimi, kirjeldus, tyyp, staatus, max_koormus) VALUES ('2024-04-05 05:07:24.102532', '2024-04-05 05:07:24.102558', 'ADMIN', 'ADMIN', 1, 'Superuser', NULL, 1, 1, NULL);
INSERT INTO public.kasutajagrupp (created, modified, creator, modifier, id, nimi, kirjeldus, tyyp, staatus, max_koormus) VALUES ('2024-04-05 05:07:24.762323', '2024-04-05 05:07:24.762339', 'ADMIN', 'ADMIN', 74, 'Süsteemiadministraator', NULL, 1, 1, NULL);
INSERT INTO public.kasutajagrupp (created, modified, creator, modifier, id, nimi, kirjeldus, tyyp, staatus, max_koormus) VALUES ('2024-04-05 05:07:24.769433', '2024-04-05 05:07:24.769447', 'ADMIN', 'ADMIN', 2, 'Subject specialist', NULL, 1, 1, NULL);
INSERT INTO public.kasutajagrupp (created, modified, creator, modifier, id, nimi, kirjeldus, tyyp, staatus, max_koormus) VALUES ('2024-04-05 05:07:24.881921', '2024-04-05 05:07:24.881935', 'ADMIN', 'ADMIN', 39, 'Member of the subject working group', NULL, 1, 1, NULL);
INSERT INTO public.kasutajagrupp (created, modified, creator, modifier, id, nimi, kirjeldus, tyyp, staatus, max_koormus) VALUES ('2024-04-05 05:07:24.89847', '2024-04-05 05:07:24.898484', 'ADMIN', 'ADMIN', 3, 'Skills specialist', NULL, 1, 1, NULL);
INSERT INTO public.kasutajagrupp (created, modified, creator, modifier, id, nimi, kirjeldus, tyyp, staatus, max_koormus) VALUES ('2024-04-05 05:07:24.912464', '2024-04-05 05:07:24.912477', 'ADMIN', 'ADMIN', 69, 'Vastuste väljavõtte allalaadija', NULL, 1, 1, NULL);
INSERT INTO public.kasutajagrupp (created, modified, creator, modifier, id, nimi, kirjeldus, tyyp, staatus, max_koormus) VALUES ('2024-04-05 05:07:24.919697', '2024-04-05 05:07:24.919711', 'ADMIN', 'ADMIN', 5, 'Item writer', NULL, 2, 1, NULL);
INSERT INTO public.kasutajagrupp (created, modified, creator, modifier, id, nimi, kirjeldus, tyyp, staatus, max_koormus) VALUES ('2024-04-05 05:07:24.92848', '2024-04-05 05:07:24.928494', 'ADMIN', 'ADMIN', 6, 'Task watcher', NULL, 2, 1, NULL);
INSERT INTO public.kasutajagrupp (created, modified, creator, modifier, id, nimi, kirjeldus, tyyp, staatus, max_koormus) VALUES ('2024-04-05 05:07:24.937899', '2024-04-05 05:07:24.937912', 'ADMIN', 'ADMIN', 7, 'Task editor', NULL, 2, 1, NULL);
INSERT INTO public.kasutajagrupp (created, modified, creator, modifier, id, nimi, kirjeldus, tyyp, staatus, max_koormus) VALUES ('2024-04-05 05:07:24.956857', '2024-04-05 05:07:24.956871', 'ADMIN', 'ADMIN', 8, 'Task translator', NULL, 2, 1, NULL);
INSERT INTO public.kasutajagrupp (created, modified, creator, modifier, id, nimi, kirjeldus, tyyp, staatus, max_koormus) VALUES ('2024-04-05 05:07:24.971429', '2024-04-05 05:07:24.971442', 'ADMIN', 'ADMIN', 9, 'Task designer', NULL, 2, 1, NULL);
INSERT INTO public.kasutajagrupp (created, modified, creator, modifier, id, nimi, kirjeldus, tyyp, staatus, max_koormus) VALUES ('2024-04-05 05:07:24.983797', '2024-04-05 05:07:24.983811', 'ADMIN', 'ADMIN', 10, 'Test compiler', NULL, 3, 1, NULL);
INSERT INTO public.kasutajagrupp (created, modified, creator, modifier, id, nimi, kirjeldus, tyyp, staatus, max_koormus) VALUES ('2024-04-05 05:07:25.00374', '2024-04-05 05:07:25.003754', 'ADMIN', 'ADMIN', 11, 'Test watcher', NULL, 3, 1, NULL);
INSERT INTO public.kasutajagrupp (created, modified, creator, modifier, id, nimi, kirjeldus, tyyp, staatus, max_koormus) VALUES ('2024-04-05 05:07:25.017824', '2024-04-05 05:07:25.017875', 'ADMIN', 'ADMIN', 12, 'Test editor', NULL, 3, 1, NULL);
INSERT INTO public.kasutajagrupp (created, modified, creator, modifier, id, nimi, kirjeldus, tyyp, staatus, max_koormus) VALUES ('2024-04-05 05:07:25.03663', '2024-04-05 05:07:25.036643', 'ADMIN', 'ADMIN', 13, 'Test translator', NULL, 3, 1, NULL);
INSERT INTO public.kasutajagrupp (created, modified, creator, modifier, id, nimi, kirjeldus, tyyp, staatus, max_koormus) VALUES ('2024-04-05 05:07:25.054618', '2024-04-05 05:07:25.054631', 'ADMIN', 'ADMIN', 14, 'Test designer', NULL, 3, 1, NULL);
INSERT INTO public.kasutajagrupp (created, modified, creator, modifier, id, nimi, kirjeldus, tyyp, staatus, max_koormus) VALUES ('2024-04-05 05:07:25.071918', '2024-04-05 05:07:25.071931', 'ADMIN', 'ADMIN', 15, 'Test owner', NULL, 3, 1, NULL);
INSERT INTO public.kasutajagrupp (created, modified, creator, modifier, id, nimi, kirjeldus, tyyp, staatus, max_koormus) VALUES ('2024-04-05 05:07:25.090523', '2024-04-05 05:07:25.090539', 'ADMIN', 'ADMIN', 63, 'Work watcher', NULL, 4, 1, NULL);
INSERT INTO public.kasutajagrupp (created, modified, creator, modifier, id, nimi, kirjeldus, tyyp, staatus, max_koormus) VALUES ('2024-04-05 05:07:25.096644', '2024-04-05 05:07:25.096657', 'ADMIN', 'ADMIN', 33, 'Test organiser', NULL, 3, 1, NULL);
INSERT INTO public.kasutajagrupp (created, modified, creator, modifier, id, nimi, kirjeldus, tyyp, staatus, max_koormus) VALUES ('2024-04-05 05:07:25.10867', '2024-04-05 05:07:25.108686', 'ADMIN', 'ADMIN', 16, 'Official organising the exam', NULL, 1, 1, NULL);
INSERT INTO public.kasutajagrupp (created, modified, creator, modifier, id, nimi, kirjeldus, tyyp, staatus, max_koormus) VALUES ('2024-04-05 05:07:25.308575', '2024-04-05 05:07:25.308592', 'ADMIN', 'ADMIN', 17, 'Regional organiser', NULL, 1, 1, NULL);
INSERT INTO public.kasutajagrupp (created, modified, creator, modifier, id, nimi, kirjeldus, tyyp, staatus, max_koormus) VALUES ('2024-04-05 05:07:25.351046', '2024-04-05 05:07:25.351062', 'ADMIN', 'ADMIN', 65, 'Eksamikorraldaja', NULL, 1, 1, NULL);
INSERT INTO public.kasutajagrupp (created, modified, creator, modifier, id, nimi, kirjeldus, tyyp, staatus, max_koormus) VALUES ('2024-04-05 05:07:25.366053', '2024-04-05 05:07:25.366065', 'ADMIN', 'ADMIN', 18, 'Registrator', NULL, 1, 1, NULL);
INSERT INTO public.kasutajagrupp (created, modified, creator, modifier, id, nimi, kirjeldus, tyyp, staatus, max_koormus) VALUES ('2024-04-05 05:07:25.376111', '2024-04-05 05:07:25.376127', 'ADMIN', 'ADMIN', 19, 'Lead marker', NULL, 1, 1, NULL);
INSERT INTO public.kasutajagrupp (created, modified, creator, modifier, id, nimi, kirjeldus, tyyp, staatus, max_koormus) VALUES ('2024-04-05 05:07:25.393843', '2024-04-05 05:07:25.393855', 'ADMIN', 'ADMIN', 73, 'Testi hindamisjuht', NULL, 3, 1, NULL);
INSERT INTO public.kasutajagrupp (created, modified, creator, modifier, id, nimi, kirjeldus, tyyp, staatus, max_koormus) VALUES ('2024-04-05 05:07:25.412448', '2024-04-05 05:07:25.41246', 'ADMIN', 'ADMIN', 20, 'Marking expert', NULL, 1, 1, NULL);
INSERT INTO public.kasutajagrupp (created, modified, creator, modifier, id, nimi, kirjeldus, tyyp, staatus, max_koormus) VALUES ('2024-04-05 05:07:25.430984', '2024-04-05 05:07:25.430996', 'ADMIN', 'ADMIN', 21, 'Enterer', NULL, 1, 1, NULL);
INSERT INTO public.kasutajagrupp (created, modified, creator, modifier, id, nimi, kirjeldus, tyyp, staatus, max_koormus) VALUES ('2024-04-05 05:07:25.437167', '2024-04-05 05:07:25.43718', 'ADMIN', 'ADMIN', 22, 'Corrector of entries', NULL, 1, 1, NULL);
INSERT INTO public.kasutajagrupp (created, modified, creator, modifier, id, nimi, kirjeldus, tyyp, staatus, max_koormus) VALUES ('2024-04-05 05:07:25.447289', '2024-04-05 05:07:25.447306', 'ADMIN', 'ADMIN', 23, 'Member of Appeal Committee', NULL, 1, 1, NULL);
INSERT INTO public.kasutajagrupp (created, modified, creator, modifier, id, nimi, kirjeldus, tyyp, staatus, max_koormus) VALUES ('2024-04-05 05:07:25.453268', '2024-04-05 05:07:25.453281', 'ADMIN', 'ADMIN', 48, 'Vaidekomisjoni sekretär', NULL, 1, 1, NULL);
INSERT INTO public.kasutajagrupp (created, modified, creator, modifier, id, nimi, kirjeldus, tyyp, staatus, max_koormus) VALUES ('2024-04-05 05:07:25.459206', '2024-04-05 05:07:25.459227', 'ADMIN', 'ADMIN', 45, 'Chairman of Appeal Committee', NULL, 1, 1, NULL);
INSERT INTO public.kasutajagrupp (created, modified, creator, modifier, id, nimi, kirjeldus, tyyp, staatus, max_koormus) VALUES ('2024-04-05 05:07:25.465809', '2024-04-05 05:07:25.465823', 'ADMIN', 'ADMIN', 24, 'Special conditions specialist', NULL, 1, 1, NULL);
INSERT INTO public.kasutajagrupp (created, modified, creator, modifier, id, nimi, kirjeldus, tyyp, staatus, max_koormus) VALUES ('2024-04-05 05:07:25.475285', '2024-04-05 05:07:25.475304', 'ADMIN', 'ADMIN', 41, 'Eksamikeskuse töötaja', NULL, 1, 1, NULL);
INSERT INTO public.kasutajagrupp (created, modified, creator, modifier, id, nimi, kirjeldus, tyyp, staatus, max_koormus) VALUES ('2024-04-05 05:07:25.487855', '2024-04-05 05:07:25.487868', 'ADMIN', 'ADMIN', 62, 'Files uploader', NULL, 1, 1, NULL);
INSERT INTO public.kasutajagrupp (created, modified, creator, modifier, id, nimi, kirjeldus, tyyp, staatus, max_koormus) VALUES ('2024-04-05 05:07:25.493876', '2024-04-05 05:07:25.49389', 'ADMIN', 'ADMIN', 72, 'Oma testi korraldaja', NULL, 5, 1, NULL);
INSERT INTO public.kasutajagrupp (created, modified, creator, modifier, id, nimi, kirjeldus, tyyp, staatus, max_koormus) VALUES ('2024-04-05 05:07:25.529108', '2024-04-05 05:07:25.529124', 'ADMIN', 'ADMIN', 25, 'Pedagogue', NULL, 4, 1, NULL);
INSERT INTO public.kasutajagrupp (created, modified, creator, modifier, id, nimi, kirjeldus, tyyp, staatus, max_koormus) VALUES ('2024-04-05 05:07:25.554919', '2024-04-05 05:07:25.554937', 'ADMIN', 'ADMIN', 26, 'Test Location Administrator', NULL, 4, 1, NULL);
INSERT INTO public.kasutajagrupp (created, modified, creator, modifier, id, nimi, kirjeldus, tyyp, staatus, max_koormus) VALUES ('2024-04-05 05:07:25.60273', '2024-04-05 05:07:25.602743', 'ADMIN', 'ADMIN', 56, 'Headmaster', NULL, 4, 1, NULL);
INSERT INTO public.kasutajagrupp (created, modified, creator, modifier, id, nimi, kirjeldus, tyyp, staatus, max_koormus) VALUES ('2024-04-05 05:07:25.653507', '2024-04-05 05:07:25.653524', 'ADMIN', 'ADMIN', 55, 'Blank Manager', NULL, 4, 1, NULL);
INSERT INTO public.kasutajagrupp (created, modified, creator, modifier, id, nimi, kirjeldus, tyyp, staatus, max_koormus) VALUES ('2024-04-05 05:07:25.659734', '2024-04-05 05:07:25.659747', 'ADMIN', 'ADMIN', 57, 'Protocol Enterer', NULL, 4, 1, NULL);
INSERT INTO public.kasutajagrupp (created, modified, creator, modifier, id, nimi, kirjeldus, tyyp, staatus, max_koormus) VALUES ('2024-04-05 05:07:25.668676', '2024-04-05 05:07:25.668689', 'ADMIN', 'ADMIN', 58, 'Files downloader', NULL, 4, 1, NULL);
INSERT INTO public.kasutajagrupp (created, modified, creator, modifier, id, nimi, kirjeldus, tyyp, staatus, max_koormus) VALUES ('2024-04-05 05:07:25.674845', '2024-04-05 05:07:25.67487', 'ADMIN', 'ADMIN', 52, 'Student', NULL, 4, 1, NULL);
INSERT INTO public.kasutajagrupp (created, modified, creator, modifier, id, nimi, kirjeldus, tyyp, staatus, max_koormus) VALUES ('2024-04-05 05:07:25.67656', '2024-04-05 05:07:25.676582', 'ADMIN', 'ADMIN', 51, 'Previously graduated', NULL, 4, 1, NULL);
INSERT INTO public.kasutajagrupp (created, modified, creator, modifier, id, nimi, kirjeldus, tyyp, staatus, max_koormus) VALUES ('2024-04-05 05:07:25.678157', '2024-04-05 05:07:25.678171', 'ADMIN', 'ADMIN', 27, 'Test administrator', NULL, 4, 1, NULL);
INSERT INTO public.kasutajagrupp (created, modified, creator, modifier, id, nimi, kirjeldus, tyyp, staatus, max_koormus) VALUES ('2024-04-05 05:07:25.691731', '2024-04-05 05:07:25.691743', 'ADMIN', 'ADMIN', 28, 'Observer', NULL, 4, 1, NULL);
INSERT INTO public.kasutajagrupp (created, modified, creator, modifier, id, nimi, kirjeldus, tyyp, staatus, max_koormus) VALUES ('2024-04-05 05:07:25.703866', '2024-04-05 05:07:25.703879', 'ADMIN', 'ADMIN', 29, 'Marker (oral tests)', NULL, 4, 1, NULL);
INSERT INTO public.kasutajagrupp (created, modified, creator, modifier, id, nimi, kirjeldus, tyyp, staatus, max_koormus) VALUES ('2024-04-05 05:07:25.719589', '2024-04-05 05:07:25.719608', 'ADMIN', 'ADMIN', 30, 'Marker (written tests)', NULL, 4, 1, NULL);
INSERT INTO public.kasutajagrupp (created, modified, creator, modifier, id, nimi, kirjeldus, tyyp, staatus, max_koormus) VALUES ('2024-04-05 05:07:25.731621', '2024-04-05 05:07:25.731633', 'ADMIN', 'ADMIN', 35, '2. hindaja (suuline)', NULL, 4, 1, NULL);
INSERT INTO public.kasutajagrupp (created, modified, creator, modifier, id, nimi, kirjeldus, tyyp, staatus, max_koormus) VALUES ('2024-04-05 05:07:25.74738', '2024-04-05 05:07:25.747396', 'ADMIN', 'ADMIN', 36, 'Interviewer', NULL, 4, 1, NULL);
INSERT INTO public.kasutajagrupp (created, modified, creator, modifier, id, nimi, kirjeldus, tyyp, staatus, max_koormus) VALUES ('2024-04-05 05:07:25.761654', '2024-04-05 05:07:25.761665', 'ADMIN', 'ADMIN', 53, 'Marker-interviewer', NULL, 4, 1, NULL);
INSERT INTO public.kasutajagrupp (created, modified, creator, modifier, id, nimi, kirjeldus, tyyp, staatus, max_koormus) VALUES ('2024-04-05 05:07:25.762854', '2024-04-05 05:07:25.762866', 'ADMIN', 'ADMIN', 38, 'Examination Commission Member', NULL, 4, 1, NULL);
INSERT INTO public.kasutajagrupp (created, modified, creator, modifier, id, nimi, kirjeldus, tyyp, staatus, max_koormus) VALUES ('2024-04-05 05:07:25.772411', '2024-04-05 05:07:25.772424', 'ADMIN', 'ADMIN', 46, 'Examination Commission Chairman', NULL, 4, 1, NULL);
INSERT INTO public.kasutajagrupp (created, modified, creator, modifier, id, nimi, kirjeldus, tyyp, staatus, max_koormus) VALUES ('2024-04-05 05:07:25.782108', '2024-04-05 05:07:25.78212', 'ADMIN', 'ADMIN', 47, 'Consultant', NULL, 4, 1, NULL);
INSERT INTO public.kasutajagrupp (created, modified, creator, modifier, id, nimi, kirjeldus, tyyp, staatus, max_koormus) VALUES ('2024-04-05 05:07:25.79096', '2024-04-05 05:07:25.790979', 'ADMIN', 'ADMIN', 40, 'Tests conductor', NULL, 4, 1, NULL);
INSERT INTO public.kasutajagrupp (created, modified, creator, modifier, id, nimi, kirjeldus, tyyp, staatus, max_koormus) VALUES ('2024-04-05 05:07:25.811296', '2024-04-05 05:07:25.81131', 'ADMIN', 'ADMIN', 54, 'School Psychologist', NULL, 1, 1, NULL);
INSERT INTO public.kasutajagrupp (created, modified, creator, modifier, id, nimi, kirjeldus, tyyp, staatus, max_koormus) VALUES ('2024-04-05 05:07:25.828842', '2024-04-05 05:07:25.828855', 'ADMIN', 'ADMIN', 61, 'School Psychologist Licence Administrator', NULL, 1, 1, NULL);
INSERT INTO public.kasutajagrupp (created, modified, creator, modifier, id, nimi, kirjeldus, tyyp, staatus, max_koormus) VALUES ('2024-04-05 05:07:25.835643', '2024-04-05 05:07:25.835664', 'ADMIN', 'ADMIN', 67, 'Logopeed', NULL, 1, 1, NULL);
INSERT INTO public.kasutajagrupp (created, modified, creator, modifier, id, nimi, kirjeldus, tyyp, staatus, max_koormus) VALUES ('2024-04-05 05:07:25.854526', '2024-04-05 05:07:25.854541', 'ADMIN', 'ADMIN', 68, 'Logopeedide litsentside haldaja', NULL, 1, 1, NULL);
INSERT INTO public.kasutajagrupp (created, modified, creator, modifier, id, nimi, kirjeldus, tyyp, staatus, max_koormus) VALUES ('2024-04-05 05:07:25.860878', '2024-04-05 05:07:25.860891', 'ADMIN', 'ADMIN', 59, 'Subject teacher', NULL, 4, 1, NULL);
INSERT INTO public.kasutajagrupp (created, modified, creator, modifier, id, nimi, kirjeldus, tyyp, staatus, max_koormus) VALUES ('2024-04-05 05:07:25.867426', '2024-04-05 05:07:25.867443', 'ADMIN', 'ADMIN', 70, 'Testitöö vaataja', NULL, 4, 1, NULL);
INSERT INTO public.kasutajagrupp (created, modified, creator, modifier, id, nimi, kirjeldus, tyyp, staatus, max_koormus) VALUES ('2024-04-05 05:07:25.87384', '2024-04-05 05:07:25.873858', 'ADMIN', 'ADMIN', 60, 'User of the source code (text editor)', NULL, 1, 1, NULL);
INSERT INTO public.kasutajagrupp (created, modified, creator, modifier, id, nimi, kirjeldus, tyyp, staatus, max_koormus) VALUES ('2024-04-05 05:07:25.880343', '2024-04-05 05:07:25.880356', 'ADMIN', 'ADMIN', 4, 'Statistics specialist', NULL, 1, 1, NULL);
INSERT INTO public.kasutajagrupp (created, modified, creator, modifier, id, nimi, kirjeldus, tyyp, staatus, max_koormus) VALUES ('2024-04-05 05:07:25.935165', '2024-04-05 05:07:25.935178', 'ADMIN', 'ADMIN', 64, 'Recipient of results publication notifications', NULL, 1, 1, NULL);
INSERT INTO public.kasutajagrupp (created, modified, creator, modifier, id, nimi, kirjeldus, tyyp, staatus, max_koormus) VALUES ('2024-04-05 05:07:25.935207', '2024-04-05 05:07:25.935213', 'ADMIN', 'ADMIN', 66, 'User interface translator', NULL, 1, 1, NULL);
INSERT INTO public.kasutajagrupp (created, modified, creator, modifier, id, nimi, kirjeldus, tyyp, staatus, max_koormus) VALUES ('2024-04-05 05:07:25.944107', '2024-04-05 05:07:25.94412', 'ADMIN', 'ADMIN', 71, 'Ülesannete ja testide avaldaja', NULL, 1, 1, NULL);


--
-- Name: kasutajagrupp_id_seq; Type: SEQUENCE SET; Schema: public; Owner: eisik
--

SELECT pg_catalog.setval('public.kasutajagrupp_id_seq', 1, false);


--
-- PostgreSQL database dump complete
--

