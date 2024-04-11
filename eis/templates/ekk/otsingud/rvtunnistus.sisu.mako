<%
   c.tunnistus = c.item.tunnistus
   c.rveksam = c.item.rveksam
   c.kasutaja = c.tunnistus.kasutaja
   c.sooritaja = c.item.sooritaja
%>
<table colspacing="0" cellpadding="0" width="100%">
  <tr>
    <td>
      <h1>${c.rveksam.nimi}</h1>
    </td>
    <td align="right">
      % if c.sooritaja:
      ${_("Sooritatud test")} ${c.sooritaja.test_id}
      % endif
    </td>
  </tr>
</table>
<table width="100%" class="form border tbl-sisestamine"  cellpadding="4">
  <col width="150px"/>
  <tbody>
    <tr>
       <td class="fh">${_("Sooritaja isikukood")}</td>
       <td>${c.kasutaja.isikukood}</td>
    </tr>
    <tr>
      <td class="fh">${_("Sooritaja eesnimi")}</td>
      <td>${c.tunnistus.eesnimi}</td>
    </tr>
    <tr>
      <td class="fh">${_("Sooritaja perekonnanimi")}</td>
      <td>${c.tunnistus.perenimi}</td>
    </tr>
  </tbody>
</table>
<br/>

<table width="100%" class="form border tbl-sisestamine"  cellpadding="4">
  <col width="150px"/>
  <col/>
  <tbody>
    <% 
       on_tase = c.rveksam.keeletase_kood
       if not on_tase:
          for r in c.rveksam.rveksamitulemused:
              on_tase = r.keeletase_kood
              if on_tase:
                 break
    %>
    % if on_tase or c.item.keeletase_kood:
    <tr>
      <td class="fh">${_("Keeleoskuse tase")}</td>
      <td colspan=2>
        ${c.item.keeletase_kood or _("puudub")}
      </td>
    </tr>
    % endif

    % if c.rveksam.on_tunnistusenr:
    <tr>
      <td class="fh">${_("Tunnistuse nr")}</td>
      <td colspan=2>${c.tunnistus.tunnistusenr}</td>
    </tr>
    % endif

    <tr>
      <td class="fh">${_("Väljastatud")}</td>
      <td colspan=2 nowrap>
        ${h.str_from_date(c.tunnistus.valjastamisaeg)}
      </td>
    </tr>

    % if c.rveksam.on_kehtivusaeg:
    <tr>
      <td class="fh">${_("Kehtib kuni")}</td>
      <td colspan=2 nowrap>
        ${h.str_from_date(c.item.kehtib_kuni)}
      </td>
    </tr>
    % endif

    <tr>
      <td class="fh">
        ${_("Tulemus")}
      </td>

      <% vr = c.item.rveksamitulemus %>

      % if c.rveksam.on_arvtulemus:
        % if vr:
        <td width="120px">
        % else:
        <td>
        % endif

        % if c.item.tulemus is not None:
         % if c.rveksam.kuni:
         ${h.fstr(c.item.tulemus)}/${h.fstr(c.rveksam.kuni)}
         % else:
         ${h.fstr(c.item.tulemus)}
         % endif

         % if c.rveksam.tulemusviis == model.Rveksam.TULEMUSVIIS_PALL:
         ${_("palli")}
         % elif c.rveksam.tulemusviis == model.Rveksam.TULEMUSVIIS_PROTSENT:
         ${'%'}
         % endif
        % endif
      </td>
      % endif

      % if vr:
      <td>
        ${vr.tahis}
           % if vr.alates or vr.kuni:
            ${h.fstr(vr.alates)}-${h.fstr(vr.kuni)}
           % endif
        % if vr.keeletase_kood != vr.tahis:
        ${vr.keeletase_kood}
        % endif
      </td>
      % endif

    </tr>

    <tr>
      <td class="fh"></td>
      <td colspan=2>
        % if c.item.arvest_lopetamisel:
        ${_("Arvestatakse lõpetamise tingimusena")}
        % else:
        ${_("Ei arvestata lõpetamise tingimusena")}    
        % endif
      </td>
    </tr>

  </tbody>
</table>
<br/>

% if len(c.rveksam.rvosaoskused):
## and c.rveksam.on_osaoskused_tunnistusel:
<table width="100%" class="form border tbl-sisestamine"  cellpadding="4">
  <caption>
  % if c.rveksam.on_osaoskused_tunnistusel and c.rveksam.on_osaoskused_sooritusteatel:
  ${_("Tunnistusel ja sooritusteatel märgitud osaoskused")}
  % elif c.rveksam.on_osaoskused_tunnistusel:
  ${_("Tunnistusel märgitud osaoskused")}
  % elif c.rveksam.on_osaoskused_sooritusteatel:
  ${_("Sooritusteatel märgitud osaoskused")}
  % else:
  ${_("Osaoskused")}
  % endif
  </caption>
  <col width="150px"/>
  <tbody>
    % for n, osa in enumerate(c.rveksam.rvosaoskused):
    <% 
       rvs = c.item.get_rvsooritus(osa.id) or c.new_item()
       vr = rvs.rvosatulemus
    %>
    <tr>
       <td class="fh">${osa.nimi}
       </td>

      % if c.rveksam and rvs.tulemus is not None:
       % if vr or c.rveksam.on_osaoskused_jahei:
       <td width="120px">
       % else:
       <td>
       % endif

        % if osa.kuni:
        ${h.fstr(rvs.tulemus)}/${h.fstr(osa.kuni)}
        % else:
        ${h.fstr(rvs.tulemus)}
        % endif

        % if c.rveksam.tulemusviis == model.Rveksam.TULEMUSVIIS_PALL:
       ${_("palli")}
        % elif c.rveksam.tulemusviis == model.Rveksam.TULEMUSVIIS_PROTSENT:
       ${'%'}
        % endif
      </td>
      % endif

      % if vr:
      <td>
        ${vr.tahis}
           % if vr.alates or vr.kuni:
            ${h.fstr(vr.alates)}-${h.fstr(vr.kuni)}
           % endif
      </td>
      % endif

      % if c.rveksam.on_osaoskused_jahei:
      <td>
        % if rvs.on_labinud:
        ${_("Vastab tasemele")}
        % else:
        ${_("Ei vasta tasemele")}
        % endif
      </td>
      % endif
    </tr>
    % endfor
  </tbody>
</table>
<br/>

% endif
