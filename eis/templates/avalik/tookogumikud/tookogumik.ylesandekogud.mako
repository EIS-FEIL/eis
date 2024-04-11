## -*- coding: utf-8 -*- 
${h.form_search(h.url('tookogumik_ylesandekogud'), id="yk_search", class_="search")}
${h.hidden('partial', 1)}
<%
  c1 = request.handler.get_c_default_params('/tookogumik/ylesandekogud')
%>
<div class="gray-legend p-3 filter-w">
  <div class="row filter">
    <div class="col-12">
      ${h.flb(_("Õppeaine"),'yk_aine')}
      ${h.select('aine', c1.aine, c.opt_aine_yk, id="yk_aine", empty=True)}
    </div>
  </div>
  <div class="row filter keeletase">
    <div class="col-12">  
      ${h.flb(_("Keeleoskuse tase"),'keeletase')}
      ${h.select('keeletase', c1.keeletase, c.opt.klread_kood('KEELETASE',ylem_kood=c1.aine,ylem_required=True, empty=True), id="yk_keeletase")}
    </div>
  </div>
  <div class="row filter keeletase">
    <div class="col-12">  
      ${h.flb(_("Kooliaste"), 'yk_aste')}
      ${h.select('aste', c1.aste, c.opt.astmed(), id="yk_aste", empty=True)}
    </div>
  </div>
  <div class="row filter keeletase">
    <div class="col-12">  
      ${h.flb(_("Märksõna"), 'yk_term')}
      ${h.text('term', c1.term, id="yk_term")}
    </div>
  </div>
  <div class="d-flex">
    ${h.submit_dlg(_("Otsi"), "$('#listdiv_yk')", name="otsi", id="yk_otsi")}
  </div>
</div>
${h.end_form()}

<div id="listdiv_yk" class="listdiv">
<%include file="tookogumik.ylesandekogud_list.mako"/>
</div>
