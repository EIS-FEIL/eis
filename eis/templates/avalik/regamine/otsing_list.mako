% if c.items != '':
${h.pager(c.items)}
% endif
% if c.items:
<% on_tasu = len([r for r in c.items if r.tasu]) > 0 %>
<table class="table table-borderless table-striped mb-1">
  <thead>
    <tr>
      ${h.th_sort('test.nimi', _('Test'))}
      ${h.th(_("Toimumise aeg ja koht"))}
      ${h.th_sort('sooritaja.staatus', _('Olek'))}
      % if on_tasu:
      ${h.th_sort('sooritaja.tasu', _('Tasu'))}
##      ${h.th_sort('sooritaja.tasutud', _('Tasutud'))}
      % endif
      <th sorter="false"></th>
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(c.items):
    <tr>
      <td>
        <%
           test = rcd.test
           testiliik = test.testiliik_kood
           voib_reg = rcd.voib_reg()
           if voib_reg and rcd.staatus == const.S_STAATUS_TYHISTATUD:
              url = h.url('regamine_avaldus_testid', testiliik=testiliik)
           elif voib_reg and rcd.staatus == const.S_STAATUS_REGAMATA:
              url = h.url('regamine_avaldus_isikuandmed', testiliik=testiliik)
           elif rcd.staatus in (const.S_STAATUS_TASUMATA, const.S_STAATUS_REGATUD):
              url = h.url('regamine_avaldus_kinnitamine', testiliik=testiliik)
           else:
              url = None
           nimi = test.nimi
           if rcd.kursus_kood:
              nimi += ' (%s)' % (rcd.kursus_nimi)
           if rcd.tasu:
              on_tasu = True
        %>
        % if url:
        ${h.link_to(nimi, url)}
        % else:
        ${nimi}
        % endif
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
      <td>${h.mstr(rcd.tasu) or _("Puudub")}</td>
##      <td>
##        % if rcd.tasu and rcd.staatus != const.S_STAATUS_TYHISTATUD:
##        % if rcd.tasutud:
##        ${h.badge_success(_("Tasutud"))}
##        % else:
##        ${h.badge_danger(_("Tasumata"))}
##        % endif
##        % endif
##      </td>
      % endif
      <td>
        % if url:
        ${h.btn_to('', url, mdicls="mdi-file-document-edit", title=_("Muuda"), level=0)}
        % endif
      </td>
    </tr>
    % endfor
  </tbody>
</table>
% endif
