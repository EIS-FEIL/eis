${h.form_save(None)}
% if not len(c.eksperthindajad):
${h.alert_error(_("Ekspertrühm on moodustamata"))}
% else:
<div class="mb-2">
  % for rcd in c.eksperthindajad:
  <div>
    ${h.checkbox('lv_id', rcd.id, checkedif=c.kasutusel, label=rcd.kasutaja.nimi)}
  </div>
  % endfor
</div>
<div class="text-right">
  ${h.submit()}
</div>
% endif
${h.end_form()}
