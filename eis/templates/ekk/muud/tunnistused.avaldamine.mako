<%inherit file="/common/formpage.mako"/>
<%def name="draw_tabs()">
<%include file="tunnistused.tabs.mako"/>
</%def>
<%def name="page_title()">
${_("Eksamitunnistuste avaldamine")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Eksamitunnistused"), h.url('muud_tunnistused_valjastamised'))}
${h.crumb(_("Avaldamine"))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'muud' %>
</%def>

${h.form_search(url=h.url('muud_tunnistused_avaldamised'))}
${h.hidden('staatus', c.staatus)}
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
    ${h.flb3(_("Testsessioon"))}
    <div class="col">
      ${h.select('sessioon_id', c.sessioon_id,
      c.opt_sessioon, empty=True,
      onchange="this.form.submit()")} 
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
      empty=True, onchange="this.form.submit()")}
    </div>
  </div>
</div>
${h.end_form()}

% if c.sessioon_id:
<div class="form-wrapper-lineborder mb-2">
  <div class="form-group row">
    ${h.flb3(_("Avaldatud tunnistusi"))}
    <div class="col-md-1">
      ${c.avaldatud}
    </div>
    <div class="col">
      % if c.avaldatud and c.avaldatud > 0:
      ${h.form_search(url=h.url('muud_tunnistused_avaldamised'))}
      ${h.hidden('sessioon_id', c.sessioon_id)}
      ${h.hidden('testimiskord_id', c.testimiskord_id)}
      ${h.hidden('staatus', const.N_STAATUS_AVALDATUD)}
      ${h.hidden('testiliik', c.testiliik)}
      ${h.submit(_("Näita"), id='naita')}
      ${h.end_form()}
      % endif
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Salvestatud avaldamata tunnistusi"))}
    <div class="col-md-1">
      ${c.salvestatud}
    </div>
    <div class="col">
      % if c.salvestatud and c.salvestatud > 0:
      <div class="d-flex">
        <div>
          ${h.form_save(None)}
          ${h.hidden('sessioon_id', c.sessioon_id)}
          ${h.hidden('testimiskord_id', c.testimiskord_id)}
          ${h.hidden('staatus', const.N_STAATUS_SALVESTATUD)}
          ${h.hidden('testiliik', c.testiliik)}
          ${h.submit(_("Avalda"), clicked=True)}
          ${h.end_form()}
        </div>
        <div>
          ${h.form_search(url=h.url('muud_tunnistused_avaldamised'))}
          ${h.hidden('sessioon_id', c.sessioon_id)}
          ${h.hidden('testimiskord_id', c.testimiskord_id)}
          ${h.hidden('staatus', const.N_STAATUS_SALVESTATUD)}
          ${h.hidden('testiliik', c.testiliik)}
          ${h.submit(_("Näita"), id='naita')}      
          ${h.end_form()}     
        </div>
      </div>
      % endif
    </div>
  </div>
  
  <div class="form-group row">
    ${h.flb3(_("Salvestamata tunnistusi"))}
    <div class="col-md-1">
      ${c.salvestamata}
    </div>
    <div class="col">
      % if c.salvestamata > 0:
      ${h.form_search(url=h.url('muud_tunnistused_avaldamised'))}
      ${h.hidden('sessioon_id', c.sessioon_id)}
      ${h.hidden('testimiskord_id', c.testimiskord_id)}
      ${h.hidden('staatus', const.N_STAATUS_KEHTIV)}      
      ${h.hidden('testiliik', c.testiliik)}
      ${h.submit(_("Näita"), id='naita')}
      ${h.end_form()}
      % endif
    </div>
  </div>
</div>

${h.form_save(None)}
${h.hidden('sessioon_id', c.sessioon_id)}
${h.hidden('testimiskord_id', c.testimiskord_id)}
${h.hidden('staatus', c.staatus)}
${h.hidden('testiliik', c.testiliik)}
% if c.user.has_permission('tunnistused', const.BT_UPDATE):
<div class="form-wrapper-lineborder">
  <div class="form-group row">
    ${h.flb3(_("Väljastamise alus"))}
    <div class="col-md-6">
      ${h.text('alus', c.alus)}
    </div>
    <div class="col-md-3">
      ${h.submit(_("Salvesta"), id='salvesta_alus', clicked=True)}
    </div>
  </div>
</div>
% endif

<div class="listdiv">
<%include file="tunnistused.avaldamine_list.mako"/>
</div>
${h.end_form()}

% endif
