<%inherit file="/avalik/lahendamine/esitlus.mako"/>
<%def name="outside_contents()">
<div id="testtys1" style="display:none">
${self.before_item()}
<div class="tools d-flex justify-content-end"></div>
</div>

<div id="testtys2" style="display:none">
${self.after_item(c.vy, c.ylesandevastus)}
${self.task_buttons(c.ty)}
</div>
</%def>

<%def name="ty_skann(ty, ylesandevastus)">
% if c.prepare_correct and c.ylesandevastus and c.ylesandevastus.skann:
<div class="my-1">
      ${h.image(h.url('tulemus_yvskann', sooritus_id=c.sooritus.id,
      id=c.ylesandevastus.id), width=c.ylesandevastus.laius_orig and c.ylesandevastus.laius_orig/4)}
</div>
% endif
</%def>

<%def name="task_buttons(ty)">
<div class="d-flex flex-wrap mb-3">
  ${self.marking_task_buttons()}
  ${h.spinner(_("Laadin ülesannet..."), 'taskloadspinner mx-3', hide=True)}
</div>
</%def>

<%def name="marking_task_buttons()">
## hindamise korral kirjutatakse üle
</%def>
            
<%def name="before_item()">
## vajadusel kirjutatakse üle
</%def>

<%def name="after_item(vy, ylesandevastus)">
## hindamise korral kirjutatakse üle
</%def>

