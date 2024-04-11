${h.pager(c.items)}
<%
   c.on_kursused = c.test.on_kursused
   c.aine_kood = c.test.aine_kood
%>
% if c.items:
<table width="100%" class="table table-borderless table-striped tablesorter" border="0" >
  <thead>
    <tr>
      % for sort, title in c.header:
      ${h.th(title)}
      % endfor
    </tr>
  </thead>
  <tbody>
    <% 
       prev_hk = None
       prev_k_id = None
    %>
    % for rcd in c.items:
    <%  
       k_nimi, k_id, hkogum_tahis, ty_id, kursus_kood, ty_tahis, a_seq, ty_seq, ty_max, h_count, h_min, h_max, h_avg, h_dev = rcd 
    %>
    % if not c.punktides:
    % if k_id != prev_k_id or hkogum_tahis != prev_hk:
    ${self.row_hk(k_id, hkogum_tahis, k_nimi)}
    % endif
    % endif

    <%
       prev_hk = hkogum_tahis
       prev_k_id = k_id

       t_avg = c.total[ty_id]
       if t_avg is not None and h_avg is not None:
         erinevus = h_avg - t_avg 
         protsent = t_avg > 0 and erinevus * 100 / t_avg or 0
       else:
         erinevus = None
         protsent = None
    %>
    <tr>
      <td>
        ${k_nimi}
      </td> 
      % if c.on_kursused:
      <td>${model.Klrida.get_str('KURSUS', kursus_kood, ylem_kood=c.aine_kood)}</td>
      % endif
      <td>${hkogum_tahis or '-'}</td>
      <td>
        ${ty_tahis}
      </td>
      <td>${h.fstr(ty_max)}</td>
      <td>${h_count}</td>
      <td>${h.fstr(h_max)}</td>
      <td>${h.fstr(h_min)}</td>
      <td>${h.fstr(h_avg)}</td>
      <td>${h.fstr(t_avg)}</td>
      <td>${h.fstr(erinevus)}</td>
      <td>${h.fstr(protsent)}%</td>
      <td>
        % if erinevus is not None:
        ${erinevus > 0 and 'leebe' or erinevus < 0 and 'range' or ''}
        % endif
      </td>
      <td>${h.fstr(h_dev)}</td>
    </tr>
    % endfor
  </tbody>
</table>
% endif

<%def name="row_hk(kasutaja_id, hkogum_tahis, k_nimi)">
## hindamiskogumi ja kasutaja kohta käiv rida
<% 
   rcd = c.items_hk.get((kasutaja_id, hkogum_tahis))
%>
% if rcd:
<%
   k_id, hk_tahis, max_pallid, kursus_kood, h_count, h_max, h_min, h_avg, h_dev = rcd

   t_avg = c.total_hk[hk_tahis]
   if t_avg is not None and h_avg is not None:
      erinevus = h_avg - t_avg 
      protsent = t_avg > 0 and erinevus * 100 / t_avg or 0
   else:
      erinevus = None
      protsent = None
%>
    <tr>
      <td>
        ${k_nimi}
      </td> 
      % if c.on_kursused:
      <td>${model.Klrida.get_str('KURSUS', kursus_kood, c.aine_kood)}</td>
      % endif
      <td>${hkogum_tahis or '-'}</td>
      <td></td>
      <td>${h.fstr(max_pallid)}</td>
      <td>${h_count}</td>
      <td>${h.fstr(h_min)}</td>
      <td>${h.fstr(h_max)}</td>
      <td>${h.fstr(h_avg)}</td>
      <td>${h.fstr(t_avg)}</td>
      <td>${h.fstr(erinevus)}</td>
      <td>${h.fstr(protsent)}%</td>
      <td>
        % if erinevus is not None:
        ${erinevus > 0 and 'leebe' or erinevus < 0 and 'range' or ''}
        % endif
      </td>
      <td>${h.fstr(h_dev)}</td>
    </tr>
% endif
</%def>
