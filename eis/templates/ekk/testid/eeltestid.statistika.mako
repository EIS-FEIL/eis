
<table width="100%"  class="table table-striped" id="kys_index">
  <caption>${_("Ülesanded")}</caption>
  <thead>
    <tr>
      <th rowspan="2">${_("Jrk")}</th>
      <th rowspan="2">${_("Ülesande nimetus")}</th>
      <th rowspan="2">${_("Arvutihinnatav")}</th>
      <th colspan="2">${_("Toorpunktid")}</th>
      <th rowspan="2">${_("Koefitsient")}</th>
      <th rowspan="2">${_("Keskmine lahendusprotsent")}</th>
      <th rowspan="2">${_("Sooritajate arv")}</th>
    </tr>
    <tr>
      ${h.th(_("Keskmine"))}
      ${h.th(_("Max"))}
    </tr>
  </thead>
  <%
     total_mean = total_max = 0
  %>
  <tbody>
  % for rcd in c.items:
  <% 
     ylesanne, vy, ty, yst = rcd 
     total_max += ylesanne.max_pallid
     total_mean += yst and yst.keskmine or 0
     if c.testiruum:
        url_edit = h.url('labiviimine_edit_ylesanne',testiruum_id=c.testiruum.id,id=vy.id, lang=c.lang)
     elif c.statistika:
        url_edit = h.url('testitulemused_ylesanne', statistika_id=c.statistika.id,id=vy.id, lang=c.lang)
     else:
        url_edit = None
     jrk = ty.tahis
  %>
  <tr>
    <td>
      % if url_edit:
      ${h.link_to(jrk, url_edit)}
      % else:
      ${jrk}
      % endif
    </td>
    <td>
      % if url_edit:
      ${h.link_to(ylesanne.nimi, url_edit)}
      % else:
      ${ylesanne.nimi}
      % endif
    </td>
    <td>${h.sbool(ty.arvutihinnatav)}</td>
    <td>${h.fstr(yst and yst.keskmine)}</td>
    <td>${h.fstr(ylesanne.max_pallid)}</td>
    <td>${h.fstr(vy.koefitsient)}</td>
    <td>
      % if yst and yst.lahendatavus is not None:
      ${h.fstr(yst.lahendatavus)}%
      % endif
    </td>
    <td>
      % if yst:
      ${yst.sooritajate_arv or 0}
      % endif
    </td>
  </tr>
  % endfor
  </tbody>

  <tfoot>
    <tr>
      <th colspan="1">${_("Kokku")}</th>
      <th class="total-mean">${h.fstr(total_mean)}</th>
      <th class="total-max">${h.fstr(total_max)}</th>
      <th></th>
      <th>
        % if total_max:
        ${h.fstr(total_mean/total_max*100.)}%
        % endif
      </th>
      <th colspan="3" valign="center">
      </th>
    </tr>
  </tfoot>

</table>
