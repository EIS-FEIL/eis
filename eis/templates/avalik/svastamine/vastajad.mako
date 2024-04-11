<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Sooritajate nimistu")}
</%def>
<%def name="breadcrumbs()">
${h.crumb(_("Tsentraalsed testid"))}
${h.crumb(_("Intervjuu läbiviimine"), h.url('svastamised'))} 
${h.crumb(c.testiruum.testikoht.toimumisaeg.testimiskord.test.nimi + ', ' +
c.testiruum.testikoht.koht.nimi + ' ' + (c.testiruum.tahis or ''), h.url('svastamine_vastajad', testiruum_id=c.testiruum.id))} 
</%def>

<%def name="active_menu()">
<% c.menu1 = 'ekktestid' %>
</%def>
<h1>${_("Intervjuu läbiviimine")}</h1>
<%
   testikoht = c.testiruum.testikoht
   toimumisaeg = testikoht.toimumisaeg
%>
<div class="question-status d-flex p-3">
  <div class="item mr-5">
    ${h.flb(_("Test"), 'test_nimi')}
    <div id="test_nimi">
      ${c.test.nimi}
      ${c.testiosa.tahis}
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
</div>

${h.form_save(None)}
${h.hidden('staatus', '')}
<div class="listdiv pt-2">
<%include file="vastajad_list.mako"/>
</div>
${h.btn_to(_("Heli salvestamise kontroll"), h.url('svastamine_intervjuud', test_id=c.test.id, testiruum_id=c.testiruum.id), level=2)}

% if c.testiosa.vastvorm_kood == const.VASTVORM_SH:
${h.button(_("Alusta"), class_=f'valikuline vst-{const.S_STAATUS_REGATUD} vst-{const.S_STAATUS_ALUSTAMATA} vst-{const.S_STAATUS_POOLELI} vst-{const.S_STAATUS_KATKESTATUD}', id="alusta")}
% endif
##${h.button(_("Eemalda"), class_='valikuline vst-all', onclick="change_status('%s')" % const.S_STAATUS_EEMALDATUD, level=2)}

% if c.toimumisaeg.jatk_voimalik:
<%
  vst = f'valikuline vst-{const.S_STAATUS_PUUDUS} vst-{const.S_STAATUS_EEMALDATUD} vst-{const.S_STAATUS_TEHTUD} vst-{const.S_STAATUS_KATKESPROT}'
%>
${h.button(_("Ava lõpetatud test"), class_=vst, onclick="change_status('ava')", level=2)}
% endif

${h.end_form()}

${h.form(h.url('svastamine_intervjuud', test_id=c.test.id, testiruum_id=c.testiruum.id), method='get', id='forminter')}
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
