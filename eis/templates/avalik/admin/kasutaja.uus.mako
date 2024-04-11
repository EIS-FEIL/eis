<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Kasutajad")} | ${_("Uue kasutaja lisamine")}
</%def>
<%def name="breadcrumbs()">
${h.crumb(_("Kasutajad"), h.url('admin_kasutajad'))} 
${h.crumb(_("Uus kasutaja"), h.url('admin_new_kasutaja'))}
</%def>

${h.form_search(url=h.url('admin_new_kasutaja'))}
<div class="gray-legend p-3 filter-w">
  <div class="row filter">
    <div class="col-12 col-md-4">
      <div class="form-group">
        ${h.flb(_("Isikukood"),'isikukood')}
        ${h.text('isikukood', c.isikukood)}
      </div>
    </div>
    <div class="col d-flex justify-content-end align-items-end">
      <div>
        ${h.btn_search()}
      </div>
    </div>
  </div>
</div>

${h.btn_back(url=h.url('admin_kasutajad'))}
${h.end_form()}
