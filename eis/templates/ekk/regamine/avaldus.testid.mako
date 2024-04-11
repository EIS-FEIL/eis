<%inherit file="/common/formpage.mako"/>
<%def name="draw_tabs()">
<% c.tab1 = 'testivalik' %>
<%include file="avaldus.tabs.mako"/>
</%def>

<%def name="page_title()">
${_("Eksamile registreerimise taotluse sisestamine")}
</%def>      
<%def name="active_menu()">
<% c.menu1 = 'regamised' %>
</%def>

<%def name="breadcrumbs()">
${h.crumb(_("Registreerimine"), h.url('regamised'))} 
${h.crumb(_("Registreerimise taotluse sisestamine"))}
</%def>

${h.form_search(url=h.url('regamine_avaldus_testid', id=c.kasutaja.id))}

<div class="gray-legend p-3 filter-w">
  <div class="row filter">
    ${h.flb3(_("Testi liik"),'testiliik', 'text-md-right')}
    <div class="col-md-6">
      ${h.select('testiliik', c.testiliik, c.opt.testiliik, onchange="this.form.submit()", wide=False, style="min-width:200px")}
    </div>
  </div>
</div>
${h.end_form()}

<table  class="table table-borderless table-striped" width="100%">
  <caption>${_("Valitud testid")}</caption>
  <thead>
    <tr>
      ${h.th(_("Valitud test"))}
      ${h.th(_("Testimiskord"))}
      ${h.th(_("Testi liik"), class_="d-none d-lg-table-cell")}
      ${h.th(_("Soorituskeel"), class_="d-none d-lg-table-cell")}
      ${h.th(_("Soorituspiirkond"), class_="d-none d-lg-table-cell")}
      ${h.th(_("Olek"))}
      ${h.th(_("Soovib konsultatsiooni"), class_="d-none d-lg-table-cell")}
      ${h.th(_("Tugiisik"), class_="d-none d-lg-table-cell")}
      ${h.th(_("Märkus"), class_="d-none d-lg-table-cell")}
      <th colspan="2"></th>
    </tr>
  </thead>
  <tbody>
    % for rcd in c.sooritajad:
    <%
      test = rcd.test
      testimiskord = rcd.testimiskord
    %>
    <tr>
      <td>${test.nimi}
        % if rcd.kursus_kood:
        (${rcd.kursus_nimi})
        % endif
        <!--s=${rcd.id}-->
      </td>
      <td>${testimiskord.tahised}</td>
      <td class="d-none d-lg-table-cell">
        ${test.testiliik_nimi}</td>
      <td class="d-none d-lg-table-cell">
        ${model.Klrida.get_lang_nimi(rcd.lang)}</td>
      <td class="d-none d-lg-table-cell">
        ${rcd.piirkond_nimi}
        % if testimiskord.reg_kohavalik:
        <div>${rcd.kohavalik_nimi}</div>
        % endif
      </td>
      <td>${rcd.staatus_nimi}</td>
      <td class="d-none d-lg-table-cell">
        % if test.on_tseis:
        ${h.sbool(rcd.soovib_konsultatsiooni)}
        % else:
        -
        % endif
      </td>
      <td class="d-none d-lg-table-cell">
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
      <td class="d-none d-lg-table-cell">
        ${rcd.reg_markus}</td>
      <td>
        ${h.btn_to_dlg('', h.url('regamine_avaldus_edit_test',
        sooritaja_id=rcd.id, id=c.kasutaja.id), 
        title=_("Muuda"), dlgtitle=test.nimi, mdicls='mdi-file-edit', level=0)}
      </td>
      <td>${h.remove(h.url('regamine_avaldus_delete_test', id=c.kasutaja.id, sooritaja_id=rcd.id))}</td>
    </tr>
    % endfor
  </tbody>
  <tfoot>
    <tr>
      <td colspan="10" class="fh">
        ${h.btn_to_dlg(_("Lisa"), h.url('regamine_avaldus_otsitestid',
        kasutaja_id=c.kasutaja.id, testiliik=c.testiliik), 
        title=_("Testide valimine"),
        width=1100, size='lg')}
      </td>
    </tr>
  </tfoot>
</table>

${h.form_save(None)}
${h.hidden('testiliik', c.testiliik)}
<%include file="rahvusvaheline_eksam_avaldus.mako"/>

% if c.testiliik == const.TESTILIIK_TASE:
<div class="form-wrapper">
  <div class="form-group row">
    <label class="font-weight-bold col-lg-3">
      ${_("Õppis eesti keelt")}
      (${_("valikuid võib olla rohkem kui üks")})
    </label>
    <div class="col-lg-9">
      <%include file="te_oppekohtet.mako"/>
    </div>
  </div>
  <% te_data = c.kasutaja.te_data %>
  <div class="form-group row">
    ${h.flb3(_("Töövaldkond"),'f_tvaldkond_kood')}
    <div class="col-md-9">
      ${h.select('f_tvaldkond_kood', te_data.tvaldkond_kood, 
      c.opt.klread_kood('TVALDKOND', vaikimisi=te_data.tvaldkond_kood), 
      empty=True, wide=False)}
      % if not c.is_edit and te_data.tvaldkond_kood == const.TVALDKOND_MUU:
      ${te_data.tvaldkond_muu}
      % endif
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Amet"),'f_amet_muu')}
    <div class="col-md-9">
      ${h.text('f_amet_muu', te_data.amet_muu)}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Haridus"),'f_haridus_kood')}
    <div class="col-md-9">
      ${h.select('f_haridus_kood', te_data.haridus_kood, 
      c.opt.klread_kood('HARIDUS', vaikimisi=te_data.haridus_kood), 
      empty=True, wide=False)}
    </div>
  </div>
</div>

% endif

% if len(c.ajalugu):
<table  class="table table-borderless table-striped" width="100%">
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
        % if rcd.kursus_kood:
        (${rcd.kursus_nimi})
        % endif
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
    ${h.btn_to(_("Tagasi"), h.url('regamine_avaldus_edit_isikuandmed', id=c.kasutaja.id), mdicls='mdi-arrow-left-circle', level=2)}
  </div>
  <div>
    ${h.submit(_("Jätka"), id='jatka', mdicls2='mdi-arrow-right-circle')}
  </div>
</div>
${h.end_form()}
