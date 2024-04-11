<%inherit file="/common/formpage.mako"/>
<%def name="draw_tabs()">
<% c.tab1 = 'tagasisideviis' %>
<%include file="tabs.mako"/>
</%def>
<%def name="draw_subtabs()">
<%include file="tagasiside.tabs.mako"/>
</%def>

<%def name="page_title()">
${_("Test")}: ${c.test.nimi or ''} | ${_("Tagasiside")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Testid"), h.url('testid'))} 
${h.crumb(c.test.nimi or _("Test"))} 
${h.crumb(_("Tagasiside"))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'testid' %>
</%def>
<%def name="require()">
<%
c.includes['subtabs'] = True
c.includes['plotly'] = True
%>
</%def>
<%def name="page_headers()">
<style>
  table.iline>tbody>tr>td {
    border-top: .5px #e4882a solid; 
  }
  table.iline {
    margin-left: 25px;
  }
  td.leftborder {
    border-left: .5px #e4882a solid;
    padding-left: 3px;
  }

  <%include file="/avalik/tagasiside/tagasiside.css"/>
</style>
</%def>
<%
  c.is_edit = True
  if c.lang and isinstance(c.lang, list): c.lang = c.lang[0]
%>
% if c.hardcoded_tv:
<%include file="tagasiside.translating.mako"/>
<br/>
% endif

% if c.tsvorm and c.tsvorm.sisu or c.hardcoded_tv:
  % if c.test.testiliik_kood == const.TESTILIIK_KOOLIPSYH:
  ${_("Koolipsühholoogi testi tagasiside eelvaadet ei või päris sooritajate andmete põhjal näidata")}
% else:
  ${self.vaba_filter()}
  % endif
% endif

% if c.tagasiside_html:
<div class="fbwrapper" url="${h.url_current(None, getargs=True)}">
  <!-- ${h.request.url} -->
${c.tagasiside_html}
</div>
##<%include file="/avalik/ktulemused/gruppidetulemused_list.mako"/>
<%
  pdf_url = h.url_current('show', id=c.tsvorm_id, testimiskord_id=c.testimiskord_id, kool_koht_id=c.kool_koht_id, sooritaja_id=c.sooritaja_id, nimekiri_id=c.nimekiri_id, genrnd=c.genrnd and 1 or '', pdf=1)
%>
${h.btn_to(_("PDF"), pdf_url)}

% if c.can_xls:
<%
  xls_url = h.url_current('show', id=c.tsvorm_id, testimiskord_id=c.testimiskord_id, kool_koht_id=c.kool_koht_id, sooritaja_id=c.sooritaja_id, nimekiri_id=c.nimekiri_id, genrnd=c.genrnd and 1 or '', xls=1)
%>
${h.btn_to(_("Excel"), xls_url)}
% endif
% endif

<%def name="vaba_filter()">
  <script>
    ## vormi muutmisel peidame ära genereerimise võimaluse, kuna genereerimine toimub salvestatud vormi põhjal
    $(document).ready(function(){
      $('#f_sisu,input[name="liik"]').change(function(){
        $('.proovi').hide();
      });
      $('.proovi form').submit(function(){
      ## kopeerime genereerimise valikud põhivormile, et põhivormi muutmisel jääks need alles
        var fs = $('form#form_save');
        var fp = $(this);
        fs.find('input[name="testimiskord_id"]').val(fp.find('input[name="testimiskord_id"]').val());
        fs.find('input[name="tookood"]').val(fp.find('input[name="tookood"]').val());
        fs.find('input[name="kool_koht_id"]').val(fp.find('select[name="kool_koht_id"]').val());
      });
    });
  </script>
  <%
    on_opilane = c.tsvorm_id == 'F1' or c.tsvorm and c.tsvorm.liik in (model.Tagasisidevorm.LIIK_OPILANE, model.Tagasisidevorm.LIIK_OPETAJA)
    found = False
  %>
<div class="proovi mb-3">
  % for tk in c.testimiskorrad:
  <% found = True %>
  <div class="d-flex flex-wrap align-items-center my-1">
    ${h.flb('%s %s' % (_("Testimiskord"), tk.tahised), '', 'pr-4')}
    <div>
    ${h.form(h.url_current('show', id=c.tsvorm_id), method='get')}
    ${h.hidden('testimiskord_id', tk.id)}
    ${h.hidden('lang', c.lang)}   
    % if on_opilane:
      <span class="px-2">
        ${_("Töö kood")} ${h.text('tookood', c.tookood, size=5, ronly=False)}
      </span>
      <span class="px-2">
        ${_("Isikukood")} ${h.text('isikukood', c.isikukood, size=12, ronly=False)}
      </span>
      ${h.submit(_("Genereeri"))}
    % elif c.liik == model.Tagasisidevorm.LIIK_VALIM:
      <% leidub_valim = c.leidub_valim(tk.id) %>
      % if leidub_valim:
      ${h.submit(_("Genereeri"))}      
      % else:
      ${_("Valim puudub")}
      % endif
    % elif c.liik == model.Tagasisidevorm.LIIK_RIIKLIK:      
       ## seda liiki grupi kaupa ei kasutata
      ${h.submit(_("Genereeri"))}

    % else:
      <% st_opt = c.tk_statistikad_opt(tk) %>
      % if not st_opt:
      <span>${_("Koolide statistikat ei leitud")}</span>
      % else:
      <span class="px-2">
        ${_("Grupp")} ${h.select('kool_koht_id', c.kool_koht_id, st_opt, ronly=False, wide=False, empty=tk.statistika_arvutatud)}
      </span>
      ${h.submit(_("Genereeri"))}
      % endif
    % endif
    ${h.end_form()}
    </div>
  </div>
  % endfor
  <%
  %>
  % if c.nk_opt:
  <% found = True %>  
  <div class="d-flex flex-wrap align-items-center">
    ${h.flb(_("Testimiskorrata"), '', 'pr-4')}
    <div>
      ${h.form(h.url_current('show', id=c.tsvorm_id), method='get')}
      ${h.hidden('lang', c.lang)}
      <span class="px-2">
        ${_("Nimekiri")} ${h.select('nimekiri_id', c.nimekiri_id, c.nk_opt, ronly=False, wide=False)}
      </span>
      ${h.submit(_("Genereeri"))}
      ${h.end_form()}
    </div>
  </div>
  % endif
</div>

<div class="mb-2">
  ${h.form(h.url_current('show', id=c.tsvorm_id), method='get')}
  ${h.hidden('lang', c.lang)}
  ${h.submit(_("Genereeri juhuslikult"), id="genrnd")}
  ${h.end_form()}
</div>
</%def>

