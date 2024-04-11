<div class="fbwrapper" url="${h.url_current(None, getargs=True)}" style="display:none">
  ${c.tagasiside_html}
</div>
<script>
  $(function(){
  ## tagasiside alamosade peitmine
  $('.fbrpartfilter:not(:checked)').each(function(){
    $('.fbrpart#fbrpart_' + this.value).hide();
  });
  $('.fbwrapper').show();
  
  % if c.controller in ('gruppidetulemused','osalejatetulemused'):
  ## ktbl klasside nimetustest teeme lingid osalejate sakile
  $('a.lnk-opilased').each(function(){
  var href = "${h.url('ktulemused_osalejatetulemused', test_id=c.test.id, testimiskord_id=c.testimiskord.id, kursus=c.kursus or '')}"
  $(this).prop('href', href + '?' + $(this).attr('data-arg'));
  });

  $('.fbwrapper a.lnk-opilane').each(function(){
  ## link sooritajale funktsiooni g_lnk_np_ns_cnt tulemusena genereeritud sooritajate loetelust 
   var href = "${h.url('ktulemused_opetajatulemus', test_id=c.test.id, testimiskord_id=c.testimiskord.id, id='SOORITAJAID', kursus=c.kursus or '')}";
  $(this).prop('href', href.replace('SOORITAJAID', $(this).data('j')));
  });
  % endif
  
  });
</script>
