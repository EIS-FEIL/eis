  <%
     td_style = 'background-color:#f6f2da;'
     top_style = (c.sugu or c.lang) and 'border-top: 2px solid #f7a047;' or ''
  %>

  % for title, k_class, k_url, rows in c.items2:
    % for n, (row, d_url, d_title) in enumerate(rows):
    <tr>
      % if n == 0:
      <td rowspan="${len(rows)}" style="${td_style}${top_style}">
        ${title}
      </td>
      % endif
      % for value in row:
      <td style="${td_style}${n==0 and top_style or ''}">${value}</td>
      % endfor
    </tr>
    % endfor
  % endfor
