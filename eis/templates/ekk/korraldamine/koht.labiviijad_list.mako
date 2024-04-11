% if c.items != '' and not c.items:
${_("Läbiviijaid ei ole")}
% elif c.items:
<% c.can_update = c.user.has_permission('korraldamine', const.BT_UPDATE, obj=c.testikoht) %>
${h.pager(c.items, form='', list_url=h.url_current(partial=1))}
<table width="100%" class="table table-borderless table-striped" border="0" >
  <caption>${_("Soorituskohta määratud läbiviijad")}</caption>
  % if c.can_update:
  <col width="60px"/>
  <col width="20px"/>
  % endif
  <thead>
    <tr>
      <th></th>
      <th>
        % if c.can_update:
        ${h.checkbox1('all', 1, title=_("Vali kõik"), class_="nosave")}
        % endif
      </th>
      ${h.th_sort('kasutaja.isikukood', _("Testi läbiviija"))}
      ${h.th_sort('labiviija.tahis', _("Läbiviija tähis"))}
      ${h.th_sort('testiruum.tahis',_("Testiruum"))}
      ${h.th_sort('ruum.tahis', _("Ruum"))}
      ${h.th_sort('testiruum.algus', _("Algus"))}
      ${h.th(_("Roll"))}
      ${h.th(_("Olek"))}
      ${h.th(_("Muud osalemised"))}
      <th></th>
    </tr>
  </thead>
  <tbody>
    <%
       testsessioon_id = c.toimumisaeg.testimiskord.testsessioon_id
    %>
    % for n, rcd in enumerate(c.items):
    <% 
       lv, k, truum_algus, truum_tahis, ruum_tahis = rcd 
       can_change = c.can_update and lv.kasutajagrupp_id != const.GRUPP_HINDAJA_K
    %>
    <tr>
      <td>
        % if can_change:
        % if not (c.toimumisaeg.ruum_noutud and truum_tahis and not ruum_tahis):
        ${h.btn_to_dlg('', h.url('korraldamine_koht_otsilabiviijad',
toimumisaeg_id=c.toimumisaeg.id, testikoht_id=c.testikoht.id, labiviija_id=lv.id,default=True),
        title=_("Vali isik"),
        dlgtitle=lv.kasutajagrupp.nimi,
        mdicls='mdi-account-edit',
        size='lg', level=0)}
        % endif
        % endif
      </td>
      <td>
        % if k and c.can_update:
        ${h.checkbox('labiviija_id', lv.id, onchange='toggle_viija()', class_='labiviija_id nosave', mr0=True, title=_("Vali rida {s}").format(s=''))}
        % endif
      </td>
      <td>
        % if k:
        ${h.link_to(k.nimi, h.url('admin_kasutaja', id=k.id))}
        % else:
        ${_("Määramata")}
        % endif
        % if can_change:
        ${h.remove(h.url('korraldamine_koht_delete_labiviija',
        toimumisaeg_id=c.toimumisaeg.id, testikoht_id=c.testikoht.id,
        id=lv.id, kasutaja_id=lv.kasutaja_id))}
        % endif
      </td>
      <td>${lv.tahis}</td>
      <td>
        ${truum_tahis}
      </td>
      <td>
        % if truum_tahis:
        ${ruum_tahis or _("määramata")}
        % endif
      </td>
      <td>${h.str_from_datetime(truum_algus)}</td>
      <td>${lv.kasutajagrupp.nimi}
        % if lv.liik:
        (${lv.liik_nimi})
        % endif
        % if lv.valimis:
        (${_("valim")})
        % endif
        <% hk = lv.hindamiskogum %>
        % if hk:
        ${hk.tahis}
        % if not hk.staatus:
        <div class="error">${_("Kehtetu hindamiskogum!")}</div>
        % endif
        % endif
      </td>
      <td>
        ${lv.staatus_nimi}
      </td>
      <td>
        % if k and testsessioon_id:
        <%
           muud_cnt = model.Labiviija.query.filter_by(kasutaja_id=k.id).join(model.Labiviija.toimumisaeg).join(model.Toimumisaeg.testimiskord).filter(model.Testimiskord.testsessioon_id==testsessioon_id).count()
        %>
          % if muud_cnt>1:
        ${h.link_to_dlg(muud_cnt-1, h.url('korraldamine_labiviija',
        toimumisaeg_id=c.toimumisaeg.id,id=lv.id, partial=True),
        title=_("Muuda osalemiste arv"),
        dlgtitle=lv.kasutaja.nimi, size='lg', level=2)}
          % endif
        % endif
      </td>
      <td>
        % if can_change:
        % if not (c.toimumisaeg.ruum_noutud and truum_tahis and not ruum_tahis):
        ${h.btn_to('', h.url('korraldamine_koht_labiviijad',
        toimumisaeg_id=c.toimumisaeg.id, testikoht_id=c.testikoht.id,
        labiviija_id=lv.id,default=True, uus=True), method='post', level=0,
        title=_("Lisa uus rida"),
        mdicls='mdi-account-plus')}
        % endif
        % endif
      </td>
    </tr>
    % endfor
  </tbody>
</table>
% endif
