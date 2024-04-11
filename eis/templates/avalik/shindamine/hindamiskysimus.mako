## -*- coding: utf-8 -*- 
${h.form_save(c.item.id)}
${h.hidden('lang', c.lang)}
## partial - kas kysimuse esitamise dialoog avati dialoogiaknast või peaaknast, st kuhu minna tagasi
${h.hidden('partial', c.partial)}
${h.textarea('kysimus', '', rows=5, cols=70)}
<br/>
${h.submit_dlg()}
${h.end_form()}
