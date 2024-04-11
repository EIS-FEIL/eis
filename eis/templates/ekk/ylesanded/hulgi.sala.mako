<%include file="/common/message.mako" />

${h.form(h.url('ylesanded_update_hulga', id=c.ylesanded_id), method='post',
id="dlg_form")}

${h.hidden('sub', c.sub)}

###############################################################
% if c.sub == 'secret':
## Salastame, võib-olla koos krüptimisega

${self.markused()}
<table width="100%" > 
<tr>
<td>
${h.submit(_("Salasta krüptimata"), id="secret")}
</td>
</tr>
</table>

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
