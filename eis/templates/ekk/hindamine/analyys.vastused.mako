<%inherit file="/common/formpage.mako"/>
<%def name="require()">
<%
  c.includes['subtabs'] = True
  c.includes['math'] = True
%>
</%def>
<%def name="page_title()">
${c.toimumisaeg.testimiskord.test.nimi} ${c.toimumisaeg.millal} | ${_("Vastuste analüüs")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Hindamine"), h.url('hindamised'))} 
${h.crumb('%s %s' % (c.toimumisaeg.testimiskord.test.nimi, c.toimumisaeg.millal))}
% if c.user.has_permission('hindamisanalyys', const.BT_SHOW, obj=c.test):
${h.crumb(_("Hindamise analüüs"), h.url('hindamine_analyys_protokollid', toimumisaeg_id=c.toimumisaeg.id))}
% else:
${h.crumb(_("Hindamise analüüs"))}
% endif
${h.crumb(_("Vastuste analüüs"), h.url('hindamine_analyys_vastused', toimumisaeg_id=c.toimumisaeg.id))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'hindamised' %>
</%def>

<%def name="draw_before_tabs()">
<%include file="before_tabs.mako"/>
</%def>

<%def name="draw_tabs()">
<% c.tab1 = 'analyys' %>
<%include file="tabs.mako"/>
</%def>

<%def name="draw_subtabs()">
<%include file="analyys.tabs.mako"/>
</%def>

${h.form_search(url=h.url('hindamine_analyys_vastused', toimumisaeg_id=c.toimumisaeg.id))}
<div class="gray-legend p-3">
  <div class="row filter">
  % if len(c.opt_testiosad) == 1:
    ${h.hidden('testiosa_id', c.testiosa_id)}
  % else:
    <div class="col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Testiosa"), 'testiosa_id')}
        ${h.select('testiosa_id', c.testiosa_id, c.opt_testiosad, 
        class_="exec-submit", ronly=False, empty=True)}
      </div>
    </div>
  % endif

  % if c.testiosa_id:
    <% testiosa = model.Testiosa.get(c.testiosa_id) %>
    % if testiosa.on_alatestid:
    <% opt_kursused = c.test.opt_kursused %>
    % if opt_kursused:
    <div class="col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Kursus"), 'kursus')}
        ${h.select('kursus', c.kursus, opt_kursused, class_="exec-submit", ronly=False, empty=False)}
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
    <div class="col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Ülesandekomplekt"), 'komplekt_id')}
        ${h.select('komplekt_id', c.komplekt_id, c.opt_komplekt,
        class_="exec-submit", ronly=False, empty=True)}
      </div>
    </div>
    <div class="col-md-8 col-lg-6 d-flex align-items-end">
      <div class="form-group">
        ${h.checkbox('komplektis', 1, checked=c.komplektis,
        label=_("Mitmes komplektis esinevate ülesannete statistika komplektide kaupa"))}
      </div>
    </div>
    % endif
  % endif
    <div class="col d-flex justify-content-end align-items-end">
      <div class="form-group">    
      ${h.submit(_("Väljasta PDF"), id='pdf', level=2)}
      </div>
    </div>
  </div>
</div>
<script>
  $('.filter select.exec-submit').change(function(){ this.form.submit(); });
</script>


<%include file="analyys.vastused_list.mako"/>
${h.end_form()}

% if c.arvutusprotsessid:
<%
  c.url_refresh = h.url_current('index', sub='progress')
  c.protsessid_no_pager = True
%>
<%include file="/common/arvutusprotsessid.mako"/>
% endif

<script>
$(function(){
  $('input#komplektis').click(function(){
     ## kysimuste vaates avatakse kysimuse vaade, ylesannete vaates ylesannete vaade
     window.location.href = "${h.url_current(getargs=True, komplektis=not c.komplektis and 1 or 0)}";
  });
});
</script>
