<%inherit file="/common/dlgpage.mako"/>
<%include file="translating.mako"/>

<%include file="/common/message.mako"/>

${h.form_save(c.item.id)}
${h.hidden('lang', c.lang)}
${h.hidden('is_tr', c.is_tr)} 

<%include file="testiosa.sisu.mako"/>
<div class="text-right">
% if c.is_edit or c.is_tr:
${h.submit_dlg(clicked=True)}
% endif
</div>

<span id="progress"></span>
${h.end_form()}

% if c.is_edit or c.is_tr:
<script>
$(function(){
    destroy_old_ckeditor();  
    var inputs = $('#f_sooritajajuhend.editable,#f_alustajajuhend.editable');
    init_ckeditor(inputs, 'osa_ckeditor_top', '${request.localizer.locale_name}', '${h.ckeditor_toolbar('basic')}', null, 50);
});
</script>
<div style="height:0">
<div id="osa_ckeditor_top" class="ckeditor-top-float"></div>
</div>
% endif
      
      
<%def name="tran_editable(key, item, prefix)">
<%
  orig_val = item and item.__getattr__(key)
  if c.lang:
     tran = item and item.tran(c.lang, False)
     tran_val = tran and tran.__getattr__(key) or ''
%>
% if c.lang:
<div>
  ${h.lang_orig(h.literal(orig_val), c.test.lang)}
</div>
${h.lang_tag()}
% if c.is_tr:
${h.textarea(prefix + key, tran_val, ronly=False, class_="editable")}
% else:
${tran_val}
% endif
% else:
% if c.is_edit or c.is_tr:
${h.textarea(prefix + key, orig_val, ronly=False, class_="editable")}
% else:
${orig_val}
% endif
% endif
</%def>
