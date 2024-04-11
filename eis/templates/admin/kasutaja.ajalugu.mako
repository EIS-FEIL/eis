<%inherit file="/common/formpage.mako"/>
<%def name="require()">
<% c.includes['jstree'] = True %>
</%def>
<%def name="page_title()">
${_("Kasutajad")} | ${c.kasutaja.nimi or _("Uus kasutaja")}
</%def>
<%def name="breadcrumbs()">
${h.crumb(_("Kasutajad"), h.url('admin_kasutajad'))} 
${h.crumb(c.kasutaja.nimi, h.url('admin_kasutaja', id=c.kasutaja.id))}
${h.crumb(_("Läbiviija ajalugu"))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'admin' %>
</%def>
<%def name="draw_tabs()">
<%include file="kasutaja.tabs.mako"/>
</%def>

${h.form_search(h.url('admin_kasutaja_ajalugu', kasutaja_id=c.kasutaja.id))}
<div class="gray-legend p-3 filter-w">
  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Testsessioon"),'testsessioon_id')}
        ${h.select('testsessioon_id', c.testsessioon_id, c.opt.testsessioon, empty=True)}
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
      <div class="form-group">
        ${h.btn_search()}
      </div>
    </div>
  </div>
</div>
${h.end_form()}

<div class="listdiv">
<%include file="kasutaja.ajalugu_list.mako"/>
</div>
