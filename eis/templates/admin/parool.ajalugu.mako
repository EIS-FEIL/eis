%   if len(c.items) == 0:
${_("Sellele kasutajale pole varem parooli antud")}
%   else:
${h.pager(c.items)}
<table class="table table-borderless table-striped" width="400px" border="0" >
  <caption>${_("Varasemad parooli omistamised")}</caption>
  <thead>
    <tr>
      ${h.th_sort('modifier', _("Muutja"))}
      ${h.th_sort('modified', _("Muutmise aeg"))}
    </tr>
  </thead>
  <tbody>
    <% modifiers = {} %>
    % for item in c.items:
    <%
      ik = item.modifier
      if ik not in modifiers:
         k = ik and model.Kasutaja.get_by_ik(ik)
         modifiers[ik] = k and k.nimi
      name = modifiers[ik]
    %>
    <tr>
      <td nowrap>
        ${item.modifier}
        ${name}
      </td>
      <td nowrap>
        ${h.str_from_datetime(item.modified)}
      </td>
    </tr>
    % endfor
  </tbody>
</table>
% endif
