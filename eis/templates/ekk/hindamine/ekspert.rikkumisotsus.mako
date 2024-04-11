<%include file="/common/message.mako"/>
${h.form_save(c.sooritus.id, autocomplete='off')}
<div class="my-1">
  ${h.checkbox1('on_rikkumine', 1, checked=c.item.on_rikkumine,
  label=_("Rikkumise tõttu hinnata testitöö 0 punktiga"))}
</div>
<div class="my-1">
  ${h.flb(_("Põhjendus"), 'rikkumiskirjeldus')}
  ${h.textarea('rikkumiskirjeldus', c.item.rikkumiskirjeldus, rows=6)}
</div>
${h.submit_dlg(_("Salvesta"))}
${h.end_form()}
