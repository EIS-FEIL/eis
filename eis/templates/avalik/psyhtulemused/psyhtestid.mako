## -*- coding: utf-8 -*- 
<%inherit file="/common/pagenw.mako"/>
<%def name="page_title()">
${_("Testid")}
</%def>      
<h1>${_("Testide loetelu")}</h1>
${h.form_search(url=h.url('psyhtestid'))}

<%def name="active_menu()">
<% c.menu1 = 'kpsyh' %>
</%def>

<div class="gray-legend p-3 filter-w">
  ##${h.toggle_filter()}
  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("ID"), 'id')}
        ${h.posint('id', c.id)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Nimetus"),'nimi')}
        ${h.text('nimi', c.nimi)}
      </div>
    </div>      
    <div class="col d-flex justify-content-end align-items-end">  
      <div>
      ${h.btn_search()}
      </div>
    </div>
  </div>
</div>

${h.end_form()}

<div class="listdiv">
<%include file="psyhtestid_list.mako"/>
</div>
