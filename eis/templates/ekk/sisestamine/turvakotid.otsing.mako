<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Turvakottide numbrite sisestamine")}
</%def>      
<%def name="breadcrumbs()">
</%def>
<%def name="active_menu()">
<% c.menu1 = 'sisestamine' %>
</%def>


<h1>${_("Turvakottide numbrite sisestamine")}</h1>
${h.form_search(url=h.url('sisestamine_turvakotid'))}

<div class="gray-legend p-3 filter-w">
  ##${h.toggle_filter()}
  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Sisesta testi toimumisaja tähis"),'ta_tahised')}
        ${h.text('ta_tahised', c.ta_tahised)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("või vali testsessioon"),'sessioon_id')}
        ${h.select('sessioon_id', c.sessioon_id,
        c.opt.testsessioon, empty=True, onchange='this.form.submit()')}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("või testi ID"),'test_id')}
        ${h.posint('test_id', c.test_id)}
      </div>
    </div>
    <div class="col d-flex justify-content-end align-items-end">      
      <div class="form-group">
        ${h.btn_search()}
      </div>
    </div>
  </div>
</div>

${h.end_form()}
<div class="listdiv">
<%include file="turvakotid.otsing_list.mako"/>
</div>
