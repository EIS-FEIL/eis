CREATE OR REPLACE FUNCTION html_resp(html character varying) RETURNS character varying AS
$BODY$
BEGIN
-- funktsioon kireva tekstina antud kysimuse vastuse standardiseerimiseks
-- eemaldatakse tyhikud jms (tyhik jääb alles ainult "class=" ees)
-- eemaldatakse style atribuut (eeldatavasti ainus atribuut on class)
-- eemaldatakse sildid <span>, <div> ja <p>
RETURN
  regexp_replace(
  regexp_replace(
  regexp_replace(
  regexp_replace(
  regexp_replace(
  regexp_replace(
  html,
  '\s|\t\|\n|\r|&nbsp;', ' ', 'g'), 
  '(<[^>]+) style="[^"]*"', '\1', 'g'),
  '<span>|</span>|<span/>|<div>|</div>|<div/>|<p>|</p>|<p/>', ' ', 'g'),
  ' class=', '_class=', 'g'),
  ' +', '', 'g'),
  '_class=', ' class=', 'g');
END;
$BODY$
LANGUAGE plpgsql VOLATILE;
