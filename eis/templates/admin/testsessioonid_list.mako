% if c.items != '':
${h.pager(c.items)}
% endif
% if c.items:
      
      <table width="100%" class="table table-borderless table-striped singleselect" >
        % for rcd in c.items:
          % if c.item and rcd.id == c.item.id:
        <tr class="selected">
          % else:
        <tr>
          % endif
          <td>
            ${h.link_to(rcd.nimi, h.url('admin_testsessioon', id=rcd.id))}
          </td>
          <td>${rcd.oppeaasta}</td>
          <td>${rcd.testiliik_nimi}</td>
        </tr>
        % endfor
      </table>

% endif
