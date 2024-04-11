<%include file="/common/message.mako"/>
${h.form_save(c.item.id)}
<div class="form-wrapper-lineborder mb-2">
  <div class="form-group row">
    ${h.flb3(_("Nimi"))}
    <div class="col">${c.item.kasutaja.nimi}</div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Tunnistuse nr"))}
    <div class="col">${c.item.tunnistusenr}</div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Olek"))}
    <div class="col">${c.item.staatus_nimi}</div>
  </div>
  
  <div class="form-group row">
    <div class="col">
      % if c.item.staatus == const.N_STAATUS_KEHTETU:
      ${h.flb(_("Tühistamise/ennistamise põhjendus"))}
      % else:
      ${h.flb(_("Tühistamise põhjendus"))}
      % endif
      <div class="my-1">
        ${h.textarea('tyh_pohjendus', c.item.tyh_pohjendus, rows=4, maxlength=256)}
      </div>
      % if c.item.staatus != const.N_STAATUS_KEHTETU:
      ${h.checkbox('tyh_sooritused', label=_("Tühistada ka eksamisooritused"))}
      % endif
    </div>
  </div>
</div>

      
<table width="100%" class="table table-borderless table-striped" border="0" >
  <thead>
    <tr>
      <th>${_("Test")}</th>
      <th>${_("Kuupäev")}</th>
      <th>${_("Tulemus")}</th>
      <th>${_("Olek")}</th>            
    </tr>
  </thead>
  <tbody>
    % for r in c.item.testitunnistused:
    <% sooritaja = r.sooritaja %>
    <tr>
      <td>${sooritaja.test.nimi}</td>
      <td>${sooritaja.millal}</td>
      <td>${sooritaja.get_tulemus()}</td>
      <td>${sooritaja.staatus_nimi}</td>
    </tr>
    % endfor
  </tbody>
</table>

<div class="text-right">
% if c.user.has_permission('tunnistused', const.BT_UPDATE):
% if c.item.staatus != const.N_STAATUS_KEHTETU:
${h.hidden('staatus', const.N_STAATUS_KEHTETU)}
${h.submit_dlg(_("Tühista"))}
% else:
${h.hidden('staatus', const.N_STAATUS_AVALDATUD)}
${h.submit_dlg(_("Ennista"))}
% endif
% endif
</div>

${h.end_form()}

