<%inherit file="/common/formpage.mako"/>
<%def name="draw_tabs()">
<%include file="tunnistused.tabs.mako"/>
</%def>
<%def name="page_title()">
${_("Eksamitunnistuste vormistamine")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Eksamitunnistused"), h.url('muud_tunnistused_valjastamised'))}
${h.crumb(_("Väljastamine"))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'muud' %>
</%def>
${h.form_search(url=h.url('muud_tunnistused_valjastamised'))}

<div class="form-wrapper-lineborder mb-2">
  <div class="form-group row">
    ${h.flb3(_("Testi liik"))}
    <div class="col">
      <% opt_testiliik = [r for r in c.opt.testiliik if r[0] in (const.TESTILIIK_RIIGIEKSAM, const.TESTILIIK_POHIKOOL, const.TESTILIIK_TASE, const.TESTILIIK_SEADUS)] %>
      ${h.select('testiliik', c.testiliik, opt_testiliik, 
      onchange="this.form.submit()")}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Tunnistuse liik"))}
    <div class="col">
      <%
         opt_tliigid = [(const.TESTILIIK_RIIGIEKSAM, _("Riigieksamitunnistus")),
                        (const.TESTILIIK_TASE, _("Riigikeele tasemeeksami tunnistus")),
                        (const.TESTILIIK_SEADUS, _("Seaduse tundmise eksami tunnistus")),
                       ]
         opt_tunnistuseliik = [r for r in opt_tliigid if r[0] in c.map_liigid[c.testiliik]]
      %>
      ${h.select('tunnistuseliik', c.tunnistuseliik, opt_tunnistuseliik, 
      onchange="this.form.submit()")}
    </div>
  </div>
</div>

${h.end_form()}

${h.form_search(url=h.url('muud_tunnistused_valjastamised'))}
${h.hidden('sub','kontroll')}
${h.hidden('testiliik', c.testiliik)}
${h.hidden('tunnistuseliik', c.tunnistuseliik)}
${h.rqexp()}
<div class="form-wrapper-lineborder mb-2">
  <div class="form-group row">
    ${h.flb3(_("Testsessioon"), rq=True)}
    <div class="col">
      ${h.select('sessioon_id', c.sessioon_id,
      model.Testsessioon.get_opt(c.testiliik), empty=True, onchange="this.form.submit()", class_='nosave')}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Testimiskord"))}
    <div class="col">
      <% 
         opt_testimiskord = model.Testimiskord.get_opt(c.sessioon_id or -1, testityyp=const.TESTITYYP_EKK) or []
         if c.testimiskord_id and int(c.testimiskord_id) not in [r[0] for r in opt_testimiskord]:
            c.testimiskord_id = None
         %>
      ${h.select('testimiskord_id', c.testimiskord_id, opt_testimiskord,
      empty=True, onchange="this.form.submit()", class_='nosave')}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Tunnistuse mall"), rq=True)}
    <div class="col">
    % if len(c.opt_t_name):
      <% if not c.t_name: c.t_name = c.opt_t_name[0][0] %>
      ${h.select('t_name', c.t_name, c.opt_t_name)}
      % if c.sessioon_id and c.tunnistuseliik:
      <div class="text-right">
        ${h.submit(_("Proovi"),id='demo', level=2)}
      </div>
      % endif
    % else:
      ${_("Valitud liigile vastavaid tunnistuste malle ei leitud")}
      ${h.hidden('t_name','')}
    % endif
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Isikukood"))}
    <div class="col">
      ${h.text('isikukood', c.isikukood, maxlength=50, size=16, class_='nosave')}
    </div>
  </div>
</div>

<div class="text-right mb-2">
  ${h.submit(_("Kontrolli tunnistuste arvu"))}
</div>
${h.end_form()}

% if c.uusi or c.asendatavaid:
${h.form_save(None)}
${h.hidden('testiliik', c.testiliik)}
${h.hidden('tunnistuseliik', c.tunnistuseliik)}
${h.hidden('sessioon_id', c.sessioon_id)}
${h.hidden('testimiskord_id', c.testimiskord_id)}
${h.hidden('t_name', c.t_name)}
${h.hidden('isikukood', c.isikukood)}
${h.hidden('sub', 'valjasta')}
<div class="form-wrapper-lineborder mb-2">
% if c.uusi != '':
  <div class="form-group row">
    ${h.flb3(_("Väljastatavaid uusi tunnistusi"))}
    <div class="col">
      ${c.uusi}
      ${h.hidden('uusi', c.uusi)}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Asendatavaid tunnistusi"))}
    <div class="col">
      ${c.asendatavaid}
      ${h.hidden('asendatavaid', c.asendatavaid)}
    </div>
  </div>
  % if c.user.has_permission('tunnistused', const.BT_UPDATE):
  <div class="form-group row">
    <div class="col">
      ${h.checkbox('ainultuued', 1, checked=c.ainultuued, 
      label=_("Väljasta ainult uued tunnistused"))}
    </div>
  </div>
  % endif
% endif

  % if c.user.has_permission('tunnistused', const.BT_UPDATE):
  <div class="form-group row">
    ${h.flb3(_("Põhjendus"))}
    <div class="col">
      ${h.textarea('pohjendus', c.pohjendus, rows=2)}
    </div>
  </div>
  % endif
</div>

<div class="text-right my-2">
% if c.user.has_permission('tunnistused', const.BT_UPDATE):
${h.submit(_("Väljasta"), clicked=True)}
% endif
</div>

${h.end_form()}
% endif

% if c.arvutusprotsessid:
<%
  c.protsessid_no_caption = True
  c.url_refresh = h.url('muud_tunnistused_valjastamised', sessioon_id=c.sessioon_id, sub='progress')
%>
<%include file="/common/arvutusprotsessid.mako"/>
% endif
