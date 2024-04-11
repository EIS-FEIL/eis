<h2>${_("Registreeritud arvutid")}</h2>
<table id="arvutid_tbl" class="table table-striped tablesorter">
  <thead>
    <tr>
      % for value in c.arvutid_header:
      ${h.th(value)}
      % endfor
      <% n_lnk = len(c.arvutid_header) - 1 %>
    </tr>
  </thead>
  <tbody>
    % for rcd in c.arvutid_items:
    <% arvuti_id = rcd[0] %>
    <tr id="a${arvuti_id}">
      % for ind, value in enumerate(rcd[1:]):
      % if value and ind == n_lnk:
      <td>${h.remove(value)}</td>
      % else:
      <td>${value}</td>
      % endif
      % endfor
    </tr>
    % endfor
  </tbody>
  <tfoot>
    <tr>
      <%
        total_reg = len(c.arvutid_items)
        total = len(c.uniq_arvuti_id)
      %>
      % if total == total_reg: 
      <td colspan="5" class="brown">${_("Registreeritud on kokku {n} arvutit").format(n='<span id="cnt">%s</span>' % total)}</td>
      % else:
      <td colspan="5" class="brown">${_("Kokku on {n1} registreeringut {n} brauseris").format(n1=total_reg, n='<span id="cnt">%s</span>' % total)}</td>      
      % endif
    </tr>
  </tfoot>
</table>
