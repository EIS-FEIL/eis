<%inherit file="/common/pagenw.mako"/>
<%def name="page_title()">
${_("Kasutajad")} | ${_("Läbiviijate laadimine")}
</%def>
<%def name="breadcrumbs()">
${h.crumb(_("Kasutajad"), h.url('admin_kasutajad'))} 
${h.crumb(_("Läbiviijate laadimine"))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'admin' %>
</%def>


${h.form_save(None, h.url('admin_labiviijalaadimine'), multipart=True)}
${h.hidden('testiliik', c.testiliik)}

<div class="p-2 mb-4">
  <div class="form-group row">
    ${h.flb3(_("Läbiviija roll"))}
    <div class="col">
      <%
        if c.is_ats or 1:
           grupid_id = (const.GRUPP_HINDAJA_K, const.GRUPP_T_ADMIN)
        else:
           grupid_id = (const.GRUPP_T_ADMIN,)
        opt_grupp = [(g_id, c.opt.grupp_nimi(g_id)) for g_id in grupid_id]
      %>
      ${h.select('kasutajagrupp_id', c.kasutajagrupp_id, opt_grupp, 
      onchange="onchange_grupp()")}
    </div>      
  </div>
  <div class="form-group row">
    ${h.flb3(_("Andmefail"))}
    <div class="col">
      ${h.file('fail', value=_("Fail"))}
      <small class="grupp-khindaja" style="display:none">
        ${_("Faili kõik read peavad olema kujul <i>õppeaine kood;piirkonna nimi;keele kood;isikukood;eesnimi;perekonnanimi</i>")}
      </small>
      <small class="grupp-tadmin" style="display:none">
        ${_("Faili kõik read peavad olema kujul <i>isikukood;eesnimi;perekonnanimi</i>")}
      </small>      
    </div>
  </div>
</div>
<div class="d-flex">
  <div class="flex-grow-1">
    ${h.btn_to(_("Tagasi"), h.url('admin_kasutajad'), level=2)}
  </div>
  ${h.submit(_("Laadi"), onclick="$('.alert-danger').remove()")}
</div>
${h.end_form()}

<script>
function onchange_grupp()
{
    var grupp_id = $('#kasutajagrupp_id').val();
    $('.grupp-khindaja').toggle(grupp_id == "${const.GRUPP_HINDAJA_K}");
    $('.grupp-tadmin').toggle(grupp_id == "${const.GRUPP_T_ADMIN}");
}
$(document).ready(onchange_grupp);
</script>
