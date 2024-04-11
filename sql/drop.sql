select 'DROP TABLE '||table_name||';' from information_schema.tables where table_schema='public';

select 'DROP SEQUENCE '||sequence_name||';' from information_schema.sequences where sequence_schema='public';

