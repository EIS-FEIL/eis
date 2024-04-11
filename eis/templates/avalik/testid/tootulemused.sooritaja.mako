${h.not_top()}
% for tos in c.sooritaja.sooritused:
<table class="table table-borderless table-striped" width="100%" >
  <thead>
    <tr>
      <th>${_("Jrk")}</th>
      <th>${_("Ülesanne")}</th>
      <th>${_("Lahendamiste arv")}</th>
      <th>${_("Viimase lahendamise tulemus")}</th>
      <th>${_("Viimase lahendamise aeg")}</th>
    </tr>
  </thead>
  <tbody>
    % for rcd in c.ylesanded:
    <%
      ty_seq, ty_id, vy_id, y_nimi, cnt, pallid, max_pallid, ajakulu, yv_id = rcd
      if max_pallid and pallid is not None:
         prot = '%s%%' % h.fstr(pallid * 100. / max_pallid, 0)
      else:
         prot = None
      li_hist = c.yvhist.get(vy_id)
      li_aeg = c.yvaeg.get(vy_id)
    %>
    <tr>
      <td>${ty_seq}</td>
      <td>
        ${y_nimi}
      </td>
      <td>${cnt or 0}</td>
      <td>
        % if li_hist:
        <span style="cursor:pointer;text-decoration:underline" onclick="$(this).closest('td').find('div.yvhist').toggle()">${prot}</span>
        <div class="yvhist" style="display:none">
          ${_("Eelmised lahendamised:")} ${', '.join(li_hist)}
        </div>
        % else:
        ${prot}
        % endif
      </td>
      <td>
        % if li_aeg:
        <span style="cursor:pointer;text-decoration:underline" onclick="$(this).closest('td').find('div.yvaeg').toggle()">${h.str_from_time_sec(ajakulu)}</span>
        <div class="yvaeg" style="display:none">
          ${_("Eelmised lahendamised:")} ${', '.join(li_aeg)}
        </div>
        % else:
        ${h.str_from_time_sec(ajakulu)}
        % endif
      </td>
    </tr>
    % endfor
  </tbody>
</table>
<br/>
${h.btn_to(_('Vaata tööd'), h.url('test_labiviimine_sooritus', test_id=c.test_id, testiruum_id=tos.testiruum_id, id=tos.id))}
% endfor
