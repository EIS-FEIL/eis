${h.form_save(c.item.id)}
${h.hidden('testiosa_id', c.item.testiosa.id)}

<h3>${_("Sisestuskogum")}</h3>
${h.rqexp()}
<div class="form-wrapper mb-3">
  <div class="form-group row">
    ${h.flb3(_("Tähis"))}
    <div class="col">
      ${h.text('f_tahis', c.item.tahis, size=10)}
    </div>
  </div>

  <div class="form-group row">
    ${h.flb3(_("Nimetus"), rq=True)}
    <div class="col">
      ${h.text('f_nimi', c.item.nimi)}
    </div>
  </div>
  
  <div class="form-group row">
    ${h.flb3(_("Hindamise liik"), rq=True)}
    <div class="col">
      ${h.select('f_hindamine_kood', c.item.hindamine_kood, c.opt.klread_kood('HINDAMINE'),
      onchange='change_hindamine()')}
    </div>
  </div>

  % if c.testiosa.vastvorm_kood in (const.VASTVORM_KP, const.VASTVORM_SP):
   % if c.testiosa.vastvorm_kood == const.VASTVORM_KP:
  <div class="form-group row">
    ${h.flb3(_("Skannimine"))}
    <div class="col">
      ${h.checkbox1('f_on_skannimine', True, checked=c.item.on_skannimine)}
    </div>
  </div>
   % endif
  <div class="form-group row">
    ${h.flb3(_("Sisestaja tasu"))}
    <div class="col">
      ${h.float5('f_tasu', c.item.tasu)} &euro;
    </div>
  </div>
   % if c.testiosa.vastvorm_kood == const.VASTVORM_KP:
  <div class="form-group row">
    ${h.flb3(_("Sisestamine hindamisprotokollilt"))}
    <div class="col">
      ${h.sbool(c.item.on_hindamisprotokoll)}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Sisestamine testitöölt"))}
    <div class="col">
      ${h.sbool(c.item.on_vastused)}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Tulemuse kuvamine"))}
    <div class="col">
      ${h.checkbox1('f_naita_pallid', True, checked=c.item.naita_pallid,
      label=_("Näita vastuste sisestamisel sisestuskogumi tulemust"))}
    </div>
  </div>
   % endif
  % endif
</div>
  
<table class="table form-border${c.is_edit and ' multipleselect' or ''} mb-3" >
  <caption>${_("Hindamiskogumid")}</caption>
  <thead>
  <tr>
    <th></th>
    <th>${_("Tähis")}</th>
    <th>${_("Nimetus")}</th>
    <th>${_("Hindamise liik")}</th>
  </tr>
  </thead>
  <tbody>
<% sk_komplektivalik = c.item.get_komplektivalik() %>
  % for rcd in c.testiosa.hindamiskogumid:
      % if c.is_edit or rcd.sisestuskogum_id == c.item.id:
         % if rcd.sisestuskogum_id == c.item.id:
        <tr class="selected">
         % else:
        <tr>
         % endif
          <td>
            % if not sk_komplektivalik or rcd.get_komplektivalik() == sk_komplektivalik:
            % if not rcd.sisestuskogum_id or rcd.sisestuskogum_id == c.item.id:
            ${h.checkbox('hk_id', rcd.id, 
            checked=rcd.sisestuskogum_id==c.item.id,
            class_=rcd.hindamine_kood==const.HINDAMINE_SUBJ and 'hsubj' or 'hobj')}
            % endif
            % endif
          </td>
          <td>${rcd.tahis}</td>
          <td>${rcd.nimi}</td>
          <td>${rcd.hindamine_nimi}</td>
        </tr>
      % endif
  % endfor
    </tbody>
</table>

<script>
function change_hindamine()
{
## sisestuskogumi ja selles olevate hindamiskogumite 
## hindamise liigid peavad olema samad
  if($('#f_hindamine_kood').val() == '${const.HINDAMINE_SUBJ}')
  {
     $('#hk_id.hsubj').removeProp('disabled');
     $('#hk_id.hobj').prop('disabled', true);
  }
  else
  {
     $('#hk_id.hobj').removeProp('disabled');
     $('#hk_id.hsubj').prop('disabled', true);
  }
}
$(document).ready(function(){
  change_hindamine();
});
</script>

% if c.item.id:  
<% 
   hindamiskogumid_id = [rcd.id for rcd in c.item.hindamiskogumid] + [None]
   c.ty_cnt = -1
   c.opt_sisestusviis = [(model.Testiylesanne.SISESTUSVIIS_PALLID, _("Toorpunktid")),
                         (model.Testiylesanne.SISESTUSVIIS_BOOL, _("Õige/vale")),
                         (model.Testiylesanne.SISESTUSVIIS_VASTUS, _("Vastus"))]
%>
<table width="100%" class="table" >
  <caption>${_("Testiülesanded")}</caption>
  <thead>
  <tr>
    ${h.th(_("Tähis hindamisprotokollil"))}
    ${h.th(_("Hindamiskogum"))}
    ${h.th(_("Alatest"))}
    ${h.th(_("Plokk"))}
    ${h.th(_("Tähis"))}
    ${h.th(_("Nimetus"))}
    ${h.th(_("Arvutihinnatav"))}
    ${h.th(_("Sisestusviis"))}
    ${h.th(_("Kursor hüppab valikväljalt ise edasi"))}
  </tr>
  </thead>
  <tbody>
     % for rcd in c.testiosa.testiylesanded:
        % if rcd.hindamiskogum_id in hindamiskogumid_id:
        ${self.row_testiylesanne(rcd)}
        % endif
     % endfor
  </tbody>
</table>
% endif

<p>
${_("Sisetuskogumite, hindamiskogumite ja testiülesannete omavaheliste seoste muutmise korral  tuleb arvestada, et tehtavad muutused võivad segamini paisata hindamisprotokollide sisestusmaatriksi.")}
</p>

${h.end_form()}

<%def name="row_testiylesanne(rcd)">
       % if c.item.id and rcd.hindamiskogum.sisestuskogum_id == c.item.id:

  <tr class="selected">
    <td>${rcd.tahis}</td>
       % else:
  <tr>
    <td></td>
       % endif
    <td>
      ${rcd.hindamiskogum.tahis}
    </td>
    <td>${rcd.alatest and rcd.alatest.nimi or ''}</td>
    <td>${rcd.testiplokk and rcd.testiplokk.nimi or ''}</td>
    <td>
      ${rcd.tahis}
    </td>
    <td>${rcd.nimi}</td>
    <td>${h.sbool(rcd.arvutihinnatav)}</td>
    <td>
      % if c.testiosa.vastvorm_kood == const.VASTVORM_KP:
      <%
         c.ty_cnt += 1
         prefix = 'ty-%d' % c.ty_cnt
         #if rcd.hindamiskogum.on_hindamisprotokoll:
            # toimub hindamisprotokollilt punktide sisestamine
            # sealt saab sisestada ainult punkte
            # aga võib olla lubatud statistika mõttes ka vastuseid sisestada
            # seetõttu ei keelata vastuste sisestmmist
            #opt_sisestusviis = c.opt_sisestusviis[:1]
         if rcd.arvutihinnatav:
            # tööde sisestamine, kolm viisi
            opt_sisestusviis = c.opt_sisestusviis
         else:
            # tööde sisestamine, aga vastuseid ei sisestata, 
            # sest neist ei saa tulemust arvutada
            opt_sisestusviis = c.opt_sisestusviis[:2]
      %>
      ${h.select('%s.sisestusviis' % prefix, rcd.sisestusviis, opt_sisestusviis)}
      ${h.hidden('%s.id' % prefix, rcd.id)}
      % else:
      ${rcd.sisestusviis_nimi}
      % endif
    </td>
    <td>
      % if c.testiosa.vastvorm_kood == const.VASTVORM_KP:
      ${h.checkbox('%s.hyppamisviis' % prefix, 1, checked=rcd.hyppamisviis or not rcd.id,
      class_=rcd.sisestusviis==model.Testiylesanne.SISESTUSVIIS_PALLID and 'invisible' or None)}
      % endif
    </td>
  </tr>
</%def>

<script>
$(document).ready(function() {  
 $('select[name$="sisestusviis"]').change(function(){
    var saab_hypata = $(this).val() == '${model.Testiylesanne.SISESTUSVIIS_PALLID}';
    $(this).closest('tr').find('input[name$="hyppamisviis"]').toggleClass('invisible', saab_hypata);
 });
});
</script>
