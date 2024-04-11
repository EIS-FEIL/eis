CREATE OR REPLACE FUNCTION lang_sort(lang character varying) RETURNS integer AS
$BODY$
BEGIN 
  IF lang = 'et' THEN
     RETURN 1;
  ELSIF lang = 'ru' THEN
     RETURN 2;
  ELSIF lang = 'en' THEN
     RETURN 3;
  ELSIF lang = 'de' THEN
     RETURN 4;
  ELSIF lang = 'fr' THEN
     RETURN 5;
  END IF;
  RETURN NULL;
END;
$BODY$
LANGUAGE plpgsql VOLATILE;
