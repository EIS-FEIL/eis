-- $Id: comments.sql 2517 2011-12-14 16:58:37Z eeahtkeld $
-- Kommentaaride erandid, mis ei kajastu Elixiri klassides olevates kommentaarides

COMMENT ON TABLE beaker_cache IS 'Kasutajaseansid';
COMMENT ON COLUMN beaker_cache.namespace IS 'seansi identifikaator';
COMMENT ON COLUMN beaker_cache.accessed IS 'viimase aktiivsuse aeg';
COMMENT ON COLUMN beaker_cache.created IS 'seansi loomise aeg';
COMMENT ON COLUMN beaker_cache.data IS 'seansi andmed';
COMMENT ON COLUMN beaker_cache.kasutaja_id IS 'viide kasutajale';
COMMENT ON COLUMN beaker_cache.autentimine IS 'autentimisviis';
COMMENT ON COLUMN beaker_cache.kehtetu IS 'kas seanss on juba kehtetu';
COMMENT ON COLUMN beaker_cache.remote_addr IS 'kasutaja kliendi host';
COMMENT ON COLUMN beaker_cache.app IS 'rakendus';

COMMENT ON COLUMN klassifikaator.ylem_kood IS 'viide ülemklassifikaatorile (klassifikaatorite hierarhia korral)';
COMMENT ON COLUMN klrida.klassifikaator_kood IS 'viide klassifikaatorile, mille väärtust kirje kirjeldab';

COMMENT ON COLUMN piirkond_kord.testimiskord_id IS 'viide testimiskorrale';
COMMENT ON COLUMN piirkond_kord.piirkond_id IS 'viide piirkonnale';
COMMENT ON TABLE piirkond_kord IS 'Piirkonnad, kus testimiskord läbi viiakse';

COMMENT ON COLUMN sisuobjekt.row_type IS 'sisuobjekti tüüp: b - taustobjekt; g - lohistatav pilt; m - multimeedia';

COMMENT ON COLUMN testimiskord_kiirvalik.testimiskord_id IS 'viide testimiskorrale';
COMMENT ON COLUMN testimiskord_kiirvalik.kiirvalik_id IS 'viide kiirvalikule';
COMMENT ON TABLE testimiskord_kiirvalik IS 'Kiirvalikud, kuhu testimiskord kuulub';


COMMENT ON COLUMN toimumisaeg_komplekt.komplekt_id IS 'viide ülesandekomplektile';
COMMENT ON COLUMN toimumisaeg_komplekt.toimumisaeg_id IS 'viide toimumisajale';
COMMENT ON TABLE toimumisaeg_komplekt IS 'Ülesandekomplektid, mis on antud toimumisajal kasutusel';

COMMENT ON COLUMN valik.row_type IS 'valiku tüüp: h - piirkond pildil; NULL - tekst';

COMMENT ON COLUMN ylesandefail.row_type IS 'faili tüüp: a - ülesande fail; s - ülesande lahenduse fail; o - ülesande lähtematerjal';
