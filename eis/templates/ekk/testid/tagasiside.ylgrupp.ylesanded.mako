${h.not_top()}
${h.form_save(c.item.id)}
% if len(c.opt_osa) > 1:
<div class="d-flex mb-3">
  ${h.flb(_("Testiosa"), 'osa_id', 'mr-2')}
  <div>
  ${h.select('osa_id', c.curr_osa_id, c.opt_osa)}
  </div>
</div>
% endif

% for osa_id, o_data in c.gy_data:
% if o_data:
<% naita_komplekt = len(o_data) > 1 %>
<div class="yg-osa yg-osa-${osa_id}" style="display:${osa_id==c.curr_osa_id and 'block' or 'none'}">
% for k_tahis, li in o_data:
% if li:
  % if naita_komplekt:
   <h4>${_("Komplekt")} ${k_tahis}</h4>
  % endif
    % for ty_tahis, vy_id, y_id ,y_nimi, gy_id in li:
    <% label = '%s %s (%s)' % (ty_tahis or '', y_nimi, '%s %s' % (_("ül"), y_id)) %>
    <div>
    % if c.is_edit:
    ${h.checkbox('vy_id', vy_id, label=label, checked=gy_id)}
    % else:
    ${label}
    % endif
    </div>
    % endfor
% endif
    % endfor
</div>
% endif
% endfor

% if c.is_edit:
${h.submit_dlg()}
% endif
${h.end_form()}

% if c.is_edit and len(c.opt_osa) > 1:
<script>
  $('select#osa_id').change(function(){
     var osa_id = $(this).val();
     $('.yg-osa.yg-osa-' + osa_id).show();
     $('.yg-osa:not(.yg-osa-' + osa_id+')').hide();
  });
</script>
% endif
