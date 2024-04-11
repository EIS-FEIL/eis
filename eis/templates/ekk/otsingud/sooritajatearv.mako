<%inherit file="/common/formpage.mako" />
<%def name="page_title()">
${_("Sooritajate arv")}
</%def>
<%def name="breadcrumbs()">
</%def>
<%def name="draw_tabs()">
<%include file="sooritajatearv.tabs.mako"/>
</%def>
<%def name="active_menu()">
<% c.menu1 = 'otsing' %>
</%def>
<%def name="requirenw()">
<% c.pagenw = True %>
</%def>
<h1>${_("Sooritajate arv")}</h1>
${h.form_search()}
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
        ${h.time('alates_kell', c.alates_kell, show0=True)}
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
        ${h.time('kuni_kell', c.kuni_kell, show0=True)}            
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Samm"),'step')}
          <%
            opt_step = [(10, _("{n} minutit").format(n=10)),
                        (15, _("{n} minutit").format(n=15)),
                        (30, _("{n} minutit").format(n=30)),
                        (60, _("Tunni sooritajad kokku")),            
                        (1440, _("Päeva sooritajad kokku"))]
          %>
        ${h.select('step', c.step or 10, opt_step)}
      </div>
    </div>
  </div>
  <div class="col d-flex justify-content-end align-items-end">
    <div class="form-group">
    ${h.btn_search()}
    ${h.submit(_("CSV"), id="csv", class_="filter", level=2)}      

    </div>
  </div>
</div>
${h.end_form()}

<div class="listdiv">
<%include file="sooritajatearv_list.mako" />
</div>

<script>
  function s2d(val){
    var li = (val || '').split('.');
    if(li.length==3) return new Date(li[2], li[1]-1, li[0]);
  }
  $('#alates').change(function(){
    var alates = $('#alates').val(), kuni = $('#kuni').val(),
        d_alates = s2d(alates), d_kuni = s2d(kuni);
    if(d_alates && d_kuni && (d_alates > d_kuni)) $('#kuni').val(alates);
  });
  $('#alates_kell').change(function(){
    var alates = $('#alates').val(), kuni = $('#kuni').val(),
        d_alates = s2d(alates), d_kuni = s2d(kuni),
        alates_kell = $('#alates_kell').val(), kuni_kell = $('#kuni_kell').val();
    if(d_alates && d_kuni && alates_kell && kuni_kell && (alates == kuni) && (alates_kell > kuni_kell))
       $('#kuni_kell').val(alates_kell);
  });
</script>
