<%inherit file="/common/formpage.mako"/>
<%def name="draw_tabs()">
<%include file="tabs.mako"/>
</%def>

<%def name="page_title()">
${c.test.nimi or ''} | ${_("Läbiviimine")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_('Minu töölaud'), h.url('tookogumikud'))}
${h.crumb(c.test.nimi or _('Test'))} 
${h.crumb(_('Läbiviimine'))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'tookogumikud' %>
</%def>

% if c.testiruum:
<%
  c.can_update = c.user.has_permission('omanimekirjad', const.BT_UPDATE, c.testiruum) or \
                 c.user.has_permission('testiadmin', const.BT_UPDATE, c.testiruum)
%>
<h3>
  ${c.test.nimi}
  (${h.fstr(c.test.max_pallid)} p)
</h3>
<div class="d-flex flex-wrap justify-content-between">
  <h4>${c.testiruum.nimekiri.nimi}</h4>
  <% c.testiosavalik_action = h.url_current('edit') %>
  <%include file="testiosavalik.mako"/>
</div>

<div class="data-box">
  <div class="row">
    % if c.testiosa.piiraeg:
    <div class="column col-sm-3">
      ${h.flb(_("Piiraeg"),'dpiiraeg')}
    </div>
    <div class="column col-sm-9" id="dpiiraeg">
      ${h.str_from_time(c.testiosa.piiraeg)}
    </div>
    % endif
    
    <% eeltest = c.test.eeltest %>
    % if eeltest:
    %   if eeltest.markus_korraldajatele:
    <div class="column col-sm-3">
      ${h.flb(_("Koostaja märkus"),'dmarkus_korraldajatele')}
    </div>
    <div class="column col-sm-9" id="dmarkus_korraldajatele">
      ${eeltest.markus_korraldajatele or ''}
    </div>
    %   endif
    % if c.can_update or c.markuskoostajale:
    <div class="column col-sm-3">
      ${h.flb(_("Tagasiside koostajale"), 'dmarkuskoostajale')}
      % if c.can_update:
      ${h.btn_to_dlg('',
      h.url_current('edit', id=c.testiruum.id, sub='markuskoostajale',partial=True), 
      title=_('Tagasiside koostajale'), width=600, level=2, mdicls='mdi-file-edit')}
      % endif
    </div>
    <div class="column col-sm-9" id="dmarkuskoostajale">
      % if c.markuskoostajale:
      ${c.markuskoostajale.sisu}
      % endif
    </div>
    % endif
    % endif
  </div>
  
  % if c.on_kutse and c.testiruum.on_arvuti_reg:
  <div class="row">
    <div class="column col-sm-3">
      ${h.flb(_("Koht"),'dkoht')}
    </div>
    <div class="column col-md-9" id="dkoht">
      ${c.testikoht.koht.nimi}
    </div>
    % if c.testiruum.algus:
    <div class="column col-sm-3">
      ${h.flb(_("Algus"),'dalgus')}
    </div>
    <div class="column col-sm-9" id="dalgus">
      ${h.str_from_datetime(c.testiruum.algus)}
      % if c.testiruum.alustamise_lopp:
      - ${h.str_time_from_datetime(c.testiruum.alustamise_lopp)}
      % endif
    </div>
    % endif
    
    % if c.testiosa.vastvorm_kood in (const.VASTVORM_KE, const.VASTVORM_SE):
    <div class="column col-sm-3">
      ${h.flb3(_("Arvutite registreerimine"),'arvuti_reg')}
    </div>
    <div class="column col-sm-9">
      ${h.form_save(c.testiruum.id)}
      ${h.hidden('sub', 'reg')}
      ${h.select('arvuti_reg', c.testiruum.arvuti_reg, c.opt.arvuti_reg[1:], class_='nosave', 
      onchange="this.form.submit()", wide=False, ronly=c.veel_ei_toimu)}
      % if c.testiruum.arvuti_reg == const.ARVUTI_REG_ON:
      ${_("Parool")}:
      ${c.testiruum.parool}
      % endif
      ${h.end_form()}
    </div>
    % endif    
  </div>
  % endif
</div>

% if c.testiruum and c.testiruum.arvuti_reg and c.testiosa.vastvorm_kood in (const.VASTVORM_KE, const.VASTVORM_SE):
<%include file="/avalik/klabiviimine/arvutid_list.mako"/>
% endif

<div class="listdiv" width="100%">
  <%include file="../klabiviimine/sooritajad.mako"/>
</div>

% if c.dialog_markus:
<div id="div_dialog_markus">
  <%include file="../klabiviimine/markus.mako"/>
</div>
<script>
  $(function(){
    open_dialog({'contents_elem': $('#div_dialog_markus'), 'title': "${_('Märge')}"});
  });
</script>
% endif

% if c.dialog_markuskoostajale:
<div id="div_dialog_markuskoostajale">
  <%include file="markuskoostajale.mako"/>
</div>
<script>
  $(function(){
    open_dialog({'contents_elem': $('#div_dialog_markuskoostajale'), 'title': "${_('Märkus koostajale')}"});
  });
</script>
% endif

% if c.dialog_lisaaeg:
<div id="div_dialog_lisaaeg">
  <%include file="../klabiviimine/lisaaeg.mako"/>
</div>
<script>
  $(function(){
    open_dialog({'contents_elem': $('#div_dialog_lisaaeg'), 'title': "${_('Lisaaeg')}"});
  });
</script>
% endif
% endif
