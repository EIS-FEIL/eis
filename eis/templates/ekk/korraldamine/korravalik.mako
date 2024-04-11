## Nupule "Jaota teisele testimiskorrale" vajutamisel avaneva dialoogiakna sisu

% if len(c.teisedkorrad) == 0:
${h.alert_error(_("Sellel testil ei ole teisi testimiskordi, mis on veel algamata ning mille kõigi toimumisaegade kohtadesse jaotamine on kinnitamata."), False)}

% else:
${h.form_save(None, h.url_current('create'))}
${h.hidden('sub', 'teinekord')}

% if c.sooritused_id:
% for s_id in c.sooritused_id:
${h.hidden('sooritus_id', s_id)}
% endfor
${_("Valitud {n} sooritajat").format(n=c.total_cnt)}
% else:
${_("Soorituskohas on {n} registreeritud sooritajat").format(n=c.total_cnt)}
% endif

<div class="form-group row">
  ${h.flb(_("Jaotatavate sooritajate arv"), 'arv', 'col-md-4')}
  <div class="col">
    ${h.posint5('arv', c.total_cnt, maxvalue=c.total_cnt)}
  </div>
</div>
<div class="form-group row">
  ${h.flb(_("Testimiskord"), 'tkord', 'col-md-4')}
  <div class="col">
    % for tkord in c.teisedkorrad:
    <div>
      ${tkord.tahised}
      <span class="pl-4">${h.submit(_("Vali"), id='tk_%s' % tkord.id)}</span>
    </div>
    % endfor
  </div>
</div>
${h.end_form()}
% endif
