<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("E-kogud")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Haldus"))}
${h.crumb(_("E-kogud"))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'admin' %>
</%def>
<h1>${_("E-kogud")}</h1>
${h.form_search(url=h.url('ylesandekogud'))}
<div class="gray-legend p-3 filter-w">
  ##${h.toggle_filter()}
  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">  
        ${h.flb(_("ID"),'id')}
        ${h.posint('id', c.id)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Nimetus"),'nimi')}
        ${h.text('nimi', c.nimi)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Kooliaste"),'aste')}
        ${h.select('aste', c.aste, c.opt.astmed(c.aine), empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Klass"),'klass')}
        ${h.select('klass', c.klass, const.EHIS_KLASS, empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Ainevaldkond"),'ainevald')}
        ${h.select('ainevald', c.ainevald, c.opt.klread_kood('AINEVALD', empty=True))}
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
        ${h.flb(_("Teema"),'valdkond')}
        ${h.select('valdkond', c.valdkond, 
        c.opt.klread_kood('TEEMA',c.aine,ylem_required=True,bit=c.opt.aste_bit(c.aste),empty=True), names=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Alateema"),'teema')}
        ${h.select('teema', c.teema, c.opt.klread_kood('ALATEEMA',ylem_id=c.teema_id,ylem_required=True,bit=c.opt.aste_bit(c.aste, c.aine),empty=True))}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3 keeletase">
      <div class="form-group">    
        ${h.flb(_("Keeleoskuse tase"), 'keeletase')}
        ${h.select('keeletase', c.keeletase, c.opt.klread_kood('KEELETASE',ylem_kood=c.aine,ylem_required=True,empty=True))}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3 oskus">
      <div class="form-group">    
        ${h.flb(_("Oskus"),'oskus')}
        ${h.select('oskus', c.oskus, 
        c.opt.klread_kood('OSKUS',c.aine,ylem_required=True,empty=True))}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
            <% s_opt = [(str(st), c.opt.YK_STAATUS.get(st)) for st in (const.YK_STAATUS_MITTEAVALIK, const.YK_STAATUS_TESTIMISEL, const.YK_STAATUS_AVALIK, const.YK_STAATUS_ARHIIV)] %>
            ${h.select_checkbox('staatus', c.staatus, s_opt, linebreak=False)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Ülesannete arv"),'y_alates')}<br/>
        <span class="nowrap">${_("min")} ${h.int5('y_alates', c.y_alates)}</span>
        -
        <span class="nowrap">${_("max")} ${h.int5('y_kuni', c.y_kuni)}</span>
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Punktid"),'p_min')}<br/>
        <span class="nowrap">${_("min")} ${h.int5('p_min', c.p_min)}</span>
        -
        <span class="nowrap">${_("max")} ${h.int5('p_max', c.p_max)}</span>
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Loodud"),'alates')}
        ${h.date_field('alates', c.alates)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("kuni"), 'kuni')}
        ${h.date_field('kuni', c.kuni)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Ülesande ID"),'ylesanne_id')}
        ${h.posint('ylesanne_id', c.ylesanne_id)}
      </div>
    </div>
    <div class="col d-flex justify-content-end align-items-end">
      <div class="form-group">
        ${h.submit(_("CSV"), id='csv', class_="filter", level=2)}
        ${h.btn_search()}
        % if c.user.has_permission('ylesandekogud', const.BT_CREATE):
        ${h.btn_new(h.url('new_ylesandekogu'))}
        % endif
      </div>
    </div>
  </div>
</div>
${h.end_form()}
<script>
  <%include file="otsing.js"/>
</script>
<div class="listdiv">
<%include file="otsing_list.mako"/>
</div>
