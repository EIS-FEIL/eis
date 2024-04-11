<%inherit file="/common/formpage.mako"/>
<%def name="requirenw()">
<% c.pagenw = True %>
</%def>

<%def name="draw_tabs()">
<% c.tab1 = 'tagasisideviis' %>
<%include file="tabs.mako"/>
</%def>
<%def name="draw_subtabs()">
<%include file="tagasiside.tabs.mako"/>
</%def>

<%def name="page_title()">
${_("Test")}: ${c.test.nimi or ''} | ${_("Tagasiside")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Testid"), h.url('testid'))} 
${h.crumb(c.test.nimi or _("Test"))} 
${h.crumb(_("Tagasiside"))}
</%def>
<%def name="require()">
<%
c.includes['ckeditor'] = True
c.includes['subtabs'] = True
c.includes['sortablejs'] = True
%>
</%def>
<%def name="active_menu()">
<% c.menu1 = 'testid' %>
</%def>
<%def name="page_headers()">
<style>
  tr.tr-border-sortable>td {
    border-top: 1px #B22F16 dashed;
    border-bottom: 1px #B22F16 dashed;
  }
  tr.tr-border-sortable>td:first-child {
    border-left: 1px #B22F16 dashed;
  }
  tr.tr-border-sortable>td:last-child {
    border-right: 1px #B22F16 dashed;
  }
</style>
</%def>

<% c.is_edit = c.user.has_permission('ekk-testid', const.BT_UPDATE, c.test) %>
% if not c.is_saved:
<%include file="tagasiside.translating.mako"/>
% endif
% if c.is_edit or c.is_tr:
${h.form_save(None)}
${h.hidden('lang', c.lang)}
% endif

<%
  nsgrupid = list(c.testiosa.nsgrupid)
  grid_id = 'tbl_nsg'
  prefix = 'nsg'
%>
% if c.is_edit or list(nsgrupid):

<table id="${grid_id}" class="m-2 table table-borderless table-striped nsgrupid"
       style="max-width:1000px;">
  % if c.is_edit:
  <col width="20px"/>
  <col/>
  <col width="30px"/>
  % else:
  <col/>
  % endif
  <thead>
    <tr>
      % if c.is_edit:
      <th></th>
      % endif
      ${h.th(_("Grupi nimetus"))}
      % if c.is_edit:
      <th></th>
      % endif
    </tr>
  </thead>
  <tbody class="sortables">
  % if c._arrayindexes != '' and not c.is_tr:
## valideerimisvigade korral
  %   for cnt in c._arrayindexes.get(prefix) or []:
        ${self.row_nsgrupp(c.new_item(), '%s-%s' % (prefix, cnt))}
  %   endfor
  % else:
## tavaline kuva
  %   for cnt,item in enumerate(nsgrupid):
        ${self.row_nsgrupp(item, '%s-%s' % (prefix, cnt))}
  %   endfor
  % endif
  </tbody>
% if c.is_edit:
  <tfoot id="sample_${grid_id}" class="d-none sample">
   ${self.row_nsgrupp(c.new_item(), '%s__cnt__' % prefix)}
  </tfoot>
% endif
</table>
% endif

<div class="d-flex">
  <div class="flex-grow-1">
% if c.is_edit:
${h.button(_("Lisa"), onclick=f"grid_addrow('{grid_id}',null,null,false,null,'nsg');on_addrow_nsg('{grid_id}');", level=2, mdicls='mdi-plus')}
% endif
  </div>
  ${h.submit()}
</div>
${h.end_form()}

<%def name="row_nsgrupp(item, prefix)">
<tr class="sortable ${c.is_edit and 'tr-border-sortable' or ''}">
  % if c.is_edit:
  <td>
    ${h.mdi_icon('mdi-drag-vertical')}
  </td>
  % endif
  <td>
    ${self.tran_editable('nimi', item, prefix + '.')}
    ${h.hidden('%s.id' % prefix, item.id)}
  </td>
  % if c.is_edit:
  <td>
    ${h.grid_remove()}
    <span class="glyphicon glyphicon-chevron-up tsg-up"></span>
    <span class="glyphicon glyphicon-chevron-down tsg-down"></span>
  </td>
  % endif
</tr>
</%def>              

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
% if c.is_edit:
${h.textarea(prefix + key, orig_val, ronly=False, class_="editable")}
% else:
${orig_val}
% endif
% endif
</%def>

% if c.is_edit or c.is_tr:
<div id="tts_ckeditor_top" class="ckeditor-top-float" style="z-index:100"></div>
<script>
function on_addrow_nsg(tableid)
{
    init_ckeditor_tbl('tts', tableid, -1, '${request.localizer.locale_name}', '${h.ckeditor_toolbar('basic')}', null, null, 'body16');
}
function tts_reinit_ckeditor()
{
    destroy_old_ckeditor();
    var inputs = $('.nsgrupid>tbody .editable');
    init_ckeditor(inputs, 'tts_ckeditor_top', '${request.localizer.locale_name}', '${h.ckeditor_toolbar('basic')}', null, null, 'body16');
}

$(function(){
% if c.is_edit:
    $('table.nsgrupid').on('click', '.tsg-up', function(){
        var tr = $(this).closest('tr')[0];
        if(tr.previousElementSibling)
        {
            tr.parentNode.insertBefore(tr, tr.previousElementSibling);
            tts_reinit_ckeditor();
        }
    });
    $('table.nsgrupid').on('click', '.tsg-down', function(){
        var tr = $(this).closest('tr')[0];        
        if(tr.nextElementSibling)
        {
            tr.parentNode.insertBefore(tr.nextElementSibling, tr);
            tts_reinit_ckeditor();
        }
    }); 
## gruppide järjestuse muutmine
    $('tbody.sortables').each(function(n, sortables){
        new Sortable(sortables, {
            animation: 150,
        });
    });
    $("tbody.sortables").disableSelection();
% endif
    tts_reinit_ckeditor();
});
</script>
% endif
