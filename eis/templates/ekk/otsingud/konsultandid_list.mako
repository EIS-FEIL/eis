% if c.items != '':
${h.pager(c.items)}
% endif
% if c.items:
<table width="100%" class="table table-borderless table-striped" border="0" >
  <caption>${_("Konsultantide aruanne")}</caption>
  <thead>
    <tr>
      ${h.th_sort('kasutaja.isikukood', _("Isikukood"))}
      ${h.th_sort('kasutaja.eesnimi', _("Eesnimi"))}
      ${h.th_sort('kasutaja.perenimi', _("Perekonnanimi"))}
      ${h.th_sort('toimumisaeg.tahised', _("Toimumisaja tähised"))}
      ${h.th_sort('test.nimi', _("Test"))}
      ${h.th_sort('koht.nimi', _("Soorituskoht"))}
      ${h.th_sort('testiruum.algus', _("Aeg"))}
      ${h.th(_("Maksumus"))}
      ${h.th_sort('kasutaja.epost', _("E-post"))}
    </tr>
  </thead>
  <tbody>
    <% header, items = c.prepare_items(c.items) %>
    % for n, rcd in enumerate(items):
    <tr>
      % for s in rcd:
      <td>${s}</td>
      % endfor
    </tr>
    % endfor
  </tbody>
</table>
% endif
