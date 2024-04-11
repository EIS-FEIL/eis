${h.form_save(c.testiruum.id)}
${h.hidden('sub', 'markus')}
${h.hidden('sooritus_id', c.sooritus.id)}

% if c.sooritus.stpohjus:
<div class="mb-3">
  <div>${c.sooritus.staatus_nimi}</div>
  <div>${c.sooritus.stpohjus}</div>
</div>
% endif

${_("Märkus testisooritaja {s} kohta").format(s=c.sooritus.sooritaja.kasutaja.nimi)}<br/>
${h.textarea('markus', c.sooritus.markus, cols=70, rows=7)}
</p>

<div class="text-right">
  ${h.submit()}
</div>
${h.end_form()}
