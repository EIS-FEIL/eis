<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Profiilileht")} | ${c.kasutaja.nimi}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Testid"), h.url('otsing_testisooritused'))}
${h.crumb('%s, %s' % (c.sooritaja.test.nimi, c.sooritaja.nimi), h.url('otsing_testisooritus',id=c.sooritaja.id))}
${h.crumb("Profiilileht", h.url('otsing_profiilileht', id=c.item.id))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'otsing' %>
</%def>

<h2>${c.kasutaja.nimi}</h2>

${c.tagasiside_html}
