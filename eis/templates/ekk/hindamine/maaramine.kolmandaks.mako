${h.form_save(None, form_name='form_kolmandaks')}

<% ch = h.colHelper('col-md-6', 'col-md-6') %>
<div>
  % if c.hindamiskogum:
  <div class="form-group row">
    ${ch.flb(_("Hindamiskogum"))}
    <div class="col">
      ${c.hindamiskogum.tahis}
      ${h.hidden('hindamiskogum_id', c.hindamiskogum_id)}
    </div>
  </div>
  % endif

  % if c.lang:
  <div class="form-group row">
    ${ch.flb(_("Soorituskeel"))}
    <div class="col">
      ${model.Klrida.get_str('SOORKEEL', c.lang)}
      ${h.hidden('lang', c.lang)}
    </div>
  </div>
  % endif

  % if c.piirkond_id:
  <div class="form-group row">
    ${ch.flb(_("Soorituspiirkond"))}
    <div class="col">
      ${model.Piirkond.get(c.piirkond_id).nimi}
      ${h.hidden('piirkond_id', c.piirkond_id)}
    </div>
  </div>
  % endif

  % if c.testimiskord.sisaldab_valimit:
  <div class="form-group row">
    <div class="col">
      ${h.radio('valim', '0', label=_("Ainult mitte-valimi tööd"))}
      ${h.radio('valim', '1', label=_("Ainult valimi tööd"))}
    </div>
  </div>
  % endif
  
  <div class="form-group row">
    ${ch.flb(_("Täiendava hindamise tööde protsent"))}
    <div class="col">
      ${h.posint5('protsent', c.kolmasprotsent, maxvalue=100)} %
    </div>
  </div>
</div>
${h.submit_dlg()}
${h.end_form()}

