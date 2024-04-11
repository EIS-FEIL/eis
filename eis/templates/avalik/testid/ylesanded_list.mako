<span id="progress"></span>
% if c.items != '' and len(c.items) == 0:
 ${_("Otsingu tingimustele vastavaid ülesandeid ei ole")}
% else:
${h.pager(c.items)}
<table width="100%" class="table table-borderless table-striped" border="0" >
  <tr>
    <th></th>
    ${h.th_sort('id', 'ID')}
    ${h.th_sort('nimi', _('Nimetus'))}
    ${h.th_sort('max_pallid', _('Pallid'))}
    ${h.th_sort('arvutihinnatav', _('Arvutiga hinnatav'))}
  </tr>
  % for item in c.items:
  <tr>
    <td>
      ${h.checkbox('ylesanne_id', item.id, onclick="toggle_add()", class_="ylesanne_id")} 
    </td>
    <td>${item.id}</td>
    <td>${h.link_to(item.nimi, h.url('lahendamine1', id=item.id), target='_blank')}</td>
    <td>${h.fstr(item.get_max_pallid())}</td>
    <td>${h.sbool(item.arvutihinnatav)}</td>
  </tr>
  % endfor
</table>
% endif
<br/>
<script>
  function toggle_add(){   
         var visible = ($('input:checked.ylesanne_id').length > 0);
         if(visible)
         { 
           $('span#add.invisible').removeClass('invisible');
         }
         else
         {
           $('span#add').filter(':not(.invisible)').addClass('invisible');
         }
  }
</script>
% if c.items:
${h.button(_('Vali kõik'), onclick="$('input.ylesanne_id').prop('checked', true);toggle_add();")}
${h.button(_('Tühista valik'), onclick="$('input.ylesanne_id').prop('checked', false);toggle_add();")}
<span id="add" class="invisible">
${h.submit(_('Salvesta'))}
</span>
% endif
