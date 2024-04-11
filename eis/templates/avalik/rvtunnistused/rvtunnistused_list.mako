## -*- coding: utf-8 -*- 
## $Id: rvtunnistused_list.mako 724 2016-06-03 11:08:19Z ahti $         
${h.pager(c.items)}
% if c.items:
<table width="100%" class="table table-borderless table-striped" border="0" >
  <thead>
    <tr>
      ${h.th_sort('rveksam.nimi',  _('Tunnistus'))}
      ${h.th_sort('tunnistus.tunnistusenr',  _('Tunnistuse nr'))}
      ${h.th_sort('tunnistus.valjastamisaeg',  _('Väljastamisaeg'))}
      ${h.th_sort('rvsooritaja.kehtib_kuni',  _('Kehtib kuni'))}
      ${h.th_sort('kasutaja.isikukood',  _('Isikukood'))}
      ${h.th_sort('tunnistus.eesnimi',  _('Eesnimi'))}
      ${h.th_sort('tunnistus.perenimi',  _('Perekonnanimi'))}
      ${h.th_sort('opilane.klass opilane.paralleel',  _('Klass'))}
      ${h.th_sort('rvsooritaja.keeletase_kood',  _('Tase'))}
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(c.items):
    <% 
       rvsooritaja, rveksam, tunnistus, kasutaja_ik, opilane = rcd
       ##url_show = h.url('otsing_rvtunnistus', id=rvsooritaja.id)
    %>
    <tr>
      <td>${rveksam.nimi}</td>
      <td>${tunnistus.tunnistusenr}</td>
      <td>${h.str_from_date(tunnistus.valjastamisaeg)}</td>
      <td>${h.str_from_date(rvsooritaja.kehtib_kuni)}</td>
      <td>${kasutaja_ik}</td>
      <td>${tunnistus.eesnimi}</td>
      <td>${tunnistus.perenimi}</td>
      <td>${opilane.klass} ${opilane.paralleel}</td>
      <td>${rvsooritaja.keeletase_kood}</td>
    </tr>
    % endfor
  </tbody>
</table>
% endif
