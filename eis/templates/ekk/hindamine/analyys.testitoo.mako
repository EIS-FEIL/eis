## Ühe soorituse ühe hindamiskogumi vaatamine
<%inherit file="/common/formpage.mako"/>
<%def name="require()">
<%
c.includes['test'] = True
c.includes[ 'subtabs'] = True
%>
</%def>

<%def name="page_title()">
${c.toimumisaeg.testimiskord.test.nimi} ${c.toimumisaeg.millal} |
${c.sooritus.tahis} ${c.hindamiskogum and c.hindamiskogum.tahis or ''}
</%def>      

<%def name="breadcrumbs()">
${h.crumb(_("Hindamine"), h.url('hindamised'))} 
${h.crumb('%s %s' % (c.toimumisaeg.testimiskord.test.nimi, c.toimumisaeg.millal))} 
${h.crumb(_("Hindamise analüüs"), h.url('hindamine_analyys_hindamised3', toimumisaeg_id=c.toimumisaeg.id))}
${h.crumb(u'%s %s' % (c.sooritus.tahis, c.hindamiskogum and c.hindamiskogum.tahis or ''))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'hindamised' %>
</%def>

<%def name="draw_before_tabs()">
<%include file="before_tabs.mako"/>
</%def>

<%def name="draw_tabs()">
<% c.tab1 = 'analyys' %>
<%include file="tabs.mako"/>
</%def>

<%def name="draw_subtabs()">
<%include file="analyys.tabs.mako"/>
</%def>

<%include file="ekspert.sooritusinfo.mako"/>
${self.hindamiskogumid()}

<%def name="hindamiskogumid()">
<table  class="table table-borderless table-striped" width="100%">
    <tr>
      <th colspan="2">${_("Hindamiskogum")}</th>
      <th>${_("Olek")}</th>
      <th>${_("Tulemus")}</th>
      <th>${_("Max")}</th>
      <th>${_("Hindamise liik")}</th>
      <th>${_("Arvutihinnatav")}</th>
      <th>${_("Tase")}</th>
      <th>${_("Probleem")}</th>
      <th>${_("Hindajad")}</th>
    </tr>
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
      % endif
      </td>
      % if holek and on_ylesanded:
      <td>${holek.staatus_nimi}</td>
      <td>
        % if holek.staatus == const.H_STAATUS_HINNATUD or on_vaie:
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
      <td>
        % if holek:
        % for hi in holek.hindamised:
        <div>
          <% hik = hi.hindaja_kasutaja %>
          ${hik and hik.nimi} (${hi.staatus_nimi} ${hi.liik_nimi})
        </div>
        % endfor
        % endif
      </td>
    </tr>
      % endif
    % endfor
</table>
</%def>   
