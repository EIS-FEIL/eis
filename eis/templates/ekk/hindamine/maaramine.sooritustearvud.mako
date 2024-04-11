<%
      if c.testimiskord.sisaldab_valimit:
         valimis_values = [False, True]
      else:
         valimis_values = [None]
%>
<table width="100%"  class="table">
% for ind, valimis in enumerate(valimis_values):
  <tr>
    <td class="frh">
      % if valimis:
      ${_("Valimi registreeritute arv")}
      % elif valimis == False:
      ${_("Mitte-valimi registreeritute arv")}
      % else:
      ${_("Registreeritute arv")}
      % endif
    </td>
    <td width="70px">
      <span class="brown">
        ${c.sooritajatearvud[valimis]['total']}
      </span>
    </td>
    <td class="frh">${_("Hinnatavate testisoorituste arv")}</td>
    <td width="70px">
      <span class="brown">
        ${c.hinnataarvud[valimis]['total']}
      </span>
    </td>
    <td class="frh">
      % if c.hindamiskogum and ind == 0:
      ${_("Hindamiskogum")} ${c.hindamiskogum.tahis}
      % endif
    </td>
    % if c.planeeritudarvud:
    <td class="frh">${_("Kokku hindajate poolt planeeritud hinnata")}</td>
    <td width="70px">
      <span class="brown">
        ${c.planeeritudarvud[valimis]['total']}
      </span>
    </td>
    % else:
    <td class="frh"></td>
    % endif
  </tr>
  % for lang in c.toimumisaeg.testimiskord.get_keeled():
  <tr>
    <td class="frh">${model.Klrida.get_lang_nimi(lang)}</td>
    <td><span class="brown">${c.sooritajatearvud[valimis].get(lang)}</span></td>
    <td class="frh">${model.Klrida.get_lang_nimi(lang)}</td>
    <td><span class="brown">${c.hinnataarvud[valimis].get(lang)}</span></td>
    <td class="frh">
      % if ind == 0 and c.hindamiskogum and c.hinnataarvud[valimis].get(lang):
      % if c.testiosa.vastvorm_kood in (const.VASTVORM_KE, const.VASTVORM_SE, const.VASTVORM_I, const.VASTVORM_KP):
      ${h.btn_to(_("Hindaja eelvaade"), h.url('hindamine_hindajavaade_hkhindamised', toimumisaeg_id=c.toimumisaeg.id, hindaja_id='hk%d' % c.hindamiskogum.id, sooritus_id=0, lang=lang))}
      ##% elif c.testiosa.vastvorm_kood == const.VASTVORM_SH:
      ##${h.btn_to(_("Hindaja eelvaade"), h.url('hindamine_hindajavaade_shindamised', toimumisaeg_id=c.toimumisaeg.id, hindaja_id='hk%d' % c.hindamiskogum.id, sooritus_id=0, lang=lang))}      
      % endif
      % endif
    </td>
    % if c.planeeritudarvud.get(valimis):
    <td class="frh">${model.Klrida.get_lang_nimi(lang)}</td>
    <td><span class="brown">${c.planeeritudarvud[valimis].get(lang)}</span></td>
    % else:
    <td class="frh"></td>
    % endif
  </tr>
  % endfor
% endfor
</table>
