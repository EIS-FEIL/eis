<%inherit file="/common/formpage.mako"/>
<%def name="require()">
<%
c.includes['subtabs'] = True
c.includes['jstree'] = True
c.includes['ckeditor'] = True
%>
</%def>

<%def name="requirenw()">
<% c.pagenw = True %>
</%def>

<%def name="draw_tabs()">
<% c.tab1 = 'korraldus' %>
<%include file="tabs.mako"/>
</%def>

<%def name="draw_subtabs()">
<% c.tab2 = 'kogumid' %>
<%include file="korraldus.tabs.mako"/>
</%def>

<%def name="page_title()">
${_("Test")}: ${c.test.nimi or ''} | ${_("Ülesannete kogumid")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Testid"), h.url('testid'))} 
${h.crumb(c.test.nimi or _("Test"))} 
${h.crumb(_("Korraldus"))}
${h.crumb(_("Ülesannete kogumid"))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'testid' %>
</%def>

<% 

if c.hindamiskogum:
   c.hindamiskogum_id = c.hindamiskogum.id
   c.testiosa = c.hindamiskogum.testiosa
if c.sisestuskogum:
   c.sisestuskogum_id = c.sisestuskogum.id
   c.testiosa = c.sisestuskogum.testiosa

if not c.testiosa and len(c.test.testiosad):
   c.testiosa = c.test.testiosad[0]

c.can_update = c.user.has_permission('testimiskorrad', const.BT_UPDATE, c.test) and \
   c.test.staatus in (const.T_STAATUS_KOOSTAMISEL, const.T_STAATUS_KINNITATUD)

%>
<div class="row">
  <section class="col-12 col-md-4 col-xl-3">

      <table width="100%" class="table singleselect mb-1" >
        <caption>${_("Testiosad")}</caption>
        <thead>
        <tr>
          <th>${_("Tähis")}</th>
          <th>${_("Nimetus")}</th>
        </tr>
        </thead>
        <tbody>
        % for rcd in c.test.testiosad:
          % if rcd.id == c.testiosa.id:
        <tr class="selected">
          % else:
        <tr>
          % endif
          <td>${rcd.tahis}</td>
          <td>${h.link_to(rcd.nimi, h.url('test_kogumid', test_id=c.test.id,
          testiosa_id=rcd.id))}</td>
        </tr>
        % endfor
        </tbody>
      </table>

      % if c.testiosa and c.testiosa.vastvorm_kood in (const.VASTVORM_KP, const.VASTVORM_SP):
      <table width="100%" class="table singleselect mb-1" >
        <caption>${_("Sisestuskogumid")}</caption>
        <tbody>
        % for rcd in c.testiosa.sisestuskogumid:
        % if rcd.id:
          % if rcd.id == c.sisestuskogum_id:
        <tr class="selected">
          % else:
        <tr>
          % endif
          <td>${h.link_to('%s %s' % (rcd.tahis, rcd.nimi),
                  h.url('test_edit_sisestuskogum', test_id=c.test.id, id=rcd.id))}
          </td>
          <td>${h.remove(h.url('test_delete_sisestuskogum', test_id=c.test.id,id=rcd.id))}</td>
        </tr>
        % endif
        % endfor
        % if len(c.testiosa.sisestuskogumid) == 0:
        <tr><td>${_("Testiosas pole ühtki sisestuskogumit")}</td></tr>
        % endif
        </tbody>
      </table>
      % endif

      % if c.testiosa:
      <table width="100%" class="table singleselect mb-1" >
        <caption>${_("Hindamiskogumid")}</caption>
        <tbody>
      % for kv in c.testiosa.komplektivalikud:
        % for rcd in kv.hindamiskogumid:
          % if rcd.id:
            % if rcd.id == c.hindamiskogum_id:
        <tr class="selected">
            % else:
        <tr>
            % endif
            <td>
              <%
                 if c.testiosa.lotv:
                    yl_arv = len(rcd.valitudylesanded)
                 else:
                    yl_arv = len(rcd.testiylesanded)
              %>
              ${h.link_to('%s %s (%d)' % (rcd.tahis, rcd.nimi, yl_arv),
                  h.url('test_edit_hindamiskogum', test_id=c.test.id, id=rcd.id))}
            </td>
            <td>
              % if not rcd.staatus:
              ${h.remove(h.url('test_delete_hindamiskogum', test_id=c.test.id,id=rcd.id))}
              % endif
            </td>
        </tr>
          % endif
        % endfor
       % endfor
       </tbody>
      </table>
      % endif
  </section>
  <section class="col">
      % if c.hindamiskogum:
      <%include file="kogumid.hindamiskogum.mako"/>
      % elif c.sisestuskogum:
      <%include file="kogumid.sisestuskogum.mako"/>
      % endif
  </section>
</div>

<div class="d-flex flex-wrap">
  % if c.can_update:
  <div class="flex-grow-1">
      % if c.testiosa:
      % if c.can_add_new_hindamiskrit:
      ${h.btn_to_dlg(_("Lisa hindamiskriteerium"), h.url('test_new_hindamiskriteerium', test_id=c.test.id, hindamiskogum_id=c.item.id),
      title=_("Hindamiskriteerium"), level=2, size='lg')}
      % endif
      
        % if c.testiosa.vastvorm_kood in (const.VASTVORM_KP, const.VASTVORM_SP):
      ${h.btn_to(_("Lisa sisestuskogum"), h.url('test_new_sisestuskogum',
      test_id=c.test.id, testiosa_id=c.testiosa.id), level=2)}
        % endif
        % if c.testiosa.vastvorm_kood not in (const.VASTVORM_SH, const.VASTVORM_SP):
         ## suulises testiosas ei tohi luua rohkem kui 1 hindamiskogumi, sest muidu ei toimi hindamiste otsing
      ${h.btn_to(_("Lisa hindamiskogum"), h.url('test_new_hindamiskogum',
      test_id=c.test.id, testiosa_id=c.testiosa.id, sisestuskogum_id=c.sisestuskogum_id), level=2)}
        % endif
      % endif

  </div>
      % if c.hindamiskogum:
        % if c.is_edit:
        ${h.submit(out_form=True)}
        % else:
        ${h.btn_to(_("Muuda"), h.url('test_edit_hindamiskogum', test_id=c.test.id, id=c.item.id))}
        % endif
      % elif c.sisestuskogum:

        % if c.is_edit:
        ${h.submit(out_form=True)}
        % elif c.item.id:
        ${h.btn_to(_("Muuda"), h.url('test_edit_sisestuskogum', test_id=c.test.id,
          id=c.item.id))}
        % endif
      % endif
   % endif
</div>
