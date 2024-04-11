<%inherit file="/common/formpage.mako"/>
<%def name="require()">
<%
   if c.user.has_permission('avylesanded', const.BT_SHOW, c.item):
      c.includes['subtabs'] = True
   c.includes['test'] = True
%>
</%def>

<%def name="page_title()">
% if c.user.has_permission('avylesanded', const.BT_SHOW, c.ylesanne):
${c.item.nimi} | ${_("Lahendamine")}
% else:
${c.item.nimi}
% endif
</%def>      

<%def name="breadcrumbs()">
${h.crumb(_("Minu töölaud"), h.url('tookogumikud'))} 
${h.crumb(c.item.nimi, h.url('ylesanne', id=c.item.id))}
% if c.user.has_permission('avylesanded', const.BT_SHOW, c.ylesanne):
${h.crumb(_("Sisu"), h.url('ylesanded_sisu', id=c.item.id))} 
${h.crumb(_("Lahendamine"))}
% endif
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

<% 
c.ylesanne = c.item
%>
<div class="testinst">
  <% c.ylesanne = c.item %>
  ${h.form_save(c.item.id, form_name="form_save_responses", multiple=True, autocomplete='off')}
  ${h.hidden('list_url', c.list_url, class_="list_url")}
  ${h.hidden('prev_id', c.prev_id)}
  ${h.hidden('next_id', c.next_id)}
  ${h.hidden('temp_id', model.gen_temp_id())}
  ${h.hidden('yv_id', c.yv_id)}
  % if not c.read_only:
  <div class="in-write"></div>
  % endif
  <div class="d-flex flex-wrap justify-content-end tools-null">  
    <div class="flex-grow-1">
    <%
    aine_nimi = aine_kood = keeletase_nimi = None
    teemad = []
    for ya in c.ylesanne.ylesandeained:
        if not aine_nimi:
            aine_nimi = ya.aine_nimi
            aine_kood = ya.aine_kood
        for yt in ya.ylesandeteemad:
            teema_nimi = yt.teema_nimi
            if teema_nimi not in teemad:
                teemad.append(teema_nimi)
    aste_nimed = c.ylesanne.aste_nimed
    if c.ylesanne.keeletase_kood:
        keeletase_nimi = model.Klrida.get_str('KEELETASE', c.ylesanne.keeletase_kood, ylem_kood=aine_kood)
    %>
    <div>${aine_nimi}</div>
    % if aste_nimed:
    <div>${c.ylesanne.aste_nimed}</div>
    % endif
    % if teemad:
    <div>
      % for teema in teemad:
      <div>${teema}</div>
      % endfor
    </div>
    % endif
    % if keeletase_nimi:
    <div>${keeletase_nimi}</div>
    % endif
    % if c.ylesanne.autor:
    <div>${_("Autor")}: ${c.ylesanne.autor}</div>
    % endif
    % if c.ylesanne.kvaliteet_kood:
    <div>${_("Kvaliteedimärk")}: ${c.ylesanne.kvaliteet_nimi}</div>
    % endif
    % if c.ylesanne.markus:
    <div>
      <div onclick="$('.markus').toggle()" style="text-decoration:underline;cursor:pointer;">Märkused</div>
      <div class="markus" style="display:none">
        ${c.ylesanne.markus.replace('\n', '<br/>')}
      </div>
    </div>
    % endif
  </div>
  
    % if len(c.item.keeled) > 1:
    <div class="m-2">
      ${_("Vali keel")}: 
      % for lang in c.item.keeled:
      ${h.radio('lang', lang, checkedif=c.lang or c.item.lang, 
      href=h.url('ylesanded_lahendamine',id=c.item.id, lang=lang), class_='LISTPOST',
      label=model.Klrida.get_str('SOORKEEL', lang))}
      % endfor
    </div>
    % endif
    <div class="m-2">
      % if c.item.max_pallid:
      <b> ${_("max {p}p").format(p=h.fstr(c.item.max_pallid or 0))} </b>
      % endif
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
  </div>
  
  <div class="d-flex flex-wrap">
    <div class="flex-grow-1 d-flex">
      ${h.btn_to(_("Töölaud"), h.url('tookogumikud'), level=2)}
      % if not c.read_only and c.item.is_interaction:
      <% cls = c.ylesanne.lahendada_lopuni and 'finish-task' or '' %>
      <div class="ifedit ${cls}">
        ${h.button(_("Salvesta ja kinnita"), onclick="end_task()")}
      </div>
      % endif
      <div class="taskloadspinner mx-3">
        ${h.spinner()}
      </div>
    </div>
    <div>
% if c.prev_id:
${h.btn_to(_("Eelmine"), h.url_current('edit', id=c.prev_id, lang=c.lang), method='LISTPOST', mdicls="mdi-arrow-left-circle", level=2)}
% endif
% if c.next_id:
${h.btn_to(_("Järgmine"), h.url_current('edit', id=c.next_id, lang=c.lang), method='LISTPOST', mdicls2="mdi-arrow-right-circle", level=2)}
% endif
  ${h.btn_to_dlg(_("Lisa töökogumikku"), 
   h.url_current('edit', id=c.item.id, sub='kogumikku'), method='get', width=300, mdicls="mdi-plus", level=2, title=_("Ülesande lisamine töökogumikku"))}
    </div>
  </div>
  ${h.end_form()}
</div>

% if c.user.has_permission('avylesanded', const.BT_UPDATE, c.ylesanne):
% if c.vastus:
<div width="100%">
<h1>${_("Antud vastused")}</h1>
${h.literal(c.vastus)}
</div>
% endif

% if c.calculation:
<div width="100%">
<h1>${_("Arvutuskäik")}</h1>
${h.literal(c.calculation)}
</div>
% endif
% endif

<script>
 $(function(){  
  ## paneme lingile loetelutingimused kaasa
  $('.LISTPOST').click(function(event) {
    var list_url = ($('input.list_url').length ? $('input.list_url').val() : '');
    $('<form method="POST" style="display:none"><input type="hidden" name="list_url" value="'+list_url+'" /></form>')
      .insertAfter($(this))
      .attr({
        action: $(this).attr('href')
      }).submit();
    return false;
  });
 });
</script>

