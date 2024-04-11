<%inherit file="komplektid.mako"/>

<%def name="breadcrumbs()">
${h.crumb(_("Testid"), h.url('testid'))} 
${h.crumb(c.test.nimi or _("Test"))} 
${h.crumb(_("Ülesanded"))}
</%def>

% if c.test.is_encrypted:
${h.alert_notice(_("Test on krüptitud"))}
% else:

${h.form_search(url=h.url('test_valitudylesanded', test_id=c.test.id))}
${h.hidden('testiosa_id', c.testiosa_id)}
${h.hidden('komplektivalik_id', c.komplektivalik_id)}
${h.hidden('komplekt_id', c.komplekt_id)}

<div class="gray-legend p-3 filter-w">
  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Testiosa"))}
        ${h.roxt(c.testiosa.tahis)}
      </div>
    </div>
    % if c.testiosa.on_alatestid:
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">        
        ${h.flb(_("Alatest"),'alatest_id')}
        <% 
         if c.komplektivalik:
           opt_alatestid = c.komplektivalik.opt_alatestid
         else:
           opt_alatestid = c.testiosa.opt_alatestid
        %>
        ${h.select('alatest_id', c.alatest_id, opt_alatestid, empty=True,
        onchange="$(this).parents('form')[0].submit();")}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">        
        ${h.flb(_("Plokk"),'testiplokk_id')}
        ${h.select('testiplokk_id', c.testiplokk_id, c.alatest and
        c.alatest.opt_testiplokid, empty=True, onchange="$(this).parents('form')[0].submit();")}
      </div>
    </div>
    % endif
  </div>
</div>
${h.end_form()}


% if len(c.items) == 0:
  % if not c.komplektivalik:
${h.alert_notice(_("Ühtki ülesandekomplekti pole loodud"))}
  % else:
${h.alert_notice(_("Ühtki ülesannet pole kirjeldatud"))}
  % endif
% else:

<div>
<%include file="valitudylesanded_list.mako"/>
</div>

% endif
<br/>
<div align="left">

% if c.can_update and not c.test.is_encrypted:
<% on_kursusi = len([r for r in c.test.testikursused if r.kursus_kood]) > 0 %>
  % if c.kursus or not on_kursusi:
${h.btn_to_dlg(_("Lisa komplekt"), h.url('test_testiosa_new_komplekt',
test_id=c.test.id, testiosa_id=c.testiosa.id, kursus=c.kursus, komplektivalik_id=c.komplektivalik_id, partial=True), 
title=_("Komplekt"), width=400, level=2)}
  % endif

 % if c.komplekt:
    % if c.komplekt.staatus==const.K_STAATUS_KOOSTAMISEL:
${h.btn_to_dlg(_("Muuda tähis/keel"), h.url('test_testiosa_edit_komplekt', test_id=c.test.id, 
testiosa_id=c.testiosa.id, komplektivalik_id=c.komplektivalik_id, id=c.komplekt.id, partial=True), 
title=_("Komplekt"), width=400, level=2)}

${h.btn_to(_("Vali ülesanded"), h.url('test_valitudylesanded', test_id=c.test.id, 
testiosa_id=c.testiosa.id, komplektivalik_id=c.komplektivalik_id, komplekt_id=c.komplekt_id, vali=1), level=2)}

${h.btn_to_dlg(_("Vali ülesanded failist"), h.url('test_komplekt_valimitu', test_id=c.test.id, 
testiosa_id=c.testiosa.id, komplektivalik_id=c.komplektivalik_id, komplekt_id=c.komplekt.id), 
title=_("Vali ülesanded failist"), width=800, level=2)}

${h.btn_to(_("Kinnita komplekt"), h.url('test_valitudylesanne', test_id=c.test.id,
id=c.komplekt.id, testiosa_id=c.testiosa.id, komplektivalik_id=c.komplektivalik_id, 
komplekt_id=c.komplekt.id, sub='kinnita'), method='put', level=2)}

    % endif

${h.btn_to(_("Eemalda komplekt"), h.url('test_testiosa_delete_komplekt', test_id=c.test.id, 
testiosa_id=c.testiosa.id, id=c.komplekt.id), method='delete', level=2)}

${h.btn_to(_("Kopeeri komplekt"), h.url('test_valitudylesanne', test_id=c.test.id,
id=c.komplekt.id, testiosa_id=c.testiosa.id, komplektivalik_id=c.komplektivalik_id, komplekt_id=c.komplekt.id, sub='kopeeri'), method='put', level=2)}

    % if c.komplekt.staatus == const.K_STAATUS_ARHIIV:
${h.btn_to(_("Too arhiivist välja"), h.url('test_valitudylesanne', test_id=c.test.id,
id=c.komplekt.id, testiosa_id=c.testiosa.id, komplektivalik_id=c.komplektivalik_id, komplekt_id=c.komplekt.id, sub='koosta'), method='put', level=2)}
    % elif c.test.avaldamistase not in (const.AVALIK_SOORITAJAD, const.AVALIK_OPETAJAD, const.AVALIK_MAARATUD):
${h.btn_to(_("Arhiveeri komplekt"), h.url('test_valitudylesanne', test_id=c.test.id,
id=c.komplekt.id, testiosa_id=c.testiosa.id, komplektivalik_id=c.komplektivalik_id, komplekt_id=c.komplekt.id, sub='arhiiv'), method='put', level=2)}
    % endif

${h.button(_("Ekspordi"), onclick="window.open('%s')" % h.url('test_komplekt_export', test_id=c.test.id,
komplekt_id=c.komplekt.id, format='html'), level=2)}

${h.btn_to(_("Kontrolli ja arvuta"), h.url('test_valitudylesanne', test_id=c.test.id,
id=c.komplekt.id, testiosa_id=c.testiosa.id, komplektivalik_id=c.komplektivalik_id, komplekt_id=c.komplekt.id, sub='kontroll'), method='put', level=2)}

  % endif

% endif
% endif
</span>
