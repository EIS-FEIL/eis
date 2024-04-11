<%inherit file="/common/page.mako" />
<%def name="page_title()">
${_("Logi")}
</%def>
<%def name="breadcrumbs()">
${h.crumb(_("Haldus"))}
${h.crumb(_("Logi"))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'admin' %>
</%def>
<%def name="require()">
<%
  c.pagexl = True
%>
</%def>

<h1>${_("Logi")}</h1>
${h.form_search(url=h.url('admin_logi'))}
<div class="gray-legend p-3 filter-w">
  ##${h.toggle_filter()}

  <div class="row filter">    
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Aeg"),'alates')}
        ${h.date_field('alates', c.alates)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("kell"), 'alates_kell')}
        ${h.time('alates_kell', c.alates_kell, show0=True, is_sec=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("kuni"),'kuni')}
        ${h.date_field('kuni', c.kuni)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("kell"),'kuni_kell')}
        ${h.time('kuni_kell', c.kuni_kell, show0=True, is_sec=True)}            
      </div>
    </div>
  </div>

  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Pöördumise ID"), 'request_id')}
        ${h.text('request_id', c.request_id)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Logi ID"), 'idr')}
        ${h.text('idr', c.idr or c.id)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Logi UUID"), 'uuid')}
        ${h.text('uuid', c.uuid)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Liik"), 'tyyp')}
        ${h.select('tyyp', c.tyyp, c.opt.logityyp, empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Isikukood"), 'isikukood')}
        ${h.text('isikukood', c.isikukood, maxlength=50)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Nimi"),'nimi')}
        ${h.text('nimi', c.nimi)}
      </div>
    </div>

    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("IP"), 'remote_addr')}
        ${h.text('remote_addr', c.remote_addr)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Parameetrid"),'param')}
        ${h.text('param', c.param)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Rada"), 'path')}
        ${h.text('path', c.path)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Logi"), 'sisu')}
        ${h.text('sisu', c.sisu)}    
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Ülesande ID"), 'ylesanne_id')}
        ${h.posint('ylesanne_id', c.ylesanne_id)}    
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3 d-flex align-items-end">
      <div class="form-group">    
        ${h.checkbox('method', 'POST', checked=c.method, label=_("POST"))}
      </div>
    </div>
    <div class="col d-flex justify-content-end align-items-end">
      <div class="form-group">
      ${h.btn_search()}
      ${h.submit(_("Excel"), id='xls', class_="filter", level=2)}
      </div>
    </div>
  </div>
</div>
${h.end_form()}

<div class="listdiv">
<%include file="logi_list.mako" />
</div>

<script>
  function s2d(val){
    var li = (val || '').split('.');
    if(li.length==3) return new Date(li[2], li[1]-1, li[0]);
  }
  $('#alates').change(function(){
    var alates = $('#alates').val(), kuni = $('#kuni').val(),
        d_alates = s2d(alates), d_kuni = s2d(kuni);
    if(d_alates && (d_kuni && (d_alates > d_kuni) || !d_kuni)) $('#kuni').val(alates);
  });
  $('#alates_kell').change(function(){
    var alates = $('#alates').val(), kuni = $('#kuni').val(),
        d_alates = s2d(alates), d_kuni = s2d(kuni),
        alates_kell = $('#alates_kell').val(), kuni_kell = $('#kuni_kell').val();
    if(d_alates && d_kuni && alates_kell && kuni_kell && (alates == kuni) && (alates_kell > kuni_kell))
       $('#kuni_kell').val(alates_kell);
  });
</script>

