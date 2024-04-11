<%inherit file="/common/formpage.mako"/>
<%def name="require()">
<%
c.includes['subtabs'] = True
c.includes['before_subtabs'] = True
c.includes['test'] = True
c.includes['form'] = True
c.includes['countdown'] = True
c.includes['ckeditor'] = True
%>
</%def>
<%def name="draw_tabs()">
<% c.tab1 = 'valitudylesanded' %>
<%include file="tabs.mako"/>
</%def>

<%def name="page_title()">
${_("Test")}: ${c.test.nimi or ''} | ${_("Ülesanded")}
</%def>      

<%def name="breadcrumbs()">
${h.crumb(_("Testid"), h.url('testid'))} 
${h.crumb(c.test.nimi or _("Test"))} 
${h.crumb(_("Komplektid"))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'testid' %>
</%def>
<% 
c.can_update = c.user.has_permission('ekk-testid', const.BT_UPDATE, c.test) and \
  c.test.staatus in (const.T_STAATUS_KOOSTAMISEL, const.T_STAATUS_KINNITATUD)
%>

<script>
function change_komplekt(field)
{
  var form = $(field).parents('form')[0];
  % if self.name.endswith('erialatestid.mako') or self.name.endswith('eelvaade.mako'):
    ## need vormid ei paku otsimist, otsima suundutakse valitudylesannetesse
     form.action = "${h.url('test_valitudylesanded', test_id=c.test.id)}";
  % endif
  form.submit();
}
function change_komplektivalik(field)
{
  $('#komplekt_id').val('');
  $('#alatest_id1').val('');
  $('#testiplokk_id').val('');
  change_komplekt(field);
}
function change_kursus(field)
{
  $('#komplektivalik_id').val('');  
  change_komplektivalik(field);
}
function change_testiosa(field)
{
  $('#kursus').val('');
  change_kursus(field);
}
</script>

% if c.testiosa:

${next.body()}

% endif

% if c.dialog_ylesanne:
  ${self.open_dialog('testiosa', '/ekk/testid/otsiylesanded.mako', _("Ülesande valik"), size='lg')}
% endif

% if c.dialog_komplekt:
  ${self.open_dialog('komplekt', '/ekk/testid/komplekt.mako', _("Komplekt"))}
% endif

<%def name="draw_before_subtabs()">
${h.form_search()}
<%
if not c.testiosa and len(c.test.testiosad):
   c.testiosa = c.test.testiosad[0]
   c.testiosa_id = c.testiosa.id
if c.testiosa and not c.komplektivalik and len(c.testiosa.komplektivalikud) == 1:
   c.komplektivalik = c.testiosa.komplektivalikud[0]
   c.komplektivalik_id = c.komplektivalik.id
if c.komplektivalik and not c.komplekt and len(c.komplektivalik.komplektid) == 1:
   c.komplekt = c.komplektivalik.komplektid[0]
   c.komplekt_id = c.komplekt.id
opt_kursused = c.test.opt_kursused
%>
<div class="gray-legend p-2 p-md-4 mb-4 py-4">
  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Testiosa"),'testiosa_id')}
        ${h.select('testiosa_id', c.testiosa and c.testiosa.id, c.test.opt_testiosad, 
        onchange="change_testiosa(this);", ronly=False)}
      </div>
    </div>
    % if len(opt_kursused) > 1:
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Kursus"),'kursus')}
        ${h.select('kursus', c.kursus, opt_kursused, onchange="change_kursus(this)", empty=True)}
      </div>
    </div>
    % endif

    % if c.testiosa and c.testiosa.on_alatestid:
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Komplektidega kaetud alatestid"),'komplektivalik_id')}
        ${h.select('komplektivalik_id', c.komplektivalik_id, c.testiosa.get_opt_komplektivalikud(True, c.kursus), 
        onchange="change_komplektivalik(this);", ronly=False, empty=True)}
      </div>
    </div>
    % if c.komplektivalik and not c.komplektivalik.lukus:
    % if self.filename.endswith('valitudylesanded.mako'):
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
            ${h.btn_to_dlg(_("Muuda alatestide valik"), h.url('test_testiosa_edit_komplektivalik', test_id=c.test.id, 
            testiosa_id=c.testiosa.id, id=c.komplektivalik.id, komplekt_id=c.komplekt_id, partial=True), 
            title=_("Alatestide valik"), width=400)}
      </div>
    </div>
    % endif
    % endif

    <% katmata = ['%s %s' % (alatest.kursus_nimi or '', alatest.seq) for alatest in c.testiosa.alatestid if not alatest.komplektivalik_id] %>
    % if len(katmata):
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${_("Komplektidega katmata alatestid")}: ${', '.join(katmata)}
      </div>
    </div>
    % endif
    % endif

    % if c.komplektivalik:
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Ülesandekomplekt"),'komplekt_id')}
        ${h.select('komplekt_id', c.komplekt_id, c.komplektivalik.opt_komplektid, 
        onchange="change_komplekt(this);", ronly=False, empty=True)}
      </div>
    </div>
    % if c.komplekt:
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Ülesandekomplekti olek"), 'komplekt_olek')}
        <div id="komplekt_olek">
          ${c.komplekt.staatus_nimi}
        </div>
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Keeled"), 'keeled')}
        <div id="keeled">
            <% keeled = c.komplekt.keeled %>
            % for lang in keeled:
            ${model.Klrida.get_lang_nimi(lang)} <br/>
            % endfor
            % if not keeled:
            ${h.alert_error(_("Keeled puuduvad"))}
            % endif
        </div>
      </div>
    </div>
    % endif
    % endif
  </div>
</div>
${h.hidden('alatest_id', c.alatest_id, id='alatest_id1')}
${h.hidden('testiplokk_id', c.testiplokk_id)}
${h.end_form()}

</%def>

<%def name="draw_subtabs()">
<%namespace name="tab" file='/common/tab.mako'/>
<%
if not c.testiosa and len(c.test.testiosad):
   c.testiosa = c.test.testiosad[0]
%>
% if c.testiosa:
    ${tab.subdraw('valitudylesanded', h.url('test_valitudylesanded', 
               test_id=c.test.id, testiosa_id=c.testiosa.id, komplekt_id=c.komplekt_id), _("Ülesanded"))}
    ${tab.subdraw('failid', h.url('test_failid', 
               test_id=c.test.id, testiosa_id=c.testiosa.id, komplekt_id=c.komplekt_id), _("Failid"))}

    ${tab.subdraw('eelvaade', h.url('test_new_eelvaade', 
test_id=c.test.id, testiosa_id=c.testiosa.id, klaster_id='', e_komplekt_id=c.komplekt_id or '', komplekt_id='', alatest_id='', lang=c.lang), _("Eelvaade"))}
  % if c.komplekt_id:
    ${tab.subdraw('erialatestid', h.url('test_erialatest',
               test_id=c.test.id, id=c.komplekt_id), _("Eritingimused"))}
  % endif
% endif
</%def>

