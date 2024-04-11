% if c.items != '' and not c.items:
${h.alert_notice(_("Sooritajaid ei ole"), False)}
% elif c.items:
<%
   oma_kavaaeg = c.testikoht.testiosa.oma_kavaaeg
   on_kursus = c.toimumisaeg.testiosa.test.on_kursused
   peidus = c.toimumisaeg.testimiskord.sooritajad_peidus
%>
<div>
  ${h.pager(c.items, msg_not_found=_("Sooritajaid ei leitud"), msg_found_one=_("Leiti 1 sooritaja"), msg_found_many=_("Leiti {n} sooritajat"))}
</div>
<div>
  ${h.alert_notice(_("Alloleva tabeli andmeid saab sortida, kui klõpsata sorditava veeru päisel. Kui soovite sortida mitme veeru andmeid, tuleb klõpsata kõigepealt esimese veeru päisel, hoida all Shift klahvi ning seejärel järgmise veeru päisel."), False)}
</div>

<table width="100%" class="table table-borderless table-striped" border="0" >
  <caption>${_("Sooritajad")}</caption>
  <thead>
    <tr>
      <th sorter="false">${h.checkbox1('alls',1, title=_("Vali kõik"))}</th>
      % for h_sort, h_title in c.header:
      ${h.th_sort(h_sort, h_title)}
      % endfor
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(c.items):
    <tr>
      <td>
        <%
          row, tos, n_aeg, n_opetajad = c.prepare_item(rcd, n, True)
          opetajaga = bool(row[n_opetajad]) and 'opetajaga' or ''
        %>
        ${h.checkbox('sooritus_id', tos.id, onchange="toggle_add()", class_=f"nosave sooritus_id {opetajaga}", title=_("Vali rida"))}
      </td>
      % for ind, value in enumerate(row):
      <td>
        % if ind == 0:
          ${value}
          ${h.hidden('s-%d.sooritus_id' % n, tos.id)}
        % elif ind == n_aeg and oma_kavaaeg:
          ${h.str_from_date(tos.kavaaeg)}
          ${h.time('s-%d.kellaaeg' % n, tos.kavaaeg)}
        % elif ind == n_opetajad:
           ## õpetajate nimed
          % for op_nimi in value:
          <div class="hasopet">${op_nimi}</div>
          % endfor
        % elif ind == 2:
          ${value}
          ${h.hidden('err_sooritus_%s' % tos.id,'')}   
        % else:
          ${value}
        % endif
      </td>
      % endfor
    </tr>
    % endfor
  </tbody>
</table>
% endif
