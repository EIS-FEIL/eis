${h.form_search(h.url('test_otsiylesandekogud', test_id=c.test.id, testiruum_id=c.testiruum_id), id="yk_search", class_="search")}

<div class="gray-legend p-3 filter-w">
  <div class="row filter">
    <div class="col-12 col-md-6">
      <div class="form-group">    
        ${h.flb(_("Õppeaine"),'aine')}
        <div>
          ${h.select('aine', c.aine, c.opt_aine_yk, empty=True)}
        </div>
      </div>
    </div>
    <div class="col-12 col-md-6" class="keeletase">
      <div class="form-group">        
        ${h.flb(_("Keeleoskuse tase"),'keeletase')}
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
        ${h.flb(_("Märksõna"),'term')}
        <div>
          ${h.text('term', c.term)}
        </div>
      </div>
    </div>
    <div class="d-flex justify-content-end filter align-items-end">
      <div class="form-group">
        ${h.submit_dlg(_('Otsi'), "$('#listdiv_yk')")}
      </div>
    </div>
  </div>
</div>
${h.hidden('partial',1)}
${h.end_form()}

${h.form_save(None, h.url('test_ylesanded', test_id=c.test.id, testiruum_id=c.testiruum_id))}
<div id="listdiv_yk">
% if c.items != '':
<%include file="otsiylesandekogud_list.mako"/>
% endif
</div>
${h.end_form()}

<script>
<%include file="otsiylesandekogud.js"/>
</script>
