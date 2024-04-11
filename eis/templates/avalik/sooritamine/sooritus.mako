## Testiosa sooritamine
<%inherit file="/common/formpage.mako"/>
<%def name="require()">
<%
c.includes['form'] = True
c.includes['countdown'] = True
c.includes['test'] = True
if not c.read_only:
  c.no_tabs = True
  c.no_breadcrumbs = True
  # kui käib sooritamine ning päis on testiosa või alatesti seadetes peidetud
  if c.testiosa and c.testiosa.peida_pais \
       or c.alatest and c.alatest.peida_pais \
       or c.user.get_seb_id():
     c.hide_header_footer = True
%>
</%def>
<%def name="active_menu()">
<% c.menu1 = 'sooritamised' %>
</%def>

<%namespace name="tab" file='/common/tab.mako'/>
<%def name="draw_tabs()">
<%
   nimi = c.test.nimi
   if c.kursus_nimi:
       nimi = nimi + f' ({c.kursus_nimi})'
%>
${tab.draw('sooritus', None, nimi, True, True)}
</%def>

<%def name="page_title()">
% if c.read_only:
${_("Vastuste vaatamine")}
% else:
${_("Testi sooritamine")}
% endif
| ${c.test.nimi} 
% if c.testiosa.nimi:
| ${c.testiosa.nimi}
% endif
</%def>      

<%def name="breadcrumbs()">
% if c.read_only:
% if not c.user.testpw_id:
${h.crumb(_("Sooritus"), h.url('sooritamised'))} 
% endif
${h.crumb(c.test.nimi, h.url('sooritamine_alustamine', test_id=c.test.id, sooritaja_id=c.sooritaja_id))}
${h.crumb(_("Vastuste vaatamine"))}
% endif
</%def>

<%def name="testiosasisu()">
<% 
  c.url_to_alatest = lambda alatest :  h.url_current('edit', alatest_id=alatest.id, rid=True)
  if not c.test.oige_naitamine:
        c.prepare_correct = False
        c.btn_correct = False
  c.submit_url = h.url_current('update', alatest_id=c.alatest and c.alatest_id or '')
  c.url_back = h.url('sooritamine_alustamine', test_id=c.test.id, sooritaja_id=c.sooritaja_id)
  c.olen_sooritaja = True
%>
% if c.no_tabs:
<h1>${c.test.nimi}</h1>
% endif
% if c.on_tugiisik or c.on_intervjuu:
<h4>${c.sooritaja_nimi}</h4>
% endif
<%include file="/avalik/sooritamine/testiosasisu.mako"/>

% if not c.read_only:
<span class="is_test_ongoing"></span>
% endif
</%def>

## menüü kaotamine sooritamise ajal, et minimeerida kognitiivset koormatust
<%def name="menu()">
% if c.read_only:
  ## tavaline menyy
  ${parent.menu()}
% endif
</%def>

${self.testiosasisu()}
