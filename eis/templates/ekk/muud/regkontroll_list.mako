% if c.items != '':
${h.pager(c.items, msg_not_found=_("Õpilasi ei leitud"), msg_found_one=_("Leiti 1 õpilane"), msg_found_many=_("Leiti {n} õpilast"))}
% endif
% if c.items:
<table width="100%" class="table table-borderless table-striped" border="0" >
  <thead>
    <tr>
      % for srt, title in c.prepare_header():
      % if srt:
      ${h.th_sort(srt, title)}
      % else:
      ${h.th(title)}
      % endif
      % endfor
    </tr>
  </thead>
  <tbody>
    % for item in c.items:
    <tr>
      % for value in c.prepare_item(item, 0):
      <td>${value}</td>
      % endfor
    </tr>
    % endfor
  </tbody>
</table>
% endif
