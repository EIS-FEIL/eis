## Ühe soorituse hindamine või vaatamine eksperdi poolt
## kuvatakse soorituse hindamisolekute tabel
## või kirjalik sooritus
## või suuline sooritus
<%inherit file="/common/formpage.mako"/>
<%def name="require()">
<%
c.includes['test'] = True
c.includes['subtabs'] = True
c.includes['subtabs_label'] = True  
%>
</%def>

<%def name="page_title()">
${c.test.nimi} | ${c.sooritus.tahis}
</%def>      

<%def name="breadcrumbs()">
${h.crumb(_("Hindamine"), h.url('hindamised'))} 
${h.crumb('%s %s' % (c.toimumisaeg.testimiskord.test.nimi, c.toimumisaeg.millal))} 
${h.crumb(_("Eksperthindamine"), h.url('hindamine_eksperttood', toimumisaeg_id=c.toimumisaeg.id))}
${h.crumb(_("Testitöö") + ' %s' % c.sooritus.tahised,
h.url('hindamine_ekspert_kogum', toimumisaeg_id=c.toimumisaeg.id, id=c.sooritus.id))}
% if c.hindamiskogum:
${h.crumb(_("Hindamiskogum") + ' %s' % c.hindamiskogum.tahis)}
% endif
</%def>
<%def name="active_menu()">
<% c.menu1 = 'hindamised' %>
</%def>

<%def name="page_headers()">
<style>
## parema poole peitmine
#hindamine_p_div.hidden-r {  flex-direction: column-reverse;  }
#hindamine_p_div.hidden-r .r_body_hider { display: none; }
#hindamine_p_div.hidden-r .hindamine_r_tabs { float: right; }
#hindamine_p_div.hidden-r #hindamine_r_body { display: none; }
</style>
</%def>

<%def name="draw_before_tabs()">
<%include file="before_tabs.mako"/>
</%def>

<%def name="draw_tabs()">
<% c.tab1 = 'ekspert' %>
<%include file="tabs.mako"/>
</%def>

<%def name="draw_subtabs()">
<% c.tab2 = 'ekspertkogumid' %>
<%include file="ekspert.tabs.mako"/>
</%def>

<%def name="subtabs_label()">
  ${h.flb(_("Hindamise liik"),'hliik')}
  <span class="brown ml-1" id="hliik">
      % if c.olen_hindaja6:
      ${_("VI hindamine")}
      % elif c.toimumisaeg.testimiskord.tulemus_kinnitatud:
      ${_("Vaide korral hindamine")}
      % else:
      ${_("IV hindamine")}
      % endif
  </span>
</%def>

<%include file="ekspert.sooritusinfo.mako"/>

% for hindamine in c.hindamised + [c.hindamine]:
% if hindamine and hindamine.hindamispohjus:
<div class="row">
  ${h.flb3(_("VI hindamise põhjus"), 'hindamispohjus')}
  <div class="col" id="hindamispohjus">
    ${hindamine.hindamispohjus}
  </div>
</div>
% endif
% endfor

% if c.testiosa.vastvorm_kood in (const.VASTVORM_KE, const.VASTVORM_SE, const.VASTVORM_KP, const.VASTVORM_I):
<%include file="ekspert.hindamine.sisu.mako"/>
% else:
<%
  c.testiruum = c.sooritus.testiruum
  c.items = [c.sooritus]
%>
<%include file="ekspert.suulinesisu.mako"/>
% endif


