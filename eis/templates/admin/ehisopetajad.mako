<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Uuenda EHISest")}
</%def>
<%def name="breadcrumbs()">
${h.crumb(_("Kasutajad"), h.url('admin_kasutajad'))}
${h.crumb(_("Uuenda EHISest"), h.url('admin_kasutajad_ehisopetajad'))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'admin' %>
</%def>
${h.form_search(None)}
<div class="gray-legend p-3 filter-w">
  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Kool"),'kool_id')}
        ${h.select2('kool_id', c.kool_id, c.opt_kool, allowClear=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Õppeaine"),'aine')}
        ${h.select('aine', c.aine, c.opt_aine, empty=False)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Kooliaste"),'aste')}
        ${h.select('aste', c.aste, c.opt_aste, empty=False)}
      </div>
    </div>
    <div class="col d-flex justify-content-end align-items-end">
      <div class="form-group">
      ${h.submit(_("Näita"))}
      ${h.submit(_("CSV"), id='csv')}
      ${h.button(_("Uuenda"), id="uuenda")}
      % if request.params.get('debug'):
      ${h.hidden('debug', request.params.get('debug'))}
      % endif
      </div>
    </div>
  </div>
</div>

${h.end_form()}

${h.form_save(None)}
${h.hidden('aine', c.aine)}
${h.hidden('aste', c.aste)}
${h.hidden('kool_id', c.kool_id)}
${h.hidden('debug', c.debug)}
${h.end_form()}
<script>
$(function(){
  $('#uuenda').click(function(){
    $('form#form_save input[name="kool_id"]').val($('form#form_search select[name="kool_id"]').val());
    $('form#form_save input[name="aine"]').val($('form#form_search select[name="aine"]').val());
    $('form#form_save input[name="aste"]').val($('form#form_search select[name="aste"]').val());
    $('form#form_save').submit();
  });
});
</script>

<div class="listdiv">
<%include file="ehisopetajad_list.mako"/>
</div>

<%
  c.url_refresh = h.url('admin_kasutajad_ehisopetajad', sub='progress')
%>
<%include file="/common/arvutusprotsessid.mako"/>
