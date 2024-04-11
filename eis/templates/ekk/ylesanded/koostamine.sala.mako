<%include file="/common/message.mako" />

${h.form(h.url('ylesanded_update_koostamine', id=c.item.id), method='post',
id="dlg_form")}

${h.hidden('sub', c.sub)}

###############################################################
% if c.sub == 'secret':
## Salastame

${self.markused()}
<div class="text-right">
% if c.item.salastatud == const.SALASTATUD_POLE:
% if not c.ylesanne.has_permission('ylesanded', const.BT_UPDATE, None, c.user, salastatud=True):
${h.alert_notice(_("Soovid salastada ülesannet, mille salastatust sa ei saa ise lõpetada"))}
% endif
${h.submit(_("Salasta"), id="secret")}
% endif
</div>

###############################################################
% elif c.sub == 'nosecret':
## Lõpetame salastamise
   % if c.item.salastatud == const.SALASTATUD_POLE:
${_("Ülesanne pole salastatud")}
   % elif c.item.salastatud == const.SALASTATUD_SOORITATAV:
      ${self.markused()}
<div class="text-right">
  ${h.submit(_("Lõpeta salastatus"), id="nosecret")}
</div>
   % elif c.item.salastatud == const.SALASTATUD_LOOGILINE:
${self.markused()}
<div class="text-right">
  ${h.submit(_("Lõpeta salastatus"), id="nosecret")}
</div>
   % endif

% endif

${h.end_form()}

<%def name="markused()">
<p>
${_("Märkused")}<br/>
${h.textarea('markus', '', cols=65, rows=4)}
</p>
</%def>
