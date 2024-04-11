<%inherit file="/common/formpage.mako"/>
<%def name="draw_tabs()">
<% c.tab1 = 'kinnitamine' %>
<%include file="avaldus.tabs.mako"/>
</%def>

<%def name="page_title()">
${_("Eksamile registreerimise taotluse sisestamine")}
</%def>      

<%def name="breadcrumbs()">
${h.crumb(_("Tsentraalsed testid"))}
${h.crumb(_("Testi sooritajate määramine"), h.url('nimekirjad_testimiskorrad'))} 
${h.crumb(_("Avaldus"))}
</%def>

<%def name="active_menu()">
<% c.menu1 = 'ekktestid' %>
</%def>

<%def name="draw_before_tabs()">
<h1>${c.kasutaja.nimi}</h1>
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

<%
  c.sooritajad = list(c.kasutaja.get_reg_sooritajad(c.testiliik))
  on_tasu = len([r for r in c.sooritajad if r.tasu])
%>
<table  class="table table-borderless table-striped" width="100%">
  <caption>${_("Valitud testid")}</caption>
  <thead>
    <tr>
      ${h.th(_("Valitud test"))}
      ${h.th(_("Soorituskeel"))}
      ${h.th(_("Soorituspiirkond või -koht"))}
      % if on_tasu:
      ${h.th(_("Tasu"))}
      % endif
    </tr>
  </thead>
  <tbody>
    % for rcd in c.sooritajad:
    <%
      testimiskord = rcd.testimiskord
      test = rcd.test
    %>
    <tr>
      <td>${test.nimi}
        % if rcd.kursus_kood:
        (${rcd.kursus_nimi})
        % endif
      </td>
      <td>${model.Klrida.get_lang_nimi(rcd.lang)}</td>
      <td>${rcd.piirkond_nimi}
        % if testimiskord.reg_kohavalik:
        <div>${rcd.kohavalik_nimi}</div>
        % endif
      </td>
      % if on_tasu:
      <td>
        % if rcd.tasu:
        ${h.mstr(rcd.tasu) or ''}
        ${rcd.tasutud and _("tasutud") or _("tasumata")}
        % endif
      </td>
      % endif
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
      </td>
    </tr>
  </tbody>
</table>
% endif

<div class="d-flex flex-wrap">
  <div class="flex-grow-1">
    ${h.btn_to(_("Tagasi"), h.url('nimekirjad_avaldus_testid', id=c.kasutaja.id, testiliik=c.testiliik), mdicls='mdi-arrow-left-circle', level=2)}
    ${h.btn_to(_("Katkesta"), h.url('nimekirjad_avaldus_delete_kinnitamine', id=c.kasutaja.id, testiliik=c.testiliik), method='delete', confirm=u'Kas oled kindel, et soovid registreerimise katkestada?', class_='confirm-yesno', level=2)}
  </div>
  <div>
    <span class="mx-2">
      ${h.checkbox('regteade', 1, checked=True, label=_("Saata registreerimise teade"))}
    </span>
    ${h.submit(_("Kinnita avaldus"))}
  </div>
</div>
${h.end_form()}

<% c.continue_url = h.url('nimekirjad_avaldus_kinnitamine', id=c.kasutaja.id, testiliik=c.testiliik) %>
<%include file="avaldus.katkestus.mako"/>               
