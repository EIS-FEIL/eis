<%include file="/common/message.mako"/>
% if c.do_close:
<script>close_dialog('chkemaildlg');</script>
% else:

<% kasutaja = c.user.get_kasutaja() %>
  % if not kasutaja.epost:
  ${h.alert_notice(_("Kasutaja kontaktandmed puuduvad"), False)}
  % else:
  ${h.alert_notice(_("Saabunud on aeg uuendada kontaktandmeid!"), False)}
  % endif
  ${h.form_save(None, h.url('minu_kontaktuuendamine'), form_name='chk_form', class_="chk-form")}
  <div class="form-group row">
    ${h.flb3(_("E-posti aadress"), 'chk_epost')}
    <div class="col-md-9">
      ${h.text('chk_epost', kasutaja.epost, ronly=False)}
    </div>
  </div>
  <div class="form-group row">  
    ${h.flb3(_("Korda e-posti aadressi"),'chk_epost2')}
    <div class="col-md-9">
      ${h.text('chk_epost2', kasutaja.epost, ronly=False)}
    </div>
  </div>

  <div class="mt-5 d-flex flex-wrap">
    <div class="flex-grow-1">
      % if c.app_eis or c.app_plank:
      ${h.submit_dlg(_("Katkesta"), op='cancel', level=2)}
      % endif
    </div>
    ${h.submit_dlg()}
  </div>
  ${h.end_form()}
% endif
