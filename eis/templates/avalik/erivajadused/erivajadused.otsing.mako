<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Eritingimuste andmete väljastamine")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Tsentraalsed testid"))}
${h.crumb(_('Eritingimused'), h.url('erivajadused'))}
</%def>

<%def name="active_menu()">
<% c.menu1 = 'ekktestid' %>
</%def>
<h1>${_("Eritingimused")}</h1>
${h.form_search(url=h.url('erivajadused'))}

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
        ${h.flb(_("Testsessioon"),'sessioon_id')}
        ${h.select('sessioon_id', c.sessioon_id, c.opt_sessioon)}
      </div>
    </div>      
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Õppeaine"), 'aine_kood')}
        ${h.select('aine_kood', c.aine_kood, c.opt.klread_kood('AINE'), empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-8 col-lg-6">
      <div class="form-group">    
        ${h.checkbox('kinnitatud', 1, checked=c.kinnitatud,
        label=_('Näita ainult kinnitatuid'),
        onchange="$('input#kinnitamata').prop('checked',false);")}
        <br/>
        ${h.checkbox('kinnitamata', 1, checked=c.kinnitamata,
        label=_('Näita ainult kinnitamata'),
        onchange="$('input#kinnitatud').prop('checked',false);")}            
      </div>
    </div>
    <div class="col d-flex justify-content-end align-items-end">    
      <div class="form-group">
        ${h.btn_search()}
        ${h.submit(_('Excel'), id='csv', class_="filter")}
      </div>
    </div>
  </div>
</div>
${h.end_form()}

<div class="listdiv">
<%include file="erivajadused.otsing_list.mako"/>
</div>
