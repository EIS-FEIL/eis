<%inherit file="/common/tabpage.mako"/>
<div id="hindamiskysimused_div">
<% c.r_tab = 'hindamiskysimused' %>
<%include file="hindamine_r_tabs.mako"/>
<div id="hindamine_r_body">
<%include file="/common/message.mako"/>

<% items = list(c.ylesanne.hindamiskysimused) %>
% if not items:
${h.alert_notice(_("Ei ole küsimusi"), False)}
% else:
<table class="table table-striped tablesorter vertmar">
  <thead>
    <tr>
      <th>${_("Küsimus")}</th>
      <th>${_("Vastus")}</th>
      <th>${_("Vastaja")}</th>
      <th>${_("Vastamise aeg")}</th>
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(items):
      % if rcd.avalik or rcd.kysija_kasutaja_id==c.user.id:
    <tr>
      <td>${rcd.kysimus}</td>
      <td>${rcd.vastus}</td>
      <td>
        % if rcd.vastaja_kasutaja:
        ${rcd.vastaja_kasutaja.nimi}
        % endif
      </td>
      <td>${h.str_from_datetime(rcd.vastamisaeg)}</td>
    </tr>
      % endif
    % endfor    
  </tbody>
</table>
% endif

<% disabled = bool(c.app_ekk) %>
${h.btn_to_dlg(_("Esita hindamisjuhile küsimus"), h.url_current('new', indlg=c.indlg),
  title=_("Küsimus"), width=560, dialog_id='dlghkys', disabled=disabled or None)}

<script>
  ## hindamiskysimuse esitamise dialoogiaken kinni
  close_dialog('dlghkys');
</script>
</div>
</div>
