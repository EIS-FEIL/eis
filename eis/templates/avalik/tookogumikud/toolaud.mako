<%inherit file="/common/page.mako"/>

<%def name="require()">
<% c.widepage = True %>
<% c.includes['sortablejs'] = True %>
</%def>
<%def name="page_title()">
${_("Minu töölaud")} 
</%def>      
<%def name="breadcrumbs()">
##${h.crumb(_("Minu töölaud"))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'tookogumikud' %>
</%def>
<%def name="page_headers()">
<style>
  .ppane {overflow-y: auto; padding: 1rem 0.5rem;}
  .ppane#ppane2 { padding: 1rem 1.5rem; }  
  .tkosa { min-height:400px;border:2px solid #fff;}
  .tkosa.sortable { border:2px dotted #ababab; }
  .tkogumik.open { background-color: #fff; }
  .tkogumik .tkogumik-btns { display: none; }
  .tkogumik.open .tkogumik-btns { display: block; }
  .tkogumik .mdi-folder-open-outline { display: none;}
  .tkogumik.open .mdi-folder-open-outline { display: inline-block;}
  .tkogumik .mdi-folder-outline { display: inline-block;}
  .tkogumik.open .mdi-folder-outline { display: none;}
</style>
</%def>

<%
c.can_update = c.user.has_permission('tookogumikud', const.BT_UPDATE)
%>
<%namespace name="tab" file='/common/tab.mako'/>
<div class="container-fluid">
<div class="row">
  <div class="col-sm-5 col-md-5 col-xl-4 otsing ppane" id="ppane1">
    <div>
      <%include file="tookogumik.otsingud.mako"/>
    </div>
  </div>
  <div class="col-sm-7 col-md-7 col-xl-4 bg-gray-50 large-card1 ppane d-flex flex-column ppane" id="ppane2">
    <div>
      <%include file="tookogumikud.mako"/>
    </div>
  </div>
  <div class="col-sm-12 col-md-12 col-xl-4 ppane" id="ppane3">
    <div>
    % if c.user.koht_id and c.user.has_permission('klass', const.BT_SHOW):
    <%include file="tookogumik.opperyhmad.mako"/>
    % endif
    <%include file="tookogumik.jagamised.mako"/>
    </div>
  </div>
</div>
</div>

% if c.is_edit:
<script>
  var pub_url = "${h.url('pub_formatted_valikud', kood='')}";
</script>
% if c.min_js:
${h.javascript_link('/static/eis/tookogumik.js')}
% else:
${h.javascript_link('/static/eis/source/tookogumik.js')}
% endif
% endif
