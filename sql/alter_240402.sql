CREATE TABLE public.seade (
    created timestamp without time zone NOT NULL,
    modified timestamp without time zone NOT NULL,
    creator character varying(50) NOT NULL,
    modifier character varying(50) NOT NULL,
    id integer NOT NULL,
    key character varying(50),
    svalue character varying(50),
    nvalue integer
);
ALTER TABLE public.seade OWNER TO eisik;
CREATE SEQUENCE public.seade_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public.seade_id_seq OWNER TO eisik;
ALTER SEQUENCE public.seade_id_seq OWNED BY public.seade.id;
ALTER TABLE ONLY public.seade ALTER COLUMN id SET DEFAULT nextval('public.seade_id_seq'::regclass);
ALTER TABLE ONLY public.seade
    ADD CONSTRAINT seade_pkey PRIMARY KEY (id);

\i grant.sql

INSERT INTO seade (created, modified, creator, modifier, key, nvalue)
   VALUES (current_timestamp, current_timestamp, 'ADMIN', 'ADMIN', 'ksm.luba.hindaja', 0);
INSERT INTO seade (created, modified, creator, modifier, key, nvalue)
   VALUES (current_timestamp, current_timestamp, 'ADMIN', 'ADMIN', 'ksm.luba.sooritaja', 0);

