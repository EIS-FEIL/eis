<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Tsentraalse kirjaliku testi hindamine")}
</%def>
<%def name="breadcrumbs()">
${h.crumb(_("Hindamine"))}
${h.crumb(_("Tsentraalsed testid"), h.url('khindamised'))} 
${h.crumb('%s, %s' % (c.test.nimi, c.hindamiskogum.tahis), h.url('khindamine_vastajad', toimumisaeg_id=c.toimumisaeg.id, hindaja_id=c.hindaja.id))}
</%def>

<%def name="require()">
<% c.includes['test'] = True %>
</%def>

<%def name="active_menu()">
<% c.menu1 = 'hindamine' %>
</%def>
<h1>${_("Hindamiskogum")}
  <b>${c.hindamiskogum.nimi}
    % if c.hindamiskogum.nimi != c.hindamiskogum.tahis:
    (${c.hindamiskogum.tahis})
    % endif
  </b>
</h1>
<%include file="vastajad_sisu.mako"/>

