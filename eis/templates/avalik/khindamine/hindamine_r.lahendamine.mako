<%inherit file="/common/tabpage.mako"/>
<div id="lahendamine_div" class="testinst">
<%
  if c.show_correct:
     c.r_tab = 'correct'
  else:
     c.r_tab = 'lahendamine'
%>
<%include file="hindamine_r_tabs.mako"/>
<div id="hindamine_r_body">
<%include file="/common/message.mako"/>

% if len(c.item.vahendid):
<div class="d-flex justify-content-end tools-null">
    <div class="tools m-2">
      <%include file="/avalik/lahendamine/tools.mako"/>
    </div>
</div>
% endif

<div class="testtys">
  % if not c.read_only:
  <div class="in-write"></div>
  % endif
  <div class="testtys-before"></div>
  <%
    if c.show_correct:
       task_url = h.url_current('correct', id=c.item.id, task_id=c.item.id, lang=c.lang)
    else:
       task_url = h.url_current('edittask', id=c.item.id, lang=c.lang, yv_id=c.yv_id, kl_id=c.klaster_id)
    %>
  <iframe name="ritask1" class="ylesanne" src="${task_url}"
          onload="on_iframe_ylesanne_load(this)"
          width="100%" height="100px" scrolling="no" frameBorder="0"
          aria-label="${_("Ülesande sisu")}">          
  </iframe>
  <iframe name="ritask2" class="tmptask"
          onload="on_iframe_ylesanne_load(this)"
          width="100%" height="100px" scrolling="no" frameBorder="0"
          aria-label="${_("Ülesande sisu")}">          
  </iframe>
  <div class="testtys-after"></div>
</div>

% if not c.show_correct and c.ylesanne.is_interaction:
<div class="d-flex justify-content-end">
  ${h.spinner(_("Laadin ülesannet..."), 'taskloadspinner mx-3', hide=False)}
  <% cls = c.item.lahendada_lopuni and 'finish-task' or '' %>
  <div class="ifedit ${cls}">
    ${h.button(_("Salvesta ja kinnita"), id="endtask")}
    <script> $('button#endtask').click(function(){  end_task();  }); </script>
  </div>
</div>
% endif
</div>
</div>
