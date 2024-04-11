<%inherit file="/common/formpage.mako"/>
<%def name="require()">
<% c.includes['subtabs'] = True %>
</%def>
<%def name="page_title()">
${_("Testi korraldamine")} | ${c.toimumisaeg.testimiskord.test.nimi} ${h.str_from_date(c.toimumisaeg.alates)}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Korraldamine"), h.url('korraldamised'))} 
${h.crumb('%s %s' % (c.toimumisaeg.testimiskord.test.nimi, h.str_from_date(c.toimumisaeg.alates)))} 
${h.crumb(_("Soorituskohtade planeerimine"), h.url('korraldamine_soorituskohad', toimumisaeg_id=c.toimumisaeg.id))}
${h.crumb(c.testikoht.koht.nimi)}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'korraldamised' %>
</%def>

<%def name="draw_before_tabs()">
<%include file="before_tabs.mako"/>
</%def>

<%def name="draw_tabs()">
<% c.tab1 = 'soorituskohad' %>
<%include file="tabs.mako"/>
</%def>

<%def name="draw_subtabs()">
<%include file="koht.tabs.mako"/>
</%def>

<%
  c.koht = c.testikoht.koht 
  c.can_update = c.user.has_permission('korraldamine', const.BT_UPDATE, obj=c.testikoht)
  if not c.can_update:
    c.is_edit = False
%>
${h.form_save(None)}

<table width="100%"  class="table">
  <tr>
    <td class="fh">${_("Tähis")}</td>
    <td>${c.testikoht.tahis}</td>
    <td class="frh">${_("Reg nr")}</td>
    <td>${c.koht.kool_regnr}</td>
    <td class="frh">${_("EHIS ID")}</td>
    <td>${c.koht.kool_id}</td>
  </tr>
  <tr>
    <td class="fh">${_("Nimi")}</td>
    <td colspan="3">${c.koht.nimi}</td>
    <td align="right" colspan="2">
      ${h.btn_to(_("Soorituskoha haldus"), h.url('admin_koht', id=c.koht.id), target='_blank')}

      % if c.user.has_permission('kohteelvaade', const.BT_SHOW):
      ${h.btn_to(_("Soorituskoha administraatori eelvaade"), '/eis/kohteelvaade/%s' % c.testikoht.koht_id, target='_blank')}
      % endif
    </td>
  </tr>
  <tr>
    <td class="fh">${_("Piirkond")}</td>
    <td colspan="5">${c.koht.piirkond and c.koht.piirkond.nimi or ''}</td>
  </tr>
  <tr>
    <td class="fh">${_("Aadress")}</td>
    <td colspan="5">
      ${c.koht.tais_aadress}
    </td>
  </tr>
  <tr>
    <td class="fh">${_("Telefon")}</td>
    <td colspan="5">${c.koht.telefon}</td>
  </tr>
  <tr>
    <td class="fh">${_("E-post")}</td>
    <td colspan="5">${c.koht.epost}</td>
  </tr>
  <tr>
    <td class="fh">${_("Kohtade arv")}</td>
    <td colspan="5">${c.koht.ptestikohti}</td>
  </tr>
  <tr>
    <td class="fh">${_("E-kohtade arv")}</td>
    <td colspan="5">${c.koht.etestikohti}</td>
  </tr>
  <tr>
    <td class="fh">${_("Ruumid")}</td>
    <td colspan="5">
      <%include file="koht.ruumid.mako"/>
    </td>
  </tr>
</table>
% if c.can_update:
${h.submit(_("Salvesta"))}
% endif
${h.end_form()}
