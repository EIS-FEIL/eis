<%inherit file="/common/page.mako" />
<%def name="page_title()">
${_("Ettepanekud")}
</%def>
<%def name="breadcrumbs()">
</%def>
<%def name="active_menu()">
<% c.menu1 = 'muud' %>
</%def>
<h1>${_("Küsimused ja ettepanekud")}</h1>
${h.form_search(url=h.url('muud_ettepanekud'))}

<div class="gray-legend p-3 filter-w">
##${h.toggle_filter()}
  <div class="row filter">
    <div class="col-12 col-md-8 col-lg-6">
      <div class="form-group">
        ${h.flb(_("Aeg"),'alates')}
        <div class="row">
          <div class="col-md-5">
            ${h.date_field('alates', h.str_from_date(c.alates))}
          </div>
          <div class="col-md-1">
            ${_("kuni")}
          </div>
          <div class="col-md-5">
            ${h.date_field('kuni', h.str_from_date(c.kuni))}
          </div>
        </div>
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Esitaja"),'saatja')}
        ${h.text('saatja', c.saatja)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Teema"),'teema')}
        ${h.text('teema', c.teema)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Sisu"),'sisu')}
        ${h.text('sisu', c.sisu)}
      </div>
    </div>
    <div class="col d-flex justify-content-end align-items-end">
      <div class="form-group">
        ${h.btn_search()}
        ${h.submit(_("Väljasta CSV"), id='csv', class_="filter")}
      </div>
    </div>
  </div>
</div>
${h.end_form()}

<div class="listdiv">
<%include file="ettepanekud_list.mako" />
</div>
