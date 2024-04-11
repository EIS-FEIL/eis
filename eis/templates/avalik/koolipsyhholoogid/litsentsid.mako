<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Koolipsühholoogid")} | ${_("Litsentside laadimine")}
</%def>
<%def name="breadcrumbs()">
${h.crumb(_("Koolipsühholoogid"), h.url('koolipsyhholoogid'))} 
${h.crumb(_("Litsentside laadimine"))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'kpsyh' %>
</%def>

${h.form_save(None, h.url('koolipsyhholoogid_litsentsid'), multipart=True)}

<div class="form-wrapper mb-1">
  <div class="form-group row">
    ${h.flb3(_("CSV fail"), 'fail')}
    <div class="col-md-9">
      ${h.file('fail', value=_("Fail"))}
    </div>
  </div>
  <div class="form-group">
      ${h.alert_notice(_("Tekstifailis peavad olema isikute isikukoodid, kellele antakse koolipsühholoogi roll, iga isikukood eraldi real"), False)}
  </div>
</div>
${h.btn_back(url=h.url('koolipsyhholoogid'))}
${h.submit(_("Laadi"))}
${h.end_form()}
