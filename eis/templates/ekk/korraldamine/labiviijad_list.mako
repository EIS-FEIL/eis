<% c.can_update = c.user.has_permission('korraldamine', const.BT_UPDATE, obj=c.test) %>

${h.pager(c.items)}
% if c.items:
<table width="100%" class="table table-borderless table-striped" border="0" >
  <thead>
    <tr>
      <th></th>
      ${h.th_sort('koht.nimi', _("Soorituskoht"))}
      ${h.th_sort('testiruum.tahis',_("Testiruum"))}
      ${h.th_sort('ruum.tahis', _("Ruum"))}
      ${h.th_sort('testiruum.algus', _("Algus"))}
      ${h.th_sort('labiviija.kasutajagrupp_id', _("Roll"))}
      ${h.th_sort('kasutaja.nimi', _("Testi läbiviija"))}
      ${h.th_sort('labiviija.tahis', _("Läbiviija tähis"))}
      <th colspan="2"></th>
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(c.items):
    <% 
       testiruum = rcd.testiruum
       ruum = testiruum and testiruum.ruum or None
       testikoht = rcd.testikoht
       koht = testikoht.koht
       url_edit = h.url('korraldamine_koht_labiviijad',
          toimumisaeg_id=c.toimumisaeg.id, testikoht_id=testikoht.id)
       kasutaja = rcd.kasutaja
       # kirjalikke hindajaid siin ei lisa, kuna siin ei toimu hindamiskogumi valikut
       can_change = c.can_update and rcd.kasutajagrupp_id != const.GRUPP_HINDAJA_K
    %>
    <tr>
      <td>
        % if rcd.kasutaja_id and c.can_update:
        ${h.checkbox('labiviija_id', rcd.id, onclick='toggle_viija()', class_="labiviija_id")}
        % endif
      </td>
      <td>${h.link_to(koht.nimi, url_edit)}</td>
      <td>
        % if testiruum:
        ${testiruum.tahis}
        % endif
      </td>
      <td>
        % if testiruum:
        ${ruum and ruum.tahis or _("määramata")}
        % endif 
      </td>
      <td>
        ${h.str_from_datetime(testiruum and testiruum.algus or testikoht.alates)}
      </td>
      <td>${rcd.kasutajagrupp.nimi}
        % if rcd.liik:
        (${rcd.liik_nimi})
        % endif
        % if rcd.valimis:
        (${_("valim")})
        % endif
        <% hk = rcd.hindamiskogum %>
        % if hk:
        ${hk.tahis}
        % if not hk.staatus:
        <div class="error">${_("Kehtetu hindamiskogum!")}</div>
        % endif
        % endif
      </td>
      <td>
        % if can_change:
        <% 
           lv_opt = rcd.get_labiviijad_opt()
           if kasutaja and kasutaja.id not in [o[0] for o in lv_opt]:
              lv_opt = [(kasutaja.id, kasutaja.nimi)] + lv_opt
        %>
        ${h.select('lv_%d_kasutaja_id' % (rcd.id), rcd.kasutaja_id, lv_opt, empty=True)}
        % elif kasutaja:
        ${kasutaja.nimi}
        % endif
      </td>
      <td>${rcd.tahis}</td>
      <td>
        % if can_change:
        % if not (c.toimumisaeg.ruum_noutud and testiruum and not ruum):
        ${h.btn_to_dlg(_("Lisa"),
        h.url('korraldamine_new_labiviija', toimumisaeg_id=c.toimumisaeg.id,
        labiviija_id=rcd.id, list_url=h.get_list_url()),
        title=_("Testi läbiviija"), width=700, mdicls='mdi-plus', level=2)}
        % endif
        ${h.bremove(h.url('korraldamine_delete_labiviija',
        toimumisaeg_id=c.toimumisaeg.id, id=rcd.id))}
        % endif
      </td>
      <td></td>
    </tr>
    % endfor
  </tbody>
</table>
% endif
