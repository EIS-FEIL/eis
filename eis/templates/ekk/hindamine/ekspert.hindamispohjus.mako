
${h.form_save(c.sooritus.id, autocomplete='off')}

<p>
${_("VI hindamise põhjus")}

${h.textarea('hindamispohjus', c.hindamine and c.hindamine.hindamispohjus or '', rows=6)}
</p>

${h.submit_dlg(_("Hinda"))}
${h.end_form()}
