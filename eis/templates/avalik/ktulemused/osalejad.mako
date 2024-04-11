<%inherit file="/common/formpage.mako"/>
<%namespace name="tab" file='/common/tab.mako'/>

<%def name="draw_tabs()">
<%include file="tabs.mako"/>
</%def>
<%def name="require()">
<%
  c.includes['subtabs'] = True
  c.includes['subtabs_label'] = True
%>
</%def>
<%def name="draw_subtabs()">
<% tab2 = c.klass_id %>
% if len(c.klassidID) > 1:
<%
  ALL = '.'
  if not tab2: tab2 = ALL
%>
${tab.draw(ALL, h.url_current('index', klass_id=ALL), _("Kõik osalejad"), tab2)}
% endif
% for klassID in c.klassidID:
<%
  klass_id = klassID.id
  if not tab2: tab2 = klass_id
%>
${tab.draw(klass_id, h.url_current('index', klass_id=klass_id), klassID.name or _("Klass puudub"), tab2)}
% endfor
</%def>
<%def name="subtabs_label()">
<% klassid_id = c.klass_id == ALL and c.klass_id or '' %>
${h.btn_to(_("Excel"), h.url_current('index', klass_id=c.klass_id, xls=1), level=2)}
${h.btn_to_dlg(_("Saada tulemused õpilasele"),
h.url('ktulemused_osalejad_saatmised', test_id=c.test.id, testimiskord_id=c.testimiskord.id, kursus=c.kursus, klassid_id=klassid_id),
title=_("Tulemuste saatmine õpilastele"), mdicls="mdi-email-send-outline", size='lg', level=2)}
</%def>

<%def name="page_title()">
${c.test.nimi or ''} | ${_("Osalejad")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Tsentraalsed testid"))}
${h.crumb(_('Tulemused'), h.url('ktulemused'))}
${h.crumb(c.test.nimi, h.url('ktulemused_osalejad', test_id=c.test.id, testimiskord_id=c.testimiskord.id, kursus=c.kursus))}
</%def>

<%def name="draw_before_tabs()">
<%include file="before.mako"/>
</%def>

<table class="table table-borderless table-striped tablesorter">
  <thead>
    <tr>
      % for sort_field, title in c.header:
        % if sort_field:
        ${h.th_sort(sort_field, title)}
        % else:
        ${h.th(title)}
        % endif
      % endfor
    </tr>
  </thead>
  <tbody>   
    % for n, rcd in enumerate(c.items):
    <% item, url = c.prepare_item(rcd, n) %>
    <tr>
      % for n2, s in enumerate(item):
      <td>
        % if n2 in (0,1) and url:
        ${h.link_to(s, url)}
        % else:
        ${s}
        % endif
      </td>
      % endfor
    </tr>
    % endfor
  </tbody>
</table>
