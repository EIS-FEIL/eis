<%inherit file="/common/formpage.mako"/>
<%def name="draw_tabs()">
<%include file="tabs.mako"/>
</%def>

<%def name="page_title()">
${c.test.nimi or ''} | ${_("Hindamine")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_('Minu töölaud'), h.url('tookogumikud'))}
${h.crumb(c.test.nimi or _('Test'))} 
${h.crumb(_('Hindamine'))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'tookogumikud' %>
</%def>

<%include file="vastused.statistika.mako"/>

<br/>
% if len(c.sooritused) > 0:
% if c.test.testiliik_kood == const.TESTILIIK_KOOLIPSYH:
## koolipsühholoogi testis ei või kõigi sooritajate tulemusi korraga kuvada
<table class="table table-borderless table-striped tablesorter" width="100%" >
  <caption>${_("Testitööd")}</caption>
  <thead>
    <tr>
      ${h.th(_('Sooritaja'))}
    </tr>
  </thead>
  <tbody>
    % for rcd in c.sooritused:
    <% 
       tos, eesnimi, perenimi = rcd
       res = c.res.get(tos.id)       
    %>
    <tr>
      <td>
        <!--${perenimi},${eesnimi}-->
        ${h.link_to('%s %s' % (eesnimi, perenimi),
        h.url('test_tulemus', test_id=c.test_id, testiruum_id=c.testiruum_id, id=tos.id))}
      </td>
    </tr>
    % endfor
  </tbody>
</table>

% else:
<%
  hindamiskogumid = [hk for hk in c.testiosa.hindamiskogumid if hk.staatus == const.B_STAATUS_KEHTIV]
  testiylesanded = [ty for ty in c.testiosa.testiylesanded if ty.liik == const.TY_LIIK_Y]
%>
<table class="table table-borderless table-striped tablesorter" width="100%" >
  <caption>${_("Testitööd")}</caption>
  <thead>
    <tr>
      ${h.th(_('Sooritaja'))}
      % if len(hindamiskogumid) != 1:
      ${h.th(_('Hindamiskogumid'), sorter='false')}
      % endif
      % for ty in testiylesanded:
      ${h.th(ty.tahis)}
      % endfor
      ${h.th(_('Kokku'))}
    </tr>
  </thead>
  <tbody>
    % for rcd in c.sooritused:
    <% 
       tos, eesnimi, perenimi = rcd
       nimi = '%s %s' % (eesnimi, perenimi)
       res = c.res.get(tos.id)
    %>
    <tr>
      <td>
        <!--${perenimi},${eesnimi}-->
        % if len(hindamiskogumid) == 1:
        <%
          hk = hindamiskogumid[0]
          holek = tos.get_hindamisolek(hk)
        %>
        % if not holek.mittekasitsi:
        ${h.link_to(nimi, h.url('test_hindamine', test_id=c.test_id, testiruum_id=c.testiruum_id, id=tos.id, hindamiskogum_id=hk.id))}
        % else:
        ${nimi}
        % endif
        % else:
        ${nimi}
        % endif
      </td>
      % if len(hindamiskogumid) != 1:
      <td>
        % for hk in hindamiskogumid:
        <% holek = tos.get_hindamisolek(hk) %>
        % if holek and not holek.mittekasitsi:
        ${h.link_to(hk.tahis, h.url('test_hindamine', test_id=c.test_id, testiruum_id=c.testiruum_id, id=tos.id, hindamiskogum_id=hk.id))}        
        % else:
        ${hk.tahis}
        % endif
        % endfor
      </td>
      % endif
      % for ty in testiylesanded:
      <td>${res and h.fstr(res.get((ty.alatest_seq, ty.seq))) or ''}</td>
      % endfor
      <td>
        ${tos.get_tulemus()}

        % if c.test.testiliik_kood == const.TESTILIIK_KUTSE:
        <div style="white-space:nowrap">
              % for alatest in tos.alatestid:
              <% atos = tos.get_alatestisooritus(alatest.id) %>
              <div>
              ${alatest.nimi}
                % if atos and atos.staatus == const.S_STAATUS_TEHTUD and not c.test.pallideta:
              ${atos.get_tulemus(alatest.max_pallid) or atos.staatus_nimi}
                % elif atos:
              ${atos.staatus_nimi}
                % endif
              </div>
              % endfor
        </div>
        % endif
      </td>
    </tr>
    % endfor
  </tbody>
</table>

% endif
% endif
