<%include file="/common/message.mako" />

${h.form(h.url('test_update_koostamine', id=c.item.id), method='put',
id="dlg_form")}

${h.hidden('sub', c.sub)}

###############################################################
% if c.sub == 'secret':
## Salastame

${self.markused()}
<div class="text-right">
% if c.item.salastatud == const.SALASTATUD_POLE:
${h.submit(_("Salasta (sooritatav)"), id="secret1")}
${h.submit(_("Salasta"), id="secret")}
% endif
</div>

###############################################################
% elif c.sub == 'nosecret':
## Lõpetame salastamise
   % if c.item.salastatud == const.SALASTATUD_POLE:
${_("Ülesanne pole salastatud")}
   % elif c.item.salastatud == const.SALASTATUD_KRYPTITUD:
      ${_("Salastamise lõpetamiseks tuleb esmalt ülesande sisu lahti krüptida")}
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
${h.textarea('markus', '', rows=4)}
</p>
</%def>

