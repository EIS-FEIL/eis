${h.form_search(url=h.url_current('index'), id='form_otsikogum')}
${h.hidden('sub', 'otsihindaja')}
${h.hidden('valimis', c.valimis and 1 or '')}
<% ch = h.colHelper('col-md-6','col-md-6') %>
<div class="p-3 border">
<div class="form-group row">
  ${ch.flb(_("Planeeritav hinnatavate soorituste arv"))}
  <div class="col">
  <% sooritajate_arv = c.toimumisaeg.get_sooritajatearv() %>
  ${h.posint5('planeeritud_toode_arv', '', maxvalue=sooritajate_arv)}
  </div>
</div>
<div class="form-group row">
  ${ch.flb(_("Keel"))}
  <div class="col">
    ${h.select('lang', None,
    c.toimumisaeg.testimiskord.opt_keeled)}
  </div>
</div>
</div>

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
var flt = (($('.hk2:checked').length > 0 || $('.hk1').length == 0) ? '.hk2' : '.hk1');
$('.hk1,.hk2').prop('checked', false);
$(flt).prop('checked', checked);
choose_k();
}
</script>

<%
  testiosa = c.toimumisaeg.testiosa
  hindamiskogumid = list(testiosa.hindamiskogumid)
%>
% if not hindamiskogumid:
${h.alert_notice(_("Hindamiskogumeid pole"), False)}
% else:
<table width="100%"  class="table table-borderless table-striped">
  <caption>${_("Vali hindamiskogum")}</caption>
  <tr>
    <th width="50px">${h.checkbox('all_hk', 1, onclick="toggle_all()", title=_("Vali kõik"))}</th>
    <th>${_("Tähis")}</th>
    <th>${_("Nimetus")}</th>
    <th>${_("Hindamise liik")}</th>
    <th>${_("Paarishindamine")}</th>
  </tr>
  % for rcd in hindamiskogumid:
  <tr>
    <td>
      % if rcd.staatus == const.B_STAATUS_KEHTETU:
      ${_("Ülesanneteta")}
      % elif rcd.arvutihinnatav and testiosa.vastvorm_kood in (const.VASTVORM_KE, const.VASTVORM_SE, const.VASTVORM_I):
      ${_("Arvutihinnatav")}
      % else:
      <% hk_cls = rcd.paarishindamine and 'hk2' or 'hk1' %>
      ${h.checkbox('hk_id', rcd.id, onclick="choose_k(this)", class_='hkid %s' % hk_cls, title=_("Vali rida {s}").format(s=rcd.tahis))}
      % endif
    </td>
    <td>${rcd.tahis}</td>
    <td>${rcd.nimi}</td>
    <td>${rcd.hindamine_nimi}</td>
    <td>${h.sbool(rcd.paarishindamine)}</td>
  </tr>
  % endfor
</table>
<div class="chosen-hk text-right" style="display:none">
  ${h.submit_dlg(_("Vali"))}
</div>
% endif
${h.end_form()}
