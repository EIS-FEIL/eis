${h.pager(c.items)}
% if c.items:
<table width="100%" class="table table-borderless table-striped tablesorter mb-2" border="0" >
  <thead>
    <tr>
      % for h_sort, h_title in c.header:
      ${h.th(h_title)}
      % endfor
      <th sorter="false"></th>
      % if not c.on_loige:
      <th sorter="false"></th>
      % endif
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(c.items):
    <%
       row, d_url, r_url, h_url, d_groups = c.prepare_row(rcd)
    %>
    % if row:
    <tr>
      % for ind, value in enumerate(row):
      <td>
        % if ind == c.ind_col_test and h_url:
        ${h.link_to(value, h_url)}
        % else:
        ${value}
        % endif
      </td>
      % endfor
      <td>
        % if d_url:
        <%
           link_title = '<img src="/static/images/chart.png" alt="Diagramm" width="20px"/>'
           dlg_title = _("Tulemuste jaotus")
           if d_groups:
              dlg_title += ' - %s' % d_groups
        %>
        ${h.link_to_dlg(h.literal(link_title), d_url, title=dlg_title, width=900)}
        % endif
      </td>
      % if not c.on_loige:      
      <td>
        % if r_url:
        ${h.pdflink_to(r_url)}
        % endif
      </td>
      % endif
    </tr>
    % endif
    % endfor
  </tbody>
</table>
<div class="my-1">
% if c.warn_small_result:
${h.alert_notice(_("Statistikat ei kuvata, kui otsitavas grupis on vähem kui 5 sooritajat!"))}
% endif
% if c.warn_kool:
${h.alert_notice(_("Koolide kaupa statistikat ei kuvata."))}
% endif
% if c.warn_kov2:
${h.alert_notice(_("Statistikat ei kuvata selliste kohalike omavalitsuste kaupa, millest testil osales ainult üks kool."))}
% endif
</div>
% endif

% if c.rv_rows:
<table class="table table-borderless table-striped" border="0" >
  <caption>${_("Rahvusvahelise võõrkeeleeksami tunnistuse esitanud")}</caption>
  <thead>
    <tr>
      % for h_title in c.prepare_rv_header():
      ${h.th(h_title)}
      % endfor
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(c.rv_rows):
    <%
      row = c.prepare_rv_row(rcd)
    %>
    <tr>
      % for value in row:
      <td>${value}</td>
      % endfor
    </tr>
    % endfor
  </tbody>
</table>
% endif
