## Testiosa soorituse vaatamine
<%inherit file="/common/formpage.mako"/>
<%def name="require()">
<%
c.includes['form'] = True
c.includes[ 'test'] = True
%>
</%def>
<%namespace name="tab" file='/common/tab.mako'/>
<%def name="draw_tabs()">
${tab.draw('sooritus', None, c.test.nimi, True, True)}
</%def>

<%def name="page_title()">
${_("Vastuste vaatamine")}
| ${c.test.nimi} 
% if c.testiosa.nimi:
| ${c.testiosa.nimi}
% endif
</%def>      

<%def name="breadcrumbs()">
${h.crumb(_("Registreerimisnimekirjad"), h.url('nimekirjad_testimiskorrad'))}
${h.crumb(_("Testidele registreerimise kontroll"), h.url('nimekirjad_kontrollid'))}
${h.crumb(c.item.sooritaja.nimi)}
</%def>
<% 
  c.sooritus = c.item
  if c.is_edit:
     c.url_to_alatest = lambda alatest :  h.url('tulemus_edit_osa', test_id=c.test.id, testiosa_id=c.testiosa_id, id=c.item.id, alatest_id=alatest.id)
  else:
     c.url_to_alatest = lambda alatest :  h.url('nimekirjad_kontroll_tulemus_osa', test_id=c.test.id, testiosa_id=c.testiosa_id, id=c.item.id, alatest_id=alatest.id)
     if not c.test.oige_naitamine:
        c.prepare_correct = False
        c.btn_correct = False
  c.olen_sooritaja = True
%>
<%include file="/avalik/sooritamine/testiosasisu.mako"/>

<br/>
${h.btn_to(_("Tagasi"), h.url('nimekirjad_kontroll_tulemus', id=c.sooritus.sooritaja_id))}

