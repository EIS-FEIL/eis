<%include file="/common/message.mako" />

${h.form(h.url('testid_update_hulga', id=c.testid_id), method='post',
id="dlg_form")}

${h.hidden('sub', c.sub)}

###############################################################
% if c.sub == 'secret':
## Salastame

${self.markused()}
${h.submit(_("Salasta (sooritatav)"), id="secret1")}
${h.submit(_("Salasta"), id="secret")}

###############################################################
% elif c.sub == 'nosecret':
## Lõpetame salastamise

${self.markused()}
${h.submit(_("Lõpeta salastatus"), id="nosecret")}

% endif

${h.end_form()}

<%def name="markused()">
<p>
${_("Märkused")}<br/>
${h.textarea('markus', '', cols=65, rows=4)}
</p>
</%def>
