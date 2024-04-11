## Testiosa sooritamine
<%inherit file="/common/formpage.mako"/>
<%def name="require()">
<%
c.includes['form'] = True
c.includes['test'] = True
%>
</%def>
<%namespace name="tab" file='/common/tab.mako'/>
<%def name="active_menu()">
<% c.menu1 = 'tulemused' %>
</%def>

<%def name="draw_tabs()">
% if c.test.diagnoosiv:
${tab.draw('tulemused', h.url('tulemus', id=c.sooritus.sooritaja_id), _("Tagasiside"))}
% else:
${tab.draw('tulemused', h.url('tulemus', id=c.sooritus.sooritaja_id), _("Tulemus"))}
% endif
<% url_s = h.url('tulemus_osa', test_id=c.test.id, testiosa_id=c.sooritus.testiosa_id, alatest_id='', id=c.sooritus.id) %>
% if len(c.sooritus.sooritaja.sooritused) > 1:
${tab.draw('sooritus', url_s, c.sooritus.testiosa.nimi)}
% else:
${tab.draw('sooritus', url_s, _("Näita vastuseid"))}
% endif
</%def>

<%def name="page_title()">
${_("Vastuste vaatamine")}
| ${c.test.nimi} 
% if c.testiosa.nimi:
| ${c.testiosa.nimi}
% endif
</%def>      

<%def name="breadcrumbs()">
${h.crumb(_("Tulemused"), h.url('tulemused'))}
${h.crumb(c.sooritus.sooritaja.test.nimi, h.url('tulemus',id=c.sooritus.sooritaja_id))}
${h.crumb(_("Vastuste vaatamine"))}
</%def>
<% 
  c.url_to_alatest = lambda alatest :  h.url('tulemus_osa', test_id=c.test.id, testiosa_id=c.testiosa_id, id=c.sooritus.id, alatest_id=alatest.id)
  if not c.test.oige_naitamine:
     c.btn_correct = c.prepare_correct = False
  c.olen_sooritaja = True
%>
<%include file="/avalik/sooritamine/testiosasisu.mako"/>

${h.btn_to(_("Tagasi"), h.url('tulemus', id=c.sooritus.sooritaja_id))}

