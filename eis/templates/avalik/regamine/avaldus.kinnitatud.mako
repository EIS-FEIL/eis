<%inherit file="/common/formpage.mako"/>

<%def name="draw_tabs()">
<% c.tab1 = 'kinnitamine' %>
<%include file="avaldus.tabs.mako"/>
</%def>

<%def name="page_title()">
${_("Eksamile registreerimise taotluse sisestamine")}
</%def>      
<%def name="active_menu()">
<% c.menu1 = 'regamised' %>
</%def>

<%def name="breadcrumbs()">
${h.crumb(_('Registreerimine'), h.url('regamised'))} 
${h.crumb(_('Registreerimise taotluse sisestamine'))}
</%def>

<%
   m = request.session.pop_flash('notice2')
   messages = list(dict.fromkeys(m))
   sent_epost = messages and messages[0] or None
  
   regatud = [r for r in c.sooritajad if r.staatus in (const.S_STAATUS_REGATUD, const.S_STAATUS_TASUMATA)]
   teavitatud = [r for r in regatud if r.regteateaeg] 
%>
% if sent_epost:
<h1>${_("Palun kontrolli, kas said teavituse!")}</h1>
<div class="mb-5">
  ${_("Saatsime aadressile {email} teavituse registreeringust. Palun kontrolli, kas teavitus jõudis Sinuni!").format(email=sent_epost)}
</div>
% elif regatud:
<h1 class="mb-7">${_("Registreerimine on kinnitatud!")}</h1>
% else:
<h1 class="mb-7">${_("Registreerimine ei ole kinnitatud!")}</h1>
% endif

% if c.tasumata:
<%include file="avaldus.tasumine.mako"/>
% endif

${h.form_save(None)}

<%
  tyhistatav = False
  for sooritaja in c.sooritajad:
     if sooritaja.voib_reg():
         tyhistatav = True
         break
%>

<div class="d-flex flex-wrap my-3">
  <div class="flex-grow-1">
    % if c.kasutaja.epost:
    ${h.btn_to(_('Muuda e-posti aadress'), h.url('regamine_avaldus_isikuandmed', testiliik=c.testiliik), level=2)}
    % else:
    ${h.btn_to(_('Lisa e-posti aadress'), h.url('regamine_avaldus_isikuandmed', testiliik=c.testiliik), level=2)}
    % endif
    % if tyhistatav:
    ${h.btn_to(_("Tühista registreering"), h.url('regamine_avaldus_tyhista', testiliik=c.testiliik), level=2)}
    % endif
  </div>
  <div>
    % if regatud and teavitatud and c.kasutaja.epost:
    ${h.submit(_('Saada teavitus uuesti'), name="saadauuesti")}
    ${h.btn_to(_('Sain teavituse kätte'), h.url('regamised'))}
    % elif regatud and not c.tasumata and c.kasutaja.epost:
    ${h.submit(_('Saada teavitus'), name="saadauuesti")}
    ${h.btn_to(_('Tagasi'), h.url('regamised'))}
    % else:
    ${h.btn_to(_('Tagasi'), h.url('regamised'))}
    % endif
  </div>
</div>
${h.end_form()}

