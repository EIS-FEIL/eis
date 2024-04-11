${h.form_search(url=h.url('test_otsiylesanded', test_id=c.test.id, testiruum_id=c.testiruum_id), id="yo_search", class_="search")}

<div class="gray-legend p-3 filter-w">
  <div class="row filter">
    <div class="col-12 col-md-6">
      <div class="form-group">    
        ${h.flb(_("Ülesande ID"),'yleasnne_id')}
        <div>${h.int10('ylesanne_id', c.ylesanne_id)}</div>
      </div>
    </div>
    <div class="col-12 col-md-6">
      <div class="form-group">        
        ${h.flb(_("Õppeaine"),'aine')}
        <div>
          ${h.select('aine', c.aine, c.opt.klread_kood('AINE'), empty=True)}
        </div>
      </div>
    </div>
    <div class="col-12 col-md-6">
      <div class="form-group" class="keeletase">        
        ${h.flb(_("Keeleoskuse tase"))}
        <div>
          ${h.select('keeletase', c.keeletase, c.opt.klread_kood('KEELETASE',ylem_kood=c.aine,ylem_required=True,empty=True))}
        </div>
      </div>
    </div>
    <div class="col-12 col-md-6">
      <div class="form-group">        
        ${h.flb(_("Kooliaste"),'aste')}
        <div>
          ${h.select('aste', c.aste, c.opt.astmed(), empty=True)}
        </div>
      </div>
    </div>
    <div class="col-12 col-md-6">
      <div class="form-group">        
        ${h.flb(_("Teema"),'teema')}
        <div>
          ${h.select('teema', c.teema,
          c.opt.klread_kood('TEEMA',c.aine,empty=True,ylem_required=True), names=True)}
        </div>
      </div>
    </div>
    <div class="col-12 col-md-6">
      <div class="form-group">        
        ${h.flb(_("Alateema"),'alateema')}
        <div>
          ${h.select('alateema', c.alateema,
          c.opt.klread_kood('ALATEEMA',ylem_id=c.teema_id, ylem_required=True,empty=True))}
        </div>
      </div>
    </div>
    <div class="col-12 col-md-6">
      <div class="form-group">        
        ${h.flb(_("Õpitulemus"),'opitulemus_id')}
        <div>
            <% opt_opitulemus = c.opt.opitulemused(c.aine, False) %>
            ${h.select2('opitulemus_id', c.opitulemus_id, opt_opitulemus, empty=True, allowClear=True)}
        </div>
      </div>
    </div>
    <div class="col-12 col-md-6">
      <div class="form-group">        
        ${h.flb(_("Keel"),'lang')}
        <div>
          ${h.select('lang', c.lang, c.opt.klread_kood('SOORKEEL', empty=True))}
        </div>
      </div>
    </div>
    <div class="col-12 col-md-6">
      <div class="form-group">        
        ${h.flb(_("Ülesandetüüp"),'kysimus')}
        <div>
          ${h.select('kysimus', c.kysimus, c.opt.interaction_empty)}
        </div>
      </div>
    </div>
    <div class="col-12 col-md-6">
      <div class="form-group">        
        ${h.flb(_("Märksõna"),'term')}
        <div>
          ${h.text('term', c.term)}
        </div>
      </div>
    </div>
    <div class="d-flex justify-content-end filter align-items-end">
      <div class="form-group">
        ${h.submit_dlg(_('Otsi'), "$('#listdiv_yl')")}
      </div>
    </div>
  </div>
</div>

${h.hidden('partial',1)}
${h.end_form()}

${h.form_save(None, h.url('test_ylesanded', test_id=c.test.id, testiruum_id=c.testiruum_id))}
<div id="listdiv_yl">
% if c.items != '':
<%include file="otsiylesanded_list.mako"/>
% endif
</div>
${h.end_form()}
<script>
  <%include file="otsiylesanded.js"/>
</script>
