<div container_sel="div.grupid-list">
<% grupid = list(c.testiosa.ylesandegrupid) %>
% if grupid:
<table class="table select-ok singleselect" style="max-width:680px">
  <col/>
  <col width="20px"/>
  <col width="80px"/>
  <thead>
    <tr>
      <th>${_("Ülesandegrupi nimetus")}</th>
      <th>${_("Ülesanded")}</th>
      % if c.can_np:
      <th></th>
      % endif
    </tr>
  </thead>
  <tbody>
  % for grupp in grupid:
    <%
      vyy_id = [str(r.valitudylesanne_id) for r in grupp.grupiylesanded]
    %>
  <tr class="notselected">
  <td><!--yg ${grupp.id}-->
    ${h.checkbox('curr', 1, class_="selectrow curr-grp nosave", style="display:none", id="curr_%s" % grupp.id)}
    ${grupp.nimi}
    ${h.hidden('vyy_id', ','.join(vyy_id), id="vyy_id_%s" % grupp.id)}
  </td>
  <td class="len_grp">
      ${len(vyy_id)}
  </td>
  % if c.can_np:
  <td>
    <%
      upd_url = h.url('test_testiosa_update_ylesandegrupp', test_id=c.test.id, testiosa_id=c.testiosa.id, id=grupp.id)
      del_url = h.url('test_testiosa_delete_ylesandegrupp', test_id=c.test.id, testiosa_id=c.testiosa.id, id=grupp.id)
    %>
    <i class="mdi mdi-check-circle mdi-24px save_grp_cmd d-none" title="${_("Salvesta")}" href="${upd_url}"></i>
    <i class="mdi mdi-delete-forever mdi-24px del_grp_cmd" title="${_("Kustuta")}" href="${del_url}"></i>
  </td>
  % endif
</tr>
  % endfor
  </tbody>
</table>
% endif

<script>
function select_row(tr, is_selected, event, nochange){
    if(event)
    {
        var trg = $(event.target);
        if(trg.is('a') || trg.is('input:not(.selectrow)'))
            return;
    }
    tr.toggleClass('notselected', !is_selected)
        .toggleClass('selected', is_selected);
    if (!event || event.target.type !== 'checkbox') {
        var cb = $('.selectrow', tr).prop('checked', is_selected);
        if(!nochange) cb.trigger('change');
    }
}

$(function(){
## algselt eemaldame ylesannete valiku (nt peale uue grupi lisamist)
select_row($('table.multipleselect tr.selected'), false, null, true);

## kui valitakse grupp, siis näidatakse grupi ylesanded
$('input.curr-grp.selectrow').change(function(){
   if(this.checked){
     var buf = $(this).closest('tr').find('input[name="vyy_id"]').val();
     var vyy_id = buf.split(',');
     var rows = $('tr.tr-ty');
     var selecting = rows.filter(function(){
         var value = $(this).find('input[name="vy_id"]').val();
         return (vyy_id.indexOf(value) > -1);
     });
     select_row(rows.not(selecting), false, null, true);
     select_row(selecting, true, null, true);
   }
  });
% if c.can_np:  
## kõigi ylesannete korraga valimine/valiku eemaldamine
  $('input[name="vy_all_id"]').click(function(){
    var rows = $(this).closest('table').find('tbody>tr.tr-ty:not(.notselectable)');
    select_row(rows, this.checked, null, false);
  });

  ## muutmise lõpetamisel eemaldatakse realt valik
  $('.save_grp_cmd').click(function(){
    var href = $(this).attr('href');
    var td = $(this).closest('tr');
    var data = 'vyy_id='+td.find('input[name="vyy_id"]').val();
    dialog_load(href, data, 'POST', $('div.grupid-list'));
    dirty = false;
    return false;
  });
  ## grupi kustutamine
  $('.del_grp_cmd').click(function(){
    var href = $(this).attr('href');
    confirm_dialog(eis_textjs.confirm_delete,
       function(){
        dialog_load(href, '', 'POST', $('div.grupid-list'));
        close_confirm_dialog();
       });
    return false;
  });
% endif
});
</script>
</div>
