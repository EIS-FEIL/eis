
${h.form_save(c.item.id)}
${h.hidden('sub', 'test')}
${h.hidden('f_test_id', c.f_test.id)}
<table class="table" width="100%" >
  <caption>${_("Test")}</caption>
  <tr>
    <td>
      ${c.f_test.nimi}
    </td>
  </tr>
</table>

<table class="table table-borderless table-striped" width="100%" >
  <caption>${_("Testimiskorrad")}</caption>
  % for rcd in c.f_test.testimiskorrad:
     % if rcd in c.item.testimiskorrad:
        <% checked = True %>
  <tr class="selected">
     % else:
        <% checked = False %>
  <tr>
     % endif
    <td>
      ${h.checkbox('kord_id', rcd.id, checked=checked, class_="selectrow")}
    </td>
    <td>
      ${h.link_to('%s %s' % (rcd.test.nimi, rcd.tahis), 
          h.url('test_kord', test_id=rcd.test.id, id=rcd.id), target='_blank')}
    </td>
  </tr>
  % endfor
</table>
${h.submit()}
${h.end_form()}
