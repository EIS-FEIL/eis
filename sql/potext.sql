
CREATE TABLE potext (
    created timestamp without time zone NOT NULL,
    modified timestamp without time zone NOT NULL,
    creator character varying(25) NOT NULL,
    modifier character varying(25) NOT NULL,
    id integer NOT NULL,
    msgid character varying(1024),
    msgstr character varying(1024),
    lang character varying(2)
);
CREATE UNIQUE INDEX ix_potext ON potext USING btree (lang, msgid);
CREATE SEQUENCE potext_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE potext_id_seq OWNER TO eisik;
ALTER SEQUENCE potext_id_seq OWNED BY potext.id;
ALTER TABLE ONLY potext ALTER COLUMN id SET DEFAULT nextval('potext_id_seq'::regclass);
ALTER TABLE ONLY potext
    ADD CONSTRAINT potext_pkey PRIMARY KEY (id);
