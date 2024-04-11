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
      ${h.th_sort('testimiskord.tutv_taotlus_alates', _("Taotlemise algus"))}
      ${h.th_sort('testimiskord.tutv_taotlus_kuni', _("Taotlemise lõpp"))}
      ${h.th_sort('testimiskord.tutv_hindamisjuhend_url', _("Hindamisjuhend"))}
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(c.items):
    <%
       test = rcd.test
    %>
    <tr>
      <td>
        ${h.checkbox('kord_id', rcd.id, onclick='toggle_add()', 
        checked=rcd.id in korrad_id, class_='nosave')}
      </td>
      <td>${test.nimi}</td>
      <td>${test.id}-${rcd.tahis}</td>
      <td>${h.str_from_date(rcd.tutv_taotlus_alates)}</td>
      <td>
        % if rcd.tutv_taotlus_kuni:
        ${h.str_from_date(rcd.tutv_taotlus_kuni)}
        % elif rcd.tutv_taotlus_alates:
        <i>${_("alatine")}</i>
        % endif
      </td>
      <td>
        % if rcd.tutv_hindamisjuhend_url:
        ${h.link_to(rcd.tutv_hindamisjuhend_url, rcd.tutv_hindamisjuhend_url)}
        % endif
      </td>
    </tr>
    % endfor
  </tbody>
</table>
% endif
      
<script>
  function toggle_add()
  {
         var visible = ($('input:checked[name="kord_id"]').length > 0);
         if(visible)
         { 
           $('span.add.invisible').removeClass('invisible');
         }
         else
         {
           $('span.add').filter(':not(.invisible)').addClass('invisible');
         }
  }
  $(document).ready(function(){
     toggle_add();
  });
</script>
