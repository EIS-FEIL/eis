<%inherit file="/common/formpage.mako"/>
<%def name="draw_tabs()">
<% c.tab1 = 'avtulemused' %>
<%include file="tabs.mako"/>
</%def>
<%def name="require()">
<%
c.includes['subtabs'] = True
c.includes['subtabs_label'] = True
%>
</%def>
<%def name="page_title()">
${c.test.nimi or ''} | ${_("Tulemused")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_('Töölaud'), h.url('tookogumikud'))}
${h.crumb(c.test.nimi or  _('Test'), h.url('testid_yldandmed', id=c.test_id, testiruum_id=c.testiruum_id))} 
${h.crumb( _('Tulemused'), h.url('test_avtulemused', test_id=c.test_id, testiruum_id=c.testiruum_id))}
${h.crumb( _('Tulemused ülesannete kaupa'), h.url('test_avylesanded', test_id=c.test_id, testiruum_id=c.testiruum_id))}
</%def>

<%def name="draw_subtabs()">
<% c.tab2 = 'avylesanded' %>
<%include file="avtulemused.tabs.mako"/>
</%def>

<%def name="subtabs_label()">
<% c.testiosavalik_action = h.url_current('index') %>
  <%include file="testiosavalik.mako"/>
</%def>

% if len(c.sooritused) == 0:
${h.alert_notice(_("Sooritajaid pole lisatud"), False)}
% else:
<table class="table table-striped tablesorter hidden" width="100%" >
  <thead>
    <tr>
      % for ty_seq, h_title in c.header:
      % if ty_seq is not None:
      <th class="tdy" data-seq="${ty_seq}">${h_title}</th>      
      % else:
      ${h.th(h_title)}
      % endif
      % endfor
    </tr>
  </thead>
  <tbody>
  % for n, rcd in enumerate(c.sooritused):
      <%
        row, html_extra = c.prepare_item(rcd, n, is_html=True)
        tos, eesnimi, perenimi, ik = rcd
        nimi = '%s %s' % (eesnimi, perenimi)
      %>
  <tr>
    % for ind, value in enumerate(row):
    <%
      try:
         ty_seq, ty_id = html_extra[ind]
      except:
         ty_seq = ty_id = None
    %>
    % if ty_seq is None:
    <td>
      % if ind == 0:
        <!--${perenimi},${eesnimi}-->
        % if c.test.on_jagatudtoo and tos.staatus > const.S_STAATUS_ALUSTAMATA:
        ${h.link_to_dlg(value, h.url('test_tootulemus', id=tos.sooritaja_id, test_id=c.test.id, testiruum_id=c.testiruum_id), title=nimi, size='lg', width=800)}        
        % elif not c.test.on_jagatudtoo and tos.staatus == const.S_STAATUS_TEHTUD:
        ${h.link_to(value, h.url('test_labiviimine_sooritusaknas', test_id=c.test_id, testiruum_id=c.testiruum_id, id=tos.id), class_="fblink")}
        % else:
        ${value}
        % endif
      % else:
         ${value}
      % endif
    </td>
    % else:
    ## ty veerg
    <td class="tdy" data-seq="${ty_seq}">
      % if ty_id:
        ${h.link_to_dlg(value, h.url('test_tootulemus', sub='ty', id=tos.sooritaja_id, test_id=c.test.id, testiruum_id=c.testiruum_id, ty_id=ty_id),
        title=_("Tagasiside"), size='lg')}
      % else:
        ${value}
      % endif
    </td>
    % endif
    % endfor
  </tr>
  % endfor
  </tbody>
</table>

<%include file="avtulemused.ylesanded.paginator.mako"/>
% endif
${h.btn_to(_("CSV"), h.url_current('index', csv=1))}
