## Testimiskordade avaldamise seadete muutmise vorm

${h.form_save(None, form_name="form_save_dlg")}
${h.hidden('sub', 'avaldamine')}
${h.hidden('sessioon_id', c.sessioon_id)}
${h.hidden('list_url', c.list_url)}
% for kord in c.korrad:
${h.hidden('kord_id', kord.id)}
% endfor

<div class="my-2">
  <div>
      ${h.checkbox('koondtulemus_avaldet', 1,
      checked=c.koondtulemus_avaldet, 
      label=_("Koondtulemus avaldatud"))}
  </div>
  <div>
      ${h.checkbox('alatestitulemused_avaldet', 1,
      checked=c.alatestitulemused_avaldet, 
      label=_("Alatestide lõikes tulemused avaldatud"))}
  </div>
  <div>
      ${h.checkbox('ylesandetulemused_avaldet', 1,
      checked=c.ylesandetulemused_avaldet, 
      label=_("Ülesannete lõikes tulemused avaldatud"))}
  </div>
  <div>
      ${h.checkbox('aspektitulemused_avaldet', 1,
      checked=c.aspektitulemused_avaldet, 
      label=_("Aspektide lõikes tulemused avaldatud"))}
  </div>
  <div>
      ${h.checkbox('ylesanded_avaldet', 1,
      checked=c.ylesanded_avaldet, 
      disabled=c.ylesanded_avaldet,
      label=_("Ülesanded ja vastused avaldatud"))}
  </div>
</div>
<div class="text-right">
  ${h.submit_dlg()}
</div>
${h.end_form()}
