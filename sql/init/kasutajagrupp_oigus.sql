SELECT pg_catalog.set_config('search_path', 'public', false);
INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='abi';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='abimaterjalid';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='admin';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='aineopetaja';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='ametnikud';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='aruanded-erinevused';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='aruanded-kohateated';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='aruanded-labiviijad';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='aruanded-labiviijakaskkirjad';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='aruanded-labiviijateated';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='aruanded-nousolekud3';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='aruanded-osalemine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='aruanded-osaoskused';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='aruanded-prktulemused';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='aruanded-rvtunnistused';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='aruanded-sooritajatearv';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='aruanded-soorituskohad';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='aruanded-teated';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='aruanded-testisooritused';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='aruanded-testitulemused';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='aruanded-tugiisikud';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='aruanded-tulemused';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='aruanded-tulemusteteavitused';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='aruanded-tunnistused';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='aruanded-vaatlejateated';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='aruanded-vaided';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='avalikadmin';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='avtugi';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='avylesanded';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='caeeeltest';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='ekk-hindamine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='ekk-hindamine6';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='ekk-testid';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='ekk-testid-failid';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='ekk-testid-toimetamine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='ekk-testid-tolkimine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='eksaminandid';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='eksaminandid-ik';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='eksperthindamine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='ekspertryhmad';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='erivajadused';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='ettepanekud';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='ettepanemine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='failid';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='hindajamaaramine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='hindamisanalyys';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='intervjuu';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='juhendamine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='kasutajad';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='keskserver';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='khindamine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='kiirvalikud';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='klass';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='klassifikaatorid';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='kohad';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='kohteelvaade';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='konsultatsioonid';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='koolipsyh';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='korduvsooritatavus';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='korraldamine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='kparoolid';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='lahendamine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='lepingud';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='lglitsentsid';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='logi';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='logopeed';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='lopetamised';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='lukustlahti';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='minu';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='nimekirjad';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='nousolekud';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='olulineinfo';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='omanimekirjad';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='parandamine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='paroolid';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='piirkonnad';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='plangid';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='profiil';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='profiil-vaatleja';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='pslitsentsid';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='regamine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='regkontroll';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='rveksamid';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='sessioonid';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='shindamine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='sisestamine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='sisuavaldamine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='skannid';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='sooritamine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='srcedit';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='statistikaraportid';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='sysinfo';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='testhulgi';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='testiadmin';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='testid';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='testid-toimetamine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='testid-tolkimine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='testimiskorrad';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='testiroll';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='thindamine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='tkorddel';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='toimumisprotokoll';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='tookogumikud';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='toovaatamine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='tprotsisestus';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='tulemusteavaldamine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='tunnistused';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='ui-tolkimine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='vaided';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='vastusteanalyys';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='vastustevaljavote';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='yhisfailid';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='ylesanded';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='ylesanded-failid';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='ylesanded-markused';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='ylesanded-toimetamine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='ylesanded-tolkimine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='ylesandekogud';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='ylesandemall';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='ylesanderoll';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='ylesandetahemargid';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='ylesannelukustlahti';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='ylhulgi';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=1 AND o.nimi='ylkvaliteet';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=2 AND o.nimi='aruanded-erinevused';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=2 AND o.nimi='aruanded-labiviijad';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=2 AND o.nimi='aruanded-labiviijakaskkirjad';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=2 AND o.nimi='aruanded-nousolekud3';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=2 AND o.nimi='aruanded-osalemine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=2 AND o.nimi='aruanded-osaoskused';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=2 AND o.nimi='aruanded-testitulemused';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=2 AND o.nimi='aruanded-tulemused';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=2 AND o.nimi='aruanded-vaided';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 3
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=2 AND o.nimi='ekk-hindamine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=2 AND o.nimi='ekk-testid';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=2 AND o.nimi='hindamisanalyys';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 3
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=2 AND o.nimi='kasutajad';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 3
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=2 AND o.nimi='klassifikaatorid';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=2 AND o.nimi='konsultatsioonid';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=2 AND o.nimi='omanimekirjad';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=2 AND o.nimi='profiil';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 3
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=2 AND o.nimi='testid';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=2 AND o.nimi='testiroll';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=2 AND o.nimi='vastusteanalyys';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=2 AND o.nimi='yhisfailid';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=2 AND o.nimi='ylesanded';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=2 AND o.nimi='ylesandekogud';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=2 AND o.nimi='ylesanderoll';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=2 AND o.nimi='ylkvaliteet';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=3 AND o.nimi='yhisfailid';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=3 AND o.nimi='ylesanded';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=3 AND o.nimi='ylesanderoll';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 3
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=4 AND o.nimi='aruanded-erinevused';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 3
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=4 AND o.nimi='aruanded-kohateated';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 3
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=4 AND o.nimi='aruanded-labiviijad';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 3
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=4 AND o.nimi='aruanded-labiviijakaskkirjad';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 3
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=4 AND o.nimi='aruanded-osalemine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 3
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=4 AND o.nimi='aruanded-rvtunnistused';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 3
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=4 AND o.nimi='aruanded-soorituskohad';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 3
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=4 AND o.nimi='aruanded-testisooritused';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 3
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=4 AND o.nimi='aruanded-tulemused';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 3
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=4 AND o.nimi='aruanded-tunnistused';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 3
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=4 AND o.nimi='aruanded-vaatlejateated';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 3
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=4 AND o.nimi='aruanded-vaided';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 3
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=4 AND o.nimi='hindamisanalyys';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=4 AND o.nimi='statistikaraportid';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=4 AND o.nimi='tulemusteavaldamine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 2
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=4 AND o.nimi='tunnistused';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 3
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=4 AND o.nimi='vastusteanalyys';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 2
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=4 AND o.nimi='vastustevaljavote';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=5 AND o.nimi='avylesanded';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=5 AND o.nimi='ylesanded';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 3
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=6 AND o.nimi='ylesanded';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=6 AND o.nimi='ylesanded-markused';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 3
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=7 AND o.nimi='ylesanded';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=7 AND o.nimi='ylesanded-markused';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=7 AND o.nimi='ylesanded-toimetamine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=7 AND o.nimi='ylesandetahemargid';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 3
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=8 AND o.nimi='ylesanded';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=8 AND o.nimi='ylesanded-markused';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=8 AND o.nimi='ylesanded-tolkimine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=8 AND o.nimi='ylesandetahemargid';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 3
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=9 AND o.nimi='ylesanded';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=9 AND o.nimi='ylesanded-failid';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=9 AND o.nimi='ylesanded-markused';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=10 AND o.nimi='ekk-testid';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=10 AND o.nimi='konsultatsioonid';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=10 AND o.nimi='testid';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 3
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=10 AND o.nimi='vastusteanalyys';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=10 AND o.nimi='ylesanded';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 3
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=11 AND o.nimi='ekk-testid';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 3
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=11 AND o.nimi='vastusteanalyys';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 3
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=11 AND o.nimi='ylesanded';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 3
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=12 AND o.nimi='ekk-testid';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=12 AND o.nimi='ekk-testid-toimetamine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 3
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=12 AND o.nimi='ylesanded';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=12 AND o.nimi='ylesanded-markused';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=12 AND o.nimi='ylesanded-toimetamine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 3
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=13 AND o.nimi='ekk-testid';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=13 AND o.nimi='ekk-testid-tolkimine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 3
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=13 AND o.nimi='ylesanded';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=13 AND o.nimi='ylesanded-markused';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=13 AND o.nimi='ylesanded-tolkimine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 3
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=14 AND o.nimi='ekk-testid';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=14 AND o.nimi='ekk-testid-failid';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 3
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=14 AND o.nimi='ylesanded';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=14 AND o.nimi='ylesanded-failid';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=14 AND o.nimi='ylesanded-markused';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 3
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=15 AND o.nimi='avylesanded';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=15 AND o.nimi='ekk-testid';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=15 AND o.nimi='omanimekirjad';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=15 AND o.nimi='testid';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=15 AND o.nimi='thindamine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=16 AND o.nimi='aruanded-erinevused';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=16 AND o.nimi='aruanded-kohateated';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=16 AND o.nimi='aruanded-labiviijad';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=16 AND o.nimi='aruanded-labiviijakaskkirjad';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=16 AND o.nimi='aruanded-labiviijateated';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=16 AND o.nimi='aruanded-nousolekud3';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=16 AND o.nimi='aruanded-osalemine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=16 AND o.nimi='aruanded-osaoskused';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=16 AND o.nimi='aruanded-prktulemused';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=16 AND o.nimi='aruanded-sooritajatearv';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=16 AND o.nimi='aruanded-soorituskohad';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=16 AND o.nimi='aruanded-teated';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=16 AND o.nimi='aruanded-testisooritused';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=16 AND o.nimi='aruanded-testitulemused';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=16 AND o.nimi='aruanded-tugiisikud';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=16 AND o.nimi='aruanded-tulemused';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=16 AND o.nimi='aruanded-tulemusteteavitused';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=16 AND o.nimi='aruanded-tunnistused';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=16 AND o.nimi='aruanded-vaatlejateated';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=16 AND o.nimi='aruanded-vaided';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=16 AND o.nimi='ekk-hindamine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 3
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=16 AND o.nimi='ekk-testid';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=16 AND o.nimi='eksaminandid';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=16 AND o.nimi='eksaminandid-ik';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 3
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=16 AND o.nimi='eksperthindamine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 3
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=16 AND o.nimi='ekspertryhmad';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=16 AND o.nimi='erivajadused';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=16 AND o.nimi='hindajamaaramine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=16 AND o.nimi='hindamisanalyys';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=16 AND o.nimi='juhendamine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=16 AND o.nimi='kasutajad';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=16 AND o.nimi='kiirvalikud';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=16 AND o.nimi='kohad';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 2
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=16 AND o.nimi='kohteelvaade';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=16 AND o.nimi='konsultatsioonid';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=16 AND o.nimi='korraldamine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=16 AND o.nimi='kparoolid';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=16 AND o.nimi='lopetamised';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=16 AND o.nimi='parandamine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=16 AND o.nimi='piirkonnad';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=16 AND o.nimi='profiil';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=16 AND o.nimi='regamine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=16 AND o.nimi='regkontroll';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=16 AND o.nimi='sessioonid';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=16 AND o.nimi='sisestamine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=16 AND o.nimi='statistikaraportid';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=16 AND o.nimi='testimiskorrad';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=16 AND o.nimi='testiroll';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=16 AND o.nimi='tulemusteavaldamine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 2
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=16 AND o.nimi='tunnistused';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 3
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=16 AND o.nimi='vaided';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=16 AND o.nimi='vastusteanalyys';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=16 AND o.nimi='ylesanderoll';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=17 AND o.nimi='aruanded-prktulemused';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=17 AND o.nimi='aruanded-vaatlejateated';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 3
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=17 AND o.nimi='erivajadused';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=17 AND o.nimi='kasutajad';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 3
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=17 AND o.nimi='kiirvalikud';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=17 AND o.nimi='kohad';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=17 AND o.nimi='korraldamine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=17 AND o.nimi='piirkonnad';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 3
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=17 AND o.nimi='profiil';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=17 AND o.nimi='profiil-vaatleja';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 3
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=17 AND o.nimi='sessioonid';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 3
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=18 AND o.nimi='erivajadused';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=18 AND o.nimi='regamine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=19 AND o.nimi='ekk-hindamine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 3
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=19 AND o.nimi='eksperthindamine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=19 AND o.nimi='ekspertryhmad';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=19 AND o.nimi='hindajamaaramine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=19 AND o.nimi='juhendamine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 3
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=20 AND o.nimi='ekk-hindamine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=20 AND o.nimi='eksperthindamine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 3
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=20 AND o.nimi='ekspertryhmad';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=20 AND o.nimi='hindamisanalyys';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=20 AND o.nimi='vastusteanalyys';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=21 AND o.nimi='sisestamine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=22 AND o.nimi='parandamine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=22 AND o.nimi='sisestamine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=23 AND o.nimi='vaided';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=24 AND o.nimi='erivajadused';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 3
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=24 AND o.nimi='regamine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 4
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=25 AND o.nimi='avylesanded';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=25 AND o.nimi='klass';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=25 AND o.nimi='nimekirjad';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=25 AND o.nimi='omanimekirjad';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=25 AND o.nimi='testid';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=25 AND o.nimi='tookogumikud';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=25 AND o.nimi='ylesanded';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 3
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=26 AND o.nimi='abimaterjalid';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=26 AND o.nimi='avalikadmin';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 4
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=26 AND o.nimi='avylesanded';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=26 AND o.nimi='klass';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=26 AND o.nimi='nimekirjad';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=26 AND o.nimi='omanimekirjad';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=26 AND o.nimi='paroolid';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=26 AND o.nimi='profiil';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=26 AND o.nimi='testiadmin';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=26 AND o.nimi='testid';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=26 AND o.nimi='toimumisprotokoll';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 3
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=27 AND o.nimi='omanimekirjad';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=27 AND o.nimi='testiadmin';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 3
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=27 AND o.nimi='toimumisprotokoll';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=28 AND o.nimi='nousolekud';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 3
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=28 AND o.nimi='testiadmin';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 3
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=28 AND o.nimi='toimumisprotokoll';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=29 AND o.nimi='nousolekud';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=29 AND o.nimi='shindamine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 3
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=29 AND o.nimi='testiadmin';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 3
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=29 AND o.nimi='toimumisprotokoll';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=30 AND o.nimi='khindamine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=30 AND o.nimi='nousolekud';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=30 AND o.nimi='thindamine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=33 AND o.nimi='omanimekirjad';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=33 AND o.nimi='testid';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=33 AND o.nimi='thindamine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=35 AND o.nimi='nousolekud';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=35 AND o.nimi='shindamine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 3
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=35 AND o.nimi='testiadmin';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 3
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=35 AND o.nimi='toimumisprotokoll';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=36 AND o.nimi='intervjuu';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=36 AND o.nimi='nousolekud';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 3
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=36 AND o.nimi='testiadmin';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 3
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=36 AND o.nimi='toimumisprotokoll';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 3
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=38 AND o.nimi='testiadmin';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 3
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=38 AND o.nimi='toimumisprotokoll';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=39 AND o.nimi='yhisfailid';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=39 AND o.nimi='ylesanded';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=39 AND o.nimi='ylesanded-markused';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=39 AND o.nimi='ylesandetahemargid';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=40 AND o.nimi='intervjuu';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 3
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=40 AND o.nimi='khindamine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=40 AND o.nimi='nousolekud';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 3
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=40 AND o.nimi='shindamine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 3
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=40 AND o.nimi='testiadmin';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 3
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=40 AND o.nimi='toimumisprotokoll';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 1
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=41 AND o.nimi='ekk-hindamine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 1
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=41 AND o.nimi='ekk-testid';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 1
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=41 AND o.nimi='ylesanded';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=45 AND o.nimi='vaided';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=46 AND o.nimi='testiadmin';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=46 AND o.nimi='toimumisprotokoll';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 3
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=47 AND o.nimi='testiadmin';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=47 AND o.nimi='toimumisprotokoll';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=48 AND o.nimi='vaided';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=54 AND o.nimi='koolipsyh';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=54 AND o.nimi='omanimekirjad';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=54 AND o.nimi='testid';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=54 AND o.nimi='tookogumikud';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=54 AND o.nimi='ylesanded';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=55 AND o.nimi='plangid';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 3
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=56 AND o.nimi='abimaterjalid';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=56 AND o.nimi='avalikadmin';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 4
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=56 AND o.nimi='avylesanded';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=56 AND o.nimi='failid';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=56 AND o.nimi='kasutajad';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=56 AND o.nimi='klass';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=56 AND o.nimi='nimekirjad';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=56 AND o.nimi='omanimekirjad';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=56 AND o.nimi='paroolid';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=56 AND o.nimi='plangid';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=56 AND o.nimi='profiil';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=56 AND o.nimi='testiadmin';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=56 AND o.nimi='testid';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=56 AND o.nimi='toimumisprotokoll';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=56 AND o.nimi='tookogumikud';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 3
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=57 AND o.nimi='toimumisprotokoll';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=57 AND o.nimi='tprotsisestus';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 3
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=58 AND o.nimi='failid';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=59 AND o.nimi='aineopetaja';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=60 AND o.nimi='srcedit';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=61 AND o.nimi='pslitsentsid';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=62 AND o.nimi='failid';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 3
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=63 AND o.nimi='testid';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 3
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=65 AND o.nimi='ekk-testid';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=65 AND o.nimi='korraldamine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=65 AND o.nimi='regamine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=65 AND o.nimi='testimiskorrad';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=66 AND o.nimi='ui-tolkimine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=67 AND o.nimi='logopeed';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=67 AND o.nimi='omanimekirjad';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=67 AND o.nimi='testid';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=67 AND o.nimi='tookogumikud';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=67 AND o.nimi='ylesanded';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=68 AND o.nimi='lglitsentsid';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 2
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=69 AND o.nimi='vastustevaljavote';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 1
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=70 AND o.nimi='toovaatamine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=71 AND o.nimi='sisuavaldamine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=72 AND o.nimi='ekk-hindamine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=72 AND o.nimi='ekk-testid';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=72 AND o.nimi='eksperthindamine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=72 AND o.nimi='hindajamaaramine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=72 AND o.nimi='hindamisanalyys';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=72 AND o.nimi='korraldamine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=72 AND o.nimi='testimiskorrad';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=72 AND o.nimi='testiroll';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=72 AND o.nimi='vastusteanalyys';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=72 AND o.nimi='ylesanded';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=72 AND o.nimi='ylesanderoll';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=73 AND o.nimi='ekk-hindamine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 3
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=73 AND o.nimi='eksperthindamine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=73 AND o.nimi='ekspertryhmad';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=73 AND o.nimi='hindajamaaramine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=73 AND o.nimi='juhendamine';

INSERT INTO kasutajagrupp_oigus (creator, created, modifier, modified,
 kasutajagrupp_id, kasutajaoigus_id, nimi, grupp_tyyp, grupp_staatus, bitimask) 
 SELECT 'ADMIN', current_timestamp, 'ADMIN', current_timestamp,
 g.id, o.id, o.nimi, g.tyyp, g.staatus, 31
 FROM kasutajagrupp g, kasutajaoigus o 
 WHERE g.id=74 AND o.nimi='sysinfo';

