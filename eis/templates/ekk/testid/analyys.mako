<%inherit file="/common/formpage.mako"/>
<%def name="draw_tabs()">
<%include file="tabs.mako"/>
</%def>

<%def name="page_title()">
${_("Test")}: ${c.test.nimi or ''} | ${_("Vastuste analüüs")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Testid"), h.url('testid'))} 
${h.crumb(c.test.nimi or _("Test"))} 
${h.crumb(_("Vastuste analüüs"))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'testid' %>
</%def>

${h.form_search()}
<div class="gray-legend p-2 p-md-4 mb-4 py-4">
  <div class="row filter">

  % if len(c.opt_testiosad) == 1:
    ${h.hidden('testiosa_id', c.testiosa_id)}
  % else:
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Testiosa"),'testiosa_id')}
        ${h.select('testiosa_id', c.testiosa_id, c.opt_testiosad, 
        class_="exec-submit", ronly=False)}
      </div>
    </div>
  % endif

  % if c.testiosa_id:
    <% testiosa = model.Testiosa.get(c.testiosa_id) %>
    % if testiosa.on_alatestid:
    <% opt_kursused = c.test.opt_kursused %>
    % if len(opt_kursused) > 1:
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Kursus"),'kursus')}
        ${h.select('kursus', c.kursus, opt_kursused, class_="exec-submit", empty=True)}
      </div>
    </div>
    % endif

    % if len(c.opt_kv) > 1:
    <div class="col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Alatest"), 'komplektivalik_id')}
        ${h.select('komplektivalik_id', c.komplektivalik_id, c.opt_kv,
        class_="exec-submit", ronly=False, empty=True)}
      </div>
    </div>
    % endif
    % endif
    
    % if c.opt_komplekt:
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Ülesandekomplekt"),'komplekt_id')}
        ${h.select('komplekt_id', c.komplekt_id, c.opt_komplekt, 
        class_="exec-submit", ronly=False, empty=True)}
      </div>
    </div>
    % endif

    % if c.app_ekk and c.sooritajad_cnt != '':
    <div class="col d-flex justify-content-end align-items-end">
      <div class="form-group">    
        <span class="p-3">
          ${_("Testimiskorrata sooritanute arv")}: ${c.sooritajad_cnt}
        </span>
      </div>
    </div>
    % endif
  </div>
</div>

<script>
  $('.filter select.exec-submit').change(function(){ this.form.submit(); });
</script>
<%include file="/ekk/hindamine/analyys.vastused_list.mako"/>
${h.end_form()}

<% can_edit = c.user.has_permission('ekk-testid', const.BT_UPDATE, c.test) %>
% if can_edit:
<div class="my-3">
        ${h.form_save(None)}
        ${h.hidden('testiosa_id', c.testiosa_id)}
        ${h.submit(_("Arvuta tulemused üle"), id='result', level=2)}
        ${h.submit(_("Arvuta statistika"), id='stat', level=2)}

        <span class="pl-3">
        % if last_stat:
        ${_("Statistika arvutatud")} ${h.str_from_datetime(last_stat)}
        % else:
        ${_("Statistika arvutamata")}
        % endif
        </span>
        % if c.debug:
        ${h.hidden('debug', c.debug)}
        % endif
        ${h.end_form()}
</div>
% endif

% if c.arvutusprotsessid:
<%
  c.url_refresh = h.url_current('index', sub='progress')
  c.protsessid_no_pager = True
%>
<%include file="/common/arvutusprotsessid.mako"/>
% endif


% endif

