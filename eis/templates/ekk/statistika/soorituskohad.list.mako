${h.pager(c.items, msg_not_found=_("Toimumisaegu ei leitud"), msg_found_one=_("Leiti 1 toimumisaeg"), msg_found_many=_("Leiti {n} toimumisaega"))}
% if c.items:

<% 
   colspan = 0
   if c.ruumid:
      colspan += 2
   if c.sooritajad:
      colspan += len(c.keeled) + 1 
   if c.vaatlejad:
      colspan += 1
%>

## c.items on jada toimumisaegade andmetest ta_data

## ta_data on jada, milles:
## - esimene liige on toimumisaja tähis
## - teine kuni eelviimane liige on piirkonna andmed prk_data
## - viimane liige on toimumisaja koond [None, {KEELED}, kokku, vaatlejaid]

## prk_data on jada, milles:
## - esimene liige on piirkonna nimi
## - teine kuni eelviimane liige on soorituskoha andmed 
##   [koha nimi, paev, ruumide arv, {KEELED}, kokku, vaatlejaid, [SUUNATUD]]
## - viimane liige on piirkonna koond [None, {KEELED}, kokku, vaatlejaid]

## suunatud koolide jada on jada koolidest, mille õpilased on 
## sellesse kohta suunatud sooritama
## jada element on kujul [kooli nimi, {KEELED}, kokku]


<table width="100%" class="table table-borderless table-striped" border="0" >
  <col width="20px"/>
  <col width="20px"/>
  <col width="20px"/>
  <col width="200px"/>
  % if c.ruumid:
  <col width="100px"/>
  <col width="100px"/>
  % endif
  % if c.sooritajad:
  % for lang in c.keeled:
  <col width="80px"/>
  % endfor
  <col width="80px"/>
  % endif
  % if c.vaatlejad:
  <col width="80px"/>
  % endif
  <thead>
    <tr>
      <th colspan="4"></th>
      % if c.ruumid:
      <th>${_("Kuupäev")}</th>
      <th>${_("Ruumide arv")}</th>
      % endif
      % if c.sooritajad:
      % for lang in c.keeled:
      <th>${model.Klrida.get_lang_nimi(lang)}</th>
      % endfor
      <th>${_("Kokku")}</th>
      % endif
      % if c.vaatlejad:
      <th>${_("Vaatlejaid")}</th>
      % endif
    </tr>
  </thead>
  <tbody>
% for ta_data in c.items:
    <tr>
      <td colspan="4">
        <b><i>${ta_data[0]}</i></b>
      </td>
      <td colspan="${colspan}"></td>
    </tr>
  % for prk_data in ta_data[1:-1]:
    <tr>
      <td></td>
      <td colspan="3"><b>${prk_data[0]}</b></td>
      <td colspan="${colspan}"></td>
    </tr>
    % for rcd in prk_data[1:-1]:
    <tr>
      <td colspan="2"></td>
      <td colspan="2">${rcd[0]}</td>
      % if c.ruumid:
      <td>${h.str_from_date(rcd[1])}</td>
      <td>${rcd[2]}</td>
      % endif
      % if c.sooritajad:
      % for lang in c.keeled:
      <td>${rcd[3].get(lang) or 0}</td>
      % endfor
      <td>${rcd[4]}</td>
      % endif
      % if c.vaatlejad:
      <td>${rcd[5]}</td>
      % endif
    </tr>
       % if rcd[6]:
           ## suunatud koolid
           % for rcd2 in rcd[6]:
    <tr>
      <td colspan="3"></td>
      <td><i>${rcd2[0]}</i></td>
      % if c.ruumid:
      <td colspan="2"></td>
      % endif
      % for lang in c.keeled:
      <td>${rcd2[1].get(lang) or 0}</td>
      % endfor
      <td>${rcd2[2]}</td>
      % if c.vaatlejad:
      <td></td>
      % endif
    </tr>
           % endfor
       % endif 
    % endfor

    % if c.sooritajad:
    <% rcd = prk_data[-1] %>
    <tr>
      <td colspan="1"></td>
      <td colspan="3"><b>${_("Soorituspiirkonnas kokku")}</b></td>
      % if c.ruumid:
      <td colspan="2"></td>
      % endif
      % for lang in c.keeled:
      <td><b>${rcd[1].get(lang) or 0}</b></td>
      % endfor
      <td><b>${rcd[2]}</b></td>
      % if c.vaatlejad:
      <td><b>${rcd[3]}</b></td>
      % endif
    </tr>
    % endif

  % endfor

  % if c.sooritajad:
  <% rcd = ta_data[-1] %>
    <tr>
      <td colspan="4"><b><i>${_("Toimumisajal kokku")}</i></b></td>
      % if c.ruumid:
      <td colspan="2"></td>
      % endif
      % for lang in c.keeled:
      <td><b><i>${rcd[1].get(lang) or 0}</i></b></td>
      % endfor
      <td><b><i>${rcd[2]}</i></b></td>
      % if c.vaatlejad:
      <td><b><i>${rcd[3]}</i></b></td>
      % endif
    </tr>
  % endif
% endfor
  </tbody>
</table>
% endif
