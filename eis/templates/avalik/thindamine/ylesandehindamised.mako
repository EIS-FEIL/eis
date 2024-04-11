<%inherit file="/common/formpage.mako"/>
<%def name="draw_tabs()">
<% c.tab1 = 'hindamised' %>
<%include file="/avalik/testid/tabs.mako"/>
</%def>
<%def name="require()">
<%
  c.includes['subtabs'] = True
  c.includes['test'] = True
%>
</%def>
<%def name="draw_subtabs()">
<% c.tab2 = 'ylesandehindamised' %>
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

% if c.items:
${self.ylesanded_tbl()}
% else:
${h.alert_notice(_("Hinnatavaid ülesandeid ei ole"), False)}
% endif

<%def name="ylesanded_tbl()">
<table class="table table-striped tablesorter" width="100%" >
  <caption>${_("Ülesanded")}</caption>
  <thead>
    <tr>
      % for sort_field, title in c.header:
        ${h.th_sort(sort_field, title)}
      % endfor
    </tr>
  </thead>
  <tbody>
    % for rcd in c.items:
    <% 
      item, on_pooleli, vy_id, y_url = c.prepare_item(rcd, True)
      url_edit = h.url('test_ylesanne_hindamised', test_id=c.test_id, testiruum_id=c.testiruum_id, vy_id=vy_id)
    %>
    <tr>
      % for ind, v in enumerate(item):
      <td>
        % if ind == 2:
        ${h.btn_to_dlg(_("Vaata"), y_url, level=2, size='lg', title=_("Ülesanne"))}
        % else:
        ${v}
        % endif
      </td>
      % endfor
      <td>
        % if not c.test.opetajale_peidus:
        % if on_pooleli:
        ${h.btn_to(_("Jätka hindamist"), url_edit)}
        % elif on_pooleli == False:
        ${h.btn_to(_("Alusta hindamist"), url_edit)}
        % endif
        % endif
      </td>
    </tr>
    % endfor
  </tbody>
</table>
</%def>
