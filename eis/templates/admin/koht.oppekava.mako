${h.form_save(None)}
<div class="form-wrapper-lineborder mb-2">
  <div class="form-group row">
    ${h.flb3(_("Õppetase"), 'oppetase_kood')}
    <div class="col">
      ${h.select('oppetase_kood', c.item.oppetase_kood, c.opt.klread_kood('OPPETASE'), onchange="oppetase_changed()", empty=True)}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Õppekavajärgne haridustase"),'kavatase_kood')}
    <div class="col">
      ${h.select('kavatase_kood', c.item.kavatase_kood, c.opt.klread_kood('KAVATASE', ylem_kood=c.item.kavatase_kood, ylem_required=True))}
    </div>
  </div>
</div>

<script>
  function oppetase_changed()
  {
       var target = $('select#kavatase_kood');
       update_options($('select#oppetase_kood'), 
                      "${h.url('pub_formatted_valikud', kood='KAVATASE', format='json')}", 
                      'ylem_kood', 
                      target);
  }
</script>
<div class="text-right">
  ${h.submit_dlg()}
</div>
${h.end_form()}
