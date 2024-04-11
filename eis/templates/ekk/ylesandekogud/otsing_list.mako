% if c.items != '':
${h.pager(c.items,msg_not_found=_("Otsingu tingimustele vastavaid e-kogusid ei leitud"),
          msg_found_one=_("Leiti üks tingimustele vastav e-kogu"),
          msg_found_many=_("Leiti {n} tingimustele vastavat e-kogu"))}
% endif
% if c.items:
<table width="100%" class="table table-borderless table-striped" border="0" >
  <tr>
    % for h_sort, h_title in c.header:
    % if h_sort:
    ${h.th_sort(h_sort, h_title)}
    % else:
    ${h.th(h_title)}
    % endif
    % endfor
  </tr>
  % for n, rcd in enumerate(c.items):
      <%
        row = c.prepare_item(rcd, n)
        kogu = rcd[0]
        can_update = c.user.has_permission('ylesandekogud', const.BT_UPDATE, kogu)
        can_show = can_update or c.user.has_permission('ylesandekogud',const.BT_SHOW, kogu)
        rcd_url = can_update and h.url('edit_ylesandekogu', id=kogu.id) or \
              can_show and h.url('ylesandekogu', id=kogu.id) or None
      %>
  <tr>
    % for ind, value in enumerate(row):
    <td>
       % if ind < 3 and rcd_url:
         ${h.link_to(value, rcd_url)}
       % else:
         ${value}
       % endif
    </td>
    % endfor
  </tr>
  % endfor  
</table>
% endif
