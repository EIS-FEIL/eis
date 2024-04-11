${h.form(h.url('nimekiri_sooritajad', testimiskord_id=c.testimiskord_id), method='post', multipart=True)}
${h.hidden('sub', 'fail')}

<div class="p-2">
  <div class="form-group row">
    ${h.flb3(_("Sooritajate fail"))}
    <div class="col-md-9">
      ${h.file('ik_fail', value=_("Fail"))}
    </div>
  </div>
  <% opt_keeled = c.testimiskord and c.testimiskord.opt_keeled or c.test.opt_keeled %>
  % if len(opt_keeled) > 0:
  <div class="form-group row">
    ${h.flb3(_("Soorituskeel"))}
    <div class="col">
      % if len(opt_keeled) > 1:
      ${h.select('keel', c.keel, opt_keeled, wide=False)}    
      % else:
      ${opt_keeled[0][1]}
      ${h.hidden('keel', opt_keeled[0][0])}
      % endif
    </div>
  </div>
  % endif
    
  <% opt_kursused = c.test.opt_kursused %>
  % if len(opt_kursused):
  <div class="form-group row">  
    ${h.flb3(_("Kursus"))}
    <div class="col">
      ${h.select('kursus', None, opt_kursused, wide=False)}    
    </div>
  </div>
  % endif
</div>

<div class="text-right">
  ${h.submit(_("Salvesta"), clicked=True)}
</div>
${h.end_form()}
