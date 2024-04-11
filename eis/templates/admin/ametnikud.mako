<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Kasutajad")}
</%def>
<%def name="breadcrumbs()">
${h.crumb(_("Haldus"))}
${h.crumb(_("Eksamikeskuse kasutajad"),h.url('admin_ametnikud'))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'admin' %>
</%def>
<h1>${_("Eksamikeskuse kasutajad")}</h1>
${h.form_search(url=h.url('admin_ametnikud'))}
<div class="gray-legend p-3 filter-w">
  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Isikukood"),'isikukood')}
        ${h.text('isikukood', c.isikukood)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Eesnimi"),'eesnimi')}
        ${h.text('eesnimi', c.eesnimi)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Perekonnanimi"),'perenimi')}
        ${h.text('perenimi', c.perenimi)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.checkbox('amkehtib', value=1, checked=c.amkehtib, label=_("Ainult kehtivad Harno kasutajad"))}            
        ${h.checkbox('rollita', value=1, checked=c.rollita, label=_("Ilma kehtiva rollita"))}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Roll"),'roll_id')}
        ${h.select('roll_id', c.roll_id, c.opt.ametnikgrupp_empty)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Õigus"),'oigus_id')}
        ${h.select('oigus_id', c.oigus_id, c.opt.oigused(), empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Õppeaine"),'aine')}
        ${h.select('aine', c.aine, c.opt.klread_kood('AINE', empty=True))}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Rolli andja isikukood"),'rollisikukood')}
        ${h.text('rollisikukood', c.rollisikukood)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Rolli andmise JIRA pilet"),'jira_nr')}
        ${h.posint('jira_nr', c.jira_nr)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3 rolloigus">
      <div class="form-group">    
        ${h.flb(_("Rolli kehtivus"),'kehtib')}
        <div>
          ${h.checkbox('kehtib', value=1, checked=c.kehtib or not c.kehtetu, label=_("Kehtiv"))}
          ${h.checkbox('kehtetu', value=1, checked=c.kehtetu, label=_("Kehtetu"))}
        </div>
      </div>
    </div>
    <div class="col d-flex justify-content-end align-items-end">  
      <div class="form-group">
      ${h.btn_search()}
      % if c.user.has_permission('ametnikud', const.BT_CREATE):
      ${h.btn_new(h.url('admin_new_ametnik'))}
      % endif
      ${h.submit(_("CSV"), id='csv', class_="filter", level=2)}

      <span style="float:right">
      ${h.btn_to(_("Failist laadimine"), h.url('admin_ametnikulaadimine'), level=2)}
      </span>
      </div>
    </div>
  </div>
</div>
${h.end_form()}

<div class="listdiv">
  <%include file="ametnikud_list.mako"/>
</div>
<script>
  $(function(){
  ## rolli kehtivust saab valida ainult siis, kui roll või õigus või aine on valitud
  $('select#roll_id,select#oigus_id,select#aine').change(function(){
  $('.rolloigus').toggle(($('select#roll_id').val() || $('select#oigus_id').val() || $('select#aine').val()) != '');
  });
  $('.rolloigus').toggle(($('select#roll_id').val() || $('select#oigus_id').val() || $('select#aine').val()) != '');  
  });
</script>
