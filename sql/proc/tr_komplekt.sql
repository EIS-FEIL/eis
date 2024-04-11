CREATE OR REPLACE FUNCTION tr_komplekt_lukus() RETURNS TRIGGER AS $tr_komplekt$
DECLARE K_ID INTEGER;
BEGIN
-- komplekti kirje muutmisel muudetakse ylesannete lukustus
-- komplekti lukustus on varem määratud Komplekt.set_lukus()
K_ID := NULL;
IF TG_OP = 'UPDATE' THEN
   IF OLD.lukus IS NULL AND NEW.lukus IS NOT NULL OR
      OLD.lukus IS NOT NULL AND NEW.lukus IS NULL OR 
      OLD.lukus <> NEW.lukus THEN
     K_ID := NEW.ID;
   END IF;
ELSIF TG_OP = 'INSERT' THEN 
     K_ID := NEW.ID;
ELSIF TG_OP = 'DELETE' THEN 
     K_ID := OLD.ID;
END IF;

IF K_ID IS NOT NULL THEN
   UPDATE ylesanne SET lukus=
       (SELECT max(k.lukus) FROM valitudylesanne vy, komplekt k
       WHERE vy.ylesanne_id=ylesanne.id 
       AND vy.komplekt_id=k.id)
       WHERE ylesanne.id IN 
       (SELECT ylesanne_id FROM valitudylesanne 
       WHERE komplekt_id=K_ID);
END IF;
RETURN NULL;
END;
$tr_komplekt$ LANGUAGE plpgsql;

-- DROP TRIGGER tr_komplekt ON komplekt;
CREATE TRIGGER tr_komplekt
AFTER INSERT OR UPDATE OR DELETE ON komplekt
  FOR EACH ROW EXECUTE PROCEDURE tr_komplekt_lukus();
