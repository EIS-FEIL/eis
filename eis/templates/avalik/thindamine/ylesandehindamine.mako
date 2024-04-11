## -*- coding: utf-8 -*- 
<%inherit file="/common/formpage.mako"/>
<%def name="draw_tabs()">
<% c.tab1 = 'hindamised' %>
<%include file="/avalik/testid/tabs.mako"/>
</%def>
<%def name="require()">
<%
  c.includes['subtabs'] = True
  c.includes['test'] = c.includes['spectrum'] = True
  c.includes['math'] = True
  c.pagexl = True
%>
</%def>
<%def name="draw_subtabs()">
<% c.tab2 = 'ylesandehindamised' %>
<%include file="hindamised.tabs.mako"/>
</%def>

<%def name="page_title()">
${c.test.nimi or ''} | ${_("Hindamine")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_('Minu töölaud'), h.url('tookogumikud'))}
${h.crumb(c.test.nimi or _('Test'))} 
${h.crumb(_('Hindamine'), h.url('test_toohindamised', test_id=c.test.id, testiruum_id=c.testiruum.id))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'tookogumikud' %>
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

<h1>${_("Ülesandekaupa hindamine")}</h1>
<%include file="/avalik/khindamine/hindamine.sisu.mako"/>
