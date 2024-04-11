<%inherit file="/common/formpage.mako"/>
<%def name="require()">
<% c.includes['subtabs'] = True %>
</%def>
<%def name="page_title()">
${_("Testi korraldamine")} | ${c.toimumisaeg.testimiskord.test.nimi} ${h.str_from_date(c.toimumisaeg.alates)}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Korraldamine"), h.url('korraldamised'))} 
${h.crumb('%s %s' % (c.toimumisaeg.testimiskord.test.nimi, h.str_from_date(c.toimumisaeg.alates)))} 
${h.crumb(_("Materjalide tagastus"))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'korraldamised' %>
</%def>

<%def name="draw_before_tabs()">
<%include file="before_tabs.mako"/>
</%def>

<%def name="draw_tabs()">
<% c.tab1 = 'tagastus' %>
<%include file="tabs.mako"/>
</%def>

<%def name="draw_subtabs()">
<%include file="tagastus.tabs.mako"/>
</%def>

${h.form_search(url=h.url('korraldamine_tagastuskotid', toimumisaeg_id=c.toimumisaeg.id))}
<div class="gray-legend p-3 filter-w">
  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Soorituskoht"), 'testikoht_id')}
        ${h.select('testikoht_id', c.testikoht_id,
        c.toimumisaeg.get_testikohad_opt(), empty=True,
        onchange="$(this).parents('form').submit()")}
      </div>
    </div>
  </div>
</div>
${h.end_form()}

<div class="listdiv">
<%include file="tagastus.kotid_list.mako"/>
</div>
<br/>

