${h.pager(c.items)}
% if c.items:
<table width="100%" class="table table-borderless table-striped" border="0" >
  <thead>
    <tr>
      % for r in c.header:
      <%
        sort_field, title = r[:2] 
        helpable_id = len(r) > 2 and r[2] or None
        if title == 'Hindamiskogum': title = 'Hindamis-<br/>kogum' 
      %>
      ${h.th_sort(sort_field, title, helpable_id=helpable_id)}
      % endfor
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(c.items):    
    <tr>
      <%
        lv, hk, ta, k_nimi, tr_tahis, tr_id = rcd
        testiosa = ta.testiosa
        hk_tahis, test_id, test_nimi, liik_nimi, lang_nimi, skoht, dummy, alustamata, pooleli, hinnatud, badge = c.prepare_item(rcd, n)
        if tr_id and testiosa.vastvorm_kood in (const.VASTVORM_SH, const.VASTVORM_SP):
           # soorituskoha määratud suuline hindaja viiakse oma ruumi sooritajate nimekirja juurde
           url_pooleli = tr_id and h.url('shindamine_vastajad', testiruum_id=tr_id) or None
        else:
           # kirjalik hindaja või ruumiga sidumata SH hindaja
           url_pooleli = h.url('khindamine_vastajad', toimumisaeg_id=ta.id, hindaja_id=lv.id, staatus=const.H_STAATUS_POOLELI)
      %>
      <td>
        <div class="d-flex flex-wrap justify-content-between">
          <div class="dot-badge"><span class="badge badge-${badge}"> </span>
            ${hk_tahis}
            % if lv.valimis:
            (${_("valim")})
            % endif
          </div>
        </div>
      </td>
      <td>${test_id}</td>
      <td>
        % if url_pooleli:
        ${h.link_to(test_nimi, url_pooleli)}
        % else:
        ${test_nimi}
        % endif 
      </td>
      <td>
        ${liik_nimi}
      </td>
      <td>
        ${lang_nimi}
      </td>
      <td>
        ${skoht}
      </td>
      <td>
        ${alustamata or 0}
      </td>
      <td>
        ${pooleli}
      </td>
      <td>
        ${hinnatud}
      </td>
    </tr>
    % endfor
  </tbody>
</table>
% endif
