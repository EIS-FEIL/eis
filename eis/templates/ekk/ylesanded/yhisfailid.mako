<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Ühised failid")}
</%def>      

<%def name="breadcrumbs()">
${h.crumb(_("Ülesanded"), h.url('ylesanded'))} 
${h.crumb(_("Ühised failid"))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'ylesanded' %>
</%def>

${h.form_search(url=h.url('ylesanne_yhisfailid'))}
<div class="gray-legend p-3 filter-w">
  <div class="row">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Failinimi"), 'filename')}
        ${h.text('filename', c.filename)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Teema"),'teema')}
        ${h.text('teema', c.teema)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Liik"),'liik')}
        ${h.select('yhisfail',c.yhisfail,c.opt.klread_kood('YHISFAIL', empty=True))}
      </div>
    </div>
    <div class="col d-flex justify-content-end align-items-end">
        ${h.btn_search()}
        ${h.btn_new(h.url('ylesanne_new_yhisfail'))}
    </div>
  </div>
</div>
${h.end_form()}

<div class="listdiv">
<%include file="yhisfailid_list.mako"/>
</div>
