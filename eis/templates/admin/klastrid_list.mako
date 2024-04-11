% if c.items != '':
${h.pager(c.items)}
% endif
% if c.items:
<table class="table table-borderless table-striped">
  <thead>
    <tr>
      ${h.th_sort('klaster.seqmult', _("Unikaalne kordaja"))}
      ${h.th_sort('klaster.int_host', _("Sisevõrgu host"))}
      ${h.th_sort('klaster.staatus', _("Olek"))}
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(c.items):
    <% url = h.url('admin_edit_klaster', id=rcd.id) %>
    <tr>
      <td>
        ${rcd.seqmult}
      </td>
      <td>
        ${h.link_to_dlg(rcd.int_host, url, title=_("Klaster"))}
      </td>
      <td>
        % if rcd.staatus:
        ${h.badge_success(_("Kasutusel"))}
        % else:
        ${h.badge_secondary(_("Pole kasutusel"))}
        % endif
      </td>
    </tr>
    % endfor
  </tbody>
</table>
% endif

