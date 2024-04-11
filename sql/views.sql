-- osaoskuste tulemused
\i statvastus.sql

CREATE OR REPLACE VIEW v_alaosatulemused AS
SELECT 
s.sooritaja_id,
s.id sooritus_id,
a.id alatestisooritus_id,
s.testiosa_id,
a.alatest_id,
CASE WHEN a.id IS NOT NULL THEN a.pallid ELSE s.pallid END pallid,
CASE WHEN a.id IS NOT NULL THEN a.tulemus_protsent ELSE s.tulemus_protsent END tulemus_protsent,
CASE WHEN a.id IS NOT NULL THEN a.staatus ELSE s.staatus END staatus
FROM sooritus s
LEFT OUTER JOIN alatestisooritus a ON a.sooritus_id=s.id;

COMMENT ON COLUMN v_alaosatulemused.sooritaja_id IS 'testisoorituse id';
COMMENT ON COLUMN v_alaosatulemused.sooritus_id IS 'testiosasoorituse id';
COMMENT ON COLUMN v_alaosatulemused.alatestisooritus_id IS 'alatestisoorituse id (alatestideta testiosa korral NULL)';
COMMENT ON COLUMN v_alaosatulemused.testiosa_id IS 'testiosa id';
COMMENT ON COLUMN v_alaosatulemused.alatest_id IS 'alatesti id (alatestideta testiosa korral NULL)';
COMMENT ON COLUMN v_alaosatulemused.pallid IS 'alatesti pallid või alatestideta testiosa pallid';
COMMENT ON COLUMN v_alaosatulemused.tulemus_protsent IS 'alatesti tulemuse protsent või alatestideta testiosa tulemuse protsent';
COMMENT ON COLUMN v_alaosatulemused.staatus IS 'olek';

COMMENT ON view v_alaosatulemused IS 'sooritajate tulemused alatestide ja alatestideta testiosade kaupa';

