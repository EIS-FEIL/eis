${h.form(h.url('tulemused_create_volitused'), method='post')}
<% c.kasutaja = c.user.get_kasutaja() %>
<table width="100%" class="table table-borderless table-striped tablesorter" border="0" >
  <caption>${_("Minu tulemusi tohivad vaadata")}</caption>
  % if len(c.kasutaja.opilane_volitused) == 0:
  <tbody>
    <tr>
      <td colspan="3">${_("Tulemuste vaatamise õigust pole teistele antud")}</td>
    </tr>
  </tbody>
  % else:
  <thead>
    <tr>
      ${h.th(_("Isikukood"))}
      ${h.th(_("Nimi"))}
      <th></th>
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(c.kasutaja.get_volitatud()):
    <tr>
      <td>${rcd.isikukood}</td>
      <td>${rcd.nimi}</td>
      <td>${h.remove(h.url('tulemused_delete_volitus', id=rcd.id))}</td>
    </tr>
    % endfor
  </tbody>
  % endif
  <tfoot>
    <tr>
      <td colspan="3">
        ${_("Isikukood")}
        ${h.text('isikukood', c.isikukood, size=16, maxlength=50)}        
        ${h.submit(_("Lisa"))}
      </td>
    </tr>
  </tfoot>
</table>
${h.end_form()}
