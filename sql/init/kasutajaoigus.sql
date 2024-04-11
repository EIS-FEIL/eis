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
-- Data for Name: kasutajaoigus; Type: TABLE DATA; Schema: public; Owner: eisik
--

INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.043032', '2024-04-05 05:07:17.043056', 'ADMIN', 'ADMIN', 1, 'abi', 'Abiinfo');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.048575', '2024-04-05 05:07:17.048594', 'ADMIN', 'ADMIN', 2, 'minu', 'Oma parooli muutmine jm seaded');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.050023', '2024-04-05 05:07:17.050038', 'ADMIN', 'ADMIN', 3, 'lahendamine', 'Ülesannete lahendamine');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.051376', '2024-04-05 05:07:17.05139', 'ADMIN', 'ADMIN', 4, 'sooritamine', 'Testimiskorra sooritamine');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.052711', '2024-04-05 05:07:17.052729', 'ADMIN', 'ADMIN', 5, 'ylesanded', 'Kõik õigused ülesannetega, välja arvatud rollid');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.053967', '2024-04-05 05:07:17.053981', 'ADMIN', 'ADMIN', 6, 'ylesanded-markused', 'Ülesannetele märkuste kirjutamine');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.055122', '2024-04-05 05:07:17.055136', 'ADMIN', 'ADMIN', 7, 'ylesanded-toimetamine', 'Ülesannete toimetamine, sisutekstide muutmine põhikeeles');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.056552', '2024-04-05 05:07:17.056567', 'ADMIN', 'ADMIN', 8, 'ylesanded-tolkimine', 'Ülesannete tõlkimine, sisutekstide muutmine tõlkekeeltes');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.05779', '2024-04-05 05:07:17.057804', 'ADMIN', 'ADMIN', 9, 'ylesanded-failid', 'Ülesannete lisafailide lisamine/kustutamine');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.0594', '2024-04-05 05:07:17.059416', 'ADMIN', 'ADMIN', 10, 'ylesanderoll', 'Konkreetse ülesandega seotud rollide andmine');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.060676', '2024-04-05 05:07:17.060689', 'ADMIN', 'ADMIN', 11, 'ylesandemall', 'Ülesandemallide koostamine');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.061819', '2024-04-05 05:07:17.06183', 'ADMIN', 'ADMIN', 12, 'ylesandetahemargid', 'Ülesande tähemärkide kokkulugemine');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.062831', '2024-04-05 05:07:17.062842', 'ADMIN', 'ADMIN', 13, 'ylesandekogud', 'Ülesandekogude haldamine');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.063824', '2024-04-05 05:07:17.063835', 'ADMIN', 'ADMIN', 14, 'ylkvaliteet', 'Ülesande kvaliteedimärgi sisestamine');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.065005', '2024-04-05 05:07:17.065017', 'ADMIN', 'ADMIN', 15, 'ylhulgi', 'Kõigi ülesannete hulgi muutmine');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.066134', '2024-04-05 05:07:17.06615', 'ADMIN', 'ADMIN', 16, 'yhisfailid', 'Ühiste failide lisamine ja muutmine ülesannetes kasutamiseks');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.067492', '2024-04-05 05:07:17.067505', 'ADMIN', 'ADMIN', 17, 'ekk-testid', 'Kõik õigused EKK testidega, välja arvatud rollid');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.068535', '2024-04-05 05:07:17.068549', 'ADMIN', 'ADMIN', 18, 'ekk-testid-toimetamine', 'EKK testi toimetamine');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.069635', '2024-04-05 05:07:17.069646', 'ADMIN', 'ADMIN', 19, 'ekk-testid-tolkimine', 'EKK testi tõlkimine');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.070541', '2024-04-05 05:07:17.07055', 'ADMIN', 'ADMIN', 20, 'ekk-testid-failid', 'EKK testi failid');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.071543', '2024-04-05 05:07:17.071554', 'ADMIN', 'ADMIN', 21, 'testhulgi', 'Kõigi testide hulgi muutmine');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.072483', '2024-04-05 05:07:17.072493', 'ADMIN', 'ADMIN', 22, 'ylesannelukustlahti', 'Ülesande lukust lahti võtmine');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.073432', '2024-04-05 05:07:17.073442', 'ADMIN', 'ADMIN', 23, 'lukustlahti', 'Testi lukust lahti võtmine');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.074364', '2024-04-05 05:07:17.074374', 'ADMIN', 'ADMIN', 24, 'korduvsooritatavus', 'EKK vaate testi korduvsooritatavuse seaded');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.075239', '2024-04-05 05:07:17.075248', 'ADMIN', 'ADMIN', 25, 'konsultatsioonid', 'Konsultatsioonid');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.076161', '2024-04-05 05:07:17.076172', 'ADMIN', 'ADMIN', 26, 'testid', 'Kõik õigused avaliku vaate testidega');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.077115', '2024-04-05 05:07:17.077125', 'ADMIN', 'ADMIN', 27, 'testid-toimetamine', 'Avaliku vaate testi toimetamine');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.078027', '2024-04-05 05:07:17.078037', 'ADMIN', 'ADMIN', 28, 'testid-tolkimine', 'Avaliku vaate testi tõlkimine');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.079012', '2024-04-05 05:07:17.079022', 'ADMIN', 'ADMIN', 29, 'testiroll', 'Konkreetse testiga seotud rollide andmine');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.079922', '2024-04-05 05:07:17.079931', 'ADMIN', 'ADMIN', 30, 'regamine', 'Registreerimine, EKK vaade');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.080877', '2024-04-05 05:07:17.080887', 'ADMIN', 'ADMIN', 31, 'ekk-hindamine', 'Hindamise korraldamine, EKK vaade');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.081804', '2024-04-05 05:07:17.081814', 'ADMIN', 'ADMIN', 32, 'ekk-hindamine6', 'VI hindamine');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.082782', '2024-04-05 05:07:17.082793', 'ADMIN', 'ADMIN', 33, 'hindamisanalyys', 'Hindamise analüüs, EKK vaade');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.083657', '2024-04-05 05:07:17.083667', 'ADMIN', 'ADMIN', 34, 'vastusteanalyys', 'Vastuste analüüs, EKK vaade');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.084625', '2024-04-05 05:07:17.084636', 'ADMIN', 'ADMIN', 35, 'vastustevaljavote', 'Vastuste väljavõte, EKK vaade');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.085527', '2024-04-05 05:07:17.085536', 'ADMIN', 'ADMIN', 36, 'eksperthindamine', 'Eksperthindamine, EKK vaade');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.08654', '2024-04-05 05:07:17.086551', 'ADMIN', 'ADMIN', 37, 'ekspertryhmad', 'Ekspertrühmade haldamine, EKK vaade');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.087584', '2024-04-05 05:07:17.087594', 'ADMIN', 'ADMIN', 38, 'hindajamaaramine', 'Hindajate määramine, EKK vaade');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.088565', '2024-04-05 05:07:17.088574', 'ADMIN', 'ADMIN', 39, 'juhendamine', 'Hindajate juhendamine, EKK vaade');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.089392', '2024-04-05 05:07:17.089401', 'ADMIN', 'ADMIN', 40, 'nimekirjad', 'Testile registreerimise nimekirjad');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.090231', '2024-04-05 05:07:17.09024', 'ADMIN', 'ADMIN', 41, 'avtugi', 'EKK toe ligipääs testimiskorrata nimekirjadele');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.091092', '2024-04-05 05:07:17.091101', 'ADMIN', 'ADMIN', 42, 'paroolid', 'Paroolide muutmine');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.092011', '2024-04-05 05:07:17.092024', 'ADMIN', 'ADMIN', 43, 'avalikadmin', 'Soorituskoha administraatori tegevused');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.092949', '2024-04-05 05:07:17.092959', 'ADMIN', 'ADMIN', 44, 'avylesanded', 'Avalikus vaates ülesande koostamine');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.093911', '2024-04-05 05:07:17.093921', 'ADMIN', 'ADMIN', 45, 'aruanded-tunnistused', 'Päringud/Eksamitunnistused');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.094848', '2024-04-05 05:07:17.094859', 'ADMIN', 'ADMIN', 46, 'aruanded-testisooritused', 'Päringud/Testisooritused');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.095877', '2024-04-05 05:07:17.095888', 'ADMIN', 'ADMIN', 47, 'aruanded-kohateated', 'Päringud/Testisoorituskoha teated');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.096869', '2024-04-05 05:07:17.096879', 'ADMIN', 'ADMIN', 48, 'aruanded-vaatlejateated', 'Päringud/Vaatlejate teated');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.097742', '2024-04-05 05:07:17.097752', 'ADMIN', 'ADMIN', 49, 'aruanded-labiviijateated', 'Päringud/Läbiviijate teated');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.098691', '2024-04-05 05:07:17.098703', 'ADMIN', 'ADMIN', 50, 'aruanded-tulemusteteavitused', 'Päringud/Tulemuste teavitused');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.099713', '2024-04-05 05:07:17.099725', 'ADMIN', 'ADMIN', 51, 'aruanded-teated', 'Päringud/Teadete ülevaade');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.100763', '2024-04-05 05:07:17.100774', 'ADMIN', 'ADMIN', 52, 'aruanded-labiviijad', 'Päringud/Läbiviijate aruanded');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.101775', '2024-04-05 05:07:17.101789', 'ADMIN', 'ADMIN', 53, 'aruanded-labiviijakaskkirjad', 'Päringud/Läbiviijate käskkirjad');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.102834', '2024-04-05 05:07:17.102844', 'ADMIN', 'ADMIN', 54, 'aruanded-nousolekud3', 'Päringud/III hindamise nõusolekud');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.103802', '2024-04-05 05:07:17.103814', 'ADMIN', 'ADMIN', 55, 'aruanded-erinevused', 'Päringud/Hindamiserinevused');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.104809', '2024-04-05 05:07:17.104818', 'ADMIN', 'ADMIN', 56, 'aruanded-soorituskohad', 'Päringud/Soorituskohad');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.10574', '2024-04-05 05:07:17.10575', 'ADMIN', 'ADMIN', 57, 'aruanded-tulemused', 'Päringud/Tulemuste statistika');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.106626', '2024-04-05 05:07:17.106636', 'ADMIN', 'ADMIN', 58, 'aruanded-osalemine', 'Päringud/Osalemise statistika');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.107545', '2024-04-05 05:07:17.107555', 'ADMIN', 'ADMIN', 59, 'aruanded-prktulemused', 'Päringud/Piirkondade tulemused');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.108491', '2024-04-05 05:07:17.108501', 'ADMIN', 'ADMIN', 60, 'aruanded-vaided', 'Päringud/Vaiete statistika');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.109426', '2024-04-05 05:07:17.109437', 'ADMIN', 'ADMIN', 61, 'aruanded-osaoskused', 'Osaoskuste võrdlus');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.11039', '2024-04-05 05:07:17.1104', 'ADMIN', 'ADMIN', 62, 'aruanded-testitulemused', 'Testitulemuste võrdlus');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.111356', '2024-04-05 05:07:17.111366', 'ADMIN', 'ADMIN', 63, 'aruanded-rvtunnistused', 'Päringud/Rahvusvahelised eksamid');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.112254', '2024-04-05 05:07:17.112263', 'ADMIN', 'ADMIN', 64, 'aruanded-tugiisikud', 'Päringud/Tugiisikud');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.113163', '2024-04-05 05:07:17.113172', 'ADMIN', 'ADMIN', 65, 'aruanded-sooritajatearv', 'Päringud/Sooritajate arv');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.114', '2024-04-05 05:07:17.114009', 'ADMIN', 'ADMIN', 66, 'erivajadused', 'Erivajaduste haldamine');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.114848', '2024-04-05 05:07:17.114857', 'ADMIN', 'ADMIN', 67, 'korraldamine', 'Eksamikorraldamine');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.115666', '2024-04-05 05:07:17.115675', 'ADMIN', 'ADMIN', 68, 'sisestamine', 'Sisestamine');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.116543', '2024-04-05 05:07:17.116552', 'ADMIN', 'ADMIN', 69, 'parandamine', 'Sisestuste parandamine');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.117501', '2024-04-05 05:07:17.117511', 'ADMIN', 'ADMIN', 70, 'tunnistused', 'Tunnistuste genereerimine ja avaldamine');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.118529', '2024-04-05 05:07:17.118541', 'ADMIN', 'ADMIN', 71, 'statistikaraportid', 'Statistikaraportite genereerimine ja avaldamine');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.119581', '2024-04-05 05:07:17.119591', 'ADMIN', 'ADMIN', 72, 'lepingud', 'Läbiviijate lepingute haldamine');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.12055', '2024-04-05 05:07:17.12056', 'ADMIN', 'ADMIN', 73, 'lopetamised', 'Lõpetamise kontroll');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.121445', '2024-04-05 05:07:17.121457', 'ADMIN', 'ADMIN', 74, 'regkontroll', 'Registreerimise kontroll');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.122915', '2024-04-05 05:07:17.122926', 'ADMIN', 'ADMIN', 75, 'vaided', 'Vaiete haldamine (HTM)');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.123874', '2024-04-05 05:07:17.123885', 'ADMIN', 'ADMIN', 76, 'skannid', 'Skannitud eksamitööd');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.124783', '2024-04-05 05:07:17.124792', 'ADMIN', 'ADMIN', 77, 'ettepanekud', 'Ettepanekute vaatamine');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.125612', '2024-04-05 05:07:17.125622', 'ADMIN', 'ADMIN', 78, 'testiadmin', 'Testi administraator');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.126434', '2024-04-05 05:07:17.126445', 'ADMIN', 'ADMIN', 79, 'intervjuu', 'Intervjuu läbiviimine');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.127251', '2024-04-05 05:07:17.127261', 'ADMIN', 'ADMIN', 80, 'shindamine', 'Suulise testi hindamine');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.128174', '2024-04-05 05:07:17.128183', 'ADMIN', 'ADMIN', 81, 'khindamine', 'Kirjaliku testi hindamine');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.129049', '2024-04-05 05:07:17.129058', 'ADMIN', 'ADMIN', 82, 'thindamine', 'Testimiskorrata testi hindamine');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.129909', '2024-04-05 05:07:17.129918', 'ADMIN', 'ADMIN', 83, 'nousolekud', 'Testide läbiviimises osalemise nõusoleku andmine');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.130706', '2024-04-05 05:07:17.130716', 'ADMIN', 'ADMIN', 84, 'toovaatamine', 'Sooritaja testitöö vaatamine');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.131708', '2024-04-05 05:07:17.131721', 'ADMIN', 'ADMIN', 85, 'klass', 'Pedagoogi õigus (klassi õpilaste loetelu, kooli testinimekirjad)');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.13277', '2024-04-05 05:07:17.13278', 'ADMIN', 'ADMIN', 86, 'admin', 'Kõik administreerimismenüü tegevused');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.133691', '2024-04-05 05:07:17.133702', 'ADMIN', 'ADMIN', 87, 'olulineinfo', 'Olulise info muutmine');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.134605', '2024-04-05 05:07:17.134615', 'ADMIN', 'ADMIN', 88, 'keskserver', 'Kohalikus serveris õigus laadida keskserverist andmeid');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.13547', '2024-04-05 05:07:17.13548', 'ADMIN', 'ADMIN', 89, 'testimiskorrad', 'Testimiskordade ja toimumisaegade haldamine, EKK vaade');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.1364', '2024-04-05 05:07:17.13641', 'ADMIN', 'ADMIN', 90, 'tkorddel', 'Testimiskorra kustutamine');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.137325', '2024-04-05 05:07:17.137335', 'ADMIN', 'ADMIN', 91, 'piirkonnad', 'Piirkondade haldus');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.138254', '2024-04-05 05:07:17.138264', 'ADMIN', 'ADMIN', 92, 'kohad', 'Soorituskohtade haldus');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.139213', '2024-04-05 05:07:17.139223', 'ADMIN', 'ADMIN', 93, 'kiirvalikud', 'Kiirvalikute haldus');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.140126', '2024-04-05 05:07:17.140136', 'ADMIN', 'ADMIN', 94, 'sessioonid', 'Testsesioonide haldus');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.141075', '2024-04-05 05:07:17.141085', 'ADMIN', 'ADMIN', 95, 'ametnikud', 'Eksamikeskuse kasutajate haldus (välja arvatud admin)');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.141948', '2024-04-05 05:07:17.141958', 'ADMIN', 'ADMIN', 96, 'kasutajad', 'Testide läbiviimisega seotud kasutajate haldus');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.142817', '2024-04-05 05:07:17.142827', 'ADMIN', 'ADMIN', 97, 'eksaminandid', 'Sooritajate haldus');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.143714', '2024-04-05 05:07:17.143723', 'ADMIN', 'ADMIN', 98, 'eksaminandid-ik', 'Sooritajale isikukoodi lisamine');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.144612', '2024-04-05 05:07:17.144622', 'ADMIN', 'ADMIN', 99, 'caeeeltest', 'CAE eeltesti sooritanute laadimine');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.145498', '2024-04-05 05:07:17.145507', 'ADMIN', 'ADMIN', 100, 'kparoolid', 'Eksamikeskuse vaates parooli genereerimine või määramine (neile, kes pole eksamikeskuse kasutajad)');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.146448', '2024-04-05 05:07:17.14646', 'ADMIN', 'ADMIN', 101, 'profiil', 'Läbiviija profiil');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.147402', '2024-04-05 05:07:17.147413', 'ADMIN', 'ADMIN', 102, 'profiil-vaatleja', 'Vaatleja profiili osa läbiviija profiili vormil');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.148339', '2024-04-05 05:07:17.148348', 'ADMIN', 'ADMIN', 103, 'klassifikaatorid', 'Klassifikaatorite haldus');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.149467', '2024-04-05 05:07:17.14948', 'ADMIN', 'ADMIN', 104, 'logi', 'Logi vaatamine');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.150701', '2024-04-05 05:07:17.150712', 'ADMIN', 'ADMIN', 105, 'abimaterjalid', 'Küsitluste abimaterjalid');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.151623', '2024-04-05 05:07:17.151633', 'ADMIN', 'ADMIN', 106, 'toimumisprotokoll', 'Toimumise protokoll avalikus vaates');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.15248', '2024-04-05 05:07:17.152489', 'ADMIN', 'ADMIN', 107, 'tprotsisestus', 'Toimumise protokolli osalejate sisestamine avalikus vaates');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.153281', '2024-04-05 05:07:17.153291', 'ADMIN', 'ADMIN', 108, 'aineopetaja', 'Aineõpetaja õigus oma õpilaste tulemusi vaadata ja sisestada toimumise protokollile');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.1542', '2024-04-05 05:07:17.15421', 'ADMIN', 'ADMIN', 109, 'rveksamid', 'Rahvusvaheliste eksamite tunnistuste kirjeldamine');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.15513', '2024-04-05 05:07:17.155139', 'ADMIN', 'ADMIN', 110, 'failid', 'Failide allalaadimine koolis');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.155987', '2024-04-05 05:07:17.155999', 'ADMIN', 'ADMIN', 111, 'plangid', 'Plankide haldur koolis');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.156801', '2024-04-05 05:07:17.156811', 'ADMIN', 'ADMIN', 112, 'srcedit', 'Ülesannete koostamisel HTML lähtekoodi kasutamine');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.157724', '2024-04-05 05:07:17.157734', 'ADMIN', 'ADMIN', 113, 'koolipsyh', 'Koolipsühholoogi testid');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.158651', '2024-04-05 05:07:17.158661', 'ADMIN', 'ADMIN', 114, 'pslitsentsid', 'Koolipsühholoogide litsentside haldamine');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.159565', '2024-04-05 05:07:17.159576', 'ADMIN', 'ADMIN', 115, 'logopeed', 'Logopeeditestid');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.160439', '2024-04-05 05:07:17.160449', 'ADMIN', 'ADMIN', 116, 'lglitsentsid', 'Logopeedide litsentside haldamine');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.161236', '2024-04-05 05:07:17.161245', 'ADMIN', 'ADMIN', 117, 'omanimekirjad', 'Avaliku vaate testide sooritajate nimekirjad');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.162178', '2024-04-05 05:07:17.162187', 'ADMIN', 'ADMIN', 118, 'tookogumikud', 'Pedagoogide töökogumikud');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.163113', '2024-04-05 05:07:17.163123', 'ADMIN', 'ADMIN', 119, 'kohteelvaade', 'Soorituskoha administraatori eelvaade');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.163849', '2024-04-05 05:07:17.163858', 'ADMIN', 'ADMIN', 120, 'ui-tolkimine', 'Kasutajaliidese tekstide tõlkimine');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.164805', '2024-04-05 05:07:17.164817', 'ADMIN', 'ADMIN', 121, 'tulemusteavaldamine', 'Tulemuste avaldamine');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.165891', '2024-04-05 05:07:17.165918', 'ADMIN', 'ADMIN', 122, 'ettepanemine', 'Küsimuste ja ettepanekute esitamine avalikus vaates');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.167145', '2024-04-05 05:07:17.167155', 'ADMIN', 'ADMIN', 123, 'sisuavaldamine', 'Ülesannete, testide ja e-kogude avaldamine');
INSERT INTO public.kasutajaoigus (created, modified, creator, modifier, id, nimi, kirjeldus) VALUES ('2024-04-05 05:07:17.168112', '2024-04-05 05:07:17.168122', 'ADMIN', 'ADMIN', 124, 'sysinfo', 'Süsteemi monitoorimise info');


--
-- Name: kasutajaoigus_id_seq; Type: SEQUENCE SET; Schema: public; Owner: eisik
--

SELECT pg_catalog.setval('public.kasutajaoigus_id_seq', 124, true);


--
-- PostgreSQL database dump complete
--

