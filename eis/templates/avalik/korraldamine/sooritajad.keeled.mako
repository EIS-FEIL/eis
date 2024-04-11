## -*- coding: utf-8 -*- 
${h.form_save(None)}
${h.hidden('sub', 'keeled')}
${h.hidden('sooritused_id', c.sooritused_id)}
<% keeled = c.testimiskord.keeled %>
<p>
  % for lang in const.LANG_ORDER:
  % if lang in keeled:
  ${h.radio('lang', lang, checkedif=c.default_lang, label=model.Klrida.get_lang_nimi(lang))}<br/>
  % endif
  % endfor
</p>
${h.submit_dlg(_("Salvesta"))}
${h.end_form()}
