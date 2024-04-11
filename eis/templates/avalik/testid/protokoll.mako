<%inherit file="/common/formpage.mako"/>

<%def name="require()">
<%
  c.includes['idcard'] = True 
%>
</%def>

<%def name="page_title()">
${c.test.nimi or ''} | ${_("Läbiviimine")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(c.test.nimi or _('Test'))} 
${h.crumb(_('Protokoll'))}
</%def>

<%def name="draw_tabs()">
<%include file="tabs.mako"/>
</%def>

<div class="row">
  <div class="col-6">
    <b>
      % if not c.toimumisprotokoll or not c.toimumisprotokoll.has_file:
      ${_("Protokolli pole koostatud")}
      % elif c.toimumisprotokoll.staatus == const.B_STAATUS_EKK_KINNITATUD:
      ${_("Protokoll on kinnitatud eksamikeskuse poolt")}
      % elif c.toimumisprotokoll.staatus == const.B_STAATUS_KINNITATUD:
      ${_("Protokoll on kinnitatud")}      
      % else:
      ${_("Protokoll on kinnitamata")}
      % endif
    </b>
  </div>
  % if c.toimumisprotokoll and c.toimumisprotokoll.has_file:
  <div class="col-6">
    <!-- tpr ${c.toimumisprotokoll.id} -->
    <%
      ext = c.toimumisprotokoll.fileext
    %>
    % if ext in (const.BDOC, const.DDOC, const.ASICE):
    <% img = ' <img src="/static/images/bdoc.png" alt="BDOC" border="0"/>' %>
    ${h.btn_to(_("Laadi alla") + h.literal(img), h.url_current('download', format=ext, id=c.toimumisprotokoll.id))}
    % else:
    ${h.btn_to(_("Laadi alla"), h.url_current('download', format=ext, id=c.toimumisprotokoll.id), mdicls='mdi-file-pdf')}   
    % endif
  </div>
  % endif
</div>

<div class="row">
  <div class="col">
      ${h.form_save(None)}
      % if c.cnt_alustamata or c.cnt_pooleli:
      <div>${_("Protokolli ei saa koostada")}</div>
      % if c.cnt_alustamata:
      <div>${_("{n} sooritust on alustamata").format(n=c.cnt_alustamata)}</div>
      % endif
      % if c.cnt_pooleli:
      <div>${_("{n} sooritust on pooleli").format(n=c.cnt_pooleli)}</div>
      % endif
      <div>${_("Kui oled veendunud, et ükski sooritaja enam testi ei tee, siis vali läbiviimise vormil lõpetamata sooritajad ning kliki testi lõpetamise nupul")}</div>
      % endif

      % if c.toimumisprotokoll and c.toimumisprotokoll.has_file:
      % if c.toimumisprotokoll.staatus not in (const.B_STAATUS_KINNITATUD, const.B_STAATUS_EKK_KINNITATUD):
      ${h.submit(_('Koosta protokoll uuesti'), id='genereeri')}
      % endif
      % elif c.is_edit:
      ${h.submit(_('Koosta protokoll'), id='genereeri')}
      % endif
      ${h.end_form()}
  </div>
</div>

## Digiallkirjastamise väljad ja vormid
<div id="pluginLocation"></div>
<div id="error" style="color:red;"></div>

${h.form_save(None, form_name='form_prepare')}
${h.hidden('sub', 'prepare_signature')}
${h.hidden('cert_hex', '')}
${h.hidden('cert_id', '')}
${h.hidden('dformat', '')}
${h.end_form()}

${h.form_save(None, form_name='form_finalize')}
${h.hidden('sub', 'finalize_signature')}
${h.hidden('signature', '')}
${h.hidden('sig_no', '')}
${h.hidden('sesscode', '')}
${h.hidden('dformat', '')}
${h.end_form()}
