<%
   on_alatestid = c.testiosa.on_alatestid
%>
<table width="100%" class="table table-striped" id="kys_index">
  <caption>${_("Ülesanded")}</caption>
  <thead>
    <tr>
      <th rowspan="2">${_("Jrk")}</th>
      % if on_alatestid:
      <th rowspan="2">${_("Alatest")}</th>
      % endif
      <th rowspan="2">${_("Ülesande nimetus")}</th>
      <th rowspan="2">${_("Arvutihinnatav")}</th>
      <th colspan="2">${_("Toorpunktid")}</th>
      <th rowspan="2">${_("Koefitsient")}</th>
      <th rowspan="2">${_("Keskmine lahendus-<br/>protsent")}</th>
      % if c.test.testiliik_kood==const.TESTILIIK_KOOLIPSYH:
      <th colspan="3">${_("Aeg")}</th>
      % endif
      <th rowspan="2">${_("Sooritajate arv")}</th>
    </tr>
    <tr>
      ${h.th(_('Keskmine'))}
      ${h.th(_('Max'))}
      % if c.test.testiliik_kood==const.TESTILIIK_KOOLIPSYH:
      ${h.th(_('Keskmine'))}
      ${h.th(_('Min'))}
      ${h.th(_('Max'))}
      % endif
    </tr>
  </thead>
  <%
     total_mean = total_max = 0
  %>
  <tbody>
  % for rcd in c.items:
  <% 
     ylesanne, vy, ty, yst = rcd 
     total_max += ylesanne.max_pallid or 0
     total_mean += yst and yst.keskmine or 0
     url_edit = h.url('test_hindamine_edit_ylesanne',test_id=c.test_id,testiruum_id=c.testiruum.id,id=vy.id, lang=c.lang)
  %>
  % if ty.liik == const.TY_LIIK_Y:
  <tr>
    <td>
      % if url_edit:
      ${h.link_to(ty.tahis, url_edit)}
      % else:
      ${ty.tahis}
      % endif
    </td>
    % if on_alatestid:
    <td>${ty.alatest.nimi}</td>
    % endif
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
    % if c.test.testiliik_kood==const.TESTILIIK_KOOLIPSYH:
    <td>${h.str_from_time_sec(yst and yst.aeg_avg)}</td>
    <td>${h.str_from_time_sec(yst and yst.aeg_min)}</td>
    <td>${h.str_from_time_sec(yst and yst.aeg_max)}</td>    
    % endif
    <td>
      % if yst:
      ${yst.sooritajate_arv or 0}
      % endif
    </td>
  </tr>
  % endif
  % endfor
  </tbody>

  <tfoot>
    <tr>
      <th colspan="${on_alatestid and 4 or 3}">Kokku</th>
      <th class="total-mean">${h.fstr(total_mean)}</th>
      <th class="total-max">${h.fstr(total_max)}</th>
      <th></th>
      <th>
        % if total_max:
        ${h.fstr(total_mean/total_max*100.)}%
        % endif
      </th>
      % if c.test.testiliik_kood==const.TESTILIIK_KOOLIPSYH:
      <th colspan="4" valign="center"></th>
      % else:
      <th colspan="1" valign="center"></th>
      % endif
    </tr>
  </tfoot>

</table>
