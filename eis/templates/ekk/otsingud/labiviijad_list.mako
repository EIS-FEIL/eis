% if c.items != '':
${h.pager(c.items, is_psize_all=True)}
% endif
% if c.items:
<table width="100%" class="table table-borderless table-striped" border="0" >
  <caption>${c.rep_title}</caption>
  <thead>
    <% header, items = c.prepare_items(c.items) %>
    <tr>
      <th>${h.checkbox('valikoik', 1)}</th>
      % for sort_field, title in header:
        % if sort_field:
        ${h.th_sort(sort_field, title)}
        % else:
        ${h.th(title)}
        % endif
      % endfor
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(items):
    <tr>
      <td>${h.checkbox('lv_id', rcd[0], checkedif=c.lv_id, class_="lv_id")}</td>
      % for s in rcd[1:]:
      <td>${s}</td>
      % endfor
    </tr>
    % endfor
  </tbody>
</table>
% endif

<script>
var toggle_nupud = function(){
  $('div[id="nupud"]').toggle($('input.lv_id:checked').length>0);
}
$(function(){
  toggle_nupud();
  $('input[name="valikoik"]').click(function(){
     $('input.lv_id').prop('checked', $(this).prop('checked'));
     toggle_nupud();
  });
  $('input.lv_id').click(function(){
     $('input[name="valikoik"]').prop('checked', false);
     toggle_nupud();
  });
});
</script>
