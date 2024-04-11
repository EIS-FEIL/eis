<%inherit file="/common/page.mako"/>
<%def name="require()">
<% c.includes['idcard'] = True %>
</%def>

<%def name="page_title()">
${_("Digiallkirjastamise testimine")}
</%def>      

## Digiallkirjastamise väljad ja vormid
<div id="pluginLocation"></div>
<div id="error" style="color:red;"></div>

% if c.item:
<div>
${h.form_save(c.item.id, form_name='form_prepare')}
${h.hidden('sub', 'prepare_signature')}
${h.hidden('cert_hex', '')}
${h.hidden('cert_id', '')}
${h.hidden('phoneno', c.user.telefon)}
${h.hidden('dformat', '')}
${h.end_form()}

${h.form_save(c.item.id, form_name='form_finalize')}
${h.hidden('sub', 'finalize_signature')}
${h.hidden('signature', '')}
${h.hidden('signature_id', '')}
${h.hidden('container_id', '')}
${h.hidden('dformat', '')}
${h.end_form()}
</div>
% endif

${_("Digiallkirjastamise testimine")}
<%include file="/common/message.mako"/>

<div class="p-2">
  ${h.form_save(None)}
  ${h.submit(_("Loo uus tekstidokument"))}
  ${h.end_form()}
</div>

% if c.item:
<div class="d-flex flex-wrap p-2">
  <div class="flex-grow-1">
    ${h.button(_("Allkirjasta smart-ID abil"), onclick='smartidSign()')}
    ${h.button(_("Allkirjasta mobiil-ID abil"), onclick='mobileSign()')}
    ${h.button(_("Allkirjasta ID-kaardiga"), onclick='getCert()')}
  </div>

  <% ext = c.item.filename.split('.')[-1] %>
  ${h.btn_to(_("Laadi alla") + ' ' + ext, h.url_current('download', id=c.item.id, format=ext))}
  % if ext == 'asice' and not c.signers:
  ${h.btn_to(_("Näita allkirjastajad") + ' .asice', h.url_current('show', id=c.item.id, signers=1))}      
  % endif
</div>

% if c.signers:
<div class="p-2">
  % for value in c.signers:
  ${value}<br/>
  % endfor
</div>
% endif
% endif

<div id="ddoc_status"> </div>
