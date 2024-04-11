<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Abiinfo")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Haldus"))}
${h.crumb(_("Lehekülje abiinfo"), h.url('admin_abiinfo'))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'admin' %>
</%def>
<%def name="require()">
<%
c.includes['ckeditor'] = True
%>
</%def>
<%
   koodid = (
             ('sisu2', 'EKSAMISTATISTIKA', _("Testide tulemuste statistika")),
            )
%>

% for (name, kood, label) in koodid:
<% item = model.Abiinfo.get_info(kood) %>
<h1>${label}</h1>

${h.form_save(None, h.url('admin_create_abiinfo'))}
${h.hidden('kood', kood)}
<table  class="table" width="90%">
  <tr>
    <td>
      ${h.ckeditor(name, item and item.sisu, rows=12)}
    </td>
  </tr>
</table>

<div class="d-flex">
  <div class="flex-grow-1">
    <% log_list_cls = 'log_list_%s' % kood %>
    <span class="${log_list_cls}">
      ${h.btn_to(_("Logi"), h.url_current('index', sub='log', kood=kood), target='.'+log_list_cls, level=2)}
    </span>
  </div>
% if c.is_edit:
${h.submit()}
% endif
${h.end_form()}

% endfor
