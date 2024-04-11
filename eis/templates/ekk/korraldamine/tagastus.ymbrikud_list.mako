${h.pager(c.items)}
% if c.items:
<table width="100%" class="table table-borderless table-striped" border="0" >
  <thead>
    <tr>
      ${h.th_sort('tagastusymbrik.tahised', _("Tähis"))}
      ${h.th_sort('tagastusymbrikuliik.nimi', _("Ümbriku liik"))}
      ${h.th_sort('koht.nimi', _("Soorituskoht"))}
      ${h.th_sort('testipakett.lang', _("Keel"))}
      ${h.th_sort('tagastusymbrik.staatus', _("Olek"))}
      ${h.th_sort('kasutaja.perenimi kasutaja.eesnimi', _("Hindaja"))}
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(c.items):
    <%
       ymbrik, y_nimi, lang, koht_nimi, k_nimi = rcd
    %>
    <tr>
      <td>${ymbrik.tahised}</td>
      <td>
        % if ymbrik.tagastusymbrikuliik_id:
        ${y_nimi}
        % else:
        ${_("Peaümbrik")}
        % endif
      </td>
      <td>${koht_nimi}</td>
      <td>${model.Klrida.get_lang_nimi(lang)}</td>
      <td>${ymbrik.staatus_nimi}</td>
      <td>${k_nimi}</td>
    </tr>
    % endfor
  </tbody>
</table>
% endif
