${h.pager(c.items,msg_not_found=_("Otsingu tingimustele vastavaid teste ei leitud"),
          msg_found_one=_("Leiti 1 test"),
          msg_found_many=_("Leiti {n} testi"))}
% if c.items:
<table width="100%" class="table table-borderless table-striped" border="0" >
  <thead>
    <tr>
      ${h.th_sort('test.id', _("ID"))}
      ${h.th_sort('test.nimi', _("Test"))}
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(c.items):
    <% 
       url_edit = h.url('nimekiri_test_nimekirjad', test_id=rcd.id)
    %>
    <tr>
      <td>${rcd.id}</td>
      <td>
        ${h.link_to(rcd.nimi, url_edit)}
      </td>
    </tr>
    % endfor
  </tbody>
</table>
% endif
