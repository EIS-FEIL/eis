<%inherit file="/common/formpage.mako"/>
<%def name="draw_tabs()">
<% c.tab1 = 'yldandmed' %>
<%include file="tabs.mako"/>
</%def>
<%def name="page_title()">
% if c.item.on_jagatudtoo:
${c.item.nimi or ''} | ${_("Töö kirjeldus")}
% else:
${c.item.nimi or ''} | ${_("Testi kirjeldus")}
% endif
</%def>      
<%def name="active_menu()">
<% c.menu1 = 'tookogumikud' %>
</%def>

<%def name="breadcrumbs()">
${h.crumb(_('Minu töölaud'), h.url('tookogumikud'))}
${h.crumb(c.item.nimi or _('Test'))}
</%def>
% if not c.item.id or c.action == 'create':
${h.form_save(c.item.id, h.url('create_testid'))}
% else:
${h.form_save(c.item.id, h.url('testid_update_yldandmed', id=c.item.id, testiruum_id=c.testiruum_id))}
% endif
<%
   testiosa = c.item.get_testiosa()
%>
${h.rqexp()}
<% ch = h.colHelper('col-md-2', 'col-md-4') %>
<div class="form-wrapper mb-2">
  <div class="form-group row">
    ${ch.flb(_("ID"), 'id')}
    <div class="col" id="id">
      ${c.item.id}
    </div>
  </div>
  <div class="form-group row">
    ${ch.flb(_("Nimetus"),'f_nimi', rq=True)}
    <div class="col">
      ${h.text('f_nimi', c.item.nimi)}
    </div>
  </div>
  <div class="form-group row">
    ${ch.flb(_("Õppeaine"),'aine_kood', rq=True)}
    <div class="col">
      ${h.select2('aine_kood', c.item.aine_muu or c.item.aine_kood, 
      c.opt.klread_kood('AINE', empty=True, vaikimisi=c.item.aine_muu or c.item.aine_kood), tags=True,
      selectOnClose=True)}
    </div>
  </div>
  <div class="form-group row">
    ${ch.flb(_("Keeled"),'keeled')}
    <div class="col" id="keeled">
      <%
        keeled_s = [lang_name for (value, lang_name, value_id) in c.opt.SOORKEEL if value in c.item.keeled]
      %>
      ${', '.join(keeled_s)}
    </div>
  </div>
  % if c.is_edit or testiosa and testiosa.piiraeg:
  <div class="form-group row">
    ${ch.flb(_("Lahendamise piiraeg"), 'piiraeg')}
    <div class="col">
      ${h.timedelta_min('piiraeg', testiosa and testiosa.piiraeg, wide=False)}
    </div>
  </div>
  % endif
  % if c.nimekiri:
  <div class="form-group row">
    ${ch.flb(_("Lahendamise ajavahemik"))}
    <div class="col d-flex">
      % if c.nimekiri.alates and c.nimekiri.kuni or c.is_edit:
      ${h.date_field('n_alates', c.nimekiri.alates, wide=False)}
      <span class="ml-2 mr-1">${"kuni"}</span>
      ${h.date_field('n_kuni', c.nimekiri.kuni, wide=False)}
      % elif c.nimekiri.alates:
      <div>${_("alates")} ${h.str_from_date(c.nimekiri.alates)}</div>
      % elif c.nimekiri.kuni:
      <div>${_("kuni")} ${h.str_from_date(c.nimekiri.kuni)}</div>
      % else:
      <div>${_("tähtajatult")}</div>
      % endif
      % if c.item.avalik_alates or c.item.avalik_kuni:
      <div class="mx-2">(${_("test avalik {s}").format(s='%s - %s' % (h.str_from_date(c.item.avalik_alates) or '', h.str_from_date(c.item.avalik_kuni) or ''))})</div>
      % endif
    </div>
  </div>
  % endif
  % if not c.item.on_jagatudtoo and (c.is_edit or c.item.ymardamine):
  <div class="form-group row">
    ${ch.flb(_("Ümardamine"))}
    <div class="col">
      % if c.is_edit:
      ${h.checkbox('f_ymardamine', 1, checked=c.item.ymardamine, label=_("Tulemus ümardatakse"))}
      % elif c.item.ymardamine:
      ${_("Tulemus ümardatakse")}
      % endif
    </div>
  </div>
  % endif
  % if c.is_edit or c.item.oige_naitamine or c.item.arvutihinde_naitamine:
  <div class="form-group row">
    ${ch.flb(_("Vastuste näitamine"))}
    <div class="col">
      % if c.is_edit:
      ${h.checkbox('pole_salastatud', 1, checked=not c.item.salastatud,
      label=_("Ülesannete vaatamise võimalus oma tulemusi vaadates"))}
      % elif not c.item.salastatud:
      ${_("Ülesannete vaatamise võimalus oma tulemusi vaadates")}      
      % endif
      <br/>
      % if c.is_edit:
      ${h.checkbox('f_oige_naitamine', 1, checked=c.item.oige_naitamine,
      label=_("Õigete vastuste vaatamise võimalus oma tulemusi vaadates"))}
      % elif c.item.oige_naitamine:
      ${_("Õigete vastuste vaatamise võimalus oma tulemusi vaadates")}
      % endif
      <br/>
      % if c.is_edit:
      ${h.checkbox('f_arvutihinde_naitamine', 1, checked=c.item.arvutihinde_naitamine,
      label=_("Arvutihinnatav osa tulemusest näidatakse kohe peale sooritamist"))}
      % elif c.item.arvutihinde_naitamine:
      ${_("Arvutihinnatav osa tulemusest näidatakse kohe peale sooritamist")}
      % endif

      % if c.is_edit:
      <script>
        ## kui on salastatud, siis ei saa õigeid näidata
        $('input[name="pole_salastatud"]').click(function(){
        if(!$(this).prop('checked'))
           $('input[name="f_oige_naitamine"]').prop('checked', false);
        });
        $('input[name="f_oige_naitamine"]').click(function(){
        if($(this).prop('checked'))
           $('input[name="pole_salastatud"]').prop('checked', true);
        });
      </script>
      % endif
    </div>
  </div>
  % endif
  % if c.item.autor:
  <div class="form-group row">
    ${ch.flb(_("Autor"))}
    <div class="col">${c.item.autor}</div>
  </div>
  % endif
  % if c.item.kvaliteet_kood:
  <div class="form-group row">
    ${ch.flb(_("Kvaliteedimärk"))}
    <div class="col">${c.item.kvaliteet_nimi}</div>
  </div>
  % endif
  % if not c.is_edit and c.item.markus:
  <div class="form-group row">
    ${ch.flb(_("Märkused"))}
    <div class="col">
      ${h.readonly_textarea(h.literal(c.item.markus), 'markus', nl=False)}
    </div>
  </div>
  % endif
  <% ek = c.item.eristuskiri %>
  % if not c.is_edit and ek and (ek.sisu or ek.has_file):
  <div class="form-group row">
    ${ch.flb(_("Eristuskiri"))}
    <div class="col">
      % if ek.sisu:
      ${h.textarea('ek_sisu', ek.sisu, rows=4)}
      % endif
      % if ek.has_file:
      ${h.btn_to(_("Laadi alla"), h.url_current('download', format=ek.fileext, id=c.item.id))}
      % endif
    </div>
  </div>
  % endif
  
  % if c.item.testityyp == const.TESTITYYP_TOO:
  <% testiisikud = [r for r in c.item.testiisikud if r.kasutajagrupp_id == const.GRUPP_T_OMANIK] %>
  <div class="form-group row">
    ${ch.flb(_("Töö koostaja"))}
    <div class="col">
      % for r in testiisikud:
      ${r.kasutaja.nimi}
      % endfor
    </div>
  </div>
  % endif
</div>


% if c.item.id and c.user.has_permission('testid', const.BT_UPDATE, c.item):
<%
  if c.item.on_jagatudtoo:
     grupp_id = const.GRUPP_T_TOOVAATAJA
  else:
     grupp_id = const.GRUPP_T_OMANIK
  testiisikud = [r for r in c.item.testiisikud if r.kasutajagrupp_id == grupp_id]
%>
% if testiisikud:
<table border="0" class="table nowide table-borderless table-striped tablesorter">
  <caption>
  % if c.item.on_jagatudtoo:
  ${_("Õpetajad, kes saavad tööd vaadata")}
  % else:
  ${_("Testi omanikud")}
  % endif
  </caption>
  <col/>
  <col/>
  <col width="20px"/>
  <thead>
    <tr>
      ${h.th(_('Isikukood'))}
      ${h.th(_('Nimi'))}
      <th sorter="false"></th>
    </tr>
  </thead>
  <tbody>
    % for roll in c.item.testiisikud:
    % if roll.kasutajagrupp_id == grupp_id:
    <% kasutaja = roll.kasutaja %>
    <tr>
      <td>${kasutaja.isikukood_hide}</td>
      <td>${kasutaja.nimi}</td>
      <td>
        % if len(c.item.testiisikud) > 1:
        ${h.remove(h.url_current('delete', isik_id=roll.id, sub='isik'))}
        % endif
      </td>
    </tr>
    % endif
    % endfor    
  </tbody>
</table>
% endif

<div class="d-flex flex-wrap">
  <div class="flex-grow-1">
% if c.user.has_permission('testid', const.BT_UPDATE, c.item):
% if c.item.on_jagatudtoo:
${h.btn_to_dlg(_('Lisa õpetaja'), h.url('test_isikud', test_id=c.item.id, testiruum_id=c.testiruum_id, grupp_id=grupp_id),
  title=_('Õpetajale testi vaatamiseks ligipääsu andmine'), width=500, level=2, mdicls='mdi-plus')}
% else:
${h.btn_to_dlg(_('Lisa omanik'), h.url('test_isikud', test_id=c.item.id, testiruum_id=c.testiruum_id, grupp_id=grupp_id),
  title=_('Testi omanike lisamine'), width=500, level=2, mdicls='mdi-plus')}
% endif
% endif

% endif

% if c.user.has_permission('tookogumikud', const.BT_SHOW):
${h.btn_to(_('Töölaud'), h.url('tookogumikud'), level=2)}
% endif

% if c.item.id and c.user.has_permission('testid', const.BT_DELETE, c.item):
% if c.item.on_jagatudtoo:
${h.btn_to(_('Eemalda töö'), h.url_current('delete', id=c.item.id), method='delete', level=2)}
% else:
${h.btn_to(_('Eemalda test'), h.url_current('delete', id=c.item.id), method='delete', level=2)}
% endif
% endif

% if c.item.id and c.user.has_permission('omanimekirjad', const.BT_CREATE, c.item):
${h.btn_to(_('Sooritamiseks suunamine'),
h.url('test_nimekirjad', test_id=c.item.id, testiruum_id=c.testiruum_id), level=2)}
% endif

% if c.item.id and c.item.testityyp in (const.TESTITYYP_AVALIK, const.TESTITYYP_TOO):
${h.btn_to(_('Kopeeri'), h.url('create_testid', sub='copy', id=c.item.id), method='post', level=2)}
% endif
% if c.item.id and c.is_edit:
${h.btn_to(_('Vaata'), h.url_current('show'), method='get')}
% elif c.item.id and not c.is_edit and c.user.has_permission('testid', const.BT_UPDATE, c.item):
${h.btn_to(_('Muuda'), h.url_current('edit', id=c.item.id), method='get')}
% endif
  </div>
  <div>
% if c.is_edit:
${h.submit()}
% endif
  </div>
</div>

${h.end_form()}
