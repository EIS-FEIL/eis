## -*- coding: utf-8 -*- 
${h.pager(c.items)}
% if c.items:
<table class="table table-borderless table-striped">
  <thead>
    <tr>
      ${h.th_sort('test.nimi', _("Testi nimetus"))}
      ${h.th_sort('toimumisaeg.tahised', _("Toimumisaeg"))}
      ##${h.th_sort('labiviija.lang', _("Keel"))}
      ${h.th(_("Soorituskoht ja -ruum"))}
      ${h.th_sort('testiruum.algus', _("Algus"))}
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(c.items):
    <% 
       testiruum, testikoht, test, ta = rcd
       url_edit = h.url('svastamine_vastajad', testiruum_id=testiruum.id)
    %>
    <tr>
      <td>
        ${h.link_to(test.nimi, url_edit)}
      </td>
      <td>${ta.tahised}</td>
      ##<td>${model.Klrida.get_lang_nimi(lv.lang)}</td>
      <td>
        ${testikoht.koht.nimi}
        ${testiruum.tahis}
      </td>
      <td>
        ${h.str_from_datetime(testiruum.algus)}
      </td>
    </tr>
    % endfor
  </tbody>
</table>
% endif
