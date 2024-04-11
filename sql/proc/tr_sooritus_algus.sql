CREATE OR REPLACE FUNCTION tr_sooritus_algus() RETURNS TRIGGER AS $tr_sooritus_algus$
BEGIN
  IF TG_OP = 'UPDATE' THEN
     IF (new.kavaaeg IS NULL and old.kavaaeg IS NULL  OR
         new.kavaaeg IS NOT NULL and old.kavaaeg IS NOT NULL AND new.kavaaeg = old.kavaaeg)
     THEN
        RETURN NULL;
     END IF;
  END IF;

  UPDATE sooritaja SET algus=
        (SELECT min(sooritus.kavaaeg) FROM sooritus WHERE sooritus.sooritaja_id=sooritaja.id)
         WHERE sooritaja.id=new.sooritaja_id;

  RETURN NULL;
END;
$tr_sooritus_algus$ LANGUAGE plpgsql;

CREATE TRIGGER tr_sooritus_algus
AFTER INSERT OR UPDATE ON sooritus
  FOR EACH ROW EXECUTE PROCEDURE tr_sooritus_algus();
