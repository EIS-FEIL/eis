% if c.items != '':
${h.pager(c.items)}
% endif
% if c.items:
<table width="100%" class="table table-borderless table-striped" border="0" >
  <thead>
    <tr>
      % for h_sort, h_title in c.header:
      % if h_sort:
      ${h.th_sort(h_sort, h_title)}
      % else:
      ${h.th(h_title)}
      % endif
      % endfor
      ${h.th(_("Fail"))}
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(c.items):
      <%
        prot = rcd[0]
        row = c.prepare_item(rcd, n)
      %>
    <tr>
      % for ind, value in enumerate(row):
      <td>
        % if ind==3:
        ${h.link_to(value, h.url('sisestamine_protokoll_osalejad', toimumisprotokoll_id=prot.id))}
        % else:
         ${value}
        % endif
      </td>
      % endfor
      <td>
        % if prot.has_file:
        <%
          fileext = prot.fileext
          url = h.url_current('download', format=fileext, id=prot.id)
        %>
          % if fileext in (const.BDOC, const.DDOC, const.ASICE):
        <a href="${url}"> <img src="/static/images/bdoc.png" alt="BDOC" border="0"/></a>
          % else:
        ${h.pdflink_to(url)}
          % endif
        % endif
      </td>
    </tr>
    % endfor
  </tbody>
</table>
% endif
