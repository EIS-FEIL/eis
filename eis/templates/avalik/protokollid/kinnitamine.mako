<%inherit file="/common/formpage.mako"/>

<%def name="require()">
<%
   c.includes['idcard'] = True 
%>
</%def>

<%def name="page_title()">
${_("Testi toimumise protokollimine")} | ${c.toimumisprotokoll.tahistus}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Tsentraalsed testid"))}
${h.crumb(_('Testi toimumise protokolli koostamine'), h.url('protokollid'))}
${h.crumb(c.toimumisprotokoll.tahistus, h.url('protokoll_osalejad', toimumisprotokoll_id=c.toimumisprotokoll.id))}
${h.crumb(_('Kinnitamine'))}
</%def>

<%def name="active_menu()">
<% c.menu1 = 'ekktestid' %>
</%def>

<%def name="draw_before_tabs()">
<%include file="/avalik/protokollid/before_tabs.mako"/>
</%def>

<%def name="draw_tabs()">
<%include file="/avalik/protokollid/tabs.mako"/>
</%def>

<% on_dok = c.toimumisprotokoll.has_file %>

<div class="form-wrapper-lineborder mb-2">
  % if c.is_edit:
  <div class="form-group row">
    ${h.flb3(_("Allkirjastatud protokoll"))}
    <div class="col">
      ${h.form_save(None, multipart=True)}
      ${h.file('protokoll_dok', value='Fail')}
      ${h.submit(_('Laadi üles'))}
      ${h.end_form()}
    </div>
  </div>
  % endif
  <div class="form-group row">
    <div class="col-md-3">
      % if not on_dok:
      ${_("Protokolli pole koostatud")}
      % elif c.toimumisprotokoll.staatus == const.B_STAATUS_EKK_KINNITATUD:
      ${_("Protokoll on kinnitatud")}
      % elif c.toimumisprotokoll.staatus == const.B_STAATUS_KINNITATUD:
      ${_("Protokoll on kinnitatud")}
      % else:
      ${_("Protokoll on kinnitamata")}
      % endif
      <% cnt = len(c.toimumisprotokoll.ruumifailid) %>
      % if cnt:
      <div>
        ${_("Lisatud {n} faili").format(n=cnt)}
      </div>
      % endif
    </div>
    <div class="col">
% if on_dok:
<%
  ext = c.toimumisprotokoll.fileext
%>
% if ext in (const.BDOC, const.DDOC, const.ASICE):
<%
  img = ' <img src="/static/images/bdoc.png" class="ml-2" alt="BDOC" border="0"/>'
%>
${h.btn_to(_("Laadi alla") + ' ' + h.literal(img), h.url('protokoll_kinnitamine1_format', format=ext, toimumisprotokoll_id=c.toimumisprotokoll.id, id='0'))}
% else:
${h.btn_to(_("Laadi alla"), h.url('protokoll_kinnitamine1_format', format=ext, toimumisprotokoll_id=c.toimumisprotokoll.id, id='0'), mdicls='mdi-file-pdf')}
% endif
% endif
    </div>
  </div>
</div>

<div class="d-flex flex-wrap">
  <div>
    % if c.can_edit:
    ${h.form_save(None)}
    % if not on_dok:
    ${h.submit(_('Koosta protokolli eelvaade'), id='preview')}
    ${h.submit(_('Koosta protokoll'), id='genereeri')}
    % elif c.toimumisprotokoll.staatus not in (const.B_STAATUS_EKK_KINNITATUD, const.B_STAATUS_KINNITATUD):
    ${h.submit(_('Koosta protokoll uuesti'), id='genereeri')}
    % endif
    ${h.end_form()}
    % endif
  </div>

  % if on_dok:
  <div class="text-right flex-grow-1">
      % if c.toimumisprotokoll.fileext != const.DDOC:
      ${h.button(_("Allkirjasta smart-ID abil"), onclick='smartidSign()')}
      ${h.button(_('Allkirjasta mobiil-ID abil'), onclick='mobileSign()')}
      ${h.button(_('Allkirjasta ID-kaardiga'), onclick='getCertBdoc()')}
      % endif
      <div id="ddoc_status" class="p-3"></div>
  </div>
% endif
</div>

## Digiallkirjastamise väljad ja vormid
<div id="pluginLocation"></div>
<div id="error" style="color:red;"></div>

${h.form_save(None, form_name='form_prepare')}
${h.hidden('sub', 'prepare_signature')}
${h.hidden('cert_hex', '')}
${h.hidden('cert_id', '')}
${h.hidden('phoneno', c.user.telefon)}
${h.hidden('dformat', '')}
${h.end_form()}

${h.form_save(None, form_name='form_finalize')}
${h.hidden('sub', 'finalize_signature')}
${h.hidden('signature', '')}
${h.hidden('signature_id', '')}
${h.hidden('container_id', '')}
${h.hidden('dformat', '')}
${h.end_form()}
