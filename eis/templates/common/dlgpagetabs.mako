<%inherit file="/common/dlgpage.mako"/>
## Dialoogiaknas kuvatav lk, millel on sakid

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

<%def name="draw_tabs()">
</%def>
