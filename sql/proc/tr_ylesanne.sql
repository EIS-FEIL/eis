CREATE OR REPLACE FUNCTION tr_ylesanne_kasutusmaar() RETURNS TRIGGER AS $tr_ylesanne$
DECLARE ID1 INTEGER;
DECLARE ID2 INTEGER;
DECLARE uus_kasutusmaar INTEGER;
DECLARE uus_lukus INTEGER;
BEGIN
-- valitudylesande muutmisel arvutatakse valitud ylesande kasutusmäär
-- ja pannakse ylesanne lukku, kui see on kasutusel
IF (TG_OP = 'DELETE') THEN
   ID1 := OLD.YLESANNE_ID;
   ID2 := NULL;
ELSIF (TG_OP = 'UPDATE') THEN
   ID1 := OLD.YLESANNE_ID;
   ID2 := NEW.YLESANNE_ID;   
ELSIF (TG_OP = 'INSERT') THEN
   ID1 := NEW.YLESANNE_ID;
   ID2 := NULL;
END IF;

SELECT count(*) INTO uus_kasutusmaar FROM valitudylesanne WHERE ylesanne_id=ID1;
UPDATE ylesanne SET kasutusmaar=uus_kasutusmaar
	WHERE id=ID1 AND (kasutusmaar IS NULL OR kasutusmaar!=uus_kasutusmaar);

SELECT max(k.lukus) INTO uus_lukus FROM valitudylesanne vy, komplekt k
       WHERE vy.ylesanne_id=ID1
       AND vy.komplekt_id=k.id;
UPDATE ylesanne SET lukus=uus_lukus 
       WHERE id=ID1 AND COALESCE(lukus,0)!=COALESCE(uus_lukus,0);

IF ID2 IS NOT NULL AND (ID1 IS NULL OR ID1!=ID2) THEN
    SELECT count(*) INTO uus_kasutusmaar FROM valitudylesanne WHERE ylesanne_id=ID2;
    UPDATE ylesanne SET kasutusmaar=uus_kasutusmaar
	   WHERE id=ID2 AND (kasutusmaar IS NULL OR kasutusmaar!=uus_kasutusmaar);

    SELECT max(k.lukus) INTO uus_lukus FROM valitudylesanne vy, komplekt k
       WHERE vy.ylesanne_id=ID2
       AND vy.komplekt_id=k.id;
    UPDATE ylesanne SET lukus=uus_lukus 
       WHERE id=ID2 AND COALESCE(lukus,0)!=COALESCE(uus_lukus,0);
END IF;
RETURN NULL;
END;
$tr_ylesanne$ LANGUAGE plpgsql;

CREATE TRIGGER tr_ylesanne
AFTER INSERT OR UPDATE OR DELETE ON valitudylesanne
  FOR EACH ROW EXECUTE PROCEDURE tr_ylesanne_kasutusmaar();
