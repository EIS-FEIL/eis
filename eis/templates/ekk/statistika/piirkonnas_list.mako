% if c.items1:
<table width="100%" class="table table-borderless table-striped" border="0" >
  <thead>
    <tr>
      % for value in c.header:
      ${h.th(value)}
      % endfor
    </tr>
  </thead>

  <%
     #td_style = 'background-color:#e6ddc5;'
     td_style = ''
     top_style = (c.sugu or c.lang) and 'border-top: 2px solid #f7a047;' or ''
     prk_n = 0
  %>
  
  % for title, k_class, k_url, rows in c.items1:
  <tbody>
    <% prk_n += 1 %>
    % for n, (row, d_url, d_title) in enumerate(rows):
    <tr>
      % if n == 0:
      <td rowspan="${len(rows)}" style="${td_style}${top_style}">
        % if k_url:
        <a class="menu1" href="#" onclick="open_koolid(${prk_n});return false;">
          ${title}
        </a>
        % else:
        ${title}
        % endif
        <span class="helpable" id="piirkond"></span>                
      </td>
      % endif
      % for value in row:
      <td style="${td_style}${n==0 and top_style or ''}">${value}</td>
      % endfor
    </tr>
    % endfor
  </tbody>
  % if k_url:
  <tbody class="koolid-${prk_n}" style="display:none;" data-src="${k_url}">
  </tbody>
  % endif
  % endfor
 
</table>
% endif
<p/>

<script>
  function open_koolid(prk_n)
  {
     var container = $('tbody.koolid-'+prk_n);
     var p_url = container.data('src');
     if(p_url)
     {
        dialog_load(p_url, '', 'get', container);
        container.data('src', '');
        container.show();
     }
     else
     {
        container.toggle();
     }
  }
</script>
