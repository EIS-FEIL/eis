## -*- coding: utf-8 -*- 
<div class="dlg_hindamiskysimus">
${h.form_save(c.item.id)}
${h.hidden('lang', c.lang)}
% if c.indlg:
${h.hidden('indlg', 1)}
% endif
${h.textarea('kysimus', '', rows=5, cols=70, class_="nosave")}

<div class="mb-2"></div>
${h.submit_dlg(container="$('#hindamiskysimused_div').parent()")}
${h.end_form()}
</div>
