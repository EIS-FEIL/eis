<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Kirjaliku testi vastuste sisestamine")}
</%def>      
<%def name="breadcrumbs()">
</%def>
<%def name="active_menu()">
<% c.menu1 = 'sisestamine' %>
</%def>

<h1>${_("Kirjaliku p-testi vastuste sisestamine")}</h1>
${h.form_search(url=h.url('sisestamine_testitood'))}
<div class="gray-legend p-3 filter-w">
  ##${h.toggle_filter()}
  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Sisesta toimumisaja tähis"),'ta_tahised')}
        ${h.text('ta_tahised', c.ta_tahised, onchange='refresh_sk()')}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("protokollirühma tähis"),'tpr_tahised')}
        ${h.text('tpr_tahised', c.tpr_tahised)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("sisestuskogum"), 'sisestuskogum_id')}
        ${h.select('sisestuskogum_id', c.sisestuskogum_id, c.opt_sisestuskogum or [], empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-2">
      <div class="form-group">
        ${h.flb(_("testitöö"), 'tahised')}
        ${h.text('tahised', c.tahised, maxlength=7, pattern='\d+-\d+')}
      </div>
    </div>
    <div class="col d-flex flex-wrap justify-content-end align-items-end">
      <div class="flex-grow-1">    
        ${h.submit(_("Sisesta"), id='sisesta')}
      </div>
    </div>
  </div>
  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("või vali testsessioon"),'sessioon_id')}
        ${h.select('sessioon_id', c.sessioon_id,
        c.opt.testsessioon, empty=True, onchange='clear_ta();this.form.submit()')}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("ja toimumisaeg"),'toimumisaeg_id')}
        ${h.select('toimumisaeg_id', c.toimumisaeg_id,
          c.opt_toimumisaeg, empty=True, onchange='clear_sk();this.form.submit()')}
      </div>
    </div>
  
  % if c.opt_testikoht:
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("soorituskoht"),'testikoht_id')}
        ${h.select('testikoht_id', c.testikoht_id, c.opt_testikoht, empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-2">
      <div class="form-group">    
        ${h.flb(_("isikukood"),'isikukood')}
        ${h.text('isikukood', c.isikukood)}
      </div>
    </div>
    % endif
    <div class="col d-flex flex-wrap justify-content-end align-items-end">
      <div class="flex-grow-1">        
        ${h.btn_search()}
      </div>
    </div>
  </div>

</div>

<script>
  function clear_ta()
  {
    $('#toimumisaeg_id').val('');
    clear_sk();
  }
  function clear_sk()
  {
    $('#sisestuskogum_id').val('');
    $('#sooritus_id').val('');
  }
  function refresh_sk()
  {
     var tahised = $('#ta_tahised').val();
     if(tahised != '')
     {
        var url = "${h.url('sisestamine_testitood', ta_tahised=tahised, sub='optsk')}";
        var data = {ta_tahised: tahised};
        var target = $('#sisestuskogum_id');
        update_options(null, url, null, target, data, null, true);
     }
  }
</script>
${h.end_form()}

<div class="listdiv">
<%include file="testitood.otsing_list.mako"/>
</div>
