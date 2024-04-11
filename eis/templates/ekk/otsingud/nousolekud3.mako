<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("III hindamise nõusolekud")}
</%def>      
<%def name="breadcrumbs()">
</%def>
<%def name="active_menu()">
<% c.menu1 = 'otsing' %>
</%def>
<h1>${_("III hindamise nõusolekud")}</h1>

${h.form_search(url=h.url('otsing_nousolekud3'))}
<div class="gray-legend p-3 filter-w">
  ##${h.toggle_filter()}
  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Testi liik"),'testiliik')}
            <% 
               opt_testiliik = c.opt.testiliik
               if not c.testiliik: c.testiliik = const.TESTILIIK_RIIGIEKSAM
            %>
            ${h.select('testiliik', c.testiliik, opt_testiliik, onchange="this.form.submit()")}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Testsessioon"),'sessioon_id')}
            <% 
               opt_sessioon = model.Testsessioon.get_opt(c.testiliik)
               if c.sessioon_id and int(c.sessioon_id) not in [r[0] for r in opt_sessioon]:
                  c.sessioon_id = None
            %>
            ${h.select('sessioon_id', c.sessioon_id, opt_sessioon, empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Leping"),'leping_id')}
            <% 
               opt_leping = model.Leping.opt_hindajaleping()
            %>
            ${h.select('leping_id', c.leping_id, opt_leping, empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Õppeaine"),'aine')}
        ${h.select('aine', c.aine, model.Leping.opt_hindajaained(), empty=True)}
      </div>
    </div>
  </div>
  <div class="d-flex justify-content-end filter align-items-end">
    <div class="form-group">
    ${h.submit(_("Otsi"), id='otsi')}            
    </div>
  </div>
</div>
${h.end_form()}

<div class="listdiv">
<%include file="nousolekud3_list.mako"/>
</div>
  % if c.items:
  <%
     params = request.params.mixed()
     params['format'] = 'csv'
     url_csv = h.url_current('index', **params)
  %>
<br/>
${h.btn_to(_("Väljasta CSV"), url_csv, level=2)}
% endif
