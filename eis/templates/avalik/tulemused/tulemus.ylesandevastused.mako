## ylesannete vastused (debuginfo)

${self.debug_ylesandevastused()}

<%def name="debug_ylesandevastused()">
<div class="p-2">
  <div class="text-right">
    ${h.link_to(_("Registreering"), h.url('regamine', id=c.item.id))}
  </div>

% for tos in c.item.sooritused:
<% testiosa = tos.testiosa %>
<div class="d-flex flex-wrap mt-3">
  <div class="flex-grow-1 h4">${testiosa.nimi}</div>

  % if c.is_devel and c.item.test.testiliik_kood == const.TESTILIIK_KOOLIPSYH:
  ${h.link_to(_("Profiilileht"), h.url('muud_pstulemus', id=tos.id), class_="mr-3")}
  % endif

  ${self.logilink_osa(tos, testiosa)}
</div>
${self.yvastused_index(tos, testiosa)}
${self.helivastused(tos)}

${self.debug_hindamisolekud(tos)}
% if testiosa.on_alatestid:
${self.debug_komplektid(tos)}
% endif

<%
  c.npvastused = list(tos.npvastused)
  on_np = c.npvastused or list(testiosa.normipunktid)
%>
% if on_np:
<% c.nptos = tos %>
<%include file="tulemus.npvastused.mako"/>
% endif

<div class="small">
  <div>
    <%
      testityyp = c.item.test.testityyp
      tyybid = {const.TESTITYYP_AVALIK: _("Avaliku vaate test"),
                const.TESTITYYP_EKK: _("EKK test"),
                const.TESTITYYP_TOO: _("Jagatud töö"),
                }
    %>
    ${tyybid.get(testityyp) or _("Test")}
    ${c.item.test_id} ${_("Sooritaja")} ${tos.sooritaja_id}
  </div>
  <div>
    ${_("Testiosa")} ${tos.testiosa_id}
    % if tos.toimumisaeg_id:
    ${_("Toimumisaeg")} ${tos.toimumisaeg_id}
    % endif
    ${_("Sooritus")} ${tos.id}
    <%
      lv = tos.intervjuu_labiviija
      lvk = lv and lv.kasutaja
    %>
    % if lvk:
    ${_("Intervjueerija")} ${lvk.nimi}
    % endif
    (${tos.hindamiskogumita and _("hindamiskogumita hindamine") or 'hindamine'}:
    ${tos.hindamine_staatus_nimi})
  </div>
  % if tos.ylesanneteta_tulemus:
  <div>${_("Tulemust ei arvutata, sest see on sisestatud toimumise protokollile")}</div>
  % endif

</div>
<div class="small">
  % if c.item.esitaja_kasutaja_id:
  ${_("Sooritamiseks suunanud")} ${c.item.esitaja_kasutaja.nimi}
  % endif
  % if c.item.esitaja_koht_id:
  ${c.item.esitaja_koht.nimi}
  % endif
  % if c.item.nimekiri_id:
  ${_("nimekiri")} ${c.item.nimekiri_id}
  "${c.item.nimekiri.nimi}"
  % endif
  % if c.item.opetajatest:
  (${_("õpetaja test")})
  % endif
  % if c.item.klaster_id:
  <br/>${_("Sooritamise klaster")} ${model.Klaster.get_host(c.item.klaster_id)}
  % endif
</div>
<div class="m-2 mb-3">
% if on_np:
${h.btn_to(_('Arvuta normipunktid uuesti'), h.url_current('update', sub='arvuta', sooritus_id=tos.id), method='post', level=2)}
% endif
${h.btn_to(_('Arvuta testiosa tulemused uuesti'), h.url_current('update', sub='arvuta', sooritus_id=tos.id, force=1), method='post', level=2)}
</div>
% endfor
<script>
  $(function(){
  $('a.yv-title').click(function(){
  var detail = $(this).siblings('.yv-detail');
  if(detail.is(':empty')){ dialog_load(this.href, '', 'GET', detail); }
  else { detail.toggle(); };
  return false;
  });
  });
</script>
</div>
</%def>

<%def name="logilink_osa(tos, testiosa)">
<%
 ik = kasutaja = None
 if testiosa.vastvorm_kood in (const.VASTVORM_KE, const.VASTVORM_SE):
    kasutaja = tos.tugiisik_kasutaja or c.item.kasutaja
 elif testiosa.vastvorm_kood == const.VASTVORM_I:
    lv = tos.intervjuu_labiviija
    kasutaja = lv and lv.kasutaja
  
 if kasutaja:
    ik = kasutaja.isikukood
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
  ${h.link_to(_("Logi"), h.url('admin_logi', isikukood=ik, alates=alates, alates_kell=alates_kell, kuni=kuni, kuni_kell=kuni_kell, psize=100, show_request=1), class_="pr-3")}
% endif
</%def>

<%def name="yvastused_index(tos, testiosa)">
<%
  on_diag = testiosa.test.diagnoosiv
  tos_yvastused = [(yv, yv.valitudylesanne, yv.testiylesanne) for yv in tos.ylesandevastused]
%>
% for alatest in testiosa.alatestid or [None]:
<div class="py-2">
  % if alatest:
  <% atos = tos.get_alatestisooritus(alatest.id) %>
  <div class="mt-2 h5">${_("Alatest")} ${alatest.seq} ${alatest.nimi}</div>
  % if atos:
  <small>(a${alatest.id} as${atos.id})
    % if atos.staatus in  (const.S_STAATUS_POOLELI, const.S_STAATUS_KATKESTATUD):
    <%
      vvy_id = atos.viimane_valitudylesanne_id
      vy = vvy_id and model.Valitudylesanne.get(vvy_id) or None
    %>
    % if vy:
    ${_("viimane ül {id}").format(id=vy.ylesanne_id)}
    % endif
    % endif
  </small>
  % endif
  % endif

<%
  yvastused = []
  if alatest:
      li = [(yv, vy, ty) for (yv, vy, ty) in tos_yvastused if ty.alatest_id == alatest.id]
      valikujrk = atos and atos.valikujrk
  else:
      li = tos_yvastused
      valikujrk = tos.valikujrk
  for yv, vy, ty in li:
      if vy:
          segamisjrk = valikujrk and valikujrk.index(ty.id)
          sort_key = on_diag and yv.created or (ty.alatest_seq or 0, ty.seq, yv.created, segamisjrk)
          jrk = (sort_key, ty.alatest_seq, ty.seq, vy.seq)
          yvastused.append((jrk, yv, vy, ty, segamisjrk))
  yvastused = sorted(yvastused, key=lambda r: r[0])
%>
% for r in yvastused:
<%
  yv, vy, ty, segamisjrk = r[1:] 
  ylesanne = vy and vy.ylesanne or None
%>
% if ylesanne:
<div>
  <a class="yv-title" href="${h.url_current('show', id=c.item.id, sub='yv', yv_id=yv.id)}">
    ${ty.tahis}
    % if segamisjrk or segamisjrk == 0:
    (${segamisjrk + 1})
    % endif
    % if ty.nimi != ty.tahis:
    ${ty.nimi}
    % endif
    ${_("Ülesanne")} ${ylesanne.id}
    % if yv:
    ${yv.get_tulemus()}
    % endif
  </a>
  <div class="yv-detail"></div>
</div>
% endif
% endfor
</div>
% endfor
</%def>

<%def name="helivastused(tos)">
<% helivastused = list(tos.helivastused) %>
% if helivastused:
<div class="mt-2 h4">${_("Helivastused")}</div>
<table class="table mb-2">
  <thead>
    <tr>
      ${h.th(_("Helifail"))}
      ${h.th(_("Faili suurus"))}
      ${h.th(_("Aeg"))}
      ${h.th(_("Ülesanne"))}
      ${h.th(_("Sooritajad"))}
    </tr>
  </thead>
  <tbody>
    % for hv in helivastused:
    <% hvf = hv.helivastusfail %>
    <tr>
      <td>
        <% url = h.url_current('downloadfile', file_id=f'hvf-{hvf.id}', format=hvf.fileext) %>
        ${h.link_to(hvf.filename, url)}
      </td>
      <td>${h.filesize(hvf.filesize)}</td>
      <td>${h.str_from_datetime(hvf.created, True)}</td>
      <td>
        <% ty = hv.testiylesanne %>
        % if ty:
        ${ty.tahis}
        % endif
        % if hv.ylesanne_id:
        (${hv.ylesanne_id})
        % endif
      </td>
      <td>
        % for hv2 in hvf.helivastused:
        ${hv2.sooritus.sooritaja.nimi}
        % endfor
      </td>
    </tr>
    % endfor
  </tbody>
</table>
% endif
</%def>

<%def name="debug_hindamisolekud(tos)">
<% on_lotv = tos.testiosa.lotv %>
<div class="h4 mt-2">Hindamiskogumid</div>
<table width="100%"  class="table table-striped table-align-top">
  <thead>
    <tr>
      <th>Hindamiskogum</th>
      <th>Hindamise staatus</th>
      <th>Hindamistase</th>
      <th>Hindamisprobleem</th>
      <th>Selgitus</th>
      <th>Puudus</th>
      <th>Käsitsi hinnatav</th>
      <th>Pallid</th>
      <th>Max</th>
      <th>Komplekt</th>      
      <th>Ülesanded</th>
      <th>Hindamised</th>
      <th>id</th>
    </tr>
  </thead>
  <tbody>
    % for holek in tos.hindamisolekud:
    <%
      hkogum = holek.hindamiskogum
      komplekt = holek.komplekt
    %>
    <tr>
      <td>
        % if hkogum:
        ${hkogum.tahis or _("(vaikimisi)")}
        % endif
      </td>
      <td>${holek.staatus_nimi}</td>
      <td>${holek.hindamistase}</td>
      <td>${holek.hindamisprobleem_nimi}</td>
      <td>${holek.selgitus}</td>
      <td>${h.sbool(holek.puudus)}</td>
      <td>${h.sbool(not holek.mittekasitsi)}</td>
      <td>${h.fstr(holek.pallid)}
        % if hkogum:
        % for kr in hkogum.hindamiskriteeriumid:
        <% krv = tos.get_kriteeriumivastus(kr.id) %>
          <div>${kr.aspekt_kood} - ${krv and h.fstr(krv.pallid)}</div>
        % endfor
        % endif
      </td>
      <td>
        % if hkogum:
        ${h.fstr(hkogum.max_pallid)}
        % endif
      </td>
      <td>${komplekt and komplekt.tahis}</td>
      % if hkogum:
      <td>
          % if hkogum.staatus:
            % if on_lotv:
              % for vy in hkogum.valitudylesanded:
                % if vy.komplekt_id == holek.komplekt_id:
                 ${vy.ylesanne_id} 
                % endif
              % endfor
            % else:
              % for ty in hkogum.testiylesanded:
                ${ty.tahis}
              % endfor
            % endif
          % endif
      </td>
      <td>
        % for hindamine in holek.hindamised:
        <div>
          ${self.holek_hindaja(hindamine)}
        </div>
        % endfor
      </td>
      % else:
      ## avaliku vaate hindamine hindamiskogumita
      <td colspan="2">
        % for hindamine in holek.hindamised:
        <div>
          <%
            tyy = []
            for yh in hindamine.ylesandehinded:
               vy = yh.valitudylesanne
               ty = vy.testiylesanne
               tyy.append(ty.tahis)
          %>
          ${' '.join(tyy)}
          ${self.holek_hindaja(hindamine)}
        </div>
        % endfor
      </td>
      % endif
      <td>
        ho${holek.id}
        % if hkogum:
        hk${hkogum.id}
        % endif
        k${holek.komplekt_id}
      </td>
    </tr>
    % endfor
  </tbody>
</table>
</%def>

<%def name="debug_komplektid(tos)">
<div class="h4 mt-2">Komplektid</div>
<table width="100%"  class="table table-striped table-align-top">
  <thead>
    <tr>
      <th>Alatestid</th>
      <th>Komplekt</th>
      <th>id</th>
    </tr>
  </thead>
  <tbody>
    % for sk in tos.soorituskomplektid:
    <%
      kv = sk.komplektivalik
      komplekt = sk.komplekt
    %>
    <tr>
      <td>
        % for a in kv.alatestid:
        ${a.seq}
        % endfor
      </td>
      <td>
        % if komplekt:
        ${komplekt.tahis}
        % endif
      </td>
      <td>
        kv${kv.id}
        k${sk.komplekt_id}
      </td>
    </tr>
    % endfor
  </tbody>
</table>
</%def>

<%def name="holek_hindaja(hindamine)">        
          ${hindamine.staatus_nimi}
          ${hindamine.liik_nimi}
          % if hindamine.hindaja_kasutaja_id:
          ${hindamine.hindaja_kasutaja.nimi}
          % endif
          % if hindamine.pallid:
          ${h.fstr(hindamine.pallid)}p
          % endif
          % if hindamine.tyhistatud:
          ${_("tühistatud")}
          % endif
          % if hindamine.loplik:
          ${_("lõplik")}
          % endif
          % if hindamine.sisestus == 2:
          (${_("sisestus 2")})
          % endif
          <small>lv${hindamine.labiviija_id} k${hindamine.hindaja_kasutaja_id} h${hindamine.id}</small>
</%def>
