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

<%include file="translating.mako"/>
% if not c.is_saved:
<%include file="tagasiside.translating.mako"/>
% endif

% if c.is_edit or c.is_tr:
${h.form_save(None)}
${h.hidden('lang', c.lang)}
${h.hidden('is_tr', c.is_tr)}
% endif

<%
  ylgrupid = list(c.testiosa.ylesandegrupid)
  grid_id = 'tbl_ylg'
  prefix = 'ylg'
%>
% if c.is_edit or list(ylgrupid):
<table  cellpadding="4"
       id="${grid_id}" class="table table-borderless table-striped ylgrupid"
        style="margin:5px;width:100%;max-width:1000px;">
  % if c.is_edit:
  <col width="20px"/>
  % endif
  <col/>
  <thead>
    <tr>
      % if c.is_edit:
      <th></th>
      % endif
      ${h.th(_("Grupi nimetus"))}
      ${h.th(_("Ülesanded"), colspan=2)}
      <th></th>
    </tr>
  </thead>
  <tbody class="sortables">
  % if c._arrayindexes != '' and not c.is_tr:
## valideerimisvigade korral
  %   for cnt in c._arrayindexes.get(prefix) or []:
        ${self.row_ylgrupp(c.new_item(), '%s-%s' % (prefix, cnt))}
  %   endfor
  % else:
## tavaline kuva
  %   for cnt,item in enumerate(ylgrupid):
        ${self.row_ylgrupp(item, '%s-%s' % (prefix, cnt))}
  %   endfor
  % endif
  </tbody>
% if c.is_edit:
  <tfoot id="sample_${grid_id}" class="d-none sample">
   ${self.row_ylgrupp(c.new_item(), '%s__cnt__' % prefix)}
  </tfoot>
% endif
</table>
% endif

<div class="d-flex">
  <div class="flex-grow-1">
  % if c.is_edit:
${h.button(_("Lisa"), onclick=f"grid_addrow('{grid_id}',null,null,false,null,'ylg');on_addrow_ylg('{grid_id}');", level=2, mdicls='mdi-plus')}
  % endif
  </div>
  ${h.submit()}
</div>
${h.end_form()}

<%def name="row_ylgrupp(item, prefix)">
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
  <td>
    % if item.id:
    <span id="ylcnt${item.id}">${len(item.grupiylesanded)}</span>
    % else:
    0
    % endif
  </td>
  <td>
    % if item.id:
    <%
      if c.is_edit:
         url = h.url_current('edit', id=item.id)
      else:
         url = h.url_current('show', id=item.id)
    %>
    ${h.btn_to_dlg('', url,
    title=_("Vali ülesanded"), dlgtitle=_("Ülesannete valik"), level=0, mdicls='mdi-playlist-edit')}
    % endif
  </td>
  </td>
  % if c.is_edit:
  <td>
    ${h.grid_s_remove('tr', confirm=True)}
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
## ckeditor
<div id="tts_ckeditor_top" class="ckeditor-top-float" style="z-index:100"></div>
<script>
function on_addrow_ylg(tableid)
{
    init_ckeditor_tbl('tts', tableid, -1, '${request.localizer.locale_name}', '${h.ckeditor_toolbar('basic')}', null, null, 'body16');
}
function tts_reinit_ckeditor()
{
    destroy_old_ckeditor();
    var inputs = $('.ylgrupid>tbody .editable');
    init_ckeditor(inputs, 'tts_ckeditor_top', '${request.localizer.locale_name}', '${h.ckeditor_toolbar('basic')}', null, null, 'body16');
}

$(function(){
% if c.is_edit:
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
