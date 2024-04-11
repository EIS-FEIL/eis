% if c.items:
</p>

% for (koht_nimi, ruum_tahis, li_sarnased) in c.items:
<br/>

<table width="100%" class="table table-borderless table-striped" border="0" >
<caption>${koht_nimi} ${ruum_tahis and ', %s %s' % (_("ruum"), ruum_tahis) or ''}</caption>
##  <col width="100"/>
##  <col width="70"/>
  <thead>
    <tr>
    ${h.th(_("Isikukood"))}
    ${h.th(_("Töökood"))}
    ${h.th(_("Vastused"), colspan=c.max_index)}
    ${h.th(_("Tulemus"))}
    ${h.th(u'ÕV')}
    ${h.th(u'H-H')}
    ${h.th(u'SVV')}
    ${h.th(u'MSV')}
    </tr>
  </thead>
  <tbody>
    % for rcd in li_sarnased:
    <% 
       li1, li2, hh, svv, msv = rcd
       [ik1, tahised1, pallid1, data1, oige1] = li1
       [ik2, tahised2, pallid2, data2, oige2] = li2
    %>
    <tr class="firstrow">
      <td>${ik1}</td>
      <td>${tahised1}</td>
      % for n in range(c.max_index):
      % if n in c.alatest_index:
      <td style="background-color:#f7a047;width:5px;">*</td>
      % else:
      <td>
        % if n in data1:
        ${' '.join(data1.get(n))}
        % endif
      </td>
      % endif
      % endfor
      <td>${h.fstr(pallid1)}</td>
      <td>${oige1}</td>
      <td rowspan="2">${h.fstr(hh)}</td>
      <td rowspan="2">${svv}</td>
      <td rowspan="2">${msv}</td>
    </tr>
    <tr>
      <td>${ik2}</td>
      <td>${tahised2}</td>
      % for n in range(c.max_index):
      % if n in c.alatest_index:
      <td style="background-color:#f7a047;width:5px;">*</td>
      % else:
      <td>
        % if n in data2:
        ${' '.join(data2.get(n))}
        % endif
      </td>
      % endif
      % endfor
      <td>${h.fstr(pallid2)}</td>
      <td>${oige2}</td>
    </tr>
    % endfor
  </tbody>
</table>
% endfor

<br/>
${_("Vastuste real punkt näitab õiget vastust")}
<br/>
${_("Vastuste real täht näitab vale vastust")}
<br/>
${_("ÕV - õiged vastused")}
<br/>
${_("H-H näitab sarnaste valevastuste ja mittesarnaste valevastuste suhet")}
<br/>
${_("SVV - sarnased valevastused")}
<br/>
${_("MSV - mittesarnased valevastused")}

% endif
