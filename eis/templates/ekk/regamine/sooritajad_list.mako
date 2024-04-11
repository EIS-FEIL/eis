## -*- coding: utf-8 -*- 
${h.pager(c.items)}
% if c.items:
<table width="100%" class="table table-borderless table-striped" border="0" >
  <caption>${_("Sooritajad")}</caption>
  <thead>
    <tr>
      ${h.th_sort('kasutaja.isikukood kasutaja.synnikpv', _("Isikukood või sünniaeg"))}
      ${h.th_sort('eesnimi', _("Eesnimi"))}
      ${h.th_sort('perenimi', _("Perekonnanimi"))}
    </tr>
  </thead>
  % for rcd in c.items:
  <tbody>
  <tr>
    <td>${rcd.kasutaja.isikukood or h.str_from_date(rcd.kasutaja.synnikpv)}</td>
    <td>${rcd.eesnimi}</td>
    <td>${rcd.perenimi}</td>
  </tr>
  </tbody>
  % endfor
</table>
% endif
