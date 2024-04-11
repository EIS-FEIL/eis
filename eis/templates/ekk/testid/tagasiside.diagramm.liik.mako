${h.form(h.url('test_tagasiside_new_diagramm', test_id=c.test_id, testiosa_id=c.testiosa_id), form_name='form_dlg', method='get')}
${h.hidden('dname', '')}
${h.hidden('kursus', c.kursus)}
<div class="d-flex flex-wrap">
% if c.opt_dname:
% for dname, title, subtitle in c.opt_dname:
<a href="#" data-dname="${dname}" class="dnamelink card card-is-link m-1" style="width: 20rem;">
  <div class="card-body">
    <h4 class="card-title">${title}</h4>
    <p class="card-subtitle">
      ${subtitle}
    </p>
  </div>
</a>
% endfor
% else:
${_("Testi kirjelduse osas ei saa diagramme kasutada!")}
% endif
</div>
${h.end_form()}
<script>
$('.dnamelink').click(function(){
  var dname = $(this).attr('data-dname'),
      el = $('#dname');
  el.val(dname);
  submit_dlg(el[0]);
});
</script>
