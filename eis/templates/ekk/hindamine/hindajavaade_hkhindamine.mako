<%inherit file="/common/formpage.mako"/>
<%def name="require()">
<%
  c.includes['subtabs'] = True
  c.includes['test'] = c.includes['spectrum'] = True 
  c.includes['math'] = True
  c.pagexl = True
%>
</%def>
<%def name="page_title()">
${_("Hinnatavad sooritused")}
% if c.hindaja:
| ${c.hindaja.kasutaja.nimi}
% endif
</%def>      
<%def name="active_menu()">
<% c.menu1 = 'hindamised' %>
</%def>
<%def name="breadcrumbs()">
${h.crumb(_("Hindamine"), h.url('hindamised'))} 
${h.crumb('%s %s' % (c.toimumisaeg.testimiskord.test.nimi, c.toimumisaeg.millal))} 
${h.crumb(_("Läbiviijate määramine"), h.url('hindamine_hindajad', toimumisaeg_id=c.toimumisaeg.id))}
% if c.hindaja and c.hindaja.liik == const.HINDAJA3:
${h.crumb(_("III hindamine"), h.url('hindamine_hindajad3', toimumisaeg_id=c.toimumisaeg.id))}
% else:
${h.crumb(_("Esmane (I ja II) hindamine"), h.url('hindamine_hindajad', toimumisaeg_id=c.toimumisaeg.id))}
% endif
% if c.hindaja:
${h.crumb(c.hindaja.kasutaja.nimi)}
% else:
${h.crumb('%s %s' % (_("Hindamiskogum"), c.hindamiskogum.tahis))}
% endif
</%def>

<%def name="draw_before_tabs()">
<%include file="before_tabs.mako"/>
</%def>

<%def name="draw_tabs()">
<% c.tab1 = 'maaramine' %>
<%include file="tabs.mako"/>
</%def>

<%def name="draw_subtabs()">
<%
  c.tab2 = 'vastajad'
%>
<%include file="maaramine.tabs.mako"/>
</%def>

<%def name="page_headers()">
<style>
## parema poole peitmine
#hindamine_p_div.hidden-r {  flex-direction: column-reverse;  }
#hindamine_p_div.hidden-r .r_body_hider { display: none; }
#hindamine_p_div.hidden-r .hindamine_r_tabs { float: right; }
#hindamine_p_div.hidden-r #hindamine_r_body { display: none; }
</style>
</%def>

${_("Hindaja eelvaade")} -
% if c.hindaja:
${h.link_to(c.hindaja.kasutaja.nimi,
h.url('hindamine_sooritused', toimumisaeg_id=c.toimumisaeg.id, hindaja_id=c.hindaja.id))}
${c.hindamiskogum.tahis}
% else:
${_("Hindamiskogum")} ${c.hindamiskogum.tahis}
% endif

<%include file="/avalik/khindamine/hindamine.sisu.mako"/>

##<script>
##  ## eelvaate tõttu disableme hindamise sisestamise väljad
##  $(function(){
##    $('input[type="text"],input[type="radio"],select,textarea').prop('disabled', true);
##  });
##</script>
