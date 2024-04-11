## Testiosa sooritamise hindamine
<%inherit file="/common/page.mako"/>
<%def name="require()">
<%
  c.includes['test'] = c.includes['spectrum'] = True 
  c.includes['math'] = True
  c.pagexl = True
%>
</%def>

<%def name="page_title()">
${c.test.nimi} | ${c.sooritus.tahised}
</%def>      

<%def name="breadcrumbs()">
${h.crumb(_("Hindamine"))}
${h.crumb(_("Tsentraalsed testid"), h.url('khindamised'))} 
${h.crumb('%s, %s' % (c.test.nimi, c.hindamiskogum.tahis), h.url('khindamine_vastajad', toimumisaeg_id=c.toimumisaeg.id, hindaja_id=c.hindaja.id))}
${h.crumb(_("Testitöö kood") +  ' %s' % c.sooritus.tahised,
h.url('khindamine_hkhindamised', toimumisaeg_id=c.toimumisaeg.id, hindaja_id=c.hindaja_id, sooritus_id=c.sooritus.id))}
</%def>

<%def name="active_menu()">
<% c.menu1 = 'hindamine' %>
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

<h1>${_("Testitöö hindamine")}</h1>

<%include file="hindamine.sisu.mako"/>

