<%inherit file="/common/formpage.mako"/>
<%namespace name="tab" file='/common/tab.mako'/>
<%def name="require()">
<% 
   c.includes['test'] = True
%>
</%def>
<%def name="active_menu()">
<% c.menu1 = 'lahendamine' %>
</%def>
<%def name="draw_tabs()">
${tab.draw('lahendamine', None, c.item.nimi, True)}
</%def>

<%def name="page_title()">
${c.item.nimi}
</%def>
<%def name="breadcrumbs()">
${h.crumb(_("Avalikud ülesanded"), h.url('lahendamine'))} 
${h.crumb(c.item.nimi)}
</%def>

<div class="testinst">
  % if not c.read_only:
  <div class="in-write"></div>
  % endif
  <% c.ylesanne = c.item %>
  ${h.form_save(c.item.id, multiple=True, autocomplete='off')}
  ${h.hidden('list_url', c.list_url, class_="list_url")}
  ${h.hidden('prev_id', c.prev_id)}
  ${h.hidden('next_id', c.next_id)}
  ${h.hidden('yv_id', c.yv_id)}

  <div class="d-flex justify-content-end tools-null">
    % if len(c.item.keeled) > 1:
    <div class="m-2">
      ${_("Vali keel")}: 
      % for lang in c.item.keeled:
      ${h.radio('lang', lang, checkedif=c.lang or c.item.lang, 
      href=h.url_current('show', id=c.item.id, lang=lang), class_='LISTPOST', ronly=False,
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
  
  <div class="testtys">
    <div class="testtys-before"></div>  
    <% task_url = h.url_current('edittask', lang=c.lang, yv_id=c.yv_id, kl_id=c.klaster_id) %>
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
    ${self.task_buttons()}
  </div>
  
  ${h.end_form()}
</div>

<script>
 $(function(){  
  ## paneme lingile loetelutingimused kaasa
   $('.LISTPOST').click(function(event) {
    var list_url = ($('.list_url').length ? $('.list_url').val() : '');
    $('<form method="POST" style="display:none"><input type="hidden" name="list_url" value="'+list_url+'" /></form>')
      .insertAfter($(this))
      .attr({
        action: $(this).attr('href')
      }).submit();
    return false;
  });
 });
</script>

<%def name="task_buttons()">
  <div class="d-flex flex-wrap">
    <div class="flex-grow-1 d-flex flex-wrap">
      ${h.btn_back(url=c.list_url or h.url('lahendamine'))}
      
      % if c.item.is_interaction:
      <div class="ifedit">
        % if c.item.lahendada_lopuni:
        <span class="finish-task">
          % endif
          ${h.button(_("Salvesta ja kinnita"), onclick="end_task()")}
          % if c.item.lahendada_lopuni:
        </span>
        % endif
      </div>
      % endif
      <div class="taskloadspinner mx-3">
        ${h.spinner()}
      </div>
    </div>
    
    <div>
      % if c.prev_id:
      ${h.btn_to(_("Eelmine"), h.url('lahendamine1', id=c.prev_id, lang=c.lang), method='LISTPOST', level=2, mdicls="mdi-arrow-left-circle")}
      % endif
      % if c.next_id:
      ${h.btn_to(_("Järgmine"), h.url('lahendamine1', id=c.next_id, lang=c.lang), method='LISTPOST', level=2, mdicls2="mdi-arrow-right-circle")}
      % endif
    </div>
  </div>
</%def>  
