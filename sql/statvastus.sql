DROP VIEW statvastus CASCADE;

-- EISi ülesandetüüpide mudel on loodud QTI standardi eeskujul, 
-- kus on lisaks skalaarsetele vastustele ka paarid (suunatud või suunamata).
-- Harno statistikud eelistavad andmeid lihtsustatud kujul, 
-- kus esimene paariline on küsimuse rollis ja teine paariline on skalaarse vastuse rollis.
-- Paarina kuvatakse ainult suunamata paariga vastused (seostamine).
-- Vaade statvastus projitseerib QTI põhise andmemudeli vastavaks statistikute eelistustele.
-- Allpool: eripaar - selline paar, mida statistikutele näidatakse mitme eraldi skalaarse küsimusena
CREATE OR REPLACE VIEW public.statvastus AS
SELECT 
    CASE WHEN vk.kood IS NOT NULL THEN kysimus.kood||':'||vk.kood
	     ELSE kysimus.kood
    END AS kood1, -- küsimuse kood, eripaari korral koos esimese valiku koodiga
    CASE WHEN vk.id IS NULL THEN kysimus.selgitus
	     ELSE vk.selgitus
	END AS selgitus1, -- küsimuse selgitus või eripaari esimese valiku selgitus
	kysimus.seq AS kysimus_seq, -- küsimuse jrk 
	vk.seq AS valik1_seq, -- eripaari korral esimese valiku jrk
	CASE WHEN ks.id IS NULL THEN 0
	     ELSE ks.toorpunktid 
    END AS ks_punktid, -- antud vastuse punktid (ES-2539: vastamata jätmisel korral soovitakse alati 0)
	CASE WHEN vv.paarina=false THEN COALESCE((
		    SELECT sum(ksx.toorpunktid) FROM kvsisu ksx WHERE ksx.kysimusevastus_id=kv.id 
		    AND (vv.vahetada=true AND ksx.kood2=vk.kood OR vv.vahetada=false AND ksx.kood1=vk.kood)
	       ), 0)
	     ELSE kv.toorpunktid
    END AS svpunktid, -- eripaari korral eripaari punktid, muidu küsimuse punktid
	kv.toorpunktid as kv_punktid,
    CASE WHEN vk.id IS NULL THEN coalesce(tulemus.max_pallid, tulemus.max_pallid_arv)
	     ELSE vk.max_pallid
    END AS max_punktid, -- max toorpunktid
	CASE WHEN ks.oige=2 THEN 1
	     WHEN ks.oige=1 THEN 0.5
         WHEN ks.id IS NULL OR ks.oige IS NOT NULL OR kv.vastuseta=true THEN 0
         ELSE NULL
    END AS oige, -- vastuse õigsus (1 - õige; 0,5 - osaliselt õige; 0 - vale või loetamatu või vastamata)
    CASE WHEN vv.paarina=true THEN ks.kood1||'-'||ks.kood2
	     WHEN v2.kood IS NOT NULL AND vv.vahetada THEN ks.kood1 
         WHEN v2.kood IS NOT NULL THEN ks.kood2 
	     WHEN v1.kood IS NOT NULL THEN ks.kood1 
		 ELSE COALESCE(ks.sisu,'')||COALESCE(ks.koordinaat,'')||COALESCE(ks.kujund,'')
	END AS vastus, -- vastus või eripaari teise valiku kood
    CASE WHEN vv.paarina=true THEN v1.selgitus||'-'||v2.selgitus
	     WHEN v2.kood IS NOT NULL AND vv.vahetada THEN v1.selgitus
         WHEN v2.kood IS NOT NULL THEN v2.selgitus
	     WHEN v1.kood IS NOT NULL THEN v1.selgitus
         WHEN vv.sisujarjestus=true THEN 
            (SELECT cast(string_agg(v1jrk.selgitus, ';') as character varying(255)) FROM valik v1jrk
             JOIN (SELECT regexp_split_to_table(ks.sisu, E';') AS kood) x ON x.kood=v1jrk.kood
             WHERE v1jrk.kysimus_id=vv.valik1_kysimus_id)
         ELSE hm.selgitus 
    END AS selgitus,
	maxv.seq AS kvsisu_seq, -- vastuse jrk
--v1.id v1_id, v2.id v2_id, vv.paarina, v1.kood v1_kood, v2.kood v2_kood, vk.id vk_id, vv.vahetada vv_vahetada, vk.kood vk_kood, ks.svseq,
    ks.id AS kvsisu_id, -- kvsisu.id
	kysimus.id kysimus_id, -- kysimus.id
    kv.id AS kysimusevastus_id, -- kysimusevastus.id
    kv.ylesandevastus_id, -- ylesandevastus.id						 
	COALESCE(vk.max_vastus, kysimus.max_vastus, kysimus.max_vastus_arv) AS max_vastus, -- kood1 max vastuste arv	
    vk.id AS valik1_id,
    CASE WHEN vv.paarina=false AND vv.vahetada THEN v1.id
	     ELSE v2.id
    END AS valik2_id,
    yv.valitudylesanne_id,
	yv.testiylesanne_id,
    tulemus.id tulemus_id,
    tulemus.ylesanne_id,
    s.id sooritus_id,
	s.sooritaja_id,
	s.toimumisaeg_id,
	s.testiosa_id,
	s.testikoht_id,
    s.staatus
FROM kysimus
     JOIN tulemus ON tulemus.id = kysimus.tulemus_id
     JOIN kysimusevastus kv ON kv.kysimus_id = kysimus.id AND kv.sisestus=1
	 JOIN ylesandevastus yv ON yv.id=kv.ylesandevastus_id
	 JOIN sooritus s ON s.id=yv.sooritus_id
	 LEFT JOIN valikvastus vv ON vv.tulemus_id = tulemus.id
	 LEFT JOIN valik vk ON vv.paarina = false AND 
				(vv.vahetada = true AND vk.kysimus_id = vv.valik2_kysimus_id OR
				 vv.vahetada = false AND vk.kysimus_id = vv.valik1_kysimus_id)
     JOIN (SELECT generate_series(0, 1000) as seq) maxv 
	       ON maxv.seq < CASE WHEN vv.analyys1=true THEN 1 ELSE coalesce(vk.max_vastus, kysimus.max_vastus, kysimus.max_vastus_arv, 1) END
	    -- järjestamine, järjestamine pildil: tahame ainult 1 rida
        AND (vv.sisujarjestus IS NULL OR vv.sisujarjestus=false OR maxv.seq=0)
		-- (kardinaalsus=ordered järgi ei saa, sest ka pangaga lynk on ordered)
        -- AND (tulemus.kardinaalsus NOT LIKE 'ordered%' OR maxv.seq=0)
     LEFT JOIN kvsisu ks ON ks.kysimusevastus_id = kv.id AND ks.analyysitav = true
        AND (vk.id IS NULL OR vv.vahetada = true AND vk.kood = ks.kood2 OR vv.vahetada = false AND vk.kood = ks.kood1)
        AND (vv.analyys1=true AND ks.svseq=-2  -- -2=SEQ_ANALYSIS
        OR ks.svseq = maxv.seq)
     LEFT JOIN valik v1 ON v1.kood = ks.kood1 AND v1.kysimus_id = vv.valik1_kysimus_id
	 LEFT JOIN valik v2 ON v2.kood = ks.kood2 AND v2.kysimus_id = vv.valik2_kysimus_id
	 LEFT JOIN hindamismaatriks hm ON hm.id = ks.hindamismaatriks_id
     WHERE (vv.statvastuses=true OR vv.id IS NULL)
        --AND (ks.id IS NULL OR COALESCE(vv.maatriks,1) = ks.maatriks)
        -- jätame välja mitte-paarina esitatavad paarvastused, mille kysimuse osa on ylesandest kustutatud
		AND (vk.id IS NOT NULL OR vv.paarina IS NULL OR vv.paarina=true)
        -- jätame välja puuduvad v1 ja v2
		AND (vv.valik1_kysimus_id IS NULL OR ks.kood1 IS NULL OR ks.kood1 = '' OR v1.id IS NOT NULL)
		AND (vv.valik2_kysimus_id IS NULL OR ks.kood2 IS NULL OR ks.kood2 = '' OR v2.id IS NOT NULL)
--and yv.id=12588 and kysimus.id=38747
;
GRANT ALL PRIVILEGES ON statvastus TO eisikud;
