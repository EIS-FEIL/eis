${h.pager(c.items)}
% if c.items:
<table width="100%" class="table table-borderless table-striped" border="0" >
  <thead>
    <tr>
      ${h.th_sort('test.id testimiskord.tahis', _("Tähis"))}
      ${h.th_sort('test_nimi', _("Testi nimetus"))}
      ${h.th_sort('alates', _("Aeg"))}
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(c.items):
    <% 
       t_id, t_nimi, aine, kursus, tk_id, tk_tahis, alates, kuni = rcd
       url_edit = h.url('ktulemused_kirjeldus', test_id=t_id, testimiskord_id=tk_id, kursus=kursus or '')
       if kursus:
          t_nimi += ' (%s)' % (model.Klrida.get_str('KURSUS', kursus, aine).lower())
    %>
    <tr>
      <td>
        ${t_id}-${tk_tahis}
      </td>
      <td>
        ${h.link_to(t_nimi, url_edit)}
      </td>
      <td>
        <%
           s_alates = h.str_from_date(alates)
           s_kuni = h.str_from_date(kuni)
        %>
        % if s_alates != s_kuni:
        ${s_alates} - ${s_kuni}
        % else:
        ${s_alates}
        % endif
      </td>
    </tr>
    % endfor
  </tbody>
</table>
% endif
