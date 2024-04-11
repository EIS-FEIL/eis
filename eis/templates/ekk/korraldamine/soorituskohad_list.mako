${h.pager(c.items,msg_not_found=_("Soorituskohti ei leitud"), 
          msg_found_one=_("Leiti 1 soorituskoht"),
          msg_found_many=_("Leiti {n} soorituskohta"))}
% if c.items:
<%
   vastvorm = c.toimumisaeg.testiosa.vastvorm_kood
%>

<table width="100%" class="table table-borderless table-striped" border="0" >
  <thead>
    <tr>
      <th></th>
      ${h.th_sort('testikoht.tahised', _("Tähis"))}
      ${h.th_sort('koht.nimi', _("Soorituskoht"))}
      ${h.th(_("Asukoht"))}
      ${h.th_sort('testiruum.tahis',_("Testiruum"))}
      ${h.th_sort('ruum.tahis', _("Ruum"))}
      ${h.th_sort('testiruum.kohti', _("Kohti"))}
% if vastvorm == const.VASTVORM_KONS:
      ${h.th_sort('testiruum.sooritajate_arv', _("Sooritajaid piirkonnas"))}
% else:
      ${h.th_sort('testiruum.sooritajate_arv', _("Sooritajaid"))}
% endif
      ${h.th(_("Läbiviija määramata"))}
      % if c.pole_h:
      ${h.th(_("Hindajata hindamiskogumid"))}
      % endif
      ${h.th_sort('testiruum.algus', _("Toimumise aeg"))}
      <th sorter="false"></th>
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(c.items):
    <% 
       testiruum, koht, ruum = rcd
       testikoht = testiruum.testikoht
       if vastvorm == const.VASTVORM_KONS:
          url_edit = h.url('korraldamine_koht_labiviijad',
                            toimumisaeg_id=c.toimumisaeg.id,
                            testikoht_id=testiruum.testikoht_id)
       else:
          url_edit = h.url('korraldamine_koht_sooritajad',
                            toimumisaeg_id=c.toimumisaeg.id, 
                            testikoht_id=testiruum.testikoht_id)
       row = c.prepare_item(rcd, n)
    %>
    <tr>
      <td>
        % if testiruum.sooritajate_arv:
        ${h.checkbox('tr_id', testiruum.id, onclick="toggle_testiruum()",
        class_='nosave tr-id')}
        % endif
      </td>
      <td nowrap>${testikoht.tahised}-${testiruum.tahis} <!--${testiruum.id}--></td>
      <td>${h.link_to(koht.nimi, url_edit)}</td>

      % for ind, value in enumerate(row[2:]):
      <td>${value}</td>
      % endfor

      <td>
        % if testiruum.bron_arv == 0:
        ${h.remove(h.url('korraldamine_delete_soorituskoht',
        toimumisaeg_id=c.toimumisaeg.id, id=testiruum.id))}
        % endif
      </td>
    </tr>
    % endfor
  </tbody>
</table>
% endif
