${h.form_search(h.url('test_otsitookogumikud', test_id=c.test.id, testiruum_id=c.testiruum_id), id="tk_search", class_="search")}
<div class="gray-legend p-3 filter-w">
  <div class="row filter">
    <div class="col-9 col-md-6">
      <div class="form-group">        
        ${h.flb(_("Töökogumik"),'tookogumik_id')}
        <div>
          ${h.select('tookogumik_id', c.tookogumik_id, c.opt_tookogumik)}
        </div>
      </div>
    </div>
  </div>
</div>

${h.hidden('partial',1)}
${h.end_form()}

${h.form_save(None, h.url('test_ylesanded', test_id=c.test.id, testiruum_id=c.testiruum_id))}
<div id="listdiv_tk">
<%include file="otsitookogumikud_list.mako"/>
</div>
${h.end_form()}

<script>
<%include file="otsitookogumikud.js"/>
</script>
