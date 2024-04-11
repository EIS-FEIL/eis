<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Hindamiskogumi valik")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Hindamine"))}
${h.crumb(_("Tsentraalsed testid"), h.url('khindamised'))} 
</%def>

<%def name="active_menu()">
<% c.menu1 = 'hindamine' %>
</%def>

<h1>${_("Tsentraalsete testide hindamine")}</h1>
${h.form_search(url=h.url('khindamised'))}
<div class="gray-legend p-3 filter-w">
  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Testi ID"), 'test_id')}
        ${h.posint('test_id', c.test_id)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Õppeaine"),'aine')}
        ${h.select('aine', c.aine, c.opt_aine, empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Testiosa tähis"),'testiosa_tahis')}
        ${h.text('testiosa_tahis', c.testiosa_tahis)}
      </div>
    </div>      
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Testsessioon"),'testsessioon_id')}
        ${h.select('testsessioon_id', c.testsessioon_id, model.Testsessioon.get_opt(), empty=True)}
      </div>
    </div>      
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Toimumise algusaeg"), 'alates')}
        ${h.date_field('alates', h.str_from_date(c.alates))}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("kuni"),'kuni')}
        ${h.date_field('kuni', h.str_from_date(c.kuni))}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Keel"),'lang')}
        ${h.select('lang', c.lang, c.opt_soorkeel, empty=True)}
      </div>
    </div>      
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Testi nimetus"),'t_nimi')}
        ${h.text('t_nimi', c.t_nimi)}
      </div>
    </div>      
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Vastamise vorm"),'vastvorm')}
        <%
          vormid = (const.VASTVORM_KE, const.VASTVORM_SE, const.VASTVORM_I, const.VASTVORM_SH, const.VASTVORM_KP)
          opt_vastvorm = ((vorm, c.opt.VASTVORM.get(vorm)) for vorm in vormid)
        %>
        ${h.select('vastvorm', c.vastvorm, opt_vastvorm, empty=True)}
      </div>
    </div>      
    <div class="col-12 col-md-7 col-lg-5 d-flex align-items-end">
      <div class="form-group">
        ${h.radio('hinnatud', '', checked=c.hinnatud != 't' and c.hinnatud != 'x', label=_("hindamata"))}
        ${h.radio('hinnatud', 't', checkedif=c.hinnatud, label=_("hinnatud"))}
        ${h.radio('hinnatud', 'x', checkedif=c.hinnatud, label=_("kõik"))}
      </div>
    </div>      
    <div class="col d-flex justify-content-end align-items-end">    
      <div class="form-group">
        ${h.btn_search()}
      </div>
    </div>
  </div>
</div>
${h.end_form()}

<div class="listdiv">
<%include file="hindamiskogumid_list.mako"/>
</div>
