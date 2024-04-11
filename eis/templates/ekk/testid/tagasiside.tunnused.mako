<%inherit file="/common/formpage.mako"/>
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
table.form td.fbl {backround-color: #fff; height:30px; vertical-align:bottom; font-weight:bold;}
.border-sortable {
    border: 1px #B22F16 dashed;
}
</style>

</style>
</%def>

${h.form_save(None)}
<%include file="translating.mako"/>
<%include file="tagasiside.translating.mako"/>
${h.hidden('lang', c.lang)}
${h.hidden('is_tr', c.is_tr)} 
${h.hidden('op', 'jrk')}
${h.hidden('ting', c.ting)}

<div class="profiiliseaded">
  <%
    c.n_norm = c.grupp_index = 0
    normipunktid = [r for r in c.testiosa.normipunktid]
  %>
  ${self.normipunktid(normipunktid, '', None)}
</div>

<div class="d-flex flex-wrap">
  <div class="flex-grow-1">
% if c.test.diagnoosiv:
${h.btn_to(_("Näita puud"), h.url_current('index', sub='tree', lang=c.lang), target='.dtree', level=2)}
% endif

% if normipunktid:
${h.button(c.ting and _("Peida tingimused") or _("Kuva koos tingimustega"), class_="bting", level=2)}
  <script>
    $(function(){
    $('.bting').click(function(){
    dirty=false;window.location.replace("${h.url_current('index', lang=c.lang, ting=not c.ting and 1 or 0)}");
    });
    });
  </script>
% endif  
% if c.is_edit and not c.is_tr:
${h.btn_to_dlg(_("Lisa"), h.url_current('new', alatestigrupp_id=None), title=_("Tagasiside tunnus"), size='lg')}
% endif

  </div>
  <div>
% if c.is_edit and not c.is_tr and normipunktid:
  ${h.submit(_("Salvesta järjekord"))}
% endif
  </div>
</div>
${h.end_form()}
% if c.is_edit and not c.lang:
<script>
<%include file="normipunktid.js"/>
</script>
% endif

% if c.test.diagnoosiv:
<div class="dtree" style="margin:5px 0"></div>
% endif

<%def name="normipunktid(normipunktid, grupp_prefix, grupp_id)">
<%
  prefix = 'normid'
  c.grupp_index += 1
  grid_id = 'grid_norm%d' % c.grupp_index
  atg_id = None
%>
    <div id="${grid_id}" data-grupp-prefix="${grupp_prefix}"
         % if c.is_edit:
         class="grupinormid sortables" style="min-height:30px">
         % else:
         class="grupinormid">
         % endif
      %   for cnt,item in enumerate(normipunktid):
         % if atg_id != item.alatestigrupp_id:
         <% atg_id = item.alatestigrupp_id %>
         <h2>
         % if atg_id:
         ${item.alatestigrupp.nimi}
         % else:
         ${_("Ei kuulu gruppi")}
         % endif
         </h2>
         % endif
         ${self.row_normipunkt(item, '%s-%s' % (prefix, c.n_norm), grupp_prefix)}
         <% c.n_norm += 1 %>         
      %   endfor
    </div>
    % if c.is_edit and not c.lang:
    <%
      label = not c.on_grupid and _("Lisa") or \
         grupp_prefix and _("Lisa väli gruppi") or \
         _("Lisa")
      title = ''
    %>
    % endif
</%def>


<%def name="row_normipunkt(item, prefix, grupp_prefix)">
<div class="norm ${c.is_edit and 'sortable border-sortable' or 'border'} rounded m-3 p-2" style="max-width:1000px">
  <table width="100%">
  <%
    orig_edit = c.is_edit
    c.is_edit = False
    orig_tr = c.is_tr
    c.is_tr = False
    c.normipunkt = item
  %>
  <tr>
    <td>
      <div id="drnp${item.id}">
        <%include file="normipunkt.mako"/>
      </div>
  <%
    c.is_edit = orig_edit
    c.is_tr = orig_tr
  %>
  ${h.hidden('%s.id' % prefix, item.id or '')}
  ${h.hidden('%s.grupp_prefix' % prefix, grupp_prefix)}
    </td>
  % if c.is_edit or c.is_tr:
    <td width="60px" valign="top">
      ${h.btn_to_dlg('', h.url_current('edit', id=item.id, lang=c.lang, is_tr=c.is_tr), style="float:right",
      title=_("Muuda"),
      dlgtitle=_("Tagasiside tunnus"), level=0, mdicls='mdi-file-edit', size='lg')}      
      % if not c.lang:
      <div style="float:right">${h.grid_s_remove('.norm', confirm=True)}</div>
      % endif
    </td>
  % endif
  </tr>
  </table>
</div>

</%def>
