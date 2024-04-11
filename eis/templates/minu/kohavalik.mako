## -*- coding: utf-8 -*- 
<%inherit file="/common/page.mako"/>
<%def name="require()">
<% c.includes['select2'] = True %>
</%def>

<%def name="page_title()">
${_("Õppeasutuse valik")}
</%def>      
<% c.is_edit = True %>

<h1>${_("Vali õppeasutus")}</h1>

% if c.user.on_adminkoht:
<div class="m-4 form-wrapper">
  <%
    opt_adminkoht = model.Koht.get_plangikoht_opt()
  %>
  ${h.form(h.url('login', action='koht'), id="form_loginadm", method='POST')}          

  <div class="form-group row">
    <div class="col col-12 col-md-6">
      ${h.select('koht_id', None, opt_adminkoht, empty=False)}
      <script>
$(function(){
  $('select#koht_id').select2({
    language: '${request.localizer.locale_name}'
  });
});
      </script>
    </div>
    <div class="col col-md-6">
      <div>
        ${h.submit(_("Vali"), id='adminvali')}
      </div>
    </div>
  </div>
  ${h.hidden('request_url', c.request_url)}
  ${h.end_form()}
</div>
% endif
