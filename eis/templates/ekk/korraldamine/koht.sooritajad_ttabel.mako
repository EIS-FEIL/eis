% if c.ttabel_data != '' and not c.ttabel_data:
${_("Sooritajaid ei ole")}
% elif c.ttabel_data:
<%
  header, rows = c.ttabel_data
  kpv = None 
%>
${h.hidden('upd_ttabel', 1)}
<table width="100%" class="table table-striped ttabel" border="0" >
  <thead>
    <tr>
      % for label in header:
      <th>${label}</th>
      % endfor
    </tr>
  </thead>
  <tbody>
    <% ind_tos = 0 %>
    % for row in rows:
    <%
      algus = row[0]
      ts = int(algus.timestamp())
      kpv = h.str_from_date(algus.date())
    %>
    <tr class="trtime">
      <td>
        <div style="min-height:40px">${h.str_time_from_datetime(algus)}</div>
      </td>
      % for testiruum_id, sooritused in row[1:]:
      <% cell_id = '%s_%s' % (ts, testiruum_id) %>
      <td class="sortable" data-cell="${cell_id}">
        % for sdata in sooritused:
        <div class="d-flex align-items-center mb-1 draggable border" id="ds${sdata.sooritus_id}">
          <div class="card-body p-0">
            <div class="d-flex align-items-center">
              <i class="mdi mdi-drag-vertical mdi-24px gray-300" aria-hidden="true"></i>
              <p class="card-text my-0 ml-1">
                ${sdata.tahised}
                ${sdata.nimi}
                % if sdata.kavaaeg != algus:
                (${h.str_time_from_datetime(sdata.kavaaeg)})
                % endif
                ${h.hidden('s-%d.sooritus_id' % ind_tos, sdata.sooritus_id)}
                ${h.hidden('s-%d.cell_id' % ind_tos, cell_id, class_="cell_id")}
                ${h.hidden('s-%d.moved' % ind_tos, '', class_="moved")}
                <% ind_tos += 1 %>
                ${h.button('', class_="timepicker", mdicls='mdi-watch-export', level=2)}
            </div>
          </div>
        </div>
        % endfor
      </td>
      % endfor
    </tr>
    % endfor
  </tbody>
</table>
<div class="muud-paevad" style="display:none">
</div>
<script>
function update_cnt(cell_id, add)
{
var option = $('.timepicker-dlg .pick-kell option[value="' + cell_id + '"]');
  var cnt = parseInt(option.attr('data-cnt'));
  cnt = (add ? cnt + 1 : cnt - 1);
  option.attr('data-cnt', String(cnt));
}
function move_to(draggable, cell_id)
{
  ## vana aeg
  var old_cell_id = draggable.find('input.cell_id').val();
  update_cnt(old_cell_id, false);

  ## jätame meelde uue aja ja ruumi
  draggable.find('input.cell_id').val(cell_id);

  draggable.find('input.moved').val('1');
  update_cnt(cell_id, true);
  dirty = true;
}
function can_drop(draggable, cell){
  if(!cell.is('.sortable'))
     cell = cell.closest('.sortable');
  return cell;
}
function on_drop(draggable, cell)
{
   move_to(draggable, cell.attr('data-cell'));
   cell.append(draggable);
}
$(function(){
   var current_draggable = null;
   ## sooritajate lohistamine
   DragDropEngine($('.ttabel'), 
                  $('.ttabel .draggable'),
                  $('.ttabel .sortable'),
                  {can_drop: can_drop, on_drop: on_drop});

   $('.ttabel .timepicker').click(function(){
      ## avatakse aken, kus saab valida kuupäeva ja kellaaja
      current_draggable = $(this).closest('.draggable');
      var paev = "${h.str_from_date(kpv)}";
      $('.timepicker-dlg select.pick-kpv').val(paev).change();
      $('.timepicker-dlg select.pick-kell').val('');
      open_dialog({'contents_elem': $('.timepicker-dlg'), 'title': "${_("Vali aeg")}"});
      return false; 
   });
   $('.timepicker-dlg select.pick-kpv').change(function(){
      var paev = $(this).val();
      $('.timepicker-dlg select.pick-kell option')
          .hide()
          .filter(function(){
             return ($(this).attr('data-paev') == paev) && 
                    ($(this).attr('data-cnt') == '0');
           })
          .show();
   });
   $('.timepicker-dlg #suuna').click(function(){
       var paev = $('.timepicker-dlg .pick-kpv').val();
       var cell_id = $('.timepicker-dlg .pick-kell').val();
       if(paev == '' || cell_id == '')
            return;
       var cell, ruum;
       var cell = $('td.sortable').filter(function(){
           return $(this).attr('data-cell') == cell_id;
       });
       if(cell.length == 0)
       {
           ## suunati teisele päevale
           cell = $('.muud-paevad');
       }
       move_to(current_draggable, cell_id);
       cell.append(current_draggable);
       current_draggable = null;
       close_dialog();
   });
});
</script>
<div style="display:none" class="timepicker-dlg" id="timepickerdlg">
  <table class="table">
   <col width="120"/>
   <col width="120"/>
    <tr>
      <td class="frh">${_("Kuupäev")}</td>
      <td>${h.select('kpv', '', c.opt_paev, class_="pick-kpv")}</td>
    </tr>
    <tr>
      <td class="frh">${_("Vabad ajad")}</td>
      <td>
        <select name="kell" class="pick-kell">
          <option value=""></option>
          % for ts, s_kell, cnt, s_paev in c.opt_kell:
          <option value="${ts}" data-paev="${s_paev}" data-cnt="${cnt}" style="display:none">${s_kell}</option>
          % endfor
        </select>
      </td>
    </tr>
  </table>
  ${h.button(_("Suuna"), id="suuna")}
</div>
% endif
<br/>

