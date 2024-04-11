## Mall lipikutega vormidele
<%inherit file="/common/page.mako"/>

${self.draw_before_tabs()}
${self.page_main_tabs()}

<%def name="page_main_tabs()">
<% is_tabs = not c.hide_header_footer and not c.no_tabs %>
${self.page_main_tabs_(is_tabs)}
</%def>

<%def name="page_main_tabs_(is_tabs)">
% if is_tabs:
## sakid laia akna korral
<ul class="nav nav-tabs d-none d-md-flex" role="tablist">
  <% c.tabs_mode = 'li' %>
  ${self.draw_tabs()}
</ul>

## sakid esimesest kuni jooksva sakini kitsa akna korral
<div class="accordion d-block d-md-none" id="navacc1">
  <% c.tabs_mode, c.tabs_current1 = 'accordion1', None %>
  ${self.draw_tabs()}
</div>

## valitud saki sisu
<div class="tab-content collapse show" id="main_tab_content">
  <div class="tab-pane fade show active" role="tabpanel">
    % if 'before_subtabs' in c.includes:
    ${self.draw_before_subtabs()}
    % endif
    % if 'subtabs' in c.includes:
    <ul class="nav nav-pills mb-3 float-left" role="tablist">
      <% c.tabs_mode = 'subli' %>
      ${self.draw_subtabs()}
    </ul>
    % endif
    % if 'subtabs_label' in c.includes:
    <ul class="nav nav-pills mb-3 float-right">    
      <li class="nav-item responsive-tabs">
      ${self.subtabs_label()}
      </li>
    </ul>
    % endif
    <div style="clear:both"></div>
    <div class="formpage-body">
      ${next.body()}
    </div>
  </div>
</div>

## jooksvale sakile järgnevad sakid kitsa akna korral
<div class="accordion d-block d-md-none" id="navacc2">
  <% c.tabs_mode, c.tabs_current2 = 'accordion2', None %>
  ${self.draw_tabs()}
</div>

% else:
<div class="formpage-body">
  ${next.body()}
</div>
% endif
</%def>

<%def name="draw_tabs()">
## siin tuleks kutsuda välja tab.mako faili funktsiooni draw() iga lipiku kohta
</%def>

<%def name="draw_subtabs()">
## siin tuleks kutsuda välja tab.mako faili funktsiooni subdraw() iga lipiku kohta
</%def>

<%def name="tabs_label()">
## kui tahad midagi kuvada lipikuterea paremas servas
</%def>

<%def name="subtabs_label()">
## kui tahad midagi kuvada alamlipikuterea paremas servas
</%def>

<%def name="draw_before_tabs()">
## kui tahad midagi kuvada enne lipikuterida
</%def>

<%def name="draw_before_subtabs()">
## kui tahad midagi kuvada enne alamlipikuterida
</%def>

