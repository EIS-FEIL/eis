<%inherit file="/common/dlgpage.mako"/>
<%namespace name="tab" file='/common/tab.mako'/>

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
<div class="tab-content collapse show">
  <div class="tab-pane fade show active" role="tabpanel" id="saajad">
    <div style="clear:both"></div>
    <div class="formpage-body">
      <%include file="saatmine.saajad.mako"/>
    </div>
  </div>

  <div class="tab-pane fade show" role="tabpanel" id="kirjasisu">
    <div style="clear:both"></div>
    <div class="formpage-body">
      <%include file="saatmine.kirjasisu.mako"/>
    </div>
  </div>
</div>

<%def name="draw_tabs()">
${tab.draw('saajad', '#saajad', _("Nimekiri"), 'saajad')}
${tab.draw('kirjasisu', '#kirjasisu', _("Kirja sisu"))}
</%def>
