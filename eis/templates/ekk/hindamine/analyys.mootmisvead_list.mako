${h.pager(c.items)}
% if c.items:

<table width="100%" class="table table-borderless table-striped" border="0" >
  <thead>
    <tr>
      % for (fieldname, descr) in c.headers:
      ${h.th_sort(fieldname, descr)}
      % endfor
    </tr>
  </thead>
  <tbody>
    % for rcd in c.items:
    <tr>
    <% n=1 %>
    % while n < len(rcd):
    <% 
       r = rcd[n] 
       n += 1
    %>
    % if n not in c.staatus_jrk:
    <td>
      % if isinstance(r, float):
      ${h.fstr(r)}p (${h.fstr(rcd[n])}%)
      <% n += 1 %>
      % else:
      ${r}
      % endif
    </td>
    % elif r != const.S_STAATUS_TEHTUD:
    <% 
       ignore = c.staatus_jrk[n] 
       colspan = (ignore - len([k for k in range(n+1, n+ignore+1) if k in c.staatus_jrk]))/2
       n += ignore
    %>
    <td colspan="${colspan}">${c.opt.S_STAATUS.get(r)}</td>
    % endif
    % endwhile
    </tr>
    % endfor
  </tbody>
</table>
% endif
