<span id="progress"></span>
<%include file="/common/message.mako"/>
% if c.items != '' and len(c.items) == 0:
<div style="padding:8px 0">${_("Otsingu tingimustele vastavaid ülesandeid ei ole")}</div>
% else:
${h.pager(c.items)}
<table width="100%" class="table table-borderless table-striped" border="0" >
  <tr>
    <th>${h.checkbox('all_id', 1, title=_("Vali kõik"))}</th>
    ${h.th_sort('id', u'ID')}
    ${h.th_sort('nimi', _("Nimetus"))}
    ${h.th_sort('max_pallid', _("Punktid"))}
  </tr>
  % for item in c.items:
  <tr>
    <td>
      ${h.checkbox('ylesanne_id', item.id, class_='otsiyl', title=_("Vali rida {s}").format(s=item.nimi))}
    </td>
    <td>${item.id}</td>
    <td>${h.link_to(item.nimi, h.url('ylesanded_sisu', id=item.id), target='_blank')}</td>
    <td>${h.fstr(item.get_max_pallid())}</td>
  </tr>
  % endfor
</table>
% endif
<br/>
<script>
$(function(){
  function toggle_add(){   
    $('span#add').toggle($('input.otsiyl:checked').length > 0);
  }
  $('input[name="all_id"]').click(function(){
     $('input.otsiyl').prop('checked', this.checked);
     toggle_add();
  });
  $('input.otsiyl').click(toggle_add);
});
</script>
% if c.items:
<span id="add" style="display:none">
  ${h.checkbox('on_jatk', label=_("Jätkuülesanne"))}
  ${h.submit(_("Lisa"))}
</span>
% endif
