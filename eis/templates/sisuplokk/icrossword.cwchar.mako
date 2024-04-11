## -*- coding: utf-8 -*- 
<% 
c.ylesanne = c.item.ylesanne
%>
<%include file="/common/message.mako" />

${h.form_save(None, form_name='form_dlg')}
${h.hidden('lang', c.lang)}
${h.hidden('is_tr', c.is_tr)}
## selle ruudu koordinaadid, kus klikiti
${h.hidden('pos_x', c.pos_x)}
${h.hidden('pos_y', c.pos_y)}

% if c.cw_exist:
${_("See täht on lahendajale ette antud ja ta ei saa seda muuta.")}
% else:
${_("See täht ei ole lahendajale ette antud. Salvestamisel muudetakse täht etteantuks.")}
% endif

<div class="form-group row">
  <% name = 'vihje' %>
  ${h.flb3(_("Täht"), name, 'text-md-right')}
  <div class="col-md-9">
    ${h.text('vihje', c.vihje, size=2, maxlength=1, ronly=False, style="text-transform:uppercase;")}
  </div>
</div>

${h.submit_dlg()}
% if c.cw_exist:
${h.btn_remove(h.url_current('delete', id=0, pos_x=c.pos_x, pos_y=c.pos_y, lang=c.lang))}
% endif
${h.button(_("Tagasi"), onclick="close_dialog()")}

${h.end_form()}


<div style="float:right">
  ${_("CSS klass")}
  <span class="brown">
    cw-gap-${c.pos_y}-${c.pos_x}
  </span>
</div>
