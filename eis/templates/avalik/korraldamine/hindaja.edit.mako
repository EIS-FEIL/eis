
<% kasutaja = c.item.kasutaja %>
<div class="d-flex flex-wrap mb-3">
% if kasutaja:
<div class="mr-4">
  ${kasutaja.nimi}
  <%
    item2 = c.item.get_hindaja2()
    kasutaja2 = item2 and item2.kasutaja
  %>
  % if kasutaja2:
  <br/>${kasutaja2.nimi}
  % endif
</div>
% endif
<div class="mr-4">${c.item.hindamiskogum.nimi}</div>
% if c.sooritajate_arv != '':
<div class="brown">${_("{n} hinnatavat tööd").format(n=c.sooritajate_arv)}
  % if c.testimiskord.sisaldab_valimit:
  % if c.item.valimis:
  (${_("valimis")})
  % else:
  (${_("mitte-valimis")})
  % endif
  % endif
</div>
% endif
</div>
</div>

${h.form_save(c.item.id, form_name='form_edithindaja')}

  % if len(c.klassid) > 1:
  <% r_klassid = [(r.klass or '', r.paralleel or '') for r in c.item.labiviijaklassid] %>
  <div class="form-group row">
    ${h.flb3(_("Klass"), 'klassid')}
    <div id="klassid" class="col">
    % for klass, paralleel, cnt in c.klassid:
    <%
      value = '%s-%s' % (klass, paralleel)
      label = not klass and _("määramata") or f"{klass} {paralleel}"
      checked = not r_klassid or (klass, paralleel) in r_klassid
    %>
    ${h.checkbox('klass', value, checked=checked, label=f'{label} ({cnt})')}
    % endfor
    ${h.hidden('klassid_arv', len(c.klassid))}
    </div>
  </div>
  % endif
  
  <div class="form-group row">
    ${h.flb3(_("Max tööde arv"), 'planeeritud_toode_arv', 'pr-3')}
    <div class="col">
      ${h.posint5('planeeritud_toode_arv', c.item.planeeritud_toode_arv)}
    </div>
  </div>

  <div class="text-right">
    ${h.submit_dlg()}
  </div>
${h.end_form()}
