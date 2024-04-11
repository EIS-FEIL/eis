## -*- coding: utf-8 -*- 
## normipunktide vastuste debug-info
## olemas: c.nptos, c.npvastused
<%
  testiosa = c.nptos.testiosa
  li2 = []
  for npv in c.npvastused:
     np = npv.normipunkt
     atg = np.alatestigrupp
     yg = np.ylesandegrupp
     seq = (atg and atg.seq or 0) * 10000 + (yg and yg.seq or 0) * 1000 + (np.seq or 0)
     li2.append((seq, npv, np, np.testiylesanne, yg, np.alatest, atg))
  li2.sort(key=lambda r: r[0])
  atgrupid = list(testiosa.alatestigrupid)
%>
% for atg in list(testiosa.alatestigrupid) + [None]:
<div>${atg and atg.nimi or ''}</div>
${self.list_npv(list(filter(lambda r: r[6] == atg, li2)))}
% endfor

<%def name="list_npv(li2)">
% if li2:
<% on_yl = len([r for r in li2 if r[3] or r[4] or r[5]]) %>
<table class="table table-borderless table-striped" >
  <thead>
    <tr>
      % if on_yl:
      <th>Ül/grupp/alatest</th>
      % endif
      <th>Normipunkt</th>
      <th>Kood</th>
      <th>Avaldis</th>
      <th>Tüüp</th>
      <th>Väärtus</th>
      <th>Tagasiside</th>
      <th>Loodud</th>
      <th>id</th>
    </tr>
  </thead>
  <tbody>
% for seq, nv, np, testiylesanne, ylesandegrupp, alatest, atg in li2:
<tr>
  % if on_yl:
  <td>
    % if testiylesanne:
    Ül ${testiylesanne.tahis}
    % elif ylesandegrupp:
    Grupp ${ylesandegrupp.nimi}
    % elif alatest:
    Alatest ${alatest.nimi}
    % endif
  </td>
  % endif
  <td>${np.nimi}</td>
  <td>${np.kood}</td>
  <td style="overflow-wrap:anywhere">
    ${np.kysimus_kood}
    % if np.normityyp == const.NORMITYYP_VASTUS:
    ## leiame ylesanded, kus sellise koodiga kysimus esineb
    <%
      q = (model.SessionR.query(model.Testiylesanne.tahis, model.Valitudylesanne.ylesanne_id)
           .join(model.Testiylesanne.valitudylesanded)
           .join((model.Ylesandevastus,
                  model.Ylesandevastus.valitudylesanne_id==model.Valitudylesanne.id))
           .filter(model.Ylesandevastus.sooritus_id==c.nptos.id)
           .join(model.Ylesandevastus.kysimusevastused)
           .join((model.Kysimus, model.Kysimus.id==model.Kysimusevastus.kysimus_id))
           .filter(model.Kysimus.kood==np.kysimus_kood)
           .order_by(model.Testiylesanne.alatest_seq, model.Testiylesanne.seq))
    %>
    % for k_ty_tahis, k_y_id in q.all():
    (${k_ty_tahis} ül ${k_y_id})
    % endfor
    % endif

    % if nv.viga:
    ${h.alert_error2(nv.viga)}
    % endif
  </td>
  <td>
    ${np.normityyp_nimi}
  </td>
  <td>
    ${nv.get_str_value()}        
  </td>
  <td>
    <% npts = nv.nptagasiside %>
    % if npts:
    ${npts.tagasiside}
    % endif
  </td>
  <td>
    ${h.str_from_datetime(nv.created, True)}
  </td>
  <td>
    np${np.id}
    ns${nv.nptagasiside_id}
    nv${nv.id}
  </td>
</tr>
% endfor
</tbody>
</table>
% endif
</%def>
