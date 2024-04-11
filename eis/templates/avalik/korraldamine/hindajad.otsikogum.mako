<%inherit file="/common/dlgpage.mako"/>

${h.form_search(id='form_otsikogum')}
${h.hidden('sub', 'otsihindaja')}
${h.hidden('valimis', c.valimis and 1 or '')}
<div class="d-flex m-2">
  ${h.flb(_("Keel"), 'lang', 'mr-3')}
  <div>
    <%
      opt_k = c.testimiskord.opt_keeled
      mkh = c.toimumisaeg.muu_koha_hindamine(c.valimis)
      if not mkh:
         # leiame minu soorituskohas kasutusel olevad keeled
         dik = c.toimumisaeg.get_sooritajatearvud(c.testikoht.id, valimis=c.valimis)
         opt_k2 = [r for r in opt_k if dik.get(r[0])]
         if opt_k2:
            opt_k = opt_k2
    %>
    % if len(opt_k) == 1:
    ${opt_k[0][1]}
    ${h.hidden('lang', opt_k[0][0])}
    % else:
    ${h.select('lang', None, c.testimiskord.opt_keeled, wide=False)}
    % endif
  </div>
</div>

<%
  if c.valimis:
     voib1 = c.toimumisaeg.hindaja1_maaraja_valim in const.MAARAJA_KOHAD or \
             c.toimumisaeg.hindaja1_maaraja_valim in const.MAARAJA_KOHAD
     voib2 = c.toimumisaeg.hindaja2_maaraja_valim in const.MAARAJA_KOHAD
  else:
     voib1 = c.toimumisaeg.hindaja1_maaraja in const.MAARAJA_KOHAD or \
             c.toimumisaeg.hindaja1_maaraja in const.MAARAJA_KOHAD
     voib2 = c.toimumisaeg.hindaja2_maaraja in const.MAARAJA_KOHAD

  hindamiskogumid = []
  for hk in c.toimumisaeg.testiosa.hindamiskogumid:
     if hk.staatus and not hk.arvutihinnatav:
        if voib1 or (voib2 and hk.kahekordne_hindamine and not c.valimis) or\
              (voib2 and hk.kahekordne_hindamine_valim and c.valimis):
           hindamiskogumid.append(hk) 
  if len(hindamiskogumid) == 1 and not c.hk_id:
     c.hk_id = hindamiskogumid[0].id
%>

% if not hindamiskogumid and voib2 and not voib1:
${h.alert_error(_("Selles testiosas pole kahekordse hindamisega hindamiskogumeid"), False)}
% elif not hindamiskogumid:
${h.alert_error(_("Selles testiosas pole hindamiskogumeid, millele saaks hindajaid määrata"), False)}
% else:
<table width="100%"  class="table table-borderless table-striped">
  <col width="50px"/>
  <thead>
  <tr>
    <th>${h.checkbox('all_hk', 1, onclick="toggle_all()", title=_("Vali kõik"))}</th>
    <th>${_("Hindamiskogum")}</th>
  </tr>
  </thead>
  <tbody>
  % for rcd in hindamiskogumid:
  <tr>
    <td>
      <% hk_cls = rcd.paarishindamine and 'hk2' or 'hk1' %>
      ${h.checkbox('hk_id', rcd.id, checkedif=c.hk_id, class_='hkid %s' % hk_cls, title=_("Vali rida {s}").format(s=rcd.tahis))}
    </td>
    <td>${rcd.tahis}</td>
  </tr>
  % endfor
  </tbody>
</table>
<div class="chosen-hk" style="display:none">
  ${h.submit_dlg(_("Vali"))}
</div>
% endif
${h.end_form()}


<script>
var choose_k = function(fld)
{
  if(fld)
  {
    if($(fld).hasClass('hk1')) $('.hk2').prop('checked', false); 
    else if($(fld).hasClass('hk2')) $('.hk1').prop('checked', false);
  }
  $('.chosen-hk').toggle($('form#form_otsikogum input.hkid:checked').length>0);
}
var toggle_all = function()
{
  var checked = $('input[name="all_hk"]').prop('checked');
  var flt = ($('.hk2:checked').length > 0 ? '.hk2' : '.hk1');
  $('.hk1,.hk2').prop('checked', false);
  $(flt).prop('checked', checked);
  choose_k();
}
$('input.hkid').click(function(){ choose_k(this); });
$('input.hkid:checked').each(function(){ choose_k(this); });
</script>

