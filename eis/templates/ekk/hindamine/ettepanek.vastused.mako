<% 
   vastvorm_kood = c.toimumisaeg.testiosa.vastvorm_kood
   c.testimiskord = c.toimumisaeg.testimiskord
   c.test = c.testimiskord.test
   prefix1 = 'hk-0.hmine'
%>
<%namespace name="sisu" file="/ekk/sisestamine/vastused_sisu.mako"/>

${h.form_save(c.testiylesanne.id, autocomplete='off')}
<table width="100%" class="form border tbl-sisestamine"  cellpadding="4">
  <caption>${_("Hindamiskogum")}: ${c.hindamiskogum.tahis} ${c.hindamiskogum.nimi} <!--${c.hindamiskogum.id}--></caption>
  <col width="150px"/>
  <tbody>
  <% 
     ty = c.testiylesanne
     ty_n = 0
     valikute_arv = ty.on_valikylesanne and ty.valikute_arv or 1 
     valik_vy = valikute_arv > 1 and c.hindamine and c.hindamine.get_vy_by_ty(ty)
  %>
  % for valik_seq in range(1, valikute_arv+1):
    <% 
      vy = ty.get_valitudylesanne(c.komplekt, valik_seq)
      valitud = valik_vy == vy or not valik_vy and valik_seq == 1      
    %>
    ${sisu.tr_testiylesanne(ty, valik_seq, valikute_arv, valitud,
                            '%s.ty-%d' % (prefix1, ty_n), c.hindamine, vy,
                            None, None, None
                            )}
  % endfor
  </tbody>
</table>

${h.submit(_("Salvesta"), id='kinnita')}
${h.end_form()}

<script>
## formencode pandud kole teade "Erineb" teisendatakse punaseks kastiks
$(function(){
$.each($('.error'), function(n, item){
  $(item).closest('table.showerr').addClass('form-control').addClass('is-invalid');
##  $(item).siblings('span.error-message[text()="Erineb"]').remove('');
});

## valikylesannete korral muudame mittevalitud valikud disabled olekusse, välja arvatud valiku tegemise raadionupp
$('input.valikylesanne[type="radio"]').change(function(){
 $.each($('input.valikylesanne[name="'+$(this).attr('name')+'"]'), function(n, item){
  $(item).closest('tr.tr-sisestamine').find('input,select').filter(':not(.valikylesanne)').attr('disabled', !$(item).prop('checked'));
  $(item).closest('td').find('span[id="valikradio2"]>input').prop('checked', $(item).prop('checked'));
 });
}).change();
## change() teeb dirty=true, tyhistame selle
dirty=false;
});
</script>

