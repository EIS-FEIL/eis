<%inherit file="/avalik/sooritamine/sooritus.mako"/>

<%def name="active_menu()">
<% c.menu1 = 'testid' %>
</%def>

<%def name="page_title()">
${_("Testi eelvaade")}
| ${c.test.nimi} 
% if c.testiosa.nimi:
| ${c.testiosa.nimi}
% endif
</%def>      

<%def name="breadcrumbs()">
${h.crumb(_("Testid"), h.url('testid'))} 
${h.crumb(c.test.nimi or _("Test"), h.url('test', id=c.test.id))} 
${h.crumb(_("Ülesanded"), request.handler._url_out())}
${h.crumb(_("Eelvaade"))}
</%def>


<%def name="testiosasisu()">
<% 
  # c.url_to_alatest on vajalik, kui EKK test on antud avalikuks kasutamiseks
  #if c.sooritus and c.sooritus.staatus in (const.S_STAATUS_TEHTUD, const.S_STAATUS_KATKESTATUD):
  if c.read_only:
     c.url_to_alatest = lambda alatest : h.url_current('show', alatest_id=alatest.id)
  else:
     c.url_to_alatest = lambda alatest : h.url_current('edit', alatest_id=alatest.id)
  c.submit_url = h.url_current('update', alatest_id=c.alatest and c.alatest.id or '')

  if not c.test.oige_naitamine and not c.toimumisaeg:
     c.prepare_correct = False
     c.btn_correct = False

  c.submit_method = 'post'
  c.preview = True
  c.olen_sooritaja = True
  c.url_back_post = h.url_current('delete')
%>

% if c.no_tabs:
<h1>${c.test.nimi}</h1>
% endif

% if c.read_only and c.tagasiside_html:
## and c.test.diagnoosiv:
${c.tagasiside_html}
% endif

<%include file="eelvaade.testiosasisu.mako"/>

% if not c.read_only:
<span class="is_test_ongoing"></span>
% endif
</%def>

<%def name="draw_before_tabs()">
<div class="d-flex flex-wrap mb-4 py-3 bg-gray-50">
  <h3  class="mr-3">
    % if c.e_komplekt_id:
    ${_("Komplekti eelvaade")}
    % else:
    ${_("Testi eelvaade")}
    % endif
  </h3>
  <div class="mr-3">
    ${h.btn_to(_("Välju eelvaatest"), h.url_current('delete'), method='post', spinnerin=True, level=2)}
  </div>
  <div class="mr-3">
    ${h.button(_("Proovi uuesti"), level=2, id="proovi")}
  </div>
  
  % if (c.test.diagnoosiv or c.is_debug and (c.testiosa.pos_yl_list == const.POS_NAV_HIDDEN)) and not c.read_only:
  <div class="mr-3">
    ${h.radio('linear', '0', checked=not c.is_linear, label=_("Õpilase eelvaade"),
    class_="nosave")}
    ${h.radio('linear', '1', checked=c.is_linear, label=_("Lineaarne järjekord"),
    class_="nosave")}
  </div>
  % endif

  <%
    if c.e_komplekt:
       keeled = c.e_komplekt.keeled
    else:
       keeled = c.test.keeled
  %>
  % if len(keeled) > 1:
  <div class="flex-grow-1 text-right">
    % for lang in keeled:
    ${h.radio('lang', lang, checkedif=c.lang, ronly=False, label=model.Klrida.get_lang_nimi(lang),
    class_="nosave")}
    % endfor
  </div>
  % endif
</div>

<script>
  $(function(){
      ## uuesti proovimisel pole vaja hoiatada, et andmed on muutunud
      ## lineaarsuse või keele muutmine
      $('#proovi,input[name="linear"],input[name="lang"]').click(function(){
          dirty = false;
          unset_unsaved($('iframe.ylesanne'));
          var url = "${h.url_current('new', lang='__LANG__', linear='__LINEAR__')}"
            .replace("__LANG__", $('input[name="lang"]:checked').val()||'')
            .replace("__LINEAR__", $('input[name="linear"]:checked').val()||'');
          window.location.replace(url);
      });
  });
</script>

</%def>
