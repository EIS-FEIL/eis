
${h.form(h.url('ylesanded_update_juhised', id=c.item.id, fail_id=c.fail.id), method='put')}
${h.hidden('sub', 'markus')}
${h.hidden('ylem_id', c.ylem and c.ylem.id or '')}
<table width="100%">
  <tr>
    <td>${_("Teema")}</td>
    <td>${h.text('teema', c.ylem and c.ylem.teema or '', size=65, max_length=100)}</td>
  </tr>
  <tr>
    <td colspan="2">
      ${_("Märke sisu")}<br/>
      ${h.textarea('sisu', '', cols=70, rows=7)}
    </td>
  </tr>
</table>
${h.submit()}
${h.end_form()}
