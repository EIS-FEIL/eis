<%inherit file="/common/page.mako" />
<%def name="page_title()">
${_("Soorituskohtade andmete muudatused")}
</%def>
<%def name="breadcrumbs()">
${h.crumb(_("Soorituskohad"), h.url('admin_kohad'))}
${h.crumb(_("Näita muudatusi"), h.url('admin_kohad_logi'))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'admin' %>
</%def>

${h.form_search(url=h.url('admin_kohad_logi'))}
<div class="gray-legend p-3 filter-w">
  ##${h.toggle_filter()}

  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Koha ID"),'koht_id')}
        ${h.posint('koht_id', c.koht_id)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Koha nimetus"),'koht_nimi')}
        ${h.text('koht_nimi', c.koht_nimi)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Muudatuse allikas"), 'allikas')}
        ${h.select('allikas', c.allikas, c.opt_allikas, empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Muutja nimi"), 'muutja_nimi')}
        ${h.text('muutja_nimi', c.muutja_nimi)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Alates"), 'alates')}
        ${h.date_field('alates', c.alates)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("kuni"), 'kuni')}
        ${h.date_field('kuni', c.kuni)}
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
<%include file="kohalogi_list.mako" />
</div>
