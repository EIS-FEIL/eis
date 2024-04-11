<%inherit file="/common/formpage.mako"/>
<%def name="require()">
<% c.includes['subtabs'] = True %>
</%def>
<%def name="page_title()">
${c.toimumisaeg.testimiskord.test.nimi} ${c.toimumisaeg.millal} | ${_("Koolide analüüs")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Hindamine"), h.url('hindamised'))} 
${h.crumb('%s %s' % (c.toimumisaeg.testimiskord.test.nimi, c.toimumisaeg.millal))} 
${h.crumb(_("Hindamise analüüs"), h.url('hindamine_analyys_protokollid', toimumisaeg_id=c.toimumisaeg.id))}
${h.crumb(_("Koolide analüüs"), h.url('hindamine_analyys_vastused', toimumisaeg_id=c.toimumisaeg.id))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'hindamised' %>
</%def>

<%def name="draw_before_tabs()">
<%include file="before_tabs.mako"/>
</%def>

<%def name="draw_tabs()">
<% c.tab1 = 'analyys' %>
<%include file="tabs.mako"/>
</%def>

<%def name="draw_subtabs()">
<%include file="analyys.tabs.mako"/>
</%def>

<% opt_kursused = c.test.opt_kursused %>
${h.form_search(url=h.url('hindamine_analyys_koolid', toimumisaeg_id=c.toimumisaeg.id))}


<div class="gray-legend p-3 filter-w">
  ##${h.toggle_filter()}
  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Soorituskoht"), 'testikoht_id')}
        ${h.select('testikoht_id', c.testikoht_id, c.toimumisaeg.get_testikohad_opt(),
              onchange="$('#kool_koht_id').val('');if($(this).val()!='')this.form.submit()", ronly=False, empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Õppimiskoht"), 'kool_koht_id')}
        ${h.select('kool_koht_id', c.kool_koht_id, c.koolid_id,
        onchange="$('#testikoht_id').val('');if($(this).val()!='')this.form.submit()", ronly=False, empty=True)}
      </div>
    </div>
    % if opt_kursused:
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Kursus"),'kursus')}
        ${h.select('kursus', c.kursus, opt_kursused,
        onchange="this.form.submit()", ronly=False, empty=False)}              
      </div>
    </div>
    % endif
  </div>
  <div class="row filter">
    <div class="col-12 col-md-8 col-lg-6">
      <div class="form-group">    
        ${h.checkbox('pallitud', 1, checked=c.pallitud,
        label=_("Kuva ainult need sooritajad, kellel mõne ülesande juures punkte pole"))}
      </div>
    </div>
    <div class="col d-flex justify-content-end align-items-end">
      <div>
        ${h.btn_search(clicked=True)}
        ${h.submit(_("CSV"), id='csv', level=2)}                                    
      </div>
    </div>
  </div>
</div>
${h.end_form()}

% if c.items:
<%include file="analyys.koolid_statistika.mako"/>
<br/>
<%include file="analyys.koolid_list.mako"/>
% endif
