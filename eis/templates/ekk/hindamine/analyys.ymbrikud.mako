<%inherit file="/common/formpage.mako"/>
<%def name="require()">
<% c.includes['subtabs'] = True %>
</%def>
<%def name="page_title()">
${c.toimumisaeg.testimiskord.test.nimi} ${c.toimumisaeg.millal} | ${_("Testitööde ümbrikud")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Hindamine"), h.url('hindamised'))} 
${h.crumb('%s %s' % (c.toimumisaeg.testimiskord.test.nimi, c.toimumisaeg.millal))} 
${h.crumb(_("Läbiviijate määramine"), h.url('hindamine_hindajad', toimumisaeg_id=c.toimumisaeg.id))}
${h.crumb(_("Testitööde ümbrikud"))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'hindamised' %>
</%def>

<%def name="draw_before_tabs()">
<%include file="before_tabs.mako"/>
</%def>

<%def name="draw_tabs()">
<% c.tab1 = 'maaramine' %>
<%include file="tabs.mako"/>
</%def>

<%def name="draw_subtabs()">
<%include file="maaramine.tabs.mako"/>
</%def>
<h3>${_("Tähelepanu vajavad testitööde ümbrikud")}</h3>

${h.form_search(url=h.url('hindamine_analyys_ymbrikud', toimumisaeg_id=c.toimumisaeg.id))}
<div class="gray-legend p-3 filter-w">
  <div class="row filter">
    ${h.flb3(_("Probleemi liik"),'probleem')}
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
            ${h.radio('probleem', 'maaramata', checkedif=c.probleem, 
            label=_("Läbiviija määramata"))}
            ${h.radio('probleem', 'tagastamata', checkedif=c.probleem, 
            label=_("Läbiviijalt tagastamata"))}
            <script>
              $(document).ready(function(){
              $('input[name="probleem"]').change(function(){
                this.form.submit();
              });
              });
            </script>
      </div>
    </div>
    <div class="col">
      <div class="form-group">
        ${h.submit(_("CSV"), id='csv')}
      </div>
    </div>
  </div>
</div>
${h.end_form()}

<div class="listdiv">
<%include file="analyys.ymbrikud_list.mako"/>
</div>
<br/>
