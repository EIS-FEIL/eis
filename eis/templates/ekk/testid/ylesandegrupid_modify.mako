% if c.is_saved:
<div container_sel="td.ylgrupid_modify">
% endif
<%
  grupid = list(c.testiosa.ylesandegrupid)
  grid_id = 'tbl_ylg'
%>
% if not c.is_saved:
<%include file="translating.mako"/>
% endif
% if c.is_edit or c.is_tr:
${h.form_save(None)}
${h.hidden('lang', c.lang)}
${h.hidden('sub', 'modify')}
<div id="ylg_ckeditor_top" class="ckeditor-top-float" style="z-index:100"></div>
% endif

<table  cellpadding="4"
       % if c.is_edit or c.is_tr:
       id="${grid_id}" class="table table-borderless table-striped ylgrupid"
       % else:
       class="table table-borderless table-striped"
       % endif
       style="margin:3px;width:100%;max-width:1000px;">
  <col/>
  % if c.is_edit:
  <col width="20px"/>
  % endif
  <thead>
    <tr>
      ${h.th(_("Ülesandegrupid"))}
      % if c.is_edit:
      ${h.th('')}
      % endif
    </tr>
  </thead>
  <tbody>
  % for ind, grupp in enumerate(grupid):
  <% prefix = 'ylg-%d.' % ind %>
  <tr>
    <td>
      ${self.tran_editable('nimi', grupp, prefix)}
      ${h.hidden(prefix + 'id', grupp.id)}
    </td>
    % if c.is_edit:
    <td>
      <span class="glyphicon glyphicon-chevron-up ylg-up"></span>
      <span class="glyphicon glyphicon-chevron-down ylg-down"></span>      
    </td>
    % endif
  </tr>
  % endfor
</table>

% if c.is_edit or c.is_tr:
${h.submit_dlg()}
${h.end_form()}
% endif

% if c.is_edit or c.is_tr:
<script>
function ylg_reinit_ckeditor()
{
    destroy_old_ckeditor();
    var inputs = $('.ylgrupid .editable');
    init_ckeditor(inputs, 'ylg_ckeditor_top', '${request.localizer.locale_name}', '${h.ckeditor_toolbar('basic')}', null, null, 'body16');
}
  
$(function(){
    $('table.ylgrupid').on('click', '.ylg-up', function(){
        var tr = $(this).closest('tr')[0];
        if(tr.previousElementSibling)
        {
            tr.parentNode.insertBefore(tr, tr.previousElementSibling);
            ylg_reinit_ckeditor();
        }
    });
    $('table.ylgrupid').on('click', '.ylg-down', function(){
        var tr = $(this).closest('tr')[0];        
        if(tr.nextElementSibling)
        {
            tr.parentNode.insertBefore(tr.nextElementSibling, tr);
            ylg_reinit_ckeditor();
        }
    });
    ylg_reinit_ckeditor();
});
</script>
% endif

<%def name="tran_editable(key, item, prefix)">
<div class="body16">
<%
  orig_val = item and item.__getattr__(key)
  if c.lang:
     tran = item and item.tran(c.lang, False)
     tran_val = tran and tran.__getattr__(key) or ''
%>
% if c.lang:
% if c.is_edit or c.is_tr:
<div class="cke_top_pos" name="${prefix + key}">
% else:
<div>
% endif
  ${h.lang_orig(h.literal(orig_val), c.test.lang)}
</div>
${h.lang_tag()}
% if c.is_tr:
${h.textarea(prefix + key, tran_val,
##ronly=not c.is_edit,
ronly=False,
class_="editable editable70")}
##${h.text(prefix + key, tran_val, maxlength=100, ronly=False)}
% else:
${tran_val}
% endif
% else:
% if c.is_edit:
${h.textarea(prefix + key, orig_val,
ronly=not c.is_tr and not c.is_edit, class_="editable editable70")}
##${h.text(prefix + key, orig_val, maxlength=100)}
% else:
${orig_val}
% endif
% endif
</div>
</%def>
