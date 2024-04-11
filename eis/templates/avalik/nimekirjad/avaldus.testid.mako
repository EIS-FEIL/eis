<%inherit file="/common/formpage.mako"/>
<%def name="draw_tabs()">
<% c.tab1 = 'testivalik' %>
<%include file="avaldus.tabs.mako"/>
</%def>

<%def name="page_title()">
${_("Eksamile registreerimise taotluse sisestamine")}
</%def>      

<%def name="draw_before_tabs()">
<h1>${c.kasutaja.nimi}</h1>
</%def>

<%def name="breadcrumbs()">
${h.crumb(_("Tsentraalsed testid"))}
${h.crumb(_("Testi sooritajate määramine"), h.url('nimekirjad_testimiskorrad'))} 
${h.crumb(_("Avaldus"))}
</%def>

<%def name="active_menu()">
<% c.menu1 = 'ekktestid' %>
</%def>

${h.form_search(url=h.url('nimekirjad_avaldus_testid', id=c.kasutaja.id))}

<div class="d-flex flex-wrap mb-2">
  ${h.flb(_("Testi liik"), 'testiliik','mr-5')}
  <div>
    ${h.select('testiliik', c.testiliik, c.opt_testiliigid, onchange="this.form.submit()")}
  </div>
</div>

${h.end_form()}

<table  class="table table-borderless table-striped mb-3" width="100%">
  <caption>${_("Valitud testid")}</caption>
  <thead>
    <tr>
      ${h.th(_("Valitud test"))}
      ${h.th(_("Testimiskord"))}
      ${h.th(_("Testi liik"), class_="d-none d-lg-table-cell")}
      ${h.th(_("Soorituskeel"), class_="d-none d-lg-table-cell")}
      ${h.th(_("Soorituspiirkond"), class_="d-none d-lg-table-cell")}
      ${h.th(_("Olek"))}
      ${h.th(_("Soovib konsultatsiooni"), class_="d-none d-xl-table-cell")}
      ${h.th(_("Tugiisik"), class_="d-none d-xl-table-cell")}
      ${h.th(_("Märkus"), class_="d-none d-xl-table-cell")}
      <th></th>
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
      <!--s=${rcd.id}-->
      % if rcd.kursus_kood:
      (${rcd.kursus_nimi})
      % endif
      </td>
      <td>${testimiskord.tahised}</td>
      <td class="d-none d-lg-table-cell">
        ${test.testiliik_nimi}
      </td>
      <td class="d-none d-lg-table-cell">
        ${model.Klrida.get_lang_nimi(rcd.lang)}
      </td>
      <td class="d-none d-lg-table-cell">
        ${rcd.piirkond_nimi}
        % if testimiskord.reg_kohavalik:
        <div>${rcd.kohavalik_nimi}</div>
        % endif
      </td>
      <td>${rcd.staatus_nimi}</td>
      <td class="d-none d-xl-table-cell">
        % if rcd.test.on_tseis:
        ${h.sbool(rcd.soovib_konsultatsiooni)}
        % else:
        -
        % endif
      </td>
      <td class="d-none d-xl-table-cell">
        <% sooritused = list(rcd.sooritused) %>
        % for tos in sooritused:
        <% tugik = tos.tugiisik_kasutaja %>
        % if tugik:
        <div>
          ${tugik.nimi}
          % if len(sooritused) > 1:
          (${tos.testiosa.nimi})
          % endif
        </div>
        % endif
        % endfor
      </td>
      <td class="d-none d-xl-table-cell">
        ${rcd.reg_markus}
      </td>
      <td class="text-right">
        ${h.btn_to_dlg('', h.url('nimekirjad_avaldus_edit_test',
        sooritaja_id=rcd.id, id=c.kasutaja.id),
        title=_("Muuda registreeringut"), level=0,
        dlgtitle=rcd.test.nimi, mdicls='mdi-file-edit', size='md')}

        % if not rcd.muutmatu and rcd.kool_voib_tyhistada(c.user.koht_id, test.testiliik_kood):
        ${h.remove(h.url('nimekirjad_avaldus_delete_test', id=c.kasutaja.id, sooritaja_id=rcd.id))}
        % endif
      </td>
    </tr>
    % endfor
  </tbody>
  <tfoot>
    <tr>
      <td colspan="10" class="fh">
        ${h.btn_to_dlg(_("Lisa"), h.url('nimekirjad_avaldus_otsitestid',
        kasutaja_id=c.kasutaja.id, testiliik=c.testiliik), 
        title=_("Vali uus test"),
        dlgtitle=_("Testide valimine"), size='lg',
        mdicls='mdi-plus')}
      </td>
    </tr>
  </tfoot>
</table>

${h.form_save(None)}
${h.hidden('testiliik', c.testiliik)}
<%include file="/ekk/regamine/rahvusvaheline_eksam_avaldus.mako"/>

% if c.testiliik == const.TESTILIIK_SISSE:
<div class="form-wrapper-lineborder my-1">
  <div class="form-group row">
    ${h.flb3(_("E-post"),'k_epost')}
    <div class="col-md-9 err-parent">
      ${h.text('k_epost', c.kasutaja.epost, ronly=False, size=40)}
    </div>
  </div>
  <div class="form-group row">  
    ${h.flb3(_("Korda e-posti aadressi"),'epost2')}
    <div class="col-md-9">
      ${h.text('epost2', c.kasutaja.epost, ronly=False, size=40)}
    </div>
  </div>
</div>
% endif

% if len(c.ajalugu):
<table  class="table table-borderless table-striped my-1" width="100%">
  <caption>${_("Sama liiki testide sooritamiste ajalugu")}</caption>
  <thead>
    <tr>
      ${h.th(_("Test"))}
      ${h.th(_("Testimiskord"))}
      ${h.th(_("Testi liik"))}
      ${h.th(_("Soorituskeel"))}
      ${h.th(_("Kuupäev"))}
      ${h.th(_("Olek"))}
      ${h.th(_("Tulemus"))}
      ${h.th(_("Märkus"))}
    </tr>
  </thead>
  <tbody>
    % for rcd in c.ajalugu:
    <tr>
      <td>${rcd.testimiskord.test.nimi}
      <!--s=${rcd.id}-->
      </td>
      <td>${rcd.testimiskord.tahised}</td>
      <td>${rcd.test.testiliik_nimi}</td>
      <td>${model.Klrida.get_lang_nimi(rcd.lang)}</td>
      <td>${rcd.millal}</td>
      <td>${rcd.staatus_nimi}</td>
      <td>${rcd.get_tulemus()}</td>
      <td>${rcd.reg_markus}</td>
    </tr>
    % endfor
  </tbody>
</table>
% endif

<div class="d-flex flex-wrap">
  <div class="flex-grow-1">
    ${h.submit(_("Tagasi"), id="tagasi", mdicls2='mdi-arrow-left-circle')}
##    ${h.btn_to(_("Tagasi"), h.url('nimekirjad_avaldus_isikuandmed', id=c.kasutaja.id, testiliik=c.testiliik), mdicls='mdi-arrow-left-circle', level=2)}
  </div>
  <div>
    ${h.submit(_("Jätka"), id='jatka', mdicls2='mdi-arrow-right-circle')}
  </div>
</div>

${h.end_form()}

<%include file="avaldus.katkestus.mako"/>                              
