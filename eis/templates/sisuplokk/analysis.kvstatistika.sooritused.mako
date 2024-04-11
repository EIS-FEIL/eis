## -*- coding: utf-8 -*-
<table width="100%"  class="table table-borderless table-striped">
  <col width="33%"/>
  <col width="33%"/>
  <col width="33%"/>
  <thead>
    <tr>
      ${h.th(_("Toimumisaeg"))}
      ${h.th(_("Töö"))}
##      ${h.th(_("Isikukood"))}
    </tr>
  </thead>
  <tbody>
  % for tos_id, testiosa_id, ta_tahised, tos_tahised, ik in c.items:
  <tr>
    <td>${ta_tahised}</td>
    <td>${h.link_to(tos_tahised, h.url('tulemus_osa', test_id=c.test.id, testiosa_id=testiosa_id, alatest_id='', id=tos_id), tos_tahised)}</td>
##    <td>${ik}</td>
  </tr>
  % endfor
  </tbody>
</table>
