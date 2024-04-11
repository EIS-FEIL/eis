${h.form_save(None)}
${h.hidden('sub', 'atg')}
<table width="100%">
  <col width="100"/>
  <col/>
  <col width="20px"/>
  <tr>
    <td class="fh">
      ${_("Grupi nimetus")}
    </td>
    <td>
      ${h.text('nimi', c.item.nimi, maxlength=75)}
    </td>
  </tr>
</table>
${h.submit_dlg()}
${h.end_form()}
