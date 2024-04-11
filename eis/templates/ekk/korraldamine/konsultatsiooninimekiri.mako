<%inherit file="/common/formpage.mako"/>
<%def name="page_title()">
${_("Testi korraldamine")} | ${c.toimumisaeg.testimiskord.test.nimi} ${h.str_from_date(c.toimumisaeg.alates)}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Korraldamine"), h.url('korraldamised'))} 
${h.crumb('%s %s' % (c.toimumisaeg.testimiskord.test.nimi, h.str_from_date(c.toimumisaeg.alates)))} 
${h.crumb(_("Konsultatsiooninimekirjad"),h.url('korraldamine_konsultatsiooninimekirjad',
toimumisaeg_id=c.toimumisaeg.id))}
${h.crumb(c.item.nimi, h.url_current())}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'korraldamised' %>
</%def>

<%def name="draw_before_tabs()">
<%include file="before_tabs.mako"/>
</%def>

<%def name="draw_tabs()">
<%include file="tabs.mako"/>
</%def>

<% cnt=0 %>
<table width="100%" class="table table-borderless table-striped tablesorter" border="0" >
  <caption>${c.item.nimi}</caption>
  <thead>
    <tr>
      ${h.th(_("Isikukood"))}
      ${h.th(_("Eesnimi"))}
      ${h.th(_("Perekonnanimi"))}
      ${h.th(_("Test"))}
    </tr>
  </thead>
  <tbody>
    % for eesnimi, perenimi, isikukood, t_nimi in c.items:
    <% cnt += 1 %>
    <tr>
      <td>${isikukood}</td>
      <td>${eesnimi}</td>
      <td>${perenimi}</td>
      <td>${t_nimi}</td>
    </tr>
    % endfor
  </tbody>
</table>
<br/>
% if cnt==1:
${_("Kokku 1 sooritaja")}
% else:
${_("Kokku {n} sooritajat").format(n=cnt)}
% endif

