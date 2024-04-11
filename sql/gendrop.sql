select 'DROP TABLE '||table_name||' CASCADE;' from information_schema.tables where table_schema='public';
select 'DROP SEQUENCE '||sequence_name||' CASCADE;' from information_schema.sequences where sequence_schema='public';
select 'DROP SCHEMA plank CASCADE;';
select 'CREATE SCHEMA plank;';

