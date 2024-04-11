${h.form(h.url('admin_klassifikaator', id=c.item.id, lang=c.lang), method='put')}
${h.hidden('sub', 'kirjeldus')}
${h.ckeditor('f_kirjeldus', c.item.kirjeldus)}          
${h.submit_dlg()}
${h.end_form()}

