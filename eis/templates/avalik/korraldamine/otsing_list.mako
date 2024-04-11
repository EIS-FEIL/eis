${h.pager(c.items)}
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
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(c.items):
    <% 
      testikoht = rcd[0]
      row = c.prepare_item(rcd, n)
      url_edit = h.url('korraldamine_sooritajad', testikoht_id=testikoht.id)
      testiosa = rcd[3]
      on_h_tab = testiosa.vastvorm_kood in (const.VASTVORM_KE, const.VASTVORM_SE, const.VASTVORM_KP, const.VASTVORM_I)
    %>
    <tr>
      % for ind, value in enumerate(row):
      <td>
        % if ind == 0:
        ${h.link_to(value, url_edit)}
        % elif 5 <= ind <= 7:
          % if value:
          ${h.mdi_icon('mdi-check', style="color:#00b140", title=_("Määratud"))}
          % elif value == False:
          <%
             if ind == 5:
                url_prob = url_edit
             elif ind == 6 or (ind == 7 and not on_h_tab):
                url_prob = h.url('korraldamine_labiviijad', testikoht_id=testikoht.id)
             elif ind == 7:
                url_prob = h.url('korraldamine_hindajad', testikoht_id=testikoht.id)            
          %>
          <a href="${url_prob}">
            ${h.mdi_icon('mdi-alert', style="color:#fb786e", title=_("Määramata"))}
          </a>
          % else:
               -
          % endif
        % else:
        ${value}
        % endif
      </td>
      % endfor
    </tr>
    % endfor
  </tbody>
</table>
% endif
