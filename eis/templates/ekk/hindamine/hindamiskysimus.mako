${h.form_save(c.item.id)}
${h.hidden('sub', 'vastus')}
${h.hidden('hindamiskysimus_id', c.hindamiskysimus.id)}
${h.hidden('lang', c.lang)}
${h.hidden('alatest_id', c.alatest_id)}
${h.hidden('komplekt_id', c.komplekt_id)}
${_("Küsimus")}:<br/>
% if not c.hindamiskysimus.id:
${h.textarea('kysimus', c.hindamiskysimus.kysimus, rows=5, cols=70)}
% else:
${c.hindamiskysimus.kysimus}
% endif
<br/>
${_("Vastus")}:<br/>
${h.textarea('vastus', c.hindamiskysimus.vastus, rows=5, cols=70)}
<br/>
${h.checkbox('avalik', 1, checked=c.hindamiskysimus.avalik, 
label=_("Küsimus ja vastus avaldatud kõigile hindajatele"))}
<br/>
${h.submit_dlg()}
${h.end_form()}
