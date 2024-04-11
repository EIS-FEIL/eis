## Testiosa sooritamise vaatamine
<%inherit file="/common/formpage.mako"/>
<%def name="require()">
<% c.includes['test'] = True %>
</%def>
<%namespace name="tab" file='/common/tab.mako'/>
<%def name="active_menu()">
<% c.menu1 = 'otsing' %>
</%def>
<%def name="draw_tabs()">
% if c.test.diagnoosiv:
${tab.draw('testisooritus', h.url('otsing_testisooritus', id=c.sooritus.sooritaja_id), _("Tagasiside"))}
% else:
${tab.draw('testisooritus', h.url('otsing_testisooritus', id=c.sooritus.sooritaja_id), _("Tulemus"))}
% endif
% if len(c.sooritus.sooritaja.sooritused) > 1:
${tab.draw('sooritus', h.url('tulemus_osa', test_id=c.test.id, testiosa_id=c.sooritus.testiosa_id, alatest_id='', id=c.sooritus.id), c.sooritus.testiosa.nimi)}
% else:
${tab.draw('sooritus', h.url('tulemus_osa', test_id=c.test.id, testiosa_id=c.sooritus.testiosa_id, alatest_id='', id=c.sooritus.id), _("Näita vastuseid"))}
% endif
</%def>

<%
  k = c.sooritaja.kasutaja
  tahised = c.sooritus.tahised
%>
<h2>
  ${c.sooritaja.nimi}
% if tahised:
  (${k.isikukood}, ${_("sooritus")} ${tahised})
% else:
  (${k.isikukood})
% endif
</h2>
<%def name="page_title()">
${c.test.nimi} | ${c.sooritus.sooritaja.nimi}
</%def>      

<%def name="breadcrumbs()">
${h.crumb(_("Testid"), h.url('otsing_testisooritused'))}
${h.crumb('%s, %s' % (c.test.nimi, c.sooritaja.nimi), h.url('otsing_testisooritus',id=c.sooritaja.id))}
${h.crumb(c.sooritus.sooritaja.nimi)}
</%def>
<% 
  c.url_to_alatest = lambda alatest :  h.url('tulemus_osa', test_id=c.test.id, testiosa_id=c.testiosa.id, id=c.sooritus.id, alatest_id=alatest.id)
%>
<%include file="tulemus.testiosasisu.mako"/>
