${h.pager(c.items)}
% if c.items:
<table width="100%" class="table table-borderless table-striped" border="0" >
  <thead>
    <tr>
      <th></th>
      ${h.th_sort('sooritus.tahised', _("Testitöö"))}
      ${h.th_sort('hindamiskogum.tahis', _("Hindamiskogum"))}
      ${h.th_sort('sooritaja.lang', _("Keel"))}
      ${h.th_sort('kasutaja.nimi', _("Hindaja"))}
      ${h.th_sort('hindamine_1.liik', _("Liik"))}
      ${h.th_sort('hindamine_1.staatus', _("Olek"))}
      ${h.th(_("Probleem"))}
      ${h.th_sort('hindamine_2.uus_hindamine_id', _("Määratud uus hindaja"))}
    </tr>
  </thead>
  <tbody>
    % for rcd in c.items:
    <%
       tos, holek, hindamine_vana, hindamine_uus, hk_tahis, j_lang, vana_k_nimi = rcd
       k_uus = hindamine_uus and hindamine_uus.hindaja_kasutaja or None
    %>
    <tr>
      <td>
        ${h.checkbox('hindamine1_id', hindamine_vana.id, class_='hindamine1_id hindamine-%s' % hindamine_vana.liik,
        onclick="toggle_add(%s)" % (hindamine_vana.liik))}
      </td>
      <td>${tos.tahised}</td>
      <td>${hk_tahis}</td>
      <td>${model.Klrida.get_lang_nimi(j_lang)}</td>
      <td>
	    % if hindamine_vana and hindamine_vana.labiviija_id:
        ${h.link_to(vana_k_nimi,
        h.url('hindamine_sooritused', toimumisaeg_id=c.toimumisaeg.id, hindaja_id=hindamine_vana.labiviija_id))}
        % endif
      </td>
      <td>${hindamine_vana.liik_nimi}</td>
      <td>
        ${c.opt.H_STAATUS.get(hindamine_vana.staatus)}
        % if hindamine_vana.tyhistatud:
        (${_("tühistatud")})
        % endif
      </td>
      <td>
        ${holek.selgitus or holek.hindamisprobleem_nimi}
        % if holek.hindamisprobleem == const.H_PROBLEEM_HINDAMISERINEVUS:
          % if holek.hindamistase == const.HINDAJA2:
            (vaja III hindamist)
          % elif holek.hindamistase == const.HINDAJA3:
            (vaja IV hindamist)
          % endif
        % endif
      </td>
      <td>
        % if hindamine_uus and hindamine_uus.labiviija_id:
        ${h.link_to(k_uus.nimi,
        h.url('hindamine_sooritused', toimumisaeg_id=c.toimumisaeg.id, hindaja_id=hindamine_uus.labiviija_id))}
        % endif
      </td>
    </tr>
    % endfor
  </tbody>
</table>
% endif
