<%inherit file="/common/formpage.mako"/>
<%def name="page_title()">
${_("Testi korraldamine")} | ${c.toimumisaeg.testimiskord.test.nimi} ${h.str_from_date(c.toimumisaeg.alates)}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Korraldamine"), h.url('korraldamised'))} 
${h.crumb('%s %s' % (c.toimumisaeg.testimiskord.test.nimi, h.str_from_date(c.toimumisaeg.alates)))} 
${h.crumb(_("Sooritajate aadressid"),h.url_current())}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'korraldamised' %>
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

${h.form_search(url=h.url('korraldamine_aadressid', toimumisaeg_id=c.toimumisaeg.id))}
<div class="gray-legend p-3 filter-w">
  ##${h.toggle_filter()}
  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Soovitav piirkond"),'piirkond_id')}
        <%
          c.piirkond_id = c.piirkond_id
          c.piirkond_field = 'piirkond_id'
        %>
        <%include file="/admin/piirkonnavalik.mako"/>
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">        
        ${h.flb(_("Soorituskeel"), 'langs')}
        <div id="langs">
        <% 
          keeled = c.toimumisaeg.testimiskord.get_keeled()
          if not c.lang:
             c.lang = keeled
        %>
        % for lang in keeled:
        ${h.checkbox('lang', lang, checkedif=c.lang, 
        label=model.Klrida.get_lang_nimi(lang))}
        % endfor
        </div>
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">        
        ${h.checkbox1('kooliga', 1, checked=c.kooliga or not c.koolita, label=_("Õppeasutusega"))}
        <br/>
        ${h.checkbox1('koolita', 1, checked=c.koolita or not c.kooliga, label=_("Õppeasutuseta"))}
      </div>
    </div>
    <div class="col-12 col-md-8 col-lg-3">
      <div class="form-group">
        ${h.checkbox1('opibmujal', 1, checked=c.opibmujal, label=_("Ei soorita oma õppimiskohas asuvas soorituskohas"))}
      </div>
    </div>
    <div class="col d-flex justify-content-end align-items-end">    
      <div class="form-group">
        ${h.btn_search()}        
        ${h.submit(_("PDF"), id='pdf', class_="filter", level=2)}
        ${h.submit(_("CSV"), id='csv', class_="filter", level=2)}
      </div>
    </div>
  </div>
</div>
${h.end_form()}

<div class="listdiv">
<%include file="aadressid_list.mako"/>
</div>
