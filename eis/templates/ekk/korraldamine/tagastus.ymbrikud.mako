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

${h.form_search(url=h.url('korraldamine_tagastusymbrikud', toimumisaeg_id=c.toimumisaeg.id))}
<div class="gray-legend p-3 filter-w">
  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Piirkond"),'piirkond_id')}
        <div>
        <%
          c.piirkond_id = c.piirkond_id
          c.piirkond_field = 'piirkond_id'
          c.piirkond_on_change = 'change_by_piirkond();'
        %>
        <%include file="/admin/piirkonnavalik.mako"/>
        </div>
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">  
      <div class="form-group">
        ${h.flb(_("Soorituskoht"),'testikoht_id')}
        ${h.select('testikoht_id', c.testikoht_id,
        c.toimumisaeg.get_testikohad_opt(c.piirkond_id), empty=True,
        onchange="$(this).parents('form').submit()")}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">      
      <div class="form-group">
        ${h.flb(_("Olek"),'staatus')}
        ${h.select('staatus', c.staatus, c.opt_staatus, empty=True)}
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

<script>
        function change_by_piirkond()
        {
           var url = "${h.url('pub_formatted_valikud', kood='PIIRKONNATESTIKOHT', format='json')}";
           var ylem_id = $('#piirkond_id').val();
           if(ylem_id != '')
           {
              var data = {ylem_id: ylem_id, ta_id: ${c.toimumisaeg.id}};
              var target = $('select#testikoht_id');
              update_options(null, url, null, target, data, null, true);
           }
        }
</script>

<div class="listdiv">
<%include file="tagastus.ymbrikud_list.mako"/>
</div>
<br/>
