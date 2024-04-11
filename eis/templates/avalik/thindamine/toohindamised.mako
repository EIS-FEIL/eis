<%inherit file="/common/formpage.mako"/>
<%def name="draw_tabs()">
<% c.tab1 = 'hindamised' %>
<%include file="/avalik/testid/tabs.mako"/>
</%def>
<%def name="require()">
<%
c.includes['subtabs'] = True
%>
</%def>
<%def name="draw_subtabs()">
<% c.tab2 = 'toohindamised' %>
<%include file="hindamised.tabs.mako"/>
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

% if c.test.testiliik_kood != const.TESTILIIK_KOOLIPSYH:
## koolipsühholoogi testis ei või kõigi sooritajate tulemusi korraga kuvada

% if not c.items:
${h.alert_error(_("Testi lõpetanud sooritajaid ei ole"))}
% else:
${self.sooritajad_tbl()}
% endif
% endif

<%def name="sooritajad_tbl()">
<%
  testiylesanded = [ty for ty in c.testiosa.testiylesanded if ty.liik == const.TY_LIIK_Y and ty.arvutihinnatav == False]
  if c.lubatud_ty_id:
     testiylesanded = [ty for ty in testiylesanded if ty.id in c.lubatud_ty_id]
%>
<div style="overflow-x:auto">
<table class="table table-striped tablesorter" width="100%" >
  <caption>${_("Testitööd")}</caption>
  <thead>
    <tr>
      ${h.th(_('Sooritaja'))}
      % for ty in testiylesanded:
      ${h.th(ty.tahis)}
      % endfor
      ${h.th(_('Kokku'))}
      % if not c.cannot_edit:
      ${h.th('', sorter='false')}
      % endif
    </tr>
  </thead>
  <tbody>
    % for rcd in c.items:
    <% 
       tos, eesnimi, perenimi, ho_mittekasitsi, h_staatus = rcd
       nimi = '%s %s' % (eesnimi, perenimi)
       res = c.res.get(tos.id)
       url_edit = h.url('test_sooritus_hindamised', test_id=c.test_id, testiruum_id=c.testiruum_id, sooritus_id=tos.id)
       if c.test.opetajale_peidus:
          ho_mittekasitsi = True
    %>
    <tr>
      <td>
        <!--${perenimi},${eesnimi}-->
        ${nimi}
      </td>
      % for ty in testiylesanded:
      <%
        try:
           y_pallid, varv = res and res.get((ty.alatest_seq, ty.seq))
        except:
           y_pallid = varv = None
        tdstyle = varv and 'style="background-color:%s"' % varv or ''
      %>
      <td ${tdstyle}>${h.fstr(y_pallid)}</td>
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
      % if not c.cannot_edit:
      <td>
        % if not ho_mittekasitsi:
        % if not h_staatus or h_staatus == const.H_STAATUS_HINDAMATA:
        ${h.btn_to(_("Alusta hindamist"), url_edit)}
        % elif h_staatus != const.H_STAATUS_HINNATUD:
        ${h.btn_to(_("Jätka hindamist"), url_edit)}
        % endif
        % endif
      </td>
      % endif
    </tr>
    % endfor
  </tbody>
</table>
</div>
</%def>
