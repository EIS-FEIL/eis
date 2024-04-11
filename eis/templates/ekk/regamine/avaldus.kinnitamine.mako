<%inherit file="/common/formpage.mako"/>
<%def name="draw_tabs()">
<% c.tab1 = 'kinnitamine' %>
<%include file="avaldus.tabs.mako"/>
</%def>

<%def name="page_title()">
${_("Eksamile registreerimise taotluse sisestamine")}
</%def>      

<%def name="breadcrumbs()">
${h.crumb(_("Registreerimine"), h.url('regamised'))} 
${h.crumb(_("Registreerimise taotluse sisestamine"))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'regamised' %>
</%def>

${h.form_save(c.kasutaja.id)}
${h.hidden('testiliik', c.testiliik)}

<div class="gray-legend p-3 filter-w">
  <div class="d-flex">
    % if c.kasutaja.isikukood:
    <div class="item mr-5">
      ${h.flb(_("Isikukood"),'isikukood')}
      <div id="isikukood">
        ${c.kasutaja.isikukood}
      </div>
    </div>
    % else:
    <div class="item mr-5">
      ${h.flb(_("Sünniaeg"),'synnikpv')}
      <div id="synnikpv">
        ${h.str_from_date(c.kasutaja.synnikpv)}
      </div>
    </div>
    % endif
    <div class="item mr-5">
      ${h.flb(_("Eesnimi"),'eesnimi')}
      <div id="eesnimi">
        ${c.kasutaja.eesnimi}
      </div>
    </div>
    <div class="item mr-5">    
      ${h.flb(_("Perekonnanimi"),'perenimi')}
      <div id="perenimi">
        ${c.kasutaja.perenimi}
      </div>
    </div>
  </div>
</div>

<% kinnitamata = False %>
<table  class="table table-borderless table-striped" width="100%">
  <caption>${_("Valitud testid")}</caption>
  <thead>
    <tr>
      ${h.th(_("Valitud test"))}
      ${h.th(_("Soorituskeel"))}
      ${h.th(_("Soorituspiirkond või -koht"))}
      ${h.th(_("Tasu"))}
    </tr>
  </thead>
  <tbody>
    % for rcd in c.kasutaja.get_reg_sooritajad(c.testiliik):
    <% kinnitamata |= rcd.staatus == const.S_STAATUS_REGAMATA %>
    <tr>
      <td>${rcd.testimiskord.test.nimi}</td>
      <td>${model.Klrida.get_lang_nimi(rcd.lang)}</td>
      <td>${rcd.piirkond_nimi}</td>
      <td>
        % if rcd.tasu:
        ${h.mstr(rcd.tasu) or ''}
        ${h.checkbox('tasutud_%s' % (rcd.id), 1, checked=rcd.tasutud,
        label=_("tasutud"), class_='tasutud_')}
        % endif
      </td>
    </tr>
    % endfor
  </tbody>
</table>

% if c.tasu:
<table  class="table" width="100%">
  <tbody>
    <tr>
      <td class="fh" width="225px">${_("Tasumisele kuuluv summa")}</td>
      <td>${h.mstr(c.tasu)}
        ${h.checkbox('tasutud', 1, checked=c.tasutud, 
        label=_("Summa on tasutud"),
        onchange="$('input.tasutud_').prop('checked',$(this).prop('checked'))")}
      </td>
    </tr>
  </tbody>
</table>
% endif

<div class="d-flex flex-wrap">
  <div class="flex-grow-1">
    ${h.btn_to(_("Tagasi"), h.url('regamine_avaldus_testid', id=c.kasutaja.id, testiliik=c.testiliik), mdicls='mdi-arrow-left-circle', level=2)}
    % if kinnitamata:
    ${h.submit(_("Katkesta"), id="katkesta", level=2)}
    % endif
  </div>
  <div>
    <span class="ml-3">${h.checkbox('regteade', 1, checked=True, label=_("Saata registreerimise teade"))}</span>
    ${h.submit(_("Kinnita avaldus"))} 
  </div>
</div>
${h.end_form()}
