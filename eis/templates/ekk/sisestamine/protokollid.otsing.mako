<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Testi toimumise protokolli koostamine")}
</%def>      
<%def name="breadcrumbs()">
</%def>
<%def name="active_menu()">
<% c.menu1 = 'sisestamine' %>
</%def>

<h1>${_("Testi toimumise protokolli koostamine")}</h1>
${h.form_search(url=h.url('sisestamine_protokollid'))}

<div class="gray-legend p-3 filter-w">
  ##${h.toggle_filter()}
  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Sisesta toimumisaja tähis"),'tahis')}
        ${h.text('tahis', c.tahis)}
      </div>
    </div>
  </div>
  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("või vali testsessioon"),'sessioon_id')}
        ${h.select('sessioon_id', c.sessioon_id,
        c.opt.testsessioon, empty=True, onchange='this.form.submit()')}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("ja toimumisaeg"),'toimumisaeg_id')}
        ${h.select('toimumisaeg_id', c.toimumisaeg_id,
          c.opt_toimumisaeg, empty=True, onchange='this.form.submit()')}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3 d-flex align-items-end">
      <div class="form-group">
        ${h.checkbox1('kinnitamata', 1, checked=c.kinnitamata, label=_("Kinnitamata"))}
        ${h.checkbox1('sisestamata', 1, checked=c.sisestamata, label=_("Sisestamata"))}
      </div>
    </div>
    <div class="col d-flex justify-content-end align-items-end">      
      <div class="form-group">
        ${h.btn_search()}
        ${h.submit(u'CSV', id='csv', class_="filter")}
      </div>
    </div>
  </div>
</div>
${h.end_form()}

<div class="listdiv">
<%include file="protokollid.otsing_list.mako"/>
</div>
