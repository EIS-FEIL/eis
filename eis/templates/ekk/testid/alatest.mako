<%inherit file="/common/dlgpage.mako"/>
<%include file="/common/message.mako"/>
<%include file="translating.mako"/>

${h.form_save(c.item.id)}
${h.hidden('lang', c.lang)}
${h.hidden('is_tr', c.is_tr)}
${h.rqexp()}
<% ch = h.colHelper('col-md-3','col-md-9') %>
<div class="form-wrapper mb-2">
  % if c.item.id:
  <div class="row">
    ${ch.flb(_("Alatesti jrk nr"))}
    <div class="col">
      ${c.item.tahis}
      <span class="pl-4">
        ${h.checkbox('f_numbrita', 1, checked=c.item.numbrita, label=_("Nummerdamata"))}
      </span>
    </div>
  </div>
  % endif
  <% 
           opt_alatest = c.opt.klread_kood('ALATEST',
                                           vaikimisi=c.item.alatest_kood, 
                                           ylem_kood=c.test.aine_kood) 
  %>
  % if opt_alatest:
  <div class="row">
    ${ch.flb(_("Liik"))}
    <div class="col">
      ${h.select('f_alatest_kood', c.item.alatest_kood, opt_alatest,
      wide=False, empty=True, onchange="$('#f_nimi').val($(this).find('option:selected').text())")}
    </div>
  </div>
  % endif

  <div class="row">
    ${ch.flb(_("Alatesti nimetus"), rq=True)}
    <div class="col">
            % if c.lang:
              ${h.lang_orig(c.item.nimi)}<br/>
              ${h.lang_tag()}
              ${h.text('f_nimi', c.item.tran(c.lang).nimi, ronly=not c.is_tr)}
            % else:
              ${h.text('f_nimi', c.item.nimi, ronly=not c.is_tr and not c.is_edit)}
            % endif
    </div>
  </div>
  % if c.item.kursus_kood:
  <div class="row">
    ${ch.flb(_("Kursus"))}
    <div class="col">
      ${model.Klrida.get_str('KURSUS', c.item.kursus_kood, ylem_kood=c.test.aine_kood)}
      ${h.hidden('f_kursus_kood', c.item.kursus_kood)}
    </div>
  </div>
  % endif
        
  % if c.item.id:
  % if c.item.vastvorm_kood != c.item.testiosa.vastvorm_kood:
  <div class="row">
    ${ch.flb(_("Vastamise vorm"))}
    <div class="col">
      ${c.item.vastvorm_nimi}
    </div>
  </div>
  % endif
  <div class="row">
    ${ch.flb(_("Hindepallide suurim arv"))}
    <div class="col">
      ${h.fstr(c.item.max_pallid)}
      % if c.is_edit:
      <div class="d-inline-block pl-3">
        ${_("Muuda")}: ${h.float5('max_pallid', c.max_pallid)}
      </div>
      % endif
    </div>
  </div>
  <div class="row">
    ${ch.flb(_("Tulemuse arvutamise valem"))}
    <div class="col">
      ${h.text('f_skoorivalem', c.item.skoorivalem, maxlength=256)}
    </div>
  </div>
  <div class="row">
    ${ch.flb(_("Ülesannete arv"))}
    <div class="col">
      ${c.item.ylesannete_arv}
    </div>
  </div>
  % endif
  <div class="row">
    ${ch.flb(_("Lahendamise piiraeg"))}
    <div class="col">
      <span class="mr-2">
        ${_("max")} ${h.timedelta_sec('piiraeg', h.str_from_time_sec(c.item.piiraeg),
        onchange="set_hoiatusaeg()", wide=False)}
      </span>
      ${h.checkbox('f_piiraeg_sek', 1, checked=c.item.piiraeg_sek, label=_("Kuva sekundid"))}
    </div>
  </div>
  <div class="row">
    ${ch.flb(_("Hoiatus enne lõppu"))}
    <div class="col">
      ${h.posint5('hoiatusaeg', c.item.hoiatusaeg and int(c.item.hoiatusaeg)/60)} minutit            
    </div>
  </div>

  <div class="row">
    % if c.is_edit:
    <div class="col">
      ${h.checkbox('f_yl_segamini', 1, checked=c.item.yl_segamini,
      label=_("Ülesannete segamine"))}
    </div>
    % else:
    ${ch.flb(_("Ülesannete segamine"))}
    <div class="col">
      ${h.sbool(c.item.yl_segamini or False)}
    </div>
    % endif
  </div>

  <div class="row">
    % if c.is_edit:
    <div class="col">
      ${h.checkbox('f_yhesuunaline', 1, checked=c.item.yhesuunaline, 
      onchange="if(this.checked)$('#f_on_yhekordne').prop('checked',true);",
      label=_("Ühesuunaline lahendamine"))}
    </div>
    % else:
    ${ch.flb(_("Ühesuunaline lahendamine"))}
    <div class="col">
      ${h.sbool(c.item.yhesuunaline or False)}
    </div>
    % endif
  </div>
  <div class="row">
    % if c.is_edit:
    <div class="col">
      ${h.checkbox('f_on_yhekordne', 1, checked=c.item.on_yhekordne, ronly=c.testiosa.yhesuunaline,
      onchange="if($('#f_yhesuunaline').prop('checked')) $(this).prop('checked', true);",
      label=_("Ühekordselt lahendatav"),
      disabled=c.testiosa.yhesuunaline)}
      % if c.testiosa.yhesuunaline:
      ${h.hidden('f_on_yhekordne', '1')}
      % endif
    </div>
    % else:
    ${ch.flb(_("Ühekordselt lahendatav"))}
    <div class="col">
      ${h.sbool(c.testiosa.yhesuunaline or c.item.on_yhekordne or False)}
    </div>
    % endif
  </div>
  <div class="row">
    % if c.is_edit:
    <div class="col">
      ${h.checkbox('f_peida_pais', 1, checked=c.item.peida_pais,
      label=_("Peida süsteemi päis ja jalus"),
      disabled=c.testiosa.peida_pais)}
    </div>
    % else:
    ${ch.flb(_("Peida süsteemi päis ja jalus"))}
    <div class="col">
      ${h.sbool(c.testiosa.peida_pais or c.item.peida_pais)}
    </div>
    % endif
  </div>
        
  % if c.test.testiliik_kood == const.TESTILIIK_RV and c.test.rveksam:
  <div class="row">
    ${h.flb(_("Osaoskus tunnistusel"))}
    <div class="col">
            <%
               opt_osaoskused = [(r.id, r.nimi) for r in c.test.rveksam.rvosaoskused]
            %>
            ${h.select('f_rvosaoskus_id', c.item.rvosaoskus_id, opt_osaoskused, empty=True)}
    </div>
  </div>
  % endif
       
  <div class="row">
    <div class="col">
      ${h.flb(_("Juhised sooritajale"))}
      <div>
            % if c.lang:
              ${h.lang_orig(c.item.sooritajajuhend)}<br/>
              ${h.lang_tag()}
              ${h.textarea('f_sooritajajuhend', c.item.tran(c.lang).sooritajajuhend, 
                 cols=72, rows=5, ronly=not c.is_tr)}
            % else:
              ${h.textarea('f_sooritajajuhend', c.item.sooritajajuhend,
                 cols=72, rows=5, ronly=not c.is_tr and not c.is_edit)}
            % endif
      </div>
    </div>
  </div>
</div>
<div class="text-right">
  % if c.is_edit or c.is_tr:
  ${h.submit_dlg(clicked=True)}
  % endif
  <span id="progress"></span>
</div>
${h.end_form()}

<script>
      function set_hoiatusaeg()
      {
          var piiraeg = $('#piiraeg').val();
          if(piiraeg != '' && $('#hoiatusaeg').val() == '')
          {
             var li = piiraeg.split(':');
             var piiraeg_s = parseInt(li[0]);
             if(li.length > 1)
                piiraeg_s = piiraeg_s*60 + parseInt(li[1]);
             if(piiraeg_s > 300)
              $('#hoiatusaeg').val('5');
          }
      }
</script>
