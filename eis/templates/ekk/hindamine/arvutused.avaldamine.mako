## Testimiskorra tulemuste avaldamise seadete muutmise vorm

${h.form_save(None, form_name="form_save_dlg")}
${h.hidden('sub', 'avaldamine')}

<table width="100%" class="table"  cellpadding="4">
  <tr>
    <td>
      ${h.checkbox('koondtulemus_avaldet', 1,
      checked=c.testimiskord.koondtulemus_avaldet, 
      label=_("Koondtulemus avaldatud"))}
    </td>
  </tr>
  <tr>
    <td>
      ${h.checkbox('alatestitulemused_avaldet', 1,
      checked=c.testimiskord.alatestitulemused_avaldet, 
      label=_("Alatestide lõikes tulemused avaldatud"))}
    </td>
  </tr>
  <tr>
    <td>
      ${h.checkbox('ylesandetulemused_avaldet', 1,
      checked=c.testimiskord.ylesandetulemused_avaldet, 
      label=_("Ülesannete lõikes tulemused avaldatud"))}
    </td>
  </tr>
  <tr>
    <td>
      ${h.checkbox('aspektitulemused_avaldet', 1,
      checked=c.testimiskord.aspektitulemused_avaldet, 
      label=_("Aspektide lõikes tulemused avaldatud"))}
    </td>
  </tr>
  <tr>
    <td>
      ${h.checkbox('ylesanded_avaldet', 1,
      checked=c.testimiskord.ylesanded_avaldet, 
      label=_("Ülesanded ja vastused avaldatud"))}
    </td>
  </tr>
</table>
${h.submit_dlg()}
${h.end_form()}
