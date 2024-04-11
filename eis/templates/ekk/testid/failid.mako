<%inherit file="komplektid.mako"/>
<%def name="breadcrumbs()">
${h.crumb(_("Testid"), h.url('testid'))} 
${h.crumb(c.test.nimi or _("Test"))}
${h.crumb(_("Ülesanded"))} 
${h.crumb(_("Failid"))}
</%def>

% if c.test.is_encrypted:
${h.alert_notice(_("Test on krüptitud"))}
% else:

% if len(c.items) == 0:
${h.alert_notice(_("Ühtki faili pole"))}
% else:
<div>
  <%include file="failid_list.mako"/>
</div>
% endif

  % if c.komplekt_id:

${h.form_save(None, h.url('test_failid', test_id=c.test.id), multipart=True)}
${h.hidden('komplekt_id', c.komplekt_id)}

    % if c.can_update or c.user.has_permission('ekk-testid-failid',  const.BT_UPDATE, obj=c.test):
<div class="d-flex align-items-start">
  ${h.flb(_("Nimetus"),'f_nimi')}
  <div class="m-2">
    ${h.text('f_nimi', '', size=30)}
  </div>
  ${h.file('f_filedata')}
</div>
${h.submit(_("Salvesta fail"))}
    % endif
${h.end_form()}
  % endif

% endif
