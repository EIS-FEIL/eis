<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Kirjalike paberil testitööde hindajatele väljastamise registreerimine (hindamispakettide tegemine)")}
</%def>      
<%def name="breadcrumbs()">
</%def>
<%def name="active_menu()">
<% c.menu1 = 'sisestamine' %>
</%def>

<h1>${_("Kirjalike paberil testitööde ümbrike hindajatele väljastamine")}</h1>
${h.form_search(url=h.url('sisestamine_valjastamine'))}

<div class="gray-legend p-3 filter-w">
  ##${h.toggle_filter()}
  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Sisesta toimumisaja tähis või selle algus"),'tahis')}
        ${h.text('tahis', c.tahis)}
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
        ${h.flb(_("Õppeaine"),'aine')}
        ${h.select('aine', c.aine, c.opt.klread_kood('AINE'), empty=True)}
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
<%include file="valjastamine.otsing_list.mako"/>
</div>
