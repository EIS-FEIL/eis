% if c.items:
${h.pager(c.items, msg_not_found=_("Tunnistusi ei leitud"),
                   msg_found_one=_("Leiti üks tunnistus"),
                   msg_found_many=_("Leiti {n} tunnistust"))}
<table width="100%" class="table table-borderless table-striped" border="0" >
  <thead>
    <tr>
      ${h.th(_("Isikukood või sünniaeg"))}
      ${h.th(_("Nimi"))}
      ${h.th(_("Liik"))}
      ${h.th(_("Väljastamisaeg"))}
      ${h.th(_("Olek"))}
      ${h.th_sort('tunnistusenr', _("Tunnistus"))}
      ${h.th(_("Põhjendus"))}
      % if c.user.has_permission('tunnistused', const.BT_UPDATE):
      ${h.th('')}
      % endif
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(c.items):
    <% 
       tunnistus, kasutaja = rcd
    %>
    <tr>
      <td>
        ${kasutaja.isikukood or h.str_from_date(kasutaja.synnikpv)}
      </td>
      <td>
        ${kasutaja.nimi}
      </td>
      <td>${tunnistus.testiliik_nimi}</td>
      <td>${h.str_from_date(tunnistus.valjastamisaeg)}</td>
      <td>${tunnistus.staatus_nimi}</td>
      <td>
        % if tunnistus.has_file:
        <%
          url_file = h.url('muud_tunnistused_avaldamine',  id='%d.%s' % (tunnistus.id, tunnistus.fileext))
        %>
        ${h.link_to(tunnistus.tunnistusenr, url_file)}
        % else:
        ${tunnistus.tunnistusenr}
        % endif
      </td>
      <td>
        % if tunnistus.pohjendus:
        ${tunnistus.pohjendus}<br/>
        % endif
        ${tunnistus.tyh_pohjendus}
      </td>
      % if c.user.has_permission('tunnistused', const.BT_UPDATE):
      <td>
        % if tunnistus.staatus != const.N_STAATUS_KEHTETU:
        ${h.btn_to_dlg(_("Tühista"), h.url_current('edit', id=tunnistus.id), title=_("Tunnistuse tühistamine"), width=600)}
        % else:
        ${h.btn_to_dlg(_("Ennista"), h.url_current('edit', id=tunnistus.id), title=_("Tühistatud tunnistuse ennistamine"), width=600)}        
        % endif
      </td>
      % endif
    </tr>
    % endfor
  </tbody>
</table>

% endif

