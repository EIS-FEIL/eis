<%inherit file="/common/formpage.mako"/>
<%def name="require()">
<% 
   c.includes['subtabs'] = True 
   c.includes['test'] = True
%>
</%def>

<%def name="page_title()">
${c.item.nimi} | ${_("Lahendamine")}
</%def>      

<%def name="breadcrumbs()">
${h.crumb(_("Ülesandepank"), h.url('ylesanded'))} 
${h.crumb(c.item.nimi, h.url('ylesanne', id=c.item.id))} 
${h.crumb(_("Sisu"), h.url('ylesanded_sisu', id=c.item.id))} 
${h.crumb(_("Lahendamine"))}
</%def>

<%def name="draw_tabs()">
<% c.tab1 = 'sisu' %>
<%include file="tabs.mako"/>
</%def>

<%def name="draw_subtabs()">
<%
c.tab2 = 'lahendamine'
c.ylesanne = c.item
%>
<%include file="sisuplokk.tabs.mako"/>
</%def>
<%def name="active_menu()">
<% c.menu1 = 'ylesanded' %>
</%def>

<% 
c.ylesanne = c.item
%>
<div class="testinst">
  % if not c.read_only:
  <div class="in-write"></div>
  % endif

  <div class="testtys">
    <div class="d-flex justify-content-end tools-null">
      % if len(c.item.keeled) > 1:
      <div class="m-2">
        ${_("Vali keel")}: 
        % for lang in c.item.keeled:
        ${h.radio('lang', lang, checkedif=c.lang or c.item.lang, ronly=False,
        href=h.url_current('show', id=c.item.id, lang=lang), class_='get',      
        label=model.Klrida.get_str('SOORKEEL', lang))}
        % endfor
      </div>
      % endif
      <div class="m-2">
        <b> ${_("max {p}p").format(p=h.fstr(c.item.max_pallid))} </b>
      </div>
      % if len(c.item.vahendid):
      <div class="tools m-2">
        <%include file="/avalik/lahendamine/tools.mako"/>
      </div>
      % endif
    </div>

    <div class="testtys-before"></div>  
    <% task_url = h.url_current('edittask', lang=c.lang, kl_id=c.klaster_id, yv_id=c.yv_id) %>
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

    <div class="d-flex flex-wrap">
      <% cls = c.ylesanne.lahendada_lopuni and 'finish-task' or '' %>
      % if c.item.is_interaction:
      <div class="ifedit ${cls}">
        ${h.button(_("Salvesta ja kinnita"), onclick="end_task()")}
      </div>
      % endif
      <div class="taskloadspinner mx-3">
        ${h.spinner()}
      </div>
    </div>
  </div>
    
</div>

% if c.vastus:
<div class="mt-4">
<h2>${_("Antud vastused")}</h2>
${h.literal(c.vastus)}
</div>
% endif

% if c.calculation:
<div class="mt-4">
<h2>${_("Arvutuskäik")}</h2>
${h.literal(c.calculation)}
</div>
% endif

