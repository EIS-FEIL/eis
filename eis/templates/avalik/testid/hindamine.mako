## Avaliku testi sooritamise hindamine
<%inherit file="/common/formpage.mako"/>
<%def name="require()">
<% c.includes['test'] = True %>
</%def>
<%def name="draw_tabs()">
<% c.tab1 = 'sooritus' %>
<%include file="tabs.mako"/>
</%def>

<%def name="page_title()">
${c.test.nimi or ''} | ${_("Hindamine")} | ${c.sooritus.sooritaja.nimi}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_('Töölaud'), h.url('tookogumikud'))}
${h.crumb(c.test.nimi or _('Test'))} 
${h.crumb(_('Hindamine'), h.url('test_hindamine_vastused', test_id=c.test_id, testiruum_id=c.testiruum_id))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'tookogumikud' %>
</%def>

<table width="100%" class="box">
  <tr>
    <td class="frh2">${_("Sooritaja")}</td>
    <td><h1>${c.sooritus.sooritaja.nimi}</h1><!--${c.sooritus.id}--></td>
    <td class="frh2">${_("Soorituskeel")}</td>
    <td>${model.Klrida.get_lang_nimi(c.sooritus.sooritaja.lang)}</td>
  </tr>
</table>

<% 
  c.counter = -1
  c.submit_url = h.url('test_hindamine', test_id=c.test_id, id=c.sooritus.id, testiruum_id=c.testiruum.id, hindamiskogum_id=c.hindamiskogum.id)
  c.omahindamine = True
  c.koik_alatestid = True
  ## ylesannet kuvades ei kuvata mitte-interaktsiivseid sisuplokke
  c.no_static_blocks = True
%>
<%include file="../khindamine/testiosasisu.mako"/>

