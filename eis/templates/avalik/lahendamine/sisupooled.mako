## -*- coding: utf-8 -*-
## ylesande kaks poolt
<%
width1 = c.ylesanne.paan1_laius
if not (width1 and 0 < width1 < 100):
   width1 = 50
width2 = 100 - width1
# borderi ja paddingu tõttu ei ole 100% kasutada, kasutame 95%
width2 *= .95
width1 *= .95                                
%>
<div class="task-panes">
  <div class="task-pane task-pane-left" id="taskpane0" style="width:${width1}%" data-width="${width1}%">
    <div class="fix1-toggle-pane" style="width:160px">
     <div class="fix-toggle-pane">
       ${h.button(_("Peida pool"), class_='toggle-pane', mdicls='mdi-arrow-left-circle', id="bhpane1", level=2)}
     </div>
    </div>
    <div style="height:45px"> </div>
    ${c.paanid_html.get(0) or ''}
  </div>
  <div class="task-pane task-pane-right" id="taskpane1" style="width:${width2}%" data-width="${width2}%">
    <div class="fix-toggle-pane">
      ${h.button(_("Peida pool"), class_='toggle-pane', mdicls2='mdi-arrow-right-circle', id="bhpane2", level=2)}
    </div>
    <div style="height:45px"> </div>
    ${c.paanid_html.get(1) or ''}
  </div>
</div>
