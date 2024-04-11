${h.form(h.url('test_nimekiri_sooritajad', test_id=c.test_id, nimekiri_id=c.nimekiri_id), method='post', multipart=True)}
${h.hidden('sub', 'fail')}
<%
  opt_keeled = c.testimiskord and c.testimiskord.opt_keeled or c.test.opt_keeled 
  opt_kursused = c.test.opt_kursused
  csv_data = int(request.registry.settings.get('csv.data',0))  
%>
<div class="mb-2">
  <div class="form-group row mb-3">
    <div class="col">
      <div class="mb-2">
        ${_("Laadida saab CSV tekstifailist, milles on iga isiku jaoks eraldi rida ning igal real järgmised väljad:")}
      </div>
      <div>
        ${h.checkbox('stru', 'ik', checked=True, label=_("Isikukood"), disabled=True)}
      </div>
      % if len(opt_keeled) > 1:
      <div>
      <%
        codes = '/'.join([r[0] for r in opt_keeled])
        label = '%s (%s)' % (_("Soorituskeel"), codes)
      %>
      ${h.checkbox('stru', 'lang', label=label)}
      </div>
      % endif

      % if csv_data and (c.is_devel or c.is_test):
      ## testkeskkonnas on võimalik laadida ka õpilaste andmeid, kuna EHISest ei saa
      <div class="testdata">${h.checkbox('stru', 'en', label=_("Eesnimi"))}</div>
      <div class="testdata">${h.checkbox('stru', 'pn', label=_("Perekonnanimi"))}</div>
      <div class="testdata">${h.checkbox('stru', 'kl', label=_("Klass"))}</div>
      <div class="testdata">${h.checkbox('stru', 'pl', label=_("Paralleel"))}</div>
      % endif
    </div>
  </div>

  <div class="form-group row">
    ${h.flb3(_("Sooritajate fail"))}
    <div class="col">
      ${h.file('ik_fail', value=_("Fail"))}
    </div>
  </div>
  % if len(opt_keeled) > 0:
  <div class="form-group row" id="r_lang">
    ${h.flb3(_("Soorituskeel"))}
    <div class="col">
      % if len(opt_keeled) > 1:
      ${h.select('keel', c.keel, opt_keeled, wide=False)}    
      % else:
      ${opt_keeled[0][1]}
      ${h.hidden('keel', opt_keeled[0][0])}
      % endif
    </div>
  </div>
  % endif
  % if len(opt_kursused):  
  <div class="form-group row">
    ${h.flb3(_("Kursus"))}
    <div class="col">
      ${h.select('kursus', None, opt_kursused, wide=False)}
    </div>
  </div>
  % endif
  % if c.test.testiliik_kood in (const.TESTILIIK_KOOLIPSYH, const.TESTILIIK_LOGOPEED):  
  <div class="form-group row">
    <div class="col">
      ${h.checkbox('vanem_nous', 1, label=_('Vanema nõusolek'))}
    </div>
  </div>
  % endif
</div>

<div class="d-flex">
  <div class="flex-grow-1">
  </div>
  ${h.submit(_('Salvesta'))}
</div>
${h.end_form()}

<script>
  ## kui soorituskeel on faili struktuuris, siis peidame soorituskeele valikvälja
  ## kui soorituskeel pole faili struktuuris, siis kehtib kogu failile valikväljal valitud keel
  $('input[name="stru"][value="lang"]').click(function(){
     $('#r_lang').toggle(!this.checked);
  });
  if($('input[name="stru"][value="lang"]').prop('checked')) {
     $('#r_lang').hide();
  }
  ## testandmete väljad peavad koos esinema
  $('.testdata input[name="stru"]').click(function(){
       $('.testdata input[name="stru"]').prop('checked', this.checked);
  });
</script>
