<%inherit file="/common/dlgpage.mako"/>
${h.form_save(c.ylesanne.id)}
${h.hidden('sub', 'kogumikku')}
<% found = False %>
<table class="table table-striped">
  <caption>${_("Minu töökogumikud")}</caption>
  <tbody>
    % for tk_id, tk_nimi, y_cnt in c.opt_kogu:
    <tr>
      <td>${tk_nimi}</td>
      <td>
        % if y_cnt:
        ${_("sisaldab ülesannet")}
        % else:
        ${h.submit_dlg(_("Lisa"), op=tk_id)}
        <% found = True %>
        % endif
      </td>
    </tr>
    % endfor
  </tbody>
</table>
${h.end_form()}
% if not found:
${h.alert_notice(_("Ülesanne on juba töökogumikku lisatud!"), False)}
% endif
