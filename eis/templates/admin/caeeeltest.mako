<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("CAE eeltesti sooritanud")}
</%def>
<%def name="breadcrumbs()">
${h.crumb(_("Sooritajad"), h.url('admin_eksaminandid'))}
${h.crumb(_("CAE eeltesti sooritanud"), h.url('admin_caeeeltestid'))} 
</%def>
<%def name="active_menu()">
<% c.menu1 = 'admin' %>
</%def>

${h.form_save(None, h.url_current(None), multipart=True)}

<table  class="table" width="100%">
  <col width="150"/>
  <col width="200"/>  
  <tr>
    <td class="fh">${_("Andmefail")}</td>
    <td>
      ${h.file('fail', value=_("Fail"))}
    </td>
    <td>
      ${h.submit(_("Laadi"), onclick="$('.alert-danger').remove()")}
    </td>
  </tr>
</table>
${h.end_form()}

${h.form_search(None)}
<div class="gray-legend p-3 filter-w">
  ##${h.toggle_filter()}

  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Isikukood"),'isikukood')}
        ${h.text('isikukood', c.isikukood, maxlength=50)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Eesnimi"),'eesnimi')}
        ${h.text('eesnimi', c.eesnimi)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Perekonnanimi"),'perenimi')}
        ${h.text('perenimi', c.perenimi)}
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
  <%include file="caeeeltest_list.mako"/>
</div>

