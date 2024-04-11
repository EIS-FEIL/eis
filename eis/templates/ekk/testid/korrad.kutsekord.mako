<%inherit file="korrad.mako"/>
<%def name="require()">
<%
c.includes['subtabs'] = True
c.includes['jstree'] = True
c.includes['select2'] = True  
%>
</%def>
${h.form_save(c.item.id, style="width:100%")}
<% k_keeled = c.item.keeled %>

<h2>${_("Testimiskorra andmed")}</h2>

<div class="gray-legend p-2 border-base-radius">
  <div class="form-group row">
    ${h.flb3(_("Testimiskorra tähis"), 'f_tahis')}
    <div class="col-md-9">
      ${h.text('f_tahis', c.item.tahis, maxlength=10, size=11, pattern='[0-9a-zA-Z]*')}

      % if c.item.valim_testimiskord:
      ${_("Moodustatud valimina testimiskorrast {s}").format(s=h.link_to(c.item.valim_testimiskord.tahised,
      h.url('test_kutse_edit_kord', test_id=c.item.test_id, id=c.item.valim_testimiskord_id)))}
      % endif
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Testsessioon"), 'f_testsessioon_id')}
    <div class="col-md-9">
      ${h.select('f_testsessioon_id', c.item.testsessioon_id,
      model.Testsessioon.get_opt(c.test.testiliik_kood), empty=True)}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Soorituskeeled"), 'keeled')}
    <div class="col-md-9" id="keeled">
      % for lang in c.test.keeled:
      ${h.checkbox('lang', value=lang, checked=lang in k_keeled)} ${model.Klrida.get_str('SOORKEEL', lang)}
      % endfor
      ${h.hidden('lang_err', '')}
    </div>
  </div>
</div>

% for ind, toimumisaeg in enumerate(c.item.toimumisajad):
<%
  testiosa = toimumisaeg.testiosa
  prefix = 'ta-%d' % ind
%>
${self.toimumisaeg(toimumisaeg, testiosa, prefix, k_keeled)}
% endfor
${h.end_form()}

<%def name="toimumisaeg(ta, testiosa, prefix, k_keeled)">
<% idpref = str(testiosa.id) %>
<h2>${_("Toimumisaja korraldamise parameetrid")}</h2>
${h.hidden('%s.testiosa_id' % prefix, testiosa.id)}
<div class="p-2 mb-3 border border-base-radius">
  <div class="form-group row">
    ${h.flb3(_("Toimumisaja tähis"),'tatahised'+idpref)}
    <div class="col-md-9" id="tatahised${idpref}">
      ${ta.tahised}

      % if ta.id:
      <span class="text-right">
        ${h.link_to(_("Korraldamine"), h.url('korraldamine_soorituskohad',  toimumisaeg_id=ta.id),
        class_="button button1")}
      </span>
      % endif
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Vastamise vorm"), 'vastvorm'+idpref)}
    <div class="col-md-9" id="vastvorm${idpref}">
      ${testiosa.vastvorm_nimi}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Soorituskeeled"), 'keel'+idpref)}
    <div class="col-md-9" id="keel${idpref}">
      ${', '.join([model.Klrida.get_lang_nimi(lang) for lang in k_keeled])}
    </div>
  </div>

  ${self.toimumispaevad(ta.toimumispaevad, testiosa, '%s.tpv' % prefix)}

  
  ${h.checkbox('%s.aja_jargi_alustatav' % prefix, 1, checked=ta.aja_jargi_alustatav,
  label=_("Etteantud alustamise ajavahemikul saab sooritamist alustada ilma administraatori loata"))}
  % if testiosa.vastvorm_kood in (const.VASTVORM_KE, const.VASTVORM_SE, const.VASTVORM_I):
  <div>
    ${h.checkbox('%s.on_arvuti_reg' % prefix, 1, checked=ta.on_arvuti_reg,
    label=_("Arvutite registreerimine nõutav"))}
  </div>
  % endif
</div>

${self.komplektid(ta, testiosa, prefix, k_keeled)}

</%def>

<%def name="komplektid(ta, testiosa, prefix, k_keeled)">
<h2>${_("Ülesandekomplektid")}</h2>
<div class="p-2 mb-3 border border-base-radius">
  <div class="form-group row">
    <div class="col-12">
      ${h.checkbox('%s.komplekt_valitav' % prefix, 1, checked=ta.komplekt_valitav,
      label=_("Komplekti valimine sooritaja poolt"),
      class_="komplekt_valitav mb-1")}

      <span class="valitav_y1">
        ${h.checkbox('%s.komplekt_valitav_y1' % prefix, 1, checked=ta.komplekt_valitav_y1,
        label=_("Valikuvõimalus ainult komplekti esimese ülesande juures"))}
      </span>
    </div>
  </div>
  % for kvalik in testiosa.komplektivalikud:
  <div class="form-group row">
    <div class="col-md-3 fh">
        % if not testiosa.on_alatestid and not kvalik.kursus_kood:
        ${_("Komplektid")}
        % endif
        % if kvalik.kursus_kood:
        (${kvalik.kursus_nimi})
        % endif
        % if testiosa.on_alatestid:
        ${_("Alatest")} ${kvalik.str_alatestid}:
        % endif
    </div>
    <div class="col-md-9">
        <% found = False %>
        % for rcd in kvalik.komplektid:
        % if rcd.staatus == const.K_STAATUS_KINNITATUD and set(k_keeled).issubset(set(rcd.keeled)):
        <% found = True %>
        ${h.checkbox('%s.komplekt_id' % prefix, rcd.id, checked=rcd in ta.komplektid, label=rcd.tahis)} 
        % endif
        % endfor

        % if not found:
        <span class="error">
          ${_("Valikus pole ühtki komplekti, mis vastaks testimiskorra keeltele ja oleks kinnitatud.")}
        </span>
        % endif
    </div>
  </div>
  % endfor
</div>
</%def>

<%def name="row_toimumispaev(item, testiosa, prefix)">
    <tr>
      <td>
        ${h.date_field('%s.kuupaev' % prefix, item.aeg, wide=False)}
      </td>
      <td>
        <% dflt = testiosa.vastvorm_kood in (const.VASTVORM_KP, const.VASTVORM_SP) and '10.00' or None %>        
        ${h.time('%s.kell' % prefix, item.aeg, default=dflt, wide=False)}
      </td>
      <td class="alustamise-lopp">
        ${h.time('%s.a_lopp' % prefix, item.alustamise_lopp, wide=False)}
      </td>
      <td>
        % if c.can_update and c.is_edit:
        ${h.grid_remove()}
        % endif
        ${h.hidden('%s.id' % prefix, item.id)}
      </td>
    </tr>
</%def>

<%def name="toimumispaevad(choices, testiosa, prefix)">
<% tbl_id = h.toid('tbl_%s' % prefix) %>
<table id="${tbl_id}" width="100%" border="0" class="table" > 
  <thead>
    <tr>
      <td><b>${_("Toimumise kuupäev")}</b></td>
      <td><b>${_("Alguse kellaaeg")}</b></td>
      <td class="alustamise-lopp"><b>${_("Alustamine kuni")}</b></td>      
      <td>
      % if c.is_edit:
      ${h.button(_("Lisa"), onclick="grid_addrow('%s')" % tbl_id, mdicls='mdi-plus', class_="btn-normal", level=2)}
      % endif
      </td>
    </tr>
  </thead>
  <tbody>
  % if c._arrayindexes != '':
## valideerimisvigade korral
  %   for cnt in c._arrayindexes.get(prefix) or [0]:
        ${self.row_toimumispaev(c.new_item(), testiosa, '%s-%s' % (prefix, cnt))}
  %   endfor
  % else:
## tavaline kuva
    <%
    if len(choices) == 0:
       ## alati peab vähemalt yks kuupäev olemas olema
       choices = [c.new_item()]
    %>
  %   for cnt,item in enumerate(choices):
        ${self.row_toimumispaev(item, testiosa, '%s-%s' % (prefix, cnt))}
  %   endfor
  % endif
  </tbody>
</table>
% if c.is_edit:
<div id="sample_${tbl_id}" class="invisible">
<!--
   ${self.row_toimumispaev(c.new_item(), testiosa, '%s__cnt__' % prefix)}
-->
</div>
% endif
</%def>

<%def name="buttons()">
% if c.can_update:
  % if c.is_edit:
${h.submit(out_form=True)}
  % elif c.item.id:
${h.btn_to(_("Muuda"), h.url('test_kutse_edit_kord', test_id=c.test.id, id=c.item.id))}
  % endif
% endif

% if c.item and c.item.id:
  % if c.user.has_permission('testimiskorrad', const.BT_UPDATE, c.test):
${h.btn_to(_("Kopeeri"), h.url('test_kutse_new_kord', test_id=c.test.id,
id=c.item.id))}
  % endif
  % if c.user.has_permission('tkorddel', const.BT_DELETE):
<%
  cnt = model.SessionR.query(model.sa.func.count(model.Sooritaja.id)).filter_by(testimiskord_id=c.item.id).scalar()
  if cnt:
     message = _("Testimiskorral {s} on {n} sooritajat. Kas oled kindel, et soovid selle testimiskorra koos sooritajate andmetega kustutada?").format(s=c.item.tahis, n=cnt)
  else:
     message = _("Kas oled kindel, et soovid testimiskorra {s} kustutada?").format(s=c.item.tahis)
%>
${h.btn_to(_("Kustuta"), h.url('test_kutse_delete_kord', test_id=c.test.id, id=c.item.id), method='delete', confirm=message)}
  % endif
% endif

</%def>

<script>
$(document).ready(function(){
  $('input.komplekt_valitav').change(function(){
    $(this).closest('table').find('.valitav_y1').toggle($(this).prop('checked'));
  });
  $('input.komplekt_valitav').each(function(n, fld){
    $(fld).closest('table').find('.valitav_y1').toggle($(fld).prop('checked'));
  });
});
</script>
