<%inherit file="/common/formpage.mako"/>

<%def name="page_title()">
${_("Testi toimumise protokolli koostamine")} | ${c.toimumisprotokoll.tahistus}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Tsentraalsed testid"))}
${h.crumb(_("Testi toimumise protokolli koostamine"), h.url('protokollid'))}
${h.crumb(c.toimumisprotokoll.tahistus, h.url('protokoll_osalejad', toimumisprotokoll_id=c.toimumisprotokoll.id))}
</%def>

<%def name="draw_before_tabs()">
<%include file="before_tabs.mako"/>
</%def>

<%def name="draw_tabs()">
<%include file="tabs.mako"/>
</%def>

<%def name="active_menu()">
<% c.menu1 = 'ekktestid' %>
</%def>

${h.form_search(url=h.url('protokoll_osalejad', toimumisprotokoll_id=c.toimumisprotokoll.id))}
${h.hidden('testiruum_id', c.testiruum_id)}
${h.end_form()}
<script>
  $(function(){
  ## ruumi valikväljal ruumi muutmisel päritakse vorm uuesti
  $('form#form_save select[name="testiruum_id"]').change(function(){
    $('form#form_search input[name="testiruum_id"]').val($(this).val());
    $('form#form_search').submit();
  });
  });
</script>

${h.form_save(None, disablesubmit=True)}
% if c.test.testityyp in (const.TESTITYYP_EKK, const.TESTITYYP_AVALIK):
## konsultatsiooni sooritajaid ei sisestata
% if c.testimiskord.prot_tulemusega:
<%include file="/ekk/sisestamine/protokoll.osalejad_tulemusega_list.mako"/>
% else:
<%include file="/ekk/sisestamine/protokoll.osalejad_list.mako"/>
% endif
% endif

% if not c.ainult_opetaja_id:
% if not c.testimiskord.prot_tulemusega:
## prot_tulemusega korral läbiviijaid ei sisestata
<%include file="/ekk/sisestamine/protokoll.labiviijad_list.mako"/>
${_("Märkused")}
% else:
${_("Kooli käskkirja number, eksamikomisjoni liikmete eriarvamused, märkused")}
% endif
${h.textarea('markus', c.toimumisprotokoll.markus, rows=5)}
% endif
<br/>
<div class="d-flex">
  ${h.btn_to('CSV', h.url_current('download', id=c.toimumisprotokoll.id, format='csv'), level=2)}
  <div class="flex-grow-1 text-right">
    % if c.is_edit:
    ${h.submit()}
    % endif
  </div>
</div>
${h.end_form()}
