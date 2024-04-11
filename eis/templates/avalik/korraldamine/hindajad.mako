## -*- coding: utf-8 -*- 
## See sakk on olemas siis, kui vastamise vorm on kirjalik ja toimumisaja
## andmetes on näidatud, et soorituskoht võib määrata hindajaid.

<%inherit file="/common/formpage.mako"/>
<%def name="page_title()">
${_("Testi korraldamine")} | ${c.test.nimi} ${h.str_from_date(c.toimumisaeg.alates)}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Tsentraalsed testid"))}
${h.crumb(_("Testi läbiviimise korraldamine"), h.url('korraldamised'))} 
${h.crumb('%s %s' % (c.test.nimi, c.toimumisaeg.tahised))}
${h.crumb(_("Hindajad"), h.url('korraldamine_hindajad', testikoht_id=c.testikoht.id))}
</%def>

<%def name="active_menu()">
<% c.menu1 = 'ekktestid' %>
</%def>

<%def name="page_headers()">
<style>
  tr.tr-warn > td { background-color: #fff0a5; }
</style>
</%def>

<%def name="draw_before_tabs()">
<h1>${_("Testi läbiviimise korraldamine")}</h1>
</%def>

<%def name="draw_tabs()">
<% c.tab1 = 'hindajad' %>
<%include file="tabs.mako"/>
</%def>

${h.form_search(url=h.url('korraldamine_hindajad',
testikoht_id=c.testikoht.id))}

<div class="gray-legend p-3">
  <div class="row">
    <div class="col-12 col-md-6">
      <%
        if c.testimiskord.sisaldab_valimit:
           valimis_values = [False, True]
        else:
           valimis_values = [None]
      %>
      % for valimis in valimis_values:
      <div>
      <% vsuff = valimis and 'v1' or '' %>
      <div class="row">
        <div class="col-6 col-md-6 text-right">
          % if valimis:
          ${h.flb(_("Valimi testisooritajate arv kokku"), f'arvk{vsuff}')}
          % elif valimis == False:
          ${h.flb(_("Mitte-valimi testisooritajate arv kokku"), f'arvk{vsuff}')}
          % else:
          ${h.flb(_("Testisooritajate arv kokku"), f'arvk{vsuff}')}
          % endif
        </div>
        <div class="col-6 col-md-6" id="arvk${vsuff}">
          <%
            cnt = c.testikoht.get_sooritajatearv(valimis=valimis)
            if valimis:
               c.cnt_valimis = cnt
            else:
               c.cnt_valimita = cnt
          %>
          <span class="brown">${cnt}</span>
          <% tehtud = c.testikoht.get_sooritajatearv(tehtud=True, valimis=valimis) %>
          % if tehtud:
          (${_("testi lõpetanud")} <span class="brown">${tehtud}</span>)
          % endif
        </div>
      </div>

      % for lang in c.toimumisaeg.testimiskord.get_keeled():
      <div class="row">
        <div class="col-6 col-md-6 text-right">
          ${h.flb(model.Klrida.get_lang_nimi(lang), f'arv{vsuff}_{lang}')}
        </div>
        <div class="col-6 col-md-6" id="arv${vsuff}_${lang}">
          <span class="brown">${c.testikoht.get_sooritajatearv(lang, valimis=valimis)}</span>
          % if tehtud:
          <% tehtud_l = c.testikoht.get_sooritajatearv(lang, tehtud=True, valimis=valimis) %>
          (${_("testi lõpetanud")} <span class="brown">${tehtud_l}</span>)      
          % endif
        </div>
      </div>
      % endfor
      </div>
      % endfor
    </div>
    <div class="col-12 col-md-6">
      <div class="row form-group">
        <div class="col-12 col-md-5 text-md-right">    
          ${h.flb(_("Hindamiskogum"),'hindamiskogum_id')}
        </div>
        <div class="col-12 col-md-5">
          ${h.select('hindamiskogum_id', c.hindamiskogum_id, c.hindamiskogumid_opt, empty=True)}
        </div>
        <div class="col-12 text-right col-md-2">
          ${h.btn_search()}
        </div>
      </div>
    </div>
  </div>
</div>

<% c.tab2 = c.tab2 == 'tab2' and 'tab2' or 'tab1' %>
${h.hidden('tab2', c.tab2)}
${h.end_form()}

<%namespace name="tab" file="/common/tab.mako"/>
<ul class="nav nav-pills hindajad-tabs" role="tablist">
${tab.subdraw('tab1', '', _('Hindajate kaupa'), c.tab2)}
${tab.subdraw('tab2', '', _('Hindamiskogumite kaupa'), c.tab2)}
</ul>

<div class="listdiv mt-2">
  <%include file="hindajad_list.mako"/>
</div>

% if c.toimumisaeg.hindaja1_maaraja == const.MAARAJA_KOHT or c.toimumisaeg.hindaja2_maaraja == const.MAARAJA_KOHT:
${h.btn_to_dlg(_("Kontrolli hindajate määramist"), h.url('korraldamine_new_hindaja', testikoht_id=c.testikoht.id, sub='kontroll'),
title=_("Hindajate määramise kontroll"), level=2, size='md')}
% endif

% if c.cnt_valimita:
% if c.toimumisaeg.hindaja1_maaraja in const.MAARAJA_KOHAD or c.toimumisaeg.hindaja2_maaraja in const.MAARAJA_KOHAD or c.toimumisaeg.hindaja1_maaraja in const.MAARAJA_KOHAD:
${h.btn_to_dlg(_("Lisa hindaja"), h.url('korraldamine_new_hindaja', testikoht_id=c.testikoht.id),
title=_("Hindaja lisamine"),width=700, level=2, mdicls='mdi-account-plus', size='md')}
% endif
% endif
% if c.testimiskord.sisaldab_valimit and c.cnt_valimis:
% if c.toimumisaeg.hindaja1_maaraja_valim in const.MAARAJA_KOHAD or c.toimumisaeg.hindaja2_maaraja_valim in const.MAARAJA_KOHAD or c.toimumisaeg.hindaja1_maaraja_valim in const.MAARAJA_KOHAD:
${h.btn_to_dlg(_("Lisa valimi hindaja"), h.url('korraldamine_new_hindaja', testikoht_id=c.testikoht.id, valimis=1),
title=_("Valimi hindaja lisamine"),width=700, level=2, mdicls='mdi-account-plus', size='md')}
% endif
% endif

<script>
  $('.nav.hindajad-tabs .nav-link').click(function(){
    var f = $('form#form_search');
    var val = this.id.substr(4);
    f.find('input[name="tab2"]').val(val);
    f.submit();
    return false;
  });
</script>
