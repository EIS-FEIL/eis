<%inherit file="/common/page.mako"/>
<%def name="require()">
<% c.includes['jstree'] = True %>
</%def>
<%def name="page_title()">
${_("Soorituskohad")}
</%def>
<%def name="breadcrumbs()">
${h.crumb(_("Haldus"))}
${h.crumb(_("Soorituskohad"))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'admin' %>
</%def>
<h1>${_("Soorituskohad")}</h1>
${h.form_search(url=h.url('admin_kohad'))}
<div class="gray-legend p-3 filter-w">
  ##${h.toggle_filter()}
  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("EHIS ID"),'kool_id')}
        ${h.posint('kool_id', c.kool_id)}
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
        ${h.flb(_("Koolitüüp"),'koolityyp')}
        ${h.select('koolityyp', c.koolityyp, c.opt.klread_kood('KOOLITYYP'), empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Maakond"),'maakond_kood')}
        ${h.select('maakond_kood', c.maakond_kood, 
        model.Aadresskomponent.get_opt(None), empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Piirkond"),'prk_id_0')}
        <%
          c.piirkond_id = c.piirkond
          c.piirkond_field = 'piirkond'
        %>
        <%include file="/admin/piirkonnavalik.mako"/>
      </div>
    </div>
  </div>
  <div class="d-flex justify-content-end align-items-end">      
    <div class="form-group">
    ${h.btn_search()}
    % if c.user.has_permission('kohad', const.BT_UPDATE):
    ${h.btn_new(h.url('admin_new_koht'))}
    ${h.button(_("Vali kõik"), onclick="$('input.koht').prop('checked', true);toggle_send();", level=2)}
    ${h.button(_("Tühista valik"), onclick="$('input.koht').prop('checked', false);toggle_send();", level=2)}
    <span id="send" class="invisible">
      ${h.btn_to_dlg('Saada teated', h.url('admin_new_koht', sub='mail',
      partial=True), title=_("Teate saatmine"), form="$('form#form_list')", width=560, level=2)}
    </span>
    % if c.is_debug:
    ${h.btn_to(_("Uuenda EHISest avaandmed"), h.url('admin_kohad', sub='ehisjson'), method='post', spinnerin=True, level=2)}
    % endif
    ${h.btn_to(_("Uuenda EHISest"), h.url('admin_kohad', sub='ehis'), method='post', spinnerin=True, level=2)}    
    % endif
    ${h.btn_to(_("Näita muudatusi"), h.url('admin_kohad_logi'), level=2)}
    </div>
  </div>
</div>
${h.end_form()}

<form id="form_list">
<div class="listdiv">
  <%include file="kohad_list.mako"/>
</div>
</form>

<script>
  function toggle_send(){   
         var visible = ($('input:checked.koht]').length > 0);
         if(visible)
         { 
           $('span#send.invisible').removeClass('invisible');
         }
         else
         {
           $('span#send').filter(':not(.invisible)').addClass('invisible');
         }
  }
</script>

