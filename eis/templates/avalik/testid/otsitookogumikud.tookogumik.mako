% for tkosa in c.tookogumik.tkosad:
<div class="tkosa">
  ${tkosa.nimi}
  <table class="table table-borderless table-striped">
    <col width="20px"/>
    <thead>
      <tr>
        <th>${h.checkbox('all_id', 1, ronly=False, title=_("Vali kõik"))}</th>
        ${h.th('ID')}
        ${h.th(_('Nimetus'))}
        ${h.th(_('Pallid'))}
        ${h.th(_('Arvutiga hinnatav'))}
      </tr>
    </thead>
    <tbody>
    <%
      items = sorted(list(tkosa.tkylesanded), key=lambda r: r.seq)      
    %>
    % for r in items:
    <tr>
      % if isinstance(r, model.Tkylesanne):
      <%
        url = h.url('lahendamine', id=r.ylesanne_id)
      %>
      <td>
        ${h.checkbox('ylesanne_id', r.ylesanne_id, ronly=False, title=_("Vali rida {s}").format(s=r.ylesanne_id))}
      </td>
      <td>${r.ylesanne_id}</td>
      <td>${h.link_to(r.ylesanne.nimi, url, target='ykitem')}</td>
      <td>${h.fstr(r.ylesanne.max_pallid or 0)}p</td>
      <td>${h.sbool(r.ylesanne.arvutihinnatav)}</td>
      % endif
    % endfor
    </tbody>
  </table>
</div>
% endfor
