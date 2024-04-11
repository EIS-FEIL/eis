${h.pager(c.items)}
% if c.items:
<table width="100%" class="table table-borderless table-striped" border="0" >
  <thead>
    <tr>
      ${h.th_sort('koht.nimi', _("Soorituskoht"))}
      ${h.th_sort('testiprotokoll.tahised', _("Ümbriku tähis"))}
      ${h.th_sort('tagastusymbrikuliik.nimi', _("Ümbriku liik"))}
      ${h.th_sort('kasutaja.nimi', _("Läbiviija"))}
    </tr>
  </thead>
  <tbody>
    % for rcd in c.items:
    <% ymbrik, tpr, testikoht, hindaja_nimi = rcd %>
    <tr>
      <td>${testikoht.koht.nimi}</td>
      <td>${tpr.tahised}-${ymbrik.tagastusymbrikuliik.tahis}</td>
      <td>${ymbrik.tagastusymbrikuliik.nimi}</td>
      <td>${hindaja_nimi}</td>
    </tr>
    % endfor
  </tbody>
</table>
% endif
