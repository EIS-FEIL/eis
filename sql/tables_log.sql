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
-- Name: haridlog; Type: TABLE; Schema: public; Owner: eisik
--

CREATE TABLE public.haridlog (
    created timestamp without time zone NOT NULL,
    modified timestamp without time zone NOT NULL,
    creator character varying(50) NOT NULL,
    modifier character varying(50) NOT NULL,
    id integer NOT NULL,
    state character varying(50),
    nonce character varying(32),
    aut_aeg timestamp without time zone,
    aut_params character varying(512),
    resp_params character varying(512),
    resp_aeg timestamp without time zone,
    token_data text,
    token_msg text,
    userinfo_msg text,
    isikukood character varying(50),
    eesnimi character varying(50),
    perenimi character varying(50),
    err integer,
    request_url character varying(200),
    remote_addr character varying(36),
    server1_addr character varying(25),
    server2_addr character varying(25)
);


ALTER TABLE public.haridlog OWNER TO eisik;

--
-- Name: TABLE haridlog; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON TABLE public.haridlog IS 'HarID autentimispäringute logi';


--
-- Name: COLUMN haridlog.created; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.haridlog.created IS 'kirje loomise aeg';


--
-- Name: COLUMN haridlog.modified; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.haridlog.modified IS 'kirje viimase muutmise aeg';


--
-- Name: COLUMN haridlog.creator; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.haridlog.creator IS 'kirje looja isikukood';


--
-- Name: COLUMN haridlog.modifier; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.haridlog.modifier IS 'kirje viimase muutja isikukood';


--
-- Name: COLUMN haridlog.id; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.haridlog.id IS 'kirje identifikaator';


--
-- Name: COLUMN haridlog.state; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.haridlog.state IS 'genereeritud juharvu räsi';


--
-- Name: COLUMN haridlog.nonce; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.haridlog.nonce IS 'genereeritud juhuarv';


--
-- Name: COLUMN haridlog.aut_aeg; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.haridlog.aut_aeg IS 'autentimispäringu aeg';


--
-- Name: COLUMN haridlog.aut_params; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.haridlog.aut_params IS 'autentimispäringu parameetrid';


--
-- Name: COLUMN haridlog.resp_params; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.haridlog.resp_params IS 'autentimispäringu vastus GET URL';


--
-- Name: COLUMN haridlog.resp_aeg; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.haridlog.resp_aeg IS 'autentimispäringu vastuse aeg';


--
-- Name: COLUMN haridlog.token_data; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.haridlog.token_data IS 'identifitseerimistõendi kest';


--
-- Name: COLUMN haridlog.token_msg; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.haridlog.token_msg IS 'identifitseerimistõendi sisu peale lahti kodeerimist';


--
-- Name: COLUMN haridlog.userinfo_msg; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.haridlog.userinfo_msg IS 'infopäringu vastus';


--
-- Name: COLUMN haridlog.isikukood; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.haridlog.isikukood IS 'autenditud kasutaja riik ja isikukood';


--
-- Name: COLUMN haridlog.eesnimi; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.haridlog.eesnimi IS 'autenditud kasutaja eesnimi';


--
-- Name: COLUMN haridlog.perenimi; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.haridlog.perenimi IS 'autenditud kasutaja perekonnanimi';


--
-- Name: COLUMN haridlog.err; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.haridlog.err IS 'vea kood (vt loginharid.py)';


--
-- Name: COLUMN haridlog.request_url; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.haridlog.request_url IS 'EISi URL, mille poole pöördudes suunati kasutaja autentima ja kuhu peale autentimist kasutaja tagasi suuname';


--
-- Name: COLUMN haridlog.remote_addr; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.haridlog.remote_addr IS 'klient';


--
-- Name: COLUMN haridlog.server1_addr; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.haridlog.server1_addr IS 'server, kust autentimist alustati';


--
-- Name: COLUMN haridlog.server2_addr; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.haridlog.server2_addr IS 'server, kuhu kasutaja HarIDist tagasi suunati';


--
-- Name: haridlog_id_seq; Type: SEQUENCE; Schema: public; Owner: eisik
--

CREATE SEQUENCE public.haridlog_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.haridlog_id_seq OWNER TO eisik;

--
-- Name: haridlog_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: eisik
--

ALTER SEQUENCE public.haridlog_id_seq OWNED BY public.haridlog.id;


--
-- Name: logi; Type: TABLE; Schema: public; Owner: eisik
--

CREATE TABLE public.logi (
    id integer NOT NULL,
    uuid character varying(32),
    request_id character varying(32),
    aeg timestamp without time zone NOT NULL,
    isikukood character varying(50),
    kontroller character varying(50),
    tegevus character varying(50),
    param text,
    tyyp integer,
    sisu text,
    url character varying(200),
    path character varying(160),
    meetod character varying(10),
    remote_addr character varying(60),
    server_addr character varying(60),
    user_agent character varying(150),
    app character varying(10),
    koht_id integer,
    oppekoht_id integer,
    testiosa_id integer,
    kestus double precision
);


ALTER TABLE public.logi OWNER TO eisik;

--
-- Name: TABLE logi; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON TABLE public.logi IS 'Sündmuste ja veateadete logi';


--
-- Name: COLUMN logi.id; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.logi.id IS 'kirje identifikaator';


--
-- Name: COLUMN logi.uuid; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.logi.uuid IS 'logikirje identifikaator';


--
-- Name: COLUMN logi.request_id; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.logi.request_id IS 'brauseri pöördumise identifikaator';


--
-- Name: COLUMN logi.aeg; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.logi.aeg IS 'logikirje aeg';


--
-- Name: COLUMN logi.isikukood; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.logi.isikukood IS 'kasutaja isikukood';


--
-- Name: COLUMN logi.kontroller; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.logi.kontroller IS 'rakenduse kontroller, milles logisündmus tekkis (või muu lk identifikaator)';


--
-- Name: COLUMN logi.tegevus; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.logi.tegevus IS 'rakenduse tegevus, milles logisündmus tekkis';


--
-- Name: COLUMN logi.param; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.logi.param IS 'rakenduse parameetrid, kui logisündmus tekkis';


--
-- Name: COLUMN logi.tyyp; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.logi.tyyp IS 'logitüüp: 1 - kasutuslogi; 2 - vealogi; 3 - sisselogimise logi; 4 - kasutajaõiguste muutmine; 5 - X-tee kliendi sõnumite logi; 6 - muu info; 7 - JSON sõnum; 8 - koha valik; 9 - webhook';


--
-- Name: COLUMN logi.sisu; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.logi.sisu IS 'logi sisu';


--
-- Name: COLUMN logi.url; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.logi.url IS 'tegevuse URL';


--
-- Name: COLUMN logi.path; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.logi.path IS 'URLis sisalduv rada';


--
-- Name: COLUMN logi.meetod; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.logi.meetod IS 'HTTP meetod (get, post)';


--
-- Name: COLUMN logi.remote_addr; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.logi.remote_addr IS 'klient';


--
-- Name: COLUMN logi.server_addr; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.logi.server_addr IS 'server';


--
-- Name: COLUMN logi.user_agent; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.logi.user_agent IS 'brauser';


--
-- Name: COLUMN logi.app; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.logi.app IS 'rakendus: eis, ekk, plank, adapter';


--
-- Name: COLUMN logi.koht_id; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.logi.koht_id IS 'viide töökohale';


--
-- Name: COLUMN logi.oppekoht_id; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.logi.oppekoht_id IS 'viide koolile, kus kasutaja õpib';


--
-- Name: COLUMN logi.testiosa_id; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.logi.testiosa_id IS 'viide testiosale, kui see on testi sooritamisel tekkinud logi (testisoorituste arvu saamiseks ajavahemikul)';


--
-- Name: COLUMN logi.kestus; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.logi.kestus IS 'päringu kestus sekundites';


--
-- Name: logi_adapter; Type: TABLE; Schema: public; Owner: eisik
--

CREATE TABLE public.logi_adapter (
    id integer NOT NULL,
    algus timestamp without time zone,
    aeg timestamp without time zone NOT NULL,
    client character varying(100),
    userid character varying(66),
    service character varying(50),
    input_xml text,
    output_xml text,
    remote_addr character varying(60),
    server_addr character varying(60),
    url text,
    tyyp character varying(1)
);


ALTER TABLE public.logi_adapter OWNER TO eisik;

--
-- Name: TABLE logi_adapter; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON TABLE public.logi_adapter IS 'X-tee serveri logi';


--
-- Name: COLUMN logi_adapter.id; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.logi_adapter.id IS 'kirje identifikaator';


--
-- Name: COLUMN logi_adapter.algus; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.logi_adapter.algus IS 'päringu alguse aeg';


--
-- Name: COLUMN logi_adapter.aeg; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.logi_adapter.aeg IS 'logikirje aeg (päringu lõpp)';


--
-- Name: COLUMN logi_adapter.client; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.logi_adapter.client IS 'kliendi andmed';


--
-- Name: COLUMN logi_adapter.userid; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.logi_adapter.userid IS 'riigi kood ja isikukood';


--
-- Name: COLUMN logi_adapter.service; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.logi_adapter.service IS 'kasutatud teenuse nimi';


--
-- Name: COLUMN logi_adapter.input_xml; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.logi_adapter.input_xml IS 'sisendi XML/JSON';


--
-- Name: COLUMN logi_adapter.output_xml; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.logi_adapter.output_xml IS 'väljundi XML/JSON';


--
-- Name: COLUMN logi_adapter.remote_addr; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.logi_adapter.remote_addr IS 'klient';


--
-- Name: COLUMN logi_adapter.server_addr; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.logi_adapter.server_addr IS 'server';


--
-- Name: COLUMN logi_adapter.url; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.logi_adapter.url IS 'URL';


--
-- Name: COLUMN logi_adapter.tyyp; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.logi_adapter.tyyp IS 'J - JSON; X - XML';


--
-- Name: logi_adapter_id_seq; Type: SEQUENCE; Schema: public; Owner: eisik
--

CREATE SEQUENCE public.logi_adapter_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.logi_adapter_id_seq OWNER TO eisik;

--
-- Name: logi_adapter_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: eisik
--

ALTER SEQUENCE public.logi_adapter_id_seq OWNED BY public.logi_adapter.id;


--
-- Name: logi_id_seq; Type: SEQUENCE; Schema: public; Owner: eisik
--

CREATE SEQUENCE public.logi_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.logi_id_seq OWNER TO eisik;

--
-- Name: logi_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: eisik
--

ALTER SEQUENCE public.logi_id_seq OWNED BY public.logi.id;


--
-- Name: ltest; Type: TABLE; Schema: public; Owner: eisik
--

CREATE TABLE public.ltest (
    id integer NOT NULL,
    aeg timestamp without time zone NOT NULL,
    algus timestamp without time zone,
    isikukood character varying(50),
    kestus integer,
    liik character varying(20),
    url character varying(200),
    meetod character varying(10),
    remote_addr character varying(60),
    server_addr character varying(60),
    user_agent character varying(150),
    test_jrk integer
);


ALTER TABLE public.ltest OWNER TO eisik;

--
-- Name: TABLE ltest; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON TABLE public.ltest IS 'Koormustesti logiandmed';


--
-- Name: COLUMN ltest.id; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.ltest.id IS 'kirje identifikaator';


--
-- Name: COLUMN ltest.aeg; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.ltest.aeg IS 'logikirje aeg';


--
-- Name: COLUMN ltest.algus; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.ltest.algus IS 'pöördumise alguse aeg (sama pöördumise transaktsioonide sidumiseks)';


--
-- Name: COLUMN ltest.isikukood; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.ltest.isikukood IS 'kasutaja isikukood';


--
-- Name: COLUMN ltest.kestus; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.ltest.kestus IS 'transaktsiooni kestus ms';


--
-- Name: COLUMN ltest.liik; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.ltest.liik IS 'transaktsiooni lõpp: commit/rollback';


--
-- Name: COLUMN ltest.url; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.ltest.url IS 'tegevuse URL';


--
-- Name: COLUMN ltest.meetod; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.ltest.meetod IS 'HTTP meetod (get, post)';


--
-- Name: COLUMN ltest.remote_addr; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.ltest.remote_addr IS 'klient';


--
-- Name: COLUMN ltest.server_addr; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.ltest.server_addr IS 'server';


--
-- Name: COLUMN ltest.user_agent; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.ltest.user_agent IS 'brauser';


--
-- Name: COLUMN ltest.test_jrk; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.ltest.test_jrk IS 'koormustesti jrk nr (omistatakse peale testi lõppu)';


--
-- Name: ltest_id_seq; Type: SEQUENCE; Schema: public; Owner: eisik
--

CREATE SEQUENCE public.ltest_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.ltest_id_seq OWNER TO eisik;

--
-- Name: ltest_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: eisik
--

ALTER SEQUENCE public.ltest_id_seq OWNED BY public.ltest.id;


--
-- Name: taralog; Type: TABLE; Schema: public; Owner: eisik
--

CREATE TABLE public.taralog (
    created timestamp without time zone NOT NULL,
    modified timestamp without time zone NOT NULL,
    creator character varying(50) NOT NULL,
    modifier character varying(50) NOT NULL,
    id integer NOT NULL,
    state character varying(50),
    nonce character varying(32),
    aut_aeg timestamp without time zone,
    aut_params character varying(512),
    resp_params character varying(512),
    resp_aeg timestamp without time zone,
    token_data text,
    token_msg text,
    isikukood character varying(50),
    eesnimi character varying(50),
    perenimi character varying(50),
    err integer,
    request_url character varying(200),
    remote_addr character varying(36)
);


ALTER TABLE public.taralog OWNER TO eisik;

--
-- Name: TABLE taralog; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON TABLE public.taralog IS 'TARA autentimispäringute logi';


--
-- Name: COLUMN taralog.created; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.taralog.created IS 'kirje loomise aeg';


--
-- Name: COLUMN taralog.modified; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.taralog.modified IS 'kirje viimase muutmise aeg';


--
-- Name: COLUMN taralog.creator; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.taralog.creator IS 'kirje looja isikukood';


--
-- Name: COLUMN taralog.modifier; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.taralog.modifier IS 'kirje viimase muutja isikukood';


--
-- Name: COLUMN taralog.id; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.taralog.id IS 'kirje identifikaator';


--
-- Name: COLUMN taralog.state; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.taralog.state IS 'genereeritud juharvu räsi';


--
-- Name: COLUMN taralog.nonce; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.taralog.nonce IS 'genereeritud juhuarv';


--
-- Name: COLUMN taralog.aut_aeg; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.taralog.aut_aeg IS 'autentimispäringu aeg';


--
-- Name: COLUMN taralog.aut_params; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.taralog.aut_params IS 'autentimispäringu parameetrid';


--
-- Name: COLUMN taralog.resp_params; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.taralog.resp_params IS 'autentimispäringu vastus GET URL';


--
-- Name: COLUMN taralog.resp_aeg; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.taralog.resp_aeg IS 'autentimispäringu vastuse aeg';


--
-- Name: COLUMN taralog.token_data; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.taralog.token_data IS 'identifitseerimistõendi kest';


--
-- Name: COLUMN taralog.token_msg; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.taralog.token_msg IS 'identifitseerimistõendi sisu peale lahti kodeerimist';


--
-- Name: COLUMN taralog.isikukood; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.taralog.isikukood IS 'autenditud kasutaja riik ja isikukood';


--
-- Name: COLUMN taralog.eesnimi; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.taralog.eesnimi IS 'autenditud kasutaja eesnimi';


--
-- Name: COLUMN taralog.perenimi; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.taralog.perenimi IS 'autenditud kasutaja perekonnanimi';


--
-- Name: COLUMN taralog.err; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.taralog.err IS 'vea kood (vt logintara.py)';


--
-- Name: COLUMN taralog.request_url; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.taralog.request_url IS 'EISi URL, mille poole pöördudes suunati kasutaja autentima ja kuhu peale autentimist kasutaja tagasi suuname';


--
-- Name: COLUMN taralog.remote_addr; Type: COMMENT; Schema: public; Owner: eisik
--

COMMENT ON COLUMN public.taralog.remote_addr IS 'klient';


--
-- Name: taralog_id_seq; Type: SEQUENCE; Schema: public; Owner: eisik
--

CREATE SEQUENCE public.taralog_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.taralog_id_seq OWNER TO eisik;

--
-- Name: taralog_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: eisik
--

ALTER SEQUENCE public.taralog_id_seq OWNED BY public.taralog.id;


--
-- Name: haridlog id; Type: DEFAULT; Schema: public; Owner: eisik
--

ALTER TABLE ONLY public.haridlog ALTER COLUMN id SET DEFAULT nextval('public.haridlog_id_seq'::regclass);


--
-- Name: logi id; Type: DEFAULT; Schema: public; Owner: eisik
--

ALTER TABLE ONLY public.logi ALTER COLUMN id SET DEFAULT nextval('public.logi_id_seq'::regclass);


--
-- Name: logi_adapter id; Type: DEFAULT; Schema: public; Owner: eisik
--

ALTER TABLE ONLY public.logi_adapter ALTER COLUMN id SET DEFAULT nextval('public.logi_adapter_id_seq'::regclass);


--
-- Name: ltest id; Type: DEFAULT; Schema: public; Owner: eisik
--

ALTER TABLE ONLY public.ltest ALTER COLUMN id SET DEFAULT nextval('public.ltest_id_seq'::regclass);


--
-- Name: taralog id; Type: DEFAULT; Schema: public; Owner: eisik
--

ALTER TABLE ONLY public.taralog ALTER COLUMN id SET DEFAULT nextval('public.taralog_id_seq'::regclass);


--
-- Name: haridlog haridlog_pkey; Type: CONSTRAINT; Schema: public; Owner: eisik
--

ALTER TABLE ONLY public.haridlog
    ADD CONSTRAINT haridlog_pkey PRIMARY KEY (id);


--
-- Name: logi_adapter logi_adapter_pkey; Type: CONSTRAINT; Schema: public; Owner: eisik
--

ALTER TABLE ONLY public.logi_adapter
    ADD CONSTRAINT logi_adapter_pkey PRIMARY KEY (id);


--
-- Name: logi logi_pkey; Type: CONSTRAINT; Schema: public; Owner: eisik
--

ALTER TABLE ONLY public.logi
    ADD CONSTRAINT logi_pkey PRIMARY KEY (id);


--
-- Name: ltest ltest_pkey; Type: CONSTRAINT; Schema: public; Owner: eisik
--

ALTER TABLE ONLY public.ltest
    ADD CONSTRAINT ltest_pkey PRIMARY KEY (id);


--
-- Name: taralog taralog_pkey; Type: CONSTRAINT; Schema: public; Owner: eisik
--

ALTER TABLE ONLY public.taralog
    ADD CONSTRAINT taralog_pkey PRIMARY KEY (id);


--
-- Name: ix_haridlog_aut_aeg; Type: INDEX; Schema: public; Owner: eisik
--

CREATE INDEX ix_haridlog_aut_aeg ON public.haridlog USING btree (aut_aeg);


--
-- Name: ix_haridlog_nonce; Type: INDEX; Schema: public; Owner: eisik
--

CREATE INDEX ix_haridlog_nonce ON public.haridlog USING btree (nonce);


--
-- Name: ix_haridlog_state; Type: INDEX; Schema: public; Owner: eisik
--

CREATE INDEX ix_haridlog_state ON public.haridlog USING btree (state);


--
-- Name: ix_logi_adapter_aeg; Type: INDEX; Schema: public; Owner: eisik
--

CREATE INDEX ix_logi_adapter_aeg ON public.logi_adapter USING btree (aeg);


--
-- Name: ix_logi_aeg; Type: INDEX; Schema: public; Owner: eisik
--

CREATE INDEX ix_logi_aeg ON public.logi USING btree (aeg);


--
-- Name: ix_logi_isikukood; Type: INDEX; Schema: public; Owner: eisik
--

CREATE INDEX ix_logi_isikukood ON public.logi USING btree (isikukood);


--
-- Name: ix_logi_path; Type: INDEX; Schema: public; Owner: eisik
--

CREATE INDEX ix_logi_path ON public.logi USING btree (path);


--
-- Name: ix_logi_request_id; Type: INDEX; Schema: public; Owner: eisik
--

CREATE INDEX ix_logi_request_id ON public.logi USING btree (request_id);


--
-- Name: ix_logi_tyyp; Type: INDEX; Schema: public; Owner: eisik
--

CREATE INDEX ix_logi_tyyp ON public.logi USING btree (tyyp);


--
-- Name: ix_logi_uuid; Type: INDEX; Schema: public; Owner: eisik
--

CREATE INDEX ix_logi_uuid ON public.logi USING btree (uuid);


--
-- Name: ix_ltest_aeg; Type: INDEX; Schema: public; Owner: eisik
--

CREATE INDEX ix_ltest_aeg ON public.ltest USING btree (aeg);


--
-- Name: ix_taralog_aut_aeg; Type: INDEX; Schema: public; Owner: eisik
--

CREATE INDEX ix_taralog_aut_aeg ON public.taralog USING btree (aut_aeg);


--
-- Name: ix_taralog_nonce; Type: INDEX; Schema: public; Owner: eisik
--

CREATE INDEX ix_taralog_nonce ON public.taralog USING btree (nonce);


--
-- Name: ix_taralog_state; Type: INDEX; Schema: public; Owner: eisik
--

CREATE INDEX ix_taralog_state ON public.taralog USING btree (state);


--
-- PostgreSQL database dump complete
--

