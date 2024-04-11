## etteantud: testiylesannete arv c.cnt_testiylesanded
<% YCNT = 12 %>
% if c.cnt_testiylesanded <= YCNT:
<script>
$(function(){
  $('table.list.hidden').removeClass('hidden');
});
</script>
% else:
<nav aria-label="Paginaator" class="nav-tdy">
<script>
var current_min_seq = 1;
function show_tdy(min_seq){
  if(min_seq < 1 || min_seq > ${c.cnt_testiylesanded})
    return;
  var cols = $('.tdy');
  var shown = cols.filter(function(){
    var seq = parseInt($(this).attr('data-seq'));
    return (seq >= min_seq && seq < min_seq + ${YCNT});
  });
  shown.show();
  cols.not(shown).hide();
  $('.nav-tdy .page-item.active').removeClass('active');
  $('.nav-tdy .page-item a.show-tdy[data-range="' + min_seq + '"]').closest('.page-item').addClass('active');
  current_min_seq = min_seq;
}                                     
$(function(){
  show_tdy(1);
  $('a.show-tdy').click(function(){
    show_tdy(parseInt($(this).attr('data-range')));
  });                                   
  $('a.prev-tdy').click(function(){
    show_tdy(current_min_seq-1);
  });
  $('a.next-tdy').click(function(){
    show_tdy(current_min_seq+1);
  });                                                                       
  $('table.list.hidden').removeClass('hidden');
});
  </script>

  <ul class="pagination flex-wrap justify-content-end mb-0">
    <li class="page-item"><a class="page-link prev-tdy"><i class="mdi mdi-arrow-left" aria-hidden="true"></i></a></li>
    % for n in range(int((c.cnt_testiylesanded-1)/YCNT)+1):
    <%
      begin_range = n*YCNT + 1
      end_range = min(c.cnt_testiylesanded, (n+1)*YCNT)
    %>
    <li class="page-item"><a class="page-link show-tdy" data-range="${begin_range}">${begin_range}-${end_range}</a></li>
    % endfor
    <li class="page-item"><a class="page-link next-tdy"><i class="mdi mdi-arrow-right" aria-hidden="true"></i></a></li>
  </ul>
</nav>
% endif
