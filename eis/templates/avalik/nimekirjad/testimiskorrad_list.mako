${h.pager(c.items,msg_not_found=_("Otsingu tingimustele vastavaid testimiskordi ei leitud"),
          msg_found_one=_("Leiti 1 testimiskord"),
          msg_found_many=_("Leiti {n} testimiskorda"))}
% if c.items:
<table width="100%" class="table table-borderless table-striped" border="0" >
  <thead>
    <tr>
      ${h.th_sort('testimiskord.test_id', _("ID"))}
      ${h.th_sort('test.nimi', _("Test"))}
      ${h.th_sort('testimiskord.tahis', _("Tähis"))}
      ${h.th_sort('reg_sooritaja_alates', _("Reg aeg (ise)"))}
      ${h.th_sort('reg_kool_alates', _("Reg aeg (kool)"))}
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(c.items):
    <% 
       url_edit = h.url('nimekirjad_testimiskord_korrasooritajad', testimiskord_id=rcd.id)
       test = rcd.test
       cnt = c.get_reg_arv(rcd.id)
    %>
    <tr>
      <td>${rcd.test_id}</td>
      <td>
        ${h.link_to(test.nimi, url_edit)}
        % if cnt:
        (${cnt})
        % endif
      </td>
      <td>
        ${h.link_to(rcd.tahis or '', url_edit)}
      </td>
      <td>
        % if rcd.reg_sooritaja:
        ${h.str_from_date(rcd.reg_sooritaja_alates)} - ${h.str_from_date(rcd.reg_sooritaja_kuni)}
        % endif
      </td>
      <td>
        % if rcd.reg_kool_ehis or rcd.reg_kool_eis or rcd.reg_kool_valitud:
        ${h.str_from_date(rcd.reg_kool_alates)} - ${h.str_from_date(rcd.reg_kool_kuni)}
        % endif
      </td>
      ##<td>${len(rcd.sooritajad)}</td>
    </tr>
    % endfor
  </tbody>
</table>
% endif
