<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Kirjaliku testi vastuste sisestamine")} | ${c.sooritus.tahised}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_('Kirjaliku testi vastuste sisestamine'),
h.url('sisestamine_testitood', sisestuskogum_id=c.sisestuskogum.id,
toimumisaeg_id=c.toimumisaeg.id, sessioon_id=c.testimiskord.testsessioon_id,
tpr_tahised=c.protokoll.get_tahised_tk()))}
${h.crumb(c.sooritus.tahised)}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'sisestamine' %>
</%def>
<%def name="page_headers()">
<style>
  .tr-hindaja, .tr-sisestamine { border-bottom: 1px solid #cfcfcf; }
  .td-sis-header { min-width: 175px; background-color: #fafafa; padding: 3px 12px;}
  .td-sis-value, .td-sis-value2 {padding: 3px; margin: 0px 5px;}
</style>
</%def>
<% 
   vastvorm_kood = c.toimumisaeg.testiosa.vastvorm_kood
   c.testikoht = c.protokoll.testipakett.testikoht
   c.toimumisaeg = c.testikoht.toimumisaeg
   c.testimiskord = c.toimumisaeg.testimiskord
   c.test = c.testimiskord.test
   c.testiruum = c.protokoll.testiruum
   sisestus_isikukoodiga = c.toimumisaeg.testimiskord.sisestus_isikukoodiga
%>
<%namespace name="sisu" file="vastused_sisu.mako"/>

${h.form_search()}
<div class="question-status d-flex flex-wrap justify-content-between mb-2 bg-gray-50">
  <div class="item mr-5">
    ${h.flb(_("Test"), 'test_nimi')}
    <div id="test_nimi">
      ${c.test.nimi}
      ${c.toimumisaeg.tahised}
      ${h.str_from_date(c.testiruum.algus)}
    </div>
  </div>
  <div class="item mr-5">
    ${h.flb(_("Protokollirühm"))}
    <div>
      ${c.protokoll.get_tahised_tk()}
    </div>
  </div>
  <div class="item mr-5">
    ${h.flb(_("Testisooritus"))}
    <div>
      <span class="h2">
        ${c.sooritus.tahised}
        % if sisestus_isikukoodiga:
        ${c.sooritus.sooritaja.kasutaja.isikukood}
        % endif
      </span>
    </div>
  </div>
  <div class="item mr-5">
    ${h.flb(_("Sisestuskogum"))}
    <div>
      ${model.Sisestuskogum.get(c.solek.sisestuskogum_id).tahis}
    </div>
  </div>
  <div class="item mr-5">
    ${h.flb(_("Ülesandekomplekt"))}
    <div>
      ${sisu.td_komplekt()}
    </div>
  </div>

  % if str(c.sisestus) == '1':
  <div class="item mr-5">
    ${h.flb(_("Sisestus"))}
    <div>
      1 
      (${c.solek.staatus1_nimi})
    </div>
  </div>
  % elif str(c.sisestus) == '2':
  <div class="item mr-5">
    ${h.flb(_("Sisestus"))}
    <div>
      2 
      (${c.solek.staatus2_nimi})
    </div>
  </div>
  % elif c.sisestus == 'p':
  <div class="item mr-5">
    ${h.flb(_("Sisestuste parandamine"))}
    <div>
      (${c.solek.staatus_nimi})
    </div>
  </div>
  % endif

  % if c.sisestuskogum.naita_pallid and c.solek.pallid is not None:
  <div class="item mr-5">
    ${h.fstr(c.solek.pallid)} ${_("palli")}
    <br/>
    ${h.fstr(c.solek.toorpunktid)} ${_("toorpunkti")}
  </div>
  % endif
</div>
${h.end_form()}

% if c.komplekt:
${h.form_save(None, autocomplete='off')}
${h.hidden('komplekt_id', c.komplekt.id)}
${h.hidden('komplekt_id2', c.komplekt_id2)}
${h.hidden('op', '')}
  % for hk_n, hkogum in enumerate(c.sisestuskogum.hindamiskogumid):
  % if hkogum.staatus and not hkogum.on_hindamisprotokoll:
  <% 
     holek = c.sooritus.get_hindamisolek(hkogum)
     if holek:
        if c.sisestus == 'p':
          hindamine = holek.get_hindamine(c.hindamine_liik, 1)
          hindamine2 = c.kahekordne_sisestamine and holek.get_hindamine(c.hindamine_liik, 2) or None
        else:
          hindamine = holek.get_hindamine(c.hindamine_liik, c.sisestus)
          hindamine2 = None

        if hindamine and hindamine.komplekt_id != c.komplekt.id:
          ## kõigil sama sisestusega sisestatavatel kogumitel peaks olema yhine komplekt
          hindamine = None

        if hindamine2 and hindamine2.komplekt_id != c.komplekt.id:
          ## ei saa näidata teist sisestamist, sest ylesanded erinevad
          hindamine2 = None

     else:
       hindamine = hindamine2 = None

     prefix1 = 'hk-%d.hmine' % (hk_n)
     prefix2 = 'hk-%d.hmine2' % (hk_n)
  %>
  ${h.hidden('hk-%d.hindamiskogum_id' % (hk_n), hkogum.id)}
  <h3>${_("Hindamiskogum")}: ${hkogum.tahis} ${hkogum.nimi} <!--${hkogum.id}--></h3>
  <div class="form border tbl-sisestamine mb-2">
    ${sisu.tr_hindaja(hkogum, vastvorm_kood, holek, 
                      prefix1, hindamine, 
                      prefix2, hindamine2)}

##  % for ty_n,ty in enumerate(hkogum.testiylesanded):
% for ty_n, ty in enumerate(hkogum.testiylesanded):
  <% 
     valikute_arv = ty.on_valikylesanne and ty.valikute_arv or 1 
     valik_vy = valikute_arv > 1 and hindamine and hindamine.get_vy_by_ty(ty)
  %>
  % for valik_seq in range(1, valikute_arv+1):
    <% 
      vy = vy2 = ty.get_valitudylesanne(c.komplekt, valik_seq)
      valitud = valik_vy == vy or not valik_vy and valik_seq == 1      
    %>
    ${sisu.tr_testiylesanne(ty, valik_seq, valikute_arv, valitud,
                            '%s.ty-%d' % (prefix1, ty_n), hindamine, vy,
                            '%s.ty-%d' % (prefix2, ty_n), hindamine2, vy2
                            )}
  % endfor
% endfor
  </div>
  % endif
  % endfor

  ## järgmised väljad on siin selleks, et vigade korral formencode 
  ## ei teeks järgmise töö valimise vormi välju tühjaks
  ${h.hidden('sisestuskogum_id',c.sisestuskogum.id)}
  ${h.hidden('sessioon_id',c.testimiskord.testsessioon_id)}
  ${h.hidden('toimumisaeg_id',c.toimumisaeg.id)}
  ${h.hidden('tahised', c.tahised)}

  % if c.komplekt:
  ## Salvesta-nupp on teistest nuppudest varem, et kursoriga liikudes satuks esmalt sellele
  ## Submit nupp on input ja set_focus_to_next_input_field toob eelmiselt väljalt enteriga siia
  <div class="text-right">
    ${h.submit(_('Salvesta'), id='kinnita', clicked=True)}
  </div>
  % endif

  ${h.end_form()}
% endif

  <div class="d-flex flex-wrap mt-3">
    <div class="flex-grow-1">
${h.form_search(h.url('sisestamine_testitood'))}
${h.hidden('sisestuskogum_id',c.sisestuskogum.id)}
${h.hidden('sessioon_id',c.testimiskord.testsessioon_id)}
${h.hidden('toimumisaeg_id',c.toimumisaeg.id)}
${h.hidden('eelmine_id', c.sooritus.id)}
${h.hidden('sisesta',1)}
% if c.sisestus == 'p':
## parandamisel valib süsteem ise järgmise
${h.hidden('sisestus', 'p')}
% else:

% if sisestus_isikukoodiga:
${_("Järgmine isikukood:")}
${h.text('isikukood', c.isikukood, size=12, pattern='\d{11}', class_=c.focus and 'initialfocus' or None)}
<% if c.focus: c.focus = None %>
% endif

${_("Järgmise töö tähis: ")}
## kui on seatud URLi parameeter focus, siis järgmise tähise väli saab fookuse
${h.text('tahised', c.tahised, size=7, class_=c.focus and 'initialfocus' or None)}
${_("protokollirühm:")}
${h.text('tpr_tahised', c.tpr_tahised or c.protokoll.get_tahised_tk(), size=10, tabIndex=100)}


% endif
${h.button(_('Järgmine'), id='otsi', onclick='this.form.submit()')}
${h.end_form()}

    </div>
    <div>
      % if c.komplekt:
        % if c.sisestus != 'p':
      ${h.button(_('Loobu'), id='loobu', level=2)}
          % if c.user.has_permission('parandamine', const.BT_UPDATE):
      ${h.btn_to(_('Parandamine'), h.url_current(sisestus='p'), level=2)}
          % endif
        % endif
      % endif
    </div>
  </div>
<script>
## formencode pandud kole teade "Erineb" teisendatakse punaseks kastiks
$(document).ready(function(){
$.each($('.error'), function(n, item){
  $(item).closest('.showerr').addClass('form-control').addClass('is-invalid');
});

## loobumise ja kinnitamise nupud
$('button#loobu,button#kinnita').click(function(){
  if(!is_btn_clicked($(this),5000))
  {
     set_btn_clicked($(this));
     set_spinner($(this));
     $('form#form_save input[name="op"]').val(this.id);
     $('form#form_save').submit();
  }
});
## valikylesannete korral muudame mittevalitud valikud disabled olekusse, välja arvatud valiku tegemise raadionupp
$('input.valikylesanne[type="radio"]').change(function(){
 $.each($('input.valikylesanne[name="'+$(this).attr('name')+'"]'), function(n, item){
  $(item).closest('.tr-sisestamine').find('input,select').filter(':not(.valikylesanne)').attr('disabled', !$(item).prop('checked'));
  $(item).closest('.td-sis-header').find('span[id="valikradio2"]>input').prop('checked', $(item).prop('checked'));
 });
}).change();
## change() teeb dirty=true, tyhistame selle
dirty=false;
});
</script>

