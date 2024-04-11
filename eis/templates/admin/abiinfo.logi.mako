% if c.items:
<table width="100%" class="table table-borderless table-striped" border="0" >
  <tbody>
    % for n, rcd in enumerate(c.items):
    <tr>
      <td>${h.str_from_datetime(rcd[0])}</td>
      <td>${rcd[2] or rcd[1]}</td>
      <td>${rcd[3]}</td>
    </tr>
    % endfor
  </tbody>
</table>
% endif
