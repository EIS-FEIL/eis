-- mediaani arvutamine PostgreSQL < v9.4 korral
-- alates PostgreSQL v9.4 kasuta selle asemel percentile_cont(0.5), mis on kiirem
CREATE OR REPLACE FUNCTION _final_median(double precision[])
   RETURNS double precision AS
$$
   SELECT AVG(val)
   FROM (
     SELECT val
     FROM unnest($1) val
     ORDER BY 1
     LIMIT  2 - MOD(array_upper($1, 1), 2)
     OFFSET CEIL(array_upper($1, 1) / 2.0) - 1
   ) sub;
$$
LANGUAGE 'sql' IMMUTABLE;
 
CREATE AGGREGATE median(double precision) (
  SFUNC=array_append,
  STYPE=double precision[],
  FINALFUNC=_final_median,
  INITCOND='{}'
);
