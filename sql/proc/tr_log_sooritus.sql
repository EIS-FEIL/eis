CREATE OR REPLACE FUNCTION tr_log_sooritus() RETURNS TRIGGER AS $tr_log_sooritus$
BEGIN
IF COALESCE(old.staatus,0) <> COALESCE(new.staatus,0)
OR COALESCE(old.hindamine_staatus,0) <> COALESCE(new.hindamine_staatus,0)
OR COALESCE(old.pallid,0) <> COALESCE(new.pallid,0)
OR COALESCE(old.pallid_arvuti,0) <> COALESCE(new.pallid_arvuti,0)
OR COALESCE(old.pallid_kasitsi,0) <> COALESCE(new.pallid_kasitsi,0)
OR COALESCE(old.tulemus_protsent,0) <> COALESCE(new.tulemus_protsent,0)
OR old.ylesanneteta_tulemus <> new.ylesanneteta_tulemus
THEN
  INSERT INTO log_sooritus
  (id, modified, modifier, staatus, hindamine_staatus,
  pallid, pallid_arvuti, pallid_kasitsi,
  tulemus_protsent, ylesanneteta_tulemus, new_pallid)
  VALUES
  (new.id, new.modified, new.modifier, old.staatus, old.hindamine_staatus,
  old.pallid, old.pallid_arvuti, old.pallid_kasitsi,
  old.tulemus_protsent, old.ylesanneteta_tulemus, new.pallid);
END IF;
RETURN NULL;
END;
$tr_log_sooritus$ LANGUAGE plpgsql;

CREATE TRIGGER tr_log_sooritus
AFTER UPDATE ON sooritus
  FOR EACH ROW EXECUTE PROCEDURE tr_log_sooritus();
