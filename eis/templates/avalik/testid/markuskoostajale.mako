## Eeltesti korraldaja märkused eeltesti koostajale

${h.form_save(c.testiruum.id)}
${h.hidden('sub', 'markuskoostajale')}

${h.flb(_("Märkus "), 'sisu', rq=True)}
${h.textarea('sisu', c.markuskoostajale and c.markuskoostajale.sisu or '', rows=7)}
<br/>

${h.submit_dlg()}
${h.end_form()}
