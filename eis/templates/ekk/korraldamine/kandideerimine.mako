<%inherit file="/common/formpage.mako"/>
<%def name="page_title()">
${_("Testi korraldamine")} | ${c.toimumisaeg.testimiskord.test.nimi} ${h.str_from_date(c.toimumisaeg.alates)}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Korraldamine"), h.url('korraldamised'))} 
${h.crumb('%s %s' % (c.toimumisaeg.testimiskord.test.nimi, h.str_from_date(c.toimumisaeg.alates)))} 
${h.crumb(_("Kandideerimine"), h.url_current())}
</%def>

<%def name="draw_before_tabs()">
<%include file="before_tabs.mako"/>
</%def>

<%def name="draw_tabs()">
<% c.tab1 = 'muu' %>
<%include file="tabs.mako"/>
</%def>

<%def name="require()">
<% c.includes['subtabs'] = True %>
</%def>

<%def name="draw_subtabs()">
<%include file="muu.subtabs.mako"/>
</%def>

${h.form_search(url=h.url('korraldamine_kandideerimine', toimumisaeg_id=c.toimumisaeg.id))}
<div class="gray-legend p-3 filter-w">
  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Tulemuste vaatamise õigusega kool"), 'koht_id')}
        ${h.select('koht_id', c.koht_id, c.opt_vvkohad, empty=True)}
      </div>
    </div>
    <div class="d-flex justify-content-end align-items-end">    
      <div class="form-group">
        ${h.btn_search()}        
        ${h.submit(_("CSV"), id='csv', class_="filter", level=2)}
      </div>
    </div>
  </div>
</div>
${h.end_form()}

<div class="listdiv">
<%include file="kandideerimine_list.mako"/>
</div>
