<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Uuenda EHISest")}
</%def>
<%def name="breadcrumbs()">
${h.crumb(_("Sooritajad"), h.url('admin_eksaminandid'))}
${h.crumb(_("Uuenda EHISest"), h.url('admin_eksaminandid_ehisoppurid'))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'admin' %>
</%def>
<%def name="require()">
<% c.includes['select2'] = True %>
</%def>
${h.form_save(None)}

<div class="gray-legend p-3 filter-w">

<ul class="nav nav-pills" role="tablist">
  <li class="nav-item" role="tab" aria-controls="tab1"
      aria-selected="${not c.bytest and 'true' or 'false'}">
    <a class="nav-item nav-link ${not c.bytest and 'active' or ''}"
      id="first-tab" data-toggle="tab" href="#tab1">${_("Kooli järgi")}</a>
  </li>
  <li class="nav-item" role="tab" aria-controls="tab2"
      aria-selected="${c.bytest and 'true' or 'false'}">
    <a class="nav-item nav-link ${c.bytest and 'active' or ''}"
      id="second-tab" data-toggle="tab" href="#tab2">${_("Testi järgi")}</a>
  </li>
</ul>
<div class="tab-content" id="ttabs">
  <div class="tab-pane rounded-0 border-0 fade ${not c.bytest and 'show active' or ''}"
    id="tab1"
    role="tabpanel"
    aria-labelledby="first-tab">
    ${self.filter_kool()}
  </div>
  <div class="tab-pane rounded-0 border-0 fade ${c.bytest and 'show active' or ''}"
    id="tab2"
    role="tabpanel"
       aria-labelledby="second-tab">
    ${self.filter_test()}
  </div>
</div>
</div>
${h.end_form()}

<%def name="filter_kool()">

  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Kool"),'kool_id')}
        ${h.select2('kool_id', c.kool_id, c.opt_kool, allowClear=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Klass"), 'klass')}
        ${h.select('klass', c.klass, c.opt_klass, empty=False)}
      </div>
    </div>
    <div class="d-flex justify-content-end align-items-end">
      <div class="form-group">
        ${h.submit(_("Uuenda"))}
        % if request.params.get('debug'):
        ${h.hidden('debug', request.params.get('debug'))}
        % endif
      </div>
    </div>
  </div>
</%def>

<%def name="filter_test()">

  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Testiliik"),'testiliik')}
        ${h.select('testiliik', c.testiliik, c.opt.testiliik)}
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
        ${h.flb(_("Test"),'test_id')}
            <%
               opt_test = model.Test.get_opt(c.sessioon_id or -1, keeletase=c.keeletase) or []
               if c.test_id and int(c.test_id) not in [r[0] for r in opt_test]:
                  c.test_id = None
            %>
            ${h.select('test_id', c.test_id, opt_test, empty=True)}
      </div>
    </div>
    <div class="d-flex justify-content-end align-items-end">
      <div class="form-group">
        ${h.submit(_("Uuenda"), name="uuenda2")}
      </div>
    </div>
  </div>

      <script>
        $(function(){
         $('select#testiliik').change(
           callback_select("${h.url('pub_formatted_valikud', kood='SESSIOON', format='json')}", 
                           'testiliik', 
                           $('select#sessioon_id'),
                           null,
                           $('select#test_id'))
        );
         $('select#sessioon_id').change(
           callback_select("${h.url('pub_formatted_valikud', kood='TEST', format='json')}", 
                           'sessioon_id', 
                           $('select#test_id'),
                           function(){return {testiliik:$('#testiliik').val()}})
        );
        });
      </script>
  
</%def>


<%
  c.url_refresh = h.url('admin_eksaminandid_ehisoppurid', sub='progress')
%>
<%include file="/common/arvutusprotsessid.mako"/>
