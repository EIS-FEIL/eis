<%inherit file="/common/formpage.mako"/>
<%def name="draw_tabs()">
<%include file="tabs.mako"/>
</%def>

<%def name="page_title()">
${c.item.nimi} | ${_("Koostamine")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Ülesandepank"), h.url('ylesanded'))} 
${h.crumb(c.item.nimi or c.item.id, h.url('ylesanne', id=c.item.id))} 
${h.crumb(_("Koostamine"), None, True)}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'ylesanded' %>
</%def>

<%
  can_update = c.user.has_permission('ylesanded',const.BT_UPDATE, c.item)
  can_update_r = c.user.has_permission('ylesanderoll', const.BT_UPDATE, c.item)
  can_classify = c.item.has_permission('ylesanded', const.BT_VIEW, None, c.user, True)
%>

<div class="form-wrapper mb-3">
<div class="form-group row">
  ${h.flb3(_("Olek"), 'staatus')}
  <div class="col-md-6" id="staatus">
    ${h.roxt(c.item.staatus_nimi)}
  </div>
  % if can_update:
  <div class="col-md-3">
    ${h.btn_to_dlg(_("Muuda olek"), h.url_current('edit', sub='olek', partial=True),
    dlgtitle=_("Ülesande olek"), size='lg')}
    ${h.btn_to_dlg(_("Kontrolli"), h.url('edit_ylesanne', id=c.item.id, sub='kontroll', partial=True), 
    dlgtitle=_("Ülesande kontrollimine"), size='lg', level=2)}
  </div>
  % endif
</div>
<div class="form-group row">
  ${h.flb3(_("Salastatud"), 'salastatud')}
  <div class="col-md-6" id="salastatud">
    ${h.roxt(c.item.salastatud_nimi())}
  </div>
  % if can_update:
  <div class="col-md-3">
      % if c.item.salastatud == const.SALASTATUD_POLE:
      % if can_classify:
      ${h.btn_to_dlg(_("Salasta"), h.url_current('edit', sub='secret',partial=True), dlgtitle=_("Salasta"), width=560)}
      % endif
      % elif c.item.salastatud == const.SALASTATUD_LOOGILINE:
      ${h.btn_to_dlg(_("Lõpeta salastatus"), h.url_current('edit', sub='nosecret',partial=True), dlgtitle=_("Lõpeta salastatus"), width=560)}
      % endif
  </div>
  % endif
</div>
<div class="form-group row">
  ${h.flb3(_("Muutmise lukustus"),'lukus')}
  <div class="col-md-6" id="lukus">
    ${h.roxt(c.item.lukus_nimi or '')}
  </div>
  % if can_update and c.item.lukus:
  % if c.item.lukus < const.LUKUS_SOORITATUD or c.user.has_permission('ylesannelukustlahti', const.BT_UPDATE) or not c.item.get_lukustusvajadus():  
  <div class="col-md-3">
    ${h.btn_to(_("Võta lukust lahti"), h.url_current('update', sub='avalukk'),
    method='post',
     confirm=_("Luku eemaldamisel on kerge teha asju, mis viivad andmed ebakõlla. \nKas oled kindel, et soovid lukku eemaldada?"))}
  </div>
  % endif
  % elif can_update and c.item.get_lukustusvajadus():
  <div class="col-md-9 pt-1">
    ${h.alert_error(_("Ülesanne peaks olema lukus, kuid on lukust lahti võetud."), False)}
  </div>
  <div class="col-md-3">
    ${h.btn_to(_("Taasta lukustus"), h.url_current('update', sub='taastalukk'), method='post')}
  </div>
  % endif
</div>

<div class="form-group row">
  ${h.flb3(_("Muudatuste logi"),'logitase')}
  <div class="col-md-6" id="logitase">
    ${h.roxt(h.sbool(c.item.logitase == const.LOG_LEVEL_CHANGE))}
  </div>
  % if can_update and c.item.logitase < const.LOG_LEVEL_CHANGE:
    ## logi välja lülitamise võimalus maha võetud (ES-197)
  <div class="col-md-3">
    ${h.btn_to_dlg(_("Muuda logitase"), h.url_current('edit',
    sub='logitase',partial=True), dlgtitle=_("Logitase"), width=560)}
  </div>
  % endif
</div>
</div>

<table width="600" border="0"  class="mb-2 table table-borderless table-striped tablesorter">
  <caption>${_("Ülesandega seotud isikud")}</caption>
## Siin kuvatakse kasutajad, kellele on antud õigused 
## selle konkreetse ülesande kohta. Need isikud omavad 
## ülesandele ligipääsus ka siis, kui ülesanne on salastatud.
## Märkus: õigus võidakse anda ülesande suhtes või tuleneda testist 
## (testi suhtes antud õigused laienevad kõikidele testi valitud ülesannetele).
  <col/>
  <col/>
  <col/>
  <col width="80px"/>
  <thead>
    <tr>
      <th>${_("Nimi")}</th>
      <th>${_("Roll")}</th>
      <th nowrap>${_("Kehtib kuni")}</th>      
      % if can_update_r:
      <th sorter="false"></th>
      % endif
    </tr>
  </thead>
  <tbody>
    % for roll in c.item.ylesandeisikud:
    <tr>
      <td>${roll.kasutaja.nimi}</td>
      <td>${roll.kasutajagrupp.nimi}</td>
      <td>${h.str_from_date(roll.kehtib_kuni_ui)}</td>
      % if can_update_r:
      <td>
        ${h.btn_to_dlg('', h.url('ylesanne_koostamine_edit_isik', id=roll.id, ylesanne_id=c.item.id),
        title=_("Muuda"),
        dlgtitle=_("Kasutajaroll"),
        mdicls='mdi-account-edit', size='md', level=0)}
      </td>
      % endif
    </tr>
    % endfor    
  </tbody>
% if can_update_r:
  <tfoot>
    <tr>
      <td colspan="4" class="field_body">
        ${h.btn_to_dlg(_("Lisa"), h.url('ylesanne_koostamine_isikud', ylesanne_id=c.item.id, partial=True), title=_("Ülesandega seotud isikute lisamine"), mdicls='mdi-account-plus')}
      </td>
    </tr>
  </tfoot>
% endif
</table>

<% rollid = c.item.get_testitegelejad() %>
% if rollid:
<table width="600" border="0"  class="mb-2 table table-borderless table-striped tablesorter">
  <caption>${_("Ülesandega testi kaudu seotud isikud")}</caption>
  ## Siin on isikud, kellele on antud õigus mõnele testile, 
  ## kus seda ülesannet kasutatakse
  <thead>
    <tr>
      <th>${_("Nimi")}</th>
      <th>${_("Roll")}</th>
    </tr>
  </thead>
  <tbody>
    % for k_id, g_id in rollid:
    <% 
       kasutaja = model.Kasutaja.get(k_id)
       kasutajagrupp = model.Kasutajagrupp.get(g_id)
    %>
    <tr>
      <td>${kasutaja.nimi}</td>
      <td>${kasutajagrupp.nimi}</td>
    </tr>
    % endfor
  </tbody>
</table>
% endif

<% rollid = c.item.get_rollitegelejad() %>
% if rollid and c.item.staatus not in const.Y_ST_AV:
<table width="600" border="0"  class="mb-2 table table-borderless table-striped tablesorter">
  <caption>${_("Ülesannetega tegelejad")}</caption>
## Siin nimekirjas kuvatakse kasutajad, 
## kes omavad ülesande õppeaine suhtes ainespetsialisti 
## või õppeaine, osaoskuse ja testi liigi suhtes osaoskuse spetsialisti 
## õiguseid.
  <thead>
    <tr>
      <th>${_("Nimi")}</th>
      <th>${_("Roll")}</th>
    </tr>
  </thead>
  <tbody>
    % for roll in rollid:
    <tr>
      <td>${roll.kasutaja.nimi}</td>
      <td>${roll.kasutajagrupp.nimi}</td>
    </tr>
    % endfor
  </tbody>
</table>
% endif

% if c.item.staatus not in const.Y_ST_AV:
${h.btn_to_dlg(_("Saada teade"), h.url_current('edit',sub='mail',partial=True),
title=_("Teate saatmine"), size='lg')}
% endif

% if c.dialog_mail:
<div id="div_dialog_mail">
  <%include file="koostamine.mail.mako"/>
</div>
<script>
  $(function(){
    open_dialog({'contents_elem': $('#div_dialog_mail'), 'title':'${_("Teate saatmine")}'});
  });
</script>
% endif
