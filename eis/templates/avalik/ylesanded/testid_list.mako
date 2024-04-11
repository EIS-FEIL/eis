## -*- coding: utf-8 -*- 
% if c.items != '':
${h.pager(c.items,msg_not_found=_("Ülesanne ei ole testides kasutusel"),
          msg_found_one=_("Leiti üks test"),
          msg_found_many=_("Leiti {n} testi"))}
% endif
% if c.items:
<table width="100%" class="table table-borderless table-striped" border="0" >
  <col width="120"/>
  <thead>
    <tr>
    ${h.th_sort('test.id', _("ID"))}
    ${h.th_sort('test.nimi', _("Nimetus"))}
    </tr>
  </thead>
  <tbody>
  % for n, rcd in enumerate(c.items):
    <tr>
      <td>
        ${rcd.id}
      </td>
      <td>
        ${h.link_to(rcd.nimi, url=h.url('edit_test', id=rcd.id))}
      </td>
    </tr>
  % endfor
  </tbody>
</table>
% endif
