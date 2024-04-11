${h.form_save(c.item.id)}
${h.hidden('testiosa_id', c.item.testiosa.id)}

% if c.item.sisestuskogum_id:
  <%
    c.sisestuskogum_id = c.item.sisestuskogum_id 
    sisestuskogum = c.item.sisestuskogum or model.Sisestuskogum.get(c.item.sisestuskogum_id) 
  %>
<h3>${_("Sisestuskogum")}</h3>   
<div class="form-group row">
  ${h.flb3(_("Tähis"))}
  <div class="col">
    ${sisestuskogum.tahis}
  </div>
</div>
<div class="form-group row">
  ${h.flb3(_("Nimetus"))}
  <div class="col">
    ${sisestuskogum.nimi}
  </div>
</div>
% endif

${h.hidden('sisestuskogum_id', c.sisestuskogum_id)}

% if c.item.vaikimisi:
<h3>${_("Vaikimisi hindamiskogum")}</h3>
% else:
<h3>${_("Hindamiskogum")}</h3>
% endif
${h.rqexp()}
<div class="form-wrapper mb-2">
<div class="form-group row">
  ${h.flb3(_("Tähis"), rq=True)}
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
  ${h.flb3(_("Hindepallide arv"))}
  <div class="col">
      ${h.fstr(c.item.max_pallid)}
  </div>
</div>

  % if c.item.sisestuskogum and c.item.sisestuskogum.on_skannimine and c.item.arvutihinnatav:
<div class="form-group row">
  ${h.flb3(_("Vastuste tuvastamine skannimisel"))}
  <div class="col">
    ${h.checkbox1('f_on_digiteerimine', 1, checked=c.item.on_digiteerimine,
    onchange='changed_digiteerimine()')}
  </div>
</div>
  % endif

<div class="form-group row">  
  ${h.flb3(_("Hindamisprotokoll"))}
  <div class="col">
    ${h.checkbox1('f_on_hindamisprotokoll', 1, checked=c.item.on_hindamisprotokoll)}</div>
</div>

<div class="form-group row">
  ${h.flb3(_("Komplektide toorpunktide erinevus"))}
  <div class="col">
    ${h.checkbox1('f_erinevad_komplektid', 1, checked=c.item.erinevad_komplektid,
      label=_("Printida igale komplektile eraldi hindamisprotokoll"))}
  </div>
</div>

<div class="form-group row">  
  ${h.flb3(_("Hindamise liik"))}
  <div class="col">
      ${h.select('f_hindamine_kood', c.item.hindamine_kood, c.opt.klread_kood('HINDAMINE'),
      onchange='change_hindamine()')}
  </div>
</div>

<div class="form-group row">  
  ${h.flb3(_("Arvutihinnatav"))}
  <div class="col">
      ${h.sbool(c.item.arvutihinnatav)}
  </div>
</div>
<div class="form-group row">
  ${h.flb3(_("Kahekordne hindamine"))}
  <div class="col">
      <%
        q = (model.Session.query(model.Testimiskord.id)
             .filter_by(test_id=c.test.id).filter_by(sisaldab_valimit=True))
        sisaldab_valimit = q.count() > 0
      %>
      % if sisaldab_valimit:
      ${h.checkbox1('f_kahekordne_hindamine', 1,
      checked=c.item.kahekordne_hindamine,
      onclick='change_kahekordne(true)', label=_("mitte-valim"))}
      
      ${h.checkbox1('f_kahekordne_hindamine_valim', 1,
      checked=c.item.kahekordne_hindamine_valim,
      onclick='change_kahekordne()', label=_("valim"))}

      % else:
      ${h.checkbox1('f_kahekordne_hindamine', 1,
      checked=c.item.kahekordne_hindamine,
      onclick='change_kahekordne(true)')}
      
      ${h.hidden('f_kahekordne_hindamine_valim',
      c.item.kahekordne_hindamine and '1' or '')}
      % endif
  </div>
</div>

  % if c.item.testiosa.vastvorm_kood in (const.VASTVORM_KE, const.VASTVORM_SE, const.VASTVORM_I, const.VASTVORM_KP):
<div class="form-group row">  
    ${h.flb3(_("Paarishindamine"))}
    <div class="col">
      ${h.checkbox1('f_paarishindamine', 1, checked=c.item.paarishindamine,
      onclick='change_kahekordne()')}
    </div>
</div>
  % endif
  
<div class="form-group row">  
    ${h.flb3(_("Kahe hindajaga ühekordne hindamine"))}
    <div class="col">
      ${h.checkbox1('f_kontrollijaga_hindamine', 1, checked=c.item.kontrollijaga_hindamine)}
    </div>
</div>

<div class="form-group row">  
    ${h.flb3(_("Lubatud erinevus"))}
    <div class="col">
      ${h.int5('f_hindajate_erinevus', c.item.hindajate_erinevus)}%
      % if c.item.hindajate_erinevus is not None and c.item.max_pallid is not None:
      (${h.fstr(c.item.hindajate_erinevus*c.item.max_pallid/100.)}p)
      % endif
    </div>
</div>

<div class="form-group row">  
    ${h.flb3(_("Kolmas hindamine on lõplik"))}
    <div class="col">
      ${h.checkbox1('f_hindamine3_loplik', 1, checked=c.item.hindamine3_loplik)}
    </div>      
</div>

<div class="form-group row">  
    ${h.flb3(_("Arvutamise meetod"))}
    <div class="col">
      ${h.select('f_arvutus_kood', c.item.arvutus_kood, c.opt.klread_kood('ARVUTUS'))}
    </div>
</div>

<div class="form-group row">  
    ${h.flb3(_("Hindaja tasu"))}
    <div class="col">
      ${h.money('f_tasu', c.item.tasu)} &euro;
    </div>
</div>
% if c.item.testiosa.vastvorm_kood in (const.VASTVORM_SP, const.VASTVORM_SH):
<div class="form-group row">  
    ${h.flb3(_("Intervjueerimise eest hindajale juurde makstav tasu"))}
    <div class="col">
      ${h.money('f_intervjuu_lisatasu', c.item.intervjuu_lisatasu)} &euro;
    </div>
</div>

<div class="form-group row">  
  ${h.flb3(_("Intervjueerija tasu"))}
  <div class="col">
    ${h.money('f_intervjuu_tasu', c.item.intervjuu_tasu)} &euro;
  </div>
</div>
% endif

<div class="form-group row">  
  ${h.flb3(_("Oma kooli hindamine"))}
  <div class="col">
    ${h.checkbox1('f_oma_kool_tasuta', 1, checked=c.item.oma_kool_tasuta,
    label=_("Töötasude aruandes ei arvestata oma kooli õpilaste töid"))}
  </div>
</div>
## form-wrapper end
</div>

<script>
function change_hindamine()
{
  if($('#f_hindamine_kood').val() == '${const.HINDAMINE_SUBJ}') 
  {
    ## subjektiivse hindamise korral saab valida, kas on kahekordne hindamine või mitte
    $('#f_kahekordne_hindamine,#f_kahekordne_hindamine_valim,#f_paarishindamine').removeAttr('disabled');
    change_kahekordne();
    $('#f_on_digiteerimine').attr('disabled', true);
    $('#f_kontrollijaga_hindamine').attr('disabled', true);
  }
  else
  {
    ## objektiivse hindamise korral ei saa valida neid 
    $('#f_kahekordne_hindamine,#f_kahekordne_hindamine_valim,#f_paarishindamine,#f_hindajate_erinevus,#f_arvutus_kood,#f_hindamine3_loplik').attr('disabled', true);
    $('#f_hindamine3_loplik').prop('checked', false);
    $('#f_on_digiteerimine').attr('disabled', false);
    $('#f_kontrollijaga_hindamine').removeAttr('disabled');
  }
}
function change_kahekordne(set_paaris)
{
  if(set_paaris)
  {
     ## kui valimit pole eraldatud, siis kopeerime väärtuse valimi väljale, mis on nähtamatu
     var v = ($('#f_kahekordne_hindamine').prop('checked') ? '1' : '');
     $('#f_kahekordne_hindamine_valim[type="hidden"]').val(v);
  }
  if(set_paaris && $('#f_kahekordne_hindamine').prop('checked'))
  {
     ## kui kasutaja klikkis kahekordsel hindamisel, siis enamasti tähendab see paarishindamist
     $('#f_paarishindamine').prop('checked', true);
     ## kui mitte-valimis märgitakse kahekordne hindamine, siis märgime vaikimisi ka valimis (vajadusel saab maha võtta)
     $('#f_kahekordne_hindamine_valim').prop('checked', true);
  }
  if($('#f_paarishindamine').prop('checked'))
  {
     ## paarishindamine eeldab alati, et vähemalt kuskil on kahekordne hindamine
     if(!$('#f_kahekordne_hindamine').prop('checked') && !$('#f_kahekordne_hindamine_valim').prop('checked'))
     {
        $('#f_paarishindamine').prop('checked', false);
     }
  }
  if($('#f_kahekordne_hindamine').prop('checked') || $('#f_kahekordne_hindamine_valim').prop('checked'))
  {
     $('#f_hindajate_erinevus,#f_arvutus_kood,#f_hindamine3_loplik').removeAttr('disabled');
  }
  else
  {
     $('#f_hindamine3_loplik').prop('checked', false);
     $('#f_hindajate_erinevus,#f_arvutus_kood,#f_hindamine3_loplik').attr('disabled', true);
  }
}
function changed_digiteerimine()
{
  if($('#f_on_digiteerimine').prop('checked'))
    $('#f_on_hindamisprotokoll').attr('disabled',true);
  else
    $('#f_on_hindamisprotokoll').removeAttr('disabled');
}
$(function(){
  change_hindamine();
});
</script>


  <%
     opt_komplektivalikud = c.testiosa.get_opt_komplektivalikud(naita_kursus=True)
     c.on_alatestid = c.item.testiosa.on_alatestid
     if not c.item.komplektivalik_id:
        c.item.komplektivalik_id = opt_komplektivalikud[0][0]
     c.item.komplektivalik = model.Komplektivalik.get(c.item.komplektivalik_id)
  %>
  % if c.on_alatestid:
<table width="100%" class="table" >
  <tr>
    <td class="fh" width="80">${_("Alatestid")}</td>
    <td>${h.select('f_komplektivalik_id', c.item.komplektivalik_id, opt_komplektivalikud, 
      onchange="change_komplektivalik(this);", ronly=False, empty=False, wide=False)}
    </td>
  </tr>
</table>
<br/>
    <script>
    function change_komplektivalik()
    {
        var kv_id = $('#f_komplektivalik_id').val();
        $('tbody.kv').hide();
        $('tbody.kv-' + kv_id).show();
    }
    </script>
  % else:
      ${h.hidden('f_komplektivalik_id', c.item.komplektivalik_id)}
  % endif


<%
   opt_kursused = c.test.opt_kursused
%>
${self.tbl_testiylesanded()}

% if c.item.id:
<div id="hk_hindamiskriteeriumid">
<%include file="kogum.hindamiskriteeriumid.mako"/>
</div>
% endif
${h.end_form()}


<%def name="tbl_testiylesanded()">
<table class="table ${c.is_edit and ' multipleselect' or ''}" >
  <caption>${_("Testiülesanded")}
    % if kursus_nimi:
    (${kursus_nimi})
    % endif
  </caption>
  <thead>
  <tr>
    % if not c.testiosa.lotv:
    <th></th>
    % endif
    % if c.on_alatestid:
    ${h.th(_("Alatest"))}
    ${h.th(_("Plokk"))}
    % endif
    ${h.th(_("Ülesanne"))}
    ${h.th(_("Arvutihinnatav"))}
    % if c.testiosa.lotv:
    % for komplekt in c.item.komplektivalik.komplektid:
    ${h.th(_("Komplekt") + ' ' + komplekt.tahis)}
    % endfor
    % endif
  </tr>
  </thead>
  % for kv in c.testiosa.komplektivalikud:
  <tbody class="kv kv-${kv.id}" ${kv.id != c.item.komplektivalik_id and 'style="display:none"' or ''}>
  % if c.on_alatestid:
    % for alatest in c.testiosa.alatestid:
      % if alatest.komplektivalik == kv:
        % for rcd in alatest.testiylesanded:
          ${self.row_testiylesanne(rcd)}
        % endfor
      % endif
    % endfor
  % else:
     % for rcd in c.testiosa.testiylesanded:
        ${self.row_testiylesanne(rcd)}
     % endfor          
  % endif
  </tbody>
  % endfor
</table>
<br/>
</%def>

<%def name="row_testiylesanne(rcd)">
% if c.is_edit or c.testiosa.lotv or rcd.hindamiskogum_id == c.item.id:
<%
  r_hk = rcd.hindamiskogum
%>
       % if rcd.hindamiskogum_id == c.item.id:
  <tr class="selected">
       % else:
  <tr>
       % endif
    % if not c.testiosa.lotv:
    <td>
      ${h.checkbox('ty_id', rcd.id, checked=rcd.hindamiskogum_id==c.item.id,
      disabled=rcd.hindamiskogum_id!=c.item.id and not r_hk.vaikimisi or c.item.vaikimisi)}
      % if r_hk and r_hk.tahis:
      (${r_hk.tahis})
      % endif
    </td>
    % endif
    % if c.on_alatestid:
    <td>
      <% alatest = rcd.alatest %>
      % if alatest and alatest.tahis:
      ${alatest.tahis}. ${alatest.nimi}
      % elif alatest:
      ${alatest.nimi}
      % endif
    </td>
    <td>
      <% testiplokk = rcd.testiplokk %>
      % if rcd.testiplokk:
      ${testiplokk.seq}. ${testiplokk.nimi}
      % endif
    </td>
    % endif
    <td>
      ${rcd.tahis}.
      % if rcd.tahis != rcd.nimi:
      ${rcd.nimi}
      % endif
    </td>
    <td>${h.sbool(rcd.arvutihinnatav)}</td>

    % if c.testiosa.lotv:
    % for komplekt in c.item.komplektivalik.komplektid:
       <td>
         % for vy in komplekt.valitudylesanded:
         % if vy.testiylesanne_id==rcd.id and vy.ylesanne_id:
         ${h.checkbox('vy_id', vy.id, checked=vy.hindamiskogum_id==c.item.id,
         disabled=vy.hindamiskogum_id and vy.hindamiskogum_id!=c.item.id and not vy.hindamiskogum.vaikimisi,
         label='%s %s' % (_("Ülesanne"), vy.ylesanne_id))}
         % if vy.hindamiskogum and vy.hindamiskogum.tahis:
         (${vy.hindamiskogum.tahis})
         % endif
         % if vy.ylesanne:
         <span title="${_("Arvutihinnatav")}">${vy.ylesanne.arvutihinnatav and "*" or ''}</span>
         % endif
         % endif
         % endfor
       </td>
    % endfor
    % endif
  </tr>
% endif
</%def>
