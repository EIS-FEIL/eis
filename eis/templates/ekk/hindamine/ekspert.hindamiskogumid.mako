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
<%def name="active_menu()">
<% c.menu1 = 'hindamised' %>
</%def>

<%def name="breadcrumbs()">
${h.crumb(_("Hindamine"), h.url('hindamised'))} 
${h.crumb('%s %s' % (c.toimumisaeg.testimiskord.test.nimi, c.toimumisaeg.millal))} 
${h.crumb(_("Eksperthindamine"), h.url('hindamine_eksperttood', toimumisaeg_id=c.toimumisaeg.id))}
${h.crumb(_("Test") + ' %s' % c.sooritus.tahised,
h.url('hindamine_ekspert_kogum', toimumisaeg_id=c.toimumisaeg.id, id=c.sooritus.id))}
% if c.hindamiskogum:
${h.crumb(_("Hindamiskogum") + ' %s' % c.hindamiskogum.tahis)}
% endif
</%def>

<%def name="draw_before_tabs()">
<%include file="before_tabs.mako"/>
</%def>

<%def name="draw_tabs()">
<% c.tab1 = 'ekspert' %>
<%include file="tabs.mako"/>
</%def>

<%def name="draw_subtabs()">
<%include file="ekspert.tabs.mako"/>
</%def>

<%def name="subtabs_label()">
  ${h.flb(_("Hindamise liik"), 'hliik')}
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

<%
   sooritaja = c.sooritus.sooritaja
   on_vaie = sooritaja.vaie_esitatud and True or False
   saab_hindaja6 = c.toimumisaeg.testimiskord.tulemus_kinnitatud \
       and c.user.has_permission('ekk-hindamine6', const.BT_UPDATE, obj=c.test)
%>
<h3>${_("Hindamiskogumid")}</h3>
<table  class="table table-borderless table-striped">
  <thead>
    <tr>
      <th colspan="2">${_("Hindamiskogum")}</th>
      <th>${_("Olek")}</th>
      <th>${_("Tulemus")}</th>
      <th>${_("Max")}</th>
      <th>${_("Hindamise liik")}</th>
      <th>${_("Arvutihinnatav")}</th>
      <th>${_("Tase")}</th>
      <th>${_("Probleem")}</th>
    </tr>
  </thead>
  <tbody>
<% kursus = c.sooritus.sooritaja.kursus_kood %>
    % for hk in c.testiosa.hindamiskogumid:
      % if hk.staatus and hk.kursus_kood == kursus:
        <% 
           holek = c.sooritus.get_hindamisolek(hk)
           hk_title = '%s %s' % (hk.tahis or '', hk.nimi or '')
           if holek and holek.puudus:
              on_ylesanded = holek.komplekt_on_hindamiskogumis()
           else:
              on_ylesanded = True
        %>
    <tr>
      <td valign="top">
        ${hk_title}
      </td>
      <td>
      % if not on_ylesanded:
        ## valitud komplekt ei sisalda selle hindamiskogumi ylesandeid
        ${_("Ei sooritanud")}
      % elif c.sooritus.ylesanneteta_tulemus:
         Tulemused ainult protokollil
      % else:
        ${h.link_to(_("Vaata"), h.url('hindamine_ekspert_vaatamised', toimumisaeg_id=c.toimumisaeg.id, sooritus_id=c.sooritus.id, hindamiskogum_id=hk.id))}

        <!-- olen_ekspert: ${c.olen_ekspert} eksperthindaja:${c.ekspert_labiviija} -->
        % if c.olen_ekspert or c.ekspert_labiviija:
        ${h.link_to(_("Hinda"), h.url('hindamine_ekspert_hindamised',
        toimumisaeg_id=c.toimumisaeg.id, sooritus_id=c.sooritus.id,
        hindamiskogum_id=hk.id))}
        % elif saab_hindaja6:
          ${h.link_to_dlg(_("VI hindamine"),
             h.url('hindamine_edit_hindamispohjus',
             toimumisaeg_id=c.toimumisaeg.id, id=c.sooritus.id, hindamiskogum_id=hk.id),
             title=_("Hindamiskogum: {s}").format(s=hk.nimi or hk.tahis), width=900)}
        % endif
      % endif
      </td>
      % if holek and on_ylesanded:
      <td>${holek.staatus_nimi}</td>
      <td>
        % if holek.pallid is not None:
        ##% if holek.staatus == const.H_STAATUS_HINNATUD or on_vaie:
        ${h.fstr(holek.pallid)}p
        % endif
      </td>
      <td>${h.fstr(holek.hindamiskogum.max_pallid)}p</td>
      % else:
      <td colspan="3"></td>
      % endif

        % if holek and on_ylesanded:
      <td>${hk.hindamine_nimi}</td>
      <td>${h.sbool(hk.arvutihinnatav)}</td>
      <td>
        % if holek.hindamistase == const.HTASE_VALIMIKOOPIA:
        koopia
        % elif holek.hindamistase == const.HTASE_ARVUTI:
        arvuti
        % else:
        ${holek.hindamistase}
        % endif
      </td>
      <td>${holek.selgitus or holek.hindamisprobleem_nimi}</td>
        % else:
      <td></td>
      <td></td>
      <td></td>
      <td></td>
        % endif
    </tr>
      % endif
    % endfor
  </tbody>
</table>

% if c.sooritus.on_rikkumine:
${h.alert_warning(_("Rikkumise tõttu on töö hinnatud 0 punktiga.") + '<br/>' + c.sooritus.rikkumiskirjeldus, False)}
% endif
% if saab_hindaja6:
${h.btn_to_dlg(_("Märgi rikkumise andmed"),
h.url('hindamine_edit_rikkumisotsus', toimumisaeg_id=c.toimumisaeg.id, id=c.sooritus.id),
title=_("Rikkumine"), level=2)}
% endif

