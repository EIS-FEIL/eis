<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Osaoskuste võrdlus")}
</%def>      
<%def name="breadcrumbs()">
</%def>
<%def name="active_menu()">
<% c.menu1 = 'otsing' %>
</%def>
<h1>${_("Osaoskuste võrdlus")}</h1>
${h.form_search()}
<div class="gray-legend p-3 filter-w">
  ##${h.toggle_filter()}
  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Testi liik"),'testiliik')}
            <% 
               opt_testiliik = c.opt.testiliik
               if not c.testiliik and opt_testiliik: c.testiliik = opt_testiliik[0][0]
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
        ${h.flb(_("Test"),'test_id')}
            <% 
               opt_test = model.Test.get_opt(c.sessioon_id or -1, testityyp=const.TESTITYYP_EKK) or []
               if c.test_id and int(c.test_id) not in [r[0] for r in opt_test]:
                  c.test_id = None
            %>
            ${h.select('test_id', c.test_id, opt_test, empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Testimiskord"),'testimiskord_id')}
            <% 
               opt_testimiskord = model.Testimiskord.get_opt(c.sessioon_id or -1, test_id=c.test_id or -1) or []
               if c.testimiskord_id and int(c.testimiskord_id) not in [r[0] for r in opt_testimiskord]:
                  c.testimiskord_id = None
            %>
            ${h.select('testimiskord_id', c.testimiskord_id, opt_testimiskord,
               empty=True)}
      <script>
        $(function(){

         $('select#sessioon_id').change(
           callback_select("${h.url('pub_formatted_valikud', kood='TEST', format='json')}", 
                           'sessioon_id', 
                           $('select#test_id'),
                           {testityyp:"${const.TESTITYYP_EKK}"},
                           $('select#testimiskord_id')));
         $('select#test_id').change(
           callback_select("${h.url('pub_formatted_valikud', kood='TESTIMISKORD', format='json')}", 
                           'test_id', 
                           $('select#testimiskord_id'),
                           function(){return {sessioon_id:$('select#sessioon_id').val()}}));
        });
      </script>
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Erinevus vähemalt"),'erinevus')}
        <br/>
        ${h.posint('erinevus', c.erinevus or 12, size=6)} ${_("palli")}
      </div>
    </div>
  </div>
  <div class="d-flex justify-content-end align-items-end">
    <div class="form-group">
    ${h.btn_search()}
    ${h.submit(_("Excel"), id='csv', class_="filter", level=2)}
    </div>
  </div>
</div>
${h.end_form()}

<div class="listdiv">
  % if not c.items and c.items != '':
  ${_("Otsingu tingimustele vastavaid andmeid ei leitud")}
  % elif c.items:
  <%include file="osaoskused_list.mako"/>
  % endif 
</div>
