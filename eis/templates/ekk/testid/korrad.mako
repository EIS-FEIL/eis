<%inherit file="/common/formpage.mako"/>
<%def name="draw_tabs()">
<% c.tab1 = 'korraldus' %>
<%include file="tabs.mako"/>
</%def>

<%def name="draw_subtabs()">
<% c.tab2 = 'korrad' %>
<%include file="korraldus.tabs.mako"/>
</%def>

<%def name="requirenw()">
<% c.pagenw = True %>
</%def>

<%def name="page_title()">
${_("Test")}: ${c.test.nimi or ''} | ${_("Testimiskorrad ja parameetrid")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Testid"), h.url('testid'))} 
${h.crumb(c.test.nimi or _("Test"))} 
${h.crumb(_("Korraldus"))}
${h.crumb(_("Testimiskorrad ja parameetrid"))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'testid' %>
</%def>

<%
c.can_update = c.user.has_permission('testimiskorrad', const.BT_UPDATE, c.test) and \
  c.test.staatus in (const.T_STAATUS_KOOSTAMISEL,const.T_STAATUS_KINNITATUD)
c.testimiskorrad = list(c.test.testimiskorrad)
%>
% if len(c.testimiskorrad) == 0:
${h.alert_notice(_("Ühtki testimiskorda ei ole sisestatud"), False)}
% endif
% if c.test.avaldamistase != const.AVALIK_EKSAM and c.test.on_kutse:
${h.alert_notice(_("Test {id} pole märgitud testimiskorraga testiks").format(id=c.test.id))}
% endif

% if c.testimiskorrad:
<div class="row content-wrapper flex-nowrap">
  ${self.aside_testimiskorrad()}
  <section class="col-12 col-md-9 col-lg-10">
    <div class="form-group d-md-hide">
      ${self.dropdown_testimiskorrad()}
      <div class="d-flex justify-content-between align-items-md-center flex-column flex-md-row">
        % if c.item:
        ${next.body()}
        % endif
      </div>
    </div>
  </section>
</div>
% elif c.item:
      <div class="d-flex justify-content-between align-items-md-center flex-column flex-md-row">
        ${next.body()}
      </div>
% endif
${self.lisamine()}

<%def name="buttons()">
</%def>

<%def name="lisamine()">        
<div class="d-flex flex-wrap">
  <div class="flex-grow-1">
        % if c.can_update:
        <%
          if c.test.on_kutse:
            url_new = h.url('test_kutse_new_kord', test_id=c.test.id)
          else:
            url_new = h.url('test_new_kord', test_id=c.test.id)
        %>
        
        <% c.opt_mall = c.opt.opt_kordmall(c.test.testiliik_kood) %>      
        % if c.opt_mall:
        <div style="display:inline-block">
          ${h.button(_("Lisa testimiskord malliga"), id="bnewm", level=2)}
          <div class="malliga" style="display:none">
            ${h.form(url_new, method='get', id="fnewm")}
            <p>
              ${_("Testimiskorra mall")}
              ${h.select('mall_id', '', c.opt_mall, wide=False, empty=True, class_="nosave")}
            </p>
            ${h.submit_dlg(_("Lisa testimiskord"))}
            ${h.end_form()}
          </div>
          <script>
            $('#bnewm').click(function(){ open_dialog({'contents_elem': $('.malliga')}); });
          </script>
        </div>
        % endif
        ${h.btn_to(_("Lisa testimiskord"), url_new, mdicls='mdi-plus')}
        % endif
  </div>
  <div class="text-right">
    ${self.buttons()}
  </div>
</div>
</%def>        

<%def name="aside_testimiskorrad()">
  <aside class="sidebar-menu col-3 col-lg-2 mr-0 d-none d-md-block">
    <nav aria-label="Külgmenüü" class="mb-5 mr-4">
      <ul class="nav level-1">
        % for rcd in c.testimiskorrad:
        <%
          if c.test.on_kutse:
             url = h.url('test_kutse_edit_kord', test_id=c.test.id, id=rcd.id)
          else:
             url = h.url('test_edit_kord', test_id=c.test.id, id=rcd.id)
        %>
        <li class="nav-item dropdown show">
          <a href="${url}"
             class="nav-link dropdown-toggle ${c.item == rcd and 'active' or ''}"
             role="button" aria-expanded="true">
            <span class="text-truncate">${rcd.tahis}</span>
          </a>
          <ul class="nav level-2">
          % for ta in rcd.toimumisajad:
          <%
            if c.test.on_kutse:
               url = None
            else:
               url = h.url('test_kord_edit_toimumisaeg', test_id=c.test.id, kord_id=rcd.id, id=ta.id)
          %>
            <li class="nav-item dropdown ${c.item == ta and 'show' or ''}">
              <a href="${url or '#'}"
                class="nav-link ${c.item == ta and 'active' or ''}"
                role="button" aria-expanded="false">
                <span class="text-truncate">${ta.tahised}</span>
              </a>
            </li>
          % endfor
          </ul>
        </li>
        % endfor
      </ul>
    </nav>
  </aside>
</%def>

<%def name="dropdown_testimiskorrad()">
      <div class="d-md-none dropdown content-dropdown w-100 mb-7">
        <button class="btn btn-select dropdown-toggle"
                type="button"
                id="dropdownMenuButtonTK"
                data-toggle="dropdown"
                aria-haspopup="true"
                aria-expanded="false">
          ${c.item and c.item.tahised}
          <i class="mdi mdi-chevron-down"></i>
        </button>
        <div class="dropdown-menu content-dropdown-menu"
             aria-labelledby="dropdownMenuButtonTK">
          % for rcd in c.testimiskorrad:
          <%
            if c.test.on_kutse:
              url = h.url('test_kutse_edit_kord', test_id=c.test.id, id=rcd.id)
            else:
              url = h.url('test_edit_kord', test_id=c.test.id, id=rcd.id)
          %>
          <a class="dropdown-item ${c.item == rcd and 'active' or ''}"
             href="${url}">${rcd.tahis}</a>
          % if not c.test.on_kutse:
          % for ta in rcd.toimumisajad:
          <%
               url = h.url('test_kord_edit_toimumisaeg', test_id=c.test.id, kord_id=rcd.id, id=ta.id)
          %>
          <a class="dropdown-item ${c.item == ta and 'active' or ''} pl-5"
             href="${url}">${ta.tahised}</a>
          % endfor
          % endif
          % endfor
        </div>
      </div>
</%def>
