<%inherit file="/common/formpage.mako"/>
<%def name="draw_tabs()">
<%include file="tabs.mako"/>
</%def>

<%def name="page_title()">
${_("Test")}: ${c.test.nimi or ''} | ${_("Eeltestimine")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Testid"), h.url('testid'))} 
${h.crumb(c.test.nimi or _("Test"))} 
${h.crumb(_("Eeltestimine"))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'testid' %>
</%def>

<div class="form container">
  <div class="row">
    <div class="col-sm-4 col-md-3">
      ${self.eeltestid_list()}
    </div>
    <div class="col-sm-8 col-md-9" style="background:#fff">
      % if c.item:
      <%include file="eeltest.mako"/>
      % endif
    </div>
  </div>
</div>

<%def name="eeltestid_list()">
<%
  c.can_update = c.user.has_permission('ekk-testid', const.BT_UPDATE, c.test)
  mitu_testiosa = len(c.test.testiosad) > 1
  eeltestid = list(c.test.eeltestid)
%>
% if eeltestid:
<table width="100%" class="table singleselect" >
        <thead>
          <tr>
            ${h.th(_("Eeltest"))}
            ${h.th(_("Ülesandekomplektid"))}
          </tr>
        </thead>
        <tbody>
          % for eeltest in eeltestid:
          <%
            avalik_test = eeltest.avalik_test
          %>
          <tr ${c.item==eeltest and 'class="selected"' or ''}>
            <td>
              <%
                title = '%s %d' % (_("Test"), eeltest.avalik_test_id)
                if avalik_test:
                   url = h.url('test_edit_eeltest', test_id=c.test.id, id=eeltest.id)
                else:
                   title += ' (%s)' % _("kustutatud")
                   url = h.url('test_eeltest', test_id=c.test.id, id=eeltest.id)
              %>
              ${h.link_to(title, url)}
            </td>
            <td>
              <%
               osak = {}
               for k in eeltest.komplektid:
                  kv = k.komplektivalik
                  osa_id = kv.testiosa_id
                  tahis = k.tahis
                  s_alatestid = kv.str_alatestid
                  if s_alatestid:
                     tahis += ' (%s %s)' % (_("alatest"), s_alatestid)
                  osak[osa_id] = (osak.get(osa_id) or []) + [tahis]
              %>
              % for osa_id, li_k in osak.items():
              % if mitu_testiosa:
              ${model.Testiosa.get(osa_id).tahis}:
              % endif
              ${'<br/>'.join(li_k)}
              % endfor
            </td>
          </tr>
          % endfor
        </tbody>
</table>
% endif
% if c.can_update:
${h.btn_to(_("Loo uus eeltest"),
h.url('test_new_eeltest', test_id=c.test.id))}
% endif
</%def>
