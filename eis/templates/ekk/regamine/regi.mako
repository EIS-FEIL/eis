## -*- coding: utf-8 -*- 
<%inherit file="/common/page.mako"/>

<%def name="page_title()">
${_("Registreerimine")}: ${c.item.nimi}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Registreerimine"), h.url('regamised'))}
${h.crumb(c.item.nimi, h.url('regamine',id=c.item.id))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'regamised' %>
</%def>

${h.form_save(c.item.id)}
<% 
   c.kasutaja = c.item.kasutaja
   c.sooritaja = c.item
   tkord = c.item.testimiskord
%>
<%include file="regi.sisu.mako"/>

% if c.item.tasu and not c.item.tasutud:
${h.submit(_("Kinnita tasumine"), id='tasutud', level=2)}

% if c.item.kasutaja.epost:
${h.btn_to(_("Meeldetuletus (e-postiga)"), 
h.url('regamine', id=c.item.id, sub='epost'), method='put', level=2)}
% endif

${h.btn_to(_("Meeldetuletus (PDF)"), 
h.url('regamine', id=c.item.id, sub='tpost'), method='put', level=2)}
% endif

% if c.item.staatus == const.S_STAATUS_TYHISTATUD and tkord and not tkord.reg_kohavalik:
${h.button(_("Taasta registreering"),
onclick="dialog_el($('div#tyhistamine'), 'Registreeringu taastamine', 600);", level=2)}

% elif c.item.staatus > const.S_STAATUS_TYHISTATUD and c.item.staatus < const.S_STAATUS_POOLELI:
${h.button(_("Tühista registreering"),
onclick="dialog_el($('div#tyhistamine'), 'Registreeringu tühistamine', 600);", level=2)}

% endif

${h.btn_to(_("Muuda"), h.url('edit_regamine', id=c.item.id), method='get')}
             
${h.end_form()}


<div id="tyhistamine" class="d-none">
  ${h.form_save(c.item.id, class_="form_save2")}
  <div class="form-group mb-3">
    ${h.flb3(_("Põhjus"))}
    ${h.textarea('pohjus', '', rows=4, ronly=False)}
  </div>
  % if c.item.staatus == const.S_STAATUS_TYHISTATUD:
  ${h.submit(_("Taasta registreering"), id='taasta')}
  % else:
  ${h.submit(_("Tühista registreering"), id='tyhista')}
  % endif
  ${h.end_form()}
</div>

