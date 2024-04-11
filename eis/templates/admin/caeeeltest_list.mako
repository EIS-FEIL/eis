% if c.items != '':
${h.pager(c.items, msg_not_found=_("Otsingu tingimustele vastavaid isikuid ei leitud"))}
% endif
% if c.items:
<table width="100%" class="table table-borderless table-striped" border="0" >
  <tr>
    % for key, label in c.prepare_header():
    % if key:
    ${h.th_sort(key, label)}
    % else:
    ${h.th(label)}
    % endif
    % endfor
  </tr>
  % for n, rcd in enumerate(c.items):
  <tr>
    % for val in c.prepare_item(rcd, n):
    <td>${val}</td>
    % endfor
  </tr>
  % endfor  
</table>
% endif

