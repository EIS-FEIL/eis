${h.form_save(c.item.id)}

<p>
  ${h.flb(_("Rühma nimetus"), 'f_nimi')}
  ${h.text('f_nimi', c.item.nimi)}
</p>

<div class="text-right">
  ${h.submit_dlg()}
</div>
${h.end_form()}
