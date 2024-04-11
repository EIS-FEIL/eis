## -*- coding: utf-8 -*- 
<table cellpadding="0" cellspacing="0" width="100%"><tr><td>
${h.pager(c.items)}
</td><td align="right">
% if c.eksam_kaib:
${_("Vastamise ajal hindamine")}
% else:
${_("Helisalvestiselt hindamine")}
% endif
</td></tr></table>

% if c.items:
<table width="100%" class="table table-borderless table-striped" border="0" >
  <thead>
    <tr>
      <th></th>
      ${h.th_sort('sooritus.tahis', _("Tähis"))}
      ${h.th_sort('kasutaja.nimi', _("Sooritaja"))}
      ${h.th_sort('sooritus.staatus', _("Vastamise olek"))}
      ${h.th_sort('hindamisolek.staatus', _("Hindamise olek"))}
      ${h.th_sort('hindamisolek.selgitus', _("Hindamisprobleem"))}
      % if c.show_hindamiskogum:
      ${h.th_sort('hindamisolek.hindamiskogum_id', _("Hindamiskogum"))}
      % endif
      ${h.th(_("Minu hindamine"))}
      ${h.th(_("Eritingimus"))}
      ${h.th_sort('sooritus.kavaaeg', _("Kavandatud algus"))}
      ${h.th_sort('sooritus.algus', _("Tegelik algus"))}
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(c.items):
    <% 
       tos, holek = rcd
       k = tos.sooritaja.kasutaja
       hindamine = holek.get_hindamine(c.labiviija.liik)
    %>
    <tr>
      <td>
        % if c.eksam_kaib:
        ${h.checkbox('sooritus_id', tos.id, class_="nosave sooritus", title=_("Vali rida {s}").format(s=k.nimi),
        checked=hindamine and hindamine.staatus==const.S_STAATUS_POOLELI)}
        % elif tos.staatus == const.S_STAATUS_TEHTUD and tos.hindamine_staatus != const.H_STAATUS_HINNATUD and holek.hindamisprobleem != const.H_PROBLEEM_TOOPUUDU:
        ${h.checkbox('sooritus_id', tos.id, class_="nosave sooritus", title=_("Vali rida {s}").format(s=k.nimi))}
        % endif
      </td>
      <td>${tos.tahis}</td>
      <td>
        ${k.isikukood} ${k.nimi}
      </td>
      <td>
        ${tos.staatus_nimi}
      </td>
      <td>
        ${holek.staatus_nimi}
      </td>
      <td>
        ${holek.selgitus}
      </td>
      % if c.show_hindamiskogum:
      <td>${holek.hindamiskogum.tahis}</td>
      % endif
      <td>
        % if hindamine:
        % if hindamine.staatus == const.H_STAATUS_HINNATUD:
        ${h.fstr(hindamine.pallid)}p
        % else:
        ${hindamine.staatus_nimi}
        % endif
        % endif
      </td>
      <td>
            <% erivajadused = tos.get_str_erivajadused() %>
            % if erivajadused:
            <% buf = h.literal(erivajadused.replace("'"," ").replace('\n',' ')) %>
            <a onclick="alert_dialog('${buf}', '${_("Eritingimused")}')" class="menu1">
              ${_("Eritingimused")}
            </a>
            % endif
      </td>
      <td>
        % if tos.kavaaeg:
        ${h.str_from_datetime(tos.kavaaeg)}
        % endif
      </td>
      <td>
        % if tos.algus:
        ${h.str_from_datetime(tos.algus)}
        % endif
      </td>
    </tr>
    % endfor
  </tbody>
</table>
% endif

<script>
function toggle_valikuline()
{
  var flds = $('input.sooritus:checked');
  $('.valikuline').hide();                     
  if(flds.length > 0)
  {
      var clist = '.vst-all';
      $('.valikuline').filter(clist).show();
  }
}
$(function(){
  $('input.sooritus').click(toggle_valikuline);                                  
  toggle_valikuline();
});
</script>
