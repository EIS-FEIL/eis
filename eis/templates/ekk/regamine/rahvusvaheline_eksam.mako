<% 
   test = c.sooritaja.test 
%>
% if test.testiliik_kood == const.TESTILIIK_RV:

## - kõik saksa keele eksamid lisaväli sünnikoha riik
## - lisaandmed vene keele valiku korral: ees- ja perekonnanimi
## - lisaandmed prantsuse keele valiku korral: sünnikoha koht, rahvus.

<div class="form-wrapper-lineborder my-1">
  % if test.aine_kood == const.AINE_DE:
  <div class="form-group row">
    ${h.flb3(_("Sünnikoha riik"),'dsynnikoht_kood')}
    <div class="col-md-9" id="dsynnikoht_kood">
      ${h.select('f_synnikoht_kodakond_kood', c.sooritaja.synnikoht_kodakond_kood, 
      c.opt.klread_kood('KODAKOND', vaikimisi=c.sooritaja.synnikoht_kodakond_kood), 
      empty=True, wide=False)}
    </div>
  </div>
  % endif

  % if test.aine_kood == const.AINE_FR:
  ## vajadusel päritakse sooritaja synnikoht RRist
  <% c.user.check_synnikoht(c.kasutaja) %>
  % if c.kasutaja.synnikoht:
  ## synnikoht on saadud RRist ja seda pole vaja ise muuta
  <div class="form-group row">
    ${h.flb3(_("Sünnikoht"),'dsynnikoht')}
    <div class="col-md-9" id="dsynnikoht">
      ${c.kasutaja.synnikoht}
      ${h.hidden('f_synnikoht', c.kasutaja.synnikoht)}
    </div>
  </div>
  % else:
  <div class="form-group row">
    ${h.flb3(_("Sünnikoha riik"),'dsynnikoht_kood')}
    <div class="col-md-9" id="dsynnikoht_kood">
      ${h.select('f_synnikoht_kodakond_kood', c.sooritaja.synnikoht_kodakond_kood, 
      c.opt.klread_kood('KODAKOND', vaikimisi=c.sooritaja.synnikoht_kodakond_kood), 
      empty=True, wide=False)}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Sünnikoht"),'dsynnikoht')}
    <div class="col-md-9" id="dsynnikoht">
      ${h.text('f_synnikoht', c.sooritaja.synnikoht)}
    </div>
  </div>
  % endif
  % endif
  
  % if test.aine_kood == const.AINE_RU:
  <div class="form-group row">
    ${h.flb3(_("Eesnimi vene keeles"),'f_eesnimi_ru')}
    <div class="col-md-9">
      ${h.text('f_eesnimi_ru', c.sooritaja.eesnimi_ru, maxlength=75, size=50, class_='char-ru')}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Perekonnanimi vene keeles"),'f_perenimi_ru')}
    <div class="col-md-9">
      ${h.text('f_perenimi_ru', c.sooritaja.perenimi_ru, maxlength=75, size=50, class_='char-ru')}
    </div>
  </div>
  % endif

  % if test.aine_kood == const.AINE_FR:
  <div class="form-group row">
    ${h.flb3(_("Rahvus"),'f_rahvus_kood')}
    <div class="col-md-9">
      ${h.select('f_rahvus_kood', c.sooritaja.rahvus_kood,
      c.opt.klread_kood('RAHVUS', vaikimisi=c.sooritaja.rahvus_kood),
      empty=True, wide=False)}
    </div>
  </div>
  % endif
</div>
% endif
