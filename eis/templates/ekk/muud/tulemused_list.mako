% if c.items != '':
${h.pager(c.items)}
% endif
% if c.items:
<%
   if c.kord_id and isinstance(c.kord_id, list):
      korrad_id = map(int, c.kord_id)
   elif c.kord_id:
      korrad_id = [int(c.kord_id)]
   else:
      korrad_id = []
%>
<table width="100%" class="table table-borderless table-striped" border="0" >
  <thead>
    <tr>
      <th></th>
      ${h.th_sort('test.nimi', _("Test"))}
      ${h.th_sort('test.id testimiskord.tahis', _("Testimiskord"))}
      ${h.th_sort('testimiskord.tulemus_kinnitatud', _("Tulemused kinnitatud"))}
      ${h.th_sort('testimiskord.koondtulemus_avaldet', _("Koondtulemused avaldatud"))}
      ${h.th_sort('testimiskord.alatestitulemused_avaldet', _("Alatestide lõikes tulemused avaldatud"))}      
      ${h.th_sort('testimiskord.ylesandetulemused_avaldet', _("Ülesannete lõikes tulemused avaldatud"))}
      ${h.th_sort('testimiskord.aspektitulemused_avaldet', _("Aspektide lõikes tulemused avaldatud"))}
      ${h.th_sort('testimiskord.ylesanded_avaldet', _("Ülesanded ja vastused avaldatud"))}
      ${h.th(_("E-posti teel teavitatavate arv"))}
      ${h.th(_("Vaiete olemasolu"))}
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(c.items):
    <%
       cnt_epost, on_vaided = c.get_count(rcd)
       test = rcd.test
    %>
    <tr>
      <td>
        ${h.checkbox('kord_id', rcd.id, onclick='toggle_add()', 
        checked=rcd.id in korrad_id, class_='kord_id nosave')}
      </td>
      <td>${test.nimi}</td>
      <td>${test.id}-${rcd.tahis}</td>
      <td>${h.sbool(rcd.tulemus_kinnitatud)}</td>
      <td>${self.sboold(rcd.koondtulemus_avaldet, rcd.koondtulemus_aval_kpv)}</td>
      <td>${self.sboold(rcd.alatestitulemused_avaldet, rcd.alatestitulemused_aval_kpv)}</td>
      <td>${self.sboold(rcd.ylesandetulemused_avaldet, rcd.ylesandetulemused_aval_kpv)}</td>
      <td>${self.sboold(rcd.aspektitulemused_avaldet, rcd.aspektitulemused_aval_kpv)}</td>
      <td>${self.sboold(rcd.ylesanded_avaldet, rcd.ylesanded_aval_kpv)}</td>
      <td>${cnt_epost}</td>
      <td>${h.sbool(on_vaided)}</td>
    </tr>
    % endfor
  </tbody>
</table>

% endif

<%def name="sboold(b, d)">
% if b and d:
${h.str_from_date(d)}
% else:
${h.sbool(b)}
% endif
</%def>
      
<script>
  function toggle_add()
  {
    var visible = ($('input:checked.kord_id').length > 0);
    $('#add').toggleClass('d-none', !visible);
  }
  $(document).ready(function(){
     toggle_add();
  });
</script>
