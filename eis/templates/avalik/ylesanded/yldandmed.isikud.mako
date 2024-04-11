
<%
  grupp_id = const.GRUPP_Y_KOOSTAJA
  ylesandeisikud = [r for r in c.item.ylesandeisikud if r.kasutajagrupp_id == grupp_id]
%>
% if ylesandeisikud:
<h3 class="mt-2">${_("Ülesande koostaja")}</h3>
<table border="0" class="table nowide table-borderless table-striped tablesorter">
  <col/>
  <col/>
  <col width="20px"/>
  <thead>
    <tr>
      ${h.th(_('Isikukood'))}
      ${h.th(_('Nimi'))}
      <th sorter="false"></th>
    </tr>
  </thead>
  <tbody>
    % for roll in ylesandeisikud:
    <% kasutaja = roll.kasutaja %>
    <tr>
      <td>${kasutaja.isikukood_hide}</td>
      <td>${kasutaja.nimi}</td>
      <td>
        % if len(ylesandeisikud) > 1:
        ${h.remove(h.url('ylesanne_delete_isik', ylesanne_id=c.item.id, id=roll.id))}
        % endif
      </td>
    </tr>
    % endfor    
  </tbody>
</table>
% endif
