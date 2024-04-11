<%inherit file="/common/formpage.mako"/>
<%def name="draw_tabs()">
<%include file="tabs.mako"/>
</%def>

<%def name="page_title()">
${c.test.nimi or ''} | ${_("Tulemused")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_('Minu töölaud'), h.url('tookogumikud'))} 
${h.crumb(c.test.nimi or _('Test'))} 
${h.crumb(_('Tulemused'))}
</%def>
<%def name="require()">
<%
  c.includes['googlecharts'] = c.includes['googlecharts.corechart'] = True
  c.includes['plotly'] = True
%>
</%def>
<%def name="active_menu()">
<% c.menu1 = 'tookogumikud' %>
</%def>

<%def name="page_headers()">
<style>
  <%include file="/avalik/tagasiside/tagasiside.css"/>
</style>
</%def>

<div class="d-flex flex-wrap mb-2">
<h1 class="h2">
  ${c.test.nimi}
  ${c.millal}
</h1>
<div class="flex-grow-1 text-right">
  ${self.lang_sel(c.test.lang, c.test_keeled)}
</div>
</div>

<div class="row">
  <div class="col-sm-4 col-md-3">
    ${h.form_search()}
    ${h.hidden('lang', c.lang)}
    <div class="listdiv text-truncate">
      <%include file="tulemused.tagasiside_list.mako"/>
    </div>
    ${h.end_form()}
  </div>
  <div class="col-sm-8 col-md-9">
    ${self.sisu()}
    % if c.tagasiside_html:
    ${h.btn_to(_("PDF"), h.url_current('download', id=0, format='pdf', lang=c.lang), level=2, class_="mt-3")}
    % endif
  </div>
</div>

<%def name="sisu()">
${c.tagasiside_html}
</%def>

<%def name="lang_sel(pohikeel, keeled)">
<div align="right" width="100%" class="brown">
  % if len(keeled) == 1:
    ${model.Klrida.get_str('SOORKEEL', pohikeel)}
  % else:
    % for lang in keeled:
      % if lang == pohikeel:
      ${h.radio('lang', '', checked=not(c.lang) or c.lang==lang, ronly=False, class_="nosave",
      label='%s (%s)' % (model.Klrida.get_str('SOORKEEL', lang), _("põhikeel")))}
      % else:
       ${h.radio('lang', lang, checkedif=c.lang, ronly=False, class_="nosave",
       label=model.Klrida.get_str('SOORKEEL', lang))}
      % endif
    % endfor
    <script>
    $(function(){
    $('input[name="lang"]').click(function(){
    var lang = $(this).val();
    var url = "${h.url_current(lang='__LANG__')}".replace("__LANG__", lang);
    window.location.replace(url);
    dirty = false;
    });
    });
    </script>
  % endif
</div>
</%def>
