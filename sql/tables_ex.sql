CREATE TABLE log_sooritus (
    id integer NOT NULL,
    db_modified timestamp without time zone not null default current_timestamp,
    modified timestamp without time zone NOT NULL,
    modifier character varying(11) NOT NULL,
    staatus integer NOT NULL,
    hindamine_staatus integer DEFAULT 0 NOT NULL,
    pallid double precision,
    pallid_arvuti double precision,
    pallid_kasitsi double precision,
    tulemus_protsent double precision,
    ylesanneteta_tulemus boolean,
    new_pallid double precision
);

