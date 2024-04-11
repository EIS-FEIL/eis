CREATE OR REPLACE FUNCTION tr_testiosareg_algus() RETURNS TRIGGER AS $tr_testiosareg_algus$
BEGIN
  IF TG_OP = 'UPDATE' THEN
     IF (new.kavaaeg IS NULL and old.kavaaeg IS NULL  OR
         new.kavaaeg IS NOT NULL and old.kavaaeg IS NOT NULL AND new.kavaaeg = old.kavaaeg)
     THEN
        RETURN NULL;
     END IF;
  END IF;

  UPDATE testireg SET algus=
        (SELECT min(testiosareg.kavaaeg) FROM testiosareg WHERE testiosareg.testireg_id=testireg.id)
         WHERE testireg.id=new.testireg_id;

  RETURN NULL;
END;
$tr_testiosareg_algus$ LANGUAGE plpgsql;

CREATE TRIGGER tr_testiosareg_algus
AFTER INSERT OR UPDATE ON testiosareg
  FOR EACH ROW EXECUTE PROCEDURE tr_testiosareg_algus();
