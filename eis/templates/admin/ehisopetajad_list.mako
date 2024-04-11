% if c.items != '':
${h.pager(c.items,
          msg_not_found=_("Ei leitud ühtki õpetajat"),
          msg_found_one=_("Leiti üks õpetaja"),
          msg_found_many=_("Leiti {n} õpetajat"))}
% endif
% if c.items:
<table width="100%" class="table table-borderless table-striped" border="0" >
  <thead>
    <tr>
      % for item in c.prepare_header():
      ${h.th_sort(item[0], item[1])}      
      % endfor
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(c.items):
    <tr>
      % for s in rcd:
      <td>${s}</td>
      % endfor
    </tr>
    % endfor
  </tbody>
</table>
<br/>
% endif
