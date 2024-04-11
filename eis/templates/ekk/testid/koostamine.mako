<%inherit file="/common/formpage.mako"/>
<%def name="draw_tabs()">
<%include file="tabs.mako"/>
</%def>

<%def name="page_title()">
${_("Test")}: ${c.test.nimi or ''} | ${_("Koostamine")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Testid"), h.url('testid'))} 
${h.crumb(c.test.nimi or _("Test"))} 
${h.crumb(_("Koostamine"))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'testid' %>
</%def>

<%
c.item = c.test
c.can_update = c.user.has_permission('ekk-testid', const.BT_UPDATE, c.test)
c.can_update_r = c.user.has_permission('testiroll', const.BT_UPDATE, c.test)
%>
${h.form_save(c.item.id)}

<% ch = h.colHelper('col-md-2', 'col-md-4') %>
<div class="form-wrapper mb-2">
  <div class="form-group row">
    ${ch.flb(_("Olek"))}
    <div class="col-md-4">
      <div class="readonly">${c.item.staatus_nimi}</div>
      <div class="readonly">
        ${c.item.avaldamistase_nimi}
        % if c.item.avalik_alates or c.item.avalik_kuni:
        ${h.str_from_date(c.item.avalik_alates)} - ${h.str_from_date(c.item.avalik_kuni)}
        % endif
      </div>
    </div>
    % if c.can_update:
    <div class="col">
      ${h.btn_to_dlg(_("Muuda olek"),
      h.url_current('edit',partial=True, sub='olek'), dlgtitle=_("Testi olek"))}
    </div>
    % endif
  </div>

  <div class="form-group row">
    ${ch.flb(_("Salastatud"))}
    <div class="col-md-4">
      <div class="readonly">
        ${c.item.salastatud_nimi()}
      </div>
    </div>
    % if c.can_update:
    <div class="col">
      % if c.item.salastatud == const.SALASTATUD_POLE:
      ${h.btn_to_dlg(_("Salasta"), h.url_current('edit',sub='secret',partial=True),
      dlgtitle=_("Salasta"))}

      % elif c.item.salastatud in (const.SALASTATUD_LOOGILINE, const.SALASTATUD_SOORITATAV):
      ${h.btn_to_dlg(_("Lõpeta salastatus"), h.url_current('edit',sub='nosecret',partial=True),
      dlgtitle=_("Lõpeta salastatus"))}

      % endif
    </div>
    % endif
  </div>
</div>

% if c.testilogid:
<% names = {} %>
<div class="form-wrapper-lineborder">
% for r in c.testilogid:
<div class="form-group row">
  <%
    name = names.get(r.creator)
    if not name:
       name = names[r.creator] = model.Kasutaja.get_name_by_creator(r.creator)
  %>
  <div class="col-9">${r.uued_andmed.replace('\n','<br/>')}</div>
  <div class="col-3"><i>${name} ${h.str_from_datetime(r.created)}</i></div>
</div>
% endfor
</div>
% endif

<table width="600" border="0"  class="table tablesorter">
  <caption>${_("Testiga seotud isikud")}</caption>
  <thead>
    <tr>
      <th>${_("Nimi")}</th>
      <th>${_("Kasutajaroll")}</th>
      <th nowrap>${_("Kehtib kuni")}</th>
      % if c.can_update_r:
      <th sorter="false"></th>
      % endif
    </tr>
  </thead>
  <tbody>
    % for roll in c.item.testiisikud:
    <tr>
      <td>${roll.kasutaja.nimi}</td>
      <td>${roll.kasutajagrupp.nimi}</td>
      <td>${h.str_from_date(roll.kehtib_kuni_ui)}</td>
      % if c.can_update_r:
      <td>
        ${h.btn_to_dlg('', h.url('test_koostamine_edit_isik', id=roll.id, test_id=c.item.id),
        title=_("Muuda"), dlgtitle=_("Kasutajaroll"),
        mdicls='mdi-account-edit', size='md', level=0)}
      </td>
      % endif
    </tr>
    % endfor    
  </tbody>
% if c.can_update_r:
  <tfoot>
    <tr>
      <td class="field_body" colspan="2">
        ${h.btn_to_dlg(_("Lisa"), h.url('test_koostamine_isikud', test_id=c.item.id, partial=True),
        title=_("Testiga seotud isikute lisamine"), mdicls='mdi-account-plus')}
        ${h.btn_to_dlg(_("Lisa korraldajad failiga"), h.url('test_koostamine_isikud', test_id=c.item.id, sub='fail', partial=True),
        title=_("Testi korraldajate lisamine"))}        
      </td>
    </tr>
  </tfoot>
% endif
</table>
<br/>

<% rollid = c.item.get_rollitegelejad() %>
% if rollid and c.item.testityyp == const.TESTITYYP_EKK:
<table width="600" border="0"  class="table table-borderless table-striped tablesorter">
  <caption>${_("Ainespetsialistid")}</caption>
  <col width="50%"/>
  <col width="50%"/>
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

% if c.item.testityyp == const.TESTITYYP_EKK:
${h.btn_to_dlg(_("Saada teade"), h.url_current('edit', sub='mail', partial=True, size='lg'),
dlgtitle=_("Teate saatmine"))}
% endif

${h.end_form()}

% if c.dialog_mail:
<div id="div_dialog_mail">
  <%include file="koostamine.mail.mako"/>
</div>
<script>
  $(function(){
    open_dialog({'contents_elem': $('#div_dialog_mail'), 'title': '${_("Teate saatmine")}'});
  });
</script>
% endif
