
${h.form(h.url('admin_update_tklassifikaator', id=c.item.id, lang=c.lang), method='put')}
${h.hidden('sub', 'kirjeldus')}

${h.literal(c.item.kirjeldus)}
<br/>
<% tran = c.item.tran(c.lang, False) %>
${h.ckeditor('f_kirjeldus', tran and tran.kirjeldus or '')}          
</p>
${h.submit()}
${h.end_form()}

