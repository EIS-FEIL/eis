## -*- coding: utf-8 -*- 
${h.form_search(h.url('tookogumik_ylesandeotsing'), id="yo_search", class_="search")}
${h.hidden('partial', 1)}
<%
  c1 = request.handler.get_c_default_params('/tookogumik/ylesandeotsing')
%>
<div class="gray-legend p-3 filter-w">
  <div class="row filter">
    <div class="col-12">
      ${h.flb(_("Ülesande ID"),'ylesanne_id')}
      ${h.posint('ylesanne_id', c1.ylesanne_id)}
    </div>
  </div>
  <div class="row filter">
    <div class="col-12">
      ${h.flb(_("Õppeaine"),'aine')}
      ${h.select('aine', c1.aine, c.opt.klread_kood('AINE'), empty=True)}
    </div>
  </div>
  <div class="row filter keeletase">
    <div class="col-12">
      ${h.flb(_("Keeleoskuse tase"),'keeletase')}
      ${h.select('keeletase', c1.keeletase, c.opt.klread_kood('KEELETASE',ylem_kood=c1.aine,ylem_required=True,empty=True))}
    </div>
  </div>
  <div class="row filter keeletase">
    <div class="col-12">
      ${h.flb(_("Kooliaste"),'aste')}
      ${h.select('aste', c1.aste, c.opt.astmed(), empty=True)}
    </div>
  </div>
  <div class="row filter keeletase">
    <div class="col-12">
      ${h.flb(_("Teema"),'teema')}
      ${h.select('teema', c1.teema,
      c.opt.klread_kood('TEEMA',c1.aine,empty=True,ylem_required=True), names=True)}
    </div>
  </div>
  <div class="row filter keeletase">
    <div class="col-12">
      ${h.flb(_("Alateema"),'alateema')}
      ${h.select('alateema', c1.alateema,
      c.opt.klread_kood('ALATEEMA',ylem_id=c1.teema_id, ylem_required=True,empty=True))}
    </div>
  </div>
  <div class="row filter keeletase">
    <div class="col-12">
      ${h.flb(_("Õpitulemus"),'opitulemus_id')}
      <% opt_opitulemus = c.opt.opitulemused(c1.aine, False) %>
      ${h.select2('opitulemus_id', c1.opitulemus_id, opt_opitulemus, allowClear=True)}
    </div>
  </div>
  <div class="row filter keeletase">
    <div class="col-12">
      ${h.flb(_("Keel"),'lang')}
      ${h.select('lang', c1.lang, c.opt.klread_kood('SOORKEEL', empty=True))}
    </div>
  </div>
  <div class="row filter keeletase">
    <div class="col-12">
      ${h.flb(_("Ülesandetüüp"),'kysimus')}
      ${h.select('kysimus', c1.kysimus, c.opt.interaction_empty)}
    </div>
  </div>
  <div class="row filter keeletase">
    <div class="col-12">
      ${h.flb(_("Märksõna"),'term')}
      ${h.text('term', c1.term)}
    </div>
  </div>
  <div class="row filter keeletase">
    <div class="col-12">
      ${h.flb(_("Olek"),'staatus')}
      <%
        st = list(map(str, const.Y_ST_AV + (const.Y_STAATUS_AVALIK, const.Y_STAATUS_PEDAGOOG)))
        koik_staatused = c.opt.klread_kood('Y_STAATUS') 
        opt_staatus = [r for r in koik_staatused if r[0] in st]
      %>
      ${h.select('staatus', c.staatus, opt_staatus, empty=True)}
    </div>
  </div>
  <div class="d-flex">
    ${h.submit_dlg(_("Otsi"), "$('#listdiv')", name='otsi')}
  </div>
</div>
${h.end_form()}

<div id="listdiv" class="listdiv">
<%include file="tookogumik.ylesandeotsing_list.mako"/>
</div>

