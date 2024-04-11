${h.pager(c.items)}
<table class="table table-borderless table-striped" width="100%" border="0" >
  <tr>
    ${h.th(_("Alatestid"))}
    ${h.th_sort('komplekt.tahis', _("Ülesandekomplekt"))}
    ${h.th_sort('testifail.nimi', _("Nimetus"))}
    ${h.th_sort('testifail.filename', _("Fail"))}
    ${h.th(_("Märkused"))}
    <th width="120px"></th>
  </tr>
  % for item in c.items:
  <tr>
    <td>${item.komplekt.komplektivalik.str_alatestid}</td>
    <td>${item.komplekt.tahis}</td>
    <td>${item.nimi}</td>
    <td>
      ${h.link_to(item.filename, h.url('test_fail', test_id=c.test.id,
      id='%s.%s' % (item.id,item.fileext or 'file')))}
    </td>
    <td>
      % if c.can_update or c.user.has_permission('ekk-testid-failid', const.BT_UPDATE, obj=c.test):
      ${h.btn_to_dlg(u'Lisa märge', 
           h.url('test_edit_fail', test_id=c.test.id, id=item.id, sub='markus', partial=True), 
      title=_("Märkus"), width=600, level=2, mdicls='mdi-plus')}
      % endif

      % if len(item.testifailimarkused):
      ${h.btn_to_dlg(u'Märked (%s)' % len(item.testifailimarkused), 
      h.url('test_fail', test_id=c.test.id, id=item.id, sub='markus', partial=True),
      title=_("Märked"), width=600, level=2)}
      % endif
    </td>
    <td>
      ${h.bremove(h.url('test_delete_fail', test_id=c.test.id, id=item.id))}
    </td>
  </tr>
  % endfor
</table>
