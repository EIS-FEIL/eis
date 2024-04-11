<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Registreerimine")} ${c.item.kasutaja.nimi or ''}
</%def>      
<%def name="breadcrumbs()">
<% 
   c.sooritaja = c.item
   c.testimiskord = c.item.testimiskord 
   c.test = c.item.test
%>
${h.crumb(_("Tsentraalsed testid"))}
${h.crumb(_("Testi sooritajate määramine"), h.url('nimekirjad_testimiskorrad'))} 
${h.crumb('%s %s' % (c.test.nimi, c.testimiskord.tahised), h.url('nimekirjad_testimiskord_korrasooritajad', testimiskord_id=c.testimiskord.id))} 
${h.crumb(c.item.kasutaja.nimi)}
</%def>

<%def name="active_menu()">
<% c.menu1 = 'ekktestid' %>
</%def>

<% 
  c.kasutaja = c.item.kasutaja
  # regikuitk - õigus registreerimisinfole eeldusel, et kasutajal on olemas testimiskorrale regamise õigus
  c.can_update = c.user.has_permission('regikuitk', const.BT_UPDATE, obj=c.item)
%>
<h1>${c.kasutaja.nimi}</h1>
${h.form_save(c.item.id)}
<%include file="/ekk/regamine/regi.sisu.mako"/>
<div class="mt-2 d-flex flex-wrap">
  <div class="flex-grow-1">
    ${h.btn_back(url=h.url('nimekirjad_testimiskord_korrasooritajad',
    testimiskord_id=c.testimiskord.id))}
  </div>
  % if c.can_update and c.user.has_permission('nimekirjad', const.BT_CREATE, obj=c.testimiskord) and not c.sooritaja.muutmatu:

% if c.item.staatus == const.S_STAATUS_REGAMATA:
${h.btn_to(_('Kinnita registreering'), h.url('nimekirjad_avaldus_testid', id=c.item.kasutaja_id, testiliik=c.test.testiliik_kood))}
% endif

  % if c.item.kool_voib_tyhistada(c.user.koht_id, c.test.testiliik_kood):
${h.button(_("Tühista registreering"),
onclick="dialog_el($('div#tyhistamine'), 'Registreeringu tühistamine');", level=2)}
  % endif

  % endif
</div>
${h.end_form()}

<div id="tyhistamine" class="d-none">
  ${h.form_save(c.item.id, h.url_current('delete'), form_name="form_del", class_="form-del")}  
  <div class="form-group mb-3">
    ${h.flb3(_("Põhjus"),'pohjus')}
    ${h.textarea('pohjus', '', rows=4, ronly=False)}
  </div>
  ${h.submit(_("Tühista registreering"))}
  ${h.end_form()}
</div>
