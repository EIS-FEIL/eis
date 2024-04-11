<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Veriffi seansside ID")}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'admin' %>
</%def>

${h.form_save(None, h.url('admin_veriffid'), multipart=True)}

<table  class="table" width="100%">
  <col width="150"/>
  <tr>
    <td class="fh">${_("Veriffist saadud fail CSV-na")}</td>
    <td>
      ${h.file('fail', value=_("Fail"))}
      <small>
        Faili esimene veerg peab olema seansi ID
      </small>
    </td>
  </tr>
</table>
${h.submit(_("Laadi"), onclick="$('.alert-danger').remove()")}
${h.end_form()}

