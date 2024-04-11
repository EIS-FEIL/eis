% if c.items != '' and not c.items:
${_("Läbiviijaid ei ole")}
% elif c.items:
${h.pager(c.items)}
<table width="100%" class="table table-borderless table-striped" border="0" >
  <caption>${_("Soorituskohta määratud läbiviijad")}</caption>
  <thead>
    <tr>
      <th></th>
      ${h.th_sort('kasutaja.nimi', _("Testi läbiviija"))}
      ${h.th_sort('labiviija.tahis', _("Tähis"))}
      ${h.th_sort('testiruum.tahis', _("Testiruum"))}
      ${h.th_sort('ruum.tahis', _("Ruum"))}
      ${h.th_sort('testiruum.algus', _("Algus"))}
      ${h.th(_("Roll"))}
      ${h.th(_("Olek"))}
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(c.items):
    <%
      lv, k, testiruum_tahis, ruum_tahis, testiruum_algus = rcd
      kasutajagrupp = lv.kasutajagrupp
      url_vali = h.url('korraldamine_otsilabiviijad', testikoht_id=c.testikoht.id, labiviija_id=lv.id, default=True)
      url_lisa = h.url('korraldamine_otsilabiviijad', testikoht_id=c.testikoht.id, grupp_id=lv.kasutajagrupp_id, default=True)
    %>
    <tr>
      <td>
        % if not (c.toimumisaeg.ruum_noutud and testiruum_tahis and not ruum_tahis):
        % if lv.kasutajagrupp_id in c.lubatud_grupid_id:
        ${h.btn_to_dlg('', url_vali, title=_("Vali isik"),
        dlgtitle=kasutajagrupp.nimi, level=0, mdicls="mdi-account-edit")}

        % if lv.testiruum and lv.kasutaja_id:
        ${h.btn_to_dlg('', url_lisa, title=_("Lisa uus rida"),
        dlgtitle=kasutajagrupp.nimi, level=0, mdicls="mdi-account-plus")}
        % endif
        % endif
        % endif
      </td>
      <td>
        % if k:
        ${k.nimi}
        % else:
        ${_("määramata")}
        % endif

        % if lv.kasutajagrupp_id in c.lubatud_grupid_id:
        ${h.remove(h.url('korraldamine_delete_labiviija',
        testikoht_id=c.testikoht.id, id=lv.id, kasutaja_id=lv.kasutaja_id),
        icon='mdi-account-remove',
        confirm_id="confirm_lv_%s" % lv.id)}
        <span id="confirm_lv_${lv.id}" style="display:none">
          % if k:
          ${_("Kas oled kindel, et soovid läbiviija rolli eemaldada ({roll} {nimi})?").format(roll=kasutajagrupp.nimi, nimi=k.nimi)}
          % else:
          ${_("Kas oled kindel, et soovid läbiviija rolli eemaldada?")}
          % endif
        </span>
        % endif
      </td>
      <td>${lv.tahis}</td>
      <td>
        ${testiruum_tahis}
      </td>
      <td>
        % if testiruum_tahis:
        ${ruum_tahis or _("määramata")}
        % endif
      </td>
      <td>${h.str_from_datetime(testiruum_algus or c.testikoht.alates)}</td>
      <td>${kasutajagrupp.nimi}
        % if lv.valimis:
        (${_("valim")})
        % endif
      </td>
      <td>${lv.staatus_nimi}</td>
    </tr>
    % endfor
  </tbody>
</table>
% endif

