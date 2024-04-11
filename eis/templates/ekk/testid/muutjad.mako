<%inherit file="/common/formpage.mako"/>
<%def name="draw_tabs()">
<%include file="tabs.mako"/>
</%def>

<%def name="page_title()">
${_("Test")}: ${c.test.nimi or ''} | ${_("Koostamise ajalugu")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Testid"), h.url('testid'))} 
${h.crumb(c.test.nimi or _("Test"))} 
${h.crumb(_("Koostamise ajalugu"))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'testid' %>
</%def>

##% if c.is_debug:
${h.form_search(url=h.url_current('show'))}
<div class="gray-legend p-3 filter-w">

  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Liik"),'liik')}
        ${h.text('liik', c.liik, ronly=False)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Vanad andmed"),'vanad')}
        ${h.text('vanad', c.vanad, ronly=False)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Uued andmed"),'uued')}
        ${h.text('uued', c.uued, ronly=False)}
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

<div width="100%" class="lightback listdiv">
<%include file="muutjad_list.mako"/>
</div>

