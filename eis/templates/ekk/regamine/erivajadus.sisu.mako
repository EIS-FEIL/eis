<% c.test = c.sooritaja.test %>
<div class="table p-2 my-2">
  <div class="row">
    <div class="col-md-2 col-xs-4 fh">
      ${_("Testisooritaja")}
    </div>
    <div id="sooritaja" class="col-md-7 col-xs-8">
      ${c.kasutaja.isikukood}
      ${c.sooritaja.nimi}
      % if c.sooritaja.vabastet_kirjalikust:
      (${_("65a ja vanem kodakondsuse taotleja")})
      % endif
      % if c.app_ekk:
      ${h.link_to(_("Testile registreerimise andmed"),h.url('regamine',id=c.sooritaja.id))}
      % endif
    </div>
    <div class="col">
    % if c.app_ekk:
      % if c.item.on_erivajadused_tagasilykatud:      
      ${_("Eritingimused on tagasi lükatud")}
      % else:
        % if c.item.on_erivajadused_kinnitatud:
        ${_("Eritingimused on kinnitatud")}
        % else:
        ${_("Eritingimused on kinnitamata")}
        % endif
        <br/>
        % if c.test.testiliik_kood!=const.TESTILIIK_RIIGIEKSAM:
        % if c.item.on_erivajadused_vaadatud:
        ${_("Eritingimused on üle vaadatud")}
        % else:
        ${_("Eritingimused on üle vaatamata")}
        % endif
        % endif
      % endif
    % else:
        ${_("Kinnitatud / üle vaadatud")}:
      % if c.item.on_erivajadused_tagasilykatud:
        ${_("Tagasi lükatud")}
      % elif c.item.on_erivajadused_kinnitatud or c.item.on_erivajadused_vaadatud:
        ${_("Jah")}
      % else:
        ${_("Üle vaatamata")}
      % endif
    % endif
    </div>
  </div>
  <div class="row">
    <div class="col-md-2 col-xs-4 fh">
      ${_("Testi andmed")}
    </div>
    <div class="col" id="test_nimi">
      ${c.test.nimi}
      <%
        testiosa = c.item.testiosa
        toimumisaeg = c.item.toimumisaeg
      %>
      ${testiosa.tahis}
      ${testiosa.vastvorm_nimi}
      % if toimumisaeg:
      ${toimumisaeg.millal}
      % endif
    </div>
  </div>
</div>

<%
   testiosad = list(c.test.testiosad)
   alatestid = list(c.item.alatestid)

   if c.test.testiliik_kood == const.TESTILIIK_POHIKOOL:
      aste_bit = const.ASTE_BIT_III
   elif c.test.testiliik_kood == const.TESTILIIK_RIIGIEKSAM:
      aste_bit = const.ASTE_BIT_G
   else:
      aste_bit = const.ASTE_BIT_I

   opt_erivajadus = c.opt.klread_kood('ERIVAJADUS', bit=aste_bit)
   opt_koodid = [r[0] for r in opt_erivajadus]
%>
% if len(testiosad) > 1 or len(alatestid) > 1:
<div class="table p-2 my-2 d-flex flex-wrap" id="vabastamine">
    % if len(testiosad) > 1:
    <div class="mr-2 fh">
      ${h.checkbox('vaba_osa', 1,
      checked=c.item.staatus==const.S_STAATUS_VABASTATUD, 
      label=_("Testiosast vabastatud"))}
    </div>
    % endif

% if len(alatestid) > 1:
    <div class="mr-2 fh">${_("Vabastatud alatestist")}:</div>
% for alatest in c.item.alatestid:
    <div class="mr-2">
      <% 
         atos = c.item.get_alatestisooritus(alatest.id) 
         vaba = atos and atos.staatus == const.S_STAATUS_VABASTATUD or \
            c.item.staatus == const.S_STAATUS_VABASTATUD
         if not vaba and not atos and alatest.alatest_kood == const.ALATEST_RK_KIRJUTAMINE:
            # alatestisoorituse kirjet veel pole
            vaba = c.sooritaja.vabastet_kirjalikust
      %>
      ${h.checkbox('vaba_alatest_id', alatest.id, checked=vaba,
      label=alatest.nimi)}
    </div>
% endfor
% endif
</div>
% endif

<script>
$(function(){
  $('#vaba_osa').change(function(){
     $('input[name="vaba_alatest_id"]').prop('checked', this.checked);
     $('#erivajadustabel').find('input,textarea').prop('disabled', this.checked);
  });
  $('input[name="vaba_alatest_id"]').change(function(){  
     var all_checked = $('input[name="vaba_alatest_id"]:not(:checked)').length == 0;
     $('#vaba_osa').prop('checked', all_checked);
     $('#erivajadustabel').find('input,textarea').prop('disabled', all_checked);
  });
% if c.item.staatus == const.S_STAATUS_VABASTATUD:
  $('#erivajadustabel').find('input,textarea').prop('disabled', true);
% endif
});
</script>

<%
  if c.app_ekk or not c.is_edit:
     # kõrvuti taotletud ja kinnitatud
     colp = "col-6" # ekraanipoole laius (label + väli)
     colh1 = "col-md-6 col-xs-12" # label 
     colh2 = "col-md-6 col-xs-12" # väli
  else:
     # ainult taotletud
     colp = "col-12" # label + väli
     colh1 = "col-md-3 col-xs-12" # label
     colh2 = "col-md-9 col-xs-12" # väli
  colb1 = "col-md-3 fh" # kontaktisiku label
  colb2 = "col-md-9"    # kontaktisiku väli
%>
${h.rqexp()}
<div id="erivajadustabel" class="table p-2">
  <div class="row">
    <div class="${colp} row">
      <div class="${colh1} fh">
        ${h.flb(_("Taotletavad eritingimused"))}
      </div>
      <div class="${colh2} fh">
        ${h.flb(_("Põhjendus"), rq=c.app_eis)}
      </div>
    </div>
    % if c.app_ekk or not c.is_edit:
    <div class="${colp} row">
      <div class="${colh1} fh">
        ${h.flb(_("Kinnitatud eritingimused"))}
      </div>
      <div class="${colh2} fh">
        ${h.flb(_("Põhjendus"))}
      </div>
    </div>
    % endif
  </div>

  % for cnt, rcd in enumerate(opt_erivajadus):
  <%
     kood = rcd[0]
     nimi = rcd[1]
     kirjeldus = rcd[3]
     item = c.item.get_erivajadus(kood)
  %>
  ${self.row_erivajadus(cnt, kood, nimi, kirjeldus, item, colp, colh1, colh2)}
  % endfor

  <%
     vanad = [item for item in c.item.erivajadused if item.erivajadus_kood and item.erivajadus_kood not in opt_koodid]
  %>
  % if vanad:
  <div class="field-header">
    ${_("Endise klassifikaatori alusel varem sisestatud eritingimused")}
  </div>
  % for item in vanad:
  <%
     cnt += 1
  %>
  ${self.row_erivajadus(cnt, item.erivajadus_kood, item.erivajadus_nimi, None, item, colp, colh1, colh2)}  
  % endfor
  % endif
  
  <div class="row">
    <% 
       cnt += 1 
       item = c.item.get_erivajadus(None)
    %>
    <div class="${colp} row">
      <div class="${colh1}">
        ${h.flb(_("Märkused"), 'ev-%s.taotlus_markus' % cnt)}
        <span class="helpable" id="erivajadus_markus"></span>
      </div>
      <div class="${colh2}">
      % if c.is_edit:
      ${h.textarea('ev-%s.taotlus_markus' % cnt, item and item.taotlus_markus)}
      ${h.hidden('ev-%s.erivajadus_kood' % cnt, '')}
      ${h.hidden('ev-%s.id' % cnt, item and item.id)}
      ${h.hidden('ev-%s.taotlus' % cnt, '')}
      % elif item:
      <span id="ev-${cnt}.taotlus_markus">
        ${item.taotlus_markus}
      </span>
      % endif
      </div>
    </div>
    
    % if c.app_ekk or not c.is_edit:
    <div class="${colp} row">
      <div class="${colh1} fh">
        ${h.flb(_("Märkused"), 'ev-%s.kinnitus_markus' % cnt)}
      </div>
      <div class="${colh2}">
      % if c.is_edit:
      ${h.textarea('ev-%s.kinnitus_markus' % cnt, item and item.kinnitus_markus)}
      ${h.hidden('ev-%s.kinnitus' % cnt, '')}
      % elif item:
      <span id="ev-${cnt}.kinnitus_markus">
        ${item.kinnitus_markus}
      </span>
      % endif
      </div>
    </div>
    % endif
  </div>
</div>

<div class="my-3">
<div class="row mt-1">
  <div class="${colb1}">
    ${h.flb(_("Kontaktisik"),'r_kontakt_nimi', rq=True)}
  </div>
  <div class="${colb2}">
    ${h.text('r_kontakt_nimi', c.sooritaja.kontakt_nimi, ronly=not c.is_edit and not c.is_edit_p)}
  </div>
</div>
<div class="row mt-1">
  <div class="${colb1}">
    ${h.flb(_("Kontaktisiku e-post"), 'r_kontakt_epost', rq=True)}
  </div>
  <div class="${colb2} err-parent">
    ${h.text('r_kontakt_epost', c.sooritaja.kontakt_epost, ronly=not c.is_edit and not c.is_edit_p)}
  </div>
</div>
<div class="row mt-1">
<% tugik = c.item.tugiisik_kasutaja %>
% if tugik:
   <div class="${colb1}">${h.flb(_("Tugiisik"), 'tugik_nimi')}</div>
   <div class="${colb2}" id="tugik_nimi">
     ${tugik.nimi}
   </div>
% else:
   <div class="${colb1}"}>${_("Tugiisikut pole määratud")}</div>
% endif
</div>

</div>

<%def name="row_erivajadus(cnt, kood, nimi, kirjeldus, item, colp, colh1, colh2)">
<%
  pole_vaja_kinnitust = model.Erivajadus.pole_vaja_kinnitust(kood, c.test)
  r_is_edit = c.is_edit or pole_vaja_kinnitust and c.is_edit_p
  on_taotlus_style = item and item.taotlus and "display:block" or "display:none"
  on_kinnitus_style = item and item.kinnitus and "display:block" or "display:none"
%>
  <div class="row mt-1 eri-row">
    <div class="${colp} row">
      <div class="${colh1} taotlus">
        <div class="fh">
        ${h.checkbox('ev-%s.taotlus' % cnt, 1, checked=item and item.taotlus, label=nimi,
        data_helpid='erivajadus_%s' % kood, ronly=not r_is_edit, class_="cb-taotlus")}
        </div>
      % if r_is_edit:
      ${h.hidden('ev-%s.erivajadus_kood' % cnt, kood)}
      ${h.hidden('ev-%s.id' % cnt, item and item.id)}
      % endif
      % if kirjeldus:
      <div class="on-taotlus" style="${on_taotlus_style}">${kirjeldus}</div>
      % endif
      </div>
      <div class="${colh2} taotlus">
        ${h.text('ev-%s.taotlus_markus' % cnt, item and item.taotlus_markus, ronly=not r_is_edit,
        class_="on-taotlus", style=on_taotlus_style)}
      </div>
    </div>
    % if (c.app_ekk or not c.is_edit) and not pole_vaja_kinnitust:
    <div class="${colp} row">
      <div class="${colh1} kinnitus fh">
      ${h.checkbox('ev-%s.kinnitus' % cnt, 1, checked=item and item.kinnitus, label=nimi,
      data_helpid='erivajadus_%s' % kood, class_="cb-kinnitus")} 
      </div>
      <div class="${colh2} kinnitus">
        ${h.text('ev-%s.kinnitus_markus' % cnt, item and item.kinnitus_markus,
        class_="on-kinnitus", style=on_kinnitus_style)}
      </div>
    </div>
    % endif
  </div>
</%def>

% if c.is_edit or c.is_edit_p:
<script>
$(function(){
  $('input.cb-taotlus').click(function(){
    $(this).closest('.eri-row').find('.on-taotlus').toggle(this.checked);
  });
  $('input.cb-kinnitus').click(function(){
    $(this).closest('.eri-row').find('.on-kinnitus').toggle(this.checked);
  });
  $('input.cb-taotlus').each(function(){
    $(this).closest('.eri-row').find('.on-taotlus').toggle(this.checked);
  });
  $('input.cb-kinnitus').each(function(){
    $(this).closest('.eri-row').find('.on-kinnitus').toggle(this.checked);
  });
});

% if c.app_ekk:
function kannayle()
{
   $.each($('.kinnitus input[type="checkbox"]'), function(n, item){
     var t = $(item).closest('.eri-row').find('.taotlus input[type="checkbox"]');
     $(item).prop('checked', t.prop('checked')).change();
   });
   $.each($('.kinnitus input[type="text"]'), function(n, item){
     var t = $(item).closest('.eri-row').find('.taotlus input[type="text"]');
     $(item).val(t.val());
   });
}
function confirm_save(vaadatud)
{
  $('input#on_erivajadused_vaadatud').val(vaadatud ? '1' : '');

  var kinnitamata = $('table#erivajadustabel .eri-row').filter(function(){
  return ($(this).find('input[type="checkbox"][name$=".taotlus"]').prop('checked') == true &&
          $(this).find('input[type="checkbox"][name$=".kinnitus"]').prop('checked') == false);
  });
  if(kinnitamata.length > 0)
  {
    confirm_dialog("${_("Kas oled kindel, et soovid kinnitada, kuigi kõik taotletavad eritingimused ei ole kinnitatud?")}", do_save);
  }
  else
  {
    do_save();
  }
}
function do_save()
{
  $('form#form_save').submit();
}
% endif:
</script>
% endif

