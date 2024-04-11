<%inherit file="/common/formpage.mako"/>
<%def name="draw_tabs()">
<% c.tab1 = 'yksikasjad' %>
<%include file="nimistu.tabs.mako"/>
</%def>

<%def name="page_title()">
${_("Eksamile registreerimise taotluse sisestamine")}
</%def>      

<%def name="breadcrumbs()">
${h.crumb(_("Registreerimine"), h.url('regamised'))} 
${h.crumb(_("Registreerimise taotluse sisestamine"))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'regamised' %>
</%def>

% for kord in c.korrad:
<table  class="table" width="100%">
  <tr>
    <td class="fh" width="10%">${_("Nimetus")}</td>
    <td width="40%">${kord.test.nimi}</td>
    <td class="fh" width="10%">${_("Testi liik")}</td>
    <td width="40%">${kord.test.testiliik_nimi}</td>
  </tr>
  <tr>
    <td class="fh">${_("Keeled")}</td>
    <td colspan="3">
      % for lang in kord.get_keeled():
      ${model.Klrida.get_lang_nimi(lang)}
      % endfor
    </td>
</table>

<table  class="table table-borderless table-striped" width="100%">
  <thead>
    <tr>
      ${h.th(_("Toimumisaeg"))}
      ${h.th(_("Aeg"))}
      ${h.th(_("Testiosa"))}
      ${h.th(_("Vastamise vorm"))}
    </tr>
  </thead>
  <tbody>
    % for ta in kord.toimumisajad:
    <% osa = ta.testiosa %>
    <tr>
      <td>${ta.tahised}</td>
      <td>${ta.millal}</td>
      <td>${osa.nimi}</td>
      <td>${osa.vastvorm_nimi}</td>
    </tr>
    % endfor
  </tbody>
</table>
<br/>
% endfor

${h.form(h.url('regamine_nimistu_edit_sooritajad', korrad_id=c.korrad_id), method='get')}
${h.hidden('testiliik', c.testiliik)}
<div class="d-flex flex-wrap">
  <div class="flex-grow-1">
    ${h.btn_to(_("Tagasi"), h.url('regamine_nimistu_testivalik', testiliik=c.testiliik, korrad_id=c.korrad_id), level=2, mdicls='mdi-arrow-left-circle')}
  </div>
  <div>
    ${h.submit(_("Jätka"), mdicls2='mdi-arrow-right-circle')}
  </div>
</div>
${h.end_form()}
