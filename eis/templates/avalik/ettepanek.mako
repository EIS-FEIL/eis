## -*- coding: utf-8 -*- 
<%include file="/common/message.mako"/>
% if c.saadetud_ok:
<center>
${h.alert_success(_("Täname! Küsimus või ettepanek on esitatud."))}

${h.button(_("Sule"), onclick='close_dialog()')}
</center>

% else:

${h.form_save(None)}
<table width="100%" class="table" >
  <col width="110"/>
  <col/>
  <tr>
    <td class="fh">
      ${_("Pöörduja")}
    </td>
    <td>
      ${c.user.fullname}
      % if c.user.koht_id:
      <br/>
      ${c.user.koht.nimi}
      % endif
    </td>
  </tr>
  <tr>
    <td class="fh">
      ${_("E-posti aadress")}
    </td>
    <td class="err-parent">
      ${h.text('epost', c.item.epost, maxlength=255)}
    </td>
  </tr>
  <tr>
    <td class="fh">
      ${_("Teema")}
    </td>
    <td>
      ${h.text('teema', c.item.teema, maxlength=255)}
    </td>
  </tr>
  <tr>
    <td colspan="2">
      ${_("Teate sisu")}<br/>
      ${h.textarea('sisu', c.item.sisu, cols=15, rows=8)}
    </td>
  </tr>
  <tr>
    <td colspan="2">
      ${h.checkbox('ootan_vastust', 1, checked=c.item.ootan_vastust, label='Ootan vastuskirja')}
    </td>
  </tr>
</table>

${h.submit_dlg(_("Saada"))}
</div>
${h.end_form()}
% endif
