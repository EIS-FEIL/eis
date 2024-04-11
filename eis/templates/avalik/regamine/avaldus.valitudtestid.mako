<% on_tasu = len([r for r in c.sooritajad if r.tasu]) > 0 %>
<div class="d-flex flex-wrap">
<h2 class="flex-grow-1">
% if c.testiliik in const.TESTILIIGID_EKSAMID:
${_("Eksamid")}
% else:
${_("Testid")}
% endif
</h2>
${h.link_to(_("Muuda valik"), h.url('regamine_avaldus_testid_testiliik', testiliik=c.testiliik))}
</div>

<table class="table mb-2">
  <thead>
    <tr>
      ${h.th(_("Nimetus"))}
      ${h.th(_("Soorituskeel"))}
      ${h.th(_("Toimumise aeg ja koht"))}
      ${h.th(_("Olek"))}
      % if on_tasu:
      ${h.th_sort('sooritaja.tasu', _('Tasu'))}
      % endif
    </tr>
  </thead>
  <tbody>
    % for rcd in c.sooritajad:
    <tr>
      <td>
        ${rcd.test.nimi}
        % if rcd.kursus_kood:
        (${rcd.kursus_nimi})
        % endif
      </td>
      <td>
        ${rcd.lang_nimi}
      </td>
      <td>
        <% c.ska_sooritaja = rcd %>
        <%include file="/avalik/regamine/sooritus_koht_aeg.mako"/>
      </td>
      <td>
        % if rcd.staatus in (const.S_STAATUS_REGATUD, const.S_STAATUS_ALUSTAMATA):
        ${h.badge_success(rcd.staatus_nimi)}
        % elif rcd.staatus == const.S_STAATUS_TYHISTATUD:
        ${h.badge_secondary(rcd.staatus_nimi)}
        % elif rcd.staatus < const.S_STAATUS_REGATUD:
        ${h.badge_danger(rcd.staatus_nimi)}
        % else:
        ${h.badge_primary(rcd.staatus_nimi)}                     
        % endif                     
      </td>
      % if on_tasu:
      <td>
        ${h.mstr(rcd.tasu) or _("Puudub")}
      </td>
      % endif
    </tr>
    % endfor
  </tbody>
</table>
