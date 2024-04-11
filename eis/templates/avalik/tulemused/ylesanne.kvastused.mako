## silumiseks vastused
<%
  yv = c.ylesandevastus
  vy = c.vy
  ylesanne = vy.ylesanne or None
  ty = c.ty
%>
% if not c.ylesandevastus:
${_("Ülesande vastust ei leitud")}
% elif not ylesanne:
${_("Ülesanne puudub")}
% else:
<div style="background:#fff;margin:5px;padding:5px;">
  <div class="d-flex flex-wrap">
    <div class="flex-grow-1">
      ${h.link_to('%s %d' % (_("Ülesanne"), ylesanne.id), h.url('ylesanded_edit_sisu', id=ylesanne.id))}
      (${h.str_from_datetime(yv.created, True)})
    </div>
    ${self.logilink_yv(yv, ylesanne)}
  </div>
  <div>${ylesanne.nimi}</div>

    ${self.tbl_yv(yv, ty, vy, ylesanne)}

    % if yv.on_toorvastus:
    ${h.alert_error(_("Toorvastus on veel lahti pakkimata"), False)}
    % endif

    ${self.tbl_sp(yv, ty, vy, ylesanne)}    

    ${self.tbl_aspektid(yv, ty, vy, ylesanne)}        

    ${self.tbl_yhinded(yv, ty, vy, ylesanne)}            
    
    ${h.btn_to(_("Arvuta ülesande tulemus uuesti"),
    h.url_current('update', sub='arvuta', ylesandevastus_id=yv.id, sooritus_id=yv.sooritus_id), method='post')}
    % if c.ylesandevastus.arvutuskaik:
    <div>
      ${h.literal(c.ylesandevastus.arvutuskaik.replace('\n','<br/>\n'))}
    </div>
    % endif
</div>
% endif

<%def name="logilink_yv(yv, ylesanne)">
% if yv and c.testiosa.vastvorm_kood in (const.VASTVORM_KE, const.VASTVORM_SE):
<%
    tos = yv.sooritus
    ik = tos.sooritaja.kasutaja.isikukood
    if tos.algus:
       alates = h.str_from_date(tos.algus)
       alates_kell = h.str_time_sec_from_datetime(tos.algus - model.timedelta(seconds=10))
    else:
       alates = alates_kell = None
    if tos.lopp:
       kuni = h.str_from_date(tos.lopp)
       kuni_kell = h.str_time_sec_from_datetime(tos.lopp + model.timedelta(seconds=10))
    else:
       kuni = kuni_kell = None
%>
% if ik and alates:
  ${h.link_to(_("Logi"), h.url('admin_logi', isikukood=ik, alates=alates, alates_kell=alates_kell, kuni=kuni, kuni_kell=kuni_kell, ylesanne_id=ylesanne.id, psize=100, show_request=1), class_="pr-3")}
% endif
% endif
</%def>

<%def name="tbl_yv(yv, ty, vy, ylesanne)">    
    <table  class="table table-borderless table-striped table-align-top">
      <thead>
        <tr>
          <th colspan="3">${_("Toorpunktid")}</th>
          <th colspan="3">${_("Pallid")}</th>
          <th rowspan="2">${_("Lõplik")}</th>
          <th rowspan="2">${_("Õigete arv")}</th>
          <th rowspan="2">${_("Valede arv")}</th>
          <th rowspan="2">${_("Valimata valede arv")}</th>
          <th rowspan="2">${_("Valimata õigete arv")}</th>
          <th rowspan="2">${_("Õigete suhe")}</th>
          <th rowspan="2">${_("Vastuseta")}</th>
          <th rowspan="2">${_("Käsitsihinnatav")}</th>
          <th rowspan="2">${_("Aeg")}</th>
          <th rowspan="2">${_("id")}</th>
        </tr>
        <tr>
          <th>${_("Kokku")}</th>
          <th>${_("Arvuti")}</th>
          <th>${_("Käsitsi")}</th>
          <th>${_("Kokku")}</th>
          <th>${_("Arvuti")}</th>
          <th>${_("Käsitsi")}</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>${h.fstr(yv.toorpunktid)}</td>
          <td>${h.fstr(yv.toorpunktid_arvuti)}</td>
          <td>${h.fstr(yv.toorpunktid_kasitsi)}</td>
          <td>${yv.get_tulemus()}</td>
          <td>${h.fstr(yv.pallid_arvuti)}</td>
          <td>${h.fstr(yv.pallid_kasitsi)}</td>
          <td>${h.sbool(yv.loplik)}</td>
          <td>${yv.oigete_arv}</td>
          <td>${yv.valede_arv}</td>
          <td>${yv.valimata_valede_arv}</td>
          <td>${yv.valimata_oigete_arv}</td>
          <td>${h.fstr(yv.oigete_suhe)}</td>
          <td>${h.sbool(yv.vastuseta)}</td>
          <td>${h.sbool(not yv.mittekasitsi)}</td>
          <td>${h.str_from_time_sec(yv.ajakulu)}</td>
          <td>
            yv${c.ylesandevastus.id} vy${c.vy.id}
            % if c.vy.hindamiskogum_id:
            vyhk${c.vy.hindamiskogum_id}
            % endif
            <br/>
            ty${c.ty.id} tyhk${c.ty.hindamiskogum_id}
            % if yv.kehtiv and not yv.muudetav:
            (${_("kinnitatud")})
            % elif yv.kehtiv and yv.muudetav:
            (${_("pooleli")})
            % elif not yv.kehtiv:
            (${_("kehtetu")})
            % endif
          </td>
        </tr>
      </tbody>
    </table>
</%def>

<%def name="tbl_sp(yv, ty, vy, ylesanne)">    
    <table  class="table table-borderless table-striped">
      <thead>
        <tr>
          <th>${_("Sisuplokk")}</th>
          <th>${_("Küsimus")}</th>
          <th>${_("Toorpunktid")}</th>
          <th>${_("Pallid")}</th>
          <th>${_("Vastus")}</th>
          <th>${_("Õige/vale")}</th>
          <th>${_("Vastuse toorpunktid")}</th>
          <th>${_("Vastuseta")}</th>
          <th>${_("Arvutihinnatud")}</th>          
          <th>${_("Õiged")}</th>
          <th>${_("Valed")}</th>
          <th>${_("id")}</th>
        </tr>
      </thead>
      <tbody>
    % for sp in ylesanne.sisuplokid:
    <%
      data = []
      sp_rows = 0
      for k in sp.kysimused:
         if k.kood:
            kv = c.ylesandevastus.get_kysimusevastus(k.id) 
            kvsisud = kv and list(kv.kvsisud) or []
            k_rows = len(kvsisud) or 1
            kdata = (k, k.tulemus, kv, kvsisud, k_rows)
            data.append(kdata)
            sp_rows += k_rows
    %>
    % for ind, (k, tulemus, kv, kvsisud, k_rows) in enumerate(data):
    <tr>
      % if ind == 0:
      <td rowspan="${sp_rows}">${sp.tahis} ${sp.tyyp_nimi}</td>
      % endif
      <td rowspan="${k_rows}">
        ${k.kood}
      </td>
      <td rowspan="${k_rows}">
        % if kv and kv.toorpunktid is not None:
        ${h.fstr(kv.toorpunktid)}p
        % endif
        % if kv and kv.nullipohj_kood:
        (${kv.nullipohj_kood})
        % endif
        % if tulemus:
        ${h.fstr(tulemus.get_max_pallid())}-st
        % endif
      </td>
      <td rowspan="${k_rows}">
        % if kv and kv.pallid is not None:
        ${h.fstr(kv.pallid)}p
        % endif
        % if k.ei_arvesta:
        (ei arvesta)
        % endif
      </td>
      % if not kvsisud:
      <td></td>
      <td></td>
      <td></td>
      <td>${h.sbool(kv and kv.vastuseta)}</td>
      <td>${h.sbool(kv and kv.arvutihinnatud)}</td>
      <td>${kv and kv.oigete_arv or ''}</td>
      <td>${kv and kv.valede_arv or ''}</td>
      <td>(k${k.id} ${kv and ' kv%s' % kv.id or ''})</td>
      % else:
      % for ind1, ks in enumerate(kvsisud):
      ${ind1 > 0 and '</tr><tr>' or ''}
      <td>${ks.as_string(False)}</td>
      <td>${ks.oige}</td>
      <td>
        ${h.fstr(ks.toorpunktid)}
      </td>
      <td>${h.sbool(kv.vastuseta)}</td>
      <td>${h.sbool(kv.arvutihinnatud)}</td>
      <td>${kv.oigete_arv}</td>
      <td>${kv.valede_arv}</td>
      <td>
        sp${sp.id} k${k.id} kv${kv.id} ks${ks.id} seq${ks.seq}
        % if ks.hindamismaatriks_id:
        hm${ks.hindamismaatriks_id}
        % endif
      </td>
       % endfor
       % endif
    </tr>
    % endfor
    % endfor
      </tbody>
    </table>
</%def>

<%def name="tbl_aspektid(yv, ty, vy, ylesanne)">    
    <% aspektid = list(ylesanne.hindamisaspektid) %>
    % if aspektid:
    <table  class="table table-borderless table-striped">
      <thead>
        <tr>
          <th>${_("Kood")}</th>
          <th>${_("Hindamisaspekt")}</th>
          <th>${_("Toorpunktid")}</th>
          <th>${_("Pallid")}</th>
          <th>${_("id")}</th>
        </tr>
      </thead>
      <tbody>
    % for ha in ylesanne.hindamisaspektid:
    <%
      va = c.ylesandevastus.get_vastusaspekt(ha.id)
    %>
    <tr>
      <td>${ha.aspekt_kood}</td>
      <td>${ha.aspekt_nimi}</td>
      <td>
        % if va:
        ${h.fstr(va.toorpunktid)}
        % if va.nullipohj_kood:
        (${va.nullipohj_kood})
        % endif
        % endif
      </td>
      <td>${va and h.fstr(va.pallid)}</td>
      <td>ha${ha.id}
        % if va:
        va${va.id}
        % endif
      </td>
    </tr>
    % endfor
      </tbody>
    </table>
    % endif
</%def>

<%def name="tbl_yhinded(yv, ty, vy, ylesanne)">    
    <% yhinded = list(yv.ylesandehinded) %>
    % if yhinded:
    <table  class="table table-borderless table-striped">
      <thead>
        <tr>
          <th>${_("Toorpunktid")}</th>
          <th>${_("Pallid")}</th>
          <th>${_("Hindaja")}</th>
          <th>${_("Hindamise liik")}</th>
          <th>${_("Hindamise olek")}</th>
          % if c.testiosa.vastvorm_kood == const.VASTVORM_KP:
          <th>${_("Sisestus")}</th>
          % endif
          <th>${_("id")}</th>
        </tr>
      </thead>
      <tbody>
        % for yhinne in yhinded:
        <%
          hindamine = yhinne.hindamine
          hkasutaja = hindamine.hindaja_kasutaja
        %>
        <tr>
          <td>
            ${h.fstr(yhinne.toorpunktid)}
            % if yv.toorpunktid_arvuti:
            (${h.fstr(yhinne.toorpunktid_kasitsi)} + ${h.fstr(yv.toorpunktid_arvuti)})
            % endif
          </td>
          <td>
            ${h.fstr(yhinne.pallid)}
            % if yv.pallid_arvuti:
            (${h.fstr(yhinne.pallid_kasitsi)} + ${h.fstr(yv.pallid_arvuti)})
            % endif
          </td>
          <td>
            % if hkasutaja:
            ${hkasutaja.nimi}
            % endif
          </td>
          <td>${hindamine.liik}</td>
          <td>
            ${hindamine.staatus_nimi}
            % if hindamine.tyhistatud:
            (tühistatud)
            % endif
          </td>
          % if c.testiosa.vastvorm_kood == const.VASTVORM_KP:
          <td>${yhinne.sisestus}</td>
          % endif
          <td>yh${yhinne.id}</td>
        </tr>
        % endfor
      </tbody>
    </table>
    % endif
</%def>

