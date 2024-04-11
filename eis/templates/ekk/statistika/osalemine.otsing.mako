<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Statistika")}
</%def>      
<%def name="breadcrumbs()">
</%def>
<%def name="active_menu()">
<% c.menu1 = 'otsing' %>
</%def>
<h1>${_("Osalemise statistika")}</h1>
${h.form_search()}
<div class="gray-legend p-3 filter-w">
  ##${h.toggle_filter()}
  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Testi ID"),'test_id')}
        ${h.posint('test_id', c.test_id)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Aasta alates"),'aasta_alates')}
        ${h.posint('aasta_alates', c.aasta_alates, maxlength=4)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Aasta kuni"),'aasta_kuni')}
        ${h.posint('aasta_kuni', c.aasta_kuni, maxlength=4)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Õppeaine"),'aine')}
        ${h.select('aine', c.aine, c.opt.klread_kood('AINE'), empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Testi liik"),'testiliik')}
        ${h.select('testiliik', c.testiliik, c.opt.testiliik)}
            <script>
              $(document).ready(function(){
                $('select#aine').change(function(){
                  if($(this).val()=='${const.AINE_RK}') $('select#testiliik').val('${const.TESTILIIK_TASE}');
                  if($(this).val()=='${const.AINE_C}') $('select#testiliik').val('${const.TESTILIIK_SEADUS}');
                });
                $('select#testiliik').change(function(){
                  if($(this).val()=='${const.TESTILIIK_TASE}') $('select#aine').val('${const.AINE_RK}');
                  if($(this).val()=='${const.TESTILIIK_SEADUS}') $('select#aine').val('${const.AINE_C}');
                });
              });
            </script>
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.checkbox('tkord',1,checked=c.tkord,  label=_("Testimiskordade kaupa"))}  
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
  <%include file="osalemine.list.mako"/>
  % endif 
</div>
