% if c.testiliik in (const.TESTILIIK_RIIGIEKSAM, const.TESTILIIK_RV):
<% 
   synnikoht = synniriik = None
   oppimisaeg = None
   rahvus = None
   eesnimi_ru = None
   perenimi_ru = None
   on_rv = on_synnikoht = on_synniriik = on_rahvus = on_ru = False

   # kui on vaja lisavälju, siis leiame nende väärtused 
   for rcd in c.sooritajad:
       test = rcd.test
       if test.testiliik_kood != const.TESTILIIK_RV:
          continue
       if test.aine_kood == const.AINE_DE:
          on_rv = on_synniriik = True
          if not synniriik and rcd.synnikoht_kodakond_kood:
             synniriik = rcd.synnikoht_kodakond_kood
       if test.aine_kood == const.AINE_RU:
          on_rv = on_ru = True
          eesnimi_ru = eesnimi_ru or rcd.eesnimi_ru
          perenimi_ru = perenimi_ru or rcd.perenimi_ru
       if test.aine_kood == const.AINE_FR:
          on_rv = on_rahvus = on_synnikoht = True
          rahvus = rahvus or rcd.rahvus_kood
          if not synnikoht:
             synnikoht = rcd.synnikoht
       if test.aine_kood == const.AINE_EN:
          on_rv = True
  
   # kui andmeid polnud, siis otsime varasemast
   def leia_varasem(field):
        q = model.SessionR.query(field, model.Sooritaja.id).\
            filter_by(kasutaja_id=c.kasutaja.id).\
            filter(field!=None).\
            order_by(model.sa.desc(model.Sooritaja.id))
        for value, id in q.all():
            return value

   if on_synniriik and not synniriik:
      synniriik = leia_varasem(model.Sooritaja.synnikoht_kodakond_kood)
   if on_synnikoht and not synnikoht:
      synnikoht = leia_varasem(model.Sooritaja.synnikoht)  
   if on_ru and not eesnimi_ru:
      eesnimi_ru = leia_varasem(model.Sooritaja.eesnimi_ru)
   if on_ru and not perenimi_ru:
      perenimi_ru = leia_varasem(model.Sooritaja.perenimi_ru)
   if on_rahvus and not rahvus:
      rahvus = leia_varasem(model.Sooritaja.rahvus_kood)
%>

% if on_synniriik or on_synnikoht or on_rahvus or on_ru:

## - kõik saksa keele eksamid lisaväli sünniriik
## - lisaandmed vene keele valiku korral: ees- ja perekonnanimi vene keeles;
## - lisaandmed prantsuse keele valiku korral: sünnikoht, rahvus.

<h2>${_("Lisaandmed rahvusvahelise võõrkeeleeksami valiku puhul")}</h2>
${h.rqexp()}
<div class="form-wrapper mb-3">
  % if on_synniriik:
  <div class="form-group row">  
    ${h.flb3(_("Sünnikoha riik"),'dsynnikoht_kood', rq=True)}
    <div class="col-md-9" id="dsynnikoht_kood">
      ## synnikohaks valitakse riik
      ${h.select('f_synnikoht_kodakond_kood', synniriik,
      c.opt.klread_kood('KODAKOND', vaikimisi=synniriik),
      empty=True)}
    </div>
  </div>
  % endif

  % if on_synnikoht:
  ## vajadusel päritakse sooritaja synnikoht RRist
  <% c.user.check_synnikoht(c.kasutaja) %>  
  % if c.kasutaja.synnikoht:
  ## synnikoht on saadud RRist ja seda pole vaja ise muuta
  <div class="form-group row">  
    ${h.flb3(_("Sünnikoht"),'dsynnikoht', rq=True)}
    <div class="col-md-9" id="dsynnikoht">
      ${c.kasutaja.synnikoht}
      ${h.hidden('f_synnikoht', c.kasutaja.synnikoht)}      
    </div>
  </div>
  % else:
  % if not on_synniriik:
  <div class="form-group row">  
    ${h.flb3(_("Sünnikoha riik"),'dsynnikoht_kood', rq=True)}
    <div class="col-md-9" id="dsynnikoht_kood">
      ## synnikohaks valitakse riik
      ${h.select('f_synnikoht_kodakond_kood', synniriik,
      c.opt.klread_kood('KODAKOND', vaikimisi=synniriik),
      empty=True)}
    </div>
  </div>
  % endif
  <div class="form-group row">  
    ${h.flb3(_("Sünnikoht"),'dsynnikoht', rq=True)}
    <div class="col-md-9" id="dsynnikoht">
      ${h.text('f_synnikoht', synnikoht)}
    </div>
  </div>
  % endif
  % endif

  % if on_ru:
  % if c.on_iseregaja:
  <div class="form-group row">  
    <div class="col fh">
      ${_("Vene keele tasemeeksami tunnistusele kantakse nimi vene keeles. Selleks, et tagada tunnistusel nime õige kirjapilt, palume esitada oma nimi vene keeles (vene tähtedega).")}
    </div>
  </div>
  % endif
  <div class="form-group row">  
    ${h.flb3(_("Eesnimi vene keeles"),'f_eesnimi_ru', rq=True)}
    <div class="col-md-9">
      ${h.text('f_eesnimi_ru', eesnimi_ru, maxlength=75, class_='char-ru')}
    </div>
  </div>
  <div class="form-group row">  
    ${h.flb3(_("Perekonnanimi vene keeles"),'f_perenimi_ru', rq=True)}
    <div class="col-md-9">
      ${h.text('f_perenimi_ru', perenimi_ru, maxlength=75, class_='char-ru')}
    </div>
  </div>
  % endif

  % if on_rahvus:
  <div class="form-group row">  
    ${h.flb3(_("Rahvus"),'f_rahvus_kood', rq=True)}
    <div class="col-md-9">
      ${h.select('f_rahvus_kood', rahvus,
      c.opt.klread_kood('RAHVUS', vaikimisi=rahvus), empty=True)}
    </div>
  </div>
  % endif

</div>
% endif
% if on_rv and c.on_iseregaja and request.is_ext():
<p>
Olen nõus, et Haridus- ja Noorteameti edastab registreerimise käigus küsitud minu isikuandmed rahvusvahelist võõrkeele tasemeeksamit koordineerivale organisatsioonile*. Andmed edastatakse krüpteeritult ja neid kasutatakse ainult rahvusvaheliste võõrkeele tasemeeksamite korraldamiseks/läbiviimiseks. Samuti nõustun sellega, et tasemeeksamit korraldav organisatsioon edastab minu eksamitulemused ja/või tunnistuse Haridus- ja Noorteametile.
</p>
<p>
*Eksameid korraldavad organisatsioonid:
<br/>Saksa keel – Goethe Keskus Tallinna Saksa Kultuuriinstituut
##<br/>Vene keel – Venemaa Rahvaste Sõpruse Ülikool
<br/>Prantsuse keel – CIEP (Rahvusvaheline Pedagoogiliste Uuringute Keskus)
<br/>Inglise keel – Cambridge Assessment English
</p>
% endif
% endif
