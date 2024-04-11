<%inherit file="/common/formpage.mako"/>
<%def name="require()">
<% c.includes['test'] = True %>
</%def>
<%def name="draw_tabs()">
<% c.tab1 = 'kanne' %>
<%include file="tabs.mako"/>
</%def>

<%def name="page_title()">
${c.test.nimi or ''} | ${_("Registreering")} ${c.item.kasutaja.nimi}
</%def>      
<%def name="breadcrumbs()">
% if c.test.on_jagatudtoo:
${h.crumb(_('Töölaud'), h.url('tookogumikud'))}
% endif
${h.crumb(c.test.nimi or _('Test'))} 
${h.crumb(c.nimekiri.nimi, h.url('test_nimekiri', test_id=c.test_id, testiruum_id=c.testiruum_id, id=c.nimekiri.id))}
${h.crumb(c.sooritaja.nimi)}
</%def>

${h.form_save(c.item.id)}
<% 
   c.kasutaja = c.item.kasutaja
   c.sooritaja = c.item
   c.regi_isikuandmeteta = True
%>
<%include file="/ekk/regamine/regi.sisu.mako"/>
<p>
${h.btn_back(url=h.url('test_nimekiri',
test_id=c.test.id, testiruum_id=c.testiruum_id, id=c.item.nimekiri_id))}

% if c.user.has_permission('nimekirjad', const.BT_CREATE, obj=c.test):

% if c.item.staatus < const.S_STAATUS_POOLELI and not c.item.muutmatu:
${h.button(_('Tühista registreering'),
onclick="dialog_el($('div#tyhistamine'), '${_('Registreeringu tühistamine')}', 600);", level=2)}
% endif

${h.btn_to_dlg(_("Määra tugiisik"), h.url('test_nimekiri_kanne_tugiisikud', nimekiri_id=c.item.nimekiri_id, sooritaja_id=c.item.id, test_id=c.test.id, testiruum_id=c.testiruum_id), level=2, title=_("Tugiisiku määramine"), size='md')}
% endif
</p>
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
