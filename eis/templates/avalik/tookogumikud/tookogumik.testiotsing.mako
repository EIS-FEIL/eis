${h.form_search(h.url('tookogumik_testiotsing'), id="t_search", class_="search")}
${h.hidden('partial', 1)}
<%
  c1 = request.handler.get_c_default_params('/tookogumik/testiotsing')
%>
<div class="gray-legend p-3 filter-w">
  <div class="row filter">
    <div class="col-12">
      ${h.flb(_("Testi ID"), 't_test_id')}
      ${h.posint('test_id', c1.test_id, id='t_test_id')}
    </div>
  </div>
  <div class="row filter">
    <div class="col-12">
      ${h.flb(_("Testi liik"),'t_testiliik')}
      ${h.select('testiliik', c1.testiliik,
      c.opt.klread_kood('TESTILIIK', empty=True), id='t_testiliik')}
    </div>
  </div>
  <div class="row filter keeletase">
    <div class="col-12">  
      ${h.flb(_("Õppeaine"),'t_aine')}
      ${h.select('aine', c1.aine, c.opt.klread_kood('AINE'), id='t_aine', empty=True)}
    </div>
  </div>
  <div class="row filter keeletase">
    <div class="col-12">  
      ${h.flb(_("Kooliaste"),'t_aste')}
      ${h.select('aste', c1.aste, c.opt.astmed(), empty=True, id='t_aste')}
    </div>
  </div>
  <div class="row filter keeletase">
    <div class="col-12">  
      ${h.checkbox('minu', 1, checked=c1.minu, label=_("Minu testid"), id='t_minu')}
    </div>
  </div>
  <div class="d-flex">
    ${h.submit_dlg(_("Otsi"), "$('#listdiv_t')", name="otsi", id='t_otsi')}
  </div>
</div>

${h.end_form()}

<div id="listdiv_t" class="listdiv">
<%include file="tookogumik.testiotsing_list.mako"/>
</div>

