<%inherit file="/common/page.mako"/>
<%namespace name="tab" file='/common/tab.mako'/>
<%def name="require()">
<% 
   c.includes['test'] = True
%>
</%def>

<%def name="page_title()">
${c.ylesanne.nimi}
</%def>
<%def name="breadcrumbs()">
${h.crumb(_("Sooritus"), h.url('sooritamised'))} 
${h.crumb(c.test.nimi, h.url('sooritamine_tooylesanded', test_id=c.test.id, sooritus_id=c.sooritus.id))}
${h.crumb(c.ylesanne.nimi)}
</%def>

<div class="testinst">
  % if not c.read_only:
  <span class="is_test_ongoing"></span>
  % endif
  
  ${self.task_contents()}
  ${self.task_buttons()}
</div>

<%def name="task_contents()">
<div class="testtys tools-null">
  <div class="testtys-before"></div>
  <% task_url = c.is_edit and h.url_current('edittask') or h.url_current('showtask') %>
  <iframe name="itask1" class="ylesanne" src="${task_url}"
          onload="on_iframe_ylesanne_load(this)"
          width="100%" height="100px" scrolling="no" frameBorder="0"
          aria-label="${_("Ülesande sisu")}">          
  </iframe>
  <iframe name="itask2" class="tmptask"
          onload="on_iframe_ylesanne_load(this)"
          width="100%" height="100px" scrolling="no" frameBorder="0"
          aria-label="${_("Ülesande sisu")}">          
  </iframe>

  <div class="testtys-after"></div>
</div>
</%def>

<%def name="task_buttons()">
<div class="d-flex flex-wrap mb-3">
  ${self.task_nav()}
  ${h.spinner(_("Laadin ülesannet..."), 'taskloadspinner mx-3', hide=False)}
</div>
</%def>

<%def name="task_nav()">
<%
  div_cls = ''
  if c.ylesanne.lahendada_lopuni and not c.read_only:
     div_cls = 'finish-task'
%>

<div class="ifshow" style="display:none">
  ${h.btn_back(url=h.url_current('index'))}
</div>

% if c.ylesanne.is_interaction:
<div class="ifedit ${div_cls}" style="display:none">
${h.button(_("Katkesta"), onclick="save_work_task()", level=2)}
${h.button(_("Salvesta ja kinnita"), onclick="end_work_task()")}
</div>
% else:
<div class="ifedit" style="display:none">
  ${h.btn_back(url=h.url_current('edit'))}
</div>
% endif

% if c.url_try:
<div class="ifshow" style="display:none">
  ${h.btn_to(_("Proovi uuesti"), c.url_try, method='get')}
</div>
% endif
</%def>
            
