
CREATE ROLE eisik WITH
	LOGIN
	SUPERUSER
	CREATEDB
	CREATEROLE
	INHERIT
	REPLICATION
	CONNECTION LIMIT -1
	PASSWORD 'eisik';

CREATE DATABASE eisdb1
    WITH
    OWNER = eisik
    ENCODING = 'UTF8'
    LC_COLLATE = 'Estonian_Estonia.1257'
    LC_CTYPE = 'Estonian_Estonia.1257'
    LOCALE_PROVIDER = 'libc'
    CONNECTION LIMIT = -1
    IS_TEMPLATE = False;

CREATE DATABASE eisdb1log
    WITH
    OWNER = eisik
    ENCODING = 'UTF8'
    LC_COLLATE = 'Estonian_Estonia.1257'
    LC_CTYPE = 'Estonian_Estonia.1257'
    LOCALE_PROVIDER = 'libc'
    CONNECTION LIMIT = -1
    IS_TEMPLATE = False;

CREATE DATABASE eisdb1sess
    WITH
    OWNER = eisik
    ENCODING = 'UTF8'
    LC_COLLATE = 'Estonian_Estonia.1257'
    LC_CTYPE = 'Estonian_Estonia.1257'
    LOCALE_PROVIDER = 'libc'
    CONNECTION LIMIT = -1
    IS_TEMPLATE = False;
