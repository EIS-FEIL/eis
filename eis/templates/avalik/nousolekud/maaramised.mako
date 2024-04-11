<%inherit file="/common/formpage.mako"/>
<%def name="page_title()">
${_("Testi läbiviimise nõusolekud")}
</%def>
<%def name="breadcrumbs()">
</%def>
<%def name="draw_tabs()">
<%include file="tabs.mako"/>
</%def>

${h.form_search(url=h.url('nousolekud_maaramised'))}

<div class="gray-legend p-3 filter-w">
  ##${h.toggle_filter()}
  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Testsessioon"),'testsessioon_id')}
        ${h.select('testsessioon_id', c.testsessioon_id,
        model.Testsessioon.get_opt(), empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Alates"),'alates')}
        ${h.date_field('alates', c.alates)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("kuni"),'kuni')}
        ${h.date_field('kuni', c.kuni)}
      </div>
    </div>
    <div class="col d-flex justify-content-end align-items-end">
      <div>
        ${h.btn_search()}
      </div>
    </div>
  </div>
</div>
${h.end_form()}

<div class="listdiv">
<%include file="maaramised_list.mako"/>
</div>
