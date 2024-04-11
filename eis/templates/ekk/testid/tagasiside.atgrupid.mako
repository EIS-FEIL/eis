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
<%include file="tagasiside.translating.mako"/>

% if c.is_edit or c.is_tr:
${h.form_save(None)}
${h.hidden('lang', c.lang)}
${h.hidden('is_tr', c.is_tr)}
% endif

<%
  grid_id = 'gridg'
  prefix = 'atg'
%>

<table class="m-2 table table-borderless table-striped" id="${grid_id}"
       style="max-width:1000px;">
  % if c.is_edit:
  <col width="20px"/>
  % endif
  <col/>
  % if c.is_edit:
  <col width="20px"/>
  % endif
  <thead>
    <tr>
      % if c.is_edit:
      <th></th>
      % endif
      <th>${_("Grupi nimetus")}</th>
      % if c.is_edit:
      <th></th>
      % endif
    </tr>
  </thead>
  <tbody class="sortables">
  % if c._arrayindexes != '' and not c.is_tr:
## valideerimisvigade korral
  %   for cnt in c._arrayindexes.get(prefix) or []:
        ${self.row_grupp(c.new_item(), '%s-%s' % (prefix, cnt))}
  %   endfor
  % else:
## tavaline kuva
  %   for cnt,item in enumerate(c.testiosa.alatestigrupid):
        ${self.row_grupp(item, '%s-%s' % (prefix, cnt))}
  %   endfor
  % endif
  </tbody>
% if c.is_edit and not c.lang:
  <tfoot id="sample_${grid_id}" class="d-none sample">
    
   ${self.row_grupp(c.new_item(), '%s__cnt__' % prefix)}
  </tfoot>
% endif
  
</table>

<div class="d-flex">
  <div class="flex-grow-1">
    % if c.is_edit and not c.lang:
    ${h.button(_("Lisa"), onclick=f"grid_addrow('{grid_id}');", level=2, mdicls='mdi-plus')}
    % endif
  </div>
  % if c.is_edit or c.is_tr:
  ${h.submit()}
  % endif
</div>
${h.end_form()}

<%def name="row_grupp(grupp, prefix)">
  <tr class="sortable ${c.is_edit and 'tr-border-sortable' or ''}">
    % if c.is_edit:
    <td>${h.mdi_icon('mdi-drag-vertical')}
    % endif
    <td>
      ${self.tran_editable('nimi', grupp, prefix + '.')}
      ${h.hidden(prefix + '.id', grupp.id)}
    </td>
    % if c.is_edit:
    <td>
      ${h.grid_s_remove('tr', confirm=True)}      
    </td>
    % endif
  </tr>
</%def>

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
##${h.textarea(prefix + key, tran_val,ronly=False,class_="editable editable70")}
${h.text(prefix + key, tran_val, maxlength=256, ronly=False)}
% else:
${tran_val}
% endif
% else:
% if c.is_edit:
##${h.textarea(prefix + key, orig_val,ronly=not c.is_tr and not c.is_edit, class_="editable editable70")}
${h.text(prefix + key, orig_val, maxlength=256)}
% else:
${orig_val}
% endif
% endif
</div>
</%def>

% if c.is_edit:
<script>
## gruppide järjestuse muutmine
    $('tbody.sortables').each(function(n, sortables){
        new Sortable(sortables, {
            animation: 150,
        });
    });
    $("tbody.sortables").disableSelection();
</script>
% endif
