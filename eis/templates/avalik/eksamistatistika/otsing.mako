<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Testide tulemuste statistika")}
</%def>      
<%def name="breadcrumbs()">
% if c.user.is_authenticated:
${h.crumb(_("Muud"))}
${h.crumb(_("Testide tulemuste statistika"), h.url('eksamistatistika'))}
% endif
</%def>
<%def name="require()">
<%
  c.includes['plotly'] = True
%>
</%def>

<%def name="active_menu()">
<% c.menu1 = c.user.is_authenticated and 'muud' or 'eksamistatistika' %>
</%def>

<h1>${_("Testide tulemuste statistika")}</h1>
<% info = model.Abiinfo.get_info(model.Abiinfo.EKSAMISTATISTIKA) %>
% if info and info.sisu:
${h.alert_notice(info.sisu.replace('\n', ' <br/>'), False)}
% endif

% if c.testityyp == const.TESTILIIK_POHIKOOL and c.aasta == 2020:
${h.alert_notice("2020. aastal toimus ainult eesti keel teise keelena põhikooli lõpueksam. Eksamil osalemine oli vabatahtlik.", False)}
% endif

${h.form_search()}

${h.rqexp(True, _("Palun esitada vähemalt kaks parameetrit neist kolmest: eksami tüüp, aasta, testi nimetus"))}
<div class="gray-legend p-3 filter-w">
  ##${h.toggle_filter()}
  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Testi tüüp"),'testityyp')}
        ${h.select('testityyp', c.testityyp, c.opt_testityyp, empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Aasta"),'aasta')}
        ${h.select('aasta', c.aasta, c.opt_aasta, empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Test"),'test_id')}
        ${h.select('test_id', c.test_id, c.opt_test, empty=True)}
      </div>
    </div>
    <div class="col d-flex justify-content-end align-items-end">
      <div class="form-group">
        ${h.button(_("Tühjenda"), onclick="reset_opt()", level=2)}
        <span class="filter">
          ${h.submit(_("Excel"), id='csv', level=2)}
          ${h.btn_search()}
        </span>
      </div>
    </div>
  </div>

  <hr class="m-2 filter-distrib"/>
  
  <div class="row filter filter-distrib" style="display:none">
    <div class="col-md-1">
      ${h.flb(_("Jaotus"),'jaotus')}
    </div>
    <div class="col-md-11" id="jaotus">
      <div class="row">
        <div class="col-12 col-md-6 col-lg-4">
          <div class="form-group">        
            ${h.flb(_("Soo järgi"),'sugu')}
            <%
              opt_all = [('', ' '), ('X', _("Vali kõik"))]
              opt_sugu = opt_all + [(const.SUGU_N, _("Tüdrukud")), (const.SUGU_M, _("Poisid"))]
            %> 
            ${h.select('sugu', c.sugu, opt_sugu, multiple=True)}
          </div>
        </div>
        <div class="col-12 col-md-6 col-lg-4 filter1 filter-t19 filter-r1 filter-r1-et2 filter-r filter-p filter-p-et2">
          <div class="form-group">
            ${h.flb(_("Õppeasutuse tüübi järgi"),'koolityyp')}
            ${h.select('koolityyp', c.koolityyp, opt_all + c.opt_koolityyp, multiple=True)}
          </div>
        </div>
        <div class="col-12 col-md-6 col-lg-4 filter1 filter-t19 filter-r1 filter-r1-et2 filter-r filter-p filter-p-et2">
          <div class="form-group">
            ${h.flb(_("Õppekeele järgi"),'oppekeel')}
            ${h.select('oppekeel', c.oppekeel, opt_all + const.EHIS_LANG_OPT, multiple=True)}
          </div>
        </div>
        <div class="col-12 col-md-6 col-lg-4 filter1 filter-r1 filter-r1-et2 filter-r filter-p filter-p-et2">
          <div class="form-group"> 
            ${h.flb(_("Õppevormi järgi"),'oppevorm')}
            ${h.select('oppevorm',c.oppevorm, opt_all + c.opt.OPPEVORM, multiple=True)}
          </div>
        </div>
        <div class="col-12 col-md-6 col-lg-4 filter1 filter-t19 filter-r1 filter-r1-et2 filter-r filter-p filter-p-et2">
          <div class="form-group">
            ${h.flb(_("Soorituskeele järgi"),'soorituskeel')}  
            ${h.select('soorituskeel', c.soorituskeel, opt_all + c.opt.SOORKEEL, multiple=True)}
          </div>
        </div>
        <div class="col-12 col-md-6 col-lg-4 filter1 filter-t19 filter-r1 filter-r1-et2 filter-r filter-p filter-p-et2">
          <div class="form-group">
            ${h.flb(_("Maakonna järgi"),'maakond')}
            ${h.select('maakond', c.maakond,  opt_all + (c.opt_mk or []),  multiple=True)}
          </div>
        </div>
        <%
          ## EKK vaates kuvada alati, avalikus vaates ainult teatud testiliigi korral
          fcls = (c.app_ekk and "filter-r filter-t19 " or "") + "filter1 filter-r1 filter-r1-et2 filter-r2 filter-p filter-p-et2" 
        %>
        <div class="col-12 col-md-6 col-lg-4 ${fcls}">
          <div class="form-group">
            ${h.flb(_("KOV järgi"),'kov')}
            ${h.select('kov', c.kov,  opt_all + (c.opt_kov or []), multiple=True)}
          </div>
        </div>
        <%
          ## mitte kuvada avalikus vaates riigieksami 2022 korral
          fcls = c.app_eis and 'filter-not-r22' or ''
          fcls = '' # ES-3280 piirangu eemaldas ES-3315
        %>
        <div class="col-12 col-md-6 col-lg-4 filter1 filter-r1 filter-r1-et2 filter-r2 ${fcls}">
          <div class="form-group">
            ${h.flb(_("Kooli järgi"),'ko')}
            ${h.select('ko', c.koolinimi_id, opt_all + (c.opt_kool or []), multiple=True, size=8, class_='koolinimi_id')}
          </div>
        </div>
      </div>
    </div>
  </div>

  <hr class="m-2 filterdisplay"/>

  <div class="row filter filterdisplay">
    <div class="col-md-1">
      ${h.flb(_("Kuvada veerud"),'kuvadaveerud')}
    </div>
    <div class="col-md-11" id="kuvadaveerud">
      <div class="row">
        <div class="col-12 col-md-4 col-lg-3">
          <div class="form-group">
                  ${h.checkbox('col_eksaminandid', 1, checked=c.col_eksaminandid, label=_("Sooritajaid"))}
                  <br/>
                  ${h.checkbox('col_maxpallid', 1, checked=c.col_maxpallid, label=_("Max võimalik pallide arv"))}
                  <br/>
                  ${h.checkbox('col_keskmine', 1, checked=c.col_keskmine, label=_("Keskmine"))}
                  <br/>
                  ${h.checkbox('col_keskminepr', 1, checked=c.col_keskminepr, label=_("Keskmine (%)"))}
                  <br/>
                  ${h.checkbox('col_halve', 1, checked=c.col_halve, label=_("St hälve"))}
                  <br/>
                  ${h.checkbox('col_mediaan', 1, checked=c.col_mediaan, label=_("Mediaan"))}
          </div>
        </div>
        <div class="col-12 col-md-4 col-lg-3">
          <div class="form-group">
                  ${h.checkbox('col_minsaajad', 1, checked=c.col_minsaajad, label=_("Min punktide saajad"))}
                  <br/>
                  ${h.checkbox('col_maxsaajad', 1, checked=c.col_maxsaajad, label=_("Max punktide saajad"))}
                  <br/>
                  ${h.checkbox('col_min', 1, checked=c.col_min, label=_("Min"))}
                  <br/>
                  ${h.checkbox('col_max', 1, checked=c.col_max, label=_("Max"))}
                  <br/>
                  
                  ${h.checkbox('col_aup', 1, checked=c.col_aup, label=_("AUP"))}
                  <br/>
                  ${h.checkbox('col_yup', 1, checked=c.col_yup, label=_("ÜUP"))}
          </div>
        </div>
        <div class="col-12 col-md-4 col-lg-3">
          <div class="form-group">
            ${_("Kuni {n}% pallidest").format(n=h.posfloat('alla', c.alla, size=3, maxvalue=100))}
            <br/>
            ${h.checkbox('col_alla20', 1, checked=c.col_alla20, label="sooritajate arv")}
            <br/>
            ${h.checkbox('col_alla20pr', 1, checked=c.col_alla20pr, label="sooritajate protsent")}
          </div>
        </div>
        <div class="col-12 col-md-4 col-lg-3">
          <div class="form-group">
            ${_("Vähemalt {n}% pallidest").format(n=h.posfloat('yle', c.yle, size=3, maxvalue=100))}
            <br/>
            ${h.checkbox('col_yle80', 1, checked=c.col_yle80, label="sooritajate arv")}
            <br/>
            ${h.checkbox('col_yle80pr', 1, checked=c.col_yle80pr, label="sooritajate protsent")}
          </div>
        </div>
        <div class="col-12 col-md-4 col-lg-3">
          <div class="form-group">
                  <span class="filter1 filter-r2 filter-p-et2">
                  ${h.checkbox('col_tase_b1', 1, checked=c.col_tase_b1, label="B1 (%)")}
                  <br/>
                  </span>
                  <span class="filter1 filter-r2 filter-r1-et2">                  
                  ${h.checkbox('col_tase_b2', 1, checked=c.col_tase_b2, label="B2 (%)")}
                  <br/>
                  </span>
                  <span class="filter1 filter-r2">                  
                  ${h.checkbox('col_tase_c1', 1, checked=c.col_tase_c1, label="C1 (%)")}
                  <br/>
                  ${h.checkbox('col_tase_c2', 1, checked=c.col_tase_c2, label="C2 (%)")}
                  <br/>
                  ${h.checkbox('col_tasemeta', 1, checked=c.col_tasemeta, label=_("Taset mitte saavutanud") + " (%)")}
                  <br/>
                  </span>
                  <span class="filter1 filter-r1-et2">
                  ${h.checkbox('col_tase_c1t', 1, checked=c.col_tase_c1t, label=_("C1 tasemetunnistuse esitanud"))}
                  </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>

${h.end_form()}

<div class="listdiv">
  % if not c.items and c.items != '':
  ${_("Otsingu tingimustele vastavaid andmeid ei leitud")}
  % elif c.items:
  <%include file="otsing_list.mako"/>
  % endif 
</div>

<script>
var opt_data = [
        % for testityyp, aasta, test_id in c.opt_data:
        ["${testityyp}","${aasta}","${test_id}"],
        % endfor
        null];
        var opt_testityyp = [
        % for row in c.opt_testityyp:
        ["${row[0]}","${h.jsparam(row[1])}"],
        % endfor
        null];
        var opt_aasta = [
        % for row in c.opt_aasta:
        ["${row[0]}","${h.literal(row[1])}"],
        % endfor
        null];
        var opt_test = [
        % for row in c.opt_test:
        ["${row[0]}","${h.jsparam(row[1])}"],
        % endfor
        null];
var testid_et2 = ${str(c.testid_et2)};
var testid_pet2 = ${str(c.testid_pet2)};
</script>
% if c.min_js:
${h.javascript_link('/static/eis/eksamistatistika.js')}
% else:
${h.javascript_link('/static/eis/source/eksamistatistika.js')}
% endif
