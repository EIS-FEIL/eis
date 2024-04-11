<%inherit file="/common/formpage.mako"/>
<%def name="draw_tabs()">
<% c.tab1 = 'tagasisideviis' %>
<%include file="tabs.mako"/>
</%def>
<%def name="draw_subtabs()">
<%include file="tagasiside.tabs.mako"/>
</%def>
<%def name="active_menu()">
<% c.menu1 = 'testid' %>
</%def>

<%def name="page_title()">
${_("Test")}: ${c.test.nimi or ''} | ${_("Tagasiside")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Testid"), h.url('testid'))} 
${h.crumb(c.test.nimi or _("Test"))} 
${h.crumb(_("Tagasiside"))}
</%def>
<%def name="require()">
<%
c.includes['ckeditor'] = True
c.includes['subtabs'] = True
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
</style>
</%def>

<%
  c.is_edit = c.user.has_permission('ekk-testid', const.BT_UPDATE, c.test)
  c.hardcoded_tv = c.tvorm and c.tvorm.id in ('F1','F2','F3','F4')
%>
% if c.hardcoded_tv:
## vabal vormil on iga keele jaoks eraldi vorm
<%include file="tagasiside.translating.mako"/>
% endif

<%
  if c.tvorm and not c.hardcoded_tv:
     c.root_tvorm = c.tvorm.get_root()
  if not c.tvorm:
     c.tvorm = c.new_item()
     c.root_tvorm = c.tvorm
  on_kursus = len(c.test.testikursused) > 0
  can_update = c.user.has_permission('ekk-testid', const.BT_UPDATE, c.test)
%>
% if len(c.items):
<table class="table table-borderless table-striped" >
  <thead>
    <tr>
      <th>${_("Tagasisidevormi nimetus")}</th>
      <th>${_("Liik")}</th>
      % if on_kursus:
      <th>${_("Kursus")}</th>
      % endif
      <th>${_("Sooritamise keel")}</th>
      <th>${_("Kehtivus")}</th>
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(c.items):
    <%
      tv = rcd
      url_edit = h.url_current('edit', id=tv.id)
      url_show = h.url_current('show', id=tv.id)
      liik_nimi = tv.liik_nimi
    %>
    <tr ${tv == c.tvorm and 'class="selected"' or ''}>
      <td>
        % if can_update:
        ${h.link_to(tv.nimi, url_edit)}        
        % else:
        ${h.link_to(tv.nimi, url_show)}
        % endif
      </td>
      <td>
        % if can_update:
        ${h.link_to(liik_nimi, url_edit)}        
        % else:
        ${h.link_to(liik_nimi, url_show)}
        % endif
        <% cnta = len(rcd.alamosad) %>
        % if cnta:
        (${cnta})
        % endif
      </td>
      % if on_kursus:
      <td>
        ${tv.kursus_nimi}
      </td>
      % endif
      <td>
        % if tv.lang:
        ${model.Klrida.get_str('SOORKEEL', tv.lang)}
        % else:
        ${_("Kõik keeled")}
        % endif
      </td>
      <td>
        % if tv.staatus == const.B_STAATUS_AUTO:
        ${_("Automaatne")}
        % elif tv.staatus:
        ${_("Kehtiv")}
        % else:
        ${_("Kehtetu")}
        % endif
      </td>
    </tr>
    % endfor
  </tbody>
</table>
% endif

${h.form_save(c.tvorm and c.tvorm.id)}
${h.hidden('sup_id', c.tvorm.ylem_id)}
${h.hidden('seq', '')}
% if c.hardcoded_tv:
${self.tvorm_diag()}
% else:
${self.tvorm_vaba_alamosad()}
% endif

<div class="pt-1 d-flex flex-wrap">
  <div class="flex-grow-1">

    % if c.tvorm.id and not c.tvorm.ylem_id and not c.hardcoded_tv:
    ${h.submit(_("Kopeeri"), id="copy", level=2)}      
    % endif

    % if c.tvorm.id and can_update and not c.hardcoded_tv:
    ${h.btn_remove(id=c.tvorm.id)}
    % if not c.tvorm.ylem_id:
    ${h.btn_to(_("Lisa mallile alamosa"), h.url_current('new', sup_id=c.tvorm.id), method='get', id="newsup")}
    % endif
    % endif

    ${h.btn_to(_("Lisa uus mall"), h.url_current('new'), method='get')}
    ${h.submit(_("Genereeri uus mall"), id="genereeri", style="display:none")}

  </div>

  % if c.test.tagasiside_mall == const.TSMALL_DIAG or c.tvorm and not c.hardcoded_tv:
  % if c.is_edit or c.is_tr:
  ${h.submit()}
  % endif
  % endif
</div>
${h.end_form()}

<script>
  $(function(){
  ## genereeri-nupp kuvada ainult siis, kui liik on "õpilaste tulemused"/"klasside tulemused"
  $('#liik').change(function(){
    var l = $('#liik').val();
    $('#genereeri').toggle(l=="${model.Tagasisidevorm.LIIK_GRUPPIDETULEMUSED}" || l=="${model.Tagasisidevorm.LIIK_OSALEJATETULEMUSED}");
  });
  var l = $('#liik').val();
  $('#genereeri').toggle(l=="${model.Tagasisidevorm.LIIK_GRUPPIDETULEMUSED}" || l=="${model.Tagasisidevorm.LIIK_OSALEJATETULEMUSED}");
  });
</script>

<%def name="tvorm_vaba_alamosad()">
<% subitems = list(c.root_tvorm.alamosad) %>
% if subitems or c.root_tvorm != c.tvorm:
<div class="row content-wrapper flex-nowrap">
  ${self.aside_parts()}
  <section class="col-12 col-md-9">
    <div class="form-group d-md-hide">
      <div class="flex-column flex-md-row">
        ${self.tvorm_vaba()}
      </div>
    </div>
  </section>
</div>
% else:
${self.tvorm_vaba()}
% endif
</%def>

<%def name="aside_parts()">
  <aside class="sidebar-menu col-3 mr-0 d-block">
    <nav aria-label="Malli osad" class="mb-5 mr-4">
      <ul class="nav level-1">
        ${self.aside_parts_item(c.root_tvorm, 2)}
      </ul>
    </nav>
  <script>
  $(function(){
      $('#moveup,#movedown').click(function(){
      var li = $(this).closest('li.dropdown');
      var is_up = $(this).is('#moveup');
      if(is_up)
      {
         var li2 = li.prev('li.dropdown');
         if(li2.length)
            li.after(li2);
      }
      else
      {
         var li2 = li.next('li.dropdown');
         if(li2.length)
            li.before(li2);
      }
      var seq = li.prevAll('li.dropdown').length;
      $('input#seq').val(seq+1);
    });
  });
  </script>
  </aside>
</%def>

<%def name="aside_parts_item(item, level)">
      <%
        action = c.is_edit and 'edit' or 'show'
        url = h.url_current(action, id=item.id)
        is_active = c.item == item
      %>
      <li class="nav-item dropdown show text-truncate">
        <div class="d-flex nav-link ${is_active and 'active' or ''}">
          <div class="flex-grow-1">
          <a href="${url}"
             style="text-decoration:none"
             role="button">
            <span class="pl-2">
              % if level == 2:
              ${_("Põhivorm")}
              % else:
              ${item.nimi}
              % endif
            </span>
          </a>
          </div>
          % if is_active:
          ${h.mdi_icon('mdi-menu-up', id="moveup")}
          ${h.mdi_icon('mdi-menu-down', id="movedown")}
          % endif
        </div>        
          <% alamosad = list(item.alamosad) %>
          <ul class="nav level-${level}">
            % for subitem in item.alamosad:
            ${self.aside_parts_item(subitem, level+1)}
            % endfor
          </ul>
        </li>
</%def>

<%def name="tvorm_vaba()">
<% ch = h.colHelper('col-md-2', 'col-md-10') %>
<div class="my-2">
  <div class="form-group row">
    ${ch.flb(_("Liik"))}
    % if c.tvorm.ylem_id:
    <% liik = c.root_tvorm.liik %>
      ${c.root_tvorm.liik_nimi}
      ${h.hidden('liik', liik)}
    % else:
    <div class="col-md-6">
      <%
        liik = c.tvorm.liik
      %>
      ${h.select('liik', c.tvorm.liik, model.Tagasisidevorm.opt_liik(), wide=False)}
    </div>
    <div class="col-md-2">
      <div class="fb-opilane">
        <% checked = not c.tvorm.id and True or c.tvorm.nahtav_opetajale %>
        ${h.checkbox('f_nahtav_opetajale', value=1, checked=checked, label=_("Õpetajale nähtav"))}
      </div>
    </div>
    <div class="col-md-2 text-md-right">
      ${h.checkbox1('staatus', const.B_STAATUS_KEHTIV, checked=c.tvorm.staatus, label=_("Kehtiv"))}
    </div>
    % endif
  </div>
  <div class="form-group row">
    ${ch.flb(_("Nimetus"))}
    <div class="col-md-9">
      ${h.text('f_nimi', c.tvorm.nimi, maxlength=100)}
    </div>
  </div>
  <%
    if c.test:
       opt_lang = [(lang, model.Klrida.get_str('SOORKEEL', lang)) for lang in c.test.keeled]
    else:
       opt_lang = [(r[0], r[1]) for r in c.opt.SOORKEEL]
  %>    
  % if len(opt_lang) > 1:
  <div class="form-group row">
    ${ch.flb(_("Keel"))}
    <div class="col-md-9">
      % if c.tvorm.ylem_id:
      ${c.root_tvorm.lang_nimi}
      % else:
      ${h.radio('f_lang', value='', checked=not c.tvorm.lang, label=_("Kõik keeled"))}
      % for lang, lang_name in opt_lang:
      ${h.radio('f_lang', value=lang, checkedif=c.tvorm.lang, label=lang_name)}
      % endfor
      % endif
    </div>
  </div>
  % endif
  <%
    opt_kursus = [(r.kursus_kood, r.kursus_nimi) for r in c.test.testikursused]
  %>
  % if len(opt_kursus) > 0:
  <div class="form-group row">
    ${ch.flb(_("Kursus"))}
    <div class="col-md-9">
      % if c.tvorm.ylem_id:
      ${model.Klrida.get_str('KURSUS', c.root_tvorm.kursus_kood, ylem_kood=c.test.aine_kood)}
      ${h.hidden('kursus', c.root_tvorm.kursus_kood, class_="kursus")}
      % else:
      ${h.radio('f_kursus', value='', checked=not c.tvorm.kursus_kood, label=_("Kõik kursused"))}
      % for k, k_name in opt_kursus:
      ${h.radio('f_kursus', value=k, checkedif=c.tvorm.kursus_kood, label=k_name)}
      % endfor
      % endif
    </div>
  </div>
  % endif
</div>

${h.ckeditor('f_sisu', c.tvorm.sisu, toolbar='feedback_src', srcmode=False, smart_quotes=False, upload_url=h.url('test_tagasiside_failid', test_id=c.test.id), browse_url=h.url('test_tagasiside_failid', test_id=c.test.id))}
<div class="jatk my-2" style="display:none">
  ${h.flb(_("Pikendatud sisu (näita rohkem)"), 'f_sisu_jatk')}
  ${h.ckeditor('f_sisu_jatk', c.tvorm.sisu_jatk, toolbar='feedback_src', srcmode=False, smart_quotes=False, upload_url=h.url('test_tagasiside_failid', test_id=c.test.id), browse_url=h.url('test_tagasiside_failid', test_id=c.test.id))}
</div>

<script>
  function get_dialog_url()
  {
  % if c.tvorm.ylem_id:
  var k = "${c.root_tvorm.kursus_kood or ''}";
  % elif opt_kursus:
  var k = $('input[name="f_kursus"]:checked').val();
  % else:
  var k = '';
  % endif
  return "${h.url('test_tagasiside_edit_diagramm', test_id=c.test.id, testiosa_id=c.testiosa.id)}" + '?kursus=' + k;
  }
  function get_feedbackvar_url()
  {
  return "${h.url('test_tagasiside_new_fbvar', test_id=c.test.id, testiosa_id=c.testiosa.id)}";
  }
  function on_liik()
  {
  % if c.is_edit:
  var liik = $('#liik').val();
  % else:
  var liik = "${c.tvorm.liik}";
  % endif
  $('.jatk').toggle(liik == "${model.Tagasisidevorm.LIIK_KIRJELDUS}");
  $('.fb-opilane').toggle(liik == "${model.Tagasisidevorm.LIIK_OPILANE}");
  % if c.is_edit and c.item and not c.item.ylem_id:
  $('#newsup').toggle(liik=="${model.Tagasisidevorm.LIIK_KIRJELDUS}" || liik=="${model.Tagasisidevorm.LIIK_GRUPPIDETULEMUSED}" || liik=="${model.Tagasisidevorm.LIIK_OSALEJATETULEMUSED}");
  % endif
  }
  $(function(){
  on_liik();
  % if c.is_edit:
  $('#liik').change(on_liik);
  % endif
  });
</script>
</%def>


<%def name="tvorm_diag()">      
${h.hidden('lang', c.lang)}
${h.hidden('is_tr', c.is_tr)} 
  <%include file="tagasiside.vorm.diag.mako"/>
</%def>
