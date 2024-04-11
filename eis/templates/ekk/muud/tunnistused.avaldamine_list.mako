<% on_salvestamata = c.staatus == str(const.N_STAATUS_KEHTIV) %>

% if c.items:
${h.pager(c.items, msg_not_found=_("Tunnistusi ei leitud"),
                   msg_found_one=_("Leiti üks tunnistus"),
                   msg_found_many=_("Leiti {n} tunnistust"))}
<table width="100%" class="table table-borderless table-striped" border="0" >
  <thead>
    <tr>
      % if on_salvestamata and c.user.has_permission('tunnistused', const.BT_UPDATE):
      <th>${h.checkbox('t_koik')}</td>
      % endif
      ${h.th_sort('tunnistusenr', _("Tunnistus"))}
      ${h.th(_("Nimi"))}
      ${h.th(_("Isikukood või sünniaeg"))}
      ${h.th(_("Olek"))}
      ${h.th(_("Väljastamisaeg"))}
      ${h.th(_("Alus"))}
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(c.items):
    <tr>
      % if on_salvestamata and c.user.has_permission('tunnistused', const.BT_UPDATE):
      <td>${h.checkbox('t_id', rcd.id)}</td>
      % endif
      <td>
        % if rcd.has_file:
        ${h.link_to(rcd.tunnistusenr, h.url('muud_tunnistused_avaldamine',  id='%d.%s' % (rcd.id, rcd.fileext)))}
        % else:
        ${rcd.tunnistusenr}
        % endif
      </td>
      <td>${rcd.eesnimi} ${rcd.perenimi}</td>
      <td>${rcd.kasutaja.isikukood or h.str_from_date(rcd.kasutaja.synnikpv)}</td>
      <td>${rcd.staatus_nimi}</td>
      <td>${h.str_from_date(rcd.valjastamisaeg)}</td>
      <td>${rcd.alus}</td>
    </tr>
    % endfor
  </tbody>
</table>

% if on_salvestamata and c.user.has_permission('tunnistused', const.BT_UPDATE):
<br/>
${h.submit(_("Kustuta ja taasta varasem"), id='delete_t', style="display:none")}
<script>
  var toggle_add = function()
  {
     $('button#delete_t').toggle($('input[name="t_id"]:checked').length > 0);
     $('button#salvesta_alus,button#salvesta').toggle($('input[name="t_id"]:checked').length == 0);  
  };
  $(function(){
    $('input[name="t_id"]').click(toggle_add);
    $('input[name="t_koik"]').click(function(){
       $('input[name="t_id"]').prop('checked', $(this).prop('checked'));
       toggle_add();
    });
  });
</script>
% endif

% endif

