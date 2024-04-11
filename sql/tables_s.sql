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
-- Name: public; Type: SCHEMA; Schema: -; Owner: pg_database_owner
--

CREATE SCHEMA public;


ALTER SCHEMA public OWNER TO pg_database_owner;

--
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: pg_database_owner
--

COMMENT ON SCHEMA public IS 'standard public schema';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: beaker_cache; Type: TABLE; Schema: public; Owner: eisik
--

CREATE TABLE public.beaker_cache (
    id integer NOT NULL,
    namespace character varying(255) NOT NULL,
    accessed timestamp without time zone NOT NULL,
    created timestamp without time zone NOT NULL,
    data bytea NOT NULL,
    kasutaja_id integer,
    autentimine character varying(2),
    kehtetu boolean,
    remote_addr character varying(60),
    app character varying(6)
);


ALTER TABLE public.beaker_cache OWNER TO eisik;

--
-- Name: TABLE beaker_cache; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON TABLE public.beaker_cache IS 'Kasutajate seansid';


--
-- Name: COLUMN beaker_cache.id; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.beaker_cache.id IS 'kirje identifikaator';


--
-- Name: COLUMN beaker_cache.namespace; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.beaker_cache.namespace IS 'seansi identifikaator';


--
-- Name: COLUMN beaker_cache.accessed; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.beaker_cache.accessed IS 'viimase kasutamise aeg';


--
-- Name: COLUMN beaker_cache.created; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.beaker_cache.created IS 'loomise aeg';


--
-- Name: COLUMN beaker_cache.data; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.beaker_cache.data IS 'andmed';


--
-- Name: COLUMN beaker_cache.kasutaja_id; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.beaker_cache.kasutaja_id IS 'kasutaja ID';


--
-- Name: COLUMN beaker_cache.autentimine; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.beaker_cache.autentimine IS 'autentimisviis';


--
-- Name: COLUMN beaker_cache.kehtetu; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.beaker_cache.kehtetu IS 'kas seanss on kehtiv';


--
-- Name: COLUMN beaker_cache.remote_addr; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.beaker_cache.remote_addr IS 'kasutaja aadress';


--
-- Name: COLUMN beaker_cache.app; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.beaker_cache.app IS 'rakenduse nimi';


--
-- Name: beaker_cache_id_seq; Type: SEQUENCE; Schema: public; Owner: eisik
--

CREATE SEQUENCE public.beaker_cache_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.beaker_cache_id_seq OWNER TO eisik;

--
-- Name: beaker_cache_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: eisik
--

ALTER SEQUENCE public.beaker_cache_id_seq OWNED BY public.beaker_cache.id;


--
-- Name: tempvastus; Type: TABLE; Schema: public; Owner: eisik
--

CREATE TABLE public.tempvastus (
    created timestamp without time zone NOT NULL,
    modified timestamp without time zone NOT NULL,
    creator character varying(50) NOT NULL,
    modifier character varying(50) NOT NULL,
    id integer NOT NULL,
    temp_id integer,
    filename character varying(256),
    filedata bytea,
    uuid character varying(36)
);


ALTER TABLE public.tempvastus OWNER TO eisik;

--
-- Name: TABLE tempvastus; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON TABLE public.tempvastus IS 'Lahendaja poolt üles laaditud failide ajutine hoiupaik,
    kui ülesannet lahendatakse proovimiseks, ilma vastuseid salvestamata';


--
-- Name: COLUMN tempvastus.created; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.tempvastus.created IS 'kirje loomise aeg';


--
-- Name: COLUMN tempvastus.modified; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.tempvastus.modified IS 'kirje viimase muutmise aeg';


--
-- Name: COLUMN tempvastus.creator; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.tempvastus.creator IS 'kirje looja isikukood';


--
-- Name: COLUMN tempvastus.modifier; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.tempvastus.modifier IS 'kirje viimase muutja isikukood';


--
-- Name: COLUMN tempvastus.id; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.tempvastus.id IS 'kirje identifikaator';


--
-- Name: COLUMN tempvastus.temp_id; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.tempvastus.temp_id IS 'vastuse id';


--
-- Name: COLUMN tempvastus.filename; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.tempvastus.filename IS 'failinimi';


--
-- Name: COLUMN tempvastus.filedata; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.tempvastus.filedata IS 'faili sisu';


--
-- Name: COLUMN tempvastus.uuid; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.tempvastus.uuid IS 'äraarvamatu osa URList faili laadimise korral';


--
-- Name: tempvastus_id_seq; Type: SEQUENCE; Schema: public; Owner: eisik
--

CREATE SEQUENCE public.tempvastus_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tempvastus_id_seq OWNER TO eisik;

--
-- Name: tempvastus_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: eisik
--

ALTER SEQUENCE public.tempvastus_id_seq OWNED BY public.tempvastus.id;


--
-- Name: toorvastus; Type: TABLE; Schema: public; Owner: eisik
--

CREATE TABLE public.toorvastus (
    created timestamp without time zone NOT NULL,
    modified timestamp without time zone NOT NULL,
    creator character varying(50) NOT NULL,
    modifier character varying(50) NOT NULL,
    id integer NOT NULL,
    ylesandevastus_id integer NOT NULL,
    kood character varying(102) NOT NULL,
    sisu text,
    filename character varying(256),
    filesize integer,
    fileversion character varying(8),
    on_pickle boolean
);


ALTER TABLE public.toorvastus OWNER TO eisik;

--
-- Name: TABLE toorvastus; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON TABLE public.toorvastus IS 'Testi sooritamise ajal saadetud ühe ülesande vastused.
    Tulemuste arvutamise ajal jagatakse need andmed põhibaasi tabelitesse
    kysimusevastus ja kvsisu, kuid see võtab aega ning testiaegse jõudluse
    optimeerimiseks tehakse seda alles siis, kui on vaja arvutada tulemusi.
    Kuni toorvastus ei ole veel põhibaasi viidud,
    seni on põhibaasis ylesandevastus.on_toorvastus = True';


--
-- Name: COLUMN toorvastus.created; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.toorvastus.created IS 'kirje loomise aeg';


--
-- Name: COLUMN toorvastus.modified; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.toorvastus.modified IS 'kirje viimase muutmise aeg';


--
-- Name: COLUMN toorvastus.creator; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.toorvastus.creator IS 'kirje looja isikukood';


--
-- Name: COLUMN toorvastus.modifier; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.toorvastus.modifier IS 'kirje viimase muutja isikukood';


--
-- Name: COLUMN toorvastus.id; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.toorvastus.id IS 'kirje identifikaator';


--
-- Name: COLUMN toorvastus.ylesandevastus_id; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.toorvastus.ylesandevastus_id IS 'põhibaasi ylesandevastus.id';


--
-- Name: COLUMN toorvastus.kood; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.toorvastus.kood IS 'küsimuse kood';


--
-- Name: COLUMN toorvastus.sisu; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.toorvastus.sisu IS 'tekstvastus (kui pole fail)';


--
-- Name: COLUMN toorvastus.filename; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.toorvastus.filename IS 'failinimi (kui on fail)';


--
-- Name: COLUMN toorvastus.filesize; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.toorvastus.filesize IS 'faili suurus baitides';


--
-- Name: COLUMN toorvastus.fileversion; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.toorvastus.fileversion IS 'versioon';


--
-- Name: COLUMN toorvastus.on_pickle; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.toorvastus.on_pickle IS 'kas filedata sisaldab pickle-pakitud sisu (kasutusel siis, kui vastus on list)';


--
-- Name: toorvastus_id_seq; Type: SEQUENCE; Schema: public; Owner: eisik
--

CREATE SEQUENCE public.toorvastus_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.toorvastus_id_seq OWNER TO eisik;

--
-- Name: toorvastus_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: eisik
--

ALTER SEQUENCE public.toorvastus_id_seq OWNED BY public.toorvastus.id;


--
-- Name: ylesandevaatamine; Type: TABLE; Schema: public; Owner: eisik
--

CREATE TABLE public.ylesandevaatamine (
    created timestamp without time zone NOT NULL,
    modified timestamp without time zone NOT NULL,
    creator character varying(50) NOT NULL,
    modifier character varying(50) NOT NULL,
    id integer NOT NULL,
    sooritus_id integer NOT NULL,
    valitudylesanne_id integer NOT NULL,
    testiylesanne_id integer NOT NULL,
    komplekt_id integer NOT NULL,
    algus timestamp without time zone NOT NULL
);


ALTER TABLE public.ylesandevaatamine OWNER TO eisik;

--
-- Name: TABLE ylesandevaatamine; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON TABLE public.ylesandevaatamine IS 'Ülesande esmase lahendajale kuvamise aja salvestamise tabel.
    Aega ei salvestata kohe tabelis Ylesandevastus, sest valikülesande korral
    võib lahendaja vaadata mitut valikut ning kõigi algusaeg on vaja salvestada,
    kuid Ylesandevastuse tabelis on jooksvalt üheainsa valiku kirje';


--
-- Name: COLUMN ylesandevaatamine.created; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.ylesandevaatamine.created IS 'kirje loomise aeg';


--
-- Name: COLUMN ylesandevaatamine.modified; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.ylesandevaatamine.modified IS 'kirje viimase muutmise aeg';


--
-- Name: COLUMN ylesandevaatamine.creator; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.ylesandevaatamine.creator IS 'kirje looja isikukood';


--
-- Name: COLUMN ylesandevaatamine.modifier; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.ylesandevaatamine.modifier IS 'kirje viimase muutja isikukood';


--
-- Name: COLUMN ylesandevaatamine.id; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.ylesandevaatamine.id IS 'kirje identifikaator';


--
-- Name: COLUMN ylesandevaatamine.sooritus_id; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.ylesandevaatamine.sooritus_id IS 'viide sooritusele';


--
-- Name: COLUMN ylesandevaatamine.valitudylesanne_id; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.ylesandevaatamine.valitudylesanne_id IS 'viide valitudülesandele';


--
-- Name: COLUMN ylesandevaatamine.testiylesanne_id; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.ylesandevaatamine.testiylesanne_id IS 'viide testiülesandele';


--
-- Name: COLUMN ylesandevaatamine.komplekt_id; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.ylesandevaatamine.komplekt_id IS 'viide komplektile';


--
-- Name: COLUMN ylesandevaatamine.algus; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.ylesandevaatamine.algus IS 'ylesande lugemise aeg';


--
-- Name: ylesandevaatamine_id_seq; Type: SEQUENCE; Schema: public; Owner: eisik
--

CREATE SEQUENCE public.ylesandevaatamine_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.ylesandevaatamine_id_seq OWNER TO eisik;

--
-- Name: ylesandevaatamine_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: eisik
--

ALTER SEQUENCE public.ylesandevaatamine_id_seq OWNED BY public.ylesandevaatamine.id;


--
-- Name: beaker_cache id; Type: DEFAULT; Schema: public; Owner: eisik
--

ALTER TABLE ONLY public.beaker_cache ALTER COLUMN id SET DEFAULT nextval('public.beaker_cache_id_seq'::regclass);


--
-- Name: tempvastus id; Type: DEFAULT; Schema: public; Owner: eisik
--

ALTER TABLE ONLY public.tempvastus ALTER COLUMN id SET DEFAULT nextval('public.tempvastus_id_seq'::regclass);


--
-- Name: toorvastus id; Type: DEFAULT; Schema: public; Owner: eisik
--

ALTER TABLE ONLY public.toorvastus ALTER COLUMN id SET DEFAULT nextval('public.toorvastus_id_seq'::regclass);


--
-- Name: ylesandevaatamine id; Type: DEFAULT; Schema: public; Owner: eisik
--

ALTER TABLE ONLY public.ylesandevaatamine ALTER COLUMN id SET DEFAULT nextval('public.ylesandevaatamine_id_seq'::regclass);


--
-- Name: beaker_cache beaker_cache_pkey; Type: CONSTRAINT; Schema: public; Owner: eisik
--

ALTER TABLE ONLY public.beaker_cache
    ADD CONSTRAINT beaker_cache_pkey PRIMARY KEY (id, namespace);


--
-- Name: tempvastus tempvastus_pkey; Type: CONSTRAINT; Schema: public; Owner: eisik
--

ALTER TABLE ONLY public.tempvastus
    ADD CONSTRAINT tempvastus_pkey PRIMARY KEY (id);


--
-- Name: toorvastus toorvastus_pkey; Type: CONSTRAINT; Schema: public; Owner: eisik
--

ALTER TABLE ONLY public.toorvastus
    ADD CONSTRAINT toorvastus_pkey PRIMARY KEY (id);


--
-- Name: ylesandevaatamine ylesandevaatamine_pkey; Type: CONSTRAINT; Schema: public; Owner: eisik
--

ALTER TABLE ONLY public.ylesandevaatamine
    ADD CONSTRAINT ylesandevaatamine_pkey PRIMARY KEY (id);


--
-- Name: ix_toorvastus_ylesandevastus_id; Type: INDEX; Schema: public; Owner: eisik
--

CREATE INDEX ix_toorvastus_ylesandevastus_id ON public.toorvastus USING btree (ylesandevastus_id);


--
-- Name: ix_ylesandevaatamine_komplekt_id; Type: INDEX; Schema: public; Owner: eisik
--

CREATE INDEX ix_ylesandevaatamine_komplekt_id ON public.ylesandevaatamine USING btree (komplekt_id);


--
-- Name: ix_ylesandevaatamine_sooritus_id; Type: INDEX; Schema: public; Owner: eisik
--

CREATE INDEX ix_ylesandevaatamine_sooritus_id ON public.ylesandevaatamine USING btree (sooritus_id);


--
-- Name: ix_ylesandevaatamine_testiylesanne_id; Type: INDEX; Schema: public; Owner: eisik
--

CREATE INDEX ix_ylesandevaatamine_testiylesanne_id ON public.ylesandevaatamine USING btree (testiylesanne_id);


--
-- Name: ix_ylesandevaatamine_valitudylesanne_id; Type: INDEX; Schema: public; Owner: eisik
--

CREATE INDEX ix_ylesandevaatamine_valitudylesanne_id ON public.ylesandevaatamine USING btree (valitudylesanne_id);


--
-- PostgreSQL database dump complete
--

