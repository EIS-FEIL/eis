## testiruumiga seotud suulise hindaja hindamine, ruumi sooritajate loetelu
<%
   testikoht = c.testiruum.testikoht
   toimumisaeg = testikoht.toimumisaeg
   test = toimumisaeg.testimiskord.test
   opt_tpr = []
   for tpr in c.testiruum.testiprotokollid:
      opt_tpr.append((tpr.id, tpr.tahis))
%>
<div class="question-status d-flex p-3">
  <div class="item mr-5">
    ${h.flb(_("Test"),'test_nimi')}
    <div id="test_nimi">
      ${test.nimi}
      % if c.is_debug:
      ${toimumisaeg.tahised}
      % else:
      ${toimumisaeg.testiosa.tahis}
      % endif
    </div>
  </div>
  <div class="item mr-5">
    ${h.flb(_("Toimumise aeg"),'ruum_algus')}
    <div id="ruum_algus">
      ${h.str_from_date(c.testiruum.algus)}
    </div>
  </div>
  <div class="item mr-5">
    ${h.flb(_("Soorituskoht"),'koht_nimi')}
    <div id="koht_nimi">
      ${testikoht.koht.nimi}
      ${c.testiruum.tahis}
    </div>
  </div>
  % if c.is_devel:
  <div class="item mr-5">
    ${h.flb(_("Tööde arv"), 'toode_arv')}
    <div id="toode_arv">
      ${c.labiviija.toode_arv}
    </div>
  </div>
  <div class="item mr-5">
    ${h.flb(_("Hinnatud tööde arv"), 'hinnatud_toode_arv')}
    <div id="hinnatud_toode_arv">
      ${c.labiviija.hinnatud_toode_arv}
    </div>
  </div>
  % endif
</div>
      
${h.form_search(url=h.url_current('index', testiruum_id=c.testiruum.id))}
<div class="gray-legend p-3 filter-w">
  <div class="row filter">
    ${h.flb3(_("Protokollirühm"),'testiprotokoll_id', 'text-md-right')}
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.select('testiprotokoll_id', c.testiprotokoll_id, opt_tpr, empty=True)}
      </div>
    </div>
    <div class="col d-flex justify-content-end align-items-end">
      <div class="form-group">
        ${h.btn_search()}
      </div>
    </div>
  </div>
</div>
${h.end_form()}

${h.form_save(None)}
<div class="listdiv">
<%include file="vastajad_list.mako"/>
</div>

${h.button(_("Alusta hindamist"), class_='valikuline vst-all', id="alusta")}
${h.end_form()}

<%
  if c.app_ekk:
     url = h.url('hindamine_hindajavaade_shindamised', toimumisaeg_id=c.toimumisaeg.id, hindaja_id=c.labiviija.id)
  else:
     url = h.url('shindamine_hindamised', hindaja_id=c.labiviija.id)
%>
${h.form(url, method='get', id='forminter')}
${h.end_form()}
<script>
$('button#alusta').click(function(){
  var f = $('form#forminter');
  f.html('');
  $('#form_save input.sooritus:checked').each(function(){
    f.append($('<input type="hidden" name="sooritus_id"/>').val(this.value));
  });
  f.submit();
});
</script>
