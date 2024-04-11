## Testiosa sooritamise vaatamine
<%inherit file="/common/formpage.mako"/>
<%def name="require()">
<% c.includes['test'] = True %>
</%def>
<%namespace name="tab" file='/common/tab.mako'/>
<%def name="draw_tabs()">
% if c.test.diagnoosiv:
${tab.draw('testisooritus', h.url('toovaatamine', id=c.sooritus.sooritaja_id), _("Tagasiside"))}
% else:
${tab.draw('testisooritus', h.url('toovaatamine', id=c.sooritus.sooritaja_id), _("Tulemus"))}
% endif
% if len(c.sooritaja.sooritused) > 1:
${tab.draw('sooritus', h.url('toovaatamine_osa', test_id=c.test.id, testiosa_id=c.sooritus.testiosa_id, alatest_id='', id=c.sooritus.id), c.sooritus.testiosa.nimi)}
% else:
${tab.draw('sooritus', h.url('toovaatamine_osa', test_id=c.test.id, testiosa_id=c.sooritus.testiosa_id, alatest_id='', id=c.sooritus.id), _("Näita vastuseid"))}
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
${c.test.nimi} | ${c.sooritaja.nimi}
</%def>      

<%def name="breadcrumbs()">
${h.crumb(_("Tsentraalsed testid"))}
${h.crumb(_("Testitööde vaatamine"), h.url('toovaatamised'))}
${h.crumb('%s, %s' % (c.sooritaja.test.nimi, c.sooritaja.nimi), h.url('toovaatamine',id=c.sooritaja.id))}
</%def>
<% 
  c.url_to_alatest = lambda alatest :  h.url('toovaatamine_osa', test_id=c.test.id, testiosa_id=c.testiosa.id, id=c.sooritus.id, alatest_id=alatest.id)
%>
<%include file="/avalik/sooritamine/testiosasisu.mako"/>
